import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import webbrowser
import math

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

class Operacion:
    def __init__(self, tipo, id_op):
        self.tipo = tipo
        self.id = id_op
        self.operandos = []
        self.resultado = None
        self.param_especial = None

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

    def reconocer_etiqueta_operacion(self):
        inicio_fila = self.fila
        inicio_col = self.columna
        lexema = ''

        if self.caracter_actual() != '<':
            return None

        lexema += self.caracter_actual()
        self.avanzar()

        if self.caracter_actual() != 'O':
            return None
        
        nombre = 'O'
        lexema += self.caracter_actual()
        self.avanzar()

        while self.es_minuscula(self.caracter_actual()):
            nombre += self.caracter_actual()
            lexema += self.caracter_actual()
            self.avanzar()

        if nombre != 'Operacion':
            return None

        if self.caracter_actual() != '=':
            return None

        lexema += self.caracter_actual()
        self.avanzar()
        self.ignorar_espacios()

        operacion = ''
        while self.es_mayuscula(self.caracter_actual()):
            operacion += self.caracter_actual()
            lexema += self.caracter_actual()
            self.avanzar()

        operaciones_validas = ['SUMA', 'RESTA', 'MULTIPLICACION', 'DIVISION', 'POTENCIA', 'RAIZ', 'INVERSO', 'MOD']
        if operacion not in operaciones_validas:
            num_error = len(self.errores) + 1
            self.errores.append(ErrorLexico(num_error, lexema, 'Operacion no valida', inicio_fila, inicio_col))
            return None

        self.ignorar_espacios()

        if self.caracter_actual() != '>':
            num_error = len(self.errores) + 1
            self.errores.append(ErrorLexico(
                num_error, lexema, 'Etiqueta sin cerrar', inicio_fila, inicio_col
            ))
            return None

        lexema += self.caracter_actual()
        self.avanzar()

        return Token('ETIQUETA_OPERACION', lexema, inicio_fila, inicio_col)

    def reconocer_etiqueta_numero(self):
        inicio_fila = self.fila
        inicio_col = self.columna
        lexema = ''

        if self.caracter_actual() != '<':
            return None

        lexema += self.caracter_actual()
        self.avanzar()

        if self.caracter_actual() != 'N':
            return None

        nombre = 'N'
        lexema += self.caracter_actual()
        self.avanzar()

        while self.es_minuscula(self.caracter_actual()):
            nombre += self.caracter_actual()
            lexema += self.caracter_actual()
            self.avanzar()

        if nombre != 'Numero':
            return None

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
            return None

        lexema += self.caracter_actual()
        self.avanzar()

        if self.caracter_actual() != '/':
            return None

        lexema += self.caracter_actual()
        self.avanzar()

        if self.caracter_actual() != 'N':
            return None
        
        lexema += self.caracter_actual()
        self.avanzar()
        
        while self.es_minuscula(self.caracter_actual()):
            lexema += self.caracter_actual()
            self.avanzar()

        self.ignorar_espacios()

        if self.caracter_actual() != '>':
            return None

        lexema += self.caracter_actual()
        self.avanzar()

        return Token('ETIQUETA_NUMERO', lexema, inicio_fila, inicio_col)

    def reconocer_etiqueta_p_r(self):
        inicio_fila = self.fila
        inicio_col = self.columna
        lexema = ''

        if self.caracter_actual() != '<':
            return None

        lexema += self.caracter_actual()
        self.avanzar()

        if self.caracter_actual() not in ['P', 'R']:
            return None

        tipo_etiqueta = self.caracter_actual()
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
            return None

        while self.es_digito(self.caracter_actual()):
            lexema += self.caracter_actual()
            self.avanzar()

        if self.caracter_actual() == '.':
            lexema += self.caracter_actual()
            self.avanzar()
            while self.es_digito(self.caracter_actual()):
                lexema += self.caracter_actual()
                self.avanzar()

        self.ignorar_espacios()

        if self.caracter_actual() != '<':
            return None

        lexema += self.caracter_actual()
        self.avanzar()

        if self.caracter_actual() != '/':
            return None

        lexema += self.caracter_actual()
        self.avanzar()

        if self.caracter_actual() != tipo_etiqueta:
            return None

        lexema += self.caracter_actual()
        self.avanzar()

        self.ignorar_espacios()

        if self.caracter_actual() != '>':
            return None

        lexema += self.caracter_actual()
        self.avanzar()

        tipo_token = 'ETIQUETA_P' if tipo_etiqueta == 'P' else 'ETIQUETA_R'
        return Token(tipo_token, lexema, inicio_fila, inicio_col)

    def reconocer_etiqueta_cierre_operacion(self):
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

        if self.caracter_actual() != 'O':
            return None

        nombre = 'O'
        lexema += self.caracter_actual()
        self.avanzar()

        while self.es_minuscula(self.caracter_actual()):
            nombre += self.caracter_actual()
            lexema += self.caracter_actual()
            self.avanzar()

        if nombre != 'Operacion':
            return None

        self.ignorar_espacios()

        if self.caracter_actual() != '>':
            return None

        lexema += self.caracter_actual()
        self.avanzar()

        return Token('ETIQUETA_CIERRE_OPERACION', lexema, inicio_fila, inicio_col)

    def analizar(self):
        while self.posicion < len(self.texto):
            self.ignorar_espacios()
            if self.posicion >= len(self.texto):
                break
            
            c = self.caracter_actual()
            if c == '<':
                pos_temp = self.posicion
                fila_temp = self.fila
                col_temp = self.columna

                token = self.reconocer_etiqueta_operacion()
                if token:
                    self.tokens.append(token)
                    continue

                self.posicion, self.fila, self.columna = pos_temp, fila_temp, col_temp
                token = self.reconocer_etiqueta_numero()
                if token:
                    self.tokens.append(token)
                    continue

                self.posicion, self.fila, self.columna = pos_temp, fila_temp, col_temp
                token = self.reconocer_etiqueta_p_r()
                if token:
                    self.tokens.append(token)
                    continue

                self.posicion, self.fila, self.columna = pos_temp, fila_temp, col_temp
                token = self.reconocer_etiqueta_cierre_operacion()
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


