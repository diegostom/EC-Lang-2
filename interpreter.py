import math, random, time, os
from ec_ast import *
from environment import Environment
from errors import ReturnSignal, BreakSignal, ContinueSignal, ECRuntimeError

class UserFunction:
    def __init__(self,decl,closure): self.decl=decl; self.closure=closure
    def call(self,interp,args):
        if len(args)!=len(self.decl.params): raise RuntimeError(f"'{self.decl.name}' esperaba {len(self.decl.params)} argumentos y recibio {len(args)}.")
        env=Environment(self.closure)
        for n,v in zip(self.decl.params,args): env.declare(n,v)
        try: interp.exec_block(self.decl.body,env)
        except ReturnSignal as r: return r.value
        return None

class Builtin:
    def __init__(self,name,fn): self.name=name; self.fn=fn
    def call(self,interp,args): return self.fn(*args)

class Namespace:
    def __init__(self,**attrs): self.attrs=attrs

class Interpreter:
    def __init__(self,output=print,input_fn=input):
        self.output=output; self.input=input_fn; self.globals=Environment(); self.env=self.globals; self.install_builtins()
    def install_builtins(self):
        ec=Namespace(
            print=Builtin('ec.print',lambda *a:self.output(*[self.stringify(x) for x in a]) or None),
            input=Builtin('ec.input',lambda prompt='':self.input(self.stringify(prompt))),
            clear=Builtin('ec.clear',lambda:os.system('cls' if os.name=='nt' else 'clear')),
            sleep=Builtin('ec.sleep',lambda ms:time.sleep(float(ms)/1000)),
            exit=Builtin('ec.exit',lambda code=0:(_ for _ in ()).throw(SystemExit(int(code))))
        )
        mathns=Namespace(**{k:Builtin(f'math.{k}',v) for k,v in {
            'sqrt':math.sqrt,'pow':pow,'abs':abs,'round':round,'floor':math.floor,'ceil':math.ceil,
            'sin':math.sin,'cos':math.cos,'tan':math.tan,'log':math.log,'random':random.random}.items()})
        listns=Namespace(sort=Builtin('list.sort',lambda xs:sorted(xs)),len=Builtin('list.len',lambda xs:len(xs)))
        self.globals.declare('ec',ec,const=True); self.globals.declare('math',mathns,const=True); self.globals.declare('list',listns,const=True)
        self.globals.declare('int',Builtin('int',lambda x=0:int(x)),const=True); self.globals.declare('float',Builtin('float',lambda x=0:float(x)),const=True)
        self.globals.declare('string',Builtin('string',lambda x='':self.stringify(x)),const=True); self.globals.declare('bool',Builtin('bool',lambda x=False:bool(x)),const=True)
    def run(self,program):
        try: self.exec_program(program)
        except ReturnSignal: raise RuntimeError('return fuera de una funcion.')
        except (BreakSignal,ContinueSignal): raise RuntimeError('break/continue fuera de un bucle.')
    def exec_program(self,p):
        for s in p.statements: self.exec(s)
    def exec_block(self,b,env=None):
        old=self.env; self.env=env or Environment(old)
        try:
            for s in b.statements: self.exec(s)
        finally: self.env=old
    def exec(self,n):
        if isinstance(n,VarDecl):
            v=self.eval(n.value); v=self.coerce(n.type_name,v); self.env.declare(n.name,v,n.const)
        elif isinstance(n,ExprStmt): self.eval(n.expr)
        elif isinstance(n,FuncDecl): self.env.declare(n.name,UserFunction(n,self.env))
        elif isinstance(n,Assign): self.assign_target(n.target,self.eval(n.value))
        elif isinstance(n,IfStmt):
            if self.truth(self.eval(n.condition)): self.exec_block(n.then)
            else:
                done=False
                for c,b in n.elifs:
                    if self.truth(self.eval(c)): self.exec_block(b); done=True; break
                if not done and n.else_block: self.exec_block(n.else_block)
        elif isinstance(n,WhileStmt):
            guard=0
            while self.truth(self.eval(n.condition)):
                guard+=1
                if guard>10_000_000: raise RuntimeError('Bucle excesivo; posible bucle infinito.')
                try:self.exec_block(n.body)
                except ContinueSignal:continue
                except BreakSignal:break
        elif isinstance(n,ForStmt):
            seq=self.eval(n.iterable)
            if isinstance(seq,(int,float)): seq=range(int(seq))
            if isinstance(seq,str): seq=list(seq)
            for item in seq:
                loopenv=Environment(self.env); loopenv.declare(n.name,item)
                try:self.exec_block(n.body,loopenv)
                except ContinueSignal:continue
                except BreakSignal:break
        elif isinstance(n,ReturnStmt): raise ReturnSignal(None if n.value is None else self.eval(n.value))
        elif isinstance(n,BreakStmt): raise BreakSignal()
        elif isinstance(n,ContinueStmt): raise ContinueSignal()
        elif isinstance(n,TryStmt):
            try:self.exec_block(n.body)
            except Exception as e:
                env=Environment(self.env); env.declare(n.error_name,str(e)); self.exec_block(n.catch,env)
        elif isinstance(n,ThrowStmt): raise RuntimeError(self.stringify(self.eval(n.expr)))
        elif isinstance(n,ImportStmt):
            if n.name not in ('math','ec'): raise RuntimeError(f"Modulo '{n.name}' no disponible en EC 2.0.")
        else: self.eval(n)
    def eval(self,n):
        if isinstance(n,Literal): return n.value
        if isinstance(n,Variable): return self.env.get(n.name)
        if isinstance(n,ListLiteral): return [self.eval(x) for x in n.items]
        if isinstance(n,RangeExpr): return range(int(self.eval(n.start)), int(self.eval(n.end))+1)
        if isinstance(n,Unary):
            v=self.eval(n.expr); return (not self.truth(v)) if n.op=='not' else (-v if n.op=='-' else +v)
        if isinstance(n,Binary):
            if n.op=='and': return self.truth(self.eval(n.left)) and self.truth(self.eval(n.right))
            if n.op=='or': return self.truth(self.eval(n.left)) or self.truth(self.eval(n.right))
            a,b=self.eval(n.left),self.eval(n.right)
            try:
                return {'+':lambda:a+b,'-':lambda:a-b,'*':lambda:a*b,'/':lambda:a/b,'%':lambda:a%b,'^':lambda:a**b,
                        '==':lambda:a==b,'!=':lambda:a!=b,'>':lambda:a>b,'<':lambda:a<b,'>=':lambda:a>=b,'<=':lambda:a<=b}[n.op]()
            except KeyError: raise RuntimeError(f'Operador desconocido {n.op}')
        if isinstance(n,Call):
            callee=self.eval(n.callee); args=[self.eval(x) for x in n.args]
            if not hasattr(callee,'call'): raise RuntimeError('El objeto no es invocable.')
            return callee.call(self,args)
        if isinstance(n,Index): return self.eval(n.obj)[self.eval(n.index)]
        if isinstance(n,Member):
            obj=self.eval(n.obj)
            if isinstance(obj,Namespace):
                try:return obj.attrs[n.name]
                except KeyError: raise RuntimeError(f"Miembro '{n.name}' no existe.")
            if isinstance(obj,list) and n.name=='length': return Builtin('list.length',lambda:len(obj))
            if isinstance(obj,str) and n.name=='length': return Builtin('string.length',lambda:len(obj))
            if isinstance(obj,str) and n.name in ('upper','lower'):
                return Builtin(f'string.{n.name}',getattr(obj,n.name))
            if isinstance(obj,list) and n.name in ('push','pop'):
                if n.name=='push': return Builtin('list.push',lambda x:(obj.append(x),None)[1])
                return Builtin('list.pop',lambda:obj.pop())
            raise RuntimeError(f"No existe el miembro '{n.name}'.")
        if isinstance(n,Assign): return self.assign_target(n.target,self.eval(n.value))
        raise RuntimeError(f'Nodo AST no soportado: {type(n).__name__}')
    def assign_target(self,t,v):
        if isinstance(t,Variable): self.env.assign(t.name,v); return v
        if isinstance(t,Index): self.eval(t.obj)[self.eval(t.index)]=v; return v
        raise RuntimeError('El destino de asignacion no es valido.')
    def coerce(self,typ,v):
        if not typ:return v
        return {'int':int,'float':float,'string':self.stringify,'bool':bool}.get(typ,lambda x:x)(v)
    def truth(self,v): return bool(v)
    def stringify(self,v):
        if isinstance(v,bool): return 'true' if v else 'false'
        if v is None:return 'null'
        if isinstance(v,str):
            return self.interpolate(v)
        if isinstance(v,list):
            return '[' + ', '.join(self.stringify(x) for x in v) + ']'
        return str(v)
    def interpolate(self,text):
        import re
        def repl(m):
            expr=m.group(1).strip()
            try:
                from lexer import Lexer
                from parser import Parser
                node=Parser(Lexer(expr).run()).parse()
                if len(node.statements)!=1 or not isinstance(node.statements[0], ExprStmt):
                    return m.group(0)
                return self.stringify(self.eval(node.statements[0].expr))
            except Exception:
                # A missing interpolation name remains visible rather than hiding an error.
                return m.group(0)
        return re.sub(r'\{([^{}]+)\}', repl, text)
