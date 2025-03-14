# Documentación del Analizador Sintáctico Predictivo

## 1. Gramática del Lenguaje

### 1.1 Estructura Básica
```ebnf
Programa → START CODE FINISH
START → "= ^ ."
FINISH → ". ^ ="
CODE → Statement CODE | ε
```

### 1.2 Declaraciones y Variables
```ebnf
Statement → VarDec | Print | ExpressionStatement | Method | Conditions | Loops | Array_Dec | Input | Comment | Break | Continue | Return
VarDec → "DECVARinter" VarList "EndDecinter"
VarList → VarDecItem RestVarList
VarDecItem → ID ":" TYPE
RestVarList → "," VarDecItem RestVarList | ε
```

### 1.3 Expresiones
```ebnf
ExpressionStatement → ID ExpressionStatementTail
ExpressionStatementTail → "=" Expresion ":3" | "[" Expresion "]" "=" Expresion ":3"
Expresion → Factor ExprTail
ExprTail → OP_ARIT Factor ExprTail | OP_REL Factor ExprTail | OP_LOG Factor ExprTail | ε
Factor → ID | NUMBER | BOOLEAN | "(" Expresion ")" | OP_LOG Factor
```

### 1.4 Estructuras de Control
```ebnf
Conditions → "Siinter" "(" Condition ")" Block OptionalElse
Block → "{" CODE "}"
OptionalElse → "Sinointer" Block | ε
Loops → "Mientinter" "(" Condition ")" Block | 
        "Forinter" "(" ForInit ";" Condition ";" ExpressionStatement ")" Block
```

### 1.5 Métodos y Arrays
```ebnf
Method → "Methodinter" ID "(" ParamList ")" Block
ParamList → ParamItem RestParams | ε
ParamItem → TYPE ID
RestParams → "," ParamItem RestParams | ε
Array_Dec → "ARRAYinter" ID "[" ArraySize "]" ":" TYPE ":3"
ArraySize → NUMBER | ID
```

### 1.6 Entrada/Salida y Control de Flujo
```ebnf
Print → "Mostrinter" "(" Printable ")" ":3"
Input → "LEERinter" "(" ID ")" ":3"
Break → "BREAKinter" ":3"
Continue → "CONTINUEinter" ":3"
Return → "Returninter" Expresion ":3"
```

## 2. Tabla de Análisis Predictivo

La tabla de análisis predictivo completa se encuentra en el archivo `Tabla.txt`. Algunas entradas importantes incluyen:

- Para declaraciones de variables: `VarDec → DECVARinter VarList EndDecinter`
- Para estructuras de control: `Conditions → Siinter "(" Condition ")" Block OptionalElse`
- Para expresiones: `Expresion → Factor ExprTail`
- Para métodos: `Method → Methodinter ID "(" ParamList ")" Block`

## 3. Funcionamiento del Analizador

### 3.1 Análisis Léxico
El analizador léxico (Lexer) realiza las siguientes funciones:
- Tokeniza el código fuente usando expresiones regulares
- Reconoce identificadores, palabras clave, operadores y símbolos
- Mantiene un seguimiento de los números de línea
- Ignora espacios en blanco y comentarios cuando es apropiado

### 3.2 Análisis Sintáctico
El analizador sintáctico (Parser) implementa:
- Análisis predictivo recursivo descendente
- Manejo de errores con modo pánico
- Sincronización en puntos clave del código
- Recuperación de errores para continuar el análisis

### 3.3 Manejo de Errores
El sistema incluye:
- Detección y reporte de errores sintácticos
- Tokens de sincronización para recuperación
- Acumulación de múltiples errores en una pasada
- Mensajes de error descriptivos con números de línea

## 4. Casos de Prueba

### 4.1 Declaración de Variables
```python
= ^ .
DECVARinter
    x: INTer,
    y: FLOATer,
    z: STRINGer,
    flag: BOOLEANter
EndDecinter
. ^ =
```

### 4.2 Operaciones y Asignaciones
```python
= ^ .
DECVARinter
    x: INTer,
    y: INTer,
    result: BOOLEANter
EndDecinter
x = 5 + 3 * 2:3
y = x - 1:3
result = (x > y) ANDter (y >= 0) ORter (x == 10):3
. ^ =
```

### 4.3 Estructuras de Control
```python
= ^ .
Siinter(x > 0) {
    Mientinter(x > 0) {
        Mostrinter(x):3
        x = x - 1:3
        Siinter(x == 5) {
            BREAKinter:3
        }
    }
} Sinointer {
    Mostrinter("No positivo"):3
}
. ^ =
```

### 4.4 Arrays y Bucles
```python
= ^ .
ARRAYinter numbers[10]: INTer:3
Forinter(DECVARinter i: INTer EndDecinter; i < 10; i = i + 1) {
    numbers[i] = i * 2:3
    Mostrinter(numbers[i]):3
}
. ^ =
```

### 4.5 Métodos
```python
= ^ .
Methodinter Factorial(INTer n) {
    DECVARinter
        result: INTer
    EndDecinter
    result = 1:3
    Mientinter(n > 0) {
        result = result * n:3
        n = n - 1:3
    }
    Returninter result:3
}
. ^ =
```

## 5. Resultados de las Pruebas

Los casos de prueba demuestran que el analizador:
- Reconoce correctamente la sintaxis básica del lenguaje
- Maneja adecuadamente las estructuras de control anidadas
- Procesa correctamente expresiones aritméticas y lógicas
- Identifica y reporta errores sintácticos
- Se recupera de errores y continúa el análisis
- Maneja correctamente los diferentes tipos de datos y declaraciones

### 5.1 Casos Válidos
- Declaraciones de variables
- Operaciones aritméticas y lógicas
- Estructuras de control anidadas
- Definición de métodos
- Expresiones booleanas complejas

### 5.2 Casos Inválidos (Detección de Errores)
- Declaraciones de variables incompletas
- Errores en estructuras de control
- Operadores inválidos en expresiones
- Paréntesis faltantes
- Errores de sintaxis en general

## 6. Conclusiones

El analizador sintáctico implementado demuestra ser robusto y capaz de:
1. Analizar correctamente programas sintácticamente válidos
2. Detectar y reportar errores de manera precisa
3. Recuperarse de errores y continuar el análisis
4. Manejar estructuras complejas y anidadas
5. Proporcionar mensajes de error útiles y descriptivos

La implementación del modo pánico y la sincronización permite un análisis más resiliente y una mejor experiencia de usuario al reportar múltiples errores en una sola pasada. #   G r a m a t i c a - L L  
 