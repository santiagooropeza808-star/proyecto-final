import sys
import random
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QStackedWidget, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QCursor

# --- ESTILOS GENERALES (Estética Relajante de Negro y Morado) ---
ESTILO_GLOBAL = """
QWidget {
    background-color: #0d0415; /* Fondo negro con tono morado muy oscuro */
    color: #e0ccff; /* Texto morado claro / lavanda */
    font-family: "Segoe UI", Arial, sans-serif;
}
QPushButton {
    background-color: #3b1066;
    border: 2px solid #5a1a99;
    border-radius: 12px;
    padding: 10px 20px;
    font-size: 16px;
    font-weight: bold;
    color: white;
}
QPushButton:hover {
    background-color: #5a1a99;
}
QPushButton:pressed {
    background-color: #2a0b4d;
}
QLineEdit {
    background-color: #1a0a29;
    border: 1px solid #5a1a99;
    border-radius: 8px;
    padding: 10px;
    font-size: 16px;
    color: #ffffff;
}
QLabel {
    font-size: 18px;
}
"""

class PreguntaPrueba:
    """Estructura nativa de Python para manejar las preguntas."""
    def __init__(self, tipo, subtema, texto, respuesta_correcta, opciones=None):
        self.tipo = tipo 
        self.subtema = subtema
        self.texto = texto
        self.respuesta_correcta = respuesta_correcta
        self.opciones = opciones 

class PantallaInicio(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        # Título Animado
        self.titulo = QLabel("Yo te ayudo")
        self.titulo.setAlignment(Qt.AlignCenter)
        self.titulo.setStyleSheet("color: #d4b3ff; font-size: 55px; font-weight: bold; margin-top: 0px;")
        layout.addWidget(self.titulo)
        
        # Variables para la animación del título
        self.offset_y = 0
        self.direccion_anim = 1
        self.timer_anim = QTimer(self)
        self.timer_anim.timeout.connect(self.animar_titulo)
        self.timer_anim.start(60)
        
        # Instrucciones
        self.label_instruccion = QLabel("Escribe tu tema (solo matemáticas)")
        self.label_instruccion.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_instruccion)
        
        # Campo de Tema
        self.input_tema = QLineEdit()
        self.input_tema.setPlaceholderText("Ejemplo: Álgebra")
        self.input_tema.setFixedWidth(400)
        layout.addWidget(self.input_tema, alignment=Qt.AlignCenter)
        
        # Campo de Puntos (Subtemas)
        self.input_puntos = QLineEdit()
        self.input_puntos.setPlaceholderText("Puntos (Ej: Ecuaciones, Sumas, Geometría)")
        self.input_puntos.setFixedWidth(400)
        layout.addWidget(self.input_puntos, alignment=Qt.AlignCenter)
        
        # Botón Empezar
        self.btn_empezar = QPushButton("Comenzar")
        self.btn_empezar.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_empezar.setFixedWidth(200)
        self.btn_empezar.clicked.connect(self.empezar)
        layout.addWidget(self.btn_empezar, alignment=Qt.AlignCenter)
        
        self.setLayout(layout)
        
    def animar_titulo(self):
        self.offset_y += self.direccion_anim
        if self.offset_y >= 15:
            self.direccion_anim = -1
        elif self.offset_y <= 0:
            self.direccion_anim = 1
        self.titulo.setStyleSheet(f"color: #d4b3ff; font-size: 55px; font-weight: bold; margin-top: {self.offset_y}px;")

    def cargar_subtemas(self, tema, subtemas):
        self.input_tema.setText(tema)
        self.input_puntos.setText(", ".join(subtemas))

    def empezar(self):
        tema = self.input_tema.text().strip()
        puntos_str = self.input_puntos.text().strip()
        
        if not tema or not puntos_str:
            self.input_tema.setStyleSheet("border: 1px solid #ff4d4d;")
            self.input_puntos.setStyleSheet("border: 1px solid #ff4d4d;")
            self.label_instruccion.setText("¡Por favor llena ambos campos para continuar!")
            self.label_instruccion.setStyleSheet("color: #ff4d4d;")
            return
            
        self.input_tema.setStyleSheet("")
        self.input_puntos.setStyleSheet("")
        self.label_instruccion.setText("Escribe tu tema (solo matemáticas)")
        self.label_instruccion.setStyleSheet("color: #e0ccff;")
        
        subtemas = [s.strip() for s in puntos_str.split(',') if s.strip()]
        self.main_app.iniciar_flujo(tema, subtemas)

