# ui/statistics.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLabel, QComboBox, QPushButton, QGroupBox,
    QMessageBox, QTabWidget
)
from PyQt6.QtCore import Qt

from sqlalchemy.orm import Session
from database.connection import SessionLocal
from database.models import Pilota, Evento, Categoria

class StatisticsModule(QWidget):
    def __init__(self):
        super().__init__()
        
        # Layout principale
        self.layout = QVBoxLayout(self)
        
        # Titolo
        self.title_label = QLabel("Statistiche e Grafici")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.layout.addWidget(self.title_label)
        
        # Tab widget per diverse tipologie di statistiche
        self.tabs = QTabWidget()
        
        # Tab per statistiche pilota
        self.rider_stats_tab = RiderStatsTab()
        self.tabs.addTab(self.rider_stats_tab, "Statistiche Pilota")
        
        # Tab per confronto piloti
        self.comparison_tab = RidersComparisonTab()
        self.tabs.addTab(self.comparison_tab, "Confronto Piloti")
        
        # Tab per statistiche evento
        self.event_stats_tab = EventStatsTab()
        self.tabs.addTab(self.event_stats_tab, "Statistiche Evento")
        
        # Tab per statistiche campionato
        self.championship_stats_tab = ChampionshipStatsTab()
        self.tabs.addTab(self.championship_stats_tab, "Statistiche Campionato")
        
        self.layout.addWidget(self.tabs)

class RiderStatsTab(QWidget):
    def __init__(self):
        super().__init__()
        
        # Layout principale
        self.layout = QVBoxLayout(self)
        
        # Selettori
        self.selectors_layout = QFormLayout()
        
        self.rider_combo = QComboBox()
        self.selectors_layout.addRow("Pilota:", self.rider_combo)
        
        self.championship_combo = QComboBox()
        self.championship_combo.addItems(["Campionato Regionale Lombardia 2025", "Trofeo Lombardia 2025"])
        self.selectors_layout.addRow("Campionato:", self.championship_combo)
        
        self.layout.addLayout(self.selectors_layout)
        
        # Bottone carica
        self.load_button = QPushButton("Carica Statistiche")
        self.load_button.clicked.connect(self.load_stats)
        self.layout.addWidget(self.load_button)
        
        # Pannello dati riassuntivi
        self.summary_group = QGroupBox("Dati Riassuntivi")
        self.summary_layout = QFormLayout()
        
        self.total_races_label = QLabel("0")
        self.summary_layout.addRow("Gare disputate:", self.total_races_label)
        
        self.podiums_label = QLabel("0")
        self.summary_layout.addRow("Podi:", self.podiums_label)
        
        self.wins_label = QLabel("0")
        self.summary_layout.addRow("Vittorie:", self.wins_label)
        
        self.points_label = QLabel("0")
        self.summary_layout.addRow("Punti totali:", self.points_label)
        
        self.best_result_label = QLabel("-")
        self.summary_layout.addRow("Miglior risultato:", self.best_result_label)
        
        self.best_lap_label = QLabel("-")
        self.summary_layout.addRow("Miglior giro:", self.best_lap_label)
        
        self.summary_group.setLayout(self.summary_layout)
        self.layout.addWidget(self.summary_group)
        
        # Grafici performance
        self.performance_group = QGroupBox("Grafici Performance")
        self.performance_layout = QVBoxLayout()
        
        self.performance_label = QLabel("Grafici performance da implementare")
        self.performance_layout.addWidget(self.performance_label)
        
        self.performance_group.setLayout(self.performance_layout)
        self.layout.addWidget(self.performance_group)
        
        # Carica piloti nel combo
        self.load_riders_combo()
    
    def load_riders_combo(self):
        """Carica i piloti nel combobox"""
        try:
            db = SessionLocal()
            piloti = db.query(Pilota).all()
            
            self.rider_combo.clear()
            for pilota in piloti:
                self.rider_combo.addItem(f"{pilota.nome} {pilota.cognome}", pilota.id)
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante il caricamento piloti: {str(e)}")
        finally:
            db.close()
    
    def load_stats(self):
        """Carica le statistiche del pilota selezionato"""
        if self.rider_combo.count() == 0:
            return
        
        pilota_id = self.rider_combo.currentData()
        if not pilota_id:
            return
        
        # Implementazione da completare - caricamento statistiche dal DB
        # Per ora mostriamo dati di esempio
        
        # Dati di esempio
        self.total_races_label.setText("7")
        self.podiums_label.setText("5")
        self.wins_label.setText("2")
        self.points_label.setText("1510")
        self.best_result_label.setText("1° (Gara 1, Gara 4, Gara 7)")
        self.best_lap_label.setText("1:42.567 (Circuito Ottobiano, Gara 3)")
        
        # Qui implementeremo la generazione dei grafici

