# ui/timing_system.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLabel, QLineEdit, QPushButton, QComboBox, 
    QTableWidget, QTableWidgetItem, QGroupBox, 
    QSpinBox, QMessageBox, QTabWidget, QSplitter,
    QRadioButton, QButtonGroup, QDialog, QDialogButtonBox
)
from PyQt6.QtCore import Qt, QTimer, QDateTime, QTime, QElapsedTimer
from PyQt6.QtGui import QIntValidator
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtCore import Qt, QTimer, QDateTime, QTime, QElapsedTimer, pyqtSignal
from database.connection import SessionLocal
from database.models import Evento, Gruppo, PartecipazioneGruppo, Iscrizione, Pilota, LapTime
from PyQt6.QtWidgets import QApplication, QMainWindow, QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget

class TimingSystem(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Layout principale
        self.layout = QVBoxLayout(self)
        
        # Titolo
        self.title_label = QLabel("Sistema di Cronometraggio - Prove Libere")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.layout.addWidget(self.title_label)
        
        # Selettore del metodo di cronometraggio
        self.timing_method_group = QGroupBox("Metodo di Cronometraggio")
        timing_method_layout = QHBoxLayout()
        
        self.method_button_group = QButtonGroup(self)
        
        self.manual_method_radio = QRadioButton("Inserimento Manuale")
        self.manual_method_radio.setChecked(True)
        self.method_button_group.addButton(self.manual_method_radio)
        timing_method_layout.addWidget(self.manual_method_radio)
        
        self.transponder_method_radio = QRadioButton("Sistema Transponder")
        self.method_button_group.addButton(self.transponder_method_radio)
        timing_method_layout.addWidget(self.transponder_method_radio)
        
        self.camera_method_radio = QRadioButton("Riconoscimento Video")
        self.method_button_group.addButton(self.camera_method_radio)
        timing_method_layout.addWidget(self.camera_method_radio)
        
        self.timing_method_group.setLayout(timing_method_layout)
        self.layout.addWidget(self.timing_method_group)
        
        # Collega il cambio di metodo all'aggiornamento dell'interfaccia
        self.method_button_group.buttonClicked.connect(self.update_timing_interface)
        
        # Selettore evento e gruppo
        self.selection_layout = QFormLayout()
        
        self.event_combo = QComboBox()
        self.selection_layout.addRow("Evento:", self.event_combo)
        
        self.group_combo = QComboBox()
        self.selection_layout.addRow("Gruppo:", self.group_combo)
        # Aggiungiamo un selettore per il tipo di sessione
        self.session_type_combo = QComboBox()
        self.session_type_combo.addItems(["Prove Libere", "Qualifiche", "Gara 1", "Gara 2"])
        self.selection_layout.addRow("Tipo Sessione:", self.session_type_combo)
        
        self.layout.addLayout(self.selection_layout)
        
        # Bottone per caricare i piloti del gruppo
        self.load_button = QPushButton("Carica Piloti del Gruppo")
        self.load_button.clicked.connect(self.load_group_riders)
        self.layout.addWidget(self.load_button)
        
        # Pannello di controllo sessione
        self.session_control = SessionControlPanel()
        self.session_control.session_finished.connect(self.on_session_finished)
        self.layout.addWidget(self.session_control)
        
        # Splitter per organizzare lo spazio
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Pannello di cronometraggio
        self.timing_panel = ManualTimingPanel()
        self.splitter.addWidget(self.timing_panel)
        
        # Visualizzazione risultati live
        self.results_panel = LiveResultsPanel()
        self.splitter.addWidget(self.results_panel)
        
        self.layout.addWidget(self.splitter)
        
        # Carica eventi nel combo
        self.load_events_combo()
        
        # Collega eventi combo
        self.event_combo.currentIndexChanged.connect(self.load_groups_combo)
    
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
    
    def load_groups_combo(self):
        """Carica i gruppi per l'evento selezionato"""
        if self.event_combo.count() == 0:
            return
        
        evento_id = self.event_combo.currentData()
        if not evento_id:
            return
        
        try:
            db = SessionLocal()
            
            # Ottieni tutti i gruppi per "Prove Libere" di questo evento
            gruppi = db.query(Gruppo).filter(
                Gruppo.evento_id == evento_id,
                Gruppo.tipo_sessione == "Prove Libere"
            ).all()
            
            self.group_combo.clear()
            for gruppo in gruppi:
                self.group_combo.addItem(f"{gruppo.nome}", gruppo.id)
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante il caricamento gruppi: {str(e)}")
        finally:
            db.close()
    
    def load_group_riders(self):
        """Carica i piloti del gruppo selezionato"""
        if self.group_combo.count() == 0:
            QMessageBox.warning(self, "Attenzione", "Nessun gruppo disponibile!")
            return
        
        gruppo_id = self.group_combo.currentData()
        
        if not gruppo_id:
            return
        
        try:
            db = SessionLocal()
            
            # Ottieni tutte le partecipazioni al gruppo
            partecipazioni = db.query(PartecipazioneGruppo).filter(
                PartecipazioneGruppo.gruppo_id == gruppo_id
            ).all()
            
            # Prepara una lista di piloti per il pannello di cronometraggio
            riders = []
            
            for partecipazione in partecipazioni:
                iscrizione = partecipazione.iscrizione
                pilota = iscrizione.pilota
                
                rider_info = {
                    "id": iscrizione.id,
                    "numero": iscrizione.numero_gara,
                    "nome": pilota.nome,
                    "cognome": pilota.cognome,
                    "transponder": iscrizione.transponder_id if hasattr(iscrizione, "transponder_id") else None
                }
                
                riders.append(rider_info)
            
            # Passare i piloti al pannello di cronometraggio
            self.timing_panel.load_riders(riders)
            self.results_panel.load_riders(riders)
            
            # Resetta il timer della sessione
            self.session_control.reset_session()
            
            QMessageBox.information(self, "Piloti Caricati", f"Caricati {len(riders)} piloti per il gruppo selezionato")
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante il caricamento piloti: {str(e)}")
        finally:
            db.close()
    
    def update_timing_interface(self, button):
        """Aggiorna l'interfaccia in base al metodo di cronometraggio selezionato"""
        # Rimuovi il pannello attuale
        if hasattr(self, 'timing_panel'):
            self.splitter.replaceWidget(0, QWidget())  # Sostituisci con un widget vuoto
        
        # Crea il nuovo pannello in base alla selezione
        if button == self.manual_method_radio:
            self.timing_panel = ManualTimingPanel()
        elif button == self.transponder_method_radio:
            self.timing_panel = TransponderTimingPanel()
        elif button == self.camera_method_radio:
            self.timing_panel = VideoRecognitionPanel()
        
        # Aggiungi il nuovo pannello allo splitter
        self.splitter.insertWidget(0, self.timing_panel)
        
        # Se ci sono già rider caricati, ricaricarli nel nuovo pannello
        if hasattr(self, 'riders') and self.riders:
            self.timing_panel.load_riders(self.riders)
    
    def on_session_finished(self):
        """Gestisce la fine della sessione di prove libere"""
        # Salva i risultati nel database
        self.save_session_results()
        
        # Mostra la classifica finale
        self.show_final_results()
    
    def save_session_results(self):
        """Salva i risultati della sessione nel database"""
        gruppo_id = self.group_combo.currentData()
        if not gruppo_id:
            return
        
        try:
            db = SessionLocal()
            
            # Ottieni i risultati dal pannello di cronometraggio
            results = self.results_panel.get_results()
            
            # Salva ogni tempo sul giro nel database
            for rider_id, lap_times in results.items():
                for lap_num, lap_data in enumerate(lap_times, 1):
                    # Crea un nuovo record LapTime
                    new_lap = LapTime(
                        iscrizione_id=rider_id,
                        sessione_tipo="Prove Libere",
                        numero_giro=lap_num,
                        tempo_ms=lap_data["time_ms"],
                        timestamp=lap_data["timestamp"]
                    )
                    db.add(new_lap)
            
            db.commit()
            QMessageBox.information(self, "Dati Salvati", "Tutti i tempi sul giro sono stati salvati nel database")
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante il salvataggio dei risultati: {str(e)}")
        finally:
            db.close()
    
    def show_final_results(self):
        """Mostra la classifica finale della sessione"""
        results_dialog = FinalResultsDialog(self.results_panel.get_best_laps(), self)
        results_dialog.exec()


class SessionControlPanel(QGroupBox):
    """Pannello di controllo per la sessione di prove libere"""
    
    # Dichiariamo il segnale proprio qui, fuori da qualsiasi metodo
    session_finished = pyqtSignal()
    
    def __init__(self):
        super().__init__("Controllo Sessione")
        
        # Layout principale
        self.layout = QHBoxLayout(self)
        
        # Timer display
        self.timer_display = QLabel("00:00.000")
        self.timer_display.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.layout.addWidget(self.timer_display)
        
        # Tempo rimanente display (per le prove: 5min+15min)
        self.remaining_time_label = QLabel("Tempo rimanente:")
        self.layout.addWidget(self.remaining_time_label)
        
        self.remaining_display = QLabel("20:00")
        self.remaining_display.setStyleSheet("font-size: 24px; font-weight: bold; color: green;")
        self.layout.addWidget(self.remaining_display)
        
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
        
        self.remaining_timer = QTimer()
        self.remaining_timer.timeout.connect(self.update_remaining_time)
        
        self.session_running = False
        self.session_elapsed_timer = QElapsedTimer()
        self.elapsed_time = 0
        
        # Durata prove libere + qualifiche: 5 min + 15 min = 20 min (1200 secondi)
        self.session_duration = 1200  # in secondi
        self.remaining_time = self.session_duration
        
        # Flag per il cambio da "Prove Libere" a "Qualifiche"
        self.qualification_flag = False
        self.free_practice_duration = 300  # 5 minuti in secondi
    
        
    def start_session(self):
        """Avvia la sessione di cronometraggio"""
        if not self.session_running:
            self.session_elapsed_timer.start()
            self.session_timer.start(100)  # Aggiorna ogni 100ms
            self.remaining_timer.start(1000)  # Aggiorna ogni secondo
            self.session_running = True
            
            self.start_button.setEnabled(False)
            self.pause_button.setEnabled(True)
            self.stop_button.setEnabled(True)
            
            self.status_label.setText("Prove Libere in corso")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
    
    def pause_session(self):
        """Mette in pausa la sessione"""
        if self.session_running:
            self.session_timer.stop()
            self.remaining_timer.stop()
            self.elapsed_time = self.session_elapsed_timer.elapsed()
            self.session_running = False
            
            self.start_button.setEnabled(True)
            self.start_button.setText("Riprendi")
            self.pause_button.setEnabled(False)
            
            self.status_label.setText("Sessione in pausa")
            self.status_label.setStyleSheet("color: orange; font-weight: bold;")
        else:
            self.session_elapsed_timer.start()
            self.session_elapsed_timer.addMSecs(-self.elapsed_time)
            self.session_timer.start(100)
            self.remaining_timer.start(1000)
            self.session_running = True
            
            self.start_button.setEnabled(False)
            self.pause_button.setEnabled(True)
            
            self.status_label.setText("Prove Libere in corso")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
    
    def stop_session(self):
        """Ferma la sessione"""
        self.session_timer.stop()
        self.remaining_timer.stop()
        self.session_running = False
        
        self.start_button.setEnabled(True)
        self.start_button.setText("Avvia")
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        
        # Finalizza i risultati
        final_time = self.session_elapsed_timer.elapsed()
        self.timer_display.setText(self.format_time(final_time))
        self.status_label.setText(f"Sessione terminata")
        self.status_label.setStyleSheet("color: blue; font-weight: bold;")
        
        # Emetti il segnale di fine sessione
        self.session_finished.emit()
    
    def update_timer(self):
        """Aggiorna il display del timer"""
        if self.session_running:
            elapsed = self.session_elapsed_timer.elapsed()
            self.timer_display.setText(self.format_time(elapsed))
            
            # Controlla se siamo passati da prove libere a qualifiche
            if not self.qualification_flag and elapsed >= self.free_practice_duration * 1000:
                self.qualification_flag = True
                self.status_label.setText("Qualifiche in corso")
                
                # Cambiamo colore per evidenziare il cambio
                self.status_label.setStyleSheet("color: red; font-weight: bold;")
                
                # Suona un beep o mostra un messaggio per avvisare
                QMessageBox.information(self, "Cambio Sessione", "Le prove libere sono terminate. Iniziano le qualifiche!")
    
    def update_remaining_time(self):
        """Aggiorna il display del tempo rimanente"""
        if self.session_running and self.remaining_time > 0:
            self.remaining_time -= 1
            minutes = self.remaining_time // 60
            seconds = self.remaining_time % 60
            
            # Cambia colore a seconda del tempo rimanente
            if self.remaining_time > 300:  # Più di 5 minuti
                color = "green"
            elif self.remaining_time > 60:  # Tra 1 e 5 minuti
                color = "orange"
            else:  # Meno di 1 minuto
                color = "red"
            
            self.remaining_display.setText(f"{minutes:02d}:{seconds:02d}")
            self.remaining_display.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {color};")
            
            if self.remaining_time == 0:
                self.stop_session()
    
    def get_elapsed_time(self):
        """Calcola il tempo trascorso in millisecondi"""
        if self.session_running:
            return self.session_elapsed_timer.elapsed()
        return self.elapsed_time
    
    def format_time(self, msecs):
        """Formatta il tempo in millisecondi come MM:SS.mmm"""
        secs = msecs // 1000
        mins = secs // 60
        secs %= 60
        msecs %= 1000
        return f"{mins:02d}:{secs:02d}.{msecs:03d}"
    
    def reset_session(self):
        """Resetta la sessione"""
        self.session_timer.stop()
        self.remaining_timer.stop()
        self.session_running = False
        
        self.session_elapsed_timer = QElapsedTimer()
        self.elapsed_time = 0
        self.remaining_time = self.session_duration
        
        self.qualification_flag = False
        
        self.timer_display.setText("00:00.000")
        self.remaining_display.setText(f"{self.session_duration // 60:02d}:00")
        self.remaining_display.setStyleSheet("font-size: 24px; font-weight: bold; color: green;")
        
        self.start_button.setEnabled(True)
        self.start_button.setText("Avvia")
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        
        self.status_label.setText("Sessione non avviata")
        self.status_label.setStyleSheet("")


class ManualTimingPanel(QGroupBox):
    """Pannello per l'inserimento manuale dei tempi"""
    def __init__(self):
        super().__init__("Inserimento Manuale")
        
        # Layout principale
        self.layout = QVBoxLayout(self)
        
        # Intestazione
        self.header_label = QLabel("Inserisci il numero di gara e premi Invio o il pulsante Registra:")
        self.layout.addWidget(self.header_label)
        
        # Inserimento numero pilota
        input_layout = QHBoxLayout()
        
        self.rider_number_label = QLabel("Numero:")
        self.rider_number_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        input_layout.addWidget(self.rider_number_label)
        
        self.rider_number_input = QLineEdit()
        self.rider_number_input.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.rider_number_input.setPlaceholderText("Numero pilota")
        self.rider_number_input.setValidator(QIntValidator(1, 999))  # Solo numeri da 1 a 999
        
        # Connessione con tasto Invio
        self.rider_number_input.returnPressed.connect(self.record_lap)
        input_layout.addWidget(self.rider_number_input)
        
        self.record_button = QPushButton("Registra")
        self.record_button.setStyleSheet("font-size: 18px; background-color: #4CAF50; color: white;")
        self.record_button.clicked.connect(self.record_lap)
        input_layout.addWidget(self.record_button)
        
        self.layout.addLayout(input_layout)
        
        # Ultimi passaggi registrati
        self.lap_times_table = QTableWidget(0, 4)
        self.lap_times_table.setHorizontalHeaderLabels([
            "Numero", "Pilota", "Giro", "Tempo sul Giro"
        ])
        self.layout.addWidget(self.lap_times_table)
        
        # Dizionario per memorizzare i piloti {numero_gara: {id, nome, cognome}}
        self.riders = {}
        # Dizionario per memorizzare i giri per pilota {numero_gara: conteggio_giri}
        self.rider_laps = {}
        # Dizionario per memorizzare i tempi dell'ultimo giro {numero_gara: timestamp_ultimo_giro}
        self.last_lap_times = {}
    
    def load_riders(self, riders_list):
        """Carica la lista dei piloti"""
        self.riders = {str(rider["numero"]): rider for rider in riders_list}
        self.rider_laps = {str(rider["numero"]): 0 for rider in riders_list}
        self.last_lap_times = {}
        
        # Pulisce la tabella
        self.lap_times_table.setRowCount(0)
        
        # Focus sull'input per iniziare subito
        self.rider_number_input.setFocus()
    
    def record_lap(self):
        """Registra il passaggio di un pilota"""
        rider_number = self.rider_number_input.text().strip()
        current_time = QDateTime.currentDateTime()
        
        if not rider_number:
            return
        
        if rider_number not in self.riders:
            QMessageBox.warning(self, "Attenzione", f"Nessun pilota trovato con il numero {rider_number}!")
            self.rider_number_input.clear()
            self.rider_number_input.setFocus()
            return
        
        # Ottieni il pilota
        rider = self.riders[rider_number]
        
        # Incrementa il conteggio dei giri
        self.rider_laps[rider_number] += 1
        lap_count = self.rider_laps[rider_number]
        
        # Calcola il tempo sul giro se non è il primo giro
        lap_time_ms = 0
        if rider_number in self.last_lap_times:
            last_timestamp = self.last_lap_times[rider_number]
            lap_time_ms = last_timestamp.msecsTo(current_time)
        
        # Memorizza il timestamp attuale
        self.last_lap_times[rider_number] = current_time
        
        # Formatta il tempo sul giro
        if lap_count == 1 or lap_time_ms == 0:
            lap_time_text = "-"
        else:
            secs = lap_time_ms // 1000
            mins = secs // 60
            secs %= 60
            msecs = lap_time_ms % 1000
            lap_time_text = f"{mins:02d}:{secs:02d}.{msecs:03d}"
        
        # Aggiungi una riga alla tabella
        row = self.lap_times_table.rowCount()
        self.lap_times_table.insertRow(row)
        
        self.lap_times_table.setItem(row, 0, QTableWidgetItem(rider_number))
        self.lap_times_table.setItem(row, 1, QTableWidgetItem(f"{rider['cognome']} {rider['nome']}"))
        self.lap_times_table.setItem(row, 2, QTableWidgetItem(str(lap_count)))
        self.lap_times_table.setItem(row, 3, QTableWidgetItem(lap_time_text))
        
        # Scorri alla riga appena aggiunta
        self.lap_times_table.scrollToItem(self.lap_times_table.item(row, 0))
        
        # Emetti un segnale che il pilota ha registrato un giro (per aggiornare la tabella dei risultati live)
        # Da implementare con un segnale personalizzato
        
        # Pulisci l'input e rimetti il focus
        self.rider_number_input.clear()
        self.rider_number_input.setFocus()
        
        # Notifica ai pannelli interessati
        parent = self.parent()
        if hasattr(parent, 'results_panel'):
            parent.results_panel.add_lap_time(rider["id"], lap_time_ms, current_time, lap_count)


class VideoRecognitionPanel(QGroupBox):
    """Pannello per il sistema di riconoscimento video"""
    def __init__(self):
        super().__init__("Riconoscimento Video")
        
        # Layout principale
        self.layout = QVBoxLayout(self)
        
        # Info
        self.info_label = QLabel("Sistema di riconoscimento video con intelligenza artificiale.")
        self.layout.addWidget(self.info_label)
        
        # Stato connessione
        status_layout = QHBoxLayout()
        
        self.status_label = QLabel("Stato:")
        status_layout.addWidget(self.status_label)
        
        self.connection_status = QLabel("Camera non connessa")
        self.connection_status.setStyleSheet("color: red;")
        status_layout.addWidget(self.connection_status)
        
        self.connect_button = QPushButton("Connetti Camera")
        self.connect_button.clicked.connect(self.toggle_connection)
        status_layout.addWidget(self.connect_button)
        
        status_layout.addStretch()
        
        self.layout.addLayout(status_layout)
        
        # Simulazione di visualizzazione camera (placeholder)
        self.camera_preview = QLabel("Anteprima Camera (non disponibile in modalità simulazione)")
        self.camera_preview.setStyleSheet("background-color: #333; color: white; padding: 20px; min-height: 150px;")
        self.camera_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.camera_preview)
        
        # Simulazione (solo a scopo dimostrativo)
        self.simulation_group = QGroupBox("Simulazione Riconoscimenti (demo)")
        simulation_layout = QVBoxLayout()
        
        self.simulate_button = QPushButton("Simula Riconoscimento Casuale")
        self.simulate_button.clicked.connect(self.simulate_random_detection)
        self.simulate_button.setEnabled(False)
        simulation_layout.addWidget(self.simulate_button)
        
        self.simulation_group.setLayout(simulation_layout)
        self.layout.addWidget(self.simulation_group)
        
        # Log dei riconoscimenti
        self.log_label = QLabel("Log dei riconoscimenti:")
        self.layout.addWidget(self.log_label)
        
        self.log_table = QTableWidget(0, 4)
        self.log_table.setHorizontalHeaderLabels([
            "Timestamp", "Numero Riconosciuto", "Pilota", "Tempo"
        ])
        self.layout.addWidget(self.log_table)
        
        # Dizionario per memorizzare i piloti {numero_gara: {id, nome, cognome}}
        self.riders = {}
        # Dizionario per memorizzare i tempi dell'ultimo giro {numero_gara: timestamp_ultimo_giro}
        self.last_lap_times = {}
        
        # Timer per simulare rilevamenti casuali (solo a scopo dimostrativo)
        self.simulation_timer = QTimer()
        self.simulation_timer.timeout.connect(self.simulate_random_detection)
    
    def load_riders(self, riders_list):
        """Carica la lista dei piloti"""
        self.riders = {str(rider["numero"]): rider for rider in riders_list}
        self.last_lap_times = {}
        
        # Pulisce la tabella
        self.log_table.setRowCount(0)
    
    def toggle_connection(self):
        """Connette o disconnette la camera"""
        if self.connect_button.text() == "Connetti Camera":
            # Simuliamo una connessione
            self.connect_button.setText("Disconnetti Camera")
            self.connection_status.setText("Camera connessa")
            self.connection_status.setStyleSheet("color: green; font-weight: bold;")
            self.simulate_button.setEnabled(True)
            self.camera_preview.setText("Anteprima Camera (connessa)")
            self.camera_preview.setStyleSheet("background-color: #007700; color: white; padding: 20px; min-height: 150px;")
            
            # Avvia la simulazione automatica (solo per demo)
            self.simulation_timer.start(4000)  # Ogni 4 secondi
        else:
            # Simuliamo una disconnessione
            self.connect_button.setText("Connetti Camera")
            self.connection_status.setText("Camera non connessa")
            self.connection_status.setStyleSheet("color: red;")
            self.simulate_button.setEnabled(False)
            self.camera_preview.setText("Anteprima Camera (non disponibile in modalità simulazione)")
            self.camera_preview.setStyleSheet("background-color: #333; color: white; padding: 20px; min-height: 150px;")
            
            # Ferma la simulazione
            self.simulation_timer.stop()
    
    def simulate_random_detection(self):
        """Simula il riconoscimento casuale di un numero (solo a scopo dimostrativo)"""
        import random
        
        # Verifica se ci sono piloti caricati
        if not self.riders:
            return
        
        # Seleziona un numero casuale
        rider_number = random.choice(list(self.riders.keys()))
        
        current_time = QDateTime.currentDateTime()
        
        # Calcola il tempo sul giro se non è il primo giro
        lap_time_ms = 0
        if rider_number in self.last_lap_times:
            last_timestamp = self.last_lap_times[rider_number]
            lap_time_ms = last_timestamp.msecsTo(current_time)
        
        # Memorizza il timestamp attuale
        self.last_lap_times[rider_number] = current_time
        
        # Formatta il tempo sul giro
        if lap_time_ms == 0:
            lap_time_text = "-"
        else:
            # Aggiungiamo un po' di casualità ai tempi (tra 1:20 e 1:50)
            if lap_time_ms < 1000:  # è la prima volta, generiamo un tempo casuale
                lap_time_ms = random.randint(80000, 110000)
            
            secs = lap_time_ms // 1000
            mins = secs // 60
            secs %= 60
            msecs = lap_time_ms % 1000
            lap_time_text = f"{mins:02d}:{secs:02d}.{msecs:03d}"
        
        # Ottieni il pilota
        rider = self.riders[rider_number]
        
        # Cambia temporaneamente lo sfondo del preview per simulare una "detection"
        current_style = self.camera_preview.styleSheet()
        self.camera_preview.setText(f"RILEVATO: {rider_number}")
        self.camera_preview.setStyleSheet("background-color: #0000CC; color: white; padding: 20px; min-height: 150px; font-size: 18px; font-weight: bold;")
        
        # Ripristina lo stile dopo 500ms
        QTimer.singleShot(500, lambda: self.camera_preview.setStyleSheet(current_style))
        QTimer.singleShot(500, lambda: self.camera_preview.setText("Anteprima Camera (connessa)"))
        
        # Aggiungi una riga alla tabella
        row = self.log_table.rowCount()
        self.log_table.insertRow(row)
        
        self.log_table.setItem(row, 0, QTableWidgetItem(current_time.toString("HH:mm:ss.zzz")))
        self.log_table.setItem(row, 1, QTableWidgetItem(rider_number))
        self.log_table.setItem(row, 2, QTableWidgetItem(f"{rider['cognome']} {rider['nome']}"))
        self.log_table.setItem(row, 3, QTableWidgetItem(lap_time_text))
        
        # Scorri alla riga appena aggiunta
        self.log_table.scrollToItem(self.log_table.item(row, 0))
        
        # Notifica ai pannelli interessati
        parent = self.parent()
        while parent and not hasattr(parent, 'results_panel'):
            parent = parent.parent()
        
        if parent and hasattr(parent, 'results_panel'):
            # Calcoliamo il numero di giri in base alle volte che appare il numero
            lap_count = 0
            for row in range(self.log_table.rowCount()):
                if self.log_table.item(row, 1).text() == rider_number:
                    lap_count += 1
            
            parent.results_panel.add_lap_time(rider["id"], lap_time_ms, current_time, lap_count)


