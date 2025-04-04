import re
from typing import List, Dict, Set, Optional

class Token:
    def __init__(self, type: str, value: str, line: int):
        self.type = type
        self.value = value
        self.line = line

    def __str__(self):
        return f"Token({self.type}, {self.value}, line={self.line})"

class Lexer:
    def __init__(self):
        self.token_patterns = [
            ('WHITESPACE', r'[ \t\n]+'),
            ('START_PROG', r'= \^ \.'),
            ('END_PROG', r'\. \^ ='),
            ('DECVAR', r'DECVARinter'),
            ('ENDDEC', r'EndDecinter'),
            ('METHOD', r'Methodinter'),
            ('IF', r'Siinter'),
            ('ELSE', r'Sinointer'),
            ('WHILE', r'Mientinter'),
            ('FOR', r'Forinter'),
            ('ARRAY', r'ARRAYinter'),
            ('PRINT', r'Mostrinter'),
            ('READ', r'LEERinter'),
            ('BREAK', r'BREAKinter'),
            ('CONTINUE', r'CONTINUEinter'),
            ('RETURN', r'Returninter'),
            ('TYPE', r'(INTer|FLOATer|STRINGter|BOOLEANter|VOIDter)'),
            ('BOOLEAN', r'(TRUEter|FALSEter)'),
            ('STRING', r'"[^"]*"'),
            ('NUMBER', r'\d+(\.\d+)?'),
            ('OP_REL', r'(==|!=|>=|<=|>|<)'),
            ('OP_LOG', r'(ANDter|ORter|NOTter)'),
            ('OP_ARIT', r'[\+\-\*/]'),
            ('END_STMT', r':3'),
            ('SEMI', r';'),
            ('COMMA', r','),
            ('COLON', r':'),
            ('LPAREN', r'\('),
            ('RPAREN', r'\)'),
            ('LBRACE', r'\{'),
            ('RBRACE', r'\}'),
            ('LBRACK', r'\['),
            ('RBRACK', r'\]'),
            ('ASSIGN', r'='),
            ('COMMENT', r'##.*'),
            ('ID', r'[a-zA-Z_][a-zA-Z0-9_]*'),  # Un solo tipo de ID para simplificar
        ]
        
        self.token_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in self.token_patterns)
        self.regex = re.compile(self.token_regex)
        
    def tokenize(self, code: str) -> List[Token]:
        tokens = []
        line = 1
        pos = 0
        
        while pos < len(code):
            match = self.regex.match(code, pos)
            if match is None:
                raise ValueError(f"Invalid character at line {line}: {code[pos]}")
                
            token_type = match.lastgroup
            token_value = match.group()
            
            if token_type != 'WHITESPACE':
                tokens.append(Token(token_type, token_value, line))
                
            if token_value.count('\n') > 0:
                line += token_value.count('\n')
                
            pos = match.end()
            
        return tokens

class SyntaxError(Exception):
    def __init__(self, message: str, line: int):
        self.message = message
        self.line = line
        super().__init__(f"Syntax Error at line {line}: {message}")

