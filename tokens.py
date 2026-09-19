from dataclasses import dataclass
from enum import Enum, auto

class TokenType(Enum):
    NUMBER = auto(); STRING = auto(); IDENT = auto()
    DEF = auto(); VAR = auto(); CONST = auto(); FUNC = auto(); IF = auto(); ELSE = auto()
    WHILE = auto(); FOR = auto(); IN = auto(); RETURN = auto(); BREAK = auto(); CONTINUE = auto()
    TRUE = auto(); FALSE = auto(); NULL = auto(); IMPORT = auto(); AND = auto(); OR = auto(); NOT = auto()
    TRY = auto(); CATCH = auto(); THROW = auto()
    PLUS = auto(); MINUS = auto(); STAR = auto(); SLASH = auto(); PERCENT = auto(); POWER = auto()
    ASSIGN = auto(); ARROW = auto(); CLOSE = auto()
    EQ = auto(); NE = auto(); GT = auto(); LT = auto(); GE = auto(); LE = auto()
    LPAREN = auto(); RPAREN = auto(); LBRACKET = auto(); RBRACKET = auto(); COMMA = auto(); DOT = auto()
    COLON = auto(); SEMI = auto(); RANGE = auto(); EOF = auto()

@dataclass(frozen=True)
class Token:
    type: TokenType
    value: object
    line: int
    column: int
