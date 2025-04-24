# ui/standings_manager.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLabel, QComboBox, QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QMessageBox, QTabWidget,
    QSpinBox, QCheckBox, QFileDialog, QGroupBox
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtPrintSupport import QPrinter
from PyQt6.QtPrintSupport import QPrintPreviewDialog

from database.connection import SessionLocal
from database.models import Evento, Iscrizione, Pilota, Categoria, Gruppo, PartecipazioneGruppo, LapTime, Risultato

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np

class StandingsManager(QWidget):
    """Gestore delle classifiche"""
    
    def __init__(self):
        super().__init__()
        
        # Layout principale
        layout = QVBoxLayout(self)
        
        # Titolo
        title_label = QLabel("Gestione Classifiche")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Creiamo un widget con tab per le diverse classifiche
        self.tabs = QTabWidget()
        
        # Tab per la classifica delle prove libere e qualifiche
        self.practice_qual_tab = PracticeQualStandingsTab()
        self.tabs.addTab(self.practice_qual_tab, "Prove/Qualifiche")
        
        # Tab per la classifica delle gare singole
        self.race_standings_tab = RaceStandingsTab()
        self.tabs.addTab(self.race_standings_tab, "Gare")
        
        # Tab per la classifica di giornata
        self.daily_standings_tab = DailyStandingsTab()
        self.tabs.addTab(self.daily_standings_tab, "Classifica Giornata")
        
        # Tab per la classifica del campionato
        self.championship_tab = ChampionshipStandingsTab()
        self.tabs.addTab(self.championship_tab, "Campionato")
        
        # Tab per le statistiche
        self.stats_tab = StatsTab()
        self.tabs.addTab(self.stats_tab, "Statistiche")
        
        layout.addWidget(self.tabs)

class PracticeQualStandingsTab(QWidget):
    """Tab per visualizzare le classifiche delle prove libere e qualifiche"""
    
    def __init__(self):
        super().__init__()
        
        # Layout principale
        layout = QVBoxLayout(self)
        
        # Selettori
        selectors_layout = QFormLayout()
        
        self.event_combo = QComboBox()
        selectors_layout.addRow("Evento:", self.event_combo)
        
        self.session_type_combo = QComboBox()
        self.session_type_combo.addItems(["Prove Libere", "Qualifiche"])
        selectors_layout.addRow("Sessione:", self.session_type_combo)
        
        self.category_combo = QComboBox()
        selectors_layout.addRow("Categoria:", self.category_combo)
        
        layout.addLayout(selectors_layout)
        
        # Bottoni
        buttons_layout = QHBoxLayout()
        
        self.load_button = QPushButton("Carica Classifica")
        self.load_button.clicked.connect(self.load_standings)
        buttons_layout.addWidget(self.load_button)
        
        self.print_button = QPushButton("Stampa Classifica")
        self.print_button.clicked.connect(self.print_standings)
        buttons_layout.addWidget(self.print_button)
        
        layout.addLayout(buttons_layout)
        
        # Tabella per i risultati
        self.results_table = QTableWidget(0, 5)
        self.results_table.setHorizontalHeaderLabels([
            "Pos", "Num", "Pilota", "Categoria", "Miglior Tempo"
        ])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.results_table)
        
        # Carica eventi
        self.load_events()
        
        # Collega eventi combo
        self.event_combo.currentIndexChanged.connect(self.load_categories)
    
    def load_events(self):
        """Carica gli eventi nel combo box"""
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
    
    def load_categories(self):
        """Carica le categorie per l'evento selezionato"""
        evento_id = self.event_combo.currentData()
        
        if not evento_id:
            return
        
        try:
            db = SessionLocal()
            
            # Otteniamo le categorie uniche degli iscritti
            iscrizioni = db.query(Iscrizione).filter(
                Iscrizione.evento_id == evento_id
            ).all()
            
            categorie_set = set()
            
            for iscrizione in iscrizioni:
                categoria = iscrizione.categoria
                categorie_set.add((categoria.id, f"{categoria.classe} {categoria.categoria}"))
            
            self.category_combo.clear()
            self.category_combo.addItem("Tutte le categorie", 0)
            
            for cat_id, cat_name in sorted(categorie_set, key=lambda x: x[1]):
                self.category_combo.addItem(cat_name, cat_id)
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante il caricamento categorie: {str(e)}")
        finally:
            db.close()
    
    def load_standings(self):
        """Carica la classifica delle prove/qualifiche"""
        evento_id = self.event_combo.currentData()
        session_type = self.session_type_combo.currentText()
        categoria_id = self.category_combo.currentData()
        
        if not evento_id:
            QMessageBox.warning(self, "Attenzione", "Seleziona un evento!")
            return
        
        try:
            db = SessionLocal()
            
            # Costruiamo la query base
            query = """
            SELECT i.id, i.numero_gara, p.nome, p.cognome, c.classe, c.categoria,
                   MIN(lt.tempo_ms) as best_time
            FROM iscrizioni i
            JOIN piloti p ON i.pilota_id = p.id
            JOIN categorie c ON i.categoria_id = c.id
            JOIN lap_times lt ON lt.iscrizione_id = i.id
            WHERE i.evento_id = :evento_id AND lt.sessione_tipo = :sessione_tipo
            """
            
            # Aggiungiamo filtro per categoria se selezionata
            if categoria_id and categoria_id > 0:
                query += " AND i.categoria_id = :categoria_id"
            
            query += " GROUP BY i.id ORDER BY best_time"
            
            # Parametri per la query
            params = {
                "evento_id": evento_id,
                "sessione_tipo": session_type
            }
            
            if categoria_id and categoria_id > 0:
                params["categoria_id"] = categoria_id
            
            results = db.execute(query, params).fetchall()
            
            # Puliamo e popoliamo la tabella
            self.results_table.setRowCount(0)
            
            if not results:
                QMessageBox.information(self, "Informazione", "Nessun risultato trovato!")
                return
            
            best_overall = results[0][6]  # Miglior tempo assoluto
            
            for i, result in enumerate(results):
                iscrizione_id, numero_gara, nome, cognome, classe, categoria, best_time = result
                
                row = self.results_table.rowCount()
                self.results_table.insertRow(row)
                
                # Posizione
                self.results_table.setItem(row, 0, QTableWidgetItem(str(i + 1)))
                
                # Numero
                self.results_table.setItem(row, 1, QTableWidgetItem(str(numero_gara)))
                
                # Pilota
                self.results_table.setItem(row, 2, QTableWidgetItem(f"{nome} {cognome}"))
                
                # Categoria
                self.results_table.setItem(row, 3, QTableWidgetItem(f"{classe} {categoria}"))
                
                # Miglior tempo
                if best_time:
                    minuti = best_time // 60000
                    secondi = (best_time % 60000) // 1000
                    millesimi = best_time % 1000
                    tempo_formattato = f"{minuti:02d}:{secondi:02d}.{millesimi:03d}"
                    
                    # Calcoliamo il distacco dal primo
                    if i > 0:
                        distacco = best_time - best_overall
                        distacco_sec = distacco / 1000
                        tempo_formattato += f" (+{distacco_sec:.3f}s)"
                else:
                    tempo_formattato = "-"
                
                self.results_table.setItem(row, 4, QTableWidgetItem(tempo_formattato))
            
            # Ridimensioniamo le colonne
            self.results_table.resizeColumnsToContents()
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante il caricamento classifica: {str(e)}")
        finally:
            db.close()
    
    def print_standings(self):
        """Stampa la classifica"""
        if self.results_table.rowCount() == 0:
            QMessageBox.warning(self, "Attenzione", "Nessun risultato da stampare!")
            return
        
        try:
            # Apriamo il dialogo per salvare il PDF
            fileName, _ = QFileDialog.getSaveFileName(
                self, "Salva Classifica", "", "PDF Files (*.pdf)"
            )
            
            if not fileName:
                return
            
            # Creiamo il writer PDF
            printer = QPrinter()
            printer.setOutputFileName(fileName)
            printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
                        
            # Impostiamo il painter
            painter = QPainter()
            painter.begin(writer)
            
            # Titolo
            font = painter.font()
            font.setPointSize(16)
            painter.setFont(font)
            
            evento_nome = self.event_combo.currentText()
            sessione_tipo = self.session_type_combo.currentText()
            categoria_nome = self.category_combo.currentText()
            
            title = f"Classifica {sessione_tipo} - {evento_nome}"
            if categoria_nome != "Tutte le categorie":
                title += f" - {categoria_nome}"
            
            painter.drawText(100, 100, title)
            
            # Intestazioni tabella
            font.setPointSize(12)
            painter.setFont(font)
            
            col_widths = [50, 60, 200, 150, 200]
            headers = ["Pos", "Num", "Pilota", "Categoria", "Miglior Tempo"]
            
            x_pos = 100
            for i, header in enumerate(headers):
                painter.drawText(x_pos, 150, header)
                x_pos += col_widths[i]
            
            # Dati tabella
            font.setPointSize(10)
            painter.setFont(font)
            
            y_pos = 180
            for row in range(self.results_table.rowCount()):
                x_pos = 100
                for col in range(self.results_table.columnCount()):
                    item = self.results_table.item(row, col)
                    if item:
                        painter.drawText(x_pos, y_pos, item.text())
                    x_pos += col_widths[col]
                y_pos += 30
            
            painter.end()
            
            QMessageBox.information(self, "Successo", f"Classifica salvata in {fileName}")
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante la stampa: {str(e)}")

