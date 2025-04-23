# Importiamo le librerie di base
from PyQt6.QtWidgets import QApplication
import sys

# Importiamo le nostre classi dalle cartelle giuste
from ui.piloti_tab import PilotiTab
from ui.eventi_tab import EventiTab
from ui.iscrizioni_tab import IscrizioniTab
from ui.practice_tab import PracticeTab
from ui.qualifications_tab import QualificationsTab
from ui.penalties_tab import PenaltiesTab
from ui.standings_manager import StandingsManager
from ui.race_groups_manager import RaceGroupsManager  # Aggiungi questa importazione
from ui.main_window import MainWindow

# Importazione per inizializzare il database
from database.connection import engine, Base
from database import init_db

# Configurazione dell'applicazione
from config import APP_NAME, APP_VERSION

if __name__ == "__main__":
    # Inizializziamo il database
    init_db()
   
    # Creiamo l'applicazione Qt
    app = QApplication(sys.argv)
   
    # Creiamo la finestra principale
    window = MainWindow()
    
    # Aggiungiamo la nuova scheda per la gestione dei gruppi di gara
    window.race_groups_tab = RaceGroupsManager()
    window.tabs.addTab(window.race_groups_tab, "Gruppi di Gara")
   
    # Mostriamo la finestra
    window.show()
   
    # Eseguiamo l'applicazione
    sys.exit(app.exec())