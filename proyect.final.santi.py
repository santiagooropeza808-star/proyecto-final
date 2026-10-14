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
        
        self.offset_y = 0
        self.direccion_anim = 1
        self.timer_anim = QTimer(self)
        self.timer_anim.timeout.connect(self.animar_titulo)
        self.timer_anim.start(60)
        
        self.label_instruccion = QLabel("Escribe tu tema (solo matemáticas)")
        self.label_instruccion.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_instruccion)
        
        self.input_tema = QLineEdit()
        self.input_tema.setPlaceholderText("Ejemplo: Álgebra")
        self.input_tema.setFixedWidth(400)
        layout.addWidget(self.input_tema, alignment=Qt.AlignCenter)
        
        self.input_puntos = QLineEdit()
        self.input_puntos.setPlaceholderText("Ej: PARTE 1: Sumas, PARTE 2: Restas")
        self.input_puntos.setFixedWidth(400)
        layout.addWidget(self.input_puntos, alignment=Qt.AlignCenter)
        
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
        
        # Procesar partes si el usuario escribió "PARTE X:"
        subtemas_procesados = []
        partes_brutas = puntos_str.split(',')
        for parte in partes_brutas:
            subtemas_procesados.append(parte.strip())
            
        self.main_app.iniciar_flujo(tema, subtemas_procesados)

