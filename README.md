# 🔍 Analizador Léxico en Python

Este proyecto implementa un **analizador léxico** en Python, diseñado como un **autómata finito determinista (AFD)** capaz de leer archivos fuente `.txt`, identificar tokens válidos (como palabras reservadas, identificadores, números, operadores, delimitadores, etc.), y reportar errores léxicos.

---

## 📌 Características

- Lectura de archivos fuente `.txt`
- Reconocimiento de:
  - Palabras reservadas (`if`, `while`, `return`, etc.)
  - Identificadores
  - Números enteros, flotantes y hexadecimales
  - Operadores simples y compuestos
  - Cadenas de texto
  - Comentarios de línea y de bloque
  - Delimitadores
- Detección de errores léxicos como caracteres no válidos o cadenas no cerradas
- Imprime una tabla con los tokens reconocidos y otra con errores encontrados
- Simulación de un AFD para cada tipo de token

---

## ⚙️ Requisitos

- Python 3.8 o superior
- Sistema operativo: Windows, Linux o macOS

---

## ▶️ Cómo ejecutar el programa

1. **Clona el repositorio:**

```bash
git clone https://github.com/tu-usuario/analizador-lexico-python.git
cd analizador-lexico-python
python analizador_lexico.py