class RidersComparisonTab(QWidget):
    def __init__(self):
        super().__init__()
        
        # Layout principale
        self.layout = QVBoxLayout(self)
        
        # Selettori
        self.selectors_layout = QFormLayout()
        
        self.rider1_combo = QComboBox()
        self.selectors_layout.addRow("Pilota 1:", self.rider1_combo)
        
        self.rider2_combo = QComboBox()
        self.selectors_layout.addRow("Pilota 2:", self.rider2_combo)
        
        self.championship_combo = QComboBox()
        self.championship_combo.addItems(["Campionato Regionale Lombardia 2025", "Trofeo Lombardia 2025"])
        self.selectors_layout.addRow("Campionato:", self.championship_combo)
        
        self.layout.addLayout(self.selectors_layout)
        
        # Bottone carica
        self.load_button = QPushButton("Confronta Piloti")
        self.load_button.clicked.connect(self.load_comparison)
        self.layout.addWidget(self.load_button)
        
        # Grafici confronto
        self.comparison_group = QGroupBox("Grafico Confronto Piloti")
        self.comparison_layout = QVBoxLayout()
        
        self.comparison_label = QLabel("Grafico confronto da implementare")
        self.comparison_layout.addWidget(self.comparison_label)
        
        self.comparison_group.setLayout(self.comparison_layout)
        self.layout.addWidget(self.comparison_group)
        
        # Tabella confronto dati
        self.table_group = QGroupBox("Dati Confronto")
        self.table_layout = QFormLayout()
        
        self.header_label = QLabel("Statistiche")
        self.rider1_header = QLabel("Pilota 1")
        self.rider2_header = QLabel("Pilota 2")
        
        self.table_layout.addRow(self.header_label, QWidget())
        self.table_layout.addRow("", QWidget())
        
        self.points_label = QLabel("Punti totali:")
        self.points_rider1 = QLabel("0")
        self.points_rider2 = QLabel("0")
        self.table_layout.addRow(self.points_label, QHBoxLayout())
        
        self.wins_label = QLabel("Vittorie:")
        self.wins_rider1 = QLabel("0")
        self.wins_rider2 = QLabel("0")
        self.table_layout.addRow(self.wins_label, QHBoxLayout())
        
        self.podiums_label = QLabel("Podi:")
        self.podiums_rider1 = QLabel("0")
        self.podiums_rider2 = QLabel("0")
        self.table_layout.addRow(self.podiums_label, QHBoxLayout())
        
        self.avg_pos_label = QLabel("Posizione media:")
        self.avg_pos_rider1 = QLabel("0")
        self.avg_pos_rider2 = QLabel("0")
        self.table_layout.addRow(self.avg_pos_label, QHBoxLayout())
        
        self.best_lap_label = QLabel("Miglior giro:")
        self.best_lap_rider1 = QLabel("-")
        self.best_lap_rider2 = QLabel("-")
        self.table_layout.addRow(self.best_lap_label, QHBoxLayout())
        
        self.table_group.setLayout(self.table_layout)
        self.layout.addWidget(self.table_group)
        
        # Carica piloti nei combo
        self.load_riders_combo()
    
    def load_riders_combo(self):
        """Carica i piloti nei combobox"""
        try:
            db = SessionLocal()
            piloti = db.query(Pilota).all()
            
            self.rider1_combo.clear()
            self.rider2_combo.clear()
            
            for pilota in piloti:
                self.rider1_combo.addItem(f"{pilota.nome} {pilota.cognome}", pilota.id)
                self.rider2_combo.addItem(f"{pilota.nome} {pilota.cognome}", pilota.id)
            
            # Seleziona il secondo pilota per default
            if self.rider2_combo.count() > 1:
                self.rider2_combo.setCurrentIndex(1)
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante il caricamento piloti: {str(e)}")
        finally:
            db.close()
    
    def load_comparison(self):
        """Carica il confronto tra i piloti selezionati"""
        if self.rider1_combo.count() == 0 or self.rider2_combo.count() == 0:
            return
        
        pilota1_id = self.rider1_combo.currentData()
        pilota2_id = self.rider2_combo.currentData()
        
        if not pilota1_id or not pilota2_id or pilota1_id == pilota2_id:
            QMessageBox.warning(self, "Avviso", "Selezionare due piloti diversi!")
            return
        
        # Implementazione da completare - caricamento confronto dal DB
        # Per ora mostriamo dati di esempio
        
        # Dati di esempio
        self.points_rider1.setText("1510")
        self.points_rider2.setText("1470")
        
        self.wins_rider1.setText("2")
        self.wins_rider2.setText("3")
        
        self.podiums_rider1.setText("5")
        self.podiums_rider2.setText("4")
        
        self.avg_pos_rider1.setText("2.1")
        self.avg_pos_rider2.setText("2.4")
        
        self.best_lap_rider1.setText("1:42.567")
        self.best_lap_rider2.setText("1:43.123")
        
        # Qui implementeremo la generazione dei grafici di confronto