class Parser:
    def __init__(self):
        self.tokens: List[Token] = []
        self.current = 0
        self.current_token: Optional[Token] = None
        self.errors: List[str] = []  # Lista para almacenar errores
        
        # Tokens de sincronización para modo pánico
        self.sync_tokens = {
            'Statement': {'END_STMT', 'SEMI', 'RBRACE', 'END_PROG'},
            'VarDec': {'ENDDEC', 'END_STMT', 'RBRACE', 'END_PROG'},
            'Method': {'RBRACE', 'END_PROG'},
            'Conditions': {'ELSE', 'END_STMT', 'RBRACE', 'END_PROG'},
            'Loops': {'RBRACE', 'END_PROG'},
            'Block': {'RBRACE', 'END_PROG', 'ELSE'},
            'Expresion': {'END_STMT', 'SEMI', 'RPAREN', 'COMMA', 'RBRACK'},
            'CODE': {'END_PROG', 'RBRACE'}
        }
        
        # Inicializar tabla de análisis predictivo
        self.parse_table: Dict[str, Dict[str, List[str]]] = self._initialize_parse_table()

    def _synchronize(self, non_terminal: str) -> bool:
        """
        Intenta sincronizar el análisis después de un error
        Retorna True si logró sincronizar, False si no hay más tokens
        """
        if non_terminal not in self.sync_tokens:
            return True

        while self.current_token is not None:
            # Si encontramos un token de sincronización para este no terminal
            if self.current_token.type in self.sync_tokens[non_terminal]:
                return True
                
            # Avanzar al siguiente token
            self.current += 1
            self.current_token = self.tokens[self.current] if self.current < len(self.tokens) else None
            
        return False

    def _initialize_parse_table(self) -> Dict[str, Dict[str, List[str]]]:
        table = {}
        
        # Programa y estructura básica
        table['Programa'] = {
            'START_PROG': ['START', 'CODE', 'FINISH']
        }
        
        table['START'] = {
            'START_PROG': ['START_PROG']
        }
        
        table['FINISH'] = {
            'END_PROG': ['END_PROG']
        }
        
        # CODE y Statement
        table['CODE'] = {
            'DECVAR': ['Statement', 'CODE'],
            'PRINT': ['Statement', 'CODE'],
            'ID': ['Statement', 'CODE'],
            'METHOD': ['Statement', 'CODE'],
            'IF': ['Statement', 'CODE'],
            'WHILE': ['Statement', 'CODE'],
            'FOR': ['Statement', 'CODE'],
            'ARRAY': ['Statement', 'CODE'],
            'READ': ['Statement', 'CODE'],
            'COMMENT': ['Statement', 'CODE'],
            'BREAK': ['Statement', 'CODE'],
            'CONTINUE': ['Statement', 'CODE'],
            'RETURN': ['Statement', 'CODE'],
            'END_PROG': ['ε'],
            'RBRACE': ['ε']
        }
        
        # Declaraciones
        table['VarDec'] = {
            'DECVAR': ['DECVAR', 'VarList', 'ENDDEC']
        }
        
        table['VarList'] = {
            'ID': ['VarDecItem', 'RestVarList']
        }
        
        table['VarDecItem'] = {
            'ID': ['ID', 'COLON', 'TYPE']
        }
        
        table['RestVarList'] = {
            'COMMA': ['COMMA', 'VarDecItem', 'RestVarList'],
            'ENDDEC': ['ε']
        }
        
        # Expresiones
        table['ExpressionStatement'] = {
            'ID': ['ID', 'ExpressionStatementTail']
        }
        
        table['ExpressionStatementTail'] = {
            'ASSIGN': ['ASSIGN', 'Expresion', 'END_STMT'],
            'LBRACK': ['LBRACK', 'Expresion', 'RBRACK', 'ASSIGN', 'Expresion', 'END_STMT']
        }
        
        table['Expresion'] = {
            'ID': ['Factor', 'ExprTail'],
            'NUMBER': ['Factor', 'ExprTail'],
            'STRING': ['Factor', 'ExprTail'],
            'LPAREN': ['Factor', 'ExprTail'],
            'BOOLEAN': ['Factor', 'ExprTail'],
            'OP_LOG': ['Factor', 'ExprTail']
        }
        
        table['ExprTail'] = {
            'OP_ARIT': ['OP_ARIT', 'Factor', 'ExprTail'],
            'OP_REL': ['OP_REL', 'Factor', 'ExprTail'],
            'OP_LOG': ['OP_LOG', 'Factor', 'ExprTail'],
            'END_STMT': ['ε'],
            'RPAREN': ['ε'],
            'COMMA': ['ε'],
            'RBRACK': ['ε']
        }
        
        table['Factor'] = {
            'ID': ['ID'],
            'NUMBER': ['NUMBER'],
            'BOOLEAN': ['BOOLEAN'],
            'STRING': ['STRING'],
            'LPAREN': ['LPAREN', 'Expresion', 'RPAREN'],
            'OP_LOG': ['OP_LOG', 'Factor']
        }
        
        # Condiciones
        table['Condition'] = {
            'ID': ['Expresion'],
            'NUMBER': ['Expresion'],
            'LPAREN': ['Expresion'],
            'BOOLEAN': ['Expresion'],
            'OP_LOG': ['Expresion']
        }
        
        # Estructuras de control
        table['Conditions'] = {
            'IF': ['IF', 'LPAREN', 'Condition', 'RPAREN', 'Block', 'OptionalElse']
        }
        
        table['Block'] = {
            'LBRACE': ['LBRACE', 'CODE', 'RBRACE']
        }
        
        table['OptionalElse'] = {
            'ELSE': ['ELSE', 'LBRACE', 'CODE', 'RBRACE'],
            'END_PROG': ['ε'],
            'DECVAR': ['ε'],
            'PRINT': ['ε'],
            'ID': ['ε'],
            'METHOD': ['ε'],
            'IF': ['ε'],
            'WHILE': ['ε'],
            'FOR': ['ε'],
            'ARRAY': ['ε'],
            'READ': ['ε'],
            'COMMENT': ['ε'],
            'BREAK': ['ε'],
            'CONTINUE': ['ε'],
            'RETURN': ['ε'],
            'RBRACE': ['ε']
        }
        
        # Bucles
        table['Loops'] = {
            'WHILE': ['WHILE', 'LPAREN', 'Condition', 'RPAREN', 'Block'],
            'FOR': ['FOR', 'LPAREN', 'ForInit', 'SEMI', 'Condition', 'SEMI', 'ExpressionStatement', 'RPAREN', 'Block']
        }
        
        table['ForInit'] = {
            'DECVAR': ['VarDec'],
            'ID': ['ExpressionStatement']
        }
        
        # Métodos
        table['Method'] = {
            'METHOD': ['METHOD', 'ID', 'LPAREN', 'ParamList', 'RPAREN', 'Block']
        }
        
        table['ParamList'] = {
            'TYPE': ['ParamItem', 'RestParams'],
            'RPAREN': ['ε']
        }
        
        table['ParamItem'] = {
            'TYPE': ['TYPE', 'ID']
        }
        
        table['RestParams'] = {
            'COMMA': ['COMMA', 'ParamItem', 'RestParams'],
            'RPAREN': ['ε']
        }
        
        # Arrays
        table['Array_Dec'] = {
            'ARRAY': ['ARRAY', 'ID', 'LBRACK', 'ArraySize', 'RBRACK', 'COLON', 'TYPE', 'END_STMT']
        }
        
        table['ArraySize'] = {
            'NUMBER': ['NUMBER'],
            'ID': ['ID']
        }
        
        # Entrada/Salida
        table['Print'] = {
            'PRINT': ['PRINT', 'LPAREN', 'Printable', 'RPAREN', 'END_STMT']
        }
        
        table['Printable'] = {
            'STRING': ['STRING'],
            'ID': ['Expresion'],
            'NUMBER': ['Expresion'],
            'BOOLEAN': ['Expresion'],
            'LPAREN': ['Expresion']
        }
        
        table['Input'] = {
            'READ': ['READ', 'LPAREN', 'ID', 'RPAREN', 'END_STMT']
        }
        
        # Control de flujo
        table['Break'] = {
            'BREAK': ['BREAK', 'END_STMT']
        }
        
        table['Continue'] = {
            'CONTINUE': ['CONTINUE', 'END_STMT']
        }
        
        table['Return'] = {
            'RETURN': ['RETURN', 'Expresion', 'END_STMT']
        }
        
        # Statement
        table['Statement'] = {
            'DECVAR': ['VarDec'],
            'PRINT': ['Print'],
            'ID': ['ExpressionStatement'],
            'METHOD': ['Method'],
            'IF': ['Conditions'],
            'WHILE': ['Loops'],
            'FOR': ['Loops'],
            'ARRAY': ['Array_Dec'],
            'READ': ['Input'],
            'COMMENT': ['Comment'],
            'BREAK': ['Break'],
            'CONTINUE': ['Continue'],
            'RETURN': ['Return']
        }
        
        # Comentarios
        table['Comment'] = {
            'COMMENT': ['COMMENT']
        }
        
        return table

    def parse(self, tokens: List[Token]) -> bool:
        """Analiza la lista de tokens usando la tabla de análisis predictivo"""
        self.tokens = tokens
        self.current = 0
        self.current_token = self.tokens[0] if tokens else None
        self.errors = []  # Reiniciar lista de errores
        
        try:
            self._parse_non_terminal('Programa')
            if self.errors:
                print("\nErrores encontrados durante el análisis:")
                for error in self.errors:
                    print(error)
                return False
            return True
        except SyntaxError as e:
            print(e)
            return False

    def _parse_non_terminal(self, non_terminal: str):
        """Procesa un símbolo no terminal usando la tabla de análisis predictivo"""
        if self.current_token is None:
            raise SyntaxError(f"Unexpected end of input while processing {non_terminal}", -1)
            
        # Obtener la producción de la tabla
        token_type = self.current_token.type
        if non_terminal not in self.parse_table or token_type not in self.parse_table[non_terminal]:
            error_msg = f"Unexpected token {token_type} while processing {non_terminal}"
            self.errors.append(f"Error en línea {self.current_token.line}: {error_msg}")
            
            # Intentar sincronizar
            if self._synchronize(non_terminal):
                return
            else:
                raise SyntaxError("Could not synchronize after error", self.current_token.line)
            
        # Obtener y procesar la producción
        production = self.parse_table[non_terminal][token_type]
        for symbol in production:
            if symbol == 'ε':  # Epsilon production
                continue
            elif symbol in self.parse_table:  # No terminal
                self._parse_non_terminal(symbol)
            else:  # Terminal
                self._match(symbol)

    def _match(self, expected: str):
        """Compara el token actual con el esperado"""
        if self.current_token is None:
            raise SyntaxError(f"Unexpected end of input, expected {expected}", -1)
            
        if self.current_token.type == expected:
            self.current += 1
            self.current_token = self.tokens[self.current] if self.current < len(self.tokens) else None
        else:
            error_msg = f"Expected {expected}, got {self.current_token.type}"
            self.errors.append(f"Error en línea {self.current_token.line}: {error_msg}")
            
            # Intentar sincronizar con el siguiente token válido
            self.current += 1
            self.current_token = self.tokens[self.current] if self.current < len(self.tokens) else None

