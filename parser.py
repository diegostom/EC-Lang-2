from tokens import TokenType as T
from ec_ast import *
from errors import ECParseError

class Parser:
    def __init__(self,tokens): self.t=tokens; self.i=0
    def cur(self): return self.t[self.i]
    def check(self,*xs): return self.cur().type in xs
    def at(self,*xs): return self.cur().type in xs
    def advance(self): x=self.cur(); self.i+=1; return x
    def eat(self,x):
        if not self.check(x): raise ECParseError(f'Se esperaba {x.name} y se encontro {self.cur().value!r}.',self.cur(),'E2000')
        return self.advance()
    def optional(self,x):
        if self.check(x): self.advance(); return True
        return False
    def parse(self):
        a=[]
        while not self.check(T.EOF): a.append(self.statement())
        return Program(a)
    def statement(self):
        if self.check(T.SEMI): self.advance(); return ExprStmt(Literal(None))
        if self.check(T.DEF):
            self.advance()
            if self.check(T.VAR): return self.var_decl(after_keyword=True)
            if self.check(T.FUNC): return self.func_decl(after_keyword=True)
            raise ECParseError("Despues de 'def' se esperaba 'var' o 'func'.", self.cur(), 'E2003')
        if self.check(T.VAR,T.CONST): return self.var_decl()
        if self.check(T.FUNC): return self.func_decl()
        if self.check(T.IF): return self.if_stmt()
        if self.check(T.WHILE): return self.while_stmt()
        if self.check(T.FOR): return self.for_stmt()
        if self.check(T.RETURN):
            self.advance(); v=None if self.check(T.SEMI,T.CLOSE,T.EOF) else self.expression(); self.optional(T.SEMI); return ReturnStmt(v)
        if self.check(T.BREAK): self.advance(); self.optional(T.SEMI); return BreakStmt()
        if self.check(T.CONTINUE): self.advance(); self.optional(T.SEMI); return ContinueStmt()
        if self.check(T.IMPORT): self.advance(); n=self.eat(T.IDENT).value; self.optional(T.SEMI); return ImportStmt(n)
        if self.check(T.TRY): return self.try_stmt()
        if self.check(T.THROW): self.advance(); e=self.expression(); self.optional(T.SEMI); return ThrowStmt(e)
        e=self.expression(); self.optional(T.SEMI); return ExprStmt(e)
    def var_decl(self, after_keyword=False):
        const=self.advance().type==T.CONST; type_name=None
        # explicit type syntax: var int edad => 20;
        if self.check(T.IDENT) and self.i+1<len(self.t) and self.t[self.i+1].type==T.IDENT:
            type_name=self.advance().value
        name=self.eat(T.IDENT).value; self.eat(T.ARROW); val=self.expression_legacy() if after_keyword else self.expression(); self.optional(T.SEMI); self.optional(T.LE)
        return VarDecl(name,val,const,type_name)
    def func_decl(self, after_keyword=False):
        if not after_keyword: self.eat(T.FUNC)
        else: self.eat(T.FUNC)
        name=self.eat(T.IDENT).value; self.eat(T.LPAREN); params=[]
        if not self.check(T.RPAREN):
            while True:
                params.append(self.eat(T.IDENT).value)
                if not self.optional(T.COMMA): break
        self.eat(T.RPAREN); self.eat(T.ARROW); self.eat(T.COLON); body=self.block(); return FuncDecl(name,params,body)
    def block(self):
        s=[]
        while not self.check(T.CLOSE,T.EOF): s.append(self.statement())
        self.eat(T.CLOSE); return Block(s)
    def if_stmt(self):
        self.eat(T.IF); cond=self.expression(); self.eat(T.ARROW); self.eat(T.COLON); then=self.block(); elifs=[]; else_b=None
        while self.check(T.ELSE):
            self.advance()
            if self.optional(T.IF):
                c=self.expression(); self.eat(T.ARROW); self.eat(T.COLON); b=self.block(); elifs.append((c,b))
            else:
                self.eat(T.COLON); else_b=self.block(); break
        return IfStmt(cond,then,elifs,else_b)
    def while_stmt(self):
        self.eat(T.WHILE); c=self.expression(); self.eat(T.ARROW); self.eat(T.COLON); return WhileStmt(c,self.block())
    def for_stmt(self):
        self.eat(T.FOR); name=self.eat(T.IDENT).value; self.eat(T.IN); it=self.expression(); self.eat(T.ARROW); self.eat(T.COLON); return ForStmt(name,it,self.block())
    def try_stmt(self):
        self.eat(T.TRY); self.eat(T.ARROW); self.eat(T.COLON); body=self.block(); self.eat(T.CATCH); err=self.eat(T.IDENT).value; self.eat(T.ARROW); self.eat(T.COLON); return TryStmt(body,err,self.block())
    def expression(self): return self.assignment()
    def expression_legacy(self):
        e=self.or_expr_legacy()
        if self.optional(T.ASSIGN): return Assign(e,self.expression_legacy())
        return e
    def or_expr_legacy(self):
        e=self.and_expr_legacy()
        while self.optional(T.OR): e=Binary(e,'or',self.and_expr_legacy())
        return e
    def and_expr_legacy(self):
        e=self.equality_legacy()
        while self.optional(T.AND): e=Binary(e,'and',self.equality_legacy())
        return e
    def equality_legacy(self):
        e=self.compare_legacy()
        while self.at(T.EQ,T.NE): op=self.advance().value; e=Binary(e,op,self.compare_legacy())
        return e
    def compare_legacy(self):
        e=self.term()
        while self.at(T.GT,T.LT,T.GE): op=self.advance().value; e=Binary(e,op,self.term())
        return e
    def assignment(self):
        e=self.or_expr()
        if self.optional(T.ASSIGN): return Assign(e,self.assignment())
        return e
    def or_expr(self):
        e=self.and_expr()
        while self.optional(T.OR): e=Binary(e,'or',self.and_expr())
        return e
    def and_expr(self):
        e=self.equality()
        while self.optional(T.AND): e=Binary(e,'and',self.equality())
        return e
    def equality(self):
        e=self.compare()
        while self.at(T.EQ,T.NE): op=self.advance().value; e=Binary(e,op,self.compare())
        return e
    def compare(self):
        e=self.term()
        while self.at(T.GT,T.LT,T.GE,T.LE): op=self.advance().value; e=Binary(e,op,self.term())
        if self.optional(T.RANGE): e=RangeExpr(e,self.term())
        return e
    def term(self):
        e=self.factor()
        while self.at(T.PLUS,T.MINUS): op=self.advance().value; e=Binary(e,op,self.factor())
        return e
    def factor(self):
        e=self.power()
        while self.at(T.STAR,T.SLASH,T.PERCENT): op=self.advance().value; e=Binary(e,op,self.power())
        return e
    def power(self):
        e=self.unary()
        if self.optional(T.POWER): e=Binary(e,'^',self.power())
        return e
    def unary(self):
        if self.at(T.NOT,T.MINUS,T.PLUS): return Unary(self.advance().value,self.unary())
        return self.postfix()
    def postfix(self):
        e=self.primary()
        while True:
            if self.optional(T.LPAREN):
                args=[]
                if not self.check(T.RPAREN):
                    while True:
                        args.append(self.expression())
                        if not self.optional(T.COMMA): break
                self.eat(T.RPAREN); e=Call(e,args)
            elif self.optional(T.LBRACKET): idx=self.expression(); self.eat(T.RBRACKET); e=Index(e,idx)
            elif self.optional(T.DOT): e=Member(e,self.eat(T.IDENT).value)
            else: break
        return e
    def primary(self):
        x=self.cur()
        if self.optional(T.NUMBER): return Literal(x.value)
        if self.optional(T.STRING): return Literal(x.value)
        if self.optional(T.TRUE): return Literal(True)
        if self.optional(T.FALSE): return Literal(False)
        if self.optional(T.NULL): return Literal(None)
        if self.optional(T.IDENT): return Variable(x.value)
        if self.optional(T.LBRACKET):
            items=[]
            if not self.check(T.RBRACKET):
                while True:
                    items.append(self.expression())
                    if not self.optional(T.COMMA): break
            self.eat(T.RBRACKET); return ListLiteral(items)
        if self.optional(T.LPAREN): e=self.expression(); self.eat(T.RPAREN); return e
        if self.check(T.CLOSE,T.EOF): raise ECParseError('Se esperaba una expresion.',x,'E2001')
        raise ECParseError(f'Expresion no valida cerca de {x.value!r}.',x,'E2002')
