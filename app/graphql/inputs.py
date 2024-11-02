import strawberry
import datetime
from typing import List, Optional

@strawberry.scalar(
    description="Um tipo que aceita qualquer valor",
    serialize=lambda v: v,
    parse_value=lambda v: v
)
class AnyScalar:
    pass

# Condição individual
@strawberry.input
class ConditionInput:
    field: str
    operator: str
    value: AnyScalar  # Valor ou lista de valores
    negate: bool = False  # Inverte a condição se for True

# Bloco lógico que combina condições com um operador (AND ou OR)
@strawberry.input
class LogicalBlockInput:
    operator: Optional[str] = "AND"  # O operador entre as condições dentro do bloco
    conditions: List[ConditionInput]  # Lista de condições individuais
    negate: bool = False  # Inverte o bloco lógico se for True

# Filtro principal, contendo blocos lógicos
@strawberry.input
class LogicalFilterInput:
    blocks: List[LogicalBlockInput]  # Blocos lógicos com operador AND entre eles
    operator: Optional[str] = "AND"
    negate: bool = False  # Inverte o filtro completo se for True
