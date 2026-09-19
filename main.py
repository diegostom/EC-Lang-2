import sys
from lexer import Lexer
from parser import Parser
from interpreter import Interpreter
from errors import ECError

VERSION='2.0.0'

def execute(source, filename='<stdin>'):
    tokens=Lexer(source).run()
    program=Parser(tokens).parse()
    Interpreter().run(program)

def repl():
    print(f'EC {VERSION} - Easy Code 2.0')
    print('Escribe .help para ver los comandos.')
    buffer=''
    while True:
        try:
            line=input('ec > ')
            if line.strip()=='.exit': break
            if line.strip()=='.version': print(VERSION); continue
            if line.strip()=='.help': print('.help  .version  .exit  .clear'); continue
            if line.strip()=='.clear': print('\n'*40); continue
            buffer += line+'\n'
            # Ejecuta una linea o bloque cuando aparecen suficientes delimitadores.
            if '<==>' not in buffer and (line.rstrip().endswith(';') or not line.strip().endswith(':')):
                Interpreter().run(Parser(Lexer(buffer).run()).parse()); buffer=''
            elif buffer.count('<==>')>=1:
                Interpreter().run(Parser(Lexer(buffer).run()).parse()); buffer=''
        except (EOFError,KeyboardInterrupt): print('\nAdios!'); break
        except ECError as e: print(e.pretty(buffer.splitlines())); buffer=''
        except Exception as e: print(f'EC Runtime Error: {e}'); buffer=''

def main():
    if len(sys.argv)==1: repl(); return
    if sys.argv[1] in ('--version','-v'): print(VERSION); return
    path=sys.argv[1]
    try:
        with open(path,'r',encoding='utf-8') as f: src=f.read()
        execute(src,path)
    except ECError as e: print(e.pretty(src.splitlines(),path)); sys.exit(1)
    except Exception as e: print(f'EC Runtime Error: {e}'); sys.exit(1)

if __name__=='__main__': main()