class RaceStandingsTab(QWidget):
    """Tab per visualizzare le classifiche delle gare"""
    
    def __init__(self):
        super().__init__()
        
        # Layout principale
        layout = QVBoxLayout(self)
        
        # Selettori
        selectors_layout = QFormLayout()
        
        self.event_combo = QComboBox()
        selectors_layout.addRow("Evento:", self.event_combo)
        
        self.session_type_combo = QComboBox()
        self.session_type_combo.addItems(["Gara 1", "Gara 2", "Supercampione"])
        selectors_layout.addRow("Gara:", self.session_type_combo)
        
        self.category_combo = QComboBox()
        selectors_layout.addRow("Categoria:", self.category_combo)
        
        layout.addLayout(selectors_layout)
        
        # Bottoni
        buttons_layout = QHBoxLayout()
        
        self.load_button = QPushButton("Carica Classifica")
        self.load_button.clicked.connect(self.load_standings)
        buttons_layout.addWidget(self.load_button)
        
        self.print_button = QPushButton("Stampa Classifica")
        self.print_button.clicked.connect(self.print_standings)
        buttons_layout.addWidget(self.print_button)
        
        layout.addLayout(buttons_layout)
        
        # Tabella per i risultati
        self.results_table = QTableWidget(0, 6)
        self.results_table.setHorizontalHeaderLabels([
            "Pos", "Num", "Pilota", "Categoria", "Tempo/Distacco", "Punti"
        ])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.results_table)
        
        # Carica eventi
        self.load_events()
        
        # Collega eventi combo
        self.event_combo.currentIndexChanged.connect(self.load_categories)
    
    def load_events(self):
        """Carica gli eventi nel combo box"""
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
    
    def load_categories(self):
        """Carica le categorie per l'evento selezionato"""
        evento_id = self.event_combo.currentData()
        
        if not evento_id:
            return
        
        try:
            db = SessionLocal()
            
            # Otteniamo le categorie uniche degli iscritti
            iscrizioni = db.query(Iscrizione).filter(
                Iscrizione.evento_id == evento_id
            ).all()
            
            categorie_set = set()
            
            for iscrizione in iscrizioni:
                categoria = iscrizione.categoria
                categorie_set.add((categoria.id, f"{categoria.classe} {categoria.categoria}"))
            
            self.category_combo.clear()
            self.category_combo.addItem("Tutte le categorie", 0)
            
            for cat_id, cat_name in sorted(categorie_set, key=lambda x: x[1]):
                self.category_combo.addItem(cat_name, cat_id)
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante il caricamento categorie: {str(e)}")
        finally:
            db.close()
    
    def load_standings(self):
        """Carica la classifica delle gare"""
        evento_id = self.event_combo.currentData()
        session_type = self.session_type_combo.currentText()
        categoria_id = self.category_combo.currentData()
        
        if not evento_id:
            QMessageBox.warning(self, "Attenzione", "Seleziona un evento!")
            return
        
        try:
            db = SessionLocal()
            
            # Costruiamo la query base
            query = """
            SELECT r.posizione, i.numero_gara, p.nome, p.cognome, 
                   c.classe, c.categoria, r.punti, r.best_lap_time,
                   i.id, r.id as risultato_id
            FROM risultati r
            JOIN iscrizioni i ON r.iscrizione_id = i.id
            JOIN piloti p ON i.pilota_id = p.id
            JOIN categorie c ON i.categoria_id = c.id
            JOIN gruppi g ON r.gruppo_id = g.id
            WHERE g.evento_id = :evento_id AND r.sessione_tipo = :sessione_tipo
            """
            
            # Aggiungiamo filtro per categoria se selezionata
            if categoria_id and categoria_id > 0:
                query += " AND i.categoria_id = :categoria_id"
            
            query += " ORDER BY r.posizione"
            
            # Parametri per la query
            params = {
                "evento_id": evento_id,
                "sessione_tipo": session_type
            }
            
            if categoria_id and categoria_id > 0:
                params["categoria_id"] = categoria_id
            
            results = db.execute(query, params).fetchall()
            
            # Puliamo e popoliamo la tabella
            self.results_table.setRowCount(0)
            
            if not results:
                QMessageBox.information(self, "Informazione", "Nessun risultato trovato!")
                return
            
            # Miglior tempo assoluto (se disponibile)
            best_overall = None
            for result in results:
                if result[7]:  # best_lap_time
                    if best_overall is None or result[7] < best_overall:
                        best_overall = result[7]
            
            for result in results:
                posizione, numero_gara, nome, cognome, classe, categoria, punti, best_time, iscrizione_id, risultato_id = result
                
                row = self.results_table.rowCount()
                self.results_table.insertRow(row)
                
                # Posizione
                self.results_table.setItem(row, 0, QTableWidgetItem(str(posizione)))
                
                # Numero
                self.results_table.setItem(row, 1, QTableWidgetItem(str(numero_gara)))
                
                # Pilota
                self.results_table.setItem(row, 2, QTableWidgetItem(f"{nome} {cognome}"))
                
                # Categoria
                self.results_table.setItem(row, 3, QTableWidgetItem(f"{classe} {categoria}"))
                
                # Tempo/Distacco
                if best_time and best_overall:
                    minuti = best_time // 60000
                    secondi = (best_time % 60000) // 1000
                    millesimi = best_time % 1000
                    tempo_formattato = f"{minuti:02d}:{secondi:02d}.{millesimi:03d}"
                    
                    # Calcoliamo il distacco dal primo
                    if posizione > 1:
                        distacco = best_time - best_overall
                        distacco_sec = distacco / 1000
                        tempo_formattato += f" (+{distacco_sec:.3f}s)"
                else:
                    tempo_formattato = "-"
                
                self.results_table.setItem(row, 4, QTableWidgetItem(tempo_formattato))
                
                # Punti
                self.results_table.setItem(row, 5, QTableWidgetItem(str(punti)))
            
            # Ridimensioniamo le colonne
            self.results_table.resizeColumnsToContents()
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante il caricamento classifica: {str(e)}")
        finally:
            db.close()
    
    def print_standings(self):
        """Stampa la classifica"""
        if self.results_table.rowCount() == 0:
            QMessageBox.warning(self, "Attenzione", "Nessun risultato da stampare!")
            return
        
        try:
            # Apriamo il dialogo per salvare il PDF
            fileName, _ = QFileDialog.getSaveFileName(
                self, "Salva Classifica", "", "PDF Files (*.pdf)"
            )
            
            if not fileName:
                return
            
            # Creiamo il writer PDF
            writer = QPdfWriter(fileName)
            writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
            
            # Impostiamo il painter
            painter = QPainter()
            painter.begin(writer)
            
            # Titolo
            font = painter.font()
            font.setPointSize(16)
            painter.setFont(font)
            
            evento_nome = self.event_combo.currentText()
            sessione_tipo = self.session_type_combo.currentText()
            categoria_nome = self.category_combo.currentText()
            
            title = f"Classifica {sessione_tipo} - {evento_nome}"
            if categoria_nome != "Tutte le categorie":
                title += f" - {categoria_nome}"
            
            painter.drawText(100, 100, title)
            
            # Intestazioni tabella
            font.setPointSize(12)
            painter.setFont(font)
            
            col_widths = [50, 60, 200, 150, 200, 60]
            headers = ["Pos", "Num", "Pilota", "Categoria", "Tempo/Distacco", "Punti"]
            
            x_pos = 100
            for i, header in enumerate(headers):
                painter.drawText(x_pos, 150, header)
                x_pos += col_widths[i]
            
            # Dati tabella
            font.setPointSize(10)
            painter.setFont(font)
            
            y_pos = 180
            for row in range(self.results_table.rowCount()):
                x_pos = 100
                for col in range(self.results_table.columnCount()):
                    item = self.results_table.item(row, col)
                    if item:
                        painter.drawText(x_pos, y_pos, item.text())
                    x_pos += col_widths[col]
                y_pos += 30
            
            painter.end()
            
            QMessageBox.information(self, "Successo", f"Classifica salvata in {fileName}")
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante la stampa: {str(e)}")

