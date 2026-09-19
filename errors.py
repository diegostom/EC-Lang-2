class ECError(Exception):
    def __init__(self, message, token=None, code='E0000'):
        self.message = message
        self.token = token
        self.code = code
        super().__init__(message)

    def pretty(self, source_lines=None, filename='<stdin>'):
        if not self.token:
            return f'EC Error [{self.code}]\n\n{self.message}'
        line = self.token.line
        col = self.token.column
        out = [f'EC Error [{self.code}]', f'Archivo: {filename}', f'Linea: {line}, Columna: {col}', '', self.message]
        if source_lines and 1 <= line <= len(source_lines):
            text = source_lines[line-1]
            out += ['', f'    {line} | {text}', ' ' * (7 + max(0,col-1)) + '^']
        return '\n'.join(out)

class ECLexError(ECError): pass
class ECParseError(ECError): pass
class ECRuntimeError(ECError): pass

class ReturnSignal(Exception):
    def __init__(self, value): self.value = value
class BreakSignal(Exception): pass
class ContinueSignal(Exception): pass
