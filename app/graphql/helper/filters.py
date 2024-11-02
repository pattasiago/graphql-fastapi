from sqlalchemy import and_, or_, not_
from sqlalchemy.orm import Query, class_mapper, contains_eager

def prepare_query_columns(fields_structure, model, query, joined_models, path_prefix=None):
    """
    Resolve campos de modelo a partir de uma estrutura aninhada, aplicando joins para atributos aninhados se necessário.

    Parameters:
        fields_structure (list): Estrutura dos campos, incluindo subcampos aninhados.
        model: Modelo SQLAlchemy de referência para os campos.
        query (Query): A consulta SQLAlchemy em construção.
        joined_models (set): Conjunto de caminhos de relacionamento já com join aplicado.
        path_prefix (tuple): Prefixo de caminho para identificar subcampos.

    Returns:
        Query: A consulta SQLAlchemy modificada.
    """
    for field in fields_structure:
        if isinstance(field, dict):  # Se o campo é um dicionário, indica uma relação
            for relationship_name, subfields in field.items():
                # Resolve o relacionamento atual e o novo modelo associado
                relationship = getattr(model, relationship_name)
                next_model = relationship.mapper.class_

                # Construindo um prefixo para evitar duplicidade de joins
                new_path_prefix = (path_prefix or ()) + (relationship,)

                # Aplica o join se ainda não foi feito para esse caminho
                if new_path_prefix not in joined_models:
                    query = query.outerjoin(relationship).options(contains_eager(*new_path_prefix))
                    joined_models.add(new_path_prefix)

                # Chamada recursiva para processar subcampos
                query = prepare_query_columns(subfields, next_model, query, joined_models, new_path_prefix)

        else:
            # Campo individual, sem subcampos aninhados - não precisa de join
            getattr(model, field, None)

    return query

def apply_filters(query: Query, logical_filter, model, fields_structure=None):
    """
    Aplica filtros lógicos em uma consulta SQLAlchemy com base nas condições definidas em logical_filter.
    
    Parameters:
        query (Query): A consulta SQLAlchemy original.
        logical_filter: Estrutura contendo blocos e condições para filtragem.
        model: Modelo de dados SQLAlchemy principal para construir os filtros.

    Returns:
        Query: A consulta modificada com os filtros aplicados.
    """
    joined_models = set()  # Conjunto para evitar joins duplicados
    query = prepare_query_columns(fields_structure, model, query, joined_models, path_prefix=None)

    if logical_filter is None:
        return query

    # Lista de expressões para os blocos de filtro
    block_expressions = []

    for block in logical_filter.blocks:
        block_expression, query = process_block(block, model, query, joined_models)
        block_expressions.append(block_expression)

    # Combina todos os blocos de expressão
    combined_expr = combine_blocks(block_expressions, logical_filter.operator, logical_filter.negate)
    
    # Aplica o filtro final à consulta
    query = query.filter(combined_expr)
    return query

def process_block(block, model, query, joined_models):
    """
    Processa um bloco de condições de filtragem, aplicando joins necessários e combinando as condições.
    
    Parameters:
        block: Bloco de condições a serem aplicadas.
        model: Modelo SQLAlchemy de referência para o bloco.
        query (Query): A consulta SQLAlchemy em construção.
        joined_models (set): Conjunto para controlar joins já realizados.

    Returns:
        Expression, Query: Expressão combinada das condições do bloco e a consulta modificada.
    """
    block_conditions = []

    for condition in block.conditions:
        field, query = resolve_field(condition.field, model, query, joined_models)
        if field is not None:
            condition_expr = build_condition_expression(field, condition)
            block_conditions.append(condition_expr)

    # Combina as condições do bloco com o operador especificado
    combined_block_expr = combine_conditions(block_conditions, block.operator, block.negate)
    return combined_block_expr, query