class TransponderTimingPanel(QGroupBox):
    """Pannello per il sistema con transponder"""
    def __init__(self):
        super().__init__("Sistema Transponder")
        
        # Layout principale
        self.layout = QVBoxLayout(self)
        
        # Info
        self.info_label = QLabel("Sistema automatico di cronometraggio con transponder.")
        self.layout.addWidget(self.info_label)
        
        # Stato connessione
        status_layout = QHBoxLayout()
        
        self.status_label = QLabel("Stato:")
        status_layout.addWidget(self.status_label)
        
        self.connection_status = QLabel("Non connesso")
        self.connection_status.setStyleSheet("color: red;")
        status_layout.addWidget(self.connection_status)
        
        self.connect_button = QPushButton("Connetti")
        self.connect_button.clicked.connect(self.toggle_connection)
        status_layout.addWidget(self.connect_button)
        
        status_layout.addStretch()
        
        self.layout.addLayout(status_layout)
        
        # Simulazione (solo a scopo dimostrativo)
        self.simulation_group = QGroupBox("Simulazione Passaggi (demo)")
        simulation_layout = QVBoxLayout()
        
        self.simulate_button = QPushButton("Simula Passaggio Casuale")
        self.simulate_button.clicked.connect(self.simulate_random_detection)
        self.simulate_button.setEnabled(False)
        simulation_layout.addWidget(self.simulate_button)
        
        self.simulation_group.setLayout(simulation_layout)
        self.layout.addWidget(self.simulation_group)
        
        # Log dei passaggi
        self.log_label = QLabel("Log dei passaggi:")
        self.layout.addWidget(self.log_label)
        
        self.log_table = QTableWidget(0, 4)
        self.log_table.setHorizontalHeaderLabels([
            "Timestamp", "Transponder ID", "Pilota", "Tempo"
        ])
        self.layout.addWidget(self.log_table)
        
        # Dizionario per memorizzare i piloti {transponder_id: {id, nome, cognome}}
        self.riders = {}
        # Dizionario per memorizzare i tempi dell'ultimo giro {transponder_id: timestamp_ultimo_giro}
        self.last_lap_times = {}
        
        # Timer per simulare rilevamenti casuali (solo a scopo dimostrativo)
        self.simulation_timer = QTimer()
        self.simulation_timer.timeout.connect(self.simulate_random_detection)
    
    def load_riders(self, riders_list):
        """Carica la lista dei piloti"""
        self.riders = {}
        self.transponder_to_rider = {}
        
        for rider in riders_list:
            if rider["transponder"]:
                # Se il pilota ha un transponder, lo usiamo come chiave
                transponder_id = rider["transponder"]
                self.transponder_to_rider[transponder_id] = rider
                self.riders[str(rider["numero"])] = rider
            else:
                # Altrimenti, generiamo un ID fittizio basato sul numero di gara
                transponder_id = f"T{rider['numero']:03d}"
                self.transponder_to_rider[transponder_id] = rider
                self.riders[str(rider["numero"])] = rider
                # Aggiorniamo il transponder ID del pilota
                rider["transponder"] = transponder_id
        
        self.last_lap_times = {}
        
        # Pulisce la tabella
        self.log_table.setRowCount(0)
    
    def toggle_connection(self):
        """Connette o disconnette il sistema di transponder"""
        if self.connect_button.text() == "Connetti":
            # Simuliamo una connessione
            self.connect_button.setText("Disconnetti")
            self.connection_status.setText("Connesso")
            self.connection_status.setStyleSheet("color: green; font-weight: bold;")
            self.simulate_button.setEnabled(True)
            
            # Avvia la simulazione automatica (solo per demo)
            self.simulation_timer.start(5000)  # Ogni 5 secondi
        else:
            # Simuliamo una disconnessione
            self.connect_button.setText("Connetti")
            self.connection_status.setText("Non connesso")
            self.connection_status.setStyleSheet("color: red;")
            self.simulate_button.setEnabled(False)
            
            # Ferma la simulazione
            self.simulation_timer.stop()
    
    def simulate_random_detection(self):
        """Simula il rilevamento casuale di un transponder (solo a scopo dimostrativo)"""
        import random
        
        # Verifica se ci sono piloti caricati
        if not self.transponder_to_rider:
            return
        
        # Seleziona un transponder casuale
        transponder_id = random.choice(list(self.transponder_to_rider.keys()))
        
        current_time = QDateTime.currentDateTime()
        
        # Calcola il tempo sul giro se non è il primo giro
        lap_time_ms = 0
        if transponder_id in self.last_lap_times:
            last_timestamp = self.last_lap_times[transponder_id]
            lap_time_ms = last_timestamp.msecsTo(current_time)
        
        # Memorizza il timestamp attuale
        self.last_lap_times[transponder_id] = current_time
        
        # Formatta il tempo sul giro
        if lap_time_ms == 0:
            lap_time_text = "-"
        else:
            # Aggiungiamo un po' di casualità ai tempi (tra 1:20 e 1:50)
            if lap_time_ms < 1000:  # è la prima volta, generiamo un tempo casuale
                lap_time_ms = random.randint(80000, 110000)
            
            secs = lap_time_ms // 1000
            mins = secs // 60
            secs %= 60
            msecs = lap_time_ms % 1000
            lap_time_text = f"{mins:02d}:{secs:02d}.{msecs:03d}"
        
        # Ottieni il pilota
        rider = self.transponder_to_rider[transponder_id]
        
        # Aggiungi una riga alla tabella
        row = self.log_table.rowCount()
        self.log_table.insertRow(row)
        
        self.log_table.setItem(row, 0, QTableWidgetItem(current_time.toString("HH:mm:ss.zzz")))
        self.log_table.setItem(row, 1, QTableWidgetItem(transponder_id))
        self.log_table.setItem(row, 2, QTableWidgetItem(f"{rider['cognome']} {rider['nome']} ({rider['numero']})"))
        self.log_table.setItem(row, 3, QTableWidgetItem(lap_time_text))
        
        # Scorri alla riga appena aggiunta
        self.log_table.scrollToItem(self.log_table.item(row, 0))
        
        # Notifica ai pannelli interessati
        parent = self.parent()
        while parent and not hasattr(parent, 'results_panel'):
            parent = parent.parent()
        
        if parent and hasattr(parent, 'results_panel'):
            # Calcoliamo il numero di giri in base alle volte che appare il transponder
            lap_count = 0
            for row in range(self.log_table.rowCount()):
                if self.log_table.item(row, 1).text() == transponder_id:
                    lap_count += 1
            
            parent.results_panel.add_lap_time(rider["id"], lap_time_ms, current_time, lap_count)


