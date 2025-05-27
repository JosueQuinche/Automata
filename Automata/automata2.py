import re
import os
from enum import Enum
'from graphviz import Digraph'

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

class AnalizadorLexico:
    def __init__(self):
        self.palabras_reservadas = {
            'if', 'else', 'while', 'for', 'int', 'float',
            'return', 'void', 'function', 'class', 'true', 'false'
        }
        self.operadores = {'+', '-', '*', '/', '=', '<', '>', '!', '&', '|', '%', '^'}
        self.operadores_compuestos = {
            '==', '!=', '<=', '>=', '&&', '||', '+=', '-=', '*=', '/='
        }
        self.delimitadores = {'(', ')', '{', '}', '[', ']', ';', ',', ':', '.'}
        self.estado_actual = 'inicio'
        self.lexema = ''
        self.linea = 1
        self.tokens = []
        self.errores = []

    def analizar_archivo(self, nombre_archivo):
        try:
            with open(nombre_archivo, 'r', encoding='utf-8') as archivo:
                contenido = archivo.read()
                self.analizar(contenido)
                return True
        except FileNotFoundError:
            print(f"\nError: El archivo '{nombre_archivo}' no existe.")
            return False
        except UnicodeDecodeError:
            print("\nError: Codificación del archivo no compatible (usar UTF-8).")
            return False
        except Exception as e:
            print(f"\nError inesperado: {str(e)}")
            return False

    def analizar(self, contenido):
        self.estado_actual = 'inicio'
        self.lexema = ''
        self.linea = 1
        self.tokens = []
        self.errores = []

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
                    if i + 1 < len(contenido) and contenido[i+1] == '/':
                        self.estado_actual = 'comentario_linea'
                        i += 1
                    elif i + 1 < len(contenido) and contenido[i+1] == '*':
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
                    self.tokens.append((TokenType.DELIMITADOR, c, self.linea))
                else:
                    self.errores.append(f"Línea {self.linea}: Carácter no reconocido '{c}'")
                i += 1

            elif self.estado_actual == 'identificador':
                if c.isalnum() or c == '_':
                    self.lexema += c
                    i += 1
                else:
                    self._procesar_identificador()
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
                    self.tokens.append((TokenType.ENTERO, self.lexema, self.linea))
                    self.lexema = ''
                    self.estado_actual = 'inicio'

            elif self.estado_actual == 'flotante':
                if c.isdigit():
                    self.lexema += c
                    i += 1
                else:
                    self._procesar_flotante()
                    self.estado_actual = 'inicio'

            elif self.estado_actual == 'hexadecimal':
                if c.isdigit() or c.lower() in 'abcdef':
                    self.lexema += c
                    i += 1
                else:
                    self._procesar_hexadecimal()
                    self.estado_actual = 'inicio'

            elif self.estado_actual == 'operador':
                if c in self.operadores:
                    self.lexema += c
                    i += 1
                else:
                    self._procesar_operador()
                    self.estado_actual = 'inicio'

            elif self.estado_actual == 'cadena':
                if c == '"':
                    self.tokens.append((TokenType.CADENA, self.lexema, self.linea))
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
                    self.tokens.append((TokenType.COMENTARIO, self.lexema, self.linea))
                    self.lexema = ''
                    self.estado_actual = 'inicio'
                    self.linea += 1
                else:
                    self.lexema += c
                i += 1

            elif self.estado_actual == 'comentario_bloque':
                if c == '*' and i + 1 < len(contenido) and contenido[i+1] == '/':
                    self.tokens.append((TokenType.COMENTARIO, self.lexema, self.linea))
                    self.lexema = ''
                    self.estado_actual = 'inicio'
                    i += 2
                elif c == '\n':
                    self.linea += 1
                    i += 1
                else:
                    self.lexema += c
                    i += 1

        self.tokens.append((TokenType.EOF, 'EOF', self.linea))

    def _procesar_identificador(self):
        if self.lexema in self.palabras_reservadas:
            token_type = TokenType.PALABRA_RESERVADA
        elif self.lexema in ['true', 'false']:
            token_type = TokenType.BOOLEANO
        else:
            token_type = TokenType.IDENTIFICADOR
        self.tokens.append((token_type, self.lexema, self.linea))
        self.lexema = ''

    def _procesar_flotante(self):
        if self.lexema.count('.') == 1 and len(self.lexema) > 1:
            self.tokens.append((TokenType.FLOTANTE, self.lexema, self.linea))
        else:
            self.errores.append(f"Línea {self.linea}: Número flotante inválido '{self.lexema}'")
        self.lexema = ''

    def _procesar_hexadecimal(self):
        if len(self.lexema) > 2 and all(c in '0123456789abcdefABCDEF' for c in self.lexema[2:]):
            self.tokens.append((TokenType.HEXADECIMAL, self.lexema, self.linea))
        else:
            self.errores.append(f"Línea {self.linea}: Hexadecimal inválido '{self.lexema}'")
        self.lexema = ''

    def _procesar_operador(self):
        if self.lexema in self.operadores_compuestos:
            self.tokens.append((TokenType.OPERADOR_COMPUESTO, self.lexema, self.linea))
        elif self.lexema in self.operadores:
            self.tokens.append((TokenType.OPERADOR, self.lexema, self.linea))
        else:
            self.errores.append(f"Línea {self.linea}: Operador inválido '{self.lexema}'")
        self.lexema = ''

    def imprimir_resultados(self):
        print("\n════════════════ TOKENS ENCONTRADOS ════════════════")
        print("{:<20} {:<30} {:<10}".format('TIPO', 'LEXEMA', 'LÍNEA'))
        print("-" * 60)
        for token in self.tokens:
            print("{:<20} {:<30} {:<10}".format(
                token[0].name,
                repr(token[1])[1:-1],
                token[2]
            ))

        if self.errores:
            print("\n══════════════════ ERRORES ══════════════════")
            for error in self.errores:
                print(error)

    def graficar_automata(self):
        dot = 'Digraph'(comment='Autómata Léxico')
        estados = ['q0', 'q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7', 'q8', 'q9']
        for estado in estados:
            shape = 'doublecircle' if estado in {'q1', 'q2', 'q3', 'q5', 'q7', 'q8'} else 'circle'
            dot.node(estado, estado, shape=shape)
        dot.edge('q0', 'q1', label='letra/_')
        dot.edge('q1', 'q1', label='letra/dígito')
        dot.edge('q0', 'q2', label='dígito')
        dot.edge('q2', 'q2', label='dígito')
        dot.edge('q2', 'q3', label='.')
        dot.edge('q3', 'q3', label='dígito')
        dot.edge('q0', 'q4', label='"')
        dot.edge('q4', 'q4', label='otro')
        dot.edge('q4', 'q5', label='"')
        dot.edge('q0', 'q6', label='/')
        dot.edge('q6', 'q7', label='/')
        dot.edge('q6', 'q8', label='*')
        dot.edge('q0', 'q9', label='operador')

        dot.render('automata', format='png', cleanup=True)
        print("\n✅ Gráfico generado como 'automata.png'")
        try:
            os.startfile('automata.png')  # Windows
        except:
            pass  # Para Linux/macOS usar xdg-open o open si lo deseas

if __name__ == "__main__":
    analizador = AnalizadorLexico()
    nombre_archivo = input("\nIngrese la ruta del archivo .txt a analizar: ")

    if analizador.analizar_archivo(nombre_archivo):
        analizador.imprimir_resultados()
        analizador.graficar_automata()

    input("\nPresione cualquier tecla para salir...")
