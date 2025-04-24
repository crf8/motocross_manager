# ui/main_window.py
from PyQt6.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QWidget, QMessageBox
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
import os
import subprocess
import platform
import json

from .piloti_tab import PilotiTab
from .eventi_tab import EventiTab
from .iscrizioni_tab import IscrizioniTab
# Importiamo la nuova versione della scheda prove libere
from ui.practice_tab import PracticeTab
from .qualifications_tab import QualificationsTab
from .penalties_tab import PenaltiesTab
from .standings_manager import StandingsManager
from ui.pilot_statistics import PilotStatistics
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtGui import QAction

from config import APP_NAME, APP_VERSION

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Imposta il titolo della finestra
        self.setWindowTitle(f"{APP_NAME} - v{APP_VERSION}")
        
        # Imposta le dimensioni della finestra
        self.resize(1200, 800)
        
        # Crea una barra degli strumenti per accesso rapido
        toolbar = self.addToolBar("Strumenti")

        # Aggiungi il pulsante Yara nella barra
        yara_toolbar_action = QAction(QIcon("ui/icons/yara_icon.png"), "Yara", self)
        yara_toolbar_action.setToolTip("Apri Yara - il tuo assistente virtuale")
        yara_toolbar_action.triggered.connect(self.show_yara_assistant)
        toolbar.addAction(yara_toolbar_action)
        
       # Crea il widget centrale
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Creazione della barra dei menu
        self.menu_bar = self.menuBar()

        # Menu File
        self.file_menu = self.menu_bar.addMenu("File")

        # Azioni del menu File
        self.new_db_action = QAction("Nuovo Database", self)
        self.new_db_action.triggered.connect(self.new_database)
        self.file_menu.addAction(self.new_db_action)

        self.open_db_action = QAction("Apri Database...", self)
        self.open_db_action.triggered.connect(self.open_database)
        self.file_menu.addAction(self.open_db_action)

        self.file_menu.addSeparator()

        self.backup_db_action = QAction("Backup Database...", self)
        self.backup_db_action.triggered.connect(self.backup_database)
        self.file_menu.addAction(self.backup_db_action)

        self.export_data_action = QAction("Esporta Dati...", self)
        self.export_data_action.triggered.connect(self.export_data)
        self.file_menu.addAction(self.export_data_action)

        self.file_menu.addSeparator()

        self.print_action = QAction("Stampa...", self)
        self.print_action.triggered.connect(self.print_document)
        self.file_menu.addAction(self.print_action)

        self.file_menu.addSeparator()

        self.exit_action = QAction("Esci", self)
        self.exit_action.triggered.connect(self.close)
        self.file_menu.addAction(self.exit_action)

        # Menu Opzioni
        self.options_menu = self.menu_bar.addMenu("Opzioni")

        self.settings_action = QAction("Impostazioni...", self)
        self.settings_action.triggered.connect(self.show_settings)
        self.options_menu.addAction(self.settings_action)

        self.user_prefs_action = QAction("Preferenze Utente...", self)
        self.user_prefs_action.triggered.connect(self.show_user_preferences)
        self.options_menu.addAction(self.user_prefs_action)

        self.options_menu.addSeparator()

        self.check_updates_action = QAction("Controlla Aggiornamenti", self)
        self.check_updates_action.triggered.connect(self.check_for_updates)
        self.options_menu.addAction(self.check_updates_action)

        self.about_action = QAction("Informazioni sul Programma", self)
        self.about_action.triggered.connect(self.show_about)
        self.options_menu.addAction(self.about_action)

        # Aggiungi Yara al menu Opzioni
        self.yara_action = QAction("Yara - Assistente Virtuale", self)
        self.yara_action.triggered.connect(self.show_yara_assistant)
        self.options_menu.addAction(self.yara_action)

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
        
        # Collegamento del pulsante statistiche della scheda piloti
        # (Aggiungeremo questa riga dopo aver modificato PilotiTab)
        self.piloti_tab.btn_statistiche.clicked.connect(self.visualizza_statistiche_pilota_selezionato)
        
        self.tabs.addTab(self.piloti_tab, "Piloti")
        self.tabs.addTab(self.eventi_tab, "Eventi")
        self.tabs.addTab(self.iscrizioni_tab, "Iscrizioni")
        self.tabs.addTab(self.practice_tab, "Prove Libere")
        self.tabs.addTab(self.qualifications_tab, "Qualifiche")
        self.tabs.addTab(self.penalties_tab, "Gestione Penalità")
        self.tabs.addTab(self.standings_manager_tab, "Classifiche e Statistiche")
        
        # Aggiungi le schede al layout
        layout.addWidget(self.tabs)

    # Aggiungere anche questa funzione alla classe MainWindow
    def show_assistant(self):
        """Mostra l'assistente virtuale Yara"""
        from ui.mx_assistant import MXAssistant  # Assicurati che questa sia la classe corretta
        assistant = MXAssistant(self)
        assistant.exec()
    
    def visualizza_statistiche_pilota(self, pilot_id):
        """
        Mostra le statistiche di un pilota.
        
        Args:
            pilot_id (int): L'ID del pilota di cui visualizzare le statistiche
        """
        try:
            # Colleghiamo il nostro programma al database
            stats_manager = PilotStatistics('motocross.db')
            
            # Chiediamo le statistiche del pilota selezionato
            statistiche = stats_manager.calculate_pilot_statistics(pilot_id)
            
            if not statistiche:
                QMessageBox.information(self, "Informazione", "Non ci sono ancora statistiche per questo pilota.")
                return
            
            # Creiamo una nuova finestra per mostrare le statistiche
            from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QFrame, QPushButton, QHBoxLayout
            
            stats_window = QDialog(self)
            stats_window.setWindowTitle(f"Statistiche - {statistiche['pilot_name']}")
            stats_window.resize(600, 500)
            
            # Layout principale
            main_layout = QVBoxLayout(stats_window)
            
            # Titolo
            title_label = QLabel(f"Statistiche di {statistiche['pilot_name']}")
            font = title_label.font()
            font.setPointSize(16)
            font.setBold(True)
            title_label.setFont(font)
            main_layout.addWidget(title_label)
            
            # Frame per le statistiche
            stats_frame = QFrame()
            stats_frame.setFrameShape(QFrame.Shape.StyledPanel)
            stats_layout = QVBoxLayout(stats_frame)
            
            # Aggiungiamo le statistiche principali
            stats_layout.addWidget(QLabel(f"Gare disputate: {statistiche['total_races']}"))
            stats_layout.addWidget(QLabel(f"Vittorie: {statistiche['wins']}"))
            stats_layout.addWidget(QLabel(f"Podi: {statistiche['podiums']}"))
            stats_layout.addWidget(QLabel(f"Punti totali: {statistiche['total_points']}"))
            stats_layout.addWidget(QLabel(f"Media punti: {statistiche['average_points_per_race']:.2f}"))
            
            main_layout.addWidget(stats_frame)
            
            # Frame per i pulsanti
            button_frame = QFrame()
            button_layout = QHBoxLayout(button_frame)
            
            # Pulsante per generare report HTML
            btn_report = QPushButton("Genera Report HTML")
            btn_report.clicked.connect(lambda: self.genera_report(stats_manager, pilot_id))
            button_layout.addWidget(btn_report)
            
            # Pulsante per visualizzare grafico
            btn_chart = QPushButton("Visualizza Grafico Posizioni")
            btn_chart.clicked.connect(lambda: self.visualizza_grafico(stats_manager.visualize_pilot_performance(pilot_id, 'position_trend')))
            button_layout.addWidget(btn_chart)
            
            main_layout.addWidget(button_frame)
            
            # Mostriamo la finestra
            stats_window.exec()
            
            # Chiudiamo la connessione al database quando abbiamo finito
            stats_manager.close_db()
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Si è verificato un errore: {str(e)}")
    
    def genera_report(self, stats_manager, pilot_id):
        """
        Genera un report HTML delle statistiche del pilota.
        
        Args:
            stats_manager (PilotStatistics): Il gestore delle statistiche
            pilot_id (int): L'ID del pilota
        """
        try:
            report_path = stats_manager.generate_statistics_report(pilot_id, 'html')
            if report_path:
                QMessageBox.information(self, "Report", f"Report salvato in: {report_path}")
                # Opzionale: aprire il report
                self.visualizza_grafico(report_path)
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante la generazione del report: {str(e)}")
    
    def visualizza_grafico(self, percorso_file):
        """
        Apre un file (grafico o report) con l'applicazione predefinita.
        
        Args:
            percorso_file (str): Il percorso del file da aprire
        """
        if percorso_file and os.path.exists(percorso_file):
            try:
                # Apre il file con il programma predefinito del sistema operativo
                if platform.system() == 'Windows':
                    os.startfile(percorso_file)
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.call(('open', percorso_file))
                else:  # Linux
                    subprocess.call(('xdg-open', percorso_file))
            except Exception as e:
                QMessageBox.warning(self, "Attenzione", f"Impossibile aprire il file: {str(e)}")
        else:
            QMessageBox.information(self, "Informazione", "Il file non esiste o non è stato generato correttamente.")
    
    def visualizza_statistiche_pilota_selezionato(self):
        """
        Ottiene il pilota selezionato nella tabella e mostra le sue statistiche.
        Questa funzione è collegata al pulsante nella scheda Piloti.
        """
        try:
            # Otteniamo la riga selezionata nella tabella
            selected_indexes = self.piloti_tab.table_piloti.selectedIndexes()
            
            if not selected_indexes:
                QMessageBox.information(self, "Informazione", "Seleziona prima un pilota dalla tabella.")
                return
            
            # Prendiamo l'ID del pilota selezionato (è nella prima colonna)
            row = selected_indexes[0].row()
            pilot_id = self.piloti_tab.table_piloti.item(row, 0).text()
            
            # Chiamiamo la funzione che mostra le statistiche
            self.visualizza_statistiche_pilota(int(pilot_id))
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Si è verificato un errore: {str(e)}")
    
    def new_database(self):
        """Crea un nuovo database"""
        reply = QMessageBox.question(self, "Nuovo Database", 
                                    "Sei sicuro di voler creare un nuovo database? Tutti i dati attuali andranno persi.",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            # Qui andrebbe il codice per creare un nuovo database
            QMessageBox.information(self, "Informazione", "Nuovo database creato con successo!")

    def open_database(self):
        """Apre un database esistente"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Apri Database", "", "Database SQLite (*.db *.sqlite);;Tutti i file (*)")
        if file_path:
            # Qui andrebbe il codice per aprire il database selezionato
            QMessageBox.information(self, "Informazione", f"Database aperto: {file_path}")

    def backup_database(self):
        """Crea una copia di backup del database attuale"""
        file_path, _ = QFileDialog.getSaveFileName(self, "Backup Database", "", "Database SQLite (*.db);;Tutti i file (*)")
        if file_path:
            # Qui andrebbe il codice per fare il backup del database
            QMessageBox.information(self, "Informazione", f"Backup completato in: {file_path}")

    def export_data(self):
        """Esporta i dati in formato CSV o Excel"""
        # Qui potresti mostrare una finestra di dialogo per scegliere cosa esportare
        QMessageBox.information(self, "Informazione", "Funzione di esportazione non ancora implementata.")

    def print_document(self):
        """Stampa report o classifiche"""
        # Qui potresti mostrare una finestra di dialogo per scegliere cosa stampare
        QMessageBox.information(self, "Informazione", "Funzione di stampa non ancora implementata.")

    def show_user_preferences(self):
        """Mostra la finestra delle preferenze utente"""
        # Qui apriresti la finestra delle preferenze
        QMessageBox.information(self, "Informazione", "Finestra preferenze non ancora implementata.")

    def check_for_updates(self):
        """Controlla se ci sono aggiornamenti disponibili"""
        # Qui andresti a controllare online per nuovi aggiornamenti
        QMessageBox.information(self, "Informazione", "Nessun aggiornamento disponibile.")

    def show_about(self):
        """Mostra informazioni sul programma"""
        about_text = f"{APP_NAME} - v{APP_VERSION}\n\n"
        about_text += "Programma per la gestione di gare di motocross\n\n"
        about_text += "Sviluppato da: Il tuo nome qui\n"
        about_text += "Copyright © 2023 - Tutti i diritti riservati"
        
        QMessageBox.about(self, "Informazioni sul Programma", about_text)

    def show_settings(self):
        """Mostra la finestra delle impostazioni"""
        from ui.settings_dialog import SettingsDialog
        settings_dialog = SettingsDialog(self)
        settings_dialog.exec()

    def show_yara_assistant(self):
        """Mostra l'assistente virtuale Yara"""
        try:
            from ui.yara_assistant import YaraAssistant
            assistant = YaraAssistant(self)
            assistant.exec()
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Impossibile avviare Yara: {str(e)}")