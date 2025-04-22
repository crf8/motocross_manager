# ui/statistics_dashboard.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLabel, QComboBox, QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QMessageBox, QTabWidget,
    QSplitter, QFrame, QFileDialog
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor, QPixmap

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np

from database.connection import SessionLocal
from database.models import Pilota, Iscrizione, Evento, Categoria, Risultato, LapTime
from .pilot_detailed_stats import PilotDetailedStatsWidget

class StatisticsDashboard(QWidget):
    """Dashboard principale per le statistiche"""
    
    def __init__(self):
        super().__init__()
        
        # Layout principale
        layout = QVBoxLayout(self)
        
        # Titolo
        title_label = QLabel("Dashboard Statistiche")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Tab widget per diverse viste statistiche
        self.tabs = QTabWidget()
        
        # Tab 1: Statistiche Pilota
        self.rider_stats_tab = PilotDetailedStatsWidget()
        self.tabs.addTab(self.rider_stats_tab, "Statistiche Pilota")
        
        # Tab 2: Statistiche Evento
        self.event_stats_tab = EventStatsWidget()
        self.tabs.addTab(self.event_stats_tab, "Statistiche Evento")
        
        # Tab 3: Classifica Campionato
        self.championship_tab = ChampionshipStatsWidget()
        self.tabs.addTab(self.championship_tab, "Classifica Campionato")
        
        # Tab 4: Statistiche Moto/Team
        self.team_stats_tab = TeamStatsWidget()
        self.tabs.addTab(self.team_stats_tab, "Statistiche Moto/Team")
        
        layout.addWidget(self.tabs)

    class EventStatsWidget(QWidget):
    """Widget per visualizzare le statistiche di un evento"""
    
    def __init__(self):
        super().__init__()
        
        # Layout principale
        layout = QVBoxLayout(self)
        
        # Selettori
        selectors_layout = QFormLayout()
        
        self.event_combo = QComboBox()
        selectors_layout.addRow("Evento:", self.event_combo)
        
        self.load_button = QPushButton("Carica Statistiche")
        self.load_button.clicked.connect(self.load_event_stats)
        
        selectors_layout.addRow("", self.load_button)
        layout.addLayout(selectors_layout)
        
        # Contenitore principale per le statistiche (diviso in due colonne)
        stats_container = QSplitter(Qt.Orientation.Horizontal)
        
        # Colonna sinistra: grafici
        left_column = QWidget()
        left_layout = QVBoxLayout(left_column)
        
        # Grafico 1: Distribuzione piloti per categoria
        self.category_chart_container = QGroupBox("Piloti per Categoria")
        category_chart_layout = QVBoxLayout(self.category_chart_container)
        
        self.category_chart = FigureCanvas(plt.Figure(figsize=(5, 4)))
        category_chart_layout.addWidget(self.category_chart)
        
        left_layout.addWidget(self.category_chart_container)
        
        # Grafico 2: Distribuzione tempi sul giro
        self.lap_times_chart_container = QGroupBox("Distribuzione Tempi sul Giro")
        lap_times_chart_layout = QVBoxLayout(self.lap_times_chart_container)
        
        self.lap_times_chart = FigureCanvas(plt.Figure(figsize=(5, 4)))
        lap_times_chart_layout.addWidget(self.lap_times_chart)
        
        left_layout.addWidget(self.lap_times_chart_container)
        
        stats_container.addWidget(left_column)
        
        # Colonna destra: tabelle
        right_column = QWidget()
        right_layout = QVBoxLayout(right_column)
        
        # Tabella 1: Migliori tempi assoluti
        self.best_times_group = QGroupBox("Migliori Tempi sul Giro")
        best_times_layout = QVBoxLayout(self.best_times_group)
        
        self.best_times_table = QTableWidget(0, 5)
        self.best_times_table.setHorizontalHeaderLabels([
            "Pos", "Pilota", "Categoria", "Tempo", "Sessione"
        ])
        self.best_times_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        best_times_layout.addWidget(self.best_times_table)
        right_layout.addWidget(self.best_times_group)
        
        # Tabella 2: Migliori piloti dell'evento
        self.best_riders_group = QGroupBox("Classifica Piloti dell'Evento")
        best_riders_layout = QVBoxLayout(self.best_riders_group)
        
        self.best_riders_table = QTableWidget(0, 5)
        self.best_riders_table.setHorizontalHeaderLabels([
            "Pos", "Pilota", "Categoria", "Punti", "Miglior Risultato"
        ])
        self.best_riders_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        best_riders_layout.addWidget(self.best_riders_table)
        right_layout.addWidget(self.best_riders_group)
        
        stats_container.addWidget(right_column)
        
        layout.addWidget(stats_container)
        
        # Carica eventi nel combo
        self.load_events()
    
    def load_events(self):
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
    
    def load_event_stats(self):
        """Carica le statistiche dell'evento selezionato"""
        evento_id = self.event_combo.currentData()
        
        if not evento_id:
            QMessageBox.warning(self, "Attenzione", "Seleziona un evento!")
            return
        
        try:
            db = SessionLocal()
            
            # Carica l'evento
            evento = db.query(Evento).get(evento_id)
            
            if not evento:
                QMessageBox.warning(self, "Attenzione", "Evento non trovato!")
                return
            
            # 1. Ottieni distribuzione piloti per categoria
            self.load_category_distribution(db, evento_id)
            
            # 2. Ottieni distribuzione tempi sul giro
            self.load_lap_times_distribution(db, evento_id)
            
            # 3. Ottieni migliori tempi dell'evento
            self.load_best_lap_times(db, evento_id)
            
            # 4. Ottieni classifica piloti dell'evento
            self.load_best_riders(db, evento_id)
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante il caricamento statistiche: {str(e)}")
        finally:
            db.close()
    
    def load_category_distribution(self, db, evento_id):
        """Carica la distribuzione dei piloti per categoria"""
        try:
            # Query per ottenere il conteggio dei piloti per categoria
            query = """
            SELECT c.classe || ' ' || c.categoria as categoria, COUNT(i.id) as num_piloti
            FROM iscrizioni i
            JOIN categorie c ON i.categoria_id = c.id
            WHERE i.evento_id = :evento_id
            GROUP BY c.classe, c.categoria
            ORDER BY num_piloti DESC
            """
            
            results = db.execute(query, {"evento_id": evento_id}).fetchall()
            
            if not results:
                return
            
            # Prepara i dati per il grafico a torta
            categories = [r[0] for r in results]
            counts = [r[1] for r in results]
            
            # Crea il grafico a torta
            ax = self.category_chart.figure.subplots()
            ax.clear()
            
            # Crea grafico a torta
            wedges, texts, autotexts = ax.pie(
                counts, 
                autopct='%1.1f%%',
                textprops={'color': "w", 'fontweight': 'bold'},
                shadow=True,
                startangle=90
            )
            
            # Aggiungi legenda
            ax.legend(
                wedges, 
                [f"{cat} ({count})" for cat, count in zip(categories, counts)],
                title="Categorie",
                loc="center left",
                bbox_to_anchor=(1, 0, 0.5, 1)
            )
            
            ax.set_title(f"Distribuzione Piloti per Categoria")
            
            self.category_chart.figure.tight_layout()
            self.category_chart.draw()
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore nella distribuzione categorie: {str(e)}")
    
    def load_lap_times_distribution(self, db, evento_id):
        """Carica la distribuzione dei tempi sul giro"""
        try:
            # Query per ottenere tutti i tempi sul giro validi
            query = """
            SELECT lt.tempo_ms
            FROM lap_times lt
            JOIN iscrizioni i ON lt.iscrizione_id = i.id
            WHERE i.evento_id = :evento_id
            AND lt.tempo_ms > 0
            AND lt.numero_giro > 1
            """
            
            results = db.execute(query, {"evento_id": evento_id}).fetchall()
            
            if not results:
                return
            
            # Ottieni i tempi in secondi
            times_sec = [r[0] / 1000.0 for r in results]
            
            # Crea istogramma
            ax = self.lap_times_chart.figure.subplots()
            ax.clear()
            
            # Calcola il numero di bin per l'istogramma (regola di Sturges)
            import math
            num_bins = int(1 + 3.322 * math.log10(len(times_sec)))
            
            # Crea istogramma
            n, bins, patches = ax.hist(
                times_sec, 
                bins=num_bins,
                alpha=0.7,
                color='skyblue',
                edgecolor='black'
            )
            
            # Evidenzia il bin con la media
            mean_time = np.mean(times_sec)
            for i, patch in enumerate(patches):
                if bins[i] <= mean_time < bins[i+1]:
                    patch.set_facecolor('orange')
                    break
            
            # Aggiungi linea verticale per la media
            ax.axvline(x=mean_time, color='r', linestyle='--', linewidth=1, label=f'Media: {mean_time:.2f}s')
            
            # Aggiungi statistiche
            min_time = min(times_sec)
            max_time = max(times_sec)
            
            stats_text = f"Min: {min_time:.2f}s\nMax: {max_time:.2f}s\nMedia: {mean_time:.2f}s"
            ax.text(0.02, 0.95, stats_text, transform=ax.transAxes, 
                     verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
            
            ax.set_xlabel('Tempo sul giro (secondi)')
            ax.set_ylabel('Frequenza')
            ax.set_title('Distribuzione dei Tempi sul Giro')
            ax.grid(True, linestyle='--', alpha=0.7)
            
            self.lap_times_chart.figure.tight_layout()
            self.lap_times_chart.draw()
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore nella distribuzione tempi: {str(e)}")
    
    def load_best_lap_times(self, db, evento_id):
        """Carica i migliori tempi sul giro dell'evento"""
        try:
            # Query per ottenere i migliori tempi sul giro
            query = """
            SELECT 
                p.nome || ' ' || p.cognome as pilota,
                c.classe || ' ' || c.categoria as categoria,
                MIN(lt.tempo_ms) as best_time,
                lt.sessione_tipo
            FROM lap_times lt
            JOIN iscrizioni i ON lt.iscrizione_id = i.id
            JOIN piloti p ON i.pilota_id = p.id
            JOIN categorie c ON i.categoria_id = c.id
            WHERE i.evento_id = :evento_id
            AND lt.tempo_ms > 0
            AND lt.numero_giro > 1
            GROUP BY i.id, lt.sessione_tipo
            ORDER BY best_time
            LIMIT 20
            """
            
            results = db.execute(query, {"evento_id": evento_id}).fetchall()
            
            # Pulisci la tabella
            self.best_times_table.setRowCount(0)
            
            for i, (pilota, categoria, tempo_ms, sessione) in enumerate(results):
                row = self.best_times_table.rowCount()
                self.best_times_table.insertRow(row)
                
                # Formatta il tempo
                secs = tempo_ms // 1000
                mins = secs // 60
                secs %= 60
                msecs = tempo_ms % 1000
                tempo_formattato = f"{mins:02d}:{secs:02d}.{msecs:03d}"
                
                self.best_times_table.setItem(row, 0, QTableWidgetItem(str(i+1)))
                self.best_times_table.setItem(row, 1, QTableWidgetItem(pilota))
                self.best_times_table.setItem(row, 2, QTableWidgetItem(categoria))
                self.best_times_table.setItem(row, 3, QTableWidgetItem(tempo_formattato))
                self.best_times_table.setItem(row, 4, QTableWidgetItem(sessione))
                
                # Colora il podio
                if i < 3:
                    for col in range(5):
                        item = self.best_times_table.item(row, col)
                        if item:
                            item.setBackground(QColor(255, 255, 200 - i*30))
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore nel caricamento migliori tempi: {str(e)}")
    
    def load_best_riders(self, db, evento_id):
        """Carica la classifica dei piloti dell'evento"""
        try:
            # Query per ottenere i risultati totali dei piloti nell'evento
            query = """
            SELECT 
                p.nome || ' ' || p.cognome as pilota,
                c.classe || ' ' || c.categoria as categoria,
                SUM(r.punti) as punti_totali,
                MIN(r.posizione) as miglior_posizione
            FROM risultati r
            JOIN iscrizioni i ON r.iscrizione_id = i.id
            JOIN piloti p ON i.pilota_id = p.id
            JOIN categorie c ON i.categoria_id = c.id
            JOIN gruppi g ON r.gruppo_id = g.id
            WHERE g.evento_id = :evento_id
            AND r.sessione_tipo IN ('Gara 1', 'Gara 2')
            GROUP BY i.pilota_id
            ORDER BY punti_totali DESC, miglior_posizione
            LIMIT 20
            """
            
            results = db.execute(query, {"evento_id": evento_id}).fetchall()
            
            # Pulisci la tabella
            self.best_riders_table.setRowCount(0)
            
            for i, (pilota, categoria, punti, posizione) in enumerate(results):
                row = self.best_riders_table.rowCount()
                self.best_riders_table.insertRow(row)
                
                # Formatta il miglior risultato
                miglior_risultato = f"{posizione}° posto"
                
                self.best_riders_table.setItem(row, 0, QTableWidgetItem(str(i+1)))
                self.best_riders_table.setItem(row, 1, QTableWidgetItem(pilota))
                self.best_riders_table.setItem(row, 2, QTableWidgetItem(categoria))
                self.best_riders_table.setItem(row, 3, QTableWidgetItem(str(punti)))
                self.best_riders_table.setItem(row, 4, QTableWidgetItem(miglior_risultato))
                
                # Colora il podio
                if i < 3:
                    for col in range(5):
                        item = self.best_riders_table.item(row, col)
                        if item:
                            item.setBackground(QColor(255, 255, 200 - i*30))
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore nel caricamento migliori piloti: {str(e)}")


    class ChampionshipStatsWidget(QWidget):
    """Widget per visualizzare le statistiche del campionato"""
    
    def __init__(self):
        super().__init__()
        
        # Layout principale
        layout = QVBoxLayout(self)
        
        # Selettori
        selectors_layout = QFormLayout()
        
        self.year_combo = QComboBox()
        self.year_combo.addItems(["2025", "2024", "2023"])
        selectors_layout.addRow("Anno:", self.year_combo)
        
        self.championship_combo = QComboBox()
        self.championship_combo.addItems(["Campionato Regionale Motocross", "Trofeo Lombardia"])
        selectors_layout.addRow("Campionato:", self.championship_combo)
        
        self.category_combo = QComboBox()
        selectors_layout.addRow("Categoria:", self.category_combo)
        
        self.load_button = QPushButton("Carica Classifica")
        self.load_button.clicked.connect(self.load_championship)
        selectors_layout.addRow("", self.load_button)
        
        layout.addLayout(selectors_layout)
        
        # Contenitore principale per le statistiche (diviso in due colonne)
        stats_container = QSplitter(Qt.Orientation.Horizontal)
        
        # Colonna sinistra: grafico classifica
        left_column = QWidget()
        left_layout = QVBoxLayout(left_column)
        
        # Grafico classifica
        self.standings_chart_container = QGroupBox("Classifica Campionato")
        standings_chart_layout = QVBoxLayout(self.standings_chart_container)
        
        self.standings_chart = FigureCanvas(plt.Figure(figsize=(5, 6)))
        standings_chart_layout.addWidget(self.standings_chart)
        
        left_layout.addWidget(self.standings_chart_container)
        
        stats_container.addWidget(left_column)
        
        # Colonna destra: tabella classifica
        right_column = QWidget()
        right_layout = QVBoxLayout(right_column)
        
        # Tabella classifica
        self.standings_group = QGroupBox("Classifica Dettagliata")
        standings_layout = QVBoxLayout(self.standings_group)
        
        self.standings_table = QTableWidget(0, 5)
        self.standings_table.setHorizontalHeaderLabels([
            "Pos", "Pilota", "Categoria", "Punti", "Vittorie"
        ])
        self.standings_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        standings_layout.addWidget(self.standings_table)
        right_layout.addWidget(self.standings_group)
        
        # Tabella statistiche campionato
        self.championship_stats_group = QGroupBox("Statistiche Campionato")
        championship_stats_layout = QFormLayout()
        
        self.total_riders_label = QLabel("0")
        self.events_completed_label = QLabel("0")
        self.most_wins_label = QLabel("-")
        self.most_points_label = QLabel("-")
        self.avg_participants_label = QLabel("0")
        
        championship_stats_layout.addRow("Piloti iscritti:", self.total_riders_label)
        championship_stats_layout.addRow("Eventi disputati:", self.events_completed_label)
        championship_stats_layout.addRow("Pilota con più vittorie:", self.most_wins_label)
        championship_stats_layout.addRow("Pilota con più punti:", self.most_points_label)
        championship_stats_layout.addRow("Media piloti per evento:", self.avg_participants_label)
        
        self.championship_stats_group.setLayout(championship_stats_layout)
        right_layout.addWidget(self.championship_stats_group)
        
        stats_container.addWidget(right_column)
        
        layout.addWidget(stats_container)
        
        # Carica categorie nel combo
        self.load_categories()
        
        # Collega il cambio di anno al caricamento delle categorie
        self.year_combo.currentIndexChanged.connect(self.load_categories)
        self.championship_combo.currentIndexChanged.connect(self.load_categories)
    
    def load_categories(self):
        """Carica le categorie nel combobox"""
        try:
            db = SessionLocal()
            
            # Ottieni tutte le categorie disponibili
            categorie = db.query(Categoria).all()
            
            self.category_combo.clear()
            self.category_combo.addItem("Tutte le categorie", 0)
            
            for categoria in categorie:
                display_text = f"{categoria.classe} {categoria.categoria}"
                self.category_combo.addItem(display_text, categoria.id)
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante il caricamento categorie: {str(e)}")
        finally:
            db.close()
    
    def load_championship(self):
        """Carica la classifica del campionato"""
        year = self.year_combo.currentText()
        championship = self.championship_combo.currentText()
        categoria_id = self.category_combo.currentData()
        
        try:
            db = SessionLocal()
            
            # Trova gli eventi del campionato nell'anno selezionato
            year_start = f"{year}-01-01"
            year_end = f"{year}-12-31"
            
            events_query = db.query(Evento).filter(
                Evento.data.between(year_start, year_end),
                Evento.tipo.contains(championship)
            ).all()
            
            if not events_query:
                QMessageBox.warning(self, "Attenzione", f"Nessun evento trovato per {championship} {year}!")
                return
            
            event_ids = [e.id for e in events_query]
            
            # Costruisci la query per i risultati
            query = """
            SELECT 
                p.id as pilota_id,
                p.nome || ' ' || p.cognome as pilota,
                c.classe || ' ' || c.categoria as categoria,
                SUM(r.punti) as punti_totali,
                COUNT(CASE WHEN r.posizione = 1 THEN 1 END) as vittorie
            FROM risultati r
            JOIN iscrizioni i ON r.iscrizione_id = i.id
            JOIN piloti p ON i.pilota_id = p.id
            JOIN categorie c ON i.categoria_id = c.id
            JOIN gruppi g ON r.gruppo_id = g.id
            WHERE g.evento_id IN :event_ids
            AND r.sessione_tipo IN ('Gara 1', 'Gara 2')
            """
            
            # Filtra per categoria se selezionata
            if categoria_id and categoria_id > 0:
                query += " AND i.categoria_id = :categoria_id"
            
            query += " GROUP BY p.id ORDER BY punti_totali DESC"
            
            params = {"event_ids": tuple(event_ids)}
            
            if categoria_id and categoria_id > 0:
                params["categoria_id"] = categoria_id
            
            results = db.execute(query, params).fetchall()
            
            if not results:
                QMessageBox.warning(self, "Attenzione", "Nessun risultato trovato!")
                return
            
            # Aggiorna la tabella classifica
            self.standings_table.setRowCount(0)
            
            for i, (pilota_id, pilota, categoria, punti, vittorie) in enumerate(results):
                row = self.standings_table.rowCount()
                self.standings_table.insertRow(row)
                
                self.standings_table.setItem(row, 0, QTableWidgetItem(str(i+1)))
                self.standings_table.setItem(row, 1, QTableWidgetItem(pilota))
                self.standings_table.setItem(row, 2, QTableWidgetItem(categoria))
                self.standings_table.setItem(row, 3, QTableWidgetItem(str(punti)))
                self.standings_table.setItem(row, 4, QTableWidgetItem(str(vittorie)))
                
                # Colora le prime 3 posizioni
                if i < 3:
                    colors = [QColor(255, 215, 0, 100),  # Oro
                              QColor(192, 192, 192, 100),  # Argento
                              QColor(205, 127, 50, 100)]  # Bronzo
                    for col in range(5):
                        item = self.standings_table.item(row, col)
                        if item:
                            item.setBackground(colors[i])
            
            # Aggiorna il grafico classifica
            self.update_standings_chart(results[:10])  # Primi 10 classificati
            
            # Aggiorna le statistiche del campionato
            self.update_championship_stats(db, event_ids, results)
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore nel caricamento classifica: {str(e)}")
        finally:
            db.close()
    
    def update_standings_chart(self, results):
        """Aggiorna il grafico della classifica"""
        try:
            # Dati per il grafico
            pilots = [r[1] for r in results]  # Nome pilota
            points = [r[3] for r in results]  # Punti
            
            # Crea il grafico a barre orizzontale
            ax = self.standings_chart.figure.subplots()
            ax.clear()
            
            # Crea le barre (orizzontali)
            bars = ax.barh(
                pilots[::-1],  # Inverti per avere il primo in alto
                points[::-1],
                color=['gold' if i == len(pilots)-1 else 
                      'silver' if i == len(pilots)-2 else 
                      'goldenrod' if i == len(pilots)-3 else 
                      'skyblue' for i in range(len(pilots))]
            )
            
            # Aggiungi etichette con i punti
            for bar in bars:
                width = bar.get_width()
                ax.text(
                    width + 5,
                    bar.get_y() + bar.get_height()/2,
                    f'{width}',
                    va='center'
                )
            
            # Titoli e assi
            championship = self.championship_combo.currentText()
            year = self.year_combo.currentText()
            ax.set_title(f"Classifica {championship} {year}")
            ax.set_xlabel('Punti')
            
            # Rimuovi linee dei bordi
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
            self.standings_chart.figure.tight_layout()
            self.standings_chart.draw()
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore nell'aggiornamento grafico: {str(e)}")
    
    def update_championship_stats(self, db, event_ids, results):
        """Aggiorna le statistiche del campionato"""
        try:
            # Numero totale di piloti
            total_riders = len(results)
            self.total_riders_label.setText(str(total_riders))
            
            # Eventi completati
            events_completed = len(event_ids)
            self.events_completed_label.setText(str(events_completed))
            
            # Pilota con più vittorie
            if