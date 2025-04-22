# ui/timing.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLabel, QLineEdit, QPushButton, QComboBox, 
    QTableWidget, QTableWidgetItem, QGroupBox, 
    QSpinBox, QMessageBox, QSplitter
)
from PyQt6.QtCore import Qt, QTimer, QDateTime, QTime

from database.connection import SessionLocal
from database.models import Evento, Iscrizione, Pilota

class TimingModule(QWidget):
    def __init__(self):
        super().__init__()
        
        # Layout principale
        self.layout = QVBoxLayout(self)
        
        # Titolo
        self.title_label = QLabel("Sistema di Cronometraggio")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.layout.addWidget(self.title_label)
        
        # Selettore evento e sessione
        self.selection_layout = QFormLayout()
        
        self.event_combo = QComboBox()
        self.selection_layout.addRow("Evento:", self.event_combo)
        
        self.session_type_combo = QComboBox()
        self.session_type_combo.addItems(["Prove Libere", "Qualifiche", "Gara 1", "Gara 2", "Supercampione"])
        self.selection_layout.addRow("Tipo Sessione:", self.session_type_combo)
        
        self.category_combo = QComboBox()
        self.selection_layout.addRow("Categoria:", self.category_combo)
        
        self.layout.addLayout(self.selection_layout)
        
        # Pannello di controllo sessione
        self.session_control = SessionControlPanel()
        self.layout.addWidget(self.session_control)
        
        # Splitter per organizzare lo spazio
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Inserimento tempi manuale
        self.manual_timing = ManualTimingPanel()
        self.splitter.addWidget(self.manual_timing)
        
        # Visualizzazione classifica
        self.standings = SessionStandingsPanel()
        self.splitter.addWidget(self.standings)
        
        self.layout.addWidget(self.splitter)
        
        # Inserimento numero di gara per tempo manuale
        self.rider_input_layout = QHBoxLayout()
        
        self.rider_number_label = QLabel("Numero Pilota:")
        self.rider_input_layout.addWidget(self.rider_number_label)
        
        self.rider_number_input = QSpinBox()
        self.rider_number_input.setMinimum(1)
        self.rider_number_input.setMaximum(999)
        self.rider_input_layout.addWidget(self.rider_number_input)
        
        self.record_lap_button = QPushButton("Registra Passaggio")
        self.record_lap_button.clicked.connect(self.record_lap)
        self.rider_input_layout.addWidget(self.record_lap_button)
        
        self.layout.addLayout(self.rider_input_layout)
        
        # Carica eventi nel combo
        self.load_events_combo()
        
        # Collega eventi combo
        self.event_combo.currentIndexChanged.connect(self.load_categories_combo)
    
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
    
    def load_categories_combo(self):
        """Carica le categorie per l'evento selezionato"""
        if self.event_combo.count() == 0:
            return
        
        evento_id = self.event_combo.currentData()
        if not evento_id:
            return
        
        try:
            db = SessionLocal()
            
            # Query per ottenere categorie uniche con piloti iscritti
            categorie = db.query(Iscrizione.categoria_id, Iscrizione.categoria.classe, Iscrizione.categoria.categoria)\
                          .filter(Iscrizione.evento_id == evento_id)\
                          .distinct()\
                          .all()
            
            self.category_combo.clear()
            
            for cat_id, classe, categoria in categorie:
                self.category_combo.addItem(f"{classe} {categoria}", cat_id)
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante il caricamento categorie: {str(e)}")
        finally:
            db.close()
    
    def record_lap(self):
        """Registra un passaggio manuale"""
        rider_number = self.rider_number_input.value()
        current_time = QDateTime.currentDateTime()
        
        # Seleziona evento, tipo sessione e categoria
        evento_id = self.event_combo.currentData()
        sessione_tipo = self.session_type_combo.currentText()
        
        if not evento_id:
            QMessageBox.warning(self, "Avviso", "Selezionare un evento!")
            return
        
        # Trova pilota dal numero di gara
        try:
            db = SessionLocal()
            iscrizione = db.query(Iscrizione).filter(
                Iscrizione.numero_gara == rider_number,
                Iscrizione.evento_id == evento_id
            ).first()
            
            if not iscrizione:
                QMessageBox.warning(self, "Avviso", f"Nessun pilota trovato con il numero {rider_number} per questo evento!")
                return
            
            # Calcola il numero del giro per questo pilota e sessione
            ultimo_giro = db.query(LapTime).filter(
                LapTime.iscrizione_id == iscrizione.id,
                LapTime.sessione_tipo == sessione_tipo
            ).order_by(LapTime.numero_giro.desc()).first()
            
            numero_giro = 1
            if ultimo_giro:
                numero_giro = ultimo_giro.numero_giro + 1
            
            # Calcola il tempo trascorso dall'inizio della sessione
            tempo_ms = self.session_control.get_elapsed_time()
            
            # Crea nuovo record tempo giro
            nuovo_tempo = LapTime(
                iscrizione_id=iscrizione.id,
                sessione_tipo=sessione_tipo,
                numero_giro=numero_giro,
                tempo_ms=tempo_ms,
                timestamp=current_time
            )
            
            db.add(nuovo_tempo)
            db.commit()
            
            # Aggiorna la visualizzazione dei tempi
            self.manual_timing.add_lap_time(
                rider_number, 
                f"{iscrizione.pilota.nome} {iscrizione.pilota.cognome}", 
                current_time
            )
            
            # Aggiorna la classifica provvisoria
            self.standings.refresh_standings()
            
            # Mostra messaggio di conferma
            QMessageBox.information(
                self, 
                "Passaggio Registrato", 
                f"Registrato passaggio di {iscrizione.pilota.nome} {iscrizione.pilota.cognome} - Giro {numero_giro} - Tempo: {nuovo_tempo.formato_tempo()}"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante la registrazione del passaggio: {str(e)}")
        finally:
            db.close()

class SessionControlPanel(QGroupBox):
    def __init__(self):
        super().__init__("Controllo Sessione")
        
        # Layout principale
        self.layout = QHBoxLayout(self)
        
        # Timer display
        self.timer_display = QLabel("00:00.000")
        self.timer_display.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.layout.addWidget(self.timer_display)
        
        # Controlli timer
        self.timer_controls = QHBoxLayout()
        
        self.start_button = QPushButton("Avvia")
        self.start_button.clicked.connect(self.start_session)
        self.timer_controls.addWidget(self.start_button)
        
        self.pause_button = QPushButton("Pausa")
        self.pause_button.clicked.connect(self.pause_session)
        self.pause_button.setEnabled(False)
        self.timer_controls.addWidget(self.pause_button)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_session)
        self.stop_button.setEnabled(False)
        self.timer_controls.addWidget(self.stop_button)
        
        self.layout.addLayout(self.timer_controls)
        
        # Status display
        self.status_label = QLabel("Sessione non avviata")
        self.layout.addWidget(self.status_label)
        
        # Timer per aggiornare l'orologio
        self.session_timer = QTimer()
        self.session_timer.timeout.connect(self.update_timer)
        self.session_running = False
        self.session_start_time = None
        self.elapsed_time = 0
    
    def start_session(self):
        """Avvia la sessione di cronometraggio"""
        if not self.session_running:
            self.session_start_time = QDateTime.currentDateTime()
            self.session_timer.start(100)  # Aggiorna ogni 100ms
            self.session_running = True
            
            self.start_button.setEnabled(False)
            self.pause_button.setEnabled(True)
            self.stop_button.setEnabled(True)
            
            self.status_label.setText("Sessione in corso")
    
    def pause_session(self):
        """Mette in pausa la sessione"""
        if self.session_running:
            self.session_timer.stop()
            self.elapsed_time = self.get_elapsed_time()
            self.session_running = False
            
            self.start_button.setEnabled(True)
            self.pause_button.setEnabled(False)
            
            self.status_label.setText("Sessione in pausa")
        else:
            self.session_start_time = QDateTime.currentDateTime().addMSecs(-self.elapsed_time)
            self.session_timer.start(100)
            self.session_running = True
            
            self.start_button.setEnabled(False)
            self.pause_button.setEnabled(True)
            
            self.status_label.setText("Sessione in corso")
    
    def stop_session(self):
        """Ferma la sessione"""
        self.session_timer.stop()
        self.session_running = False
        
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        
        # Finalizza i risultati
        final_time = self.get_elapsed_time()
        self.status_label.setText(f"Sessione terminata - Durata: {self.format_time(final_time)}")
        
        # Qui si potrebbero salvare i risultati finali
    
    def update_timer(self):
        """Aggiorna il display del timer"""
        if self.session_running:
            elapsed = self.get_elapsed_time()
            self.timer_display.setText(self.format_time(elapsed))
    
    def get_elapsed_time(self):
        """Calcola il tempo trascorso in millisecondi"""
        if self.session_start_time:
            return self.session_start_time.msecsTo(QDateTime.currentDateTime())
        return 0
    
    def format_time(self, msecs):
        """Formatta il tempo in millisecondi come MM:SS.mmm"""
        secs = msecs // 1000
        mins = secs // 60
        secs %= 60
        msecs %= 1000
        return f"{mins:02d}:{secs:02d}.{msecs:03d}"

