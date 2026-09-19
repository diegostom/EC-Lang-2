import re
import sys

# =====================================================================
# 1. ANALIZADOR LÉXICO (LEXER) - COMPLETO
# =====================================================================
TOKEN_SPEC = [
    ('COMMENT',   r'\|\|.*?\|\|'),              # Comentarios
    ('ARROW_OP',  r'=>|<=|<=='),                # Operadores de flecha
    ('STRING',    r'"[^"\\]*(?:\\.[^"\\]*)*"'), # Texto
    ('NUMBER',    r'\b\d+(\.\d+)?\b'),          # Números
    ('COMP_OP',   r'==|!=|>=|<=|>|<'),          # Operadores de comparación (¡NUEVO!)
    ('MATH_OP',   r'[\+\-\*/\^%]'),             # Matemáticas
    ('KEYWORD',   r'\b(def|var|func|if)\b'),    # Palabras clave (Añadido 'if')
    ('ID',        r'[a-zA-Z_][a-zA-Z0-9_]*'),   # Identificadores
    ('DOT',       r'\.'),                       # Puntos
    ('LPAREN',    r'\('),                       # (
    ('RPAREN',    r'\)'),                       # )
    ('SEMI',      r';'),                        # ;
    ('COLON',     r':'),                        # :
    ('SKIP',      r'[ \t\n\r]+'),               # Espacios
    ('MISMATCH',  r'.'),                        # Errores
]

def lexer(codigo_fuente):
    tok_regex = '|'.join(f'(?P<{name}>{regex})' for name, regex in TOKEN_SPEC)
    lista_tokens = []
    for mo in re.finditer(tok_regex, codigo_fuente):
        kind = mo.lastgroup
        value = mo.group()
        if kind == 'SKIP' or kind == 'COMMENT': continue
        elif kind == 'STRING': value = value[1:-1]
        elif kind == 'MISMATCH': raise SyntaxError(f"[Lexer Error] Carácter inesperado: '{value}'")
        lista_tokens.append({'tipo': kind, 'valor': value})
    return lista_tokens

