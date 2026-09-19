import re
from tokens import Token, TokenType
from errors import ECLexError

KEYWORDS = {
    'def': TokenType.DEF, 'var': TokenType.VAR, 'const': TokenType.CONST, 'func': TokenType.FUNC,
    'if': TokenType.IF, 'else': TokenType.ELSE, 'while': TokenType.WHILE,
    'for': TokenType.FOR, 'in': TokenType.IN, 'return': TokenType.RETURN,
    'break': TokenType.BREAK, 'continue': TokenType.CONTINUE, 'true': TokenType.TRUE,
    'false': TokenType.FALSE, 'null': TokenType.NULL, 'import': TokenType.IMPORT,
    'and': TokenType.AND, 'or': TokenType.OR, 'not': TokenType.NOT,
    'try': TokenType.TRY, 'catch': TokenType.CATCH, 'throw': TokenType.THROW,
}

class Lexer:
    def __init__(self, source):
        self.s = source; self.i = 0; self.line = 1; self.col = 1
        self.tokens = []

    def advance(self, n=1):
        for _ in range(n):
            if self.i >= len(self.s): return
            c = self.s[self.i]; self.i += 1
            if c == '\n': self.line += 1; self.col = 1
            else: self.col += 1

    def add(self, typ, val, line, col): self.tokens.append(Token(typ, val, line, col))

    def run(self):
        while self.i < len(self.s):
            c = self.s[self.i]
            if c.isspace(): self.advance(); continue
            if self.s.startswith('//', self.i):
                while self.i < len(self.s) and self.s[self.i] != '\n': self.advance()
                continue
            if self.s.startswith('||', self.i):
                start_line, start_col = self.line, self.col; self.advance(2)
                while self.i < len(self.s) and not self.s.startswith('||', self.i): self.advance()
                if self.i >= len(self.s): raise ECLexError('Comentario || sin cierre.', Token(TokenType.SEMI,'',start_line,start_col),'E1001')
                self.advance(2); continue
            line,col=self.line,self.col
            if self.s.startswith('<==>', self.i): self.add(TokenType.CLOSE,'<==>',line,col); self.advance(4); continue
            if self.s.startswith('=>', self.i): self.add(TokenType.ARROW,'=>',line,col); self.advance(2); continue
            if self.s.startswith('==', self.i): self.add(TokenType.EQ,'==',line,col); self.advance(2); continue
            if self.s.startswith('!=', self.i): self.add(TokenType.NE,'!=',line,col); self.advance(2); continue
            if self.s.startswith('>=', self.i): self.add(TokenType.GE,'>=',line,col); self.advance(2); continue
            if self.s.startswith('<=', self.i): self.add(TokenType.LE,'<=',line,col); self.advance(2); continue
            if self.s.startswith('..', self.i): self.add(TokenType.RANGE,'..',line,col); self.advance(2); continue
            if c in '"\'':
                quote=c; self.advance(); chars=[]
                while self.i < len(self.s) and self.s[self.i] != quote:
                    if self.s[self.i]=='\\':
                        self.advance()
                        if self.i>=len(self.s): break
                        esc=self.s[self.i]; chars.append({'n':'\n','t':'\t','r':'\r'}.get(esc,esc)); self.advance()
                    else: chars.append(self.s[self.i]); self.advance()
                if self.i>=len(self.s): raise ECLexError('Cadena sin cierre.',Token(TokenType.STRING,'',line,col),'E1002')
                self.advance(); self.add(TokenType.STRING,''.join(chars),line,col); continue
            m=re.match(r'(?:\d+\.\d+|\d+)', self.s[self.i:])
            if m:
                text=m.group(); self.advance(len(text)); val=float(text) if '.' in text else int(text); self.add(TokenType.NUMBER,val,line,col); continue
            m=re.match(r'[A-Za-z_][A-Za-z0-9_]*', self.s[self.i:])
            if m:
                text=m.group(); self.advance(len(text)); self.add(KEYWORDS.get(text,TokenType.IDENT),text,line,col); continue
            single={'+':TokenType.PLUS,'-':TokenType.MINUS,'*':TokenType.STAR,'/':TokenType.SLASH,'%':TokenType.PERCENT,'^':TokenType.POWER,
                    '=':TokenType.ASSIGN,'>':TokenType.GT,'<':TokenType.LT,'(':TokenType.LPAREN,')':TokenType.RPAREN,
                    '[':TokenType.LBRACKET,']':TokenType.RBRACKET,',':TokenType.COMMA,'.':TokenType.DOT,':':TokenType.COLON,';':TokenType.SEMI}
            if c in single:
                self.add(single[c],c,line,col); self.advance(); continue
            raise ECLexError(f"Caracter inesperado: '{c}'",Token(TokenType.SEMI,c,line,col),'E1000')
        self.tokens.append(Token(TokenType.EOF,'',self.line,self.col)); return self.tokens
