# EC 2.0 — Easy Code

A modular, executable implementation of the EC 2.0 language.

## Requirements
Python 3.10+.

## Execution

```bash
python main.py examples/01_hola.ec
python main.py examples/05_funciones.ec
```

REPL:

```bash
python main.py
```

## Features

- Variables and constants
- `int`, `float`, `string`, `bool`, `list`, `null`
- Expressions and logical operators
- `if / else if / else`
- `while` and `for ... in ...`
- `break` and `continue`
- Functions with parameters and `return`
- Lists, indexing, and basic methods
- Strings and `{variable}` interpolation
- `ec.print`, `ec.input`, `ec.clear`, `ec.sleep`, `ec.exit`
- `math` library
- `try / catch / throw`
- AST and separate lexical environments

## Block Syntax

EC preserves the identity of the original version:

```ec
if condicion =>:
    ec.print("Hola");
<==>
```

Functions use:

```ec
func sumar(a, b) =>:
    return a + b;
<==>
```

## Architecture

`source -> lexer -> tokens -> parser -> AST -> interpreter -> runtime`

Version 2.0 lays the groundwork for dictionaries, classes, external modules, and bytecode.

## `ec` Runner

### Windows (uncompiled)

```bat
ec.bat examples\01_hola.ec
```

### Generating `ec.exe`

Requires PyInstaller:

```bat
python -m pip install pyinstaller
build_ec.bat
```

The output is located at `dist\\ec.exe` and uses `ec.ico` as the icon.
