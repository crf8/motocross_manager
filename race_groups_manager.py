# ui/race_groups_manager.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLabel, QComboBox, QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QMessageBox, QGroupBox,
    QTabWidget, QRadioButton, QButtonGroup, QSpinBox, QDialog,
    QDialogButtonBox, QListWidget, QListWidgetItem, QSplitter, QLineEdit
)
from PyQt6.QtCore import Qt, QTimer, QDateTime
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from database.connection import SessionLocal
from database.models import Evento, Iscrizione, Pilota, Categoria, Gruppo, PartecipazioneGruppo, LapTime, Risultato

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QLabel
)

class QualificationGroupsTab(QWidget):
    """Tab per la creazione automatica dei gruppi in base alle qualifiche"""
    
    def __init__(self):
        super().__init__()
        
        # Layout principale
        layout = QVBoxLayout(self)
        
        # Selettori
        selectors_layout = QFormLayout()
        
        self.event_combo = QComboBox()
        selectors_layout.addRow("Evento:", self.event_combo)
        
        self.session_combo = QComboBox()
        self.session_combo.addItems(["Gara 1", "Gara 2"])
        selectors_layout.addRow("Sessione:", self.session_combo)
        
        self.category_combo = QComboBox()
        selectors_layout.addRow("Categoria:", self.category_combo)
        
        layout.addLayout(selectors_layout)
        
        # Opzioni di raggruppamento
        grouping_group = QGroupBox("Opzioni di Raggruppamento")
        grouping_layout = QVBoxLayout()
        
        self.max_riders_per_group = QSpinBox()
        self.max_riders_per_group.setMinimum(20)
        self.max_riders_per_group.setMaximum(50)
        self.max_riders_per_group.setValue(40)  # Valore predefinito da regolamento
        grouping_layout.addWidget(QLabel("Numero massimo di piloti per gruppo:"))
        grouping_layout.addWidget(self.max_riders_per_group)
        
        grouping_group.setLayout(grouping_layout)
        layout.addWidget(grouping_group)
        
        # Bottone per generare i gruppi
        self.generate_button = QPushButton("Genera Gruppi")
        # self.generate_button.clicked.connect(self.generate_groups)
        layout.addWidget(self.generate_button)
        
        # Tabella risultante
        self.groups_table = QTableWidget(0, 4)
        self.groups_table.setHorizontalHeaderLabels([
            "Gruppo", "Categoria", "N. Piloti", "Durata Gara"
        ])
        self.groups_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.groups_table)
        
        # Bottone per salvare i gruppi
        self.save_button = QPushButton("Salva Gruppi nel Database")
        # self.save_button.clicked.connect(self.save_groups)
        layout.addWidget(self.save_button)
        
        # Carica eventi e categorie
        # self.load_events()

class RaceGroupsManager(QWidget):
    """Gestione completa dei gruppi di gara"""
    
    def __init__(self):
        super().__init__()
        
        # Layout principale
        layout = QVBoxLayout(self)
        
        # Titolo
        title_label = QLabel("Gestione Gruppi di Gara")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Schede per le diverse funzionalità
        self.tabs = QTabWidget()
        
        # Tab per creare i gruppi da qualifiche
        self.qualification_groups_tab = QualificationGroupsTab()
        self.tabs.addTab(self.qualification_groups_tab, "Gruppi da Qualifiche")

        # Tab per il cronometraggio delle gare
        self.race_timing_tab = RaceTimingTab()
        self.tabs.addTab(self.race_timing_tab, "Cronometraggio Gare")
        
        layout.addWidget(self.tabs)

def create_new_group(self):
    """Crea un nuovo gruppo"""
    evento_id = self.event_combo.currentData()
    session_type = self.session_combo.currentText()
    
    if not evento_id:
        QMessageBox.warning(self, "Avviso", "Seleziona un evento!")
        return
    
    # Creiamo una finestra di dialogo per inserire le informazioni del gruppo
    dialog = QDialog(self)
    dialog.setWindowTitle("Nuovo Gruppo")
    layout = QVBoxLayout(dialog)
    
    form_layout = QFormLayout()
    
    # Campo per il nome del gruppo
    name_edit = QLineEdit()
    name_edit.setPlaceholderText("Es. Gruppo A")
    form_layout.addRow("Nome gruppo:", name_edit)
    
    # Limite di piloti
    limit_spin = QSpinBox()
    limit_spin.setMinimum(5)
    limit_spin.setMaximum(50)
    limit_spin.setValue(40)  # Valore predefinito da regolamento
    form_layout.addRow("Limite piloti:", limit_spin)
    
    layout.addLayout(form_layout)
    
    # Bottoni
    buttons = QDialogButtonBox(
        QDialogButtonBox.StandardButton.Ok | 
        QDialogButtonBox.StandardButton.Cancel
    )
    buttons.accepted.connect(dialog.accept)
    buttons.rejected.connect(dialog.reject)
    layout.addWidget(buttons)
    
    # Mostra la finestra di dialogo
    if dialog.exec() == QDialog.DialogCode.Accepted:
        nome_gruppo = name_edit.text().strip()
        limite_piloti = limit_spin.value()
        
        if not nome_gruppo:
            QMessageBox.warning(self, "Errore", "Il nome del gruppo non può essere vuoto!")
            return
        
        try:
            db = SessionLocal()
            
            # Crea il nuovo gruppo
            nuovo_gruppo = Gruppo(
                evento_id=evento_id,
                nome=nome_gruppo,
                tipo_sessione=session_type,
                limite_piloti=limite_piloti
            )
            
            db.add(nuovo_gruppo)
            db.commit()
            
            # Aggiorna la lista dei gruppi
            self.load_groups()
            
            QMessageBox.information(self, "Successo", "Gruppo creato con successo!")
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore nella creazione del gruppo: {str(e)}")
        finally:
            db.close()