def test_parser():
    lexer = Lexer()
    parser = Parser()
    
    # Caso de prueba 1: Declaración de variables y tipos
    test1 = """= ^ .
DECVARinter
    x: INTer,
    y: FLOATer,
    z: STRINGer,
    flag: BOOLEANter
EndDecinter
. ^ ="""
    
    # Caso de prueba 2: Operaciones aritméticas, lógicas y asignaciones
    test2 = """= ^ .
DECVARinter
    x: INTer,
    y: INTer,
    result: BOOLEANter
EndDecinter
x = 5 + 3 * 2:3
y = x - 1:3
result = (x > y) ANDter (y >= 0) ORter (x == 10):3
. ^ ="""
    
    # Caso de prueba 3: Estructuras de control anidadas
    test3 = """= ^ .
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
. ^ ="""
    
    # Caso de prueba 4: Arrays y bucle for
    test4 = """= ^ .
ARRAYinter numbers[10]: INTer:3
Forinter(DECVARinter i: INTer EndDecinter; i < 10; i = i + 1) {
    numbers[i] = i * 2:3
    Mostrinter(numbers[i]):3
}
. ^ ="""
    
    # Caso de prueba 5: Función con parámetros y retorno
    test5 = """= ^ .
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
. ^ ="""
    
    # Caso de prueba 6: Entrada/Salida y comentarios
    test6 = """= ^ .
## Este es un programa de ejemplo
DECVARinter
    nombre: STRINGer
EndDecinter
Mostrinter("Ingrese su nombre"):3
LEERinter(nombre):3
Mostrinter("Hola, "):3
Mostrinter(nombre):3
. ^ ="""
    
    # Caso de prueba 7: Expresiones lógicas complejas
    test7 = """= ^ .
DECVARinter
    a: BOOLEANter,
    b: BOOLEANter,
    c: BOOLEANter
EndDecinter
a = TRUEter:3
b = FALSEter:3
c = NOTter (a ANDter b) ORter (a ANDter NOTter b):3
. ^ ="""
    
    # Caso inválido 1: Error de sintaxis en declaración
    test_invalid1 = """= ^ .
DECVARinter
    x: INTer,
EndDecinter
. ^ ="""
    
    # Caso inválido 2: Error en estructura de control
    test_invalid2 = """= ^ .
Siinter x > 0 {  ## Faltan paréntesis
    Mostrinter(x):3
}
. ^ ="""
    
    # Caso inválido 3: Error en expresión
    test_invalid3 = """= ^ .
x = 5 + * 2:3  ## Operador inválido
. ^ ="""
    
    tests = [test1, test2, test3, test4, test5, test6, test7, 
             test_invalid1, test_invalid2, test_invalid3]
    
    for i, test in enumerate(tests, 1):
        print(f"\nProbando caso {i}:")
        print("-" * 40)
        print(test.strip())
        print("-" * 40)
        
        try:
            tokens = lexer.tokenize(test)
            result = parser.parse(tokens)
            print(f"Resultado: {'Válido' if result else 'Inválido'}")
        except (ValueError, SyntaxError) as e:
            print(f"Error: {str(e)}")
        
        print()

if __name__ == "__main__":
    test_parser()