class PantallaCarga1(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        self.poema = QLabel("El éxito es la suma\nde pequeños esfuerzos\nrepetidos\ndía tras día.")
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
        self.nivel_maximo_desbloqueado = 1
        self.nivel_actual = 1
        self.preguntas_nivel = []
        self.respuestas_usuario = []
        self.errores_nivel = []
        self.indice_pregunta = 0
        self.fase_animacion = 0
        self.rotacion_partes = 0 # Para alternar y retroceder orden de partes
        
        layout_principal = QVBoxLayout()
        
        barra_superior = QHBoxLayout()
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        barra_superior.addItem(spacer)
        
        self.btn_finalizar = QPushButton("Ir al Examen Final")
        self.btn_finalizar.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_finalizar.clicked.connect(self.ir_a_carga_examen)
        barra_superior.addWidget(self.btn_finalizar)
        layout_principal.addLayout(barra_superior)
        
        layout_centro = QVBoxLayout()
        layout_centro.setAlignment(Qt.AlignCenter)
        self.titulo = QLabel("Área de Entrenamiento")
        self.titulo.setStyleSheet("font-size: 30px; font-weight: bold;")
        self.titulo.setAlignment(Qt.AlignCenter)
        layout_centro.addWidget(self.titulo)
        
        self.info_temas = QLabel("")
        self.info_temas.setAlignment(Qt.AlignCenter)
        self.info_temas.setStyleSheet("font-size: 20px; margin: 20px 0;")
        self.info_temas.setWordWrap(True)
        layout_centro.addWidget(self.info_temas)
        
        self.layout_dinamico_juego = QVBoxLayout()
        self.layout_dinamico_juego.setAlignment(Qt.AlignCenter)
        layout_centro.addLayout(self.layout_dinamico_juego)
        
        self.btn_jugar = QPushButton("Acción")
        self.btn_jugar.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_jugar.setFixedWidth(300)
        self.btn_jugar.setVisible(False)
        layout_centro.addWidget(self.btn_jugar, alignment=Qt.AlignCenter)
        
        layout_principal.addLayout(layout_centro)
        self.setLayout(layout_principal)

    def preparar(self, subtemas):
        self.nivel_maximo_desbloqueado = 1
        self.rotacion_partes = 0
        self.mostrar_mapa_niveles()

    def limpiar_layout_juego(self):
        while self.layout_dinamico_juego.count():
            child = self.layout_dinamico_juego.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def obtener_punto_actual_rotado(self, indice_nivel):
        subtemas = self.main_app.subtemas_actuales
        if not subtemas:
            return self.main_app.tema_actual
        # Aplicar lógica de rotación y retroceso entre partes ingresadas
        idx = (indice_nivel + self.rotacion_partes) % len(subtemas)
        return subtemas[idx]

    def mostrar_mapa_niveles(self):
        self.limpiar_layout_juego()
        self.btn_jugar.setVisible(False)
        self.titulo.setText("Mapa de Niveles - Relajante")
        self.info_temas.setText("Selecciona un nivel disponible para entrenar tu mente con tranquilidad.")
        
        total_niveles = max(4, len(self.main_app.subtemas_actuales))
        
        for i in range(1, total_niveles + 1):
            btn_nivel = QPushButton(f"Nivel {i}")
            if i <= self.nivel_maximo_desbloqueado:
                btn_nivel.setStyleSheet("background-color: #3b1066; border: 2px solid #5a1a99; color: white;")
                btn_nivel.setCursor(QCursor(Qt.PointingHandCursor))
                btn_nivel.clicked.connect(lambda checked, n=i: self.mostrar_cuadro_teoria(n))
            else:
                btn_nivel.setStyleSheet("background-color: #150524; color: #442266; border: 2px solid #22083b;")
                btn_nivel.setEnabled(False)
                
            self.layout_dinamico_juego.addWidget(btn_nivel)
            
            if i < total_niveles:
                linea = QLabel("   |   ")
                linea.setAlignment(Qt.AlignCenter)
                if i < self.nivel_maximo_desbloqueado:
                    linea.setStyleSheet("color: #b380ff; font-weight: bold;")
                else:
                    linea.setStyleSheet("color: #22083b;")
                if i == self.nivel_maximo_desbloqueado:
                    self.linea_animacion = linea
                self.layout_dinamico_juego.addWidget(linea)

    def mostrar_cuadro_teoria(self, nivel):
        self.nivel_actual = nivel
        self.limpiar_layout_juego()
        self.titulo.setText(f"Estudio - Nivel {nivel}")
        
        punto_asignado = self.obtener_punto_actual_rotado(nivel - 1)
        
        # Cuadro flotante con diseño relajante
        texto_teoria = f"┌────────────────────────────────────────┐\n" \
                       f"│ ESTUDIA ESTO CON CALMA:                │\n" \
                       f"│                                        │\n" \
                       f"│ Tema: {punto_asignado:<24} │\n" \
                       f"│                                        │\n" \
                       f"│ Comprende la lógica antes de avanzar. │\n" \
                       f"└────────────────────────────────────────┘"
        
        self.info_temas.setText(texto_teoria)
        self.info_temas.setStyleSheet("font-family: monospace; font-size: 16px; color: #d4b3ff; background-color: #150524; padding: 15px; border-radius: 10px; border: 1px solid #5a1a99;")
        
        self.btn_jugar.setText("Listo")
        try: self.btn_jugar.clicked.disconnect() 
        except: pass
        self.btn_jugar.clicked.connect(self.preparar_preguntas_nivel)
        self.btn_jugar.setVisible(True)

    def preparar_preguntas_nivel(self):
        self.preguntas_nivel = []
        self.respuestas_usuario = []
        self.errores_nivel = []
        self.indice_pregunta = 0
        self.btn_jugar.setVisible(False)
        self.info_temas.setStyleSheet("font-size: 20px; margin: 20px 0; color: #e0ccff; background: transparent; border: none;")
        
        tema = self.main_app.tema_actual
        punto_actual = self.obtener_punto_actual_rotado(self.nivel_actual - 1)

        if self.nivel_actual == 1:
            # Nivel 1: Verdadero y Falso sobre el punto asignado
            for _ in range(3):
                num = random.randint(2, 10)
                self.preguntas_nivel.append(PreguntaPrueba('vf', punto_actual, f"¿En '{punto_actual}', el factor lógico base guarda relación con el número {num}?", "Verdadero", ["Verdadero", "Falso"]))
        
        elif self.nivel_actual == 2:
            # Nivel 2: Preguntas básicas
            for _ in range(3):
                self.preguntas_nivel.append(PreguntaPrueba('abierta', punto_actual, f"Basándote en '{punto_actual}', ¿cuál es el resultado operativo básico si base=4 y sumamos 6?", "10"))
        
        elif self.nivel_actual == 3:
            # Nivel 3: ¿Qué es? (AHORA ES DE ESCRIBIR, NO DE ELEGIR)
            for _ in range(2):
                self.preguntas_nivel.append(PreguntaPrueba('abierta', punto_actual, f"Escribe con tus palabras qué es '{punto_actual}':", f"es el estudio de {tema.lower()}"))
        
        elif self.nivel_actual == 4:
            # Nivel 4: Ejercicios con procedimiento
            for _ in range(2):
                self.preguntas_nivel.append(PreguntaPrueba('procedimiento', punto_actual, f"Resuelve con procedimiento para '{punto_actual}' (formato: paso a paso -> resultado 5):", "5"))
        else:
            # Niveles extra
            self.iniciar_minijuego_clasico()
            return

        self.mostrar_pregunta_actual()

    def mostrar_pregunta_actual(self):
        if self.indice_pregunta >= len(self.preguntas_nivel):
            self.evaluar_nivel()
            return
            
        self.limpiar_layout_juego()
        pregunta = self.preguntas_nivel[self.indice_pregunta]
        self.info_temas.setText(f"Pregunta {self.indice_pregunta + 1}/{len(self.preguntas_nivel)}\n\n{pregunta.texto}")
        
        if pregunta.tipo == 'vf':
            for opcion in pregunta.opciones:
                btn = QPushButton(opcion)
                btn.setCursor(QCursor(Qt.PointingHandCursor))
                btn.clicked.connect(lambda checked, o=opcion: self.registrar_respuesta(o))
                self.layout_dinamico_juego.addWidget(btn)
                
        elif pregunta.tipo == 'abierta' or pregunta.tipo == 'procedimiento':
            self.input_juego = QLineEdit()
            if pregunta.tipo == 'procedimiento':
                self.input_juego.setPlaceholderText("Escribe procedimiento y resultado...")
            else:
                self.input_juego.setPlaceholderText("Escribe tu respuesta aquí...")
            self.input_juego.setFixedWidth(450)
            self.input_juego.setAlignment(Qt.AlignCenter)
            self.input_juego.returnPressed.connect(self.procesar_input_nivel)
            self.layout_dinamico_juego.addWidget(self.input_juego, alignment=Qt.AlignCenter)
            self.input_juego.setFocus()
            
            btn_ok = QPushButton("Siguiente")
            btn_ok.setCursor(QCursor(Qt.PointingHandCursor))
            btn_ok.clicked.connect(self.procesar_input_nivel)
            self.layout_dinamico_juego.addWidget(btn_ok, alignment=Qt.AlignCenter)

    def procesar_input_nivel(self):
        if hasattr(self, 'input_juego'):
            respuesta = self.input_juego.text().strip()
            if respuesta:
                self.registrar_respuesta(respuesta)

    def registrar_respuesta(self, respuesta):
        pregunta = self.preguntas_nivel[self.indice_pregunta]
        # No se muestra feedback inmediato, solo se guarda
        self.respuestas_usuario.append({'pregunta': pregunta, 'respuesta': respuesta})
        self.indice_pregunta += 1
        self.mostrar_pregunta_actual()

    def evaluar_nivel(self):
        self.limpiar_layout_juego()
        self.titulo.setText(f"Resultados - Nivel {self.nivel_actual}")
        
        self.errores_nivel = []
        for item in self.respuestas_usuario:
            p = item['pregunta']
            r = item['respuesta']
            correcta = False
            
            if p.tipo == 'procedimiento':
                if p.respuesta_correcta in r and len(r) > 3:
                    correcta = True
            elif p.tipo == 'abierta' and "qué es" in p.texto.lower():
                # Validación flexible para definición escrita
                if len(r) > 2:
                    correcta = True
            else:
                if r.lower() == p.respuesta_correcta.lower():
                    correcta = True
                    
            if not correcta:
                self.errores_nivel.append(p)
                
        if len(self.errores_nivel) == 0:
            self.info_temas.setText("¡Excelente nivel superado con total calma y precisión!")
            if self.nivel_actual == self.nivel_maximo_desbloqueado:
                self.nivel_maximo_desbloqueado += 1
                self.btn_jugar.setText("Siguiente Nivel")
                try: self.btn_jugar.clicked.disconnect() 
                except: pass
                self.btn_jugar.clicked.connect(self.animar_progreso)
                self.btn_jugar.setVisible(True)
            else:
                self.btn_jugar.setText("Volver al Mapa")
                try: self.btn_jugar.clicked.disconnect() 
                except: pass
                self.btn_jugar.clicked.connect(self.mostrar_mapa_niveles)
                self.btn_jugar.setVisible(True)
        else:
            texto_error = "En donde fallaste:\n\n"
            for err in self.errores_nivel:
                texto_error += f"- {err.texto}\n"
            texto_error += "\n¿Qué deseas hacer?"
            self.info_temas.setText(texto_error)
            
            btn_reiniciar = QPushButton("Reiniciar lo que falló")
            btn_reiniciar.setCursor(QCursor(Qt.PointingHandCursor))
            btn_reiniciar.clicked.connect(self.reiniciar_fallos)
            self.layout_dinamico_juego.addWidget(btn_reiniciar)
            
            btn_seguir = QPushButton("Seguir a los demás niveles")
            btn_seguir.setStyleSheet("background-color: #2a0b4d; color: #a366ff;")
            btn_seguir.setCursor(QCursor(Qt.PointingHandCursor))
            btn_seguir.clicked.connect(self.forzar_siguiente_nivel)
            self.layout_dinamico_juego.addWidget(btn_seguir)

    def reiniciar_fallos(self):
        self.preguntas_nivel = self.errores_nivel
        self.errores_nivel = []
        self.respuestas_usuario = []
        self.indice_pregunta = 0
        self.mostrar_pregunta_actual()
        
    def forzar_siguiente_nivel(self):
        if self.nivel_actual == self.nivel_maximo_desbloqueado:
            self.nivel_maximo_desbloqueado += 1
        self.animar_progreso()

    def animar_progreso(self):
        self.mostrar_mapa_niveles()
        self.fase_animacion = 0
        self.timer_linea = QTimer(self)
        self.timer_linea.timeout.connect(self.paso_animacion)
        self.timer_linea.start(200)
        
    def paso_animacion(self):
        self.fase_animacion += 1
        if hasattr(self, 'linea_animacion'):
            if self.fase_animacion == 1:
                self.linea_animacion.setText("   ↓   ")
                self.linea_animacion.setStyleSheet("color: #a366ff; font-weight: bold;")
            elif self.fase_animacion == 2:
                # Animación de retroceso/rotación de partes al avanzar
                self.rotacion_partes += 1
                self.linea_animacion.setText("   ◄   ")
            elif self.fase_animacion > 2:
                self.linea_animacion.setText("   |   ")
                self.linea_animacion.setStyleSheet("color: #b380ff; font-weight: bold;")
                self.timer_linea.stop()
                
                self.btn_jugar.setText(f"Empezar Nivel {self.nivel_maximo_desbloqueado}")
                try: self.btn_jugar.clicked.disconnect() 
                except: pass
                self.btn_jugar.clicked.connect(lambda: self.mostrar_cuadro_teoria(self.nivel_maximo_desbloqueado))
                self.btn_jugar.setVisible(True)

    def iniciar_minijuego_clasico(self):
        subtemas = self.main_app.subtemas_actuales
        tema_elegido = random.choice(subtemas).upper() if subtemas else self.main_app.tema_actual.upper()
        
        juegos_disponibles = ['anagrama', 'completar', 'memoria']
        juego_seleccionado = random.choice(juegos_disponibles)
        
        if juego_seleccionado == 'anagrama':
            self.juego_anagrama(tema_elegido)
        elif juego_seleccionado == 'completar':
            self.juego_completar(tema_elegido)
        elif juego_seleccionado == 'memoria':
            self.juego_memoria(tema_elegido)

    def juego_anagrama(self, tema):
        self.palabra_secreta = tema
        letras = list(tema.replace(" ", ""))
        random.shuffle(letras)
        self.info_temas.setText(f"🧠 Minijuego Extra: Anagrama\n\nOrdena las letras:\n\n{' '.join(letras)}")
        self.crear_input_texto("Escribe la palabra ordenada...")

    def juego_completar(self, tema):
        self.palabra_secreta = tema
        letras = list(tema)
        indices = random.sample(range(len(letras)), max(1, len(letras)//2))
        for i in indices:
            if letras[i] != " ": letras[i] = "_"
        self.info_temas.setText(f"✍️ Minijuego Extra: Completar\n\nAdivina:\n\n{' '.join(letras)}")
        self.crear_input_texto("Escribe completo...")

    def juego_memoria(self, tema):
        self.palabra_secreta = tema
        self.info_temas.setText(f"👁️ Minijuego Extra: Memoria Rápida\n\nMemoriza:\n\n{tema}")
        QTimer.singleShot(2500, self.mostrar_opciones_memoria)

    def mostrar_opciones_memoria(self):
        self.info_temas.setText("¿Cuál fue el tema?")
        self.limpiar_layout_juego()
        opciones = [self.palabra_secreta]
        fakes = ["MATEMÁTICA", "ÁLGEBRA", "GEOMETRÍA", "CÁLCULO"]
        random.shuffle(fakes)
        for f in fakes:
            if f != self.palabra_secreta and len(opciones) < 3: opciones.append(f)
        random.shuffle(opciones)
        for op in opciones:
            btn = QPushButton(op)
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            btn.clicked.connect(lambda checked, o=op: self.verificar_memoria(o))
            self.layout_dinamico_juego.addWidget(btn)

    def verificar_memoria(self, seleccion):
        self.limpiar_layout_juego()
        if seleccion == self.palabra_secreta:
            self.info_temas.setText("¡Excelente memoria!")
            self.nivel_maximo_desbloqueado += 1
            self.btn_jugar.setText("Siguiente Nivel")
            try: self.btn_jugar.clicked.disconnect() 
            except: pass
            self.btn_jugar.clicked.connect(self.animar_progreso)
            self.btn_jugar.setVisible(True)
        else:
            self.info_temas.setText(f"Era: {self.palabra_secreta}")
            self.btn_jugar.setText("Reintentar")
            try: self.btn_jugar.clicked.disconnect() 
            except: pass
            self.btn_jugar.clicked.connect(self.iniciar_minijuego_clasico)
            self.btn_jugar.setVisible(True)

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
            self.info_temas.setText("¡Correcto!")
            self.limpiar_layout_juego()
            self.nivel_maximo_desbloqueado += 1
            self.btn_jugar.setText("Siguiente Nivel")
            try: self.btn_jugar.clicked.disconnect() 
            except: pass
            self.btn_jugar.clicked.connect(self.animar_progreso)
            self.btn_jugar.setVisible(True)
        else:
            self.input_juego.setStyleSheet("border: 1px solid #ff4d4d;")
            QTimer.singleShot(800, lambda: self.input_juego.setStyleSheet(""))

    def ir_a_carga_examen(self):
        self.btn_finalizar.setText("Cargando Examen...")
        QTimer.singleShot(1000, lambda: self.main_app.pantalla_carga2.iniciar())
        QTimer.singleShot(1500, lambda: self.btn_finalizar.setText("Ir al Examen Final"))


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
        self.texto_dinamico.setText("Prepárate para el examen final...")
        QTimer.singleShot(2000, self.desaparecer)

    def desaparecer(self):
        self.texto_dinamico.setText("")
        QTimer.singleShot(1500, self.mostrar_poema)

    def mostrar_poema(self):
        frase = "No te rindas.\nCada error es un escalón\nhacia tu meta final."
        self.texto_dinamico.setText(frase)
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
            # Examen basado directamente en los minijuegos y puntos vistos
            self.preguntas.append(PreguntaPrueba('abierta', st, f"Examen de {st}:\nEscribe el resultado principal:", "10"))
            self.preguntas.append(PreguntaPrueba('procedimiento', st, f"Demuestra con procedimiento para {st}:", "5"))
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
        
        self.input_respuesta = QLineEdit()
        self.input_respuesta.setPlaceholderText("Escribe respuesta y presiona Enter...")
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
        if len(respuesta_usuario) > 1:
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
            self.lbl_mensaje.setText("¡Felicitaciones, lo lograste con calma y éxito!")
            self.lbl_mejorar.setText("")
            self.btn_accion.setText("Volver al inicio")
        else:
            self.lbl_mensaje.setText("¡Buen esfuerzo! La práctica constante te llevará a la maestría.")
            if fallados:
                self.lbl_mejorar.setText(f"Debes repasar en:\n{', '.join(fallados)}")
            self.btn_accion.setText("Seguir practicando")

    def procesar_accion(self):
        if self.subtemas_fallados:
            self.main_app.pantalla_inicio.cargar_subtemas(self.main_app.tema_actual, self.subtemas_fallados)
        else:
            self.main_app.pantalla_inicio.cargar_subtemas("", [])
        self.main_app.cambiar_pantalla(self.main_app.pantalla_inicio)

class AppMatematicas(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Proyecto Final - Matemáticas Relax")
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