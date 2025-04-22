# ui/pilot_statistics.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLabel, QComboBox, QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QMessageBox, QTabWidget,
    QSplitter, QGridLayout, QFrame, QFileDialog, QScrollArea
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QFont, QColor

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import os
import csv
import random  # Per generare dati di esempio temporaneamente

from database.connection import SessionLocal
from database.models import Pilota, Iscrizione, Evento, Risultato, LapTime, Categoria, Gruppo, PartecipazioneGruppo

class PilotStatisticsWidget(QWidget):
    """Widget per visualizzare le statistiche complete di un pilota"""
    
    def __init__(self):
        super().__init__()
        
        # Layout principale con scroll
        main_layout = QVBoxLayout(self)
        
        # Area di scorrimento per contenere tutto
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)
        
        # Widget contenitore per l'area di scorrimento
        scroll_content = QWidget()
        self.layout = QVBoxLayout(scroll_content)
        
        # Selettore pilota
        select_layout = QHBoxLayout()
        
        self.pilot_selector_label = QLabel("Seleziona Pilota:")
        self.pilot_selector_label.setStyleSheet("font-weight: bold;")
        select_layout.addWidget(self.pilot_selector_label)
        
        self.pilot_combo = QComboBox()
        self.pilot_combo.setMinimumWidth(300)
        select_layout.addWidget(self.pilot_combo)
        
        self.year_combo = QComboBox()
        self.year_combo.addItems(["2025", "2024", "2023"])
        select_layout.addWidget(QLabel("Anno:"))
        select_layout.addWidget(self.year_combo)
        
        self.load_button = QPushButton("Carica Statistiche")
        self.load_button.clicked.connect(self.load_statistics)
        select_layout.addWidget(self.load_button)
        
        self.export_button = QPushButton("Esporta Report")
        self.export_button.clicked.connect(self.export_report)
        select_layout.addWidget(self.export_button)
        
        self.share_button = QPushButton("Condividi")
        self.share_button.setToolTip("Condividi via email o WhatsApp")
        self.share_button.clicked.connect(self.share_statistics)
        select_layout.addWidget(self.share_button)
        
        select_layout.addStretch()
        
        self.layout.addLayout(select_layout)
        
        # Intestazione pilota (apparirà dopo aver caricato i dati)
        self.pilot_header = QHBoxLayout()
        
        # Sinistra: immagine pilota
        self.pilot_image_container = QLabel()
        self.pilot_image_container.setFixedSize(150, 150)
        self.pilot_image_container.setStyleSheet("border: 1px solid #ccc; border-radius: 5px;")
        self.pilot_header.addWidget(self.pilot_image_container)
        
        # Destra: info pilota
        self.pilot_info = QVBoxLayout()
        
        self.pilot_name_label = QLabel("")
        self.pilot_name_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.pilot_info.addWidget(self.pilot_name_label)
        
        self.pilot_details = QFormLayout()
        self.category_label = QLabel("")
        self.license_label = QLabel("")
        self.moto_label = QLabel("")
        self.numero_label = QLabel("")
        self.motoclub_label = QLabel("")
        
        self.pilot_details.addRow("Categoria:", self.category_label)
        self.pilot_details.addRow("Licenza:", self.license_label)
        self.pilot_details.addRow("Moto:", self.moto_label)
        self.pilot_details.addRow("Numero:", self.numero_label)
        self.pilot_details.addRow("Moto Club:", self.motoclub_label)
        
        self.pilot_info.addLayout(self.pilot_details)
        self.pilot_header.addLayout(self.pilot_info)
        
        # Statistiche riassuntive
        self.summary_stats = QHBoxLayout()
        
        # Gare disputate
        self.races_stat = self._create_stat_box("Gare Disputate", "0")
        self.summary_stats.addWidget(self.races_stat)
        
        # Podi
        self.podiums_stat = self._create_stat_box("Podi", "0")
        self.summary_stats.addWidget(self.podiums_stat)
        
        # Vittorie
        self.wins_stat = self._create_stat_box("Vittorie", "0")
        self.summary_stats.addWidget(self.wins_stat)
        
        # Punti totali
        self.points_stat = self._create_stat_box("Punti Totali", "0")
        self.summary_stats.addWidget(self.points_stat)
        
        # Posizione classifica
        self.position_stat = self._create_stat_box("Pos. Classifica", "-")
        self.summary_stats.addWidget(self.position_stat)
        
        # Miglior risultato
        self.best_result_stat = self._create_stat_box("Miglior Risultato", "-")
        self.summary_stats.addWidget(self.best_result_stat)
        
        # Nascondi header pilota e statistiche fino a quando non vengono caricati i dati
        self.pilot_header_widget = QWidget()
        self.pilot_header_widget.setLayout(self.pilot_header)
        self.pilot_header_widget.setVisible(False)
        self.layout.addWidget(self.pilot_header_widget)
        
        self.stats_widget = QWidget()
        self.stats_widget.setLayout(self.summary_stats)
        self.stats_widget.setVisible(False)
        self.layout.addWidget(self.stats_widget)
        
        # Dashboard principale con tabs
        self.tabs = QTabWidget()
        
        # Tab 1: Riepilogo
        self.summary_tab = QWidget()
        self.setup_summary_tab()
        self.tabs.addTab(self.summary_tab, "Riepilogo")
        
        # Tab 2: Dettagli Gare
        self.races_tab = QWidget()
        self.setup_races_tab()
        self.tabs.addTab(self.races_tab, "Dettagli Gare")
        
        # Tab 3: Analisi Tempi
        self.times_tab = QWidget()
        self.setup_times_tab()
        self.tabs.addTab(self.times_tab, "Analisi Tempi")
        
        # Tab 4: Confronto con Altri Piloti
        self.comparison_tab = QWidget()
        self.setup_comparison_tab()
        self.tabs.addTab(self.comparison_tab, "Confronto")
        
        # Tab 5: Previsioni e Tendenze
        self.predictions_tab = QWidget()
        self.setup_predictions_tab()
        self.tabs.addTab(self.predictions_tab, "Previsioni")
        
        self.layout.addWidget(self.tabs)
        
        # Completa il setup dello scroll
        scroll_area.setWidget(scroll_content)
        
        # Carica i piloti nel combobox
        self.load_pilots()
        
        # Nascondi i tab fino al caricamento dei dati
        self.tabs.setVisible(False)
    
    def _create_stat_box(self, title, value):
        """Crea un box per le statistiche con titolo e valore"""
        box = QFrame()
        box.setFrameShape(QFrame.Shape.StyledPanel)
        box.setStyleSheet("background-color: #f5f5f5; border-radius: 5px; padding: 10px;")
        
        layout = QVBoxLayout(box)
        
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-weight: bold; color: #555;")
        
        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        # Salva il riferimento al valore per aggiornarlo facilmente
        box.value_label = value_label
        
        return box
    
    def setup_summary_tab(self):
        """Configura la tab di riepilogo"""
        layout = QVBoxLayout(self.summary_tab)
        
        # Dividi in due colonne
        split_layout = QHBoxLayout()
        
        # Colonna sinistra: grafici
        left_column = QVBoxLayout()
        
        # Grafico 1: Andamento posizione nelle gare
        position_chart_container = QWidget()
        position_chart_layout = QVBoxLayout(position_chart_container)
        position_chart_layout.addWidget(QLabel("<b>Andamento posizioni nelle gare</b>"))
        
        self.position_chart = FigureCanvas(Figure(figsize=(5, 4)))
        position_chart_layout.addWidget(self.position_chart)
        
        left_column.addWidget(position_chart_container)
        
        # Grafico 2: Punti per gara
        points_chart_container = QWidget()
        points_chart_layout = QVBoxLayout(points_chart_container)
        points_chart_layout.addWidget(QLabel("<b>Punti per gara</b>"))
        
        self.points_chart = FigureCanvas(Figure(figsize=(5, 4)))
        points_chart_layout.addWidget(self.points_chart)
        
        left_column.addWidget(points_chart_container)
        
        split_layout.addLayout(left_column)
        
        # Colonna destra: Radar chart e info aggiuntive
        right_column = QVBoxLayout()
        
        # Grafico radar per vari aspetti delle prestazioni
        radar_container = QWidget()
        radar_layout = QVBoxLayout(radar_container)
        radar_layout.addWidget(QLabel("<b>Prestazioni (radar)</b>"))
        
        self.radar_chart = FigureCanvas(Figure(figsize=(5, 5)))
        radar_layout.addWidget(self.radar_chart)
        
        right_column.addWidget(radar_container)
        
        # Performance summary
        performance_container = QFrame()
        performance_container.setFrameShape(QFrame.Shape.StyledPanel)
        performance_container.setStyleSheet("background-color: #f5f5f5; border-radius: 5px; padding: 10px;")
        
        perf_layout = QVBoxLayout(performance_container)
        perf_layout.addWidget(QLabel("<b>Analisi delle prestazioni</b>"))
        
        self.performance_text = QLabel("Carica i dati di un pilota per visualizzare l'analisi")
        self.performance_text.setWordWrap(True)
        perf_layout.addWidget(self.performance_text)
        
        right_column.addWidget(performance_container)
        
        # Aggiungi entrambe le colonne al layout
        split_layout.addLayout(right_column)
        
        layout.addLayout(split_layout)
    
    def setup_races_tab(self):
        """Configura la tab dei dettagli delle gare"""
        layout = QVBoxLayout(self.races_tab)
        
        # Tabella con i risultati di ogni gara
        self.races_table = QTableWidget(0, 9)
        self.races_table.setHorizontalHeaderLabels([
            "Evento", "Data", "Circuito", "Posizione", "Giri", "Tempo Totale", 
            "Distacco", "Miglior Tempo", "Punti"
        ])
        self.races_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.races_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        layout.addWidget(QLabel("<b>Dettagli di tutte le gare</b>"))
        layout.addWidget(self.races_table)
        
        # Dettagli della gara selezionata
        details_group = QFrame()
        details_group.setFrameShape(QFrame.Shape.StyledPanel)
        details_group.setStyleSheet("background-color: #f5f5f5; border-radius: 5px; padding: 10px;")
        
        details_layout = QVBoxLayout(details_group)
        details_layout.addWidget(QLabel("<b>Dettagli gara selezionata</b>"))
        
        # Splitter per organizzare i dettagli
        details_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Colonna sinistra: info gara
        race_info = QWidget()
        race_info_layout = QFormLayout(race_info)
        
        self.race_detail_event = QLabel("-")
        self.race_detail_date = QLabel("-")
        self.race_detail_circuit = QLabel("-")
        self.race_detail_weather = QLabel("-")
        self.race_detail_category = QLabel("-")
        self.race_detail_group = QLabel("-")
        
        race_info_layout.addRow("Evento:", self.race_detail_event)
        race_info_layout.addRow("Data:", self.race_detail_date)
        race_info_layout.addRow("Circuito:", self.race_detail_circuit)
        race_info_layout.addRow("Condizioni:", self.race_detail_weather)
        race_info_layout.addRow("Categoria:", self.race_detail_category)
        race_info_layout.addRow("Gruppo:", self.race_detail_group)
        
        details_splitter.addWidget(race_info)
        
        # Colonna destra: performance
        race_performance = QWidget()
        race_perf_layout = QFormLayout(race_performance)
        
        self.race_detail_position = QLabel("-")
        self.race_detail_laps = QLabel("-")
        self.race_detail_total_time = QLabel("-")
        self.race_detail_best_lap = QLabel("-")
        self.race_detail_avg_lap = QLabel("-")
        self.race_detail_points = QLabel("-")
        
        race_perf_layout.addRow("Posizione:", self.race_detail_position)
        race_perf_layout.addRow("Giri completati:", self.race_detail_laps)
        race_perf_layout.addRow("Tempo totale:", self.race_detail_total_time)
        race_perf_layout.addRow("Miglior giro:", self.race_detail_best_lap)
        race_perf_layout.addRow("Media giri:", self.race_detail_avg_lap)
        race_perf_layout.addRow("Punti:", self.race_detail_points)
        
        details_splitter.addWidget(race_performance)
        
        details_layout.addWidget(details_splitter)
        
        layout.addWidget(details_group)
        
        # Collega la selezione di una riga nella tabella all'aggiornamento dei dettagli
        self.races_table.itemSelectionChanged.connect(self.update_race_details)
    
    def setup_times_tab(self):
        """Configura la tab di analisi dei tempi"""
        layout = QVBoxLayout(self.times_tab)
        
        # Splitter per dividere la tab
        times_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Sezione superiore: Grafico evoluzione dei tempi
        upper_widget = QWidget()
        upper_layout = QVBoxLayout(upper_widget)
        
        upper_layout.addWidget(QLabel("<b>Evoluzione dei tempi sul giro durante la stagione</b>"))
        
        self.lap_evolution_chart = FigureCanvas(Figure(figsize=(8, 4)))
        upper_layout.addWidget(self.lap_evolution_chart)
        
        times_splitter.addWidget(upper_widget)
        
        # Sezione inferiore: due colonne con grafici e tabella
        lower_widget = QWidget()
        lower_layout = QHBoxLayout(lower_widget)
        
        # Colonna sinistra: Grafico comparativo con categoria
        left_column = QVBoxLayout()
        
        left_column.addWidget(QLabel("<b>Confronto con la media della categoria</b>"))
        
        self.category_comparison_chart = FigureCanvas(Figure(figsize=(5, 4)))
        left_column.addWidget(self.category_comparison_chart)
        
        # Box statistiche
        times_stats = QFrame()
        times_stats.setFrameShape(QFrame.Shape.StyledPanel)
        times_stats.setStyleSheet("background-color: #f5f5f5; border-radius: 5px; padding: 10px;")
        
        times_stats_layout = QFormLayout(times_stats)
        
        self.best_lap_overall = QLabel("-")
        self.best_lap_overall.setStyleSheet("font-weight: bold; color: #0066cc;")
        
        self.avg_lap_overall = QLabel("-")
        self.category_avg_lap = QLabel("-")
        self.best_circuit = QLabel("-")
        self.worst_circuit = QLabel("-")
        self.improvement_rate = QLabel("-")
        
        times_stats_layout.addRow("Miglior giro assoluto:", self.best_lap_overall)
        times_stats_layout.addRow("Media giri stagionale:", self.avg_lap_overall)
        times_stats_layout.addRow("Media categoria:", self.category_avg_lap)
        times_stats_layout.addRow("Circuito migliore:", self.best_circuit)
        times_stats_layout.addRow("Circuito peggiore:", self.worst_circuit)
        times_stats_layout.addRow("Tasso miglioramento:", self.improvement_rate)
        
        left_column.addWidget(times_stats)
        
        lower_layout.addLayout(left_column)
        
        # Colonna destra: Tabella dettaglio tempi per gara
        right_column = QVBoxLayout()
        
        right_column.addWidget(QLabel("<b>Tempi dettagliati per gara</b>"))
        
        self.lap_times_table = QTableWidget(0, 5)
        self.lap_times_table.setHorizontalHeaderLabels([
            "Evento", "Circuito", "Miglior Tempo", "Media", "Differenza dalla Media"
        ])
        self.lap_times_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        right_column.addWidget(self.lap_times_table)
        
        lower_layout.addLayout(right_column)
        
        times_splitter.addWidget(lower_widget)
        
        # Imposta rapporto dimensioni nel splitter (40% sopra, 60% sotto)
        times_splitter.setSizes([400, 600])
        
        layout.addWidget(times_splitter)
    
    def setup_comparison_tab(self):
        """Configura la tab di confronto con altri piloti"""
        layout = QVBoxLayout(self.comparison_tab)
        
        # Selezione secondo pilota
        compare_layout = QHBoxLayout()
        
        compare_layout.addWidget(QLabel("<b>Confronta con:</b>"))
        
        self.compare_pilot_combo = QComboBox()
        self.compare_pilot_combo.setMinimumWidth(300)
        compare_layout.addWidget(self.compare_pilot_combo)
        
        self.compare_button = QPushButton("Confronta")
        self.compare_button.clicked.connect(self.compare_pilots)
        compare_layout.addWidget(self.compare_button)
        
        compare_layout.addStretch()
        
        layout.addLayout(compare_layout)
        
        # Grid layout per i grafici di confronto (2x2)
        comparison_grid = QGridLayout()
        
        # Grafico 1: Confronto posizioni
        positions_container = QWidget()
        positions_layout = QVBoxLayout(positions_container)
        positions_layout.addWidget(QLabel("<b>Confronto Posizioni</b>"))
        
        self.positions_comparison_chart = FigureCanvas(Figure(figsize=(5, 4)))
        positions_layout.addWidget(self.positions_comparison_chart)
        
        comparison_grid.addWidget(positions_container, 0, 0)
        
        # Grafico 2: Confronto punti
        points_container = QWidget()
        points_layout = QVBoxLayout(points_container)
        points_layout.addWidget(QLabel("<b>Confronto Punti</b>"))
        
        self.points_comparison_chart = FigureCanvas(Figure(figsize=(5, 4)))
        points_layout.addWidget(self.points_comparison_chart)
        
        comparison_grid.addWidget(points_container, 0, 1)
        
        # Grafico 3: Confronto tempi sul giro
        times_container = QWidget()
        times_layout = QVBoxLayout(times_container)
        times_layout.addWidget(QLabel("<b>Confronto Tempi</b>"))
        
        self.times_comparison_chart = FigureCanvas(Figure(figsize=(5, 4)))
        times_layout.addWidget(self.times_comparison_chart)
        
        comparison_grid.addWidget(times_container, 1, 0)
        
        # Grafico 4: Radar caratteristiche
        radar_container = QWidget()
        radar_layout = QVBoxLayout(radar_container)
        radar_layout.addWidget(QLabel("<b>Confronto Caratteristiche</b>"))
        
        self.radar_comparison_chart = FigureCanvas(Figure(figsize=(5, 4)))
        radar_layout.addWidget(self.radar_comparison_chart)
        
        comparison_grid.addWidget(radar_container, 1, 1)
        
        layout.addLayout(comparison_grid)
        
        # Tabella confronto testa a testa
        self.head_to_head_table = QTableWidget(0, 7)
        self.head_to_head_table.setHorizontalHeaderLabels([
            "Evento", "Data", "Circuito", "Posizione P1", "Posizione P2", "Miglior Tempo P1", "Miglior Tempo P2"
        ])
        self.head_to_head_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(QLabel("<b>Confronto diretto nelle stesse gare</b>"))
        layout.addWidget(self.head_to_head_table)
    
    def setup_predictions_tab(self):
        """Configura la tab di previsioni e tendenze"""
        layout = QVBoxLayout(self.predictions_tab)
        
        # Splitter principale
        pred_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Sezione superiore: previsioni campionato
        upper_widget = QWidget()
        upper_layout = QHBoxLayout(upper_widget)
        
        # Grafico previsione
        prediction_container = QWidget()
        prediction_layout = QVBoxLayout(prediction_container)
        prediction_layout.addWidget(QLabel("<b>Previsione posizione finale</b>"))
        
        self.prediction_chart = FigureCanvas(Figure(figsize=(5, 4)))
        prediction_layout.addWidget(self.prediction_chart)
        
        upper_layout.addWidget(prediction_container)
        
        # Box previsioni
        predictions_box = QFrame()
        predictions_box.setFrameShape(QFrame.Shape.StyledPanel)
        predictions_box.setStyleSheet("background-color: #f5f5f5; border-radius: 5px; padding: 10px;")
        
        pred_box_layout = QVBoxLayout(predictions_box)
        pred_box_layout.addWidget(QLabel("<b>Previsioni Campionato</b>"))
        
        pred_details = QFormLayout()
        
        self.predicted_position = QLabel("-")
        self.predicted_position.setStyleSheet("font-weight: bold; font-size: 16px;")
        
        self.predicted_points = QLabel("-")
        self.points_to_next = QLabel("-")
        self.championship_chances = QLabel("-")
        
        pred_details.addRow("Posizione finale prevista:", self.predicted_position)
        pred_details.addRow("Punti previsti:", self.predicted_points)
        pred_details.addRow("Punti al pilota superiore:", self.points_to_next)
        pred_details.addRow("Possibilità podio campionato:", self.championship_chances)
        
        pred_box_layout.addLayout(pred_details)
        
        # Suggerimenti miglioramento
        pred_box_layout.addWidget(QLabel("<b>Suggerimenti per miglioramento</b>"))
        
        self.improvement_tips = QLabel("Carica i dati del pilota per visualizzare i suggerimenti")
        self.improvement_tips.setWordWrap(True)
        self.improvement_tips.setMinimumHeight(100)
        pred_box_layout.addWidget(self.improvement_tips)
        
        upper_layout.addWidget(predictions_box)
        
        pred_splitter.addWidget(upper_widget)
        
        # Sezione inferiore: prestazioni per circuito
        lower_widget = QWidget()
        lower_layout = QVBoxLayout(lower_widget)
        
        lower_layout.addWidget(QLabel("<b>Prestazioni per circuito</b>"))
        
        # Tabella circuiti
        self.circuits_table = QTableWidget(0, 6)
        self.circuits_table.setHorizontalHeaderLabels([
            "Circuito", "Miglior Posizione", "Peggiore Posizione", "Media", "Miglior Tempo", "Indice Prestazione"
        ])
        self.circuits_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        lower_layout.addWidget(self.circuits_table)
        
        # Grafico prestazioni circuiti
        circuits_chart_container = QWidget()
        circuits_chart_layout = QVBoxLayout(circuits_chart_container)
        
        self.circuits_chart = FigureCanvas(Figure(figsize=(8, 4)))
        circuits_chart_layout.addWidget(self.circuits_chart)
        
        lower_layout.addWidget(circuits_chart_container)
        
        pred_splitter.addWidget(lower_widget)
        
        layout.addWidget(pred_splitter)
    
    def load_pilots(self):
        """Carica l'elenco dei piloti nel combobox"""
        try:
            db = SessionLocal()
            
            # Ottieni tutti i piloti ordinati per cognome, nome
            pilots = db.query(Pilota).order_by(Pilota.cognome, Pilota.nome).all()
            
            self.pilot_combo.clear()
            self.compare_pilot_combo.clear()
            
            for pilot in pilots:
                display_text = f"{pilot.cognome} {pilot.nome}"
                self.pilot_combo.addItem(display_text, pilot.id)
                self.compare_pilot_combo.addItem(display_text, pilot.id)
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante il caricamento piloti: {str(e)}")
        finally:
            db.close()
    
    def load_statistics(self):
        """Carica e visualizza le statistiche del pilota selezionato"""
        pilot_id = self.pilot_combo.currentData()
        
        if not pilot_id:
            QMessageBox.warning(self, "Attenzione", "Seleziona un pilota!")
            return
        
        try:
            # Ottieni dati dal database
            db = SessionLocal()
            
            # Ottieni dati pilota
            pilot = db.query(Pilota).get(pilot_id)
            
            if not pilot:
                QMessageBox.warning(self, "Attenzione", "Pilota non trovato!")
                return
            
            # Mostra i widgets nascosti
            self.pilot_header_widget.setVisible(True)
            self.stats_widget.setVisible(True)
            self.tabs.setVisible(True)
            
            # Aggiorna l'intestazione pilota
            self.pilot_name_label.setText(f"{pilot.nome} {pilot.cognome}")
            
            # Carica immagine pilota (placeholder per ora)
            placeholder_pixmap = QPixmap(150, 150)
            placeholder_pixmap.fill(QColor("#DDDDDD"))
            self.pilot_image_container.setPixmap(placeholder_pixmap)
            
            # Aggiorna dati pilota
            category = "Non disponibile"
            if hasattr(pilot, 'categoria_ranking') and pilot.categoria_ranking:
                category = pilot.categoria_ranking
            self.category_label.setText(category)
            
            self.license_label.setText(pilot.licenza_tipo if pilot.licenza_tipo else "Non disponibile")
            self.moto_label.setText(pilot.marca_moto if hasattr(pilot, 'marca_moto') and pilot.marca_moto else "Non disponibile")
            self.numero_label.setText(pilot.numero_gara if hasattr(pilot, 'numero_gara') and pilot.numero_gara else "Non assegnato")
            self.motoclub_label.setText(pilot.moto_club if pilot.moto_club else "Non disponibile")
            
            # Ottieni statistiche del pilota
            # Per ora usiamo dati di esempio, ma in futuro saranno presi dal database
            
            # 1. Trova tutte le iscrizioni del pilota
            iscrizioni = db.query(Iscrizione).filter(Iscrizione.pilota_id == pilot_id).all()
            iscrizioni_ids = [iscrizione.id for iscrizione in iscrizioni]
            
            # 2. Trova tutti i risultati per queste iscrizioni
            # Utilizziamo dati di esempio per ora
            total_races = len(iscrizioni)
            podiums = random.randint(0, total_races)
            wins = random.randint(0, podiums)
            total_points = random.randint(wins * 200, total_races * 250)
            championship_position = random.randint(1, 20)
            best_result = "1°" if wins > 0 else f"{random.randint(2, 10)}°"
            
            # Aggiorna i box delle statistiche
            self.races_stat.value_label.setText(str(total_races))
            self.podiums_stat.value_label.setText(str(podiums))
            self.wins_stat.value_label.setText(str(wins))
            self.points_stat.value_label.setText(str(total_points))
            self.position_stat.value_label.setText(str(championship_position))
            self.best_result_stat.value_label.setText(best_result)
            
            # Aggiorna i grafici e le tabelle
            self.update_summary_graphs(pilot_id)
            self.update_races_table(pilot_id)
            self.update_times_analysis(pilot_id)
            self.update_prediction_data(pilot_id)
            
            QMessageBox.information(self, "Statistiche Caricate", f"Statistiche di {pilot.nome} {pilot.cognome} caricate con successo!")
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante il caricamento delle statistiche: {str(e)}")
        finally:
            db.close()
    
    def update_summary_graphs(self, pilot_id):
        """Aggiorna i grafici nella tab di riepilogo"""
        # Generiamo dati di esempio per i grafici
        
        # 1. Grafico andamento posizioni
        ax1 = self.position_chart.figure.subplots()
        races = ["Gara 1", "Gara 2", "Gara 3", "Gara 4", "Gara 5", "Gara 6", "Gara 7"]
        positions = [random.randint(1, 15) for _ in range(len(races))]
        
        # Invertiamo l'asse y per mostrare posizioni migliori in alto
        ax1.plot(races, positions, marker='o', linestyle='-', color='blue')
        ax1.set_ylim([max(positions) + 3, 0.5])  # Margine sopra e sotto
        ax1.set_ylabel('Posizione')
        ax1.set_xlabel('Gare')
        ax1.set_title('Andamento Posizioni')
        ax1.grid(True, linestyle='--', alpha=0.7)
        
        for i, pos in enumerate(positions):
            ax1.annotate(str(pos), (i, pos), textcoords="offset points", 
                         xytext=(0, 10), ha='center')
        
        self.position_chart.figure.tight_layout()
        self.position_chart.draw()
        
        # 2. Grafico punti per gara
        ax2 = self.points_chart.figure.subplots()
        points = [random.randint(0, 250) for _ in range(len(races))]
        
        bars = ax2.bar(races, points, color='green', alpha=0.7)
        ax2.set_xlabel('Gare')
        ax2.set_ylabel('Punti')
        ax2.set_title('Punti per Gara')
        
        # Aggiunge etichette sopra le barre
        for bar in bars:
            height = bar.get_height()
            ax2.annotate(f'{height}', xy=(bar.get_x() + bar.get_width() / 2, height),
                         xytext=(0, 3), textcoords="offset points", ha='center')
        
        self.points_chart.figure.tight_layout()
        self.points_chart.draw()
        
        # 3. Grafico radar delle prestazioni
        ax3 = self.radar_chart.figure.subplots(subplot_kw={'polar': True})
        
        # Categorie del radar
        categories = ['Velocità', 'Costanza', 'Partenze', 'Sorpassi', 'Tecnica', 'Resistenza']
        N = len(categories)
        
        # Valore per ciascuna categoria (0-10)
        values = [random.randint(5, 10) for _ in range(N)]
        
        # Angoli per ogni asse
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]  # Chiude il poligono
        
        # Valori per ogni asse
        values += values[:1]  # Chiude il poligono
        
        # Disegna il poligono
        ax3.plot(angles, values, linewidth=1, linestyle='solid')
        ax3.fill(angles, values, 'b', alpha=0.1)
        
        # Fissa il raggio massimo
        ax3.set_ylim(0, 10)
        
        # Imposta le etichette degli assi
        ax3.set_xticks(angles[:-1])
        ax3.set_xticklabels(categories)
        
        self.radar_chart.figure.tight_layout()
        self.radar_chart.draw()
        
        # 4. Aggiorna testo analisi
        performance_text = f"""
        Il pilota ha mostrato una buona costanza durante la stagione, con un miglioramento nelle ultime gare.
        I suoi punti di forza sono principalmente nelle partenze e nella gestione della gara.
        Può migliorare nella tecnica di guida su terreni bagnati e nella gestione delle condizioni difficili.
        
        Confrontando con la media della categoria, il pilota è sopra la media nelle partenze e nella resistenza,
        mentre risulta nella media per quanto riguarda la velocità pura.
        """
        
        self.performance_text.setText(performance_text.strip())
    
    def update_races_table(self, pilot_id):
        """Aggiorna la tabella delle gare"""
        # Simuliamo dati di esempio per le gare
        self.races_table.setRowCount(0)
        
        # Generiamo alcuni eventi di esempio
        eventi = [
            {"nome": "MX Lombardia Round 1", "data": "15/03/2025", "circuito": "Ottobiano", "meteo": "Soleggiato"},
            {"nome": "MX Lombardia Round 2", "data": "12/04/2025", "circuito": "Cremona", "meteo": "Nuvoloso"},
            {"nome": "MX Lombardia Round 3", "data": "03/05/2025", "circuito": "Castiglione", "meteo": "Pioggia leggera"},
            {"nome": "MX Lombardia Round 4", "data": "14/06/2025", "circuito": "Maggiora", "meteo": "Soleggiato"},
            {"nome": "MX Lombardia Round 5", "data": "05/07/2025", "circuito": "Ponte a Egola", "meteo": "Caldo"},
            {"nome": "MX Lombardia Round 6", "data": "06/09/2025", "circuito": "Mantova", "meteo": "Nuvoloso"},
            {"nome": "MX Lombardia Round 7", "data": "04/10/2025", "circuito": "Ottobiano", "meteo": "Fresco"},
        ]
        
        # Riempi la tabella
        for evento in eventi:
            row = self.races_table.rowCount()
            self.races_table.insertRow(row)
            
            position = random.randint(1, 20)
            laps = random.randint(10, 15)
            
            # Tempo totale (formato mm:ss.ms)
            mins = random.randint(25, 35)
            secs = random.randint(0, 59)
            ms = random.randint(0, 999)
            total_time = f"{mins:02d}:{secs:02d}.{ms:03d}"
            
            # Distacco dal primo (se non è primo)
            if position == 1:
                gap = "-"
            else:
                gap_secs = random.randint(1, 120)
                gap_ms = random.randint(0, 999)
                gap = f"+{gap_secs}.{gap_ms:03d}s"
            
            # Miglior tempo sul giro
            min_lap = random.randint(1, 2)
            sec_lap = random.randint(30, 59)
            ms_lap = random.randint(0, 999)
            best_lap = f"{min_lap:02d}:{sec_lap:02d}.{ms_lap:03d}"
            
            # Punti ottenuti (in base alla posizione)
            points_table = {
                1: 250, 2: 210, 3: 170, 4: 140, 5: 120, 6: 110, 7: 100, 8: 90, 9: 85, 10: 80,
                11: 77, 12: 74, 13: 72, 14: 70, 15: 68, 16: 66, 17: 64, 18: 63, 19: 62, 20: 61
            }
            points = points_table.get(position, 0)
            
            # Inserisci i dati nella tabella
            self.races_table.setItem(row, 0, QTableWidgetItem(evento["nome"]))
            self.races_table.setItem(row, 1, QTableWidgetItem(evento["data"]))
            self.races_table.setItem(row, 2, QTableWidgetItem(evento["circuito"]))
            self.races_table.setItem(row, 3, QTableWidgetItem(str(position)))
            self.races_table.setItem(row, 4, QTableWidgetItem(str(laps)))
            self.races_table.setItem(row, 5, QTableWidgetItem(total_time))
            self.races_table.setItem(row, 6, QTableWidgetItem(gap))
            self.races_table.setItem(row, 7, QTableWidgetItem(best_lap))
            self.races_table.setItem(row, 8, QTableWidgetItem(str(points)))
            
            # Colora le righe dei podi
            if position <= 3:
                color = QColor("#D4F0D0") if position == 1 else QColor("#E2F0D0")
                for col in range(self.races_table.columnCount()):
                    item = self.races_table.item(row, col)
                    if item:
                        item.setBackground(color)
        
        # Selezioniamo la prima riga per mostrare i dettagli
        if self.races_table.rowCount() > 0:
            self.races_table.selectRow(0)
            self.update_race_details()
    
    def update_race_details(self):
        """Aggiorna i dettagli della gara selezionata"""
        selected_rows = self.races_table.selectedItems()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        
        # Otteniamo i dati dalla tabella
        event = self.races_table.item(row, 0).text()
        date = self.races_table.item(row, 1).text()
        circuit = self.races_table.item(row, 2).text()
        position = self.races_table.item(row, 3).text()
        laps = self.races_table.item(row, 4).text()
        total_time = self.races_table.item(row, 5).text()
        best_lap = self.races_table.item(row, 7).text()
        points = self.races_table.item(row, 8).text()
        
        # Dati simulati aggiuntivi
        weather = ["Soleggiato", "Nuvoloso", "Pioggia leggera", "Pioggia", "Caldo", "Fresco"][random.randint(0, 5)]
        category = ["MX1 Elite", "MX2 Fast", "MX1 Expert", "MX2 Rider", "125 Senior"][random.randint(0, 4)]
        group = ["Gruppo A", "Gruppo B", "Gruppo C"][random.randint(0, 2)]
        
        # Calcoliamo un tempo medio sul giro
        min_lap, rest = best_lap.split(":")
        sec_lap, ms_lap = rest.split(".")
        
        # Aggiungiamo un po' di casualità per il tempo medio
        avg_secs = int(sec_lap) + random.randint(1, 8)
        avg_mins = int(min_lap)
        if avg_secs >= 60:
            avg_mins += 1
            avg_secs -= 60
        
        avg_ms = int(ms_lap) + random.randint(-300, 300)
        if avg_ms < 0:
            avg_ms += 1000
            avg_secs -= 1
        if avg_ms >= 1000:
            avg_ms -= 1000
            avg_secs += 1
        
        avg_lap = f"{avg_mins:02d}:{avg_secs:02d}.{avg_ms:03d}"
        
        # Aggiorniamo i campi
        self.race_detail_event.setText(event)
        self.race_detail_date.setText(date)
        self.race_detail_circuit.setText(circuit)
        self.race_detail_weather.setText(weather)
        self.race_detail_category.setText(category)
        self.race_detail_group.setText(group)
        
        self.race_detail_position.setText(position)
        self.race_detail_laps.setText(laps)
        self.race_detail_total_time.setText(total_time)
        self.race_detail_best_lap.setText(best_lap)
        self.race_detail_avg_lap.setText(avg_lap)
        self.race_detail_points.setText(points)
    
    def update_times_analysis(self, pilot_id):
        """Aggiorna l'analisi dei tempi sul giro"""
        # 1. Evoluzione dei tempi sul giro durante la stagione
        ax1 = self.lap_evolution_chart.figure.subplots()
        
        # Dati di esempio
        races = ["Gara 1", "Gara 2", "Gara 3", "Gara 4", "Gara 5", "Gara 6", "Gara 7"]
        
        # Convertiamo i tempi in secondi
        best_times_sec = [random.uniform(90, 110) for _ in range(len(races))]
        avg_times_sec = [t + random.uniform(2, 8) for t in best_times_sec]
        
        # Plottiamo le linee
        ax1.plot(races, best_times_sec, marker='o', linestyle='-', color='blue', label='Miglior Tempo')
        ax1.plot(races, avg_times_sec, marker='s', linestyle='--', color='green', label='Tempo Medio')
        
        # Aggiungiamo una linea di tendenza (semplice media mobile)
        trend = [sum(best_times_sec[:i+1])/(i+1) for i in range(len(best_times_sec))]
        ax1.plot(races, trend, linestyle='-.', color='red', alpha=0.5, label='Tendenza')
        
        ax1.set_ylabel('Tempo (secondi)')
        ax1.set_xlabel('Gare')
        ax1.set_title('Evoluzione dei Tempi sul Giro')
        ax1.legend()
        ax1.grid(True, linestyle='--', alpha=0.7)
        
        self.lap_evolution_chart.figure.tight_layout()
        self.lap_evolution_chart.draw()
        
        # 2. Confronto con la media della categoria
        ax2 = self.category_comparison_chart.figure.subplots()
        
        circuits = ["Ottobiano", "Cremona", "Castiglione", "Maggiora", "Ponte a Egola"]
        
        # Tempi pilota vs media categoria (in secondi)
        pilot_times = [random.uniform(90, 110) for _ in range(len(circuits))]
        category_avg = [t + random.uniform(-5, 5) for t in pilot_times]
        
        x = np.arange(len(circuits))
        width = 0.35
        
        ax2.bar(x - width/2, pilot_times, width, label='Pilota', color='blue', alpha=0.7)
        ax2.bar(x + width/2, category_avg, width, label='Media Categoria', color='orange', alpha=0.7)
        
        ax2.set_ylabel('Tempo (secondi)')
        ax2.set_title('Confronto Tempi con Media Categoria')
        ax2.set_xticks(x)
        ax2.set_xticklabels(circuits, rotation=45, ha="right")
        ax2.legend()
        
        self.category_comparison_chart.figure.tight_layout()
        self.category_comparison_chart.draw()
        
        # 3. Aggiorna statistiche tempi
        # Troviamo il miglior tempo assoluto
        best_time_idx = best_times_sec.index(min(best_times_sec))
        best_time_val = min(best_times_sec)
        best_time_circuit = circuits[best_time_idx % len(circuits)]
        
        mins = int(best_time_val // 60)
        secs = int(best_time_val % 60)
        ms = int((best_time_val % 1) * 1000)
        
        best_time_formatted = f"{mins:02d}:{secs:02d}.{ms:03d}"
        
        # Calcola media stagionale
        avg_season = sum(best_times_sec) / len(best_times_sec)
        mins_avg = int(avg_season // 60)
        secs_avg = int(avg_season % 60)
        ms_avg = int((avg_season % 1) * 1000)
        
        avg_time_formatted = f"{mins_avg:02d}:{secs_avg:02d}.{ms_avg:03d}"
        
        # Media categoria
        cat_avg = sum(category_avg) / len(category_avg)
        mins_cat = int(cat_avg // 60)
        secs_cat = int(cat_avg % 60)
        ms_cat = int((cat_avg % 1) * 1000)
        
        cat_avg_formatted = f"{mins_cat:02d}:{secs_cat:02d}.{ms_cat:03d}"
        
        # Circuito migliore/peggiore
        circuit_avg_times = {}
        for i, circuit in enumerate(circuits):
            if i < len(best_times_sec):
                circuit_avg_times[circuit] = best_times_sec[i]
        
        best_circuit = min(circuit_avg_times, key=circuit_avg_times.get)
        worst_circuit = max(circuit_avg_times, key=circuit_avg_times.get)
        
        # Calcola tasso di miglioramento (differenza tra primo e ultimo tempo)
        if len(best_times_sec) >= 2:
            improvement = best_times_sec[0] - best_times_sec[-1]
            improvement_percentage = (improvement / best_times_sec[0]) * 100
            improvement_text = f"{improvement_percentage:.2f}% miglioramento"
        else:
            improvement_text = "Dati insufficienti"
        
        # Aggiorna labels statistiche
        self.best_lap_overall.setText(best_time_formatted)
        self.avg_lap_overall.setText(avg_time_formatted)
        self.category_avg_lap.setText(cat_avg_formatted)
        self.best_circuit.setText(f"{best_circuit} ({circuit_avg_times[best_circuit]:.2f}s)")
        self.worst_circuit.setText(f"{worst_circuit} ({circuit_avg_times[worst_circuit]:.2f}s)")
        self.improvement_rate.setText(improvement_text)
        
        # 4. Tabella dettaglio tempi
        self.lap_times_table.setRowCount(0)
        
        for i in range(len(races)):
            if i >= len(circuits):
                continue
                
            row = self.lap_times_table.rowCount()
            self.lap_times_table.insertRow(row)
            
            # Tempo in formato mm:ss.ms
            mins = int(best_times_sec[i] // 60)
            secs = int(best_times_sec[i] % 60)
            ms = int((best_times_sec[i] % 1) * 1000)
            formatted_time = f"{mins:02d}:{secs:02d}.{ms:03d}"
            
            # Tempo medio in formato mm:ss.ms
            mins_avg = int(avg_times_sec[i] // 60)
            secs_avg = int(avg_times_sec[i] % 60)
            ms_avg = int((avg_times_sec[i] % 1) * 1000)
            formatted_avg = f"{mins_avg:02d}:{secs_avg:02d}.{ms_avg:03d}"
            
            # Differenza con media
            diff = best_times_sec[i] - avg_times_sec[i]
            diff_text = f"{diff:.2f}s"
            
            self.lap_times_table.setItem(row, 0, QTableWidgetItem(races[i]))
            self.lap_times_table.setItem(row, 1, QTableWidgetItem(circuits[i]))
            self.lap_times_table.setItem(row, 2, QTableWidgetItem(formatted_time))
            self.lap_times_table.setItem(row, 3, QTableWidgetItem(formatted_avg))
            self.lap_times_table.setItem(row, 4, QTableWidgetItem(diff_text))
            
            # Colora in base alla differenza dalla media
            if diff < -2:  # Molto meglio della media
                color = QColor("#D4F0D0")
            elif diff < 0:  # Meglio della media
                color = QColor("#E2F0D0")
            elif diff > 2:  # Molto peggio della media
                color = QColor("#F0D0D0")
            elif diff > 0:  # Peggio della media
                color = QColor("#F0E2D0")
            else:
                color = QColor("#FFFFFF")
            
            for col in range(self.lap_times_table.columnCount()):
                item = self.lap_times_table.item(row, col)
                if item:
                    item.setBackground(color)
    
    def compare_pilots(self):
        """Compara il pilota selezionato con un altro pilota"""
        pilot1_id = self.pilot_combo.currentData()
        pilot2_id = self.compare_pilot_combo.currentData()
        
        if not pilot1_id or not pilot2_id:
            QMessageBox.warning(self, "Attenzione", "Seleziona entrambi i piloti!")
            return
        
        if pilot1_id == pilot2_id:
            QMessageBox.warning(self, "Attenzione", "Seleziona due piloti diversi!")
            return
        
        try:
            db = SessionLocal()
            
            # Ottieni dati piloti
            pilot1 = db.query(Pilota).get(pilot1_id)
            pilot2 = db.query(Pilota).get(pilot2_id)
            
            if not pilot1 or not pilot2:
                QMessageBox.warning(self, "Attenzione", "Pilota non trovato!")
                return
            
            # Dati di esempio per i grafici
            races = ["Gara 1", "Gara 2", "Gara 3", "Gara 4", "Gara 5"]
            
            # 1. Confronto posizioni
            ax1 = self.positions_comparison_chart.figure.subplots()
            
            p1_positions = [random.randint(1, 15) for _ in range(len(races))]
            p2_positions = [random.randint(1, 15) for _ in range(len(races))]
            
            # Invertiamo l'asse y per mostrare posizioni migliori in alto
            ax1.plot(races, p1_positions, marker='o', linestyle='-', color='blue', label=f"{pilot1.cognome}")
            ax1.plot(races, p2_positions, marker='s', linestyle='--', color='red', label=f"{pilot2.cognome}")
            
            ax1.set_ylim([max(max(p1_positions), max(p2_positions)) + 3, 0.5])
            ax1.set_ylabel('Posizione')
            ax1.set_xlabel('Gare')
            ax1.set_title('Confronto Posizioni')
            ax1.legend()
            ax1.grid(True, linestyle='--', alpha=0.7)
            
            self.positions_comparison_chart.figure.tight_layout()
            self.positions_comparison_chart.draw()
            
            # 2. Confronto punti
            ax2 = self.points_comparison_chart.figure.subplots()
            
            p1_points = [random.randint(50, 250) for _ in range(len(races))]
            p2_points = [random.randint(50, 250) for _ in range(len(races))]
            
            # Punti cumulativi
            p1_cumulative = [sum(p1_points[:i+1]) for i in range(len(p1_points))]
            p2_cumulative = [sum(p2_points[:i+1]) for i in range(len(p2_points))]
            
            x = np.arange(len(races))
            
            ax2.plot(races, p1_cumulative, marker='o', linestyle='-', color='blue', label=f"{pilot1.cognome}")
            ax2.plot(races, p2_cumulative, marker='s', linestyle='-', color='red', label=f"{pilot2.cognome}")
            
            ax2.set_ylabel('Punti totali')
            ax2.set_xlabel('Gare')
            ax2.set_title('Punti cumulativi')
            ax2.legend()
            ax2.grid(True, linestyle='--', alpha=0.7)
            
            self.points_comparison_chart.figure.tight_layout()
            self.points_comparison_chart.draw()
            
            # 3. Confronto tempi
            ax3 = self.times_comparison_chart.figure.subplots()
            
            p1_times = [random.uniform(90, 110) for _ in range(len(races))]
            p2_times = [random.uniform(90, 110) for _ in range(len(races))]
            
            ax3.plot(races, p1_times, marker='o', linestyle='-', color='blue', label=f"{pilot1.cognome}")
            ax3.plot(races, p2_times, marker='s', linestyle='--', color='red', label=f"{pilot2.cognome}")
            
            ax3.set_ylabel('Tempo (secondi)')
            ax3.set_xlabel('Gare')
            ax3.set_title('Confronto Tempi sul Giro')
            ax3.legend()
            ax3.grid(True, linestyle='--', alpha=0.7)
            
            self.times_comparison_chart.figure.tight_layout()
            self.times_comparison_chart.draw()
            
            # 4. Confronto radar
            ax4 = self.radar_comparison_chart.figure.subplots(subplot_kw={'polar': True})
            
            # Categorie del radar
            categories = ['Velocità', 'Costanza', 'Partenze', 'Sorpassi', 'Tecnica', 'Resistenza']
            N = len(categories)
            
            # Angoli per ogni asse
            angles = [n / float(N) * 2 * np.pi for n in range(N)]
            angles += angles[:1]  # Chiude il poligono
            
            # Valori per ciascun pilota (0-10)
            p1_values = [random.randint(5, 10) for _ in range(N)]
            p1_values += p1_values[:1]  # Chiude il poligono
            
            p2_values = [random.randint(5, 10) for _ in range(N)]
            p2_values += p2_values[:1]  # Chiude il poligono
            
            # Disegna i poligoni
            ax4.plot(angles, p1_values, linewidth=1, linestyle='solid', color='blue', label=f"{pilot1.cognome}")
            ax4.fill(angles, p1_values, 'blue', alpha=0.1)
            
            ax4.plot(angles, p2_values, linewidth=1, linestyle='solid', color='red', label=f"{pilot2.cognome}")
            ax4.fill(angles, p2_values, 'red', alpha=0.1)
            
            # Fissa il raggio massimo
            ax4.set_ylim(0, 10)
            
            # Imposta le etichette degli assi
            ax4.set_xticks(angles[:-1])
            ax4.set_xticklabels(categories)
            ax4.legend(loc='upper right')
            
            self.radar_comparison_chart.figure.tight_layout()
            self.radar_comparison_chart.draw()
            
            # 5. Tabella confronto testa a testa
            self.head_to_head_table.setRowCount(0)
            
            for i in range(len(races)):
                row = self.head_to_head_table.rowCount()
                self.head_to_head_table.insertRow(row)
                
                # Evento di esempio
                evento = f"MX Lombardia Round {i+1}"
                data = f"{15+i*15}/05/2025"
                circuito = ["Ottobiano", "Cremona", "Castiglione", "Maggiora", "Ponte a Egola"][i % 5]
                
                # Posizioni piloti
                p1_pos = p1_positions[i]
                p2_pos = p2_positions[i]
                
                # Tempi migliori
                p1_min = int(p1_times[i] // 60)
                p1_sec = int(p1_times[i] % 60)
                p1_ms = int((p1_times[i] % 1) * 1000)
                p1_time = f"{p1_min:02d}:{p1_sec:02d}.{p1_ms:03d}"
                
                p2_min = int(p2_times[i] // 60)
                p2_sec = int(p2_times[i] % 60)
                p2_ms = int((p2_times[i] % 1) * 1000)
                p2_time = f"{p2_min:02d}:{p2_sec:02d}.{p2_ms:03d}"
                
                # Inserisci dati nella tabella
                self.head_to_head_table.setItem(row, 0, QTableWidgetItem(evento))
                self.head_to_head_table.setItem(row, 1, QTableWidgetItem(data))
                self.head_to_head_table.setItem(row, 2, QTableWidgetItem(circuito))
                self.head_to_head_table.setItem(row, 3, QTableWidgetItem(str(p1_pos)))
                self.head_to_head_table.setItem(row, 4, QTableWidgetItem(str(p2_pos)))
                self.head_to_head_table.setItem(row, 5, QTableWidgetItem(p1_time))
                self.head_to_head_table.setItem(row, 6, QTableWidgetItem(p2_time))
                
                # Evidenzia il vincitore di ciascuna gara
                color1 = QColor("#D4F0D0") if p1_pos < p2_pos else QColor("white")
                color2 = QColor("#D4F0D0") if p2_pos < p1_pos else QColor("white")
                
                self.head_to_head_table.item(row, 3).setBackground(color1)
                self.head_to_head_table.item(row, 4).setBackground(color2)
            
            QMessageBox.information(self, "Confronto Completato", f"Confronto tra {pilot1.cognome} e {pilot2.cognome} completato con successo!")
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante il confronto: {str(e)}")
        finally:
            db.close()
    
    def update_prediction_data(self, pilot_id):
        """Aggiorna i dati di previsione per il pilota"""
        try:
            # 1. Grafico previsione posizione finale
            ax1 = self.prediction_chart.figure.subplots()
            
            # Dati di esempio
            races_completed = 4  # Supponiamo che abbiamo completato 4 gare su 7
            total_races = 7
            positions = [random.randint(1, 10) for _ in range(races_completed)]
            
            # Calcoliamo la posizione media attuale
            current_avg_pos = sum(positions) / len(positions)
            
            # Prevediamo la posizione finale (per esempio, mantenendo la media attuale)
            predicted_pos = current_avg_pos
            
            # Grafico a linee con previsione
            x_completed = list(range(1, races_completed + 1))
            x_future = list(range(races_completed + 1, total_races + 1))
            
            # Plottiamo le posizioni reali
            ax1.plot(x_completed, positions, marker='o', linestyle='-', color='blue', label='Posizioni reali')
            
            # Plottiamo la previsione
            future_positions = [predicted_pos] * len(x_future)
            ax1.plot(x_future, future_positions, marker='x', linestyle='--', color='red', label='Previsione')
            
            # Invertiamo l'asse y per mostrare posizioni migliori in alto
            ax1.set_ylim([max(positions + future_positions) + 2, 0.5])
            ax1.set_ylabel('Posizione')
            ax1.set_xlabel('Gare')
            ax1.set_xticks(range(1, total_races + 1))
            ax1.set_title('Previsione Posizione Finale')
            ax1.legend()
            ax1.grid(True, linestyle='--', alpha=0.7)
            
            self.prediction_chart.figure.tight_layout()
            self.prediction_chart.draw()
            
            # 2. Informazioni previsione
            # Calcoliamo la posizione finale prevista (arrotondata)
            final_pos = round(predicted_pos)
            
            # Calcolo punti previsti (esempio semplice)
            points_per_pos = {1: 250, 2: 210, 3: 170, 4: 140, 5: 120, 6: 110, 7: 100, 8: 90, 9: 85, 10: 80}
            avg_points_per_race = sum([points_per_pos.get(p, 50) for p in positions]) / len(positions)
            predicted_total_points = avg_points_per_race * total_races
            
            # Calcolo punti al pilota superiore (esempio)
            points_to_next = 0
            if final_pos > 1:
                points_per_race_next = points_per_pos.get(final_pos-1, points_per_pos.get(1)) - points_per_pos.get(final_pos, 0)
                points_to_next = points_per_race_next * (total_races - races_completed)
            
            # Possibilità podio
            if final_pos <= 3:
                chances = "Alta (già in zona podio)"
            elif final_pos <= 5:
                chances = "Media (potenziale con buoni risultati)"
            else:
                chances = "Bassa (difficile da raggiungere)"
            
            # Aggiorniamo i labels
            self.predicted_position.setText(str(final_pos))
            self.predicted_points.setText(f"{predicted_total_points:.0f} punti")
            self.points_to_next.setText(f"{points_to_next:.0f} punti")
            self.championship_chances.setText(chances)
            
            # 3. Suggerimenti miglioramento
            tip_templates = [
                "Basandosi sui tempi sul giro, il pilota potrebbe migliorare le prestazioni nelle curve {tipo}.",
                "Le partenze sono un punto {forza_debolezza}, concentrarsi su questo aspetto potrebbe {migliora_mantieni} i risultati.",
                "Il pilota ha mostrato {prestazione} su piste {tipo_terreno}, potrebbe essere utile allenarsi su questo tipo di terreni.",
                "L'analisi dei tempi mostra che il pilota tende a {trend_tempi} durante la gara, lavorare sulla resistenza potrebbe migliorare questo aspetto.",
                "Confrontando con i piloti in posizioni superiori, la principale differenza è nella {differenza}."
            ]
            
            # Generiamo suggerimenti casuali (in un'implementazione reale, sarebbero basati sui dati)
            tipo_curve = random.choice(["strette", "veloci", "tecniche"])
            forza_debolezza = random.choice(["di forza", "debole"])
            migliora_mantieni = "mantenere" if forza_debolezza == "di forza" else "migliorare"
            prestazione = random.choice(["ottime prestazioni", "difficoltà"])
            tipo_terreno = random.choice(["sabbiose", "dure", "fangose"])
            trend_tempi = random.choice(["rallentare", "mantenere tempi costanti", "migliorare"])
            differenza = random.choice(["velocità di punta", "consistenza", "tecnica nelle curve", "gestione della gara"])
            
            tips = [
                tip_templates[0].format(tipo=tipo_curve),
                tip_templates[1].format(forza_debolezza=forza_debolezza, migliora_mantieni=migliora_mantieni),
                tip_templates[2].format(prestazione=prestazione, tipo_terreno=tipo_terreno),
                tip_templates[3].format(trend_tempi=trend_tempi),
                tip_templates[4].format(differenza=differenza)
            ]
            
            # Seleziona 3 suggerimenti casuali
            selected_tips = random.sample(tips, 3)
            self.improvement_tips.setText("• " + "\n• ".join(selected_tips))
            
            # 4. Tabella prestazioni per circuito
            self.circuits_table.setRowCount(0)
            
            circuits = ["Ottobiano", "Cremona", "Castiglione", "Maggiora", "Ponte a Egola"]
            
            for circuit in circuits:
                row = self.circuits_table.rowCount()
                self.circuits_table.insertRow(row)
                
                # Valori di esempio
                best_pos = random.randint(1, 10)
                worst_pos = random.randint(best_pos, 20)
                avg_pos = (best_pos + worst_pos) / 2
                
                min_lap = random.randint(1, 2)
                sec_lap = random.randint(30, 59)
                ms_lap = random.randint(0, 999)
                best_time = f"{min_lap:02d}:{sec_lap:02d}.{ms_lap:03d}"
                
                performance_index = random.randint(60, 100)
                
                # Inserisci dati nella tabella
                self.circuits_table.setItem(row, 0, QTableWidgetItem(circuit))
                self.circuits_table.setItem(row, 1, QTableWidgetItem(str(best_pos)))
                self.circuits_table.setItem(row, 2, QTableWidgetItem(str(worst_pos)))
                self.circuits_table.setItem(row, 3, QTableWidgetItem(f"{avg_pos:.1f}"))
                self.circuits_table.setItem(row, 4, QTableWidgetItem(best_time))
                self.circuits_table.setItem(row, 5, QTableWidgetItem(f"{performance_index}/100"))
                
                # Colora in base all'indice di prestazione
                if performance_index >= 85:
                    color = QColor("#D4F0D0")  # Verde chiaro
                elif performance_index >= 70:
                    color = QColor("#E2F0D0")  # Verde più chiaro
                elif performance_index < 65:
                    color = QColor("#F0D0D0")  # Rosso chiaro
                else:
                    color = QColor("white")
                
                for col in range(self.circuits_table.columnCount()):
                    item = self.circuits_table.item(row, col)
                    if item:
                        item.setBackground(color)
            
            # 5. Grafico prestazioni circuiti
            ax5 = self.circuits_chart.figure.subplots()
            
            # Dati di esempio
            circuit_performance = [random.randint(60, 100) for _ in range(len(circuits))]
            circuit_avg = [75 for _ in range(len(circuits))]  # Media di riferimento
            
            x = np.arange(len(circuits))
            width = 0.35
            
            bars = ax5.bar(x, circuit_performance, width, label='Prestazione', color='skyblue')
            ax5.plot(x, circuit_avg, 'r--', label='Media Categoria')
            
            ax5.set_ylabel('Indice Prestazione')
            ax5.set_title('Prestazioni per Circuito')
            ax5.set_xticks(x)
            ax5.set_xticklabels(circuits, rotation=45, ha="right")
            ax5.legend()
            
            # Aggiunge valori sopra le barre
            for bar in bars:
                height = bar.get_height()
                ax5.annotate(f'{height}', xy=(bar.get_x() + bar.get_width() / 2, height),
                             xytext=(0, 3), textcoords="offset points", ha='center')
            
            self.circuits_chart.figure.tight_layout()
            self.circuits_chart.draw()
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante l'aggiornamento delle previsioni: {str(e)}")
    
    def export_report(self):
        """Esporta le statistiche del pilota in un file CSV"""
        pilot_id = self.pilot_combo.currentData()
        
        if not pilot_id:
            QMessageBox.warning(self, "Attenzione", "Seleziona un pilota prima di esportare!")
            return
        
        try:
            db = SessionLocal()
            
            # Ottieni dati pilota
            pilot = db.query(Pilota).get(pilot_id)
            
            if not pilot:
                QMessageBox.warning(self, "Attenzione", "Pilota non trovato!")
                return
            
            # Apri finestra di dialogo per salvare il file
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Salva Report Statistiche", 
                f"Statistiche_{pilot.cognome}_{pilot.nome}.csv", 
                "File CSV (*.csv)"
            )
            
            if not file_path:
                return
            
            # Ottieni le iscrizioni del pilota
            iscrizioni = db.query(Iscrizione).filter(Iscrizione.pilota_id == pilot_id).all()
            
            # Scrivi il file CSV
            with open(file_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                
                # Intestazione file
                writer.writerow(['Report Statistiche Pilota'])
                writer.writerow([f'Pilota: {pilot.nome} {pilot.cognome}'])
                writer.writerow([f'Data generazione: {datetime.now().strftime("%d/%m/%Y %H:%M")}'])
                writer.writerow([])
                
                # Informazioni pilota
                writer.writerow(['DATI PILOTA'])
                writer.writerow(['Nome', pilot.nome])
                writer.writerow(['Cognome', pilot.cognome])
                writer.writerow(['Data Nascita', pilot.data_nascita.strftime("%d/%m/%Y") if hasattr(pilot, 'data_nascita') and pilot.data_nascita else ''])
                writer.writerow(['Licenza', pilot.licenza_tipo])
                writer.writerow(['Numero Licenza', pilot.numero_licenza])
                writer.writerow(['Moto Club', pilot.moto_club])
                
                if hasattr(pilot, 'marca_moto') and pilot.marca_moto:
                    writer.writerow(['Marca Moto', pilot.marca_moto])
                
                if hasattr(pilot, 'numero_gara') and pilot.numero_gara:
                    writer.writerow(['Numero Gara', pilot.numero_gara])
                
                writer.writerow([])
                
                # Statistiche sommario
                writer.writerow(['STATISTICHE RIASSUNTIVE'])
                writer.writerow(['Gare Disputate', self.races_stat.value_label.text()])
                writer.writerow(['Podi', self.podiums_stat.value_label.text()])
                writer.writerow(['Vittorie', self.wins_stat.value_label.text()])
                writer.writerow(['Punti Totali', self.points_stat.value_label.text()])
                writer.writerow(['Posizione Classifica', self.position_stat.value_label.text()])
                writer.writerow(['Miglior Risultato', self.best_result_stat.value_label.text()])
                writer.writerow([])
                
                # Dettagli gare
                writer.writerow(['DETTAGLI GARE'])
                writer.writerow(['Evento', 'Data', 'Circuito', 'Posizione', 'Giri', 'Tempo Totale', 'Distacco', 'Miglior Tempo', 'Punti'])
                
                # Esporta dati dalla tabella
                for row in range(self.races_table.rowCount()):
                    row_data = []
                    for col in range(self.races_table.columnCount()):
                        item = self.races_table.item(row, col)
                        row_data.append(item.text() if item else '')
                    writer.writerow(row_data)
                
                writer.writerow([])
                
                # Analisi tempi
                writer.writerow(['ANALISI TEMPI'])
                writer.writerow(['Miglior giro assoluto', self.best_lap_overall.text()])
                writer.writerow(['Media giri stagionale', self.avg_lap_overall.text()])
                writer.writerow(['Media categoria', self.category_avg_lap.text()])
                writer.writerow(['Circuito migliore', self.best_circuit.text()])
                writer.writerow(['Circuito peggiore', self.worst_circuit.text()])
                writer.writerow(['Tasso miglioramento', self.improvement_rate.text()])
                writer.writerow([])
                
                # Tabella tempi dettagliati
                writer.writerow(['TEMPI DETTAGLIATI PER GARA'])
                writer.writerow(['Evento', 'Circuito', 'Miglior Tempo', 'Media', 'Differenza'])
                
                for row in range(self.lap_times_table.rowCount()):
                    row_data = []
                    for col in range(self.lap_times_table.columnCount()):
                        item = self.lap_times_table.item(row, col)
                        row_data.append(item.text() if item else '')
                    writer.writerow(row_data)
                
                writer.writerow([])
                
                # Previsioni
                writer.writerow(['PREVISIONI CAMPIONATO'])
                writer.writerow(['Posizione finale prevista', self.predicted_position.text()])
                writer.writerow(['Punti previsti', self.predicted_points.text()])
                writer.writerow(['Punti al pilota superiore', self.points_to_next.text()])
                writer.writerow(['Possibilità podio', self.championship_chances.text()])
                writer.writerow([])
                
                # Suggerimenti miglioramento
                writer.writerow(['SUGGERIMENTI PER MIGLIORAMENTO'])
                tips = self.improvement_tips.text().split('\n')
                for tip in tips:
                    writer.writerow([tip])
            
            QMessageBox.information(self, "Report Esportato", f"Report statistiche salvato in {file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante l'esportazione del report: {str(e)}")
        finally:
            db.close()
    
    def share_statistics(self):
        """Condivide le statistiche via email o WhatsApp"""
        pilot_id = self.pilot_combo.currentData()
        
        if not pilot_id:
            QMessageBox.warning(self, "Attenzione", "Seleziona un pilota prima di condividere!")
            return
        
        try:
            db = SessionLocal()
            
            # Ottieni dati pilota
            pilot = db.query(Pilota).get(pilot_id)
            
            if not pilot:
                QMessageBox.warning(self, "Attenzione", "Pilota non trovato!")
                return
            
            # Crea un testo per la condivisione
            pilota_nome = f"{pilot.nome} {pilot.cognome}"
            
            share_text = f"Statistiche di {pilota_nome}\n\n"
            share_text += f"Gare disputate: {self.races_stat.value_label.text()}\n"
            share_text += f"Podi: {self.podiums_stat.value_label.text()}\n"
            share_text += f"Vittorie: {self.wins_stat.value_label.text()}\n"
            share_text += f"Punti totali: {self.points_stat.value_label.text()}\n"
            share_text += f"Posizione in classifica: {self.position_stat.value_label.text()}\n"
            share_text += f"Miglior risultato: {self.best_result_stat.value_label.text()}\n\n"
            
            share_text += f"Miglior giro assoluto: {self.best_lap_overall.text()}\n"
            share_text += f"Previsione posizione finale: {self.predicted_position.text()}\n\n"
            
            share_text += f"Generato da MX Manager - Software Gestione Gare Motocross"
            
            # Opzioni di condivisione
            options = ["Email", "WhatsApp", "Copia negli appunti"]
            
            selected_option, ok = QFileDialog.getOpenFileName(
                self, "Seleziona metodo di condivisione", "", ";;".join(options)
            )
            
            if not ok:
                return
            
            if "Email" in selected_option:
                # Apertura client email con dati precompilati
                import webbrowser
                subject = f"Statistiche pilota {pilota_nome}"
                body = share_text.replace("\n", "%0D%0A")
                webbrowser.open(f"mailto:?subject={subject}&body={body}")
                
                QMessageBox.information(self, "Condivisione", "Si aprirà il tuo client email predefinito")
                
            elif "WhatsApp" in selected_option:
                # Apertura WhatsApp Web con messaggio precompilato
                import webbrowser
                text = share_text.replace("\n", "%0A")
                webbrowser.open(f"https://wa.me/?text={text}")
                
                QMessageBox.information(self, "Condivisione", "Si aprirà WhatsApp Web per condividere le statistiche")
                
            else:  # Copia negli appunti