class DailyStandingsTab(QWidget):
    """Tab per visualizzare le classifiche di giornata"""
    
    def __init__(self):
        super().__init__()
        
        # Layout principale
        layout = QVBoxLayout(self)
        
        # Selettori
        selectors_layout = QFormLayout()
        
        self.event_combo = QComboBox()
        selectors_layout.addRow("Evento:", self.event_combo)
        
        self.category_combo = QComboBox()
        selectors_layout.addRow("Categoria:", self.category_combo)
        
        layout.addLayout(selectors_layout)
        
        # Bottoni
        buttons_layout = QHBoxLayout()
        
        self.load_button = QPushButton("Carica Classifica di Giornata")
        self.load_button.clicked.connect(self.load_standings)
        buttons_layout.addWidget(self.load_button)
        
        self.print_button = QPushButton("Stampa Classifica")
        self.print_button.clicked.connect(self.print_standings)
        buttons_layout.addWidget(self.print_button)
        
        layout.addLayout(buttons_layout)
        
        # Tabella per i risultati
        self.results_table = QTableWidget(0, 6)
        self.results_table.setHorizontalHeaderLabels([
            "Pos", "Num", "Pilota", "Categoria", "Punti Gara 1", "Punti Gara 2", "Totale"
        ])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.results_table)
        
        # Carica eventi
        self.load_events()
        
        # Collega eventi combo
        self.event_combo.currentIndexChanged.connect(self.load_categories)
    
    def load_events(self):
        """Carica gli eventi nel combo box"""
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
    
    def load_categories(self):
        """Carica le categorie per l'evento selezionato"""
        evento_id = self.event_combo.currentData()
        
        if not evento_id:
            return
        
        try:
            db = SessionLocal()
            
            # Otteniamo le categorie uniche degli iscritti
            iscrizioni = db.query(Iscrizione).filter(
                Iscrizione.evento_id == evento_id
            ).all()
            
            categorie_set = set()
            
            for iscrizione in iscrizioni:
                categoria = iscrizione.categoria
                categorie_set.add((categoria.id, f"{categoria.classe} {categoria.categoria}"))
            
            self.category_combo.clear()
            self.category_combo.addItem("Tutte le categorie", 0)
            
            for cat_id, cat_name in sorted(categorie_set, key=lambda x: x[1]):
                self.category_combo.addItem(cat_name, cat_id)
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante il caricamento categorie: {str(e)}")
        finally:
            db.close()
    
    def load_standings(self):
        """Carica la classifica di giornata"""
        evento_id = self.event_combo.currentData()
        categoria_id = self.category_combo.currentData()
        
        if not evento_id:
            QMessageBox.warning(self, "Attenzione", "Seleziona un evento!")
            return
        
        try:
            db = SessionLocal()
            
            # Otteniamo tutti i risultati delle Gara 1 e Gara 2
            query = """
            SELECT i.id as iscrizione_id, i.numero_gara, p.nome, p.cognome,
                   c.classe, c.categoria, r.sessione_tipo, r.punti
            FROM risultati r
            JOIN iscrizioni i ON r.iscrizione_id = i.id
            JOIN piloti p ON i.pilota_id = p.id
            JOIN categorie c ON i.categoria_id = c.id
            JOIN gruppi g ON r.gruppo_id = g.id
            WHERE g.evento_id = :evento_id
            AND r.sessione_tipo IN ('Gara 1', 'Gara 2')
            """
            
            # Aggiungiamo filtro per categoria se selezionata
            if categoria_id and categoria_id > 0:
                query += " AND i.categoria_id = :categoria_id"
            
            # Parametri per la query
            params = {
                "evento_id": evento_id
            }
            
            if categoria_id and categoria_id > 0:
                params["categoria_id"] = categoria_id
            
            results = db.execute(query, params).fetchall()
            
            if not results:
                QMessageBox.information(self, "Informazione", "Nessun risultato trovato!")
                return
            
            # Organizziamo i risultati per pilota
            piloti_risultati = {}
            
            for result in results:
                iscrizione_id, numero_gara, nome, cognome, classe, categoria, sessione_tipo, punti = result
                
                if iscrizione_id not in piloti_risultati:
                    piloti_risultati[iscrizione_id] = {
                        "numero_gara": numero_gara,
                        "nome": nome,
                        "cognome": cognome,
                        "classe": classe,
                        "categoria": categoria,
                        "punti_gara1": 0,
                        "punti_gara2": 0
                    }
                
                if sessione_tipo == "Gara 1":
                    piloti_risultati[iscrizione_id]["punti_gara1"] = punti
                elif sessione_tipo == "Gara 2":
                    piloti_risultati[iscrizione_id]["punti_gara2"] = punti
            
            # Calcoliamo i totali e ordiniamo
            piloti_classifica = []
            for iscrizione_id, dati in piloti_risultati.items():
                dati["totale"] = dati["punti_gara1"] + dati["punti_gara2"]
                piloti_classifica.append((iscrizione_id, dati))
            
            # Ordiniamo per totale punti (decrescente)
            piloti_classifica.sort(key=lambda x: x[1]["totale"], reverse=True)
            
            # Puliamo e popoliamo la tabella
            self.results_table.setColumnCount(7)  # Aggiungiamo una colonna per il totale
            self.results_table.setHorizontalHeaderLabels([
                "Pos", "Num", "Pilota", "Categoria", "Punti Gara 1", "Punti Gara 2", "Totale"
            ])
            self.results_table.setRowCount(0)
            
            for i, (iscrizione_id, dati) in enumerate(piloti_classifica):
                row = self.results_table.rowCount()
                self.results_table.insertRow(row)
                
                # Posizione
                self.results_table.setItem(row, 0, QTableWidgetItem(str(i + 1)))
                
                # Numero
                self.results_table.setItem(row, 1, QTableWidgetItem(str(dati["numero_gara"])))
                
                # Pilota
                self.results_table.setItem(row, 2, QTableWidgetItem(f"{dati['nome']} {dati['cognome']}"))
                
                # Categoria
                self.results_table.setItem(row, 3, QTableWidgetItem(f"{dati['classe']} {dati['categoria']}"))
                
                # Punti Gara 1
                self.results_table.setItem(row, 4, QTableWidgetItem(str(dati["punti_gara1"])))
                
                # Punti Gara 2
                self.results_table.setItem(row, 5, QTableWidgetItem(str(dati["punti_gara2"])))
                
                # Totale
                self.results_table.setItem(row, 6, QTableWidgetItem(str(dati["totale"])))
                
                # Coloriamo di verde il vincitore
                if i == 0:
                    for col in range(self.results_table.columnCount()):
                        item = self.results_table.item(row, col)
                        if item:
                            item.setBackground(QColor(200, 255, 200))  # Verde chiaro
            
            # Ridimensioniamo le colonne
            self.results_table.resizeColumnsToContents()
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante il caricamento classifica: {str(e)}")
        finally:
            db.close()
    
    def print_standings(self):
        """Stampa la classifica di giornata"""
        if self.results_table.rowCount() == 0:
            QMessageBox.warning(self, "Attenzione", "Nessun risultato da stampare!")
            return
        
        try:
            # Apriamo il dialogo per salvare il PDF
            fileName, _ = QFileDialog.getSaveFileName(
                self, "Salva Classifica", "", "PDF Files (*.pdf)"
            )
            
            if not fileName:
                return
            
            # Creiamo il writer PDF
            writer = QPdfWriter(fileName)
            writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
            
            # Impostiamo il painter
            painter = QPainter()
            painter.begin(writer)
            
            # Titolo
            font = painter.font()
            font.setPointSize(16)
            painter.setFont(font)
            
            evento_nome = self.event_combo.currentText()
            categoria_nome = self.category_combo.currentText()
            
            title = f"Classifica di Giornata - {evento_nome}"
            if categoria_nome != "Tutte le categorie":
                title += f" - {categoria_nome}"
            
            painter.drawText(100, 100, title)
            
            # Intestazioni tabella
            font.setPointSize(12)
            painter.setFont(font)
            
            col_widths = [50, 60, 200, 120, 80, 80, 80]
            headers = ["Pos", "Num", "Pilota", "Categoria", "Gara 1", "Gara 2", "Totale"]
            
            x_pos = 100
            for i, header in enumerate(headers):
                painter.drawText(x_pos, 150, header)
                x_pos += col_widths[i]
            
            # Dati tabella
            font.setPointSize(10)
            painter.setFont(font)
            
            y_pos = 180
            for row in range(self.results_table.rowCount()):
                x_pos = 100
                for col in range(self.results_table.columnCount()):
                    item = self.results_table.item(row, col)
                    if item:
                        painter.drawText(x_pos, y_pos, item.text())
                    x_pos += col_widths[col]
                y_pos += 30
            
            painter.end()
            
            QMessageBox.information(self, "Successo", f"Classifica salvata in {fileName}")
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante la stampa: {str(e)}")


