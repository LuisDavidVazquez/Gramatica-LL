import tkinter as tk
from tkinter import ttk, scrolledtext
from main import Lexer, Parser

class GLLGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("GLL Grammar Tester")
        self.root.geometry("800x600")
        
        # Configurar el estilo
        style = ttk.Style()
        style.configure('TButton', padding=5)
        
        # Crear el frame principal
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Área de texto para el código
        self.code_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, width=70, height=20)
        self.code_text.grid(row=0, column=0, columnspan=2, pady=5)
        
        # Frame para los botones de tokens
        tokens_frame = ttk.LabelFrame(main_frame, text="Tokens Comunes", padding="5")
        tokens_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Botones para tokens comunes
        self.create_token_buttons(tokens_frame)
        
        # Botón de análisis
        self.analyze_button = ttk.Button(main_frame, text="Analizar Código", command=self.analyze_code)
        self.analyze_button.grid(row=2, column=0, columnspan=2, pady=5)
        
        # Área de resultados
        self.result_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, width=70, height=10)
        self.result_text.grid(row=3, column=0, columnspan=2, pady=5)
        
        # Configurar el grid
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)

    def create_token_buttons(self, parent):
        # Tokens básicos
        basic_tokens = [
            ("Inicio Programa", "= ^ ."),
            ("Fin Programa", ". ^ ="),
            ("Declarar Variables", "DECVARinter"),
            ("Fin Declaración", "EndDecinter"),
            ("Método", "Methodinter"),
            ("Si", "Siinter"),
            ("Sino", "Sinointer"),
            ("Mientras", "Mientinter"),
            ("Para", "Forinter"),
            ("Array", "ARRAYinter"),
            ("Mostrar", "Mostrinter"),
            ("Leer", "LEERinter"),
            ("Romper", "BREAKinter"),
            ("Continuar", "CONTINUEinter"),
            ("Retornar", "Returninter")
        ]
        
        # Tipos de datos
        data_types = [
            ("Int", "INTer"),
            ("Float", "FLOATer"),
            ("String", "STRINGter"),
            ("Boolean", "BOOLEANter"),
            ("Void", "VOIDter")
        ]
        
        # Operadores
        operators = [
            ("AND", "ANDter"),
            ("OR", "ORter"),
            ("NOT", "NOTter"),
            ("True", "TRUEter"),
            ("False", "FALSEter")
        ]
        
        # Crear botones para cada categoría
        row = 0
        col = 0
        
        # Tokens básicos
        ttk.Label(parent, text="Tokens Básicos:").grid(row=row, column=col, sticky=tk.W)
        row += 1
        for text, token in basic_tokens:
            btn = ttk.Button(parent, text=text, command=lambda t=token: self.insert_token(t))
            btn.grid(row=row, column=col, padx=2, pady=2)
            row += 1
            if row > 5:  # Cambiar de columna después de 5 botones
                row = 1
                col += 1
        
        # Tipos de datos
        row = 0
        col += 1
        ttk.Label(parent, text="Tipos de Datos:").grid(row=row, column=col, sticky=tk.W)
        row += 1
        for text, token in data_types:
            btn = ttk.Button(parent, text=text, command=lambda t=token: self.insert_token(t))
            btn.grid(row=row, column=col, padx=2, pady=2)
            row += 1
        
        # Operadores
        row = 0
        col += 1
        ttk.Label(parent, text="Operadores:").grid(row=row, column=col, sticky=tk.W)
        row += 1
        for text, token in operators:
            btn = ttk.Button(parent, text=text, command=lambda t=token: self.insert_token(t))
            btn.grid(row=row, column=col, padx=2, pady=2)
            row += 1

    def insert_token(self, token):
        self.code_text.insert(tk.INSERT, token + " ")

    def analyze_code(self):
        # Limpiar resultados anteriores
        self.result_text.delete(1.0, tk.END)
        
        # Obtener el código
        code = self.code_text.get(1.0, tk.END).strip()
        
        try:
            # Crear lexer y parser
            lexer = Lexer()
            parser = Parser()
            
            # Tokenizar
            tokens = lexer.tokenize(code)
            
            # Analizar
            success = parser.parse(tokens)
            
            if success:
                self.result_text.insert(tk.END, "¡Análisis exitoso! El código es sintácticamente correcto.\n")
            else:
                self.result_text.insert(tk.END, "Error de sintaxis. Revise el código.\n")
                
            # Mostrar tokens generados
            self.result_text.insert(tk.END, "\nTokens generados:\n")
            for token in tokens:
                self.result_text.insert(tk.END, str(token) + "\n")
                
        except Exception as e:
            self.result_text.insert(tk.END, f"Error: {str(e)}\n")

def main():
    root = tk.Tk()
    app = GLLGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 