class EventStatsTab(QWidget):
    def __init__(self):
        super().__init__()
        
        # Layout principale
        self.layout = QVBoxLayout(self)
        
        # Selettori
        self.selectors_layout = QFormLayout()
        
        self.event_combo = QComboBox()
        self.selectors_layout.addRow("Evento:", self.event_combo)
        
        self.layout.addLayout(self.selectors_layout)
        
        # Bottone carica
        self.load_button = QPushButton("Carica Statistiche")
        self.load_button.clicked.connect(self.load_stats)
        self.layout.addWidget(self.load_button)
        
        # Pannello dati riassuntivi
        self.summary_group = QGroupBox("Dati Riassuntivi Evento")
        self.summary_layout = QFormLayout()
        
        self.total_riders_label = QLabel("0")
        self.summary_layout.addRow("Piloti totali:", self.total_riders_label)
        
        self.total_races_label = QLabel("0")
        self.summary_layout.addRow("Manche disputate:", self.total_races_label)
        
        self.best_lap_label = QLabel("-")
        self.summary_layout.addRow("Miglior giro assoluto:", self.best_lap_label)
        
        self.summary_group.setLayout(self.summary_layout)
        self.layout.addWidget(self.summary_group)
        
        # Grafici statistiche evento
        self.stats_group = QGroupBox("Grafici Statistiche Evento")
        self.stats_layout = QVBoxLayout()
        
        self.stats_label = QLabel("Grafici statistiche evento da implementare")
        self.stats_layout.addWidget(self.stats_label)
        
        self.stats_group.setLayout(self.stats_layout)
        self.layout.addWidget(self.stats_group)
        
        # Carica eventi nel combo
        self.load_events_combo()
    
    def load_events_combo(self):
        """Carica gli eventi nel combobox"""
        try:
            db = SessionLocal()
            eventi = db.query(Evento).all()
            
            self.event_combo.clear()
            for evento in eventi:
                self.event_combo.addItem(f"{evento.nome} ({evento.data})", evento.id)
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante il caricamento eventi: {str(e)}")
        finally:
            db.close()
    
    def load_stats(self):
        """Carica le statistiche dell'evento selezionato"""
        if self.event_combo.count() == 0:
            return
        
        evento_id = self.event_combo.currentData()
        if not evento_id:
            return
        
        # Implementazione da completare - caricamento statistiche dal DB
        # Per ora mostriamo dati di esempio
        
        # Dati di esempio
        self.total_riders_label.setText("120")
        self.total_races_label.setText("8")
        self.best_lap_label.setText("1:42.567 (Rossi Mario, MX1 Elite)")
        
        # Qui implementeremo la generazione dei grafici

class ChampionshipStatsTab(QWidget):
    def __init__(self):
        super().__init__()
        
        # Layout principale
        self.layout = QVBoxLayout(self)
        
        # Selettori
        self.selectors_layout = QFormLayout()
        
        self.championship_combo = QComboBox()
        self.championship_combo.addItems(["Campionato Regionale Lombardia 2025", "Trofeo Lombardia 2025"])
        self.selectors_layout.addRow("Campionato:", self.championship_combo)
        
        self.layout.addLayout(self.selectors_layout)
        
        # Bottone carica
        self.load_button = QPushButton("Carica Statistiche")
        self.load_button.clicked.connect(self.load_stats)
        self.layout.addWidget(self.load_button)
        
        # Pannello dati riassuntivi
        self.summary_group = QGroupBox("Dati Riassuntivi Campionato")
        self.summary_layout = QFormLayout()
        
        self.total_riders_label = QLabel("0")
        self.summary_layout.addRow("Piloti iscritti:", self.total_riders_label)
        
        self.total_events_label = QLabel("0")
        self.summary_layout.addRow("Eventi disputati:", self.total_events_label)
        
        self.total_races_label = QLabel("0")
        self.summary_layout.addRow("Manche totali:", self.total_races_label)
        
        self.summary_group.setLayout(self.summary_layout)
        self.layout.addWidget(self.summary_group)
        
        # Grafici statistiche campionato
        self.stats_group = QGroupBox("Grafici Statistiche Campionato")
        self.stats_layout = QVBoxLayout()
        
        self.stats_label = QLabel("Grafici statistiche campionato da implementare")
        self.stats_layout.addWidget(self.stats_label)
        
        self.stats_group.setLayout(self.stats_layout)
        self.layout.addWidget(self.stats_group)
    
    def load_stats(self):
        """Carica le statistiche del campionato selezionato"""
        # Implementazione da completare - caricamento statistiche dal DB
        # Per ora mostriamo dati di esempio
        
        # Dati di esempio
        self.total_riders_label.setText("180")
        self.total_events_label.setText("3 / 7")
        self.total_races_label.setText("24")
        
        # Qui implementeremo la generazione dei grafici