class Evaluador:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.operaciones = []
        self.contador_op = 1

    def extraer_numero(self, lexema):
        inicio = lexema.find('>') + 1
        fin = lexema.rfind('<')
        numero_str = lexema[inicio:fin].strip()
        return float(numero_str)

    def extraer_tipo_operacion(self, lexema):
        inicio = lexema.find('=') + 1
        fin = lexema.rfind('>')
        return lexema[inicio:fin].strip()

    def parsear(self):
        while self.pos < len(self.tokens):
            if self.tokens[self.pos].tipo == 'ETIQUETA_OPERACION':
                op = self.parsear_operacion()
                if op:
                    self.operaciones.append(op)
            else:
                self.pos += 1
        return self.operaciones

    def parsear_operacion(self):
        if self.pos >= len(self.tokens) or self.tokens[self.pos].tipo != 'ETIQUETA_OPERACION':
            return None

        tipo_op = self.extraer_tipo_operacion(self.tokens[self.pos].lexema)
        operacion = Operacion(tipo_op, self.contador_op)
        self.contador_op += 1
        self.pos += 1

        while self.pos < len(self.tokens) and self.tokens[self.pos].tipo != 'ETIQUETA_CIERRE_OPERACION':
            if self.tokens[self.pos].tipo == 'ETIQUETA_NUMERO':
                numero = self.extraer_numero(self.tokens[self.pos].lexema)
                operacion.operandos.append(numero)
                self.pos += 1
            elif self.tokens[self.pos].tipo == 'ETIQUETA_P':
                numero = self.extraer_numero(self.tokens[self.pos].lexema)
                operacion.param_especial = numero
                self.pos += 1
            elif self.tokens[self.pos].tipo == 'ETIQUETA_R':
                numero = self.extraer_numero(self.tokens[self.pos].lexema)
                operacion.param_especial = numero
                self.pos += 1
            elif self.tokens[self.pos].tipo == 'ETIQUETA_OPERACION':
                sub_op = self.parsear_operacion()
                if sub_op:
                    operacion.operandos.append(sub_op)
            else:
                self.pos += 1

        if self.pos < len(self.tokens) and self.tokens[self.pos].tipo == 'ETIQUETA_CIERRE_OPERACION':
            self.pos += 1

        operacion.resultado = self.evaluar_operacion(operacion)
        return operacion

    def evaluar_operacion(self, op):
        valores = []
        for operando in op.operandos:
            if isinstance(operando, Operacion):
                valores.append(operando.resultado)
            else:
                valores.append(operando)

        try:
            if op.tipo == 'SUMA':
                return sum(valores)
            elif op.tipo == 'RESTA':
                resultado = valores[0]
                for v in valores[1:]:
                    resultado -= v
                return resultado
            elif op.tipo == 'MULTIPLICACION':
                resultado = 1
                for v in valores:
                    resultado *= v
                return resultado
            elif op.tipo == 'DIVISION':
                resultado = valores[0]
                for v in valores[1:]:
                    if v == 0:
                        return "Error: Division por cero"
                    resultado /= v
                return resultado
            elif op.tipo == 'POTENCIA':
                if op.param_especial is not None and len(valores) > 0:
                    return math.pow(valores[0], op.param_especial)
                return "Error: POTENCIA requiere parametro P"
            elif op.tipo == 'RAIZ':
                if op.param_especial is not None and len(valores) > 0:
                    return math.pow(valores[0], 1/op.param_especial)
                return "Error: RAIZ requiere parametro R"
            elif op.tipo == 'INVERSO':
                if len(valores) > 0 and valores[0] != 0:
                    return 1 / valores[0]
                return "Error: INVERSO de cero"
            elif op.tipo == 'MOD':
                if len(valores) >= 2:
                    return valores[0] % valores[1]
                return "Error: MOD requiere 2 operandos"
        except Exception as e:
            return f"Error: {str(e)}"

        return 0


