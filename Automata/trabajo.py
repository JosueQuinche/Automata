import re
from enum import Enum

# Definición de los tipos de tokens
class TokenType(Enum):
    PALABRA_RESERVADA = 1
    IDENTIFICADOR = 2
    ENTERO = 3
    FLOTANTE = 4
    OPERADOR = 5
    DELIMITADOR = 6
    CADENA = 7
    COMENTARIO = 8
    OPERADOR_COMPUESTO = 9
    HEXADECIMAL = 10
    BOOLEANO = 11
    EOF = 12

# Analizador Léxico
class AnalizadorLexico:
    def __init__(self):
        self.palabras_reservadas = {'if', 'else', 'while', 'for', 'int', 'float', 'return', 'void', 'function', 'class', 'true', 'false'}
        self.operadores = {'+', '-', '*', '/', '=', '<', '>', '!', '&', '|', '%', '^'}
        self.operadores_compuestos = {'==', '!=', '<=', '>=', '&&', '||', '+=', '-=', '*=', '/='}
        self.delimitadores = {'(', ')', '{', '}', '[', ']', ';', ',', ':', '.'}
        self.estado_actual = 'inicio'
        self.lexema = ''
        self.linea = 1
        self.tokens = []
        self.errores = []
        self.estado_num = 0

    def analizar(self, contenido):
        self.estado_actual = 'inicio'
        self.lexema = ''
        self.linea = 1
        self.tokens = []
        self.errores = []

        try:
            with open(contenido, 'r') as archivo:
                contenido = archivo.read()
        except FileNotFoundError:
            print("\nError: Archivo no encontrado.")
            return False

        contenido += ' '
        i = 0

        while i < len(contenido):
            c = contenido[i]

            if self.estado_actual == 'inicio':
                if c.isspace():
                    if c == '\n':
                        self.linea += 1
                    i += 1
                    continue

                if c == '/':
                    if i+1 < len(contenido) and contenido[i+1] == '/':
                        self.estado_actual = 'comentario_linea'
                        i += 1
                    elif i+1 < len(contenido) and contenido[i+1] == '*':
                        self.estado_actual = 'comentario_bloque'
                        i += 1
                    else:
                        self.lexema = c
                        self.estado_actual = 'operador'
                elif c == '"':
                    self.estado_actual = 'cadena'
                    i += 1
                    continue
                elif c.isalpha() or c == '_':
                    self.estado_actual = 'identificador'
                    self.lexema += c
                elif c.isdigit():
                    self.estado_actual = 'entero'
                    self.lexema += c
                elif c in self.operadores:
                    self.lexema += c
                    self.estado_actual = 'operador'
                elif c in self.delimitadores:
                    self.tokens.append((TokenType.DELIMITADOR, c, self.linea, 'q0'))
                else:
                    self.errores.append(f"Línea {self.linea}: Carácter no reconocido '{c}'")
                i += 1

            elif self.estado_actual == 'identificador':
                if c.isalnum() or c == '_':
                    self.lexema += c
                    i += 1
                else:
                    if self.lexema in self.palabras_reservadas:
                        token_type = TokenType.PALABRA_RESERVADA
                        estado = 'q1'
                    elif self.lexema in ['true', 'false']:
                        token_type = TokenType.BOOLEANO
                        estado = 'q10'
                    else:
                        token_type = TokenType.IDENTIFICADOR
                        estado = 'q2'
                    self.tokens.append((token_type, self.lexema, self.linea, estado))
                    self.lexema = ''
                    self.estado_actual = 'inicio'

            elif self.estado_actual == 'entero':
                if c.isdigit():
                    self.lexema += c
                    i += 1
                elif c == '.':
                    self.lexema += c
                    self.estado_actual = 'flotante'
                    i += 1
                elif c.lower() == 'x' and len(self.lexema) == 1 and self.lexema[0] == '0':
                    self.lexema += c
                    self.estado_actual = 'hexadecimal'
                    i += 1
                else:
                    self.tokens.append((TokenType.ENTERO, self.lexema, self.linea, 'q3'))
                    self.lexema = ''
                    self.estado_actual = 'inicio'

            elif self.estado_actual == 'flotante':
                if c.isdigit():
                    self.lexema += c
                    i += 1
                else:
                    self.tokens.append((TokenType.FLOTANTE, self.lexema, self.linea, 'q4'))
                    self.lexema = ''
                    self.estado_actual = 'inicio'

            elif self.estado_actual == 'hexadecimal':
                if c.isdigit() or c.lower() in 'abcdef':
                    self.lexema += c
                    i += 1
                else:
                    self.tokens.append((TokenType.HEXADECIMAL, self.lexema, self.linea, 'q9'))
                    self.lexema = ''
                    self.estado_actual = 'inicio'

            elif self.estado_actual == 'operador':
                if c in self.operadores:
                    self.lexema += c
                    i += 1
                else:
                    if self.lexema in self.operadores_compuestos:
                        self.tokens.append((TokenType.OPERADOR_COMPUESTO, self.lexema, self.linea, 'q8'))
                    else:
                        self.tokens.append((TokenType.OPERADOR, self.lexema, self.linea, 'q5'))
                    self.lexema = ''
                    self.estado_actual = 'inicio'

            elif self.estado_actual == 'cadena':
                if c == '"':
                    self.tokens.append((TokenType.CADENA, self.lexema, self.linea, 'q6'))
                    self.lexema = ''
                    self.estado_actual = 'inicio'
                    i += 1
                elif c == '\n':
                    self.errores.append(f"Línea {self.linea}: Cadena no cerrada")
                    self.lexema = ''
                    self.estado_actual = 'inicio'
                else:
                    self.lexema += c
                    i += 1

            elif self.estado_actual == 'comentario_linea':
                if c == '\n':
                    self.tokens.append((TokenType.COMENTARIO, self.lexema, self.linea, 'q7'))
                    self.lexema = ''
                    self.estado_actual = 'inicio'
                    self.linea += 1
                else:
                    self.lexema += c
                    i += 1

            elif self.estado_actual == 'comentario_bloque':
                if c == '*' and i+1 < len(contenido) and contenido[i+1] == '/':
                    self.tokens.append((TokenType.COMENTARIO, self.lexema, self.linea, 'q7'))
                    self.lexema = ''
                    self.estado_actual = 'inicio'
                    i += 2
                elif c == '\n':
                    self.linea += 1
                    i += 1
                else:
                    self.lexema += c
                    i += 1

        self.tokens.append((TokenType.EOF, 'EOF', self.linea, 'q12'))
        return True

    def imprimir_resultados(self):
        print("\n════════════════ TOKENS ENCONTRADOS ════════════════")
        print("{:<20} {:<30} {:<10} {:<10}".format('TIPO', 'LEXEMA', 'LÍNEA', 'ESTADO'))
        print("-" * 70)
        for token in self.tokens:
            print("{:<20} {:<30} {:<10} {:<10}".format(
                token[0].name,
                repr(token[1])[1:-1],
                token[2],
                token[3]
            ))

        if self.errores:
            print("\n══════════════════ ERRORES ══════════════════")
            for error in self.errores:
                print(error)

# Ejecución principal
if __name__ == "__main__":
    analizador = AnalizadorLexico()
    nombre_archivo = input("\nIngrese la ruta del archivo .txt a analizar: ")

    if analizador.analizar(nombre_archivo):
        analizador.imprimir_resultados()

    input("\nPresione cualquier tecla para salir...")
