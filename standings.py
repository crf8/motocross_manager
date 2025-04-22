# ui/main_window.py
from PyQt6.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt
from .registration import RegistrationForm
from .events import EventsManager
from .timing import TimingModule
from .standings import StandingsModule

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("MX Manager - Software Gestione Gare Motocross")
        self.setMinimumSize(1024, 768)
        
        # Widget centrale con tabs
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Layout principale
        self.layout = QVBoxLayout(self.central_widget)
        
        # Tab widget per organizzare le varie sezioni
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        
        # Tab per la registrazione piloti
        self.registration_tab = RegistrationForm()
        self.tabs.addTab(self.registration_tab, "Registrazione Piloti")
        
        # Tab per la gestione eventi
        self.events_tab = EventsManager()
        self.tabs.addTab(self.events_tab, "Gestione Eventi")
        
        # Tab per il cronometraggio
        self.timing_tab = TimingModule()
        self.tabs.addTab(self.timing_tab, "Cronometraggio")
        
        # Tab per le classifiche
        self.standings_tab = StandingsModule()
        self.tabs.addTab(self.standings_tab, "Classifiche")