def delete_group(self):
    """Elimina il gruppo selezionato"""
    current_row = self.groups_list.currentRow()
    if current_row < 0:
        QMessageBox.warning(self, "Avviso", "Seleziona un gruppo da eliminare!")
        return
    
    group_id = self.groups_list.item(current_row).data(Qt.ItemDataRole.UserRole)
    group_name = self.groups_list.item(current_row).text()
    
    # Chiedi conferma
    reply = QMessageBox.question(
        self, "Conferma eliminazione", 
        f"Sei sicuro di voler eliminare {group_name}?",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    
    if reply == QMessageBox.StandardButton.Yes:
        try:
            db = SessionLocal()
            
            # Elimina prima le partecipazioni
            db.query(PartecipazioneGruppo).filter(
                PartecipazioneGruppo.gruppo_id == group_id
            ).delete()
            
            # Elimina il gruppo
            db.query(Gruppo).filter(Gruppo.id == group_id).delete()
            
            db.commit()
            
            # Aggiorna la lista
            self.load_groups()
            
            # Pulisci la tabella piloti
            self.pilots_table.setRowCount(0)
            
            QMessageBox.information(self, "Successo", "Gruppo eliminato con successo!")
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore nell'eliminazione del gruppo: {str(e)}")
        finally:
            db.close()

def add_pilot_to_group(self):
    """Aggiunge un pilota al gruppo selezionato"""
    current_row = self.groups_list.currentRow()
    if current_row < 0:
        QMessageBox.warning(self, "Avviso", "Seleziona un gruppo prima!")
        return
    
    group_id = self.groups_list.item(current_row).data(Qt.ItemDataRole.UserRole)
    
    # Creiamo una finestra di dialogo per selezionare il pilota
    dialog = QDialog(self)
    dialog.setWindowTitle("Aggiungi Pilota al Gruppo")
    dialog.resize(500, 400)
    layout = QVBoxLayout(dialog)
    
    # Label istruzioni
    layout.addWidget(QLabel("Seleziona un pilota da aggiungere al gruppo:"))
    
    # Lista piloti disponibili
    pilots_list = QTableWidget(0, 4)
    pilots_list.setHorizontalHeaderLabels(["ID", "Numero", "Pilota", "Categoria"])
    layout.addWidget(pilots_list)
    
    # Carica i piloti disponibili (quelli iscritti all'evento ma non in questo gruppo)
    try:
        db = SessionLocal()
        
        # Ottieni il gruppo per avere l'evento_id
        gruppo = db.query(Gruppo).get(group_id)
        if not gruppo:
            QMessageBox.critical(dialog, "Errore", "Gruppo non trovato!")
            db.close()
            return
        
        evento_id = gruppo.evento_id
        
        # Ottieni gli ID delle iscrizioni già nel gruppo
        partecipazioni = db.query(PartecipazioneGruppo).filter(
            PartecipazioneGruppo.gruppo_id == group_id
        ).all()
        
        iscrizioni_presenti = [p.iscrizione_id for p in partecipazioni]
        
        # Ottieni le iscrizioni all'evento che non sono già nel gruppo
        iscrizioni = db.query(Iscrizione).filter(
            Iscrizione.evento_id == evento_id,
            ~Iscrizione.id.in_(iscrizioni_presenti) if iscrizioni_presenti else True
        ).all()
        
        # Popoliamo la tabella
        for iscrizione in iscrizioni:
            row = pilots_list.rowCount()
            pilots_list.insertRow(row)
            
            pilots_list.setItem(row, 0, QTableWidgetItem(str(iscrizione.id)))
            pilots_list.setItem(row, 1, QTableWidgetItem(str(iscrizione.numero_gara)))
            pilots_list.setItem(row, 2, QTableWidgetItem(f"{iscrizione.pilota.nome} {iscrizione.pilota.cognome}"))
            pilots_list.setItem(row, 3, QTableWidgetItem(f"{iscrizione.categoria.classe} {iscrizione.categoria.categoria}"))
        
        # Ridimensiona le colonne
        pilots_list.resizeColumnsToContents()
        
    except Exception as e:
        QMessageBox.critical(dialog, "Errore", f"Errore nel caricamento piloti: {str(e)}")
        db.close()
        return
    
    # Bottoni
    buttons = QDialogButtonBox(
        QDialogButtonBox.StandardButton.Ok | 
        QDialogButtonBox.StandardButton.Cancel
    )
    buttons.accepted.connect(dialog.accept)
    buttons.rejected.connect(dialog.reject)
    layout.addWidget(buttons)
    
    # Mostra la finestra di dialogo
    if dialog.exec() == QDialog.DialogCode.Accepted:
        # Ottieni il pilota selezionato
        selected_items = pilots_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Avviso", "Nessun pilota selezionato!")
            return
        
        iscrizione_id = int(pilots_list.item(selected_items[0].row(), 0).text())
        
        try:
            # Calcola la prossima posizione in griglia
            next_pos = db.query(PartecipazioneGruppo).filter(
                PartecipazioneGruppo.gruppo_id == group_id
            ).count() + 1
            
            # Aggiungi il pilota al gruppo
            partecipazione = PartecipazioneGruppo(
                gruppo_id=group_id,
                iscrizione_id=iscrizione_id,
                posizione_griglia=next_pos
            )
            
            db.add(partecipazione)
            db.commit()
            
            # Aggiorna la visualizzazione
            self.load_group_pilots(current_row)
            
            # Aggiorna anche il testo nella lista dei gruppi
            group_text = self.groups_list.item(current_row).text()
            count_start = group_text.find('(')
            if count_start > 0:
                base_text = group_text[:count_start].strip()
                self.groups_list.item(current_row).setText(f"{base_text} ({next_pos} piloti)")
            
            QMessageBox.information(self, "Successo", "Pilota aggiunto al gruppo!")
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore nell'aggiunta del pilota: {str(e)}")
        finally:
            db.close()

# Aggiungeremo le funzioni rimanenti per completare questa classe...

class RaceResultsTab(QWidget):
    """Tab per visualizzare e gestire i risultati delle gare"""
    
    def __init__(self):
        super().__init__()
        
        # Layout principale
        layout = QVBoxLayout(self)
        
        # Selettori
        selectors_layout = QFormLayout()
        
        self.event_combo = QComboBox()
        selectors_layout.addRow("Evento:", self.event_combo)
        
        self.session_combo = QComboBox()
        self.session_combo.addItems(["Gara 1", "Gara 2", "Supercampione"])
        selectors_layout.addRow("Sessione:", self.session_combo)
        
        self.group_combo = QComboBox()
        selectors_layout.addRow("Gruppo:", self.group_combo)
        
        layout.addLayout(selectors_layout)
        
        # Bottone per caricare i risultati
        self.load_button = QPushButton("Carica Risultati")
        self.load_button.clicked.connect(self.load_results)
        layout.addWidget(self.load_button)
        
        # Tabella risultati
        self.results_table = QTableWidget(0, 8)
        self.results_table.setHorizontalHeaderLabels([
            "Pos", "Num", "Pilota", "Categoria", "Tempo Totale", "Miglior Giro", "Distacco", "Punti"
        ])
        layout.addWidget(self.results_table)
        
        # Bottoni azioni
        buttons_layout = QHBoxLayout()
        
        self.calculate_button = QPushButton("Calcola Classifica")
        self.calculate_button.clicked.connect(self.calculate_results)
        buttons_layout.addWidget(self.calculate_button)
        
        self.save_button = QPushButton("Salva Risultati")
        self.save_button.clicked.connect(self.save_results)
        buttons_layout.addWidget(self.save_button)
        
        self.export_button = QPushButton("Esporta Risultati")
        self.export_button.clicked.connect(self.export_results)
        buttons_layout.addWidget(self.export_button)
        
        layout.addLayout(buttons_layout)
        
        # Carica eventi
        self.load_events()
        
        # Collega eventi combo
        self.event_combo.currentIndexChanged.connect(self.load_groups_combo)


    def remove_pilot_from_group(self):
        """Rimuove un pilota dal gruppo selezionato"""
        # Controlliamo prima se hai selezionato un gruppo
        current_group_row = self.groups_list.currentRow()
        if current_group_row < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona prima un gruppo!")
            return
        
        # Controlliamo se hai selezionato un pilota nella tabella
        selected_rows = self.pilots_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Attenzione", "Seleziona un pilota da rimuovere!")
            return
        
        # Otteniamo l'ID del gruppo e dell'iscrizione (pilota)
        group_id = self.groups_list.item(current_group_row).data(Qt.ItemDataRole.UserRole)
        row = selected_rows[0].row()
        iscrizione_id = self.pilots_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        # Chiediamo conferma prima di rimuovere
        pilota_nome = self.pilots_table.item(row, 2).text()
        reply = QMessageBox.question(
            self, "Conferma rimozione", 
            f"Sei sicuro di voler rimuovere {pilota_nome} dal gruppo?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                db = SessionLocal()
                
                # Rimuoviamo il pilota dal gruppo
                db.query(PartecipazioneGruppo).filter(
                    PartecipazioneGruppo.gruppo_id == group_id,
                    PartecipazioneGruppo.iscrizione_id == iscrizione_id
                ).delete()
                
                db.commit()
                
                # Aggiorniamo la visualizzazione
                self.load_group_pilots(current_group_row)
                
                # Aggiorniamo anche il conteggio nella lista dei gruppi
                count = db.query(PartecipazioneGruppo).filter(
                    PartecipazioneGruppo.gruppo_id == group_id
                ).count()
                
                group_text = self.groups_list.item(current_group_row).text()
                count_start = group_text.find('(')
                if count_start > 0:
                    base_text = group_text[:count_start].strip()
                    self.groups_list.item(current_group_row).setText(f"{base_text} ({count} piloti)")
                
                QMessageBox.information(self, "Operazione completata", "Pilota rimosso dal gruppo!")
                
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Errore durante la rimozione del pilota: {str(e)}")
            finally:
                db.close()

def move_pilot_up(self):
    """Sposta il pilota selezionato verso l'alto nella griglia"""
    # Controlliamo se hai selezionato un gruppo e un pilota
    current_group_row = self.groups_list.currentRow()
    if current_group_row < 0:
        QMessageBox.warning(self, "Attenzione", "Seleziona prima un gruppo!")
        return
    
    selected_rows = self.pilots_table.selectedItems()
    if not selected_rows:
        QMessageBox.warning(self, "Attenzione", "Seleziona un pilota da spostare!")
        return
    
    # Otteniamo la riga del pilota selezionato
    row = selected_rows[0].row()
    
    # Se è già in cima, non possiamo spostarlo più su
    if row == 0:
        QMessageBox.information(self, "Informazione", "Il pilota è già in prima posizione!")
        return
    
    try:
        # Otteniamo gli ID necessari
        group_id = self.groups_list.item(current_group_row).data(Qt.ItemDataRole.UserRole)
        iscrizione_id = self.pilots_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        iscrizione_id_sopra = self.pilots_table.item(row-1, 0).data(Qt.ItemDataRole.UserRole)
        
        db = SessionLocal()
        
        # Otteniamo le partecipazioni da scambiare
        partecipazione = db.query(PartecipazioneGruppo).filter(
            PartecipazioneGruppo.gruppo_id == group_id,
            PartecipazioneGruppo.iscrizione_id == iscrizione_id
        ).first()
        
        partecipazione_sopra = db.query(PartecipazioneGruppo).filter(
            PartecipazioneGruppo.gruppo_id == group_id,
            PartecipazioneGruppo.iscrizione_id == iscrizione_id_sopra
        ).first()
        
        # Scambiamo le posizioni
        pos_temp = partecipazione.posizione_griglia
        partecipazione.posizione_griglia = partecipazione_sopra.posizione_griglia
        partecipazione_sopra.posizione_griglia = pos_temp
        
        db.commit()
        
        # Aggiorniamo la visualizzazione
        self.load_group_pilots(current_group_row)
        
        # Selezioniamo la nuova riga del pilota (ora è più in alto)
        self.pilots_table.selectRow(row-1)
        
    except Exception as e:
        QMessageBox.critical(self, "Errore", f"Errore durante lo spostamento: {str(e)}")
    finally:
        db.close()

def move_pilot_down(self):
    """Sposta il pilota selezionato verso il basso nella griglia"""
    # Controlliamo se hai selezionato un gruppo e un pilota
    current_group_row = self.groups_list.currentRow()
    if current_group_row < 0:
        QMessageBox.warning(self, "Attenzione", "Seleziona prima un gruppo!")
        return
    
    selected_rows = self.pilots_table.selectedItems()
    if not selected_rows:
        QMessageBox.warning(self, "Attenzione", "Seleziona un pilota da spostare!")
        return
    
    # Otteniamo la riga del pilota selezionato
    row = selected_rows[0].row()
    
    # Se è già in fondo, non possiamo spostarlo più giù
    if row == self.pilots_table.rowCount() - 1:
        QMessageBox.information(self, "Informazione", "Il pilota è già in ultima posizione!")
        return
    
    try:
        # Otteniamo gli ID necessari
        group_id = self.groups_list.item(current_group_row).data(Qt.ItemDataRole.UserRole)
        iscrizione_id = self.pilots_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        iscrizione_id_sotto = self.pilots_table.item(row+1, 0).data(Qt.ItemDataRole.UserRole)
        
        db = SessionLocal()
        
        # Otteniamo le partecipazioni da scambiare
        partecipazione = db.query(PartecipazioneGruppo).filter(
            PartecipazioneGruppo.gruppo_id == group_id,
            PartecipazioneGruppo.iscrizione_id == iscrizione_id
        ).first()
        
        partecipazione_sotto = db.query(PartecipazioneGruppo).filter(
            PartecipazioneGruppo.gruppo_id == group_id,
            PartecipazioneGruppo.iscrizione_id == iscrizione_id_sotto
        ).first()
        
        # Scambiamo le posizioni
        pos_temp = partecipazione.posizione_griglia
        partecipazione.posizione_griglia = partecipazione_sotto.posizione_griglia
        partecipazione_sotto.posizione_griglia = pos_temp
        
        db.commit()
        
        # Aggiorniamo la visualizzazione
        self.load_group_pilots(current_group_row)
        
        # Selezioniamo la nuova riga del pilota (ora è più in basso)
        self.pilots_table.selectRow(row+1)
        
    except Exception as e:
        QMessageBox.critical(self, "Errore", f"Errore durante lo spostamento: {str(e)}")
    finally:
        db.close()

def save_changes(self):
    """Salva eventuali modifiche manuali alla posizione in griglia"""
    current_group_row = self.groups_list.currentRow()
    if current_group_row < 0:
        QMessageBox.warning(self, "Attenzione", "Seleziona prima un gruppo!")
        return
    
    group_id = self.groups_list.item(current_group_row).data(Qt.ItemDataRole.UserRole)
    
    # Otteniamo i dati modificati dalla tabella
    modified_data = []
    for row in range(self.pilots_table.rowCount()):
        pos = int(self.pilots_table.item(row, 0).text())
        iscrizione_id = self.pilots_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        modified_data.append((iscrizione_id, pos))
    
    try:
        db = SessionLocal()
        
        # Aggiorniamo le posizioni in griglia
        for iscrizione_id, pos in modified_data:
            db.query(PartecipazioneGruppo).filter(
                PartecipazioneGruppo.gruppo_id == group_id,
                PartecipazioneGruppo.iscrizione_id == iscrizione_id
            ).update({"posizione_griglia": pos})
        
        db.commit()
        
        # Ricarica per sicurezza
        self.load_group_pilots(current_group_row)
        
        QMessageBox.information(self, "Operazione completata", "Modifiche salvate con successo!")
        
    except Exception as e:
        QMessageBox.critical(self, "Errore", f"Errore durante il salvataggio: {str(e)}")
    finally:
        db.close()


# Completiamo la classe RaceResultsTab

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

def load_groups_combo(self):
    """Carica i gruppi disponibili per l'evento e la sessione selezionati"""
    evento_id = self.event_combo.currentData()
    session_type = self.session_combo.currentText()
    
    if not evento_id:
        return
    
    try:
        db = SessionLocal()
        
        gruppi = db.query(Gruppo).filter(
            Gruppo.evento_id == evento_id,
            Gruppo.tipo_sessione == session_type
        ).all()
        
        self.group_combo.clear()
        for gruppo in gruppi:
            self.group_combo.addItem(gruppo.nome, gruppo.id)
        
    except Exception as e:
        QMessageBox.critical(self, "Errore", f"Errore durante il caricamento gruppi: {str(e)}")
    finally:
        db.close()

# Modifica alla funzione load_results nella classe RaceResultsTab

def load_results(self):
    """Carica i risultati esistenti o prepara la tabella per nuovi risultati"""
    gruppo_id = self.group_combo.currentData()
    
    if not gruppo_id:
        QMessageBox.warning(self, "Attenzione", "Seleziona un gruppo!")
        return
    
    try:
        db = SessionLocal()
        
        # Otteniamo informazioni sul gruppo
        gruppo = db.query(Gruppo).get(gruppo_id)
        if not gruppo:
            QMessageBox.warning(self, "Attenzione", "Gruppo non trovato!")
            return
        
        # Otteniamo le partecipazioni al gruppo
        partecipazioni = db.query(PartecipazioneGruppo).filter(
            PartecipazioneGruppo.gruppo_id == gruppo_id
        ).order_by(PartecipazioneGruppo.posizione_griglia).all()
        
        if not partecipazioni:
            QMessageBox.warning(self, "Attenzione", "Nessun pilota nel gruppo!")
            return
        
        # Puliamo la tabella
        self.results_table.setRowCount(0)
        
        # Verifichiamo se esistono già risultati salvati
        session_type = self.session_type_combo.currentText()
        existing_results = {}
        
        results = db.query(Risultato).filter(
            Risultato.gruppo_id == gruppo_id,
            Risultato.sessione_tipo == session_type
        ).all()
        
        for result in results:
            existing_results[result.iscrizione_id] = {
                "posizione": result.posizione,
                "punti": result.punti,
                "best_lap_time": result.best_lap_time
            }
        
        # Ottieni le penalità per questo gruppo e sessione
        penalties = {}
        penalita_query = db.query(Penalita).filter(
            Penalita.gruppo_id == gruppo_id,
            Penalita.sessione_tipo == session_type
        ).all()
        
        for penalita in penalita_query:
            if penalita.iscrizione_id not in penalties:
                penalties[penalita.iscrizione_id] = []
            penalties[penalita.iscrizione_id].append(penalita)
        
        # Popoliamo la tabella
        for i, part in enumerate(partecipazioni):
            row = self.results_table.rowCount()
            self.results_table.insertRow(row)
            
            iscrizione = part.iscrizione
            pilota = iscrizione.pilota
            categoria = iscrizione.categoria
            
            # Se esiste un risultato salvato, lo usiamo
            if iscrizione.id in existing_results:
                result = existing_results[iscrizione.id]
                pos = result["posizione"]
                punti = result["punti"]
                best_time = result["best_lap_time"]
                best_time_str = self.format_time(best_time) if best_time else "-"
            else:
                # Altrimenti, inseriamo la posizione in griglia
                pos = part.posizione_griglia
                punti = 0  # I punti verranno calcolati
                
                # Cerchiamo il miglior tempo sul giro per questo pilota
                best_lap = db.query(LapTime).filter(
                    LapTime.iscrizione_id == iscrizione.id,
                    LapTime.sessione_tipo == session_type
                ).order_by(LapTime.tempo_ms).first()
                
                best_time = best_lap.tempo_ms if best_lap else None
                best_time_str = self.format_time(best_time) if best_time else "-"
            
            # Aggiungiamo i dati alla tabella
            self.results_table.setItem(row, 0, QTableWidgetItem(str(pos)))
            self.results_table.setItem(row, 1, QTableWidgetItem(str(iscrizione.numero_gara)))
            self.results_table.setItem(row, 2, QTableWidgetItem(f"{pilota.nome} {pilota.cognome}"))
            self.results_table.setItem(row, 3, QTableWidgetItem(f"{categoria.classe} {categoria.categoria}"))
            self.results_table.setItem(row, 4, QTableWidgetItem("-"))  # Tempo totale (da calcolare)
            self.results_table.setItem(row, 5, QTableWidgetItem(best_time_str))  # Miglior giro
            self.results_table.setItem(row, 6, QTableWidgetItem("-"))  # Distacco (da calcolare)
            self.results_table.setItem(row, 7, QTableWidgetItem(str(punti)))  # Punti
            
            # Memorizziamo l'ID dell'iscrizione
            self.results_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, iscrizione.id)
            
            # Memorizziamo anche il miglior tempo per i calcoli
            self.results_table.item(row, 5).setData(Qt.ItemDataRole.UserRole, best_time)
            
            # Se il pilota ha penalità, lo evidenziamo e aggiungiamo info
            if iscrizione.id in penalties:
                # Elenco delle penalità per questo pilota
                penalty_text = []
                for penalita in penalties[iscrizione.id]:
                    if penalita.esclusione:
                        penalty_text.append("ESC")
                    elif penalita.posizioni_penalita > 0:
                        penalty_text.append(f"+{penalita.posizioni_penalita}P")
                    elif penalita.tempo_penalita > 0:
                        penalty_text.append(f"+{penalita.tempo_penalita}S")
                    elif penalita.cancella_miglior_tempo:
                        penalty_text.append("CBT")  # Cancellazione Best Time
                
                # Aggiungiamo le penalità alla colonna nome
                pilota_con_penalita = f"{pilota.nome} {pilota.cognome} ({', '.join(penalty_text)})"
                self.results_table.setItem(row, 2, QTableWidgetItem(pilota_con_penalita))
                
                # Coloriamo di rosso la riga per evidenziare la penalità
                for col in range(self.results_table.columnCount()):
                    item = self.results_table.item(row, col)
                    if item:
                        item.setBackground(QColor(255, 200, 200))  # Rosso chiaro
        
        # Ridimensioniamo le colonne
        self.results_table.resizeColumnsToContents()
        
    except Exception as e:
        QMessageBox.critical(self, "Errore", f"Errore durante il caricamento risultati: {str(e)}")
    finally:
        db.close()

def calculate_results(self):
    """Calcola la classifica finale della gara considerando anche le penalità"""
    if self.results_table.rowCount() == 0:
        QMessageBox.warning(self, "Attenzione", "Nessun risultato da calcolare!")
        return
    
    # Chiediamo conferma
    reply = QMessageBox.question(
        self, "Conferma calcolo", 
        "Vuoi calcolare la classifica finale con le eventuali penalità?",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    
    if reply != QMessageBox.StandardButton.Yes:
        return
    
    try:
        db = SessionLocal()
        gruppo_id = self.group_combo.currentData()
        session_type = self.session_type_combo.currentText()
        
        # Raccogliamo i dati della tabella
        results_data = []
        for row in range(self.results_table.rowCount()):
            iscrizione_id = self.results_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            numero = self.results_table.item(row, 1).text()
            pilota = self.results_table.item(row, 2).text()
            categoria = self.results_table.item(row, 3).text()
            best_time = self.results_table.item(row, 5).data(Qt.ItemDataRole.UserRole)
            
            # Otteniamo le penalità per questo pilota
            penalita_list = db.query(Penalita).filter(
                Penalita.iscrizione_id == iscrizione_id,
                Penalita.gruppo_id == gruppo_id,
                Penalita.sessione_tipo == session_type
            ).all()
            
            # Calcoliamo il tempo totale con le penalità
            pos_penalty = 0
            time_penalty_ms = 0
            is_excluded = False
            cancel_best_time = False
            
            for penalita in penalita_list:
                pos_penalty += penalita.posizioni_penalita
                time_penalty_ms += penalita.tempo_penalita * 1000  # Convertiamo secondi in ms
                is_excluded = is_excluded or penalita.esclusione
                cancel_best_time = cancel_best_time or penalita.cancella_miglior_tempo
            
            # Se il pilota è escluso, lo mettiamo in fondo
            if is_excluded:
                effective_time = float('inf')
            # Se dobbiamo cancellare il miglior tempo, usiamo un tempo molto alto
            elif cancel_best_time:
                effective_time = float('inf') - 1  # Un po' meglio di escluso
            # Altrimenti usiamo il tempo effettivo con le penalità
            else:
                effective_time = (best_time if best_time else float('inf')) + time_penalty_ms
            
            results_data.append({
                "row": row,
                "iscrizione_id": iscrizione_id,
                "numero": numero,
                "pilota": pilota,
                "categoria": categoria,
                "best_time": best_time if best_time else float('inf'),
                "effective_time": effective_time,
                "time_penalty_ms": time_penalty_ms,
                "pos_penalty": pos_penalty,
                "is_excluded": is_excluded,
                "cancel_best_time": cancel_best_time
            })
        
        # Ordiniamo per tempo effettivo (che include le penalità)
        results_data.sort(key=lambda x: x["effective_time"])
        
        # Applichiamo le penalità di posizione dopo l'ordinamento iniziale
        if any(result["pos_penalty"] > 0 for result in results_data):
            # Creiamo una copia dell'ordinamento iniziale
            initial_order = results_data.copy()
            
            # Per ogni pilota con penalità di posizione, lo spostiamo indietro
            for i, result in enumerate(initial_order):
                if result["pos_penalty"] > 0:
                    # Calcoliamo la nuova posizione applicando la penalità
                    new_pos = min(i + result["pos_penalty"], len(results_data) - 1)
                    
                    # Rimuoviamo il pilota dalla sua posizione attuale
                    pilot_to_move = results_data[i]
                    results_data.remove(pilot_to_move)
                    
                    # Lo inseriamo nella nuova posizione
                    results_data.insert(new_pos, pilot_to_move)
        
        # Calcoliamo i punti secondo la tabella del regolamento
        punti_tabella = self.get_points_table(len(results_data))
        
        # Aggiorniamo la tabella con i nuovi dati
        for i, result in enumerate(results_data):
            pos = i + 1
            punti = punti_tabella.get(pos, 0) if not result["is_excluded"] else 0
            
            # Calcoliamo il distacco dal primo
            if i == 0:
                distacco = "-"
                best_time = result["best_time"]
            else:
                if result["best_time"] != float('inf') and results_data[0]["best_time"] != float('inf'):
                    diff_ms = result["best_time"] - results_data[0]["best_time"]
                    distacco = f"+{diff_ms/1000:.3f}s"
                    
                    # Aggiungiamo le penalità di tempo al distacco
                    if result["time_penalty_ms"] > 0:
                        distacco += f" (+{result['time_penalty_ms']/1000:.1f}s)"
                else:
                    distacco = "-"
            
            # Aggiorniamo la riga
            row = result["row"]
            self.results_table.setItem(row, 0, QTableWidgetItem(str(pos)))
            self.results_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, result["iscrizione_id"])
            
            # Modifichiamo il testo del pilota per mostrare le penalità
            pilota_text = result["pilota"]
            if result["is_excluded"]:
                pilota_text += " [ESCLUSO]"
            elif result["pos_penalty"] > 0:
                pilota_text += f" [+{result['pos_penalty']} pos.]"
            if result["time_penalty_ms"] > 0:
                pilota_text += f" [+{result['time_penalty_ms']/1000:.1f}s]"
            if result["cancel_best_time"]:
                pilota_text += " [Miglior tempo annullato]"
            
            self.results_table.setItem(row, 2, QTableWidgetItem(pilota_text))
            self.results_table.setItem(row, 6, QTableWidgetItem(distacco))
            self.results_table.setItem(row, 7, QTableWidgetItem(str(punti)))
        
        # Riordiniamo la tabella in base alla nuova posizione
        self.results_table.sortItems(0, Qt.SortOrder.AscendingOrder)
        
        QMessageBox.information(self, "Operazione completata", "Classifica calcolata con successo!")
        
    except Exception as e:
        QMessageBox.critical(self, "Errore", f"Errore durante il calcolo della classifica: {str(e)}")
    finally:
        db.close()

def get_points_table(self, num_pilots):
    """Restituisce la tabella dei punti in base al numero di piloti"""
    # Punti secondo il regolamento FMI
    if num_pilots <= 40:  # Impianti con 40 partenti
        return {
            1: 250, 2: 210, 3: 170, 4: 140, 5: 120, 6: 110, 7: 100, 8: 90, 9: 85, 10: 80,
            11: 77, 12: 74, 13: 72, 14: 70, 15: 68, 16: 66, 17: 64, 18: 63, 19: 62, 20: 61,
            21: 60, 22: 59, 23: 58, 24: 57, 25: 56, 26: 55, 27: 54, 28: 53, 29: 52, 30: 51,
            31: 50, 32: 49, 33: 48, 34: 47, 35: 46, 36: 45, 37: 44, 38: 43, 39: 42, 40: 41
        }
    else:  # Impianti con più di 40 partenti (gruppi A, B, C)
        # Per il gruppo A
        return {
            1: 250, 2: 210, 3: 170, 4: 140, 5: 120, 6: 110, 7: 100, 8: 90, 9: 85, 10: 80,
            11: 77, 12: 74, 13: 72, 14: 70, 15: 68, 16: 66, 17: 64, 18: 63, 19: 62, 20: 61,
            # ...continua secondo regolamento
        }

def format_time(self, time_ms):
    """Formatta il tempo in millisecondi come MM:SS.mmm"""
    if not time_ms:
        return "-"
    
    secs = time_ms // 1000
    mins = secs // 60
    secs %= 60
    msecs = time_ms % 1000
    return f"{mins:02d}:{secs:02d}.{msecs:03d}"

def save_results(self):
    """Salva i risultati nel database"""
    gruppo_id = self.group_combo.currentData()
    session_type = self.session_combo.currentText()
    
    if not gruppo_id:
        QMessageBox.warning(self, "Attenzione", "Seleziona un gruppo!")
        return
    
    if self.results_table.rowCount() == 0:
        QMessageBox.warning(self, "Attenzione", "Nessun risultato da salvare!")
        return
    
    try:
        db = SessionLocal()
        
        # Verifichiamo se esistono già risultati per questo gruppo/sessione
        existing = db.query(Risultato).filter(
            Risultato.gruppo_id == gruppo_id,
            Risultato.sessione_tipo == session_type
        ).all()
        
        if existing:
            reply = QMessageBox.question(
                self, "Risultati esistenti", 
                "Esistono già risultati salvati per questo gruppo/sessione. Vuoi sovrascriverli?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                return
            
            # Eliminiamo i risultati esistenti
            for result in existing:
                db.delete(result)
        
        # Salviamo i nuovi risultati
        for row in range(self.results_table.rowCount()):
            iscrizione_id = self.results_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            posizione = int(self.results_table.item(row, 0).text())
            punti = int(self.results_table.item(row, 7).text())
            best_lap_time = self.results_table.item(row, 5).data(Qt.ItemDataRole.UserRole)
            
            risultato = Risultato(
                iscrizione_id=iscrizione_id,
                gruppo_id=gruppo_id,
                sessione_tipo=session_type,
                posizione=posizione,
                punti=punti,
                best_lap_time=best_lap_time
            )
            
            db.add(risultato)
        
        db.commit()
        
        QMessageBox.information(self, "Operazione completata", "Risultati salvati con successo!")
        
    except Exception as e:
        QMessageBox.critical(self, "Errore", f"Errore durante il salvataggio: {str(e)}")
    finally:
        db.close()

def export_results(self):
    """Esporta i risultati in un file CSV"""
    if self.results_table.rowCount() == 0:
        QMessageBox.warning(self, "Attenzione", "Nessun risultato da esportare!")
        return
    
    from PyQt6.QtWidgets import QFileDialog
    import csv
    
    # Apriamo il dialog per scegliere dove salvare
    file_path, _ = QFileDialog.getSaveFileName(
        self, "Salva Risultati", "", "File CSV (*.csv)"
    )
    
    if not file_path:
        return
    
    try:
        with open(file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            
            # Scriviamo l'intestazione
            headers = []
            for col in range(self.results_table.columnCount()):
                headers.append(self.results_table.horizontalHeaderItem(col).text())
            writer.writerow(headers)
            
            # Scriviamo i dati
            for row in range(self.results_table.rowCount()):
                row_data = []
                for col in range(self.results_table.columnCount()):
                    item = self.results_table.item(row, col)
                    row_data.append(item.text() if item else "")
                writer.writerow(row_data)
        
        QMessageBox.information(self, "Operazione completata", f"Risultati esportati in {file_path}")
        
    except Exception as e:
        QMessageBox.critical(self, "Errore", f"Errore durante l'esportazione: {str(e)}")


class SupercampioneTab(QWidget):
    """Tab per la gestione della gara Supercampione"""
    
    def __init__(self):
        super().__init__()
        
        # Creiamo il layout principale, come un foglio su cui disegnare
        layout = QVBoxLayout(self)
        
        # Aggiungiamo un titolo in alto
        title_label = QLabel("Gestione Gara Supercampione")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Aggiungiamo una spiegazione
        info_label = QLabel("La gara Supercampione seleziona i migliori piloti da ogni gruppo per una 'super gara' finale")
        layout.addWidget(info_label)
        
        # Selettori per evento 
        selectors_layout = QFormLayout()
        
        # Dropdown per scegliere l'evento
        self.event_combo = QComboBox()
        selectors_layout.addRow("Evento:", self.event_combo)
        
        # Dropdown per scegliere da quale gara prendere i risultati
        self.source_session_combo = QComboBox()
        self.source_session_combo.addItems(["Gara 1", "Gara 2"])
        selectors_layout.addRow("Gara sorgente:", self.source_session_combo)
        
        # Spinner per scegliere quanti piloti prendere da ogni gruppo
        self.pilots_per_group_spin = QSpinBox()
        self.pilots_per_group_spin.setRange(1, 10)
        self.pilots_per_group_spin.setValue(3)  # Default: primi 3 da ogni gruppo
        selectors_layout.addRow("Piloti da ogni gruppo:", self.pilots_per_group_spin)
        
        # Spinner per impostare il limite massimo di piloti
        self.max_pilots_spin = QSpinBox()
        self.max_pilots_spin.setRange(10, 50)
        self.max_pilots_spin.setValue(40)  # Default: massimo 40 piloti
        selectors_layout.addRow("Numero massimo piloti:", self.max_pilots_spin)
        
        layout.addLayout(selectors_layout)
        
        # Bottone per generare automaticamente il gruppo Supercampione
        self.generate_button = QPushButton("Genera Gruppo Supercampione")
        self.generate_button.clicked.connect(self.generate_supercampione)
        layout.addWidget(self.generate_button)
        
        # Tabella per visualizzare i piloti selezionati
        self.pilots_table = QTableWidget(0, 5)
        self.pilots_table.setHorizontalHeaderLabels([
            "Pos", "Num", "Pilota", "Categoria", "Gruppo originale"
        ])
        layout.addWidget(self.pilots_table)
        
        # Bottoni per gestire manualmente i piloti
        buttons_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Aggiungi Pilota")
        self.add_button.clicked.connect(self.add_pilot_manually)
        buttons_layout.addWidget(self.add_button)
        
        self.remove_button = QPushButton("Rimuovi Pilota")
        self.remove_button.clicked.connect(self.remove_pilot)
        buttons_layout.addWidget(self.remove_button)
        
        self.up_button = QPushButton("↑ Sposta Su")
        self.up_button.clicked.connect(self.move_pilot_up)
        buttons_layout.addWidget(self.up_button)
        
        self.down_button = QPushButton("↓ Sposta Giù")
        self.down_button.clicked.connect(self.move_pilot_down)
        buttons_layout.addWidget(self.down_button)
        
        layout.addLayout(buttons_layout)
        
        # Bottone per salvare il gruppo Supercampione
        self.save_button = QPushButton("Salva Gruppo Supercampione")
        self.save_button.clicked.connect(self.save_supercampione)
        layout.addWidget(self.save_button)
        
        # Carichiamo gli eventi disponibili
        self.load_events()
    
    def load_events(self):
        """Carica gli eventi disponibili nel dropdown"""
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
    
    def generate_supercampione(self):
        """Genera automaticamente il gruppo Supercampione"""
        evento_id = self.event_combo.currentData()
        source_session = self.source_session_combo.currentText()
        pilots_per_group = self.pilots_per_group_spin.value()
        max_pilots = self.max_pilots_spin.value()
        
        if not evento_id:
            QMessageBox.warning(self, "Attenzione", "Seleziona un evento!")
            return
        
        try:
            db = SessionLocal()
            
            # Otteniamo tutti i gruppi per la gara sorgente
            gruppi = db.query(Gruppo).filter(
                Gruppo.evento_id == evento_id,
                Gruppo.tipo_sessione == source_session
            ).all()
            
            if not gruppi:
                QMessageBox.warning(self, "Attenzione", 
                                   f"Non ci sono gruppi per {source_session} in questo evento!")
                return
            
            # Lista per memorizzare i piloti selezionati
            selected_pilots = []
            
            # Per ogni gruppo, prendiamo i migliori piloti
            for gruppo in gruppi:
                # Otteniamo i risultati di questo gruppo, ordinati per posizione
                risultati = db.query(Risultato).filter(
                    Risultato.gruppo_id == gruppo.id,
                    Risultato.sessione_tipo == source_session
                ).order_by(Risultato.posizione).limit(pilots_per_group).all()
                
                for risultato in risultati:
                    iscrizione = risultato.iscrizione
                    pilota = iscrizione.pilota
                    categoria = iscrizione.categoria
                    
                    selected_pilots.append({
                        "iscrizione_id": iscrizione.id,
                        "numero_gara": iscrizione.numero_gara,
                        "pilota": f"{pilota.nome} {pilota.cognome}",
                        "categoria": f"{categoria.classe} {categoria.categoria}",
                        "gruppo_originale": gruppo.nome,
                        "posizione_originale": risultato.posizione
                    })
            
            # Se non abbiamo trovato piloti, mostriamo un avviso
            if not selected_pilots:
                QMessageBox.warning(self, "Attenzione", 
                                   "Nessun risultato trovato per creare il Supercampione!")
                return
            
            # Limitiamo il numero di piloti al massimo specificato
            selected_pilots = selected_pilots[:max_pilots]
            
            # Visualizziamo i piloti selezionati nella tabella
            self.pilots_table.setRowCount(0)
            
            for i, pilot in enumerate(selected_pilots):
                row = self.pilots_table.rowCount()
                self.pilots_table.insertRow(row)
                
                self.pilots_table.setItem(row, 0, QTableWidgetItem(str(i+1)))
                self.pilots_table.setItem(row, 1, QTableWidgetItem(str(pilot["numero_gara"])))
                self.pilots_table.setItem(row, 2, QTableWidgetItem(pilot["pilota"]))
                self.pilots_table.setItem(row, 3, QTableWidgetItem(pilot["categoria"]))
                self.pilots_table.setItem(row, 4, QTableWidgetItem(pilot["gruppo_originale"]))
                
                # Salviamo l'ID dell'iscrizione nella tabella
                self.pilots_table.item(row, 0).setData(
                    Qt.ItemDataRole.UserRole, pilot["iscrizione_id"]
                )
            
            # Ridimensioniamo le colonne
            self.pilots_table.resizeColumnsToContents()
            
            QMessageBox.information(self, "Operazione completata", 
                                   f"Selezionati {len(selected_pilots)} piloti per il Supercampione!")
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", 
                               f"Errore durante la generazione del Supercampione: {str(e)}")
        finally:
            db.close()
    
    def add_pilot_manually(self):
        """Aggiunge manualmente un pilota al gruppo Supercampione"""
        evento_id = self.event_combo.currentData()
        
        if not evento_id:
            QMessageBox.warning(self, "Attenzione", "Seleziona un evento!")
            return
        
        # Creiamo una finestra di dialogo per selezionare il pilota
        dialog = QDialog(self)
        dialog.setWindowTitle("Aggiungi Pilota al Supercampione")
        dialog.resize(500, 400)
        layout = QVBoxLayout(dialog)
        
        # Etichetta con istruzioni
        layout.addWidget(QLabel("Seleziona un pilota da aggiungere:"))
        
        # Tabella per mostrare i piloti disponibili
        pilots_table = QTableWidget(0, 4)
        pilots_table.setHorizontalHeaderLabels([
            "ID", "Numero", "Pilota", "Categoria"
        ])
        layout.addWidget(pilots_table)
        
        try:
            # Connettiamo al database
            db = SessionLocal()
            
            # Otteniamo tutti i piloti iscritti all'evento
            iscrizioni = db.query(Iscrizione).filter(
                Iscrizione.evento_id == evento_id
            ).all()
            
            # Otteniamo gli ID delle iscrizioni già presenti nella tabella
            existing_ids = []
            for row in range(self.pilots_table.rowCount()):
                existing_ids.append(
                    self.pilots_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
                )
            
            # Filtriamo i piloti che non sono già nella tabella
            for iscrizione in iscrizioni:
                if iscrizione.id not in existing_ids:
                    row = pilots_table.rowCount()
                    pilots_table.insertRow(row)
                    
                    pilots_table.setItem(row, 0, QTableWidgetItem(str(iscrizione.id)))
                    pilots_table.setItem(row, 1, QTableWidgetItem(str(iscrizione.numero_gara)))
                    pilots_table.setItem(row, 2, QTableWidgetItem(
                        f"{iscrizione.pilota.nome} {iscrizione.pilota.cognome}"
                    ))
                    pilots_table.setItem(row, 3, QTableWidgetItem(
                        f"{iscrizione.categoria.classe} {iscrizione.categoria.categoria}"
                    ))
            
            # Ridimensioniamo le colonne
            pilots_table.resizeColumnsToContents()
            
        except Exception as e:
            QMessageBox.critical(dialog, "Errore", 
                               f"Errore durante il caricamento piloti: {str(e)}")
            db.close()
            return
        
        # Bottoni per confermare o annullare
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        # Mostriamo la finestra di dialogo
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Otteniamo il pilota selezionato
            selected_rows = pilots_table.selectedItems()
            if not selected_rows:
                QMessageBox.warning(self, "Attenzione", "Nessun pilota selezionato!")
                return
            
            # Otteniamo le informazioni del pilota selezionato
            row = selected_rows[0].row()
            iscrizione_id = int(pilots_table.item(row, 0).text())
            numero = pilots_table.item(row, 1).text()
            pilota = pilots_table.item(row, 2).text()
            categoria = pilots_table.item(row, 3).text()
            
            try:
                # Aggiungiamo il pilota alla tabella Supercampione
                row = self.pilots_table.rowCount()
                self.pilots_table.insertRow(row)
                
                self.pilots_table.setItem(row, 0, QTableWidgetItem(str(row+1)))
                self.pilots_table.setItem(row, 1, QTableWidgetItem(numero))
                self.pilots_table.setItem(row, 2, QTableWidgetItem(pilota))
                self.pilots_table.setItem(row, 3, QTableWidgetItem(categoria))
                self.pilots_table.setItem(row, 4, QTableWidgetItem("Aggiunto manualmente"))
                
                # Salviamo l'ID dell'iscrizione
                self.pilots_table.item(row, 0).setData(
                    Qt.ItemDataRole.UserRole, iscrizione_id
                )
                
                # Ridimensioniamo le colonne
                self.pilots_table.resizeColumnsToContents()
                
            except Exception as e:
                QMessageBox.critical(self, "Errore", 
                                   f"Errore durante l'aggiunta del pilota: {str(e)}")
            finally:
                db.close()
    
    def remove_pilot(self):
        """Rimuove un pilota dalla tabella Supercampione"""
        # Controlliamo se un pilota è selezionato
        selected_rows = self.pilots_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Attenzione", "Seleziona un pilota da rimuovere!")
            return
        
        # Otteniamo la riga del pilota selezionato
        row = selected_rows[0].row()
        
        # Chiediamo conferma
        pilota = self.pilots_table.item(row, 2).text()
        reply = QMessageBox.question(
            self, "Conferma rimozione", 
            f"Sei sicuro di voler rimuovere {pilota} dal Supercampione?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Rimuoviamo la riga dalla tabella
            self.pilots_table.removeRow(row)
            
            # Aggiorniamo le posizioni
            for i in range(self.pilots_table.rowCount()):
                self.pilots_table.setItem(i, 0, QTableWidgetItem(str(i+1)))
    
    def move_pilot_up(self):
        """Sposta un pilota verso l'alto nella lista"""
        # Controlliamo se un pilota è selezionato
        selected_rows = self.pilots_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Attenzione", "Seleziona un pilota da spostare!")
            return
        
        # Otteniamo la riga del pilota selezionato
        row = selected_rows[0].row()
        
        # Se è già in cima, non può salire di più
        if row == 0:
            QMessageBox.information(self, "Informazione", "Il pilota è già in prima posizione!")
            return
        
        # Salviamo i dati della riga corrente
        current_data = []
        for col in range(self.pilots_table.columnCount()):
            item = self.pilots_table.item(row, col)
            current_data.append(item.text())
        
        # Salviamo anche l'ID dell'iscrizione
        iscrizione_id = self.pilots_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        # Salviamo i dati della riga sopra
        above_data = []
        for col in range(self.pilots_table.columnCount()):
            item = self.pilots_table.item(row-1, col)
            above_data.append(item.text())
        
        iscrizione_id_above = self.pilots_table.item(row-1, 0).data(Qt.ItemDataRole.UserRole)
        
        # Scambiamo i dati (tranne la posizione che rimane invariata)
        for col in range(1, self.pilots_table.columnCount()):
            self.pilots_table.setItem(row-1, col, QTableWidgetItem(current_data[col]))
            self.pilots_table.setItem(row, col, QTableWidgetItem(above_data[col]))
        
        # Aggiorniamo anche gli ID delle iscrizioni
        self.pilots_table.item(row-1, 0).setData(Qt.ItemDataRole.UserRole, iscrizione_id)
        self.pilots_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, iscrizione_id_above)
        
        # Selezioniamo la nuova riga
        self.pilots_table.selectRow(row-1)
    
    def move_pilot_down(self):
        """Sposta un pilota verso il basso nella lista"""
        # Controlliamo se un pilota è selezionato
        selected_rows = self.pilots_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Attenzione", "Seleziona un pilota da spostare!")
            return
        
        # Otteniamo la riga del pilota selezionato
        row = selected_rows[0].row()
        
        # Se è già in fondo, non può scendere di più
        if row == self.pilots_table.rowCount() - 1:
            QMessageBox.information(self, "Informazione", "Il pilota è già in ultima posizione!")
            return
        
        # Salviamo i dati della riga corrente
        current_data = []
        for col in range(self.pilots_table.columnCount()):
            item = self.pilots_table.item(row, col)
            current_data.append(item.text())
        
        # Salviamo anche l'ID dell'iscrizione
        iscrizione_id = self.pilots_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        # Salviamo i dati della riga sotto
        below_data = []
        for col in range(self.pilots_table.columnCount()):
            item = self.pilots_table.item(row+1, col)
            below_data.append(item.text())
        
        iscrizione_id_below = self.pilots_table.item(row+1, 0).data(Qt.ItemDataRole.UserRole)
        
        # Scambiamo i dati (tranne la posizione che rimane invariata)
        for col in range(1, self.pilots_table.columnCount()):
            self.pilots_table.setItem(row+1, col, QTableWidgetItem(current_data[col]))
            self.pilots_table.setItem(row, col, QTableWidgetItem(below_data[col]))
        
        # Aggiorniamo anche gli ID delle iscrizioni
        self.pilots_table.item(row+1, 0).setData(Qt.ItemDataRole.UserRole, iscrizione_id)
        self.pilots_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, iscrizione_id_below)
        
        # Selezioniamo la nuova riga
        self.pilots_table.selectRow(row+1)
    
    def save_supercampione(self):
        """Salva il gruppo Supercampione nel database"""
        evento_id = self.event_combo.currentData()
        
        if not evento_id:
            QMessageBox.warning(self, "Attenzione", "Seleziona un evento!")
            return
        
        if self.pilots_table.rowCount() == 0:
            QMessageBox.warning(self, "Attenzione", "Nessun pilota da salvare!")
            return
        
        # Chiediamo conferma
        reply = QMessageBox.question(
            self, "Conferma salvataggio", 
            "Vuoi salvare questo gruppo Supercampione? Se esiste già un gruppo Supercampione per questo evento, verrà sovrascritto.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        try:
            db = SessionLocal()
            
            # Controlliamo se esiste già un gruppo Supercampione per questo evento
            existing_group = db.query(Gruppo).filter(
                Gruppo.evento_id == evento_id,
                Gruppo.tipo_sessione == "Supercampione"
            ).first()
            
            if existing_group:
                # Eliminiamo le partecipazioni esistenti
                db.query(PartecipazioneGruppo).filter(
                    PartecipazioneGruppo.gruppo_id == existing_group.id
                ).delete()
                
                # Usiamo il gruppo esistente
                gruppo = existing_group
            else:
                # Creiamo un nuovo gruppo
                gruppo = Gruppo(
                    evento_id=evento_id,
                    nome="Supercampione",
                    tipo_sessione="Supercampione",
                    limite_piloti=self.pilots_table.rowCount()
                )
                db.add(gruppo)
                db.flush()  # Per ottenere l'ID
            
            # Aggiungiamo i piloti al gruppo
            for row in range(self.pilots_table.rowCount()):
                iscrizione_id = self.pilots_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
                
                # Creiamo la partecipazione
                partecipazione = PartecipazioneGruppo(
                    gruppo_id=gruppo.id,
                    iscrizione_id=iscrizione_id,
                    posizione_griglia=row+1  # La posizione corrisponde all'ordine in tabella
                )
                
                db.add(partecipazione)
            
            db.commit()
            
            QMessageBox.information(self, "Operazione completata", 
                                   "Gruppo Supercampione salvato con successo!")
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", 
                               f"Errore durante il salvataggio: {str(e)}")
        finally:
            db.close()

    class RaceGroupsManager(QWidget):
        """Gestione completa dei gruppi di gara"""
        
        def __init__(self):
            super().__init__()
            
            # Layout principale
            layout = QVBoxLayout(self)
            
            # Titolo
            title_label = QLabel("Gestione Gruppi di Gara")
            title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
            layout.addWidget(title_label)
            
            # Schede per le diverse funzionalità
            self.tabs = QTabWidget()
            
            # Tab per creare i gruppi da qualifiche
            self.qualification_groups_tab = QualificationGroupsTab()
            self.tabs.addTab(self.qualification_groups_tab, "Gruppi da Qualifiche")
            
            # Tab per gestire manualmente i gruppi
            self.manual_groups_tab = ManualGroupsTab()
            self.tabs.addTab(self.manual_groups_tab, "Gestione Manuale Gruppi")
            
            # Tab per la gestione risultati gara
            self.race_results_tab = RaceResultsTab()
            self.tabs.addTab(self.race_results_tab, "Risultati Gare")
            
            # Tab per la gestione del Supercampione
            self.supercampione_tab = SupercampioneTab()
            self.tabs.addTab(self.supercampione_tab, "Gara Supercampione")
            
            layout.addWidget(self.tabs)
        
class RaceTimingTab(QWidget):
    """Tab per il cronometraggio delle gare ufficiali"""
    
    def __init__(self):
        super().__init__()
        
        # Layout principale
        layout = QVBoxLayout(self)
        
        # Titolo
        title_label = QLabel("Cronometraggio Manche Ufficiali")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Selettori per evento e gruppo
        selectors_layout = QFormLayout()
        
        self.event_combo = QComboBox()
        selectors_layout.addRow("Evento:", self.event_combo)
        
        self.session_combo = QComboBox()
        self.session_combo.addItems(["Gara 1", "Gara 2", "Supercampione"])
        selectors_layout.addRow("Manche:", self.session_combo)
        
        self.group_combo = QComboBox()
        selectors_layout.addRow("Gruppo:", self.group_combo)
        
        layout.addLayout(selectors_layout)
        
        # Bottone per caricare i piloti del gruppo
        self.load_button = QPushButton("Carica Piloti del Gruppo")
        self.load_button.clicked.connect(self.load_group_pilots)
        layout.addWidget(self.load_button)
        
        # Pannello di controllo sessione
        self.session_control = QGroupBox("Controllo Sessione")
        control_layout = QHBoxLayout()
        
        # Timer display
        self.timer_display = QLabel("00:00.000")
        self.timer_display.setStyleSheet("font-size: 24px; font-weight: bold;")
        control_layout.addWidget(self.timer_display)
        
        # Bottoni per il timer
        self.start_button = QPushButton("Avvia Gara")
        self.start_button.clicked.connect(self.start_race)
        control_layout.addWidget(self.start_button)
        
        self.pause_button = QPushButton("Pausa")
        self.pause_button.clicked.connect(self.pause_race)
        self.pause_button.setEnabled(False)
        control_layout.addWidget(self.pause_button)
        
        self.stop_button = QPushButton("Termina Gara")
        self.stop_button.clicked.connect(self.stop_race)
        self.stop_button.setEnabled(False)
        control_layout.addWidget(self.stop_button)
        
        # Display dello stato
        self.status_label = QLabel("Gara non avviata")
        control_layout.addWidget(self.status_label)
        
        self.session_control.setLayout(control_layout)
        layout.addWidget(self.session_control)
        
        # Splitter per dividere la finestra
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Pannello per registrare i tempi
        input_panel = QGroupBox("Registrazione Passaggi")
        input_layout = QVBoxLayout()
        
        input_form = QFormLayout()
        self.rider_number_input = QLineEdit()
        self.rider_number_input.setPlaceholderText("Numero pilota")
        input_form.addRow("Numero:", self.rider_number_input)
        
        self.record_button = QPushButton("Registra Passaggio")
        self.record_button.clicked.connect(self.record_lap)
        
        input_layout.addLayout(input_form)
        input_layout.addWidget(self.record_button)
        
        # Tabella ultimi passaggi
        self.last_laps_table = QTableWidget(0, 4)
        self.last_laps_table.setHorizontalHeaderLabels([
            "Ora", "Numero", "Pilota", "Tempo sul Giro"
        ])
        self.last_laps_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        input_layout.addWidget(self.last_laps_table)
        
        input_panel.setLayout(input_layout)
        splitter.addWidget(input_panel)
        
        # Pannello classifica live
        standings_panel = QGroupBox("Classifica Live")
        standings_layout = QVBoxLayout()
        
        self.standings_table = QTableWidget(0, 5)
        self.standings_table.setHorizontalHeaderLabels([
            "Pos", "Num", "Pilota", "Giri", "Miglior Tempo"
        ])
        self.standings_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        standings_layout.addWidget(self.standings_table)
        
        standings_panel.setLayout(standings_layout)
        splitter.addWidget(standings_panel)
        
        layout.addWidget(splitter)
        
        # Bottoni per le azioni finali
        buttons_layout = QHBoxLayout()
        
        self.calculate_button = QPushButton("Calcola Classifica Finale")
        self.calculate_button.clicked.connect(self.calculate_final_standings)
        self.calculate_button.setEnabled(False)
        buttons_layout.addWidget(self.calculate_button)
        
        self.save_button = QPushButton("Salva Risultati")
        self.save_button.clicked.connect(self.save_results)
        self.save_button.setEnabled(False)
        buttons_layout.addWidget(self.save_button)
        
        layout.addLayout(buttons_layout)
        
        # Timer per aggiornare l'orologio
        self.race_timer = QTimer()
        self.race_timer.timeout.connect(self.update_timer)
        self.race_running = False
        self.race_start_time = None
        self.elapsed_time = 0
        
        # Carichiamo gli eventi
        self.load_events()
        
        # Colleghiamo gli eventi dei combobox
        self.event_combo.currentIndexChanged.connect(self.load_groups_combo)
    
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
    
    def load_groups_combo(self):
        """Carica i gruppi disponibili per l'evento e la sessione selezionati"""
        evento_id = self.event_combo.currentData()
        session_type = self.session_combo.currentText()
        
        if not evento_id:
            return
        
        try:
            db = SessionLocal()
            
            gruppi = db.query(Gruppo).filter(
                Gruppo.evento_id == evento_id,
                Gruppo.tipo_sessione == session_type
            ).all()
            
            self.group_combo.clear()
            for gruppo in gruppi:
                self.group_combo.addItem(gruppo.nome, gruppo.id)
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante il caricamento gruppi: {str(e)}")
        finally:
            db.close()
    
    def load_group_pilots(self):
        """Carica i piloti del gruppo selezionato"""
        gruppo_id = self.group_combo.currentData()
        
        if not gruppo_id:
            QMessageBox.warning(self, "Attenzione", "Seleziona prima un gruppo!")
            return
        
        try:
            db = SessionLocal()
            
            # Otteniamo le partecipazioni
            partecipazioni = db.query(PartecipazioneGruppo).filter(
                PartecipazioneGruppo.gruppo_id == gruppo_id
            ).all()
            
            # Puliamo le tabelle
            self.standings_table.setRowCount(0)
            self.last_laps_table.setRowCount(0)
            
            # Popoliamo la classifica iniziale (ordine di partenza)
            for partecipazione in partecipazioni:
                iscrizione = partecipazione.iscrizione
                pilota = iscrizione.pilota
                
                row = self.standings_table.rowCount()
                self.standings_table.insertRow(row)
                
                self.standings_table.setItem(row, 0, QTableWidgetItem(str(partecipazione.posizione_griglia)))
                self.standings_table.setItem(row, 1, QTableWidgetItem(str(iscrizione.numero_gara)))
                self.standings_table.setItem(row, 2, QTableWidgetItem(f"{pilota.nome} {pilota.cognome}"))
                self.standings_table.setItem(row, 3, QTableWidgetItem("0"))  # Giri completati
                self.standings_table.setItem(row, 4, QTableWidgetItem("-"))  # Miglior tempo
                
                # Salviamo l'ID dell'iscrizione
                self.standings_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, iscrizione.id)
            
            QMessageBox.information(self, "Piloti Caricati", f"Caricati {len(partecipazioni)} piloti per il gruppo")
            
            # Ora i bottoni sono utilizzabili
            self.start_button.setEnabled(True)
            self.rider_number_input.setEnabled(False)  # Disabilitato finché non inizia la gara
            self.record_button.setEnabled(False)
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante il caricamento piloti: {str(e)}")
        finally:
            db.close()
    
    def start_race(self):
        """Avvia la sessione di gara"""
        if not self.race_running:
            self.race_start_time = QDateTime.currentDateTime()
            self.race_timer.start(100)  # Aggiorna ogni 100ms
            self.race_running = True
            
            self.start_button.setEnabled(False)
            self.pause_button.setEnabled(True)
            self.stop_button.setEnabled(True)
            
            self.rider_number_input.setEnabled(True)
            self.record_button.setEnabled(True)
            
            self.status_label.setText("Gara in corso")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
    
    def pause_race(self):
        """Mette in pausa la sessione di gara"""
        if self.race_running:
            self.race_timer.stop()
            self.elapsed_time = self.get_elapsed_time()
            self.race_running = False
            
            self.start_button.setEnabled(True)
            self.start_button.setText("Riprendi")
            self.pause_button.setEnabled(False)
            
            self.rider_number_input.setEnabled(False)
            self.record_button.setEnabled(False)
            
            self.status_label.setText("Gara in pausa")
            self.status_label.setStyleSheet("color: orange; font-weight: bold;")
        else:
            self.race_start_time = QDateTime.currentDateTime().addMSecs(-self.elapsed_time)
            self.race_timer.start(100)
            self.race_running = True
            
            self.start_button.setEnabled(False)
            self.start_button.setText("Avvia Gara")
            self.pause_button.setEnabled(True)
            
            self.rider_number_input.setEnabled(True)
            self.record_button.setEnabled(True)
            
            self.status_label.setText("Gara in corso")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
    
    def stop_race(self):
        """Termina la sessione di gara"""
        if not self.race_running and self.elapsed_time == 0:
            return
        
        reply = QMessageBox.question(
            self, "Conferma", 
            "Sei sicuro di voler terminare la gara? Questa azione non può essere annullata.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        self.race_timer.stop()
        self.race_running = False
        
        self.start_button.setEnabled(False)
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        
        self.rider_number_input.setEnabled(False)
        self.record_button.setEnabled(False)
        
        self.status_label.setText("Gara terminata")
        self.status_label.setStyleSheet("color: blue; font-weight: bold;")
        
        # Ora possiamo calcolare la classifica finale
        self.calculate_button.setEnabled(True)
        self.save_button.setEnabled(True)
    
    def update_timer(self):
        """Aggiorna il display del timer"""
        if self.race_running:
            elapsed = self.get_elapsed_time()
            self.timer_display.setText(self.format_time(elapsed))
    
    def get_elapsed_time(self):
        """Calcola il tempo trascorso in millisecondi"""
        if self.race_running and self.race_start_time:
            return self.race_start_time.msecsTo(QDateTime.currentDateTime())
        return self.elapsed_time
    
    def format_time(self, msecs):
        """Formatta il tempo in millisecondi come MM:SS.mmm"""
        secs = msecs // 1000
        mins = secs // 60
        secs %= 60
        msecs %= 1000
        return f"{mins:02d}:{secs:02d}.{msecs:03d}"
    
    def record_lap(self):
        """Registra un passaggio di un pilota"""
        if not self.race_running:
            QMessageBox.warning(self, "Attenzione", "La gara non è in corso!")
            return
        
        numero_pilota = self.rider_number_input.text().strip()
        
        if not numero_pilota:
            QMessageBox.warning(self, "Attenzione", "Inserisci un numero di pilota!")
            return
        
        current_time = QDateTime.currentDateTime()
        elapsed_time = self.get_elapsed_time()
        
        # Cerchiamo il pilota nella classifica
        found = False
        for row in range(self.standings_table.rowCount()):
            num = self.standings_table.item(row, 1).text()
            if num == numero_pilota:
                found = True
                
                # Aggiorniamo il conteggio dei giri
                giri = int(self.standings_table.item(row, 3).text())
                giri += 1
                self.standings_table.setItem(row, 3, QTableWidgetItem(str(giri)))
                
                # Otteniamo informazioni sul pilota
                iscrizione_id = self.standings_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
                pilota_nome = self.standings_table.item(row, 2).text()
                
                # Aggiungiamo il passaggio alla tabella
                row_laps = self.last_laps_table.rowCount()
                self.last_laps_table.insertRow(row_laps)
                
                self.last_laps_table.setItem(row_laps, 0, QTableWidgetItem(current_time.toString("HH:mm:ss.zzz")))
                self.last_laps_table.setItem(row_laps, 1, QTableWidgetItem(numero_pilota))
                self.last_laps_table.setItem(row_laps, 2, QTableWidgetItem(pilota_nome))
                self.last_laps_table.setItem(row_laps, 3, QTableWidgetItem(self.format_time(elapsed_time)))
                
                # Salviamo l'ID dell'iscrizione e il tempo
                self.last_laps_table.item(row_laps, 0).setData(Qt.ItemDataRole.UserRole, iscrizione_id)
                self.last_laps_table.item(row_laps, 3).setData(Qt.ItemDataRole.UserRole, elapsed_time)
                
                # Scorriamo la tabella per vedere l'ultima riga
                self.last_laps_table.scrollToItem(self.last_laps_table.item(row_laps, 0))
                
                # Aggiorniamo anche il miglior tempo nel caso sia il primo giro
                if giri == 1 or self.standings_table.item(row, 4).text() == "-":
                    self.standings_table.setItem(row, 4, QTableWidgetItem(self.format_time(elapsed_time)))
                    self.standings_table.item(row, 4).setData(Qt.ItemDataRole.UserRole, elapsed_time)
                
                break
        
        if not found:
            QMessageBox.warning(self, "Attenzione", f"Nessun pilota trovato con il numero {numero_pilota}!")
        
        # Puliamo il campo per il prossimo inserimento
        self.rider_number_input.clear()
        self.rider_number_input.setFocus()
    
    def calculate_final_standings(self):
        """Calcola la classifica finale in base ai giri completati e ai tempi"""
        if self.standings_table.rowCount() == 0:
            QMessageBox.warning(self, "Attenzione", "Nessun pilota nella classifica!")
            return
        
        # Raccogliamo i dati dalla tabella
        standings_data = []
        for row in range(self.standings_table.rowCount()):
            iscrizione_id = self.standings_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            pos = int(self.standings_table.item(row, 0).text())
            numero = self.standings_table.item(row, 1).text()
            pilota = self.standings_table.item(row, 2).text()
            giri = int(self.standings_table.item(row, 3).text())
            
            # Il miglior tempo potrebbe non esserci
            best_time_text = self.standings_table.item(row, 4).text()
            best_time = self.standings_table.item(row, 4).data(Qt.ItemDataRole.UserRole)
            if best_time is None:
                best_time = float('inf')
            
            standings_data.append({
                "iscrizione_id": iscrizione_id,
                "pos": pos,
                "numero": numero,
                "pilota": pilota,
                "giri": giri,
                "best_time": best_time,
                "best_time_text": best_time_text
            })
        
        # Ordiniamo prima per giri (decrescente), poi per tempo migliore (crescente)
        standings_data.sort(key=lambda x: (-x["giri"], x["best_time"]))
        
        # Aggiorniamo la tabella con la nuova classifica
        for i, data in enumerate(standings_data):
            row = self.standings_table.item(i, 0).row()
            
            # Aggiorniamo la posizione
            self.standings_table.setItem(row, 0, QTableWidgetItem(str(i+1)))
            self.standings_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, data["iscrizione_id"])
        
        # Ordiniamo la tabella per posizione
        self.standings_table.sortItems(0, Qt.SortOrder.AscendingOrder)
        
        QMessageBox.information(self, "Operazione completata", "Classifica finale calcolata!")
    
    def save_results(self):
        """Salva i risultati della gara nel database"""
        if self.standings_table.rowCount() == 0:
            QMessageBox.warning(self, "Attenzione", "Nessun risultato da salvare!")
            return
        
        gruppo_id = self.group_combo.currentData()
        session_type = self.session_combo.currentText()
        
        if not gruppo_id:
            QMessageBox.warning(self, "Attenzione", "Nessun gruppo selezionato!")
            return
        
        try:
            db = SessionLocal()
            
            # Controlliamo se esistono già risultati per questo gruppo/sessione
            existing = db.query(Risultato).filter(
                Risultato.gruppo_id == gruppo_id,
                Risultato.sessione_tipo == session_type
            ).all()
            
            if existing:
                reply = QMessageBox.question(
                    self, "Risultati esistenti", 
                    "Esistono già risultati per questa gara. Vuoi sovrascriverli?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply != QMessageBox.StandardButton.Yes:
                    return
                
                # Eliminiamo i risultati esistenti
                for result in existing:
                    db.delete(result)
            
            # Salviamo i risultati
            for row in range(self.standings_table.rowCount()):
                iscrizione_id = self.standings_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
                posizione = int(self.standings_table.item(row, 0).text())
                giri = int(self.standings_table.item(row, 3).text())
                
                # Calcoliamo i punti secondo il regolamento
                punti = self.calculate_points(posizione)
                
                # Otteniamo il miglior tempo
                best_time = self.standings_table.item(row, 4).data(Qt.ItemDataRole.UserRole)
                
                # Creiamo il risultato
                risultato = Risultato(
                    iscrizione_id=iscrizione_id,
                    gruppo_id=gruppo_id,
                    sessione_tipo=session_type,
                    posizione=posizione,
                    punti=punti,
                    best_lap_time=best_time
                )
                
                db.add(risultato)
            
            db.commit()
            
            QMessageBox.information(self, "Operazione completata", "Risultati salvati con successo!")
            
            # Disabilitiamo i bottoni per evitare duplicati
            self.calculate_button.setEnabled(False)
            self.save_button.setEnabled(False)
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante il salvataggio: {str(e)}")
        finally:
            db.close()
    
    def calculate_points(self, position):
        """Calcola i punti in base alla posizione secondo il regolamento FMI"""
        # Tabella punti per le categorie principali
        points_table = {
            1: 250, 2: 210, 3: 170, 4: 140, 5: 120, 6: 110, 7: 100, 8: 90, 9: 85, 10: 80,
            11: 77, 12: 74, 13: 72, 14: 70, 15: 68, 16: 66, 17: 64, 18: 63, 19: 62, 20: 61,
            21: 60, 22: 59, 23: 58, 24: 57, 25: 56, 26: 55, 27: 54, 28: 53, 29: 52, 30: 51,
            31: 50, 32: 49, 33: 48, 34: 47, 35: 46, 36: 45, 37: 44, 38: 43, 39: 42, 40: 41
        }
        
        return points_table.get(position, 0)  # 0 punti se la posizione è oltre la 40ª

    


