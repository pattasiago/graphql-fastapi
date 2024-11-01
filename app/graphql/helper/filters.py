from sqlalchemy import and_, or_, not_
from sqlalchemy.orm import Query, class_mapper, contains_eager
from datetime import datetime

# def apply_filters(query: Query, logical_filter, model):
#     if logical_filter is None:
#         return query

#     block_expressions = []
#     joined_models = set()  # Conjunto para evitar joins duplicados

#     for block in logical_filter.blocks:
#         block_conditions = []

#         for condition in block.conditions:
#             if '.' in condition.field:
#                 parts = condition.field.split('.')
#                 current_model = model

#                 # Navega pelos atributos aninhados e aplica joins
#                 for part in parts[:-1]:
#                     mapper = class_mapper(current_model)
#                     relationship = mapper.get_property(part)

#                     if relationship is None:
#                         raise ValueError(f"Relacionamento não encontrado: {part}")

#                     current_model = relationship.mapper.class_

#                     # Adiciona o join ao query apenas se ainda não estiver no conjunto de joins
#                     if current_model not in joined_models:
#                         query = query.outerjoin(current_model).options(contains_eager(relationship))
#                         joined_models.add(current_model)

#                 # Acessa o último atributo
#                 field = getattr(current_model, parts[-1], None)
#                 if field is None:
#                     continue  # Se o campo não existe, pula

#             else:
#                 field = getattr(model, condition.field, None)

#             if field is None:
#                 continue  # Se o campo não existe, pula

#             # Aplica o operador de filtragem
#             if condition.operator == "eq":
#                 expr = (field == condition.value)
#             elif condition.operator == "ne":
#                 expr = (field != condition.value)
#             elif condition.operator == "gt":
#                 expr = (field > condition.value)
#             elif condition.operator == "lt":
#                 expr = (field < condition.value)
#             elif condition.operator == "in":
#                 expr = field.in_(condition.value if isinstance(condition.value, list) else [condition.value])
#             elif condition.operator == "not_in":
#                 expr = ~field.in_(condition.value if isinstance(condition.value, list) else [condition.value])
#             elif condition.operator == "like":
#                 expr = field.ilike(f"%{condition.value}%")
#             else:
#                 raise ValueError(f"Operador não reconhecido: {condition.operator}")

#             if condition.negate:
#                 expr = not_(expr)

#             block_conditions.append(expr)

#         # Combina as condições do bloco
#         if block.operator.upper() == "AND":
#             combined_block_expr = and_(*block_conditions)
#         elif block.operator.upper() == "OR":
#             combined_block_expr = or_(*block_conditions)
#         else:
#             raise ValueError(f"Operador inválido no bloco: {block.operator}")

#         if block.negate:
#             combined_block_expr = not_(combined_block_expr)

#         block_expressions.append(combined_block_expr)

#     # Combina os blocos
#     if logical_filter.operator.upper() == "AND":
#         combined_expr = and_(*block_expressions)
#     elif logical_filter.operator.upper() == "OR":
#         combined_expr = or_(*block_expressions)
#     else:
#         raise ValueError(f"Operador inválido no filtro: {logical_filter.operator}")

#     if logical_filter.negate:
#         combined_expr = not_(combined_expr)

#     # Aplica o filtro combinado
#     query = query.filter(combined_expr)
#     return query


def apply_filters(query: Query, logical_filter, model):
    """
    Aplica filtros lógicos em uma consulta SQLAlchemy com base nas condições definidas em logical_filter.
    
    Parameters:
        query (Query): A consulta SQLAlchemy original.
        logical_filter: Estrutura contendo blocos e condições para filtragem.
        model: Modelo de dados SQLAlchemy principal para construir os filtros.

    Returns:
        Query: A consulta modificada com os filtros aplicados.
    """
    if logical_filter is None:
        return query

    # Lista de expressões para os blocos de filtro
    block_expressions = []
    joined_models = set()  # Conjunto para evitar joins duplicados

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

    # block.conditions = resolve_conditions(block.conditions)
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
        joined_models (set): Conjunto de modelos já com join aplicado.

    Returns:
        Field, Query: Campo SQLAlchemy correspondente ao field_path e a consulta modificada.
    """
    if '.' in field_path:
        parts = field_path.split('.')
        current_model = model

        for part in parts[:-1]:
            relationship = get_relationship(current_model, part)
            current_model = relationship.mapper.class_
            
            if current_model not in joined_models:
                query = query.outerjoin(current_model).options(contains_eager(relationship))
                joined_models.add(current_model)

        return getattr(current_model, parts[-1], None), query
    else:
        return getattr(model, field_path, None), query

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


# def parse_date(value):
#     """Converte uma string ISO 8601 para datetime."""
#     try:
#         return datetime.fromisoformat(value)
#     except ValueError:
#         raise ValueError(f"Invalid date format: {value}")

# def resolve_conditions(conditions):
#     for condition in conditions:
#         if condition.is_date:
#             if isinstance(condition.value, str):
#                 # Converte a string individual para datetime
#                 condition.value = parse_date(condition.value)
#             elif isinstance(condition.value, list):
#                 # Converte cada string na lista para datetime
#                 condition.value = [parse_date(v) if isinstance(v, str) else v for v in condition.value]
#     return conditions