def resolve_field(field_path, model, query, joined_models):
    """
    Resolve um campo de modelo, aplicando joins para atributos aninhados se necessário.
    
    Parameters:
        field_path (str): Caminho do campo, podendo incluir subcampos.
        model: Modelo SQLAlchemy de referência para o campo.
        query (Query): A consulta SQLAlchemy em construção.
        joined_models (set): Conjunto de caminhos de relacionamento já com join aplicado.

    Returns:
        Field, Query: Campo SQLAlchemy correspondente ao field_path e a consulta modificada.
    """
    parts = field_path.split('.')
    current_model = model  # Modelo inicial (ex.: Post)
    relationship_path = []  # Armazena o caminho do relacionamento completo

    # Itera sobre cada parte do caminho, exceto o último
    for part in parts[:-1]:
        # Obtém o relacionamento para o campo atual
        relationship = getattr(current_model, part)
        
        # Adiciona ao caminho do relacionamento e cria uma tupla para verificar
        relationship_path.append(relationship)
        relationship_path_tuple = tuple(relationship_path)
        
        # Aplica o join somente se ainda não foi aplicado
        if relationship_path_tuple not in joined_models:
            query = query.outerjoin(relationship).options(contains_eager(*relationship_path))
            joined_models.add(relationship_path_tuple)

        # Atualiza o modelo atual para o próximo na cadeia
        current_model = relationship.mapper.class_

    # Retorna o último campo na hierarquia e a query atualizada
    return getattr(current_model, parts[-1], None), query


def get_relationship(model, attribute):
    """
    Obtém uma relação de um modelo SQLAlchemy, garantindo que o relacionamento exista.
    
    Parameters:
        model: Modelo SQLAlchemy onde o relacionamento está definido.
        attribute (str): Nome do atributo de relacionamento.

    Returns:
        Relationship: Relacionamento SQLAlchemy para o atributo.

    Raises:
        ValueError: Se o relacionamento não for encontrado.
    """
    mapper = class_mapper(model)
    relationship = mapper.get_property(attribute)
    if relationship is None:
        raise ValueError(f"Relacionamento não encontrado: {attribute}")
    return relationship

def build_condition_expression(field, condition):
    """
    Constrói uma expressão de condição SQLAlchemy com base no operador e valor especificados.
    
    Parameters:
        field: Campo SQLAlchemy a ser filtrado.
        condition: Condição contendo operador e valor.

    Returns:
        Expression: Expressão SQLAlchemy correspondente à condição.
    """
    operators = {
        "=": field == condition.value,
        "!=": field != condition.value,
        ">": field > condition.value,
        "<": field < condition.value,
        ">=": field >= condition.value,
        "<=": field <= condition.value,
        "in": field.in_(condition.value if isinstance(condition.value, list) else [condition.value]),
        "not_in": ~field.in_(condition.value if isinstance(condition.value, list) else [condition.value]),
        "contains": field.ilike(f"%{condition.value}%"),
    }

    if condition.operator not in operators:
        raise ValueError(f"Operador não reconhecido: {condition.operator}")

    expr = operators[condition.operator]
    return not_(expr) if condition.negate else expr

def combine_conditions(conditions, operator, negate):
    """
    Combina condições usando operador lógico especificado.
    
    Parameters:
        conditions (list): Lista de expressões de condição.
        operator (str): Operador lógico para combinar as condições ('AND' ou 'OR').
        negate (bool): Indica se a expressão combinada deve ser negada.

    Returns:
        Expression: Expressão combinada das condições.
    """
    combined_expr = and_(*conditions) if operator.upper() == "AND" else or_(*conditions)
    return not_(combined_expr) if negate else combined_expr

def combine_blocks(block_expressions, operator, negate):
    """
    Combina blocos de condições em uma expressão final para o filtro lógico.
    
    Parameters:
        block_expressions (list): Lista de expressões de blocos.
        operator (str): Operador lógico para combinar os blocos ('AND' ou 'OR').
        negate (bool): Indica se a expressão combinada deve ser negada.

    Returns:
        Expression: Expressão combinada dos blocos.
    """
    combined_expr = and_(*block_expressions) if operator.upper() == "AND" else or_(*block_expressions)
    return not_(combined_expr) if negate else combined_expr