# =====================================================================
# 2. ANALIZADOR SINTÁCTICO (PARSER) Y EJECUTOR FINAL
# =====================================================================
class ParserEC:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.tabla_simbolos = {}   
        self.tabla_funciones = {}  

    def token_actual(self):
        if self.pos < len(self.tokens): return self.tokens[self.pos]
        return None

    def consumir(self, tipo_esperado):
        token = self.token_actual()
        if token and token['tipo'] == tipo_esperado:
            self.pos += 1
            return token
        token_val = token['valor'] if token else "FIN DE CÓDIGO"
        raise SyntaxError(f"Se esperaba {tipo_esperado} pero se encontró '{token_val}'")

    def parsear(self):
        while self.pos < len(self.tokens):
            token = self.token_actual()

            if token['tipo'] == 'KEYWORD':
                if token['valor'] == 'def':
                    siguiente = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None
                    if siguiente and siguiente['valor'] == 'var': self.parsear_declaracion()
                    elif siguiente and siguiente['valor'] == 'func': self.parsear_funcion()
                elif token['valor'] == 'if':
                    self.parsear_condicional() # ¡NUEVO!
            
            elif token['tipo'] == 'ID':
                if token['valor'] == 'ec': self.parsear_impresion()
                elif token['valor'] in self.tabla_funciones: self.ejecutar_funcion(token['valor'])
                else: raise NameError(f"Identificador desconocido: '{token['valor']}'")
            
            elif token['tipo'] == 'SEMI' or token['tipo'] == 'ARROW_OP':
                self.pos += 1 # Ignorar operadores sueltos o remanentes de cierres
            else:
                raise SyntaxError(f"Instrucción no reconocida: '{token['valor']}'")

    def parsear_declaracion(self):
        self.consumir('KEYWORD') # def
        self.consumir('KEYWORD') # var
        nombre_variable = self.consumir('ID')['valor']
        siguiente = self.token_actual()
        
        es_matematica = False
        if siguiente and siguiente['tipo'] == 'DOT':
            self.consumir('DOT') 
            token_math = self.consumir('ID')
            if token_math['valor'] != 'math': raise SyntaxError(f"Extensión desconocida '.{token_math['valor']}'")
            es_matematica = True
            nombre_variable = f"{nombre_variable}.math"

        self.consumir('ARROW_OP') # =>
        
        if es_matematica:
            expresion_tokens = []
            while self.pos < len(self.tokens):
                tok = self.token_actual()
                if tok['tipo'] == 'ARROW_OP' and tok['valor'] == '<=': break
                expresion_tokens.append(tok)
                self.pos += 1
            
            expresion_str = ""
            i = 0
            while i < len(expresion_tokens):
                t = expresion_tokens[i]
                if t['tipo'] == 'ID':
                    var_busqueda = t['valor']
                    if i + 2 < len(expresion_tokens) and expresion_tokens[i+1]['tipo'] == 'DOT' and expresion_tokens[i+2]['valor'] == 'math':
                        var_busqueda = f"{var_busqueda}.math"; i += 2
                    expresion_str += str(self.tabla_simbolos[var_busqueda])
                elif t['tipo'] == 'MATH_OP' and t['valor'] == '^': expresion_str += '**'
                else: expresion_str += t['valor']
                i += 1
            
            resultado = eval(expresion_str, {"__builtins__": None}, {})
            self.tabla_simbolos[nombre_variable] = int(resultado) if isinstance(resultado, float) and resultado.is_integer() else resultado
        else:
            self.tabla_simbolos[nombre_variable] = self.consumir('STRING')['valor']
        
        self.consumir('ARROW_OP') # <=

    def parsear_condicional(self):
        """Procesa: if [CONDICION] =>: [CUERPO] <==>"""
        self.consumir('KEYWORD') # if
        
        # Extraemos la condición hasta ver el operador '=>'
        condicion_tokens = []
        while self.pos < len(self.tokens):
            tok = self.token_actual()
            if tok['tipo'] == 'ARROW_OP' and tok['valor'] == '=>': break
            condicion_tokens.append(tok)
            self.pos += 1
            
        self.consumir('ARROW_OP') # =>
        self.consumir('COLON')    # :
        
        # Guardamos el cuerpo del condicional hasta el cierre <==>
        tokens_cuerpo = []
        while self.pos < len(self.tokens):
            tok = self.token_actual()
            if tok['tipo'] == 'ARROW_OP' and tok['valor'] == '<=':
                siguiente = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None
                if siguiente and siguiente['tipo'] == 'ARROW_OP' and siguiente['valor'] == '=>':
                    self.consumir('ARROW_OP') # <=
                    self.consumir('ARROW_OP') # =>
                    break
            tokens_cuerpo.append(tok)
            self.pos += 1

        # Evaluar la condición traduciendo variables .math
        condicion_str = ""
        i = 0
        while i < len(condicion_tokens):
            t = condicion_tokens[i]
            if t['tipo'] == 'ID':
                var_busqueda = t['valor']
                if i + 2 < len(condicion_tokens) and condicion_tokens[i+1]['tipo'] == 'DOT' and condicion_tokens[i+2]['valor'] == 'math':
                    var_busqueda = f"{var_busqueda}.math"; i += 2
                condicion_str += str(self.tabla_simbolos[var_busqueda])
            else:
                condicion_str += t['valor']
            i += 1
            
        # Si la condición es verdadera, ejecutamos el cuerpo
        if eval(condicion_str, {"__builtins__": None}, {}):
            sub_parser = ParserEC(tokens_cuerpo)
            sub_parser.tabla_simbolos = self.tabla_simbolos
            sub_parser.tabla_funciones = self.tabla_funciones
            sub_parser.parsear()

    def parsear_impresion(self):
        self.consumir('ID'); self.consumir('DOT'); self.consumir('ID')
        siguiente = self.token_actual()
        
        if siguiente and siguiente['tipo'] == 'DOT':
            self.consumir('DOT')
            nombre_var = self.consumir('ID')['valor']
            prox = self.token_actual()
            if prox and prox['tipo'] == 'DOT':
                self.consumir('DOT')
                if self.consumir('ID')['valor'] == 'math': nombre_var = f"{nombre_var}.math"
            self.consumir('LPAREN'); self.consumir('RPAREN')
            print(self.tabla_simbolos.get(nombre_var, f"Error: {nombre_var} no definida"))
                
        elif siguiente and siguiente['tipo'] == 'LPAREN':
            self.consumir('LPAREN')
            texto = self.consumir('STRING')['valor']
            self.consumir('RPAREN')
            print(texto)

    def parsear_funcion(self):
        self.consumir('KEYWORD'); self.consumir('KEYWORD')
        nombre_func = self.consumir('ID')['valor']
        self.consumir('ARROW_OP'); self.consumir('COLON')
        
        tokens_cuerpo = []
        while self.pos < len(self.tokens):
            tok = self.token_actual()
            if tok['tipo'] == 'ARROW_OP' and tok['valor'] == '<=':
                siguiente = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None
                if siguiente and siguiente['tipo'] == 'ARROW_OP' and siguiente['valor'] == '=>':
                    self.consumir('ARROW_OP'); self.consumir('ARROW_OP')
                    break
            tokens_cuerpo.append(tok); self.pos += 1
        self.tabla_funciones[nombre_func] = tokens_cuerpo

    def ejecutar_funcion(self, nombre_func):
        self.consumir('ID')
        sub_parser = ParserEC(self.tabla_funciones[nombre_func])
        sub_parser.tabla_simbolos = self.tabla_simbolos; sub_parser.tabla_funciones = self.tabla_funciones
        sub_parser.parsear()

# =====================================================================
# 3. INTERFAZ DE LÍNEA DE COMANDOS (CLI)
# =====================================================================
if __name__ == '__main__':
    if len(sys.argv) > 1:
        try:
            with open(sys.argv[1], 'r', encoding='utf-8') as f: 
                codigo = f.read()
            ParserEC(lexer(codigo)).parsear()
        except Exception as e: 
            print(f"Error: {e}")
    else:
        print("=== ec (Easy Code) ===")
        print("ADVERTENCIA: El lenguaje no esta completo en un mini lenguaje")

        print("haci se emprime texto: ec.print('texto') no pongas esas comillas tienes que poner las comillas dobles en cualquier print pero las estoy usando las comillas de una por que como uso python para este lenguaje en los prints no se permiten usar otras comillas en comillas pero usen lo que les dije ")
        print("o si tienes una variable de texto pon ec.print.nombre()")
        print("haci se se escribe una variable de texto: def var nombre => 'texto' <=")
        print("o una variable matematica: def var nombre.math => 1 * 1 <=")
        print("comentarios: || hola esto es un comentario ||")
        print("condicionales: if nombre.math <= 18 =>: print('eres mayor de edad') <==>")

        interprete_consola = ParserEC([])
        while True:
            try:
                linea = input("ec > ")
                if not linea.strip(): 
                    continue
                interprete_consola.tokens.extend(lexer(linea))
                interprete_consola.parsear()
            except (SyntaxError, NameError) as e: 
                print(e)
            except (KeyboardInterrupt, EOFError): 
                print("\n¡Adiós!")
                break