class GeneradorGrafico:
    @staticmethod
    def generar_svg(operaciones):
        def calcular_altura(op):
            if not op.operandos:
                return 1
            max_altura = max((calcular_altura(operando) for operando in op.operandos 
                            if isinstance(operando, Operacion)), default=0)
            return max_altura + 1

        def dibujar_operacion(op, x, y, ancho):
            nodos = []
            lineas = []
            
            # nodo de operación
            nodos.append(f'<rect x="{x-60}" y="{y}" width="120" height="40" fill="white" stroke="black" stroke-width="1"/>')
            nodos.append(f'<text x="{x}" y="{y+25}" text-anchor="middle" fill="black" font-size="14">{op.tipo}</text>')
            
            # potencia y raiz
            if op.param_especial is not None:
                param_x = x - 80
                param_tipo = 'P' if op.tipo == 'POTENCIA' else 'R'
                nodos.append(f'<rect x="{param_x-30}" y="{y+60}" width="60" height="30" fill="white" stroke="black" stroke-width="1"/>')
                nodos.append(f'<text x="{param_x}" y="{y+80}" text-anchor="middle" fill="black" font-size="12">{param_tipo}={op.param_especial}</text>')
                lineas.append(f'<line x1="{x-60}" y1="{y+30}" x2="{param_x}" y2="{y+60}" stroke="black" stroke-width="1"/>')
            
            # operandos
            if op.operandos:
                espacio = ancho / len(op.operandos)
                for i, operando in enumerate(op.operandos):
                    hijo_x = x - ancho/2 + espacio * i + espacio/2
                    hijo_y = y + 120
                    
                    lineas.append(f'<line x1="{x}" y1="{y+40}" x2="{hijo_x}" y2="{hijo_y}" stroke="black" stroke-width="1"/>')
                    
                    if isinstance(operando, Operacion):
                        sub_nodos, sub_lineas = dibujar_operacion(operando, hijo_x, hijo_y, espacio * 0.8)
                        nodos.extend(sub_nodos)
                        lineas.extend(sub_lineas)
                    else:
                        nodos.append(f'<circle cx="{hijo_x}" cy="{hijo_y+20}" r="25" fill="white" stroke="black" stroke-width="1"/>')
                        nodos.append(f'<text x="{hijo_x}" y="{hijo_y+25}" text-anchor="middle" fill="black" font-size="12">{operando}</text>')
            
            return nodos, lineas

        # svg
        altura_total = sum(calcular_altura(op) * 150 + 100 for op in operaciones)
        svg_parts = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg width="1200" height="{altura_total}" xmlns="http://www.w3.org/2000/svg">',
            '<defs><style>text { font-family: Arial, sans-serif; }</style></defs>',
            '<rect width="100%" height="100%" fill="white"/>'
        ]
        
        y_offset = 50
        for op in operaciones:
            nodos, lineas = dibujar_operacion(op, 600, y_offset, 800)
            svg_parts.extend(lineas)
            svg_parts.extend(nodos)
            y_offset += calcular_altura(op) * 150 + 50
        
        svg_parts.append('</svg>')
        return '\n'.join(svg_parts)

