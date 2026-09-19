from dataclasses import dataclass, field

@dataclass
class Node: pass
@dataclass
class Program(Node): statements:list
@dataclass
class Literal(Node): value:object
@dataclass
class Variable(Node): name:str
@dataclass
class ListLiteral(Node): items:list
@dataclass
class Unary(Node): op:str; expr:Node
@dataclass
class Binary(Node): left:Node; op:str; right:Node
@dataclass
class Assign(Node): target:Node; value:Node
@dataclass
class Call(Node): callee:Node; args:list
@dataclass
class RangeExpr(Node): start:Node; end:Node
@dataclass
class Index(Node): obj:Node; index:Node
@dataclass
class Member(Node): obj:Node; name:str
@dataclass
class VarDecl(Node): name:str; value:Node; const:bool=False; type_name:str|None=None
@dataclass
class ExprStmt(Node): expr:Node
@dataclass
class Block(Node): statements:list
@dataclass
class IfStmt(Node): condition:Node; then:Block; elifs:list=field(default_factory=list); else_block:Block|None=None
@dataclass
class WhileStmt(Node): condition:Node; body:Block
@dataclass
class ForStmt(Node): name:str; iterable:Node; body:Block
@dataclass
class FuncDecl(Node): name:str; params:list; body:Block
@dataclass
class ReturnStmt(Node): value:Node|None
@dataclass
class BreakStmt(Node): pass
@dataclass
class ContinueStmt(Node): pass
@dataclass
class ImportStmt(Node): name:str
@dataclass
class TryStmt(Node): body:Block; error_name:str; catch:Block
@dataclass
class ThrowStmt(Node): expr:Node
