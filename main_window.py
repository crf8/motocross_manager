# ui/main_window.py
from PyQt6.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QWidget
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

from .piloti_tab import PilotiTab
from .eventi_tab import EventiTab
from .iscrizioni_tab import IscrizioniTab
# Importiamo la nuova versione della scheda prove libere
from ui.practice_tab import PracticeTab
from .qualifications_tab import QualificationsTab
from .penalties_tab import PenaltiesTab
from .standings_manager import StandingsManager

from config import APP_NAME, APP_VERSION

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Imposta il titolo della finestra
        self.setWindowTitle(f"{APP_NAME} - v{APP_VERSION}")
        
        # Imposta le dimensioni della finestra
        self.resize(1200, 800)
        
        # Crea il widget centrale
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Crea il layout principale
        layout = QVBoxLayout(central_widget)
        
        # Crea il widget a schede
        self.tabs = QTabWidget()
        
        # Aggiungi le schede
        self.piloti_tab = PilotiTab()
        self.eventi_tab = EventiTab()
        self.iscrizioni_tab = IscrizioniTab()
        self.practice_tab = PracticeTab()  # Utilizziamo la nuova versione della scheda
        self.qualifications_tab = QualificationsTab()
        self.penalties_tab = PenaltiesTab()
        self.standings_manager_tab = StandingsManager()
        self.tabs.addTab(self.piloti_tab, "Piloti")
        self.tabs.addTab(self.eventi_tab, "Eventi")
        self.tabs.addTab(self.iscrizioni_tab, "Iscrizioni")
        self.tabs.addTab(self.practice_tab, "Prove Libere")
        self.tabs.addTab(self.qualifications_tab, "Qualifiche")
        self.tabs.addTab(self.penalties_tab, "Gestione Penalità")
        self.tabs.addTab(self.standings_manager_tab, "Classifiche e Statistiche")
        
        # Aggiungi le schede al layout
        layout.addWidget(self.tabs)