class LiveResultsPanel(QGroupBox):
    """Pannello per visualizzare i risultati live durante la sessione"""
    def __init__(self):
        super().__init__("Risultati Live")
        
        # Layout principale
        self.layout = QVBoxLayout(self)
        
        # Tabella risultati
        self.results_table = QTableWidget(0, 5)
        self.results_table.setHorizontalHeaderLabels([
            "Pos", "Num", "Pilota", "Miglior Tempo", "Ultimo Tempo"
        ])
        self.layout.addWidget(self.results_table)
        
        # Dizionari per memorizzare i dati
        self.riders = {}  # {id: {numero, nome, cognome}}
        self.lap_times = {}  # {id: [{time_ms, timestamp}, ...]}
        self.best_laps = {}  # {id: time_ms}
        self.last_laps = {}  # {id: time_ms}
    
    def load_riders(self, riders_list):
        """Carica la lista dei piloti"""
        self.riders = {rider["id"]: rider for rider in riders_list}
        self.lap_times = {rider["id"]: [] for rider in riders_list}
        self.best_laps = {}
        self.last_laps = {}
        
        # Inizializza la tabella con i piloti
        self.results_table.setRowCount(len(riders_list))
        
        for i, rider in enumerate(riders_list):
            self.results_table.setItem(i, 0, QTableWidgetItem("-"))
            self.results_table.setItem(i, 1, QTableWidgetItem(str(rider["numero"])))
            self.results_table.setItem(i, 2, QTableWidgetItem(f"{rider['cognome']} {rider['nome']}"))
            self.results_table.setItem(i, 3, QTableWidgetItem("-"))
            self.results_table.setItem(i, 4, QTableWidgetItem("-"))
        
        # Ridimensiona colonne
        self.results_table.resizeColumnsToContents()
    
    def add_lap_time(self, rider_id, time_ms, timestamp, lap_count):
        """Aggiunge un tempo sul giro per un pilota e aggiorna la tabella"""
        if rider_id not in self.riders:
            return
        
        # Non registriamo il primo giro (tempo di ingresso)
        if lap_count <= 1 or time_ms <= 0:
            return
        
        # Aggiungi il tempo alla lista dei tempi del pilota
        self.lap_times[rider_id].append({
            "time_ms": time_ms,
            "timestamp": timestamp,
            "lap": lap_count
        })
        
        # Aggiorna il miglior tempo e l'ultimo tempo del pilota
        if rider_id not in self.best_laps or time_ms < self.best_laps[rider_id]:
            self.best_laps[rider_id] = time_ms
        
        self.last_laps[rider_id] = time_ms
        
        # Aggiorna la tabella
        self.update_results_table()
    
    def update_results_table(self):
        """Aggiorna la tabella dei risultati in base ai tempi registrati"""
        # Ordina i piloti in base al miglior tempo
        sorted_riders = []
        
        for rider_id, rider in self.riders.items():
            if rider_id in self.best_laps:
                sorted_riders.append({
                    "id": rider_id,
                    "numero": rider["numero"],
                    "nome": rider["nome"],
                    "cognome": rider["cognome"],
                    "best_time": self.best_laps[rider_id],
                    "last_time": self.last_laps[rider_id]
                })
        
        # Piloti che non hanno ancora registrato tempi
        for rider_id, rider in self.riders.items():
            if rider_id not in self.best_laps:
                sorted_riders.append({
                    "id": rider_id,
                    "numero": rider["numero"],
                    "nome": rider["nome"],
                    "cognome": rider["cognome"],
                    "best_time": float('inf'),
                    "last_time": 0
                })
        
        # Ordinamento per miglior tempo
        sorted_riders.sort(key=lambda x: x["best_time"])
        
        # Aggiorna la tabella
        self.results_table.setRowCount(len(sorted_riders))
        
        for i, rider in enumerate(sorted_riders):
            self.results_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self.results_table.setItem(i, 1, QTableWidgetItem(str(rider["numero"])))
            self.results_table.setItem(i, 2, QTableWidgetItem(f"{rider['cognome']} {rider['nome']}"))
            
            # Miglior tempo
            if rider["best_time"] != float('inf'):
                best_time_text = self.format_time(rider["best_time"])
                
                # Imposta il colore in base alla posizione
                if i == 0:  # Primo
                    best_time_item = QTableWidgetItem(best_time_text)
                    best_time_item.setBackground(QColor(0, 200, 0))  # Verde
                    best_time_item.setForeground(QColor(255, 255, 255))  # Testo bianco
                    self.results_table.setItem(i, 3, best_time_item)
                else:
                    best_time_item = QTableWidgetItem(best_time_text)
                    self.results_table.setItem(i, 3, best_time_item)
            else:
                self.results_table.setItem(i, 3, QTableWidgetItem("-"))
            
            # Ultimo tempo
            if rider["last_time"] > 0:
                last_time_text = self.format_time(rider["last_time"])
                self.results_table.setItem(i, 4, QTableWidgetItem(last_time_text))
            else:
                self.results_table.setItem(i, 4, QTableWidgetItem("-"))
        
        # Ridimensiona colonne
        self.results_table.resizeColumnsToContents()
    
    def format_time(self, msecs):
        """Formatta il tempo in millisecondi come MM:SS.mmm"""
        secs = msecs // 1000
        mins = secs // 60
        secs %= 60
        msecs %= 1000
        return f"{mins:02d}:{secs:02d}.{msecs:03d}"
    
    def get_results(self):
        """Restituisce tutti i tempi sul giro registrati"""
        return self.lap_times
    
    def get_best_laps(self):
        """Restituisce i migliori tempi sul giro per ogni pilota"""
        result = []
        
        for rider_id, best_time in self.best_laps.items():
            if rider_id in self.riders:
                rider = self.riders[rider_id]
                result.append({
                    "id": rider_id,
                    "numero": rider["numero"],
                    "nome": rider["nome"],
                    "cognome": rider["cognome"],
                    "best_time": best_time,
                    "best_time_text": self.format_time(best_time)
                })
        
        # Ordina per miglior tempo
        result.sort(key=lambda x: x["best_time"])
        
        return result