class ChampionshipStandingsTab(QWidget):
    """Tab per visualizzare la classifica del campionato"""
    
    def __init__(self):
        super().__init__()
        
        # Layout principale
        layout = QVBoxLayout(self)
        
        # Selettori
        selectors_layout = QFormLayout()
        
        self.category_combo = QComboBox()
        selectors_layout.addRow("Categoria:", self.category_combo)
        
        layout.addLayout(selectors_layout)
        
        # Bottoni
        buttons_layout = QHBoxLayout()
        
        self.load_button = QPushButton("Carica Classifica Campionato")
        self.load_button.clicked.connect(self.load_standings)
        buttons_layout.addWidget(self.load_button)
        
        self.print_button = QPushButton("Stampa Classifica")
        self.print_button.clicked.connect(self.print_standings)
        buttons_layout.addWidget(self.print_button)
        
        layout.addLayout(buttons_layout)
        
        # Tabella per i risultati
        self.results_table = QTableWidget(0, 0)  # Colonne dinamiche in base al numero di eventi
        layout.addWidget(self.results_table)
        
        # Carica categorie
        self.load_categories()
    
    def load_categories(self):
        """Carica le categorie per il campionato"""
        try:
            db = SessionLocal()
            
            # Otteniamo tutte le categorie
            categorie = db.query(Categoria).all()
            
            self.category_combo.clear()
            self.category_combo.addItem("Tutte le categorie", 0)
            
            for categoria in categorie:
                self.category_combo.addItem(f"{categoria.classe} {categoria.categoria}", categoria.id)
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante il caricamento categorie: {str(e)}")
        finally:
            db.close()
    
    def load_standings(self):
        """Carica la classifica del campionato"""
        categoria_id = self.category_combo.currentData()
        
        try:
            db = SessionLocal()
            
            # Otteniamo tutti gli eventi
            eventi = db.query(Evento).order_by(Evento.data).all()
            
            if not eventi:
                QMessageBox.information(self, "Informazione", "Nessun evento trovato!")
                return
            
            # Otteniamo tutti i risultati per tutte le gare (escluso Supercampione)
            query = """
            SELECT i.id as iscrizione_id, i.pilota_id, i.numero_gara, p.nome, p.cognome,
                   c.classe, c.categoria, g.evento_id, e.nome as evento_nome, 
                   r.sessione_tipo, r.punti
            FROM risultati r
            JOIN iscrizioni i ON r.iscrizione_id = i.id
            JOIN piloti p ON i.pilota_id = p.id
            JOIN categorie c ON i.categoria_id = c.id
            JOIN gruppi g ON r.gruppo_id = g.id
            JOIN eventi e ON g.evento_id = e.id
            WHERE r.sessione_tipo IN ('Gara 1', 'Gara 2')
            """
            
            # Aggiungiamo filtro per categoria se selezionata
            if categoria_id and categoria_id > 0:
                query += " AND i.categoria_id = :categoria_id"
            
            # Parametri per la query
            params = {}
            if categoria_id and categoria_id > 0:
                params["categoria_id"] = categoria_id
            
            results = db.execute(query, params).fetchall()
            
            if not results:
                QMessageBox.information(self, "Informazione", "Nessun risultato trovato!")
                return
            
            # Organizziamo i dati per pilota e evento
            piloti = {}
            eventi_map = {}
            
            for result in results:
                iscrizione_id, pilota_id, numero_gara, nome, cognome, classe, categoria, evento_id, evento_nome, sessione_tipo, punti = result
                
                if pilota_id not in piloti:
                    piloti[pilota_id] = {
                        "nome": nome,
                        "cognome": cognome,
                        "classe": classe,
                        "categoria": categoria,
                        "numero_gara": numero_gara,
                        "punti_totali": 0,
                        "eventi": {}
                    }
                
                if evento_id not in eventi_map:
                    eventi_map[evento_id] = evento_nome
                
                if evento_id not in piloti[pilota_id]["eventi"]:
                    piloti[pilota_id]["eventi"][evento_id] = {
                        "Gara 1": 0,
                        "Gara 2": 0,
                        "totale": 0
                    }
                
                # Aggiungiamo i punti
                piloti[pilota_id]["eventi"][evento_id][sessione_tipo] = punti
                piloti[pilota_id]["eventi"][evento_id]["totale"] += punti
                piloti[pilota_id]["punti_totali"] += punti
            
            # Ordiniamo gli eventi per data
            eventi = []
            for evento in sorted(eventi, key=lambda e: e.data):
                if evento.id in eventi_map:
                    eventi.append((evento.id, evento.nome))
            
            # Ordiniamo i piloti per punteggio totale (decrescente)
            piloti_classifica = list(piloti.items())
            piloti_classifica.sort(key=lambda x: x[1]["punti_totali"], reverse=True)
            
            # Prepariamo le colonne per la tabella
            # Colonne base + 2 per ogni evento (una per ciascuna gara) + totale evento + totale campionato
            num_columns = 4 + len(eventi) * 3 + 1
            
            # Impostiamo le colonne
            self.results_table.setColumnCount(num_columns)
            
            # Prepariamo le intestazioni
            headers = ["Pos", "Num", "Pilota", "Categoria"]
            
            for evento_id, evento_nome in eventi:
                evento_nome_corto = evento_nome.split("(")[0].strip()  # Prendiamo solo la prima parte del nome
                headers.append(f"{evento_nome_corto} G1")
                headers.append(f"{evento_nome_corto} G2")
                headers.append(f"{evento_nome_corto} Tot")
            
            headers.append("Totale")
            
            self.results_table.setHorizontalHeaderLabels(headers)
            
            # Puliamo e popoliamo la tabella
            self.results_table.setRowCount(0)
            
            for i, (pilota_id, dati) in enumerate(piloti_classifica):
                row = self.results_table.rowCount()
                self.results_table.insertRow(row)
                
                # Posizione
                self.results_table.setItem(row, 0, QTableWidgetItem(str(i + 1)))
                
                # Numero
                self.results_table.setItem(row, 1, QTableWidgetItem(str(dati["numero_gara"])))
                
                # Pilota
                self.results_table.setItem(row, 2, QTableWidgetItem(f"{dati['nome']} {dati['cognome']}"))
                
                # Categoria
                self.results_table.setItem(row, 3, QTableWidgetItem(f"{dati['classe']} {dati['categoria']}"))
                
                # Per ogni evento, inseriamo i punteggi
                col = 4
                for evento_id, _ in eventi:
                    # Se il pilota ha partecipato all'evento
                    if evento_id in dati["eventi"]:
                        evento_dati = dati["eventi"][evento_id]
                        
                        # Gara 1
                        self.results_table.setItem(row, col, QTableWidgetItem(str(evento_dati["Gara 1"])))
                        col += 1
                        
                        # Gara 2
                        self.results_table.setItem(row, col, QTableWidgetItem(str(evento_dati["Gara 2"])))
                        col += 1
                        
                        # Totale evento
                        self.results_table.setItem(row, col, QTableWidgetItem(str(evento_dati["totale"])))
                        col += 1
                    else:
                        # Il pilota non ha partecipato a questo evento
                        self.results_table.setItem(row, col, QTableWidgetItem("-"))
                        col += 1
                        self.results_table.setItem(row, col, QTableWidgetItem("-"))
                        col += 1
                        self.results_table.setItem(row, col, QTableWidgetItem("-"))
                        col += 1
                
                # Totale campionato
                self.results_table.setItem(row, col, QTableWidgetItem(str(dati["punti_totali"])))
                
                # Coloriamo di verde il leader del campionato
                if i == 0:
                    for col in range(self.results_table.columnCount()):
                        item = self.results_table.item(row, col)
                        if item:
                            item.setBackground(QColor(200, 255, 200))  # Verde chiaro
            
            # Ridimensioniamo le colonne
            self.results_table.resizeColumnsToContents()
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante il caricamento classifica: {str(e)}")
        finally:
            db.close()
    
    def print_standings(self):
        """Stampa la classifica del campionato"""
        if self.results_table.rowCount() == 0:
            QMessageBox.warning(self, "Attenzione", "Nessun risultato da stampare!")
            return
        
        try:
            # Apriamo il dialogo per salvare il PDF
            fileName, _ = QFileDialog.getSaveFileName(
                self, "Salva Classifica", "", "PDF Files (*.pdf)"
            )
            
            if not fileName:
                return
            
            # Creiamo il writer PDF
            writer = QPdfWriter(fileName)
            writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
            writer.setPageOrientation(QPageLayout.Orientation.Landscape)  # Orizzontale per più colonne
            
            # Impostiamo il painter
            painter = QPainter()
            painter.begin(writer)
            
            # Titolo
            font = painter.font()
            font.setPointSize(16)
            painter.setFont(font)
            
            categoria_nome = self.category_combo.currentText()
            
            title = "Classifica Campionato"
            if categoria_nome != "Tutte le categorie":
                title += f" - {categoria_nome}"
            
            painter.drawText(100, 100, title)
            
            # Intestazioni tabella
            font.setPointSize(8)  # Testo piccolo per far stare più colonne
            painter.setFont(font)
            
            # Colonne base
            col_widths = [30, 40, 120, 80]  # Pos, Num, Pilota, Categoria
            
            # Aggiungiamo larghezze per le colonne degli eventi
            eventi_cols = (self.results_table.columnCount() - 5) // 3
            for _ in range(eventi_cols):
                col_widths.extend([40, 40, 40])  # G1, G2, Tot per ogni evento
            
            col_widths.append(50)  # Totale campionato
            
            # Intestazioni
            x_pos = 50
            for col in range(self.results_table.columnCount()):
                header = self.results_table.horizontalHeaderItem(col).text()
                painter.drawText(x_pos, 150, header)
                x_pos += col_widths[col]
            
            # Dati tabella
            y_pos = 180
            for row in range(self.results_table.rowCount()):
                x_pos = 50
                for col in range(self.results_table.columnCount()):
                    item = self.results_table.item(row, col)
                    if item:
                        painter.drawText(x_pos, y_pos, item.text())
                    x_pos += col_widths[col]
                y_pos += 20
            
            painter.end()
            
            QMessageBox.information(self, "Successo", f"Classifica salvata in {fileName}")
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante la stampa: {str(e)}")
    
