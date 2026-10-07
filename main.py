import sys
import os
import json
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QComboBox, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QFrame
)
from PyQt5.QtCore import Qt


class GestorGastos:
    def __init__(self, ruta_archivo: str = "data/gastos.json"):
        self.ruta_archivo = ruta_archivo
        self.transacciones = []
        self._asegurar_directorio()
        self.cargar_datos()

    def _asegurar_directorio(self):
        directorio = os.path.dirname(self.ruta_archivo)
        if directorio and not os.path.exists(directorio):
            os.makedirs(directorio, exist_ok=True)

    def cargar_datos(self):
        if os.path.exists(self.ruta_archivo):
            try:
                with open(self.ruta_archivo, "r", encoding="utf-8") as f:
                    self.transacciones = json.load(f)
            except Exception:
                self.transacciones = []
        else:
            self.transacciones = []

    def guardar_datos(self):
        # Escritura atómica básica para evitar corrupción
        temp_path = self.ruta_archivo + ".tmp"
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(self.transacciones, f, ensure_ascii=False, indent=4)
        os.replace(temp_path, self.ruta_archivo)

    def agregar_transaccion(self, monto: float, categoria: str, descripcion: str, tipo: str) -> dict:
        nueva_t = {
            "id": len(self.transacciones) + 1,
            "monto": monto,
            "categoria": categoria,
            "descripcion": descripcion,
            "tipo": tipo,  # "ingreso" o "gasto"
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        self.transacciones.append(nueva_t)
        self.guardar_datos()
        return nueva_t

    def obtener_presupuesto_total(self) -> float:
        return sum(t["monto"] for t in self.transacciones if t.get("tipo") == "ingreso")

    def obtener_gastos_totales(self) -> float:
        return sum(t["monto"] for t in self.transacciones if t.get("tipo") == "gasto")

    def obtener_fuga_hormiga(self) -> float:
        return sum(t["monto"] for t in self.transacciones if "Hormiga" in t.get("categoria", ""))

    def obtener_disponible(self) -> float:
        return self.obtener_presupuesto_total() - self.obtener_gastos_totales()

    def reiniciar_datos(self):
        self.transacciones = []
        self.guardar_datos()


class VentanaPrincipal(QMainWindow):
    def __init__(self, gestor: GestorGastos):
        super().__init__()
        self.gestor = gestor
        self.setWindowTitle("Gestor de Gastos Hormiga & Presupuesto")
        self.setMinimumSize(880, 620)

        self.init_ui()
        self.actualizar_interfaz()

    def init_ui(self):
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        layout_principal = QVBoxLayout(widget_central)

        lbl_titulo = QLabel("🛡️ Control Financiero & Fuga de Capital (Gastos Hormiga)")
        lbl_titulo.setObjectName("lbl_titulo")
        lbl_titulo.setAlignment(Qt.AlignCenter)
        layout_principal.addWidget(lbl_titulo)

        layout_medio = QHBoxLayout()

        frame_form = QFrame()
        frame_form.setObjectName("card")
        layout_form = QVBoxLayout(frame_form)

        lbl_form_title = QLabel("📥 Nuevo Registro")
        lbl_form_title.setObjectName("subtitle")
        layout_form.addWidget(lbl_form_title)

        self.txt_monto = QLineEdit()
        self.txt_monto.setPlaceholderText("Monto ($) Ej: 2.50")
        layout_form.addWidget(self.txt_monto)

        self.combo_categoria = QComboBox()
        self.combo_categoria.addItems([
            "🐜 Gasto Hormiga (Café, Snacks, Vicios)",
            "🛒 Mercado / Alimentación Básica",
            "🚗 Transporte / Gasolina",
            "💡 Servicios / Cuentas Fijas",
            "💵 Ingreso / Adición de Presupuesto"
        ])
        layout_form.addWidget(self.combo_categoria)

        self.txt_desc = QLineEdit()
        self.txt_desc.setPlaceholderText("Descripción (Ej: Café de la tarde)")
        layout_form.addWidget(self.txt_desc)

        btn_guardar = QPushButton("💾 Guardar Transacción")
        btn_guardar.setObjectName("btn_guardar")
        btn_guardar.clicked.connect(self.agregar_registro)
        layout_form.addWidget(btn_guardar)

        btn_reset = QPushButton("🗑️ Reiniciar Todo")
        btn_reset.setObjectName("btn_reset")
        btn_reset.clicked.connect(self.reiniciar_todo)
        layout_form.addWidget(btn_reset)

        layout_medio.addWidget(frame_form, stretch=4)

        frame_metrics = QFrame()
        frame_metrics.setObjectName("card")
        layout_metrics = QVBoxLayout(frame_metrics)

        self.lbl_presupuesto = QLabel("Presupuesto Total: $0.00")
        self.lbl_gastos = QLabel("Gastos Totales: $0.00")
        self.lbl_disponible = QLabel("Disponible: $0.00")
        self.lbl_disponible.setObjectName("lbl_disponible")
        self.lbl_hormiga = QLabel("🚨 Fuga Hormiga: $0.00 (0.0%)")
        self.lbl_hormiga.setObjectName("lbl_hormiga")

        layout_metrics.addWidget(self.lbl_presupuesto)
        layout_metrics.addWidget(self.lbl_gastos)
        layout_metrics.addWidget(self.lbl_disponible)
        layout_metrics.addWidget(self.lbl_hormiga)

        layout_medio.addWidget(frame_metrics, stretch=5)
        layout_principal.addLayout(layout_medio)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(["Fecha", "Categoría", "Descripción", "Monto"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout_principal.addWidget(self.tabla)

    def agregar_registro(self):
        monto_str = self.txt_monto.text().strip().replace(",", ".")
        desc = self.txt_desc.text().strip()
        categoria = self.combo_categoria.currentText()

        if not monto_str or not desc:
            QMessageBox.warning(self, "Atención", "Por favor ingresa un monto y una descripción.")
            return

        try:
            monto = float(monto_str)
            if monto <= 0:
                QMessageBox.warning(self, "Atención", "El monto debe ser positivo.")
                return
        except ValueError:
            QMessageBox.critical(self, "Error", "El monto debe ser un valor numérico válido.")
            return

        tipo = "ingreso" if "Ingreso" in categoria else "gasto"

        self.gestor.agregar_transaccion(monto, categoria, desc, tipo)
        self.txt_monto.clear()
        self.txt_desc.clear()
        self.actualizar_interfaz()

    def actualizar_interfaz(self):
        presupuesto = self.gestor.obtener_presupuesto_total()
        gastos = self.gestor.obtener_gastos_totales()
        disponible = self.gestor.obtener_disponible()
        hormiga = self.gestor.obtener_fuga_hormiga()

        porcentaje = (hormiga / presupuesto * 100) if presupuesto > 0 else 0.0

        self.lbl_presupuesto.setText(f"Presupuesto Total: ${presupuesto:.2f}")
        self.lbl_gastos.setText(f"Gastos Totales: ${gastos:.2f}")
        
        if disponible < 0:
            self.lbl_disponible.setText(f"Disponible: ${disponible:.2f} (En Déficit)")
            self.lbl_disponible.setStyleSheet("color: #f38ba8;")
        else:
            self.lbl_disponible.setText(f"Disponible: ${disponible:.2f}")
            self.lbl_disponible.setStyleSheet("color: #a6e3a1;")

        self.lbl_hormiga.setText(f"🚨 Fuga Hormiga: ${hormiga:.2f} ({porcentaje:.1f}%)")

        self.tabla.setRowCount(0)
        for row, t in enumerate(reversed(self.gestor.transacciones)):
            self.tabla.insertRow(row)
            self.tabla.setItem(row, 0, QTableWidgetItem(t["fecha"]))
            self.tabla.setItem(row, 1, QTableWidgetItem(t["categoria"].split("(")[0].strip()))
            self.tabla.setItem(row, 2, QTableWidgetItem(t["descripcion"]))
            
            monto_item = QTableWidgetItem(f"${t['monto']:.2f}")
            monto_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            if t.get("tipo") == "ingreso":
                monto_item.setForeground(Qt.green)
            else:
                monto_item.setForeground(Qt.red)
            self.tabla.setItem(row, 3, monto_item)

    def reiniciar_todo(self):
        respuesta = QMessageBox.question(
            self, "Confirmación", 
            "¿Estás seguro de reiniciar todo el historial de gastos?",
            QMessageBox.Yes | QMessageBox.No
        )
        if respuesta == QMessageBox.Yes:
            self.gestor.reiniciar_datos()
            self.actualizar_interfaz()


ESTILOS_QCSS = """
QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-family: 'Segoe UI', sans-serif;
    font-size: 13px;
}

#lbl_titulo {
    font-size: 18px;
    font-weight: bold;
    color: #89b4fa;
    padding: 10px;
}

#subtitle {
    font-size: 15px;
    font-weight: bold;
    color: #f5e0dc;
}

QFrame#card {
    background-color: #181825;
    border-radius: 10px;
    padding: 12px;
}

QLineEdit, QComboBox {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 6px;
    color: #cdd6f4;
}

QPushButton#btn_guardar {
    background-color: #a6e3a1;
    color: #11111b;
    font-weight: bold;
    border-radius: 6px;
    padding: 8px;
}

QPushButton#btn_guardar:hover {
    background-color: #94e2d5;
}

QPushButton#btn_reset {
    background-color: #f38ba8;
    color: #11111b;
    border-radius: 6px;
    padding: 6px;
}

#lbl_disponible {
    font-size: 16px;
    font-weight: bold;
    color: #a6e3a1;
}

#lbl_hormiga {
    font-size: 14px;
    font-weight: bold;
    color: #f38ba8;
}

QTableWidget {
    background-color: #181825;
    gridline-color: #313244;
    border-radius: 8px;
}

QHeaderView::section {
    background-color: #313244;
    color: #cdd6f4;
    font-weight: bold;
    padding: 4px;
}
"""


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(ESTILOS_QCSS)

    gestor = GestorGastos(ruta_archivo="data/gastos.json")
    ventana = VentanaPrincipal(gestor)
    ventana.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()