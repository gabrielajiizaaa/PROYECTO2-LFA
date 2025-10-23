import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import webbrowser

class Token:
    def __init__(self, tipo, lexema, fila, columna):
        self.tipo = tipo
        self.lexema = lexema
        self.fila = fila
        self.columna = columna


class ErrorLexico:
    def __init__(self, numero, lexema, tipo, fila, columna):
        self.numero = numero
        self.lexema = lexema
        self.tipo = tipo
        self.fila = fila
        self.columna = columna


class Scanner:
    def __init__(self, texto):
        self.texto = texto
        self.posicion = 0
        self.fila = 1
        self.columna = 1
        self.tokens = []
        self.errores = []

    def caracter_actual(self):
        if self.posicion < len(self.texto):
            return self.texto[self.posicion]
        return None

    def avanzar(self):
        if self.posicion < len(self.texto):
            if self.texto[self.posicion] == '\n':
                self.fila += 1
                self.columna = 1
            else:
                self.columna += 1
            self.posicion += 1

    def es_mayuscula(self, c):
        return c is not None and 'A' <= c <= 'Z'

    def es_minuscula(self, c):
        return c is not None and 'a' <= c <= 'z'

    def es_digito(self, c):
        return c is not None and '0' <= c <= '9'

    def es_espacio(self, c):
        return c in [' ', '\t', '\n', '\r']

    def ignorar_espacios(self):
        while self.caracter_actual() and self.es_espacio(self.caracter_actual()):
            self.avanzar()

    def ignorar_comentario(self):
        if self.texto[self.posicion:self.posicion + 4] == "<!--":
            while self.caracter_actual() and self.texto[self.posicion:self.posicion + 3] != "-->":
                self.avanzar()
            if self.texto[self.posicion:self.posicion + 3] == "-->":
                self.posicion += 3
            return True
        return False

    def reconocer_etiqueta_apertura_con_atributo(self):
        inicio_fila = self.fila
        inicio_col = self.columna
        lexema = ''

        if self.caracter_actual() != '<':
            return None

        lexema += self.caracter_actual()
        self.avanzar()

        if not self.es_mayuscula(self.caracter_actual()):
            return None
        lexema += self.caracter_actual()
        self.avanzar()

        while self.es_minuscula(self.caracter_actual()):
            lexema += self.caracter_actual()
            self.avanzar()

        if self.caracter_actual() != '=':
            return None

        lexema += self.caracter_actual()
        self.avanzar()
        self.ignorar_espacios()

        if not self.es_mayuscula(self.caracter_actual()):
            num_error = len(self.errores) + 1
            self.errores.append(ErrorLexico(
                num_error, lexema, 'Atributo debe comenzar con mayuscula', inicio_fila, inicio_col
            ))
            return None

        while self.es_mayuscula(self.caracter_actual()) or self.es_minuscula(self.caracter_actual()):
            lexema += self.caracter_actual()
            self.avanzar()

        self.ignorar_espacios()

        if self.caracter_actual() != '>':
            num_error = len(self.errores) + 1
            self.errores.append(ErrorLexico(
                num_error, lexema, 'Etiqueta sin cerrar', inicio_fila, inicio_col
            ))
            return None

        lexema += self.caracter_actual()
        self.avanzar()

        return Token('ETIQUETA_APERTURA_ATRIBUTO', lexema, inicio_fila, inicio_col)

    def reconocer_etiqueta_con_numero(self):
        inicio_fila = self.fila
        inicio_col = self.columna
        lexema = ''

        if self.caracter_actual() != '<':
            return None

        lexema += self.caracter_actual()
        self.avanzar()

        if not self.es_mayuscula(self.caracter_actual()):
            return None

        nombre_etiqueta = self.caracter_actual()
        lexema += self.caracter_actual()
        self.avanzar()

        while self.es_minuscula(self.caracter_actual()):
            nombre_etiqueta += self.caracter_actual()
            lexema += self.caracter_actual()
            self.avanzar()

        self.ignorar_espacios()
        if self.caracter_actual() != '>':
            return None

        lexema += self.caracter_actual()
        self.avanzar()

        self.ignorar_espacios()

        if self.caracter_actual() in ['+', '-']:
            lexema += self.caracter_actual()
            self.avanzar()

        self.ignorar_espacios()

        if not self.es_digito(self.caracter_actual()):
            num_error = len(self.errores) + 1
            self.errores.append(ErrorLexico(
                num_error, lexema, 'Se esperaba un numero', inicio_fila, inicio_col
            ))
            return None

        while self.es_digito(self.caracter_actual()):
            lexema += self.caracter_actual()
            self.avanzar()

        if self.caracter_actual() == '.':
            lexema += self.caracter_actual()
            self.avanzar()
            if not self.es_digito(self.caracter_actual()):
                num_error = len(self.errores) + 1
                self.errores.append(ErrorLexico(
                    num_error, lexema, 'Se esperaban digitos despues del punto', inicio_fila, inicio_col
                ))
                return None
            while self.es_digito(self.caracter_actual()):
                lexema += self.caracter_actual()
                self.avanzar()

        self.ignorar_espacios()

        if self.caracter_actual() != '<':
            num_error = len(self.errores) + 1
            self.errores.append(ErrorLexico(
                num_error, lexema, 'Falta etiqueta de cierre', inicio_fila, inicio_col
            ))
            return None

        lexema += self.caracter_actual()
        self.avanzar()

        if self.caracter_actual() != '/':
            num_error = len(self.errores) + 1
            self.errores.append(ErrorLexico(
                num_error, lexema, 'Falta / en etiqueta de cierre', inicio_fila, inicio_col
            ))
            return None

        lexema += self.caracter_actual()
        self.avanzar()

        nombre_cierre = ''
        if self.es_mayuscula(self.caracter_actual()):
            nombre_cierre += self.caracter_actual()
            lexema += self.caracter_actual()
            self.avanzar()
            while self.es_minuscula(self.caracter_actual()):
                nombre_cierre += self.caracter_actual()
                lexema += self.caracter_actual()
                self.avanzar()

        self.ignorar_espacios()
        if nombre_etiqueta != nombre_cierre:
            num_error = len(self.errores) + 1
            self.errores.append(ErrorLexico(
                num_error, lexema, 'Etiqueta de cierre no coincide', inicio_fila, inicio_col
            ))
            return None

        if self.caracter_actual() != '>':
            num_error = len(self.errores) + 1
            self.errores.append(ErrorLexico(
                num_error, lexema, 'Etiqueta de cierre sin cerrar', inicio_fila, inicio_col
            ))
            return None

        lexema += self.caracter_actual()
        self.avanzar()
        return Token('ETIQUETA_NUMERO', lexema, inicio_fila, inicio_col)

    def reconocer_etiqueta_cierre(self):
        inicio_fila = self.fila
        inicio_col = self.columna
        lexema = ''

        if self.caracter_actual() != '<':
            return None

        lexema += self.caracter_actual()
        self.avanzar()

        if self.caracter_actual() != '/':
            return None
        lexema += self.caracter_actual()
        self.avanzar()

        if not self.es_mayuscula(self.caracter_actual()):
            return None
        lexema += self.caracter_actual()
        self.avanzar()

        while self.es_minuscula(self.caracter_actual()):
            lexema += self.caracter_actual()
            self.avanzar()

        self.ignorar_espacios()

        if self.caracter_actual() != '>':
            num_error = len(self.errores) + 1
            self.errores.append(ErrorLexico(
                num_error, lexema, 'Etiqueta de cierre sin cerrar', inicio_fila, inicio_col
            ))
            return None

        lexema += self.caracter_actual()
        self.avanzar()
        return Token('ETIQUETA_CIERRE', lexema, inicio_fila, inicio_col)

    def analizar(self):
        while self.posicion < len(self.texto):
            self.ignorar_espacios()
            if self.posicion >= len(self.texto):
                break
            if self.ignorar_comentario():
                continue
            c = self.caracter_actual()
            if c == '<':
                pos_temp = self.posicion
                fila_temp = self.fila
                col_temp = self.columna

                token = self.reconocer_etiqueta_con_numero()
                if token:
                    self.tokens.append(token)
                    continue

                self.posicion, self.fila, self.columna = pos_temp, fila_temp, col_temp
                token = self.reconocer_etiqueta_apertura_con_atributo()
                if token:
                    self.tokens.append(token)
                    continue

                self.posicion, self.fila, self.columna = pos_temp, fila_temp, col_temp
                token = self.reconocer_etiqueta_cierre()
                if token:
                    self.tokens.append(token)
                    continue

                num_error = len(self.errores) + 1
                self.errores.append(ErrorLexico(num_error, c, 'Etiqueta mal formada', fila_temp, col_temp))
                self.avanzar()
            else:
                num_error = len(self.errores) + 1
                self.errores.append(ErrorLexico(num_error, c, 'Caracter no reconocido', self.fila, self.columna))
                self.avanzar()

        return self.tokens, self.errores


class AnalizadorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Analizador Lexico")
        self.root.geometry("900x650")
        self.archivo_actual = None
        
        self.crear_interfaz()
    
    def crear_interfaz(self):
        frame_botones = tk.Frame(self.root)
        frame_botones.pack(side=tk.TOP, fill=tk.X, pady=10)
        
        btn_abrir = tk.Button(frame_botones, text="Abrir", width=15, command=self.abrir_archivo)
        btn_abrir.pack(side=tk.LEFT, padx=10)
        
        btn_guardar = tk.Button(frame_botones, text="Guardar", width=15)
        btn_guardar.pack(side=tk.LEFT, padx=10)
        
        btn_guardar_como = tk.Button(frame_botones, text="Guardar Como", width=15)
        btn_guardar_como.pack(side=tk.LEFT, padx=10)
        
        btn_analizar = tk.Button(frame_botones, text="Analizar", width=15, command=self.analizar)
        btn_analizar.pack(side=tk.LEFT, padx=10)
        
        frame_principal = tk.Frame(self.root)
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.txt_area = scrolledtext.ScrolledText(frame_principal, width=50, height=20)
        self.txt_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
                
        frame_derecho = tk.Frame(frame_principal)
        frame_derecho.pack(side=tk.RIGHT, fill=tk.Y)
        
        btn_manual_usuario = tk.Button(frame_derecho, text="Manual de Usuario", width=20)
        btn_manual_usuario.pack(pady=5)
        
        btn_manual_tecnico = tk.Button(frame_derecho, text="Manual Tecnico", width=20)
        btn_manual_tecnico.pack(pady=5)
        
        btn_ayuda = tk.Button(frame_derecho, text="Ayuda", width=20, command=self.mostrar_ayuda)
        btn_ayuda.pack(pady=5)
        
        etiqueta = tk.Label(self.root, text="GABRIEL AJIN, VELVETH UBEDO")
        etiqueta.pack(side=tk.BOTTOM, pady=5)
    
    def abrir_archivo(self):
        archivo = filedialog.askopenfilename(
            title="Abrir archivo",
            filetypes=[("Archivos de texto", "*.txt")]
        )
        if archivo:
            try:
                with open(archivo, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                    self.txt_area.delete(1.0, tk.END)
                    self.txt_area.insert(1.0, contenido)
                    self.archivo_actual = archivo
                    messagebox.showinfo("Exito", f"Archivo cargado: {os.path.basename(archivo)}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir el archivo:\n{str(e)}")
    
    def analizar(self):
        contenido = self.txt_area.get(1.0, tk.END).strip()
        
        if not contenido:
            messagebox.showwarning("Advertencia", "No hay codigo para analizar")
            return
        
        scanner = Scanner(contenido)
        tokens, errores = scanner.analizar()
        
        self.generar_html_resultados(tokens)
        
        if errores:
            self.generar_html_errores(errores)
        
        if errores:
            messagebox.showinfo("Analisis Completo", 
                              f"Tokens reconocidos: {len(tokens)}\n"
                              f"Errores encontrados: {len(errores)}\n\n"
                              f"Archivos generados:\n- Resultados.html\n- Errores.html")
        else:
            messagebox.showinfo("Analisis Completo", 
                              f"Tokens reconocidos: {len(tokens)}\n"
                              f"Sin errores lexicos\n\n"
                              f"Archivo generado: Resultados.html")
    
    def generar_html_resultados(self, tokens):
        html = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Resultados del Analisis</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { text-align: center; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid black; padding: 8px; text-align: left; }
        th { background-color: #ddd; }
    </style>
</head>
<body>
    <h1>Tokens Reconocidos</h1>
    <table>
        <thead>
            <tr>
                <th>No.</th>
                <th>Tipo</th>
                <th>Lexema</th>
                <th>Fila</th>
                <th>Columna</th>
            </tr>
        </thead>
        <tbody>
"""
        for i, token in enumerate(tokens, 1):
            html += f"""            <tr>
                <td>{i}</td>
                <td>{token.tipo}</td>
                <td>{self.html_escape(token.lexema)}</td>
                <td>{token.fila}</td>
                <td>{token.columna}</td>
            </tr>
"""
        
        html += """        </tbody>
    </table>
</body>
</html>"""
        
        try:
            with open('Resultados.html', 'w', encoding='utf-8') as f:
                f.write(html)
            webbrowser.open('Resultados.html')
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar Resultados.html:\n{str(e)}")
    
    def generar_html_errores(self, errores):
        if not errores:
            return
        
        html = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Errores Lexicos</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { text-align: center; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid black; padding: 8px; text-align: left; }
        th { background-color: #ddd; }
    </style>
</head>
<body>
    <h1>Errores Lexicos Detectados</h1>
    <table>
        <thead>
            <tr>
                <th>No. Error</th>
                <th>Lexema</th>
                <th>Tipo</th>
                <th>Fila</th>
                <th>Columna</th>
            </tr>
        </thead>
        <tbody>
"""
        for error in errores:
            html += f"""            <tr>
                <td>{error.numero}</td>
                <td>{self.html_escape(error.lexema)}</td>
                <td>{error.tipo}</td>
                <td>{error.fila}</td>
                <td>{error.columna}</td>
            </tr>
"""
        
        html += """        </tbody>
    </table>
</body>
</html>"""
        
        try:
            with open('Errores.html', 'w', encoding='utf-8') as f:
                f.write(html)
            webbrowser.open('Errores.html')
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar Errores.html:\n{str(e)}")
    
    def html_escape(self, texto):
        return texto.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
    
    def mostrar_ayuda(self):
        mensaje = """ANALIZADOR LEXICO
- Gabriel Ajin
- Velveth Ubedo"""
        
        messagebox.showinfo("Ayuda", mensaje)


if __name__ == "__main__":
    root = tk.Tk()
    app = AnalizadorApp(root)
    root.mainloop()