class ManualTimingPanel(QGroupBox):
    def __init__(self):
        super().__init__("Tempi Registrati")
        
        # Layout principale
        self.layout = QVBoxLayout(self)
        
        # Tabella tempi
        self.lap_times_table = QTableWidget(0, 4)
        self.lap_times_table.setHorizontalHeaderLabels(
            ["Numero", "Pilota", "Tempo", "Giro"]
        )
        self.layout.addWidget(self.lap_times_table)
        
        # Dizionario per tenere traccia dei giri per pilota
        self.rider_laps = {}
    
    def add_lap_time(self, number, rider_name, timestamp):
        """Aggiunge un tempo sul giro alla tabella"""
        # Incrementa il conteggio dei giri per questo pilota
        if number in self.rider_laps:
            self.rider_laps[number] += 1
        else:
            self.rider_laps[number] = 1
        
        # Calcola nuovo tempo e migliore tempo
        lap_count = self.rider_laps[number]
        
        # Aggiunge una riga alla tabella
        row = self.lap_times_table.rowCount()
        self.lap_times_table.insertRow(row)
        
        self.lap_times_table.setItem(row, 0, QTableWidgetItem(str(number)))
        self.lap_times_table.setItem(row, 1, QTableWidgetItem(rider_name))
        self.lap_times_table.setItem(row, 2, QTableWidgetItem(timestamp.toString("HH:mm:ss.zzz")))
        self.lap_times_table.setItem(row, 3, QTableWidgetItem(str(lap_count)))
        
        # Scorri alla riga appena aggiunta
        self.lap_times_table.scrollToItem(self.lap_times_table.item(row, 0))
        
        # Ridimensiona colonne
        self.lap_times_table.resizeColumnsToContents()

