class Environment:
    def __init__(self,parent=None): self.values={}; self.constants=set(); self.parent=parent
    def declare(self,name,value,const=False):
        if name in self.values: raise RuntimeError(f"'{name}' ya esta declarado en este bloque.")
        self.values[name]=value
        if const: self.constants.add(name)
    def get(self,name):
        if name in self.values: return self.values[name]
        if self.parent: return self.parent.get(name)
        raise RuntimeError(f"Variable '{name}' no esta definida.")
    def assign(self,name,value):
        if name in self.values:
            if name in self.constants: raise RuntimeError(f"La constante '{name}' no puede modificarse.")
            self.values[name]=value; return
        if self.parent: self.parent.assign(name,value); return
        raise RuntimeError(f"Variable '{name}' no esta definida.")