class StatsTab(QWidget):
    """Tab per visualizzare statistiche"""
    
    def __init__(self):
        super().__init__()
        
        # Layout principale
        layout = QVBoxLayout(self)
        
        # Selettori
        selectors_layout = QFormLayout()
        
        self.stat_type_combo = QComboBox()
        self.stat_type_combo.addItems(["Statistiche Marche Moto", "Statistiche Moto Club"])
        selectors_layout.addRow("Tipo statistica:", self.stat_type_combo)
        
        self.category_combo = QComboBox()
        selectors_layout.addRow("Categoria:", self.category_combo)
        
        layout.addLayout(selectors_layout)
        
        # Bottoni
        buttons_layout = QHBoxLayout()
        
        self.load_button = QPushButton("Carica Statistiche")
        self.load_button.clicked.connect(self.load_stats)
        buttons_layout.addWidget(self.load_button)
        
        self.print_button = QPushButton("Stampa Statistiche")
        self.print_button.clicked.connect(self.print_stats)
        buttons_layout.addWidget(self.print_button)
        
        layout.addLayout(buttons_layout)
        
        # Contenitore per il grafico
        self.chart_widget = QWidget()
        self.chart_layout = QVBoxLayout(self.chart_widget)
        layout.addWidget(self.chart_widget)
        
        # Tabella per i dati
        self.data_table = QTableWidget(0, 3)
        self.data_table.setHorizontalHeaderLabels([
            "Marca/Moto Club", "Punti Totali", "% sul Totale"
        ])
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.data_table)
        
        # Carica categorie
        self.load_categories()
    
    def load_categories(self):
        """Carica le categorie"""
        try:
            db = SessionLocal()
            
            # Otteniamo tutte le categorie
            categorie = db.query(Categoria).all()
            
            self.category_combo.clear()
            self.category_combo.addItem("Tutte le categorie", 0)
            
            for categoria in categorie:
                self.category_combo.addItem(f"{categoria.classe} {categoria.categoria}", categoria.id)
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante il caricamento categorie: {str(e)}")
        finally:
            db.close()
    
    def load_stats(self):
        """Carica le statistiche selezionate"""
        stat_type = self.stat_type_combo.currentText()
        categoria_id = self.category_combo.currentData()
        
        try:
            db = SessionLocal()
            
            # Costruiamo la query base
            if "Marche Moto" in stat_type:
                # Statistiche per marca moto
                query = """
                SELECT p.marca_moto, SUM(r.punti) as totale_punti
                FROM risultati r
                JOIN iscrizioni i ON r.iscrizione_id = i.id
                JOIN piloti p ON i.pilota_id = p.id
                JOIN gruppi g ON r.gruppo_id = g.id
                WHERE r.sessione_tipo IN ('Gara 1', 'Gara 2')
                """
                
                group_by = "p.marca_moto"
                x_label = "Marca Moto"
                
            else:
                # Statistiche per moto club
                query = """
                SELECT p.moto_club, SUM(r.punti) as totale_punti
                FROM risultati r
                JOIN iscrizioni i ON r.iscrizione_id = i.id
                JOIN piloti p ON i.pilota_id = p.id
                JOIN gruppi g ON r.gruppo_id = g.id
                WHERE r.sessione_tipo IN ('Gara 1', 'Gara 2')
                """
                
                group_by = "p.moto_club"
                x_label = "Moto Club"
            
            # Aggiungiamo filtro per categoria se selezionata
            if categoria_id and categoria_id > 0:
                query += " AND i.categoria_id = :categoria_id"
            
            # Completiamo la query
            query += f" GROUP BY {group_by} HAVING totale_punti > 0 ORDER BY totale_punti DESC"
            
            # Parametri per la query
            params = {}
            if categoria_id and categoria_id > 0:
                params["categoria_id"] = categoria_id
            
            results = db.execute(query, params).fetchall()
            
            if not results:
                QMessageBox.information(self, "Informazione", "Nessun risultato trovato!")
                return
            
            # Calcoliamo il totale dei punti
            total_points = sum(r[1] for r in results)
            
            # Preparare i dati per il grafico
            labels = []
            values = []
            percentages = []
            
            # Limitiamo a 10 elementi per il grafico (le prime 10)
            top_results = results[:10]
            
            for label, value in top_results:
                if not label:  # Gestiamo il caso di valori nulli
                    label = "Non specificato"
                labels.append(label)
                values.append(value)
                percentage = (value / total_points) * 100
                percentages.append(percentage)
            
            # Puliamo eventuali grafici precedenti
            for i in reversed(range(self.chart_layout.count())): 
                self.chart_layout.itemAt(i).widget().setParent(None)
            
            # Creiamo il grafico
            figure = plt.figure(figsize=(8, 4))
            ax = figure.add_subplot(111)
            
            # Creiamo il grafico a barre
            bars = ax.bar(labels, values, color='skyblue')
            
            # Aggiungiamo le etichette
            ax.set_title(f"Statistiche per {x_label}")
            ax.set_ylabel('Punti')
            ax.set_xlabel(x_label)
            
            # Ruotiamo le etichette sull'asse x per renderle più leggibili
            plt.xticks(rotation=45, ha='right')
            
            # Aggiungiamo i valori sopra le barre
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f'{height}',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3),  # 3 punti sopra la barra
                            textcoords="offset points",
                            ha='center', va='bottom')
            
            plt.tight_layout()
            
            # Aggiungiamo il grafico al layout
            canvas = FigureCanvas(figure)
            self.chart_layout.addWidget(canvas)
            
            # Aggiorniamo la tabella con i dati completi
            self.data_table.setRowCount(0)
            
            for i, (label, value) in enumerate(results):
                if not label:  # Gestiamo il caso di valori nulli
                    label = "Non specificato"
                    
                row = self.data_table.rowCount()
                self.data_table.insertRow(row)
                
                # Label
                self.data_table.setItem(row, 0, QTableWidgetItem(label))
                
                # Punti
                self.data_table.setItem(row, 1, QTableWidgetItem(str(value)))
                
                # Percentuale
                percentage = (value / total_points) * 100
                self.data_table.setItem(row, 2, QTableWidgetItem(f"{percentage:.2f}%"))
                
                # Coloriamo le prime 3 posizioni
                if i < 3:
                    colors = [QColor(255, 215, 0),  # Oro
                              QColor(192, 192, 192),  # Argento
                              QColor(205, 127, 50)]  # Bronzo
                    for col in range(self.data_table.columnCount()):
                        item = self.data_table.item(row, col)
                        if item:
                            item.setBackground(colors[i])
            
            # Ridimensioniamo le colonne
            self.data_table.resizeColumnsToContents()
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante il caricamento statistiche: {str(e)}")
        finally:
            db.close()
    
    def print_stats(self):
        """Stampa le statistiche"""
        if self.data_table.rowCount() == 0:
            QMessageBox.warning(self, "Attenzione", "Nessun dato da stampare!")
            return
        
        try:
            # Apriamo il dialogo per salvare il PDF
            fileName, _ = QFileDialog.getSaveFileName(
                self, "Salva Statistiche", "", "PDF Files (*.pdf)"
            )
            
            if not fileName:
                return
            
            # Creiamo il writer PDF
            writer = QPdfWriter(fileName)
            writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
            
            # Impostiamo il painter
            painter = QPainter()
            painter.begin(writer)
            
            # Titolo
            font = painter.font()
            font.setPointSize(16)
            painter.setFont(font)
            
            stat_type = self.stat_type_combo.currentText()
            categoria_nome = self.category_combo.currentText()
            
            title = stat_type
            if categoria_nome != "Tutte le categorie":
                title += f" - {categoria_nome}"
            
            painter.drawText(100, 100, title)
            
            # Intestazioni tabella
            font.setPointSize(12)
            painter.setFont(font)
            
            col_widths = [200, 100, 100]
            headers = ["Marca/Moto Club", "Punti Totali", "% sul Totale"]
            
            x_pos = 100
            for i, header in enumerate(headers):
                painter.drawText(x_pos, 150, header)
                x_pos += col_widths[i]
            
            # Dati tabella
            font.setPointSize(10)
            painter.setFont(font)
            
            y_pos = 180
            for row in range(self.data_table.rowCount()):
                x_pos = 100
                for col in range(self.data_table.columnCount()):
                    item = self.data_table.item(row, col)
                    if item:
                        painter.drawText(x_pos, y_pos, item.text())
                    x_pos += col_widths[col]
                y_pos += 30
            
            painter.end()
            
            QMessageBox.information(self, "Successo", f"Statistiche salvate in {fileName}")
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante la stampa: {str(e)}")
