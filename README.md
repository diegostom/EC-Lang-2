# EC 2.0 — Easy Code

Implementación modular y ejecutable del lenguaje EC 2.0.

## Requisitos
Python 3.10+.

## Ejecutar

```bash
python main.py examples/01_hola.ec
python main.py examples/05_funciones.ec
```

REPL:

```bash
python main.py
```

## Características

- Variables y constantes
- `int`, `float`, `string`, `bool`, `list`, `null`
- Expresiones y operadores lógicos
- `if / else if / else`
- `while` y `for ... in ...`
- `break` y `continue`
- Funciones con parámetros y `return`
- Listas, índices y métodos básicos
- Strings e interpolación `{variable}`
- `ec.print`, `ec.input`, `ec.clear`, `ec.sleep`, `ec.exit`
- Biblioteca `math`
- `try / catch / throw`
- AST y entornos léxicos separados

## Sintaxis de bloques

EC conserva la identidad de tu versión original:

```ec
if condicion =>:
    ec.print("Hola");
<==>
```

Las funciones usan:

```ec
func sumar(a, b) =>:
    return a + b;
<==>
```

## Arquitectura

`source -> lexer -> tokens -> parser -> AST -> interpreter -> runtime`

La versión 2.0 deja preparada la base para diccionarios, clases, módulos externos y bytecode.

## Ejecutador `ec`

### Windows (sin compilar)

```bat
ec.bat examples\01_hola.ec
```

### Generar `ec.exe`

Requiere PyInstaller:

```bat
python -m pip install pyinstaller
build_ec.bat
```

El resultado queda en `dist\\ec.exe` y usa `ec.ico` como icono.
