# ui/classifiche_tab.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class ClassificheTab(QWidget):
    def __init__(self):
        super().__init__()
        
        # Crea il layout principale
        layout = QVBoxLayout(self)
        
        # Aggiungi un'etichetta temporanea
        label = QLabel("Scheda Classifiche - In costruzione")
        layout.addWidget(label)