class PantallaCarga1(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        self.poema = QLabel("En la línea de la vida,\nbusco siempre la ecuación;\nsi mi mente está perdida,\ntú eres mi solución.")
        self.poema.setAlignment(Qt.AlignCenter)
        self.poema.setStyleSheet("font-size: 26px; font-style: italic; color: #b380ff; line-height: 1.5;")
        layout.addWidget(self.poema)
        self.setLayout(layout)

    def iniciar(self):
        QTimer.singleShot(4000, lambda: self.main_app.cambiar_pantalla(self.main_app.pantalla_minijuegos))

class PantallaMinijuegos(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.palabra_secreta = ""
        
        layout_principal = QVBoxLayout()
        
        # Barra superior con botón finalizar
        barra_superior = QHBoxLayout()
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        barra_superior.addItem(spacer)
        
        self.btn_finalizar = QPushButton("Finalizar")
        self.btn_finalizar.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_finalizar.clicked.connect(self.ir_a_carga_examen)
        barra_superior.addWidget(self.btn_finalizar)
        layout_principal.addLayout(barra_superior)
        
        # Contenido
        layout_centro = QVBoxLayout()
        layout_centro.setAlignment(Qt.AlignCenter)
        self.titulo = QLabel("Área de Práctica y Minijuegos")
        self.titulo.setStyleSheet("font-size: 30px; font-weight: bold;")
        self.titulo.setAlignment(Qt.AlignCenter)
        layout_centro.addWidget(self.titulo)
        
        self.info_temas = QLabel("")
        self.info_temas.setAlignment(Qt.AlignCenter)
        self.info_temas.setStyleSheet("font-size: 20px; margin: 20px 0;")
        layout_centro.addWidget(self.info_temas)
        
        # NUEVO: Layout dinámico para poner botones o barras de texto según el minijuego
        self.layout_dinamico_juego = QVBoxLayout()
        layout_centro.addLayout(self.layout_dinamico_juego)
        
        self.btn_jugar = QPushButton("Jugar")
        self.btn_jugar.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_jugar.setFixedWidth(300)
        self.btn_jugar.clicked.connect(self.iniciar_minijuego)
        layout_centro.addWidget(self.btn_jugar, alignment=Qt.AlignCenter)
        
        layout_principal.addLayout(layout_centro)
        self.setLayout(layout_principal)

    def preparar(self, subtemas):
        self.info_temas.setText(f"Temas a repasar hoy:\n{', '.join(subtemas)}\n\n¡Presiona el botón para jugar!")
        self.btn_jugar.setText("Iniciar Minijuego Aleatorio")
        self.limpiar_layout_juego()
        self.btn_jugar.setVisible(True)

    def limpiar_layout_juego(self):
        """Elimina la barra de texto o los botones del minijuego anterior."""
        while self.layout_dinamico_juego.count():
            child = self.layout_dinamico_juego.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def iniciar_minijuego(self):
        """Elige un minijuego aleatorio."""
        subtemas = self.main_app.subtemas_actuales
        if not subtemas:
            return
            
        tema_elegido = random.choice(subtemas).upper()
        self.btn_jugar.setVisible(False)
        self.limpiar_layout_juego()
        
        juegos_disponibles = ['anagrama', 'completar', 'memoria']
        juego_seleccionado = random.choice(juegos_disponibles)
        
        if juego_seleccionado == 'anagrama':
            self.juego_anagrama(tema_elegido)
        elif juego_seleccionado == 'completar':
            self.juego_completar(tema_elegido)
        elif juego_seleccionado == 'memoria':
            self.juego_memoria(tema_elegido)

    # --- MINIJUEGO 1: ANAGRAMA ---
    def juego_anagrama(self, tema):
        self.palabra_secreta = tema
        letras = list(tema.replace(" ", ""))
        random.shuffle(letras)
        anagrama = " ".join(letras)
        
        self.info_temas.setText(f"🧠 Minijuego: Anagrama\n\nOrdena las letras para descubrir el tema:\n\n{anagrama}")
        self.crear_input_texto("Escribe la palabra ordenada y presiona Enter...")

    # --- MINIJUEGO 2: COMPLETAR PALABRA ---
    def juego_completar(self, tema):
        self.palabra_secreta = tema
        letras = list(tema)
        # Ocultar la mitad de las letras
        indices_para_ocultar = random.sample(range(len(letras)), max(1, len(letras)//2))
        for i in indices_para_ocultar:
            if letras[i] != " ":
                letras[i] = "_"
                
        palabra_oculta = " ".join(letras)
        self.info_temas.setText(f"✍️ Minijuego: Completar\n\nAdivina el tema completando las letras:\n\n{palabra_oculta}")
        self.crear_input_texto("Escribe la palabra completa y presiona Enter...")

    # --- MINIJUEGO 3: MEMORIA FLASH ---
    def juego_memoria(self, tema):
        self.palabra_secreta = tema
        self.info_temas.setText(f"👁️ Minijuego: Memoria Rápida\n\nMemoriza este tema (desaparecerá pronto):\n\n{tema}")
        # Desaparece en 2.5 segundos
        QTimer.singleShot(2500, self.mostrar_opciones_memoria)

    def mostrar_opciones_memoria(self):
        self.info_temas.setText("¿Cuál fue el tema que acabas de ver?")
        self.limpiar_layout_juego()
        
        opciones = [self.palabra_secreta]
        fakes = ["GEOMETRÍA", "ÁLGEBRA", "INTEGRALES", "DERIVADAS", "FRACCIONES", "VECTORES"]
        random.shuffle(fakes)
        
        for f in fakes:
            if f != self.palabra_secreta and len(opciones) < 3:
                opciones.append(f)
                
        random.shuffle(opciones)
        
        for op in opciones:
            btn = QPushButton(op)
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            btn.clicked.connect(lambda checked, o=op: self.verificar_memoria(o))
            self.layout_dinamico_juego.addWidget(btn)

    def verificar_memoria(self, seleccion):
        self.limpiar_layout_juego()
        if seleccion == self.palabra_secreta:
            self.info_temas.setText("¡Excelente memoria! Respuesta correcta.\n\nPuedes jugar otro, o darle a 'Finalizar'.")
        else:
            self.info_temas.setText(f"¡Ups! El tema correcto era: {self.palabra_secreta}\n\nMás suerte a la próxima.")
            
        self.btn_jugar.setText("Jugar otro minijuego")
        self.btn_jugar.setVisible(True)

    # --- UTILIDADES PARA LOS MINIJUEGOS DE TEXTO ---
    def crear_input_texto(self, placeholder):
        self.input_juego = QLineEdit()
        self.input_juego.setPlaceholderText(placeholder)
        self.input_juego.setFixedWidth(400)
        self.input_juego.setAlignment(Qt.AlignCenter)
        self.input_juego.returnPressed.connect(self.verificar_texto)
        self.layout_dinamico_juego.addWidget(self.input_juego, alignment=Qt.AlignCenter)
        self.input_juego.setFocus()

    def verificar_texto(self):
        intento = self.input_juego.text().strip().upper().replace(" ", "")
        correcta = self.palabra_secreta.upper().replace(" ", "")
        
        if intento == correcta:
            self.info_temas.setText("¡Correcto! Mente enfocada y lista.\n\nPuedes jugar otro, o darle a 'Finalizar'.")
            self.limpiar_layout_juego()
            self.btn_jugar.setText("Jugar otro minijuego")
            self.btn_jugar.setVisible(True)
        else:
            # Pinta rojo si se equivoca
            self.input_juego.setStyleSheet("border: 1px solid #ff4d4d;")
            QTimer.singleShot(800, lambda: self.input_juego.setStyleSheet(""))

    def ir_a_carga_examen(self):
        self.btn_finalizar.setText("¡Que empiece el examen!")
        QTimer.singleShot(1000, lambda: self.main_app.pantalla_carga2.iniciar())
        QTimer.singleShot(1500, lambda: self.btn_finalizar.setText("Finalizar"))

class PantallaCarga2(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        self.texto_dinamico = QLabel("")
        self.texto_dinamico.setAlignment(Qt.AlignCenter)
        self.texto_dinamico.setStyleSheet("font-size: 26px; font-style: italic; color: #b380ff;")
        layout.addWidget(self.texto_dinamico)
        self.setLayout(layout)

    def iniciar(self):
        self.main_app.cambiar_pantalla(self)
        self.texto_dinamico.setText("Prepárate para el examen...")
        QTimer.singleShot(2000, self.desaparecer)

    def desaparecer(self):
        self.texto_dinamico.setText("")
        QTimer.singleShot(1500, self.mostrar_poema)

    def mostrar_poema(self):
        poema = "Despejar tu tristeza\nes mi cuenta favorita,\nmultiplico tu belleza\ny mi amor que no se quita."
        self.texto_dinamico.setText(poema)
        QTimer.singleShot(4500, lambda: self.main_app.iniciar_examen())

class PantallaExamen(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.preguntas = []
        self.indice_actual = 0
        self.respuestas_correctas = 0
        self.subtemas_fallados = set()
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        self.lbl_progreso = QLabel("Pregunta 1/1")
        layout.addWidget(self.lbl_progreso, alignment=Qt.AlignCenter)
        
        self.lbl_pregunta = QLabel("¿Pregunta?")
        self.lbl_pregunta.setAlignment(Qt.AlignCenter)
        self.lbl_pregunta.setStyleSheet("font-size: 24px; margin-bottom: 20px;")
        self.lbl_pregunta.setWordWrap(True)
        layout.addWidget(self.lbl_pregunta)
        
        self.layout_respuestas = QVBoxLayout()
        layout.addLayout(self.layout_respuestas)
        
        self.btn_saltar = QPushButton("Saltar")
        self.btn_saltar.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_saltar.setStyleSheet("background-color: #26004d; color: #a366ff;")
        self.btn_saltar.clicked.connect(self.saltar_pregunta)
        layout.addWidget(self.btn_saltar, alignment=Qt.AlignCenter)
        
        self.setLayout(layout)

    def analizar_y_generar_preguntas(self, subtemas):
        self.preguntas = []
        for st in subtemas:
            tema_analizado = st.lower()
            
            if "suma" in tema_analizado or "adicion" in tema_analizado:
                a, b = random.randint(15, 99), random.randint(15, 99)
                texto = f"Ejercicio práctico ({st}):\nResuelve: {a} + {b}"
                self.preguntas.append(PreguntaPrueba('abierta', st, texto, str(a+b)))
                
            elif "resta" in tema_analizado or "sustraccion" in tema_analizado:
                a, b = random.randint(50, 150), random.randint(10, 49)
                texto = f"Ejercicio práctico ({st}):\nResuelve: {a} - {b}"
                self.preguntas.append(PreguntaPrueba('abierta', st, texto, str(a-b)))
                
            elif "multiplicacion" in tema_analizado or "multiplicar" in tema_analizado:
                a, b = random.randint(3, 12), random.randint(3, 12)
                texto = f"Análisis de {st} (V/F):\n¿El resultado de {a} x {b} es {a*b}?"
                self.preguntas.append(PreguntaPrueba('vf', st, texto, "Verdadero", ["Verdadero", "Falso"]))
                
            elif "division" in tema_analizado or "dividir" in tema_analizado:
                b = random.randint(2, 10)
                resultado = random.randint(2, 12)
                a = b * resultado
                texto = f"Ejercicio práctico ({st}):\n¿Cuánto es {a} / {b}?"
                self.preguntas.append(PreguntaPrueba('abierta', st, texto, str(resultado)))
                
            elif "ecuacion" in tema_analizado:
                x = random.randint(1, 10)
                b = random.randint(1, 5)
                resultado = x + b
                texto = f"Ejercicio práctico ({st}):\nDespeja la X en: x + {b} = {resultado}"
                self.preguntas.append(PreguntaPrueba('abierta', st, texto, str(x)))
                
            elif "fraccion" in tema_analizado:
                num = random.randint(1, 5)
                den = random.randint(6, 10)
                texto = f"Concepto ({st}):\nEn la fracción {num}/{den}, ¿el número {num} es el numerador?"
                self.preguntas.append(PreguntaPrueba('vf', st, texto, "Verdadero", ["Verdadero", "Falso"]))

            elif "geometria" in tema_analizado or "area" in tema_analizado or "triangulo" in tema_analizado:
                base, altura = 4, 5
                texto = f"Ejercicio ({st}) (V/F):\n¿El área de un triángulo de base {base} y altura {altura} es {(base*altura)/2}?"
                self.preguntas.append(PreguntaPrueba('vf', st, texto, "Verdadero", ["Verdadero", "Falso"]))
                
            elif "derivada" in tema_analizado:
                texto = f"Ejercicio ({st}):\n¿Cuál es la derivada de '2x'? (escribe solo el numero)"
                self.preguntas.append(PreguntaPrueba('abierta', st, texto, "2"))
                
            else:
                letras = len(st.replace(" ", ""))
                texto = f"Análisis lógico del tema ingresado:\n¿La frase '{st}' tiene exactamente {letras} letras?"
                self.preguntas.append(PreguntaPrueba('vf', st, texto, "Verdadero", ["Verdadero", "Falso"]))
                
        random.shuffle(self.preguntas)

    def iniciar(self, subtemas):
        self.analizar_y_generar_preguntas(subtemas)
        self.indice_actual = 0
        self.respuestas_correctas = 0
        self.subtemas_fallados.clear()
        self.mostrar_pregunta()

    def limpiar_layout_respuestas(self):
        while self.layout_respuestas.count():
            child = self.layout_respuestas.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def mostrar_pregunta(self):
        if self.indice_actual >= len(self.preguntas):
            self.finalizar_examen()
            return
            
        self.limpiar_layout_respuestas()
        pregunta = self.preguntas[self.indice_actual]
        self.lbl_progreso.setText(f"Pregunta {self.indice_actual + 1} de {len(self.preguntas)}")
        self.lbl_pregunta.setText(pregunta.texto)
        
        if pregunta.tipo == 'vf':
            for opcion in pregunta.opciones:
                btn = QPushButton(opcion)
                btn.setCursor(QCursor(Qt.PointingHandCursor))
                btn.clicked.connect(lambda checked, o=opcion: self.verificar_respuesta(o))
                self.layout_respuestas.addWidget(btn)
        
        elif pregunta.tipo == 'abierta':
            self.input_respuesta = QLineEdit()
            self.input_respuesta.setPlaceholderText("Escribe tu respuesta y presiona Enter...")
            self.input_respuesta.setAlignment(Qt.AlignCenter)
            self.input_respuesta.returnPressed.connect(self.procesar_teclado)
            self.layout_respuestas.addWidget(self.input_respuesta)
            self.input_respuesta.setFocus()

    def procesar_teclado(self):
        if hasattr(self, 'input_respuesta'):
            respuesta = self.input_respuesta.text().strip().lower()
            if respuesta:
                self.verificar_respuesta(respuesta)

    def verificar_respuesta(self, respuesta_usuario):
        pregunta = self.preguntas[self.indice_actual]
        respuesta_correcta = pregunta.respuesta_correcta.lower() if pregunta.tipo == 'abierta' else pregunta.respuesta_correcta
        
        if respuesta_usuario == respuesta_correcta:
            self.respuestas_correctas += 1
        else:
            self.subtemas_fallados.add(pregunta.subtema)
            
        self.indice_actual += 1
        self.mostrar_pregunta()

    def saltar_pregunta(self):
        pregunta = self.preguntas[self.indice_actual]
        self.subtemas_fallados.add(pregunta.subtema)
        self.indice_actual += 1
        self.mostrar_pregunta()

    def finalizar_examen(self):
        total = len(self.preguntas)
        nota_final = int((self.respuestas_correctas / total) * 20) if total > 0 else 0
        nota_final = max(1, min(20, nota_final))
        
        self.main_app.pantalla_resultados.mostrar_resultados(nota_final, list(self.subtemas_fallados))
        self.main_app.cambiar_pantalla(self.main_app.pantalla_resultados)

class PantallaResultados(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.subtemas_fallados = []
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        self.lbl_nota = QLabel("Nota: 0 / 20")
        self.lbl_nota.setStyleSheet("font-size: 40px; font-weight: bold; color: #d4b3ff;")
        self.lbl_nota.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_nota)
        
        self.lbl_mensaje = QLabel("")
        self.lbl_mensaje.setStyleSheet("font-size: 22px;")
        self.lbl_mensaje.setAlignment(Qt.AlignCenter)
        self.lbl_mensaje.setWordWrap(True)
        layout.addWidget(self.lbl_mensaje)
        
        self.lbl_mejorar = QLabel("")
        self.lbl_mejorar.setStyleSheet("font-size: 18px; color: #ff9999; margin-top: 20px;")
        self.lbl_mejorar.setAlignment(Qt.AlignCenter)
        self.lbl_mejorar.setWordWrap(True)
        layout.addWidget(self.lbl_mejorar)
        
        self.btn_accion = QPushButton("Volver")
        self.btn_accion.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_accion.setFixedWidth(250)
        self.btn_accion.clicked.connect(self.procesar_accion)
        layout.addWidget(self.btn_accion, alignment=Qt.AlignCenter)
        
        self.setLayout(layout)

    def mostrar_resultados(self, nota, fallados):
        self.subtemas_fallados = fallados
        self.lbl_nota.setText(f"Nota: {nota} / 20")
        
        if nota == 20:
            self.lbl_mensaje.setText("¡Felicitaciones, ya estás listo!")
            self.lbl_mejorar.setText("")
            self.btn_accion.setText("Volver al inicio")
        else:
            self.lbl_mensaje.setText("¡No te rindas! Cada error es un paso más hacia el conocimiento perfecto. Sigue esforzándote.")
            if fallados:
                self.lbl_mejorar.setText(f"Tienes que mejorar en:\n{', '.join(fallados)}")
            else:
                self.lbl_mejorar.setText("Tienes que mejorar tu consistencia.")
            self.btn_accion.setText("¿Quieres seguir practicando?")

    def procesar_accion(self):
        if self.subtemas_fallados:
            self.main_app.pantalla_inicio.cargar_subtemas(self.main_app.tema_actual, self.subtemas_fallados)
        else:
            self.main_app.pantalla_inicio.cargar_subtemas("", [])
            
        self.main_app.cambiar_pantalla(self.main_app.pantalla_inicio)

class AppMatematicas(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Proyecto Final - Matemáticas")
        self.resize(900, 600)
        self.setStyleSheet(ESTILO_GLOBAL)
        
        self.tema_actual = ""
        self.subtemas_actuales = []
        
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        self.pantalla_inicio = PantallaInicio(self)
        self.pantalla_carga1 = PantallaCarga1(self)
        self.pantalla_minijuegos = PantallaMinijuegos(self)
        self.pantalla_carga2 = PantallaCarga2(self)
        self.pantalla_examen = PantallaExamen(self)
        self.pantalla_resultados = PantallaResultados(self)
        
        self.stack.addWidget(self.pantalla_inicio)
        self.stack.addWidget(self.pantalla_carga1)
        self.stack.addWidget(self.pantalla_minijuegos)
        self.stack.addWidget(self.pantalla_carga2)
        self.stack.addWidget(self.pantalla_examen)
        self.stack.addWidget(self.pantalla_resultados)
        
        self.cambiar_pantalla(self.pantalla_inicio)

    def cambiar_pantalla(self, widget):
        self.stack.setCurrentWidget(widget)

    def iniciar_flujo(self, tema, subtemas):
        self.tema_actual = tema
        self.subtemas_actuales = subtemas
        self.pantalla_minijuegos.preparar(subtemas)
        self.cambiar_pantalla(self.pantalla_carga1)
        self.pantalla_carga1.iniciar()

    def iniciar_examen(self):
        self.pantalla_examen.iniciar(self.subtemas_actuales)
        self.cambiar_pantalla(self.pantalla_examen)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ventana = AppMatematicas()
    ventana.show()
    sys.exit(app.exec_())