# ui/penalties_tab.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLabel, QComboBox, QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QMessageBox, QSpinBox,
    QCheckBox, QTextEdit, QDialog, QDialogButtonBox
)
from PyQt6.QtCore import Qt, QDateTime
from PyQt6.QtGui import QColor

from database.connection import SessionLocal
from database.models import Evento, Iscrizione, Pilota, Gruppo, PartecipazioneGruppo, Penalita

class PenaltiesTab(QWidget):
    """Scheda per gestire le penalità dei piloti"""
    
    def __init__(self):
        super().__init__()
        
        # Layout principale
        layout = QVBoxLayout(self)
        
        # Titolo
        title_label = QLabel("Gestione Penalità")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Selettori
        selectors_layout = QFormLayout()
        
        self.event_combo = QComboBox()
        selectors_layout.addRow("Evento:", self.event_combo)
        
        self.session_type_combo = QComboBox()
        self.session_type_combo.addItems(["Prove Libere", "Qualifiche", "Gara 1", "Gara 2", "Supercampione"])
        selectors_layout.addRow("Sessione:", self.session_type_combo)
        
        self.group_combo = QComboBox()
        selectors_layout.addRow("Gruppo:", self.group_combo)
        
        layout.addLayout(selectors_layout)
        
        # Bottoni per azioni
        buttons_layout = QHBoxLayout()
        
        self.load_button = QPushButton("Carica Piloti")
        self.load_button.clicked.connect(self.load_riders)
        buttons_layout.addWidget(self.load_button)
        
        self.add_penalty_button = QPushButton("Aggiungi Penalità")
        self.add_penalty_button.clicked.connect(self.add_penalty)
        buttons_layout.addWidget(self.add_penalty_button)
        
        self.remove_penalty_button = QPushButton("Rimuovi Penalità")
        self.remove_penalty_button.clicked.connect(self.remove_penalty)
        buttons_layout.addWidget(self.remove_penalty_button)
        
        layout.addLayout(buttons_layout)
        
        # Tabella piloti e penalità
        self.penalties_table = QTableWidget(0, 7)
        self.penalties_table.setHorizontalHeaderLabels([
            "ID", "Numero", "Pilota", "Infrazione", "Descrizione", "Penalità", "Data/Ora"
        ])
        self.penalties_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.penalties_table)
        
        # Carica eventi
        self.load_events()
        
        # Collega eventi combo
        self.event_combo.currentIndexChanged.connect(self.load_groups)
        self.session_type_combo.currentIndexChanged.connect(self.load_groups)
    
    def load_events(self):
        """Carica gli eventi disponibili"""
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
    
    def load_groups(self):
        """Carica i gruppi per l'evento e la sessione selezionati"""
        evento_id = self.event_combo.currentData()
        sessione_tipo = self.session_type_combo.currentText()
        
        if not evento_id:
            return
        
        try:
            db = SessionLocal()
            
            gruppi = db.query(Gruppo).filter(
                Gruppo.evento_id == evento_id,
                Gruppo.tipo_sessione == sessione_tipo
            ).all()
            
            self.group_combo.clear()
            for gruppo in gruppi:
                self.group_combo.addItem(gruppo.nome, gruppo.id)
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante il caricamento gruppi: {str(e)}")
        finally:
            db.close()
    
    def load_riders(self):
        """Carica i piloti e le relative penalità"""
        evento_id = self.event_combo.currentData()
        sessione_tipo = self.session_type_combo.currentText()
        gruppo_id = self.group_combo.currentData()
        
        if not evento_id or not gruppo_id:
            QMessageBox.warning(self, "Attenzione", "Seleziona evento e gruppo!")
            return
        
        try:
            db = SessionLocal()
            
            # Ottieni i piloti del gruppo
            partecipazioni = db.query(PartecipazioneGruppo).filter(
                PartecipazioneGruppo.gruppo_id == gruppo_id
            ).all()
            
            # Ottieni le penalità esistenti
            penalita = db.query(Penalita).filter(
                Penalita.gruppo_id == gruppo_id,
                Penalita.sessione_tipo == sessione_tipo
            ).all()
            
            # Mappatura delle penalità per pilota
            penalita_per_pilota = {}
            for p in penalita:
                if p.iscrizione_id not in penalita_per_pilota:
                    penalita_per_pilota[p.iscrizione_id] = []
                penalita_per_pilota[p.iscrizione_id].append(p)
            
            # Popola la tabella
            self.penalties_table.setRowCount(0)
            
            for partecipazione in partecipazioni:
                iscrizione = partecipazione.iscrizione
                
                # Se il pilota ha penalità, mostrare ogni penalità come riga separata
                if iscrizione.id in penalita_per_pilota and penalita_per_pilota[iscrizione.id]:
                    for penalita in penalita_per_pilota[iscrizione.id]:
                        self._add_penalty_row(iscrizione, penalita)
                else:
                    # Aggiungi una riga vuota per il pilota senza penalità
                    self._add_rider_row(iscrizione)
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante il caricamento piloti: {str(e)}")
        finally:
            db.close()
    
    def _add_rider_row(self, iscrizione):
        """Aggiunge una riga per un pilota senza penalità"""
        row = self.penalties_table.rowCount()
        self.penalties_table.insertRow(row)
        
        self.penalties_table.setItem(row, 0, QTableWidgetItem(str(iscrizione.id)))
        self.penalties_table.setItem(row, 1, QTableWidgetItem(str(iscrizione.numero_gara)))
        self.penalties_table.setItem(row, 2, QTableWidgetItem(f"{iscrizione.pilota.cognome} {iscrizione.pilota.nome}"))
        self.penalties_table.setItem(row, 3, QTableWidgetItem("-"))
        self.penalties_table.setItem(row, 4, QTableWidgetItem("-"))
        self.penalties_table.setItem(row, 5, QTableWidgetItem("-"))
        self.penalties_table.setItem(row, 6, QTableWidgetItem("-"))
    
    def _add_penalty_row(self, iscrizione, penalita):
        """Aggiunge una riga per un pilota con penalità"""
        row = self.penalties_table.rowCount()
        self.penalties_table.insertRow(row)
        
        self.penalties_table.setItem(row, 0, QTableWidgetItem(str(iscrizione.id)))
        self.penalties_table.setItem(row, 0, QTableWidgetItem(str(penalita.id)))
        self.penalties_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, penalita.id)
        
        self.penalties_table.setItem(row, 1, QTableWidgetItem(str(iscrizione.numero_gara)))
        self.penalties_table.setItem(row, 2, QTableWidgetItem(f"{iscrizione.pilota.cognome} {iscrizione.pilota.nome}"))
        self.penalties_table.setItem(row, 3, QTableWidgetItem(penalita.tipo_infrazione))
        self.penalties_table.setItem(row, 4, QTableWidgetItem(penalita.descrizione or "-"))
        
        # Mostra il tipo di penalità
        if penalita.esclusione:
            penalty_text = "Esclusione"
        elif penalita.posizioni_penalita > 0:
            penalty_text = f"{penalita.posizioni_penalita} posizioni"
        elif penalita.tempo_penalita > 0:
            penalty_text = f"{penalita.tempo_penalita} secondi"
        elif penalita.cancella_miglior_tempo:
            penalty_text = "Cancellazione miglior tempo"
        else:
            penalty_text = "-"
        
        self.penalties_table.setItem(row, 5, QTableWidgetItem(penalty_text))
        self.penalties_table.setItem(row, 6, QTableWidgetItem(penalita.data_ora.strftime("%d/%m/%Y %H:%M")))
    
    def add_penalty(self):
        """Aggiunge una nuova penalità"""
        # Verifica se un pilota è selezionato
        selected_items = self.penalties_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Attenzione", "Seleziona un pilota!")
            return
        
        # Ottieni l'ID iscrizione
        row = selected_items[0].row()
        iscrizione_id = int(self.penalties_table.item(row, 0).text())
        
        # Apri dialogo per inserire la penalità
        dialog = PenaltyDialog(self, iscrizione_id)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Ricarica i dati
            self.load_riders()
    
    def remove_penalty(self):
        """Rimuove una penalità esistente"""
        # Verifica se una penalità è selezionata
        selected_items = self.penalties_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Attenzione", "Seleziona una penalità da rimuovere!")
            return
        
        # Ottieni l'ID della penalità
        row = selected_items[0].row()
        penalty_id = self.penalties_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        if not penalty_id:
            QMessageBox.warning(self, "Attenzione", "Nessuna penalità selezionata!")
            return
        
        # Chiedi conferma
        reply = QMessageBox.question(
            self, "Conferma rimozione", 
            "Sei sicuro di voler rimuovere questa penalità?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                db = SessionLocal()
                
                # Trova e rimuovi la penalità
                penalita = db.query(Penalita).get(penalty_id)
                if penalita:
                    db.delete(penalita)
                    db.commit()
                    
                    # Ricarica i dati
                    self.load_riders()
                    
                    QMessageBox.information(self, "Operazione completata", "Penalità rimossa con successo!")
                else:
                    QMessageBox.warning(self, "Attenzione", "Penalità non trovata!")
                
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Errore durante la rimozione: {str(e)}")
            finally:
                db.close()


class PenaltyDialog(QDialog):
    """Dialogo per inserire una nuova penalità"""
    
    def __init__(self, parent=None, iscrizione_id=None):
        super().__init__(parent)
        
        self.iscrizione_id = iscrizione_id
        self.setWindowTitle("Aggiungi Penalità")
        self.resize(500, 400)
        
        # Layout principale
        layout = QVBoxLayout(self)
        
        # Form per i dati della penalità
        form_layout = QFormLayout()
        
        # Tipo di infrazione
        self.infraction_combo = QComboBox()
        self.infraction_combo.addItems([
            "Bandiera gialla (agitata)",
            "Bandiera bianca con croce rossa",
            "Taglio percorso",
            "Aiuto esterno",
            "Comportamento antisportivo",
            "Problemi meccanici",
            "Mancato rispetto procedura di partenza",
            "Superamento limite rumorosità",
            "Altro"
        ])
        form_layout.addRow("Tipo infrazione:", self.infraction_combo)
        
        # Descrizione
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(100)
        form_layout.addRow("Descrizione:", self.description_edit)
        
        # Gruppo per il tipo di penalità
        self.penalty_group = QFormLayout()
        
        # Opzioni di penalità
        self.position_penalty_check = QCheckBox("Penalità di posizione")
        self.penalty_group.addRow("", self.position_penalty_check)
        
        self.position_spin = QSpinBox()
        self.position_spin.setRange(0, 20)
        self.position_spin.setValue(3)  # Default da regolamento
        self.position_spin.setEnabled(False)
        self.penalty_group.addRow("Posizioni:", self.position_spin)
        
        self.time_penalty_check = QCheckBox("Penalità di tempo")
        self.penalty_group.addRow("", self.time_penalty_check)
        
        self.time_spin = QSpinBox()
        self.time_spin.setRange(0, 300)
        self.time_spin.setValue(30)  # Default da regolamento
        self.time_spin.setSuffix(" secondi")
        self.time_spin.setEnabled(False)
        self.penalty_group.addRow("Tempo:", self.time_spin)
        
        self.best_time_check = QCheckBox("Cancellazione miglior tempo")
        self.penalty_group.addRow("", self.best_time_check)
        
        self.exclusion_check = QCheckBox("Esclusione dalla sessione")
        self.penalty_group.addRow("", self.exclusion_check)
        
        # Collega i checkbox per abilitare/disabilitare le opzioni
        self.position_penalty_check.stateChanged.connect(self._toggle_position_spin)
        self.time_penalty_check.stateChanged.connect(self._toggle_time_spin)
        
        # Aggiungi il gruppo delle penalità al form
        form_layout.addRow("Tipo penalità:", QWidget())  # Spacer
        layout.addLayout(form_layout)
        layout.addLayout(self.penalty_group)
        
        # Pulsanti
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Setta il tipo di penalità in base al tipo di infrazione selezionata
        self.infraction_combo.currentIndexChanged.connect(self._set_default_penalty)
        self._set_default_penalty(0)  # Imposta i valori predefiniti per la prima opzione
    
    def _toggle_position_spin(self, state):
        """Abilita/disabilita la spinbox delle posizioni"""
        self.position_spin.setEnabled(state == Qt.CheckState.Checked)
    
    def _toggle_time_spin(self, state):
        """Abilita/disabilita la spinbox del tempo"""
        self.time_spin.setEnabled(state == Qt.CheckState.Checked)
    
    def _set_default_penalty(self, index):
        """Imposta i valori predefiniti in base al tipo di infrazione"""
        infraction = self.infraction_combo.currentText()
        
        # Resetta tutti i controlli
        self.position_penalty_check.setChecked(False)
        self.time_penalty_check.setChecked(False)
        self.best_time_check.setChecked(False)
        self.exclusion_check.setChecked(False)
        
        # Imposta i valori predefiniti in base all'infrazione
        if "Bandiera gialla" in infraction or "croce rossa" in infraction:
            self.position_penalty_check.setChecked(True)
            self.position_spin.setValue(3)  # Penalità di 3 posizioni da regolamento
        
        elif "Taglio percorso" in infraction:
            # Durante prove/qualifiche: cancellazione miglior tempo
            # Durante gara: penalità di 30 secondi
            session_type = self.parent().session_type_combo.currentText()
            if "Qualifiche" in session_type or "Prove" in session_type:
                self.best_time_check.setChecked(True)
            else:
                self.time_penalty_check.setChecked(True)
                self.time_spin.setValue(30)  # 30 secondi di penalità da regolamento
        
        elif "Aiuto esterno" in infraction or "Problemi meccanici" in infraction:
            self.exclusion_check.setChecked(True)
    
    def accept(self):
        """Salva la penalità nel database"""
        evento_id = self.parent().event_combo.currentData()
        sessione_tipo = self.parent().session_type_combo.currentText()
        gruppo_id = self.parent().group_combo.currentData()
        
        if not evento_id or not gruppo_id:
            QMessageBox.warning(self, "Attenzione", "Seleziona evento e gruppo!")
            return
        
        # Verifica che almeno un tipo di penalità sia selezionato
        if not any([
            self.position_penalty_check.isChecked(),
            self.time_penalty_check.isChecked(),
            self.best_time_check.isChecked(),
            self.exclusion_check.isChecked()
        ]):
            QMessageBox.warning(self, "Attenzione", "Seleziona almeno un tipo di penalità!")
            return
        
        try:
            db = SessionLocal()
            
            # Crea una nuova penalità
            penalita = Penalita(
                iscrizione_id=self.iscrizione_id,
                sessione_tipo=sessione_tipo,
                gruppo_id=gruppo_id,
                tipo_infrazione=self.infraction_combo.currentText(),
                descrizione=self.description_edit.toPlainText(),
                posizioni_penalita=self.position_spin.value() if self.position_penalty_check.isChecked() else 0,
                tempo_penalita=self.time_spin.value() if self.time_penalty_check.isChecked() else 0,
                cancella_miglior_tempo=self.best_time_check.isChecked(),
                esclusione=self.exclusion_check.isChecked(),
                data_ora=QDateTime.currentDateTime().toPython()
            )
            
            db.add(penalita)
            db.commit()
            
            QMessageBox.information(self, "Operazione completata", "Penalità aggiunta con successo!")
            
            super().accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante il salvataggio: {str(e)}")
        finally:
            db.close()