class SessionStandingsPanel(QGroupBox):
    def __init__(self):
        super().__init__("Classifica Sessione")
        
        # Layout principale
        self.layout = QVBoxLayout(self)
        
        # Tabella classifica
        self.standings_table = QTableWidget(0, 5)
        self.standings_table.setHorizontalHeaderLabels(
            ["Pos", "Numero", "Pilota", "Miglior Tempo", "Diff"]
        )
        self.layout.addWidget(self.standings_table)
        
        # Bottone aggiorna
        self.refresh_button = QPushButton("Aggiorna Classifica")
        self.refresh_button.clicked.connect(self.refresh_standings)
        self.layout.addWidget(self.refresh_button)
    
    def refresh_standings(self):
        """Aggiorna la classifica della sessione"""
        parent = self.parent()
        if not hasattr(parent, "event_combo") or not hasattr(parent, "session_type_combo"):
            return
        
        evento_id = parent.event_combo.currentData()
        sessione_tipo = parent.session_type_combo.currentText()
        
        if not evento_id:
            return
        
        try:
            db = SessionLocal()
            
            # Query per ottenere i migliori tempi per ciascun pilota
            query = """
            SELECT i.numero_gara, p.nome, p.cognome, MIN(lt.tempo_ms) as best_time, i.id
            FROM iscrizioni i
            JOIN piloti p ON i.pilota_id = p.id
            JOIN lap_times lt ON lt.iscrizione_id = i.id
            WHERE i.evento_id = :evento_id AND lt.sessione_tipo = :sessione_tipo
            GROUP BY i.id
            ORDER BY best_time
            """
            
            result = db.execute(query, {"evento_id": evento_id, "sessione_tipo": sessione_tipo})
            
            # Pulisci tabella
            self.standings_table.setRowCount(0)
            
            best_time = None
            position = 0
            
            # Popola tabella con risultati
            for row_data in result:
                position += 1
                numero_gara, nome, cognome, tempo_ms, iscrizione_id = row_data
                
                # Formatta tempo
                secs = tempo_ms // 1000
                mins = secs // 60
                secs %= 60
                msecs = tempo_ms % 1000
                tempo_formattato = f"{mins:02d}:{secs:02d}.{msecs:03d}"
                
                # Calcola differenza dal migliore
                if position == 1:
                    best_time = tempo_ms
                    diff = "-"
                else:
                    diff_ms = tempo_ms - best_time
                    diff_secs = diff_ms // 1000
                    diff_msecs = diff_ms % 1000
                    diff = f"+{diff_secs:01d}.{diff_msecs:03d}"
                
                # Aggiungi riga alla tabella
                row = self.standings_table.rowCount()
                self.standings_table.insertRow(row)
                
                self.standings_table.setItem(row, 0, QTableWidgetItem(str(position)))
                self.standings_table.setItem(row, 1, QTableWidgetItem(str(numero_gara)))
                self.standings_table.setItem(row, 2, QTableWidgetItem(f"{nome} {cognome}"))
                self.standings_table.setItem(row, 3, QTableWidgetItem(tempo_formattato))
                self.standings_table.setItem(row, 4, QTableWidgetItem(diff))
            
            # Ridimensiona colonne
            self.standings_table.resizeColumnsToContents()
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante l'aggiornamento classifiche: {str(e)}")
        finally:
            db.close()