class Analizador:
    def __init__(self, root):
        self.root = root
        self.root.title("Analizador de Operaciones Aritmeticas")
        self.root.geometry("900x650")
        self.archivo_actual = None
        
        self.crear_interfaz()
    
    def crear_interfaz(self):
        frame_botones = tk.Frame(self.root)
        frame_botones.pack(side=tk.TOP, fill=tk.X, pady=10)
        
        btn_abrir = tk.Button(frame_botones, text="Abrir", width=15, command=self.abrir_archivo)
        btn_abrir.pack(side=tk.LEFT, padx=10)
        
        btn_guardar = tk.Button(frame_botones, text="Guardar", width=15, command=self.guardar_archivo)
        btn_guardar.pack(side=tk.LEFT, padx=10)
        
        btn_guardar_como = tk.Button(frame_botones, text="Guardar Como", width=15, command=self.guardar_como)
        btn_guardar_como.pack(side=tk.LEFT, padx=10)
        
        btn_analizar = tk.Button(frame_botones, text="Analizar", width=15, command=self.analizar)
        btn_analizar.pack(side=tk.LEFT, padx=10)
        
        frame_principal = tk.Frame(self.root)
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.txt_area = scrolledtext.ScrolledText(frame_principal, width=50, height=20)
        self.txt_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
                
        frame_derecho = tk.Frame(frame_principal)
        frame_derecho.pack(side=tk.RIGHT, fill=tk.Y)
        
        btn_manual_usuario = tk.Button(frame_derecho, text="Manual de Usuario", width=20, command=self.abrir_manual_usuario)
        btn_manual_usuario.pack(pady=5)
        
        btn_manual_tecnico = tk.Button(frame_derecho, text="Manual Tecnico", width=20, command=self.abrir_manual_tecnico)
        btn_manual_tecnico.pack(pady=5)
        
        btn_ayuda = tk.Button(frame_derecho, text="Ayuda", width=20, command=self.mostrar_ayuda)
        btn_ayuda.pack(pady=5)
        
        etiqueta = tk.Label(self.root, text="GABRIEL AJIN - VELVETH UBEDO")
        etiqueta.pack(side=tk.BOTTOM, pady=5)
    
    def abrir_archivo(self):
        archivo = filedialog.askopenfilename(
            title="Abrir archivo",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
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
    
    def guardar_archivo(self):
        if not self.archivo_actual:
            self.guardar_como()
            return
        
        try:
            contenido = self.txt_area.get(1.0, tk.END)
            with open(self.archivo_actual, 'w', encoding='utf-8') as f:
                f.write(contenido)
            messagebox.showinfo("Exito", "Archivo guardado correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{str(e)}")
    
    def guardar_como(self):
        archivo = filedialog.asksaveasfilename(
            title="Guardar como",
            defaultextension=".txt",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        if archivo:
            try:
                contenido = self.txt_area.get(1.0, tk.END)
                with open(archivo, 'w', encoding='utf-8') as f:
                    f.write(contenido)
                self.archivo_actual = archivo
                messagebox.showinfo("Exito", f"Archivo guardado como: {os.path.basename(archivo)}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{str(e)}")
    
    def analizar(self):
        try:
            contenido = self.txt_area.get(1.0, tk.END).strip()
            
            if not contenido:
                messagebox.showwarning("Advertencia", "No hay codigo para analizar")
                return
            
            # Analisis lexico
            scanner = Scanner(contenido)
            tokens, errores = scanner.analizar()
            
            # Generar reporte de tokens
            self.generar_html_tokens(tokens)
            
            # Evaluacion de operaciones
            evaluador = Evaluador(tokens)
            operaciones = evaluador.parsear()
            
            # Generar resultados
            self.generar_html_resultados(operaciones)
            
            # Generar errores si existen
            if errores:
                self.generar_html_errores(errores)
            
            # Generar grafico
            if operaciones:
                self.generar_grafico(operaciones)
            
            # Mensaje de exito
            mensaje = f"Analisis Completo\n\n"
            mensaje += f"Tokens reconocidos: {len(tokens)}\n"
            mensaje += f"Operaciones procesadas: {len(operaciones)}\n"
            mensaje += f"Errores encontrados: {len(errores)}\n\n"
            mensaje += "Archivos generados:\n"
            mensaje += "- Tokens.html\n"
            mensaje += "- Resultados.html\n"
            if errores:
                mensaje += "- Errores.html\n"
            if operaciones:
                mensaje += "- Diagrama.svg"
            
            messagebox.showinfo("Exito", mensaje)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error durante el analisis:\n{str(e)}")
            import traceback
            print(traceback.format_exc())
    
    def generar_html_tokens(self, tokens):
        html = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Tokens Reconocidos</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #ffffff; }
        h1 { text-align: center; color: #000000; }
        table { width: 100%; border-collapse: collapse; background-color: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        th, td { border: 1px solid #000000; padding: 12px; text-align: left; }
        th { background-color: #f0f0f0; color: #000000; font-weight: bold; }
        tr:nth-child(even) { background-color: #f9f9f9; }
        tr:hover { background-color: #e8e8e8; }
    </style>
</head>
<body>
    <h1>Analisis Lexico - Tokens Reconocidos</h1>
    <table>
        <thead>
            <tr>
                <th>No.</th>
                <th>Tipo de Token</th>
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
            with open('Tokens.html', 'w', encoding='utf-8') as f:
                f.write(html)
            webbrowser.open('Tokens.html')
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar Tokens.html:\n{str(e)}")
    
    def generar_html_resultados(self, operaciones):
        html = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Resultados de Operaciones</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #ffffff; }
        h1 { text-align: center; color: #000000; }
        table { width: 100%; border-collapse: collapse; background-color: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        th, td { border: 1px solid #000000; padding: 12px; text-align: left; }
        th { background-color: #f0f0f0; color: #000000; font-weight: bold; }
        tr:nth-child(even) { background-color: #f9f9f9; }
        tr:hover { background-color: #e8e8e8; }
    </style>
</head>
<body>
    <h1>Resultados de Operaciones Aritmeticas</h1>
    <table>
        <thead>
            <tr>
                <th>ID Operacion</th>
                <th>Tipo</th>
                <th>Resultado</th>
            </tr>
        </thead>
        <tbody>
"""
        
        def agregar_operacion(op):
            resultado_str = f"{op.resultado:.4f}" if isinstance(op.resultado, (int, float)) else str(op.resultado)
            return f"""            <tr>
                <td>OP-{op.id}</td>
                <td>{op.tipo}</td>
                <td>{resultado_str}</td>
            </tr>
"""
        
        def recorrer_operaciones(op):
            filas = []
            for operando in op.operandos:
                if isinstance(operando, Operacion):
                    filas.extend(recorrer_operaciones(operando))
            filas.append(agregar_operacion(op))
            return filas
        
        todas_filas = []
        for op in operaciones:
            todas_filas.extend(recorrer_operaciones(op))
        
        for fila in todas_filas:
            html += fila
        
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
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #ffffff; }
        h1 { text-align: center; color: #000000; }
        table { width: 100%; border-collapse: collapse; background-color: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        th, td { border: 1px solid #000000; padding: 12px; text-align: left; }
        th { background-color: #f0f0f0; color: #000000; font-weight: bold; }
        tr:nth-child(even) { background-color: #f9f9f9; }
        tr:hover { background-color: #e8e8e8; }
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
            messagebox.showerror("Error", f"No se pudo generar archivo de errores:\n{str(e)}")
    
    def generar_grafico(self, operaciones):
        try:
            svg_content = GeneradorGrafico.generar_svg(operaciones)
            with open('Diagrama.svg', 'w', encoding='utf-8') as f:
                f.write(svg_content)
            webbrowser.open('Diagrama.svg')
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el diagrama:\n{str(e)}")
    
    def html_escape(self, texto):
        return texto.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
    
    def abrir_manual_usuario(self):
        if os.path.exists('Manual_Usuario.pdf'):
            webbrowser.open('Manual_Usuario.pdf')
        else:
            messagebox.showwarning("Advertencia", "Manual de Usuario no encontrado.")
    
    def abrir_manual_tecnico(self):
        if os.path.exists('Manual_Tecnico.pdf'):
            webbrowser.open('Manual_Tecnico.pdf')
        else:
            messagebox.showwarning("Advertencia", "Manual Tecnico no encontrado.")
    
    def mostrar_ayuda(self):
        mensaje = """Desarrolladores: - Gabriel Ajin y Velveth Ubedo"""
        
        messagebox.showinfo("Ayuda", mensaje)

if __name__ == "__main__":
    root = tk.Tk()
    app = Analizador(root)
    root.mainloop()