class FinalResultsDialog(QDialog):
    """Finestra di dialogo per mostrare i risultati finali della sessione"""
    def __init__(self, results, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Risultati Finali Prove Libere")
        self.resize(600, 400)
        
        # Layout principale
        layout = QVBoxLayout(self)
        
        # Titolo
        title_label = QLabel("Risultati Finali Prove Libere")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Tabella risultati
        self.results_table = QTableWidget(len(results), 5)
        self.results_table.setHorizontalHeaderLabels([
            "Pos", "Num", "Pilota", "Miglior Tempo", "Distacco"
        ])
        
        # Precomputa il distacco dal primo
        best_time = results[0]["best_time"] if results else 0
        
        # Riempi la tabella
        for i, rider in enumerate(results):
            self.results_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self.results_table.setItem(i, 1, QTableWidgetItem(str(rider["numero"])))
            self.results_table.setItem(i, 2, QTableWidgetItem(f"{rider['cognome']} {rider['nome']}"))
            self.results_table.setItem(i, 3, QTableWidgetItem(rider["best_time_text"]))
            
            # Calcola il distacco
            if i == 0:
                self.results_table.setItem(i, 4, QTableWidgetItem("-"))
            else:
                gap_ms = rider["best_time"] - best_time
                gap_s = gap_ms / 1000.0
                self.results_table.setItem(i, 4, QTableWidgetItem(f"+{gap_s:.3f}s"))
        
        layout.addWidget(self.results_table)
        
        # Bottoni
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Save)
        button_box.accepted.connect(self.accept)
        button_box.button(QDialogButtonBox.StandardButton.Save).clicked.connect(self.save_results)
        layout.addWidget(button_box)
        
        # Ridimensiona colonne
        self.results_table.resizeColumnsToContents()
    
    def save_results(self):
        """Salva i risultati in un file CSV"""
        from PyQt6.QtWidgets import QFileDialog
        import csv
        
        # Apri dialog per salvare il file
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Salva Risultati", "", "File CSV (*.csv)"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', newline='') as file:
                writer = csv.writer(file)
                
                # Scrivi intestazione
                headers = []
                for col in range(self.results_table.columnCount()):
                    headers.append(self.results_table.horizontalHeaderItem(col).text())
                writer.writerow(headers)
                
                # Scrivi dati
                for row in range(self.results_table.rowCount()):
                    data = []
                    for col in range(self.results_table.columnCount()):
                        item = self.results_table.item(row, col)
                        data.append(item.text() if item else "")
                    writer.writerow(data)
            
            QMessageBox.information(self, "Salvato", f"Risultati salvati in {file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante il salvataggio: {str(e)}")