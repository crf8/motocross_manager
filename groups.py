# ui/groups.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLabel, QComboBox, QPushButton, QTableWidget, 
    QTableWidgetItem, QGroupBox, QTabWidget,
    QMessageBox, QSpinBox, QDialog, QLineEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from sqlalchemy.orm import Session
from database.connection import SessionLocal
from database.models import Evento, Categoria, Iscrizione, LapTime, Pilota, Gruppo, PartecipazioneGruppo

class GroupsModule(QWidget):
    def __init__(self):
        super().__init__()
        
        # Layout principale
        self.layout = QVBoxLayout(self)
        
        # Titolo
        self.title_label = QLabel("Gestione Gruppi")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.layout.addWidget(self.title_label)
        
        # Tab widget per diverse operazioni sui gruppi
        self.tabs = QTabWidget()
        
        # Tab per la creazione automatica dei gruppi
        self.auto_groups_tab = AutoGroupsTab()
        self.tabs.addTab(self.auto_groups_tab, "Creazione Automatica Gruppi")
        
        # Tab per la gestione manuale dei gruppi
        self.manual_groups_tab = ManualGroupsTab()
        self.tabs.addTab(self.manual_groups_tab, "Gestione Manuale Gruppi")
        
        # Tab per la visualizzazione griglie di partenza
        self.grid_view_tab = GridViewTab()
        self.tabs.addTab(self.grid_view_tab, "Griglie di Partenza")
        
        self.layout.addWidget(self.tabs)

class AutoGroupsTab(QWidget):
    def __init__(self):
        super().__init__()
        
        # Layout principale
        self.layout = QVBoxLayout(self)
        
        # Selettori
        self.selectors_layout = QFormLayout()
        
        self.event_combo = QComboBox()
        self.selectors_layout.addRow("Evento:", self.event_combo)
        
        self.category_combo = QComboBox()
        self.selectors_layout.addRow("Categoria:", self.category_combo)
        
        self.session_type_combo = QComboBox()
        self.session_type_combo.addItems([
            "Qualifiche", "Gara 1", "Gara 2", "Supercampione"
        ])
        self.selectors_layout.addRow("Tipo Sessione:", self.session_type_combo)
        
        self.layout.addLayout(self.selectors_layout)
        
        # Impostazioni gruppi
        self.settings_group = QGroupBox("Impostazioni Gruppi")
        self.settings_layout = QFormLayout()
        
        self.group_method_combo = QComboBox()
        self.group_method_combo.addItems([
            "Basato sui tempi delle qualifiche", 
            "Basato sui risultati della gara precedente",
            "Random/Sorteggio",
            "Basato sul numero di gara"
        ])
        self.settings_layout.addRow("Metodo di Raggruppamento:", self.group_method_combo)
        
        self.groups_count_spin = QSpinBox()
        self.groups_count_spin.setMinimum(1)
        self.groups_count_spin.setMaximum(10)
        self.groups_count_spin.setValue(2)
        self.settings_layout.addRow("Numero di Gruppi:", self.groups_count_spin)
        
        self.max_riders_spin = QSpinBox()
        self.max_riders_spin.setMinimum(10)
        self.max_riders_spin.setMaximum(100)
        self.max_riders_spin.setValue(40)
        self.settings_layout.addRow("Max Piloti per Gruppo:", self.max_riders_spin)
        
        self.settings_group.setLayout(self.settings_layout)
        self.layout.addWidget(self.settings_group)
        
        # Bottone genera gruppi
        self.generate_button = QPushButton("Genera Gruppi")
        self.generate_button.clicked.connect(self.generate_groups)
        self.layout.addWidget(self.generate_button)
        
        # Tabella anteprima gruppi
        self.preview_table = QTableWidget(0, 3)
        self.preview_table.setHorizontalHeaderLabels(
            ["Gruppo", "Numero Piloti", "Piloti"]
        )
        self.layout.addWidget(self.preview_table)
        
        # Bottone conferma gruppi
        self.confirm_button = QPushButton("Conferma e Salva Gruppi")
        self.confirm_button.clicked.connect(self.confirm_groups)
        self.layout.addWidget(self.confirm_button)
        
        # Inizializza dati
        self.load_events_combo()
        self.groups_data = []  # Per memorizzare temporaneamente i gruppi generati
        
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
            iscrizioni = db.query(Iscrizione).filter(Iscrizione.evento_id == evento_id).all()
            categorie_ids = set()
            
            self.category_combo.clear()
            self.category_combo.addItem("Tutte le categorie", 0)
            
            for iscrizione in iscrizioni:
                if iscrizione.categoria_id not in categorie_ids:
                    categorie_ids.add(iscrizione.categoria_id)
                    categoria = iscrizione.categoria
                    self.category_combo.addItem(f"{categoria.classe} {categoria.categoria}", categoria.id)
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante il caricamento categorie: {str(e)}")
        finally:
            db.close()
    
    def generate_groups(self):
        """Genera gruppi in base ai parametri selezionati"""
        if self.event_combo.count() == 0:
            QMessageBox.warning(self, "Avviso", "Nessun evento disponibile!")
            return
        
        evento_id = self.event_combo.currentData()
        categoria_id = self.category_combo.currentData()
        session_type = self.session_type_combo.currentText()
        group_method = self.group_method_combo.currentText()
        groups_count = self.groups_count_spin.value()
        max_riders = self.max_riders_spin.value()
        
        if not evento_id:
            QMessageBox.warning(self, "Avviso", "Selezionare un evento!")
            return
        
        try:
            db = SessionLocal()
            
            # Ottieni piloti iscritti
            query = db.query(Iscrizione).filter(Iscrizione.evento_id == evento_id)
            
            # Filtra per categoria se specificata
            if categoria_id and categoria_id > 0:
                query = query.filter(Iscrizione.categoria_id == categoria_id)
            
            iscrizioni = query.all()
            
            if not iscrizioni:
                QMessageBox.warning(self, "Avviso", "Nessun pilota iscritto trovato!")
                return
            
            # Dividi i piloti in gruppi in base al metodo selezionato
            iscrizioni_ordinate = []
            
            if group_method == "Basato sui tempi delle qualifiche" and session_type != "Qualifiche":
                # Ordinamento basato sui tempi delle qualifiche
                query = """
                SELECT i.id, i.numero_gara, p.nome, p.cognome, c.classe, c.categoria, MIN(lt.tempo_ms) as best_time
                FROM iscrizioni i
                JOIN piloti p ON i.pilota_id = p.id
                JOIN categorie c ON i.categoria_id = c.id
                LEFT JOIN lap_times lt ON lt.iscrizione_id = i.id AND lt.sessione_tipo = 'Qualifiche'
                WHERE i.evento_id = :evento_id
                """
                
                if categoria_id and categoria_id > 0:
                    query += " AND i.categoria_id = :categoria_id"
                
                query += " GROUP BY i.id ORDER BY best_time"
                
                result = db.execute(query, {"evento_id": evento_id, "categoria_id": categoria_id if categoria_id and categoria_id > 0 else None})
                
                for row in result:
                    iscrizione_id = row[0]
                    iscrizione = db.query(Iscrizione).get(iscrizione_id)
                    if iscrizione:
                        iscrizioni_ordinate.append(iscrizione)
                
                # Aggiungi piloti senza tempi alla fine
                for iscrizione in iscrizioni:
                    if iscrizione not in iscrizioni_ordinate:
                        iscrizioni_ordinate.append(iscrizione)
                        
            elif group_method == "Basato sui risultati della gara precedente" and session_type in ["Gara 2", "Supercampione"]:
                # Implementazione per ordinamento basato su gara precedente
                previous_session = "Gara 1" if session_type == "Gara 2" else "Gara 1"
                
                # Trova gruppi della gara precedente
                gruppi_precedenti = db.query(Gruppo).filter(
                    Gruppo.evento_id == evento_id,
                    Gruppo.tipo_sessione == previous_session
                ).all()
                
                # Ottieni risultati della gara precedente
                for gruppo in gruppi_precedenti:
                    # Implementazione per ottenere i risultati della gara precedente
                    pass
                
                # Per ora usa l'ordine originale
                iscrizioni_ordinate = iscrizioni
            
            elif group_method == "Random/Sorteggio":
                # Ordinamento casuale
                import random
                iscrizioni_ordinate = list(iscrizioni)
                random.shuffle(iscrizioni_ordinate)
            
            else:  # "Basato sul numero di gara" o default
                # Ordinamento per numero di gara
                iscrizioni_ordinate = sorted(iscrizioni, key=lambda x: x.numero_gara)
            
            # Crea i gruppi
            self.groups_data = []
            
            if session_type == "Supercampione":
                # Logica speciale per Supercampione: prendi i migliori X piloti da ogni gruppo di Gara 1 o Gara 2
                pass
            else:
                # Logica standard di divisione in gruppi
                
                # Calcola quanti piloti per gruppo
                piloti_per_gruppo = len(iscrizioni_ordinate) // groups_count
                piloti_extra = len(iscrizioni_ordinate) % groups_count
                
                # Assicurati che non superi il massimo per gruppo
                if piloti_per_gruppo > max_riders:
                    piloti_per_gruppo = max_riders
                    groups_count = (len(iscrizioni_ordinate) + max_riders - 1) // max_riders  # Arrotonda per eccesso
                    piloti_extra = len(iscrizioni_ordinate) % groups_count
                
                # Distribuisci i piloti nei gruppi
                for i in range(groups_count):
                    gruppo_nome = f"Gruppo {chr(65 + i)}"  # A, B, C, ...
                    piloti_in_gruppo = piloti_per_gruppo + (1 if i < piloti_extra else 0)
                    
                    inizio_indice = i * piloti_per_gruppo + min(i, piloti_extra)
                    fine_indice = inizio_indice + piloti_in_gruppo
                    
                    # Se il metodo è bizzarro (zigzag)
                    if group_method == "Basato sui tempi delle qualifiche" and session_type in ["Gara 1", "Gara 2"]:
                        piloti_gruppo = []
                        for j in range(piloti_in_gruppo):
                            if j % groups_count == i:
                                indice = j // groups_count
                                if indice < len(iscrizioni_ordinate):
                                    piloti_gruppo.append(iscrizioni_ordinate[indice])
                    else:
                        # Metodo sequenziale
                        piloti_gruppo = iscrizioni_ordinate[inizio_indice:fine_indice]
                    
                    self.groups_data.append({
                        "nome": gruppo_nome,
                        "tipo_sessione": session_type,
                        "categoria_id": categoria_id if categoria_id and categoria_id > 0 else None,
                        "piloti": piloti_gruppo,
                        "limite_piloti": max_riders
                    })
            
            # Aggiorna la tabella di anteprima
            self.update_preview_table()
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante la generazione dei gruppi: {str(e)}")
        finally:
            db.close()
    
    def update_preview_table(self):
        """Aggiorna la tabella di anteprima con i gruppi generati"""
        self.preview_table.setRowCount(0)
        
        for gruppo_data in self.groups_data:
            row = self.preview_table.rowCount()
            self.preview_table.insertRow(row)
            
            # Colonna Gruppo
            self.preview_table.setItem(row, 0, QTableWidgetItem(gruppo_data["nome"]))
            
            # Colonna Numero Piloti
            num_piloti = len(gruppo_data["piloti"])
            self.preview_table.setItem(row, 1, QTableWidgetItem(str(num_piloti)))
            
            # Colonna Piloti (primi 5 piloti)
            piloti_text = ", ".join([f"{p.pilota.nome} {p.pilota.cognome} ({p.numero_gara})" 
                                  for p in gruppo_data["piloti"][:5]])
            if num_piloti > 5:
                piloti_text += f", ... e altri {num_piloti - 5}"
            self.preview_table.setItem(row, 2, QTableWidgetItem(piloti_text))
        
        # Ridimensiona colonne
        self.preview_table.resizeColumnsToContents()
    
    def confirm_groups(self):
        """Salva i gruppi generati nel database"""
        if not self.groups_data:
            QMessageBox.warning(self, "Avviso", "Nessun gruppo generato da salvare!")
            return
        
        evento_id = self.event_combo.currentData()
        
        try:
            db = SessionLocal()
            
            # Controlla se esistono già gruppi per questo evento e sessione
            session_type = self.groups_data[0]["tipo_sessione"]
            existing_groups = db.query(Gruppo).filter(
                Gruppo.evento_id == evento_id,
                Gruppo.tipo_sessione == session_type
            ).all()
            
            if existing_groups:
                # Chiedi conferma prima di sovrascrivere
                confirm = QMessageBox.question(
                    self, "Conferma", 
                    f"Esistono già gruppi per {session_type} in questo evento. Sovrascrivere?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if confirm == QMessageBox.StandardButton.Yes:
                    # Elimina i gruppi esistenti
                    for gruppo in existing_groups:
                        # Elimina le partecipazioni
                        db.query(PartecipazioneGruppo).filter(
                            PartecipazioneGruppo.gruppo_id == gruppo.id
                        ).delete()
                    
                    # Elimina i gruppi
                    db.query(Gruppo).filter(
                        Gruppo.evento_id == evento_id,
                        Gruppo.tipo_sessione == session_type
                    ).delete()
                else:
                    db.close()
                    return
            
            # Crea i nuovi gruppi
            for gruppo_data in self.groups_data:
                nuovo_gruppo = Gruppo(
                    evento_id=evento_id,
                    nome=gruppo_data["nome"],
                    categoria_id=gruppo_data["categoria_id"],
                    tipo_sessione=gruppo_data["tipo_sessione"],
                    limite_piloti=gruppo_data["limite_piloti"]
                )
                
                db.add(nuovo_gruppo)
                db.flush()  # Per ottenere l'ID del gruppo
                
                # Aggiungi i piloti al gruppo
                for pos, iscrizione in enumerate(gruppo_data["piloti"], 1):
                    partecipazione = PartecipazioneGruppo(
                        gruppo_id=nuovo_gruppo.id,
                        iscrizione_id=iscrizione.id,
                        posizione_griglia=pos
                    )
                    
                    db.add(partecipazione)
            
            db.commit()
            QMessageBox.information(self, "Successo", "Gruppi salvati con successo!")
            
        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "Errore", f"Errore durante il salvataggio dei gruppi: {str(e)}")
        finally:
            db.close()

class ManualGroupsTab(QWidget):
    def __init__(self):
        super().__init__()
        
        # Layout principale
        self.layout = QVBoxLayout(self)
        
        # Selettori
        self.selectors_layout = QFormLayout()
        
        self.event_combo = QComboBox()
        self.selectors_layout.addRow("Evento:", self.event_combo)
        
        self.session_type_combo = QComboBox()
        self.session_type_combo.addItems([
            "Qualifiche", "Gara 1", "Gara 2", "Supercampione"
        ])
        self.selectors_layout.addRow("Tipo Sessione:", self.session_type_combo)
        
        self.group_combo = QComboBox()
        self.selectors_layout.addRow("Gruppo:", self.group_combo)
        
        self.layout.addLayout(self.selectors_layout)
        
        # Bottoni per la gestione dei gruppi
        self.buttons_layout = QHBoxLayout()
        
        self.load_button = QPushButton("Carica Gruppo")
        self.load_button.clicked.connect(self.load_group)
        self.buttons_layout.addWidget(self.load_button)
        
        self.new_group_button = QPushButton("Nuovo Gruppo")
        self.new_group_button.clicked.connect(self.create_new_group)
        self.buttons_layout.addWidget(self.new_group_button)
        
        self.layout.addLayout(self.buttons_layout)
        
        # Tabella piloti nel gruppo
        self.group_table = QTableWidget(0, 4)
        self.group_table.setHorizontalHeaderLabels(
            ["Pos", "Numero", "Pilota", "Categoria"]
        )
        self.layout.addWidget(self.group_table)
        
        # Bottoni per la modifica dei piloti
        self.edit_buttons_layout = QHBoxLayout()
        
        self.add_rider_button = QPushButton("Aggiungi Pilota")
        self.add_rider_button.clicked.connect(self.add_rider)
        self.edit_buttons_layout.addWidget(self.add_rider_button)
        
        self.remove_rider_button = QPushButton("Rimuovi Pilota")
        self.remove_rider_button.clicked.connect(self.remove_rider)
        self.edit_buttons_layout.addWidget(self.remove_rider_button)
        
        self.move_up_button = QPushButton("Sposta Su")
        self.move_up_button.clicked.connect(self.move_rider_up)
        self.edit_buttons_layout.addWidget(self.move_up_button)
        
        self.move_down_button = QPushButton("Sposta Giù")
        self.move_down_button.clicked.connect(self.move_rider_down)
        self.edit_buttons_layout.addWidget(self.move_down_button)
        
        self.layout.addLayout(self.edit_buttons_layout)
        
        # Bottone salva modifiche
        self.save_button = QPushButton("Salva Modifiche")
        self.save_button.clicked.connect(self.save_changes)
        self.layout.addWidget(self.save_button)
        
        # Inizializza dati
        self.load_events_combo()
        self.current_group_id = None
        
        # Collega eventi combo
        self.event_combo.currentIndexChanged.connect(self.load_session_groups)
        self.session_type_combo.currentIndexChanged.connect(self.load_session_groups)
    
    def load_events_combo(self):
        """Carica gli eventi nel combobox"""
        try:
            db = SessionLocal()
            eventi = db.query(Evento).all()
            
            self.event_combo.clear()
            for evento in eventi:
                self.event_combo.addItem(f"{evento.nome} ({evento.data})", evento.id)
            
            if eventi:
                self.load_session_groups()
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante il caricamento eventi: {str(e)}")
        finally:
            db.close()
    
    def load_session_groups(self):
        """Carica i gruppi per la sessione selezionata"""
        if self.event_combo.count() == 0:
            return
        
        evento_id = self.event_combo.currentData()
        session_type = self.session_type_combo.currentText()
        
        if not evento_id:
            return
        
        try:
            db = SessionLocal()
            
            # Ottieni gruppi per l'evento e la sessione
            gruppi = db.query(Gruppo).filter(
                Gruppo.evento_id == evento_id,
                Gruppo.tipo_sessione == session_type
            ).all()
            
            self.group_combo.clear()
            
            for gruppo in gruppi:
                self.group_combo.addItem(gruppo.nome, gruppo.id)
            
            # Pulisci la tabella se non ci sono gruppi
            if not gruppi:
                self.group_table.setRowCount(0)
                self.current_group_id = None
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante il caricamento gruppi: {str(e)}")
        finally:
            db.close()
    
    def load_group(self):
        """Carica i piloti del gruppo selezionato"""
        if self.group_combo.count() == 0:
            QMessageBox.warning(self, "Avviso", "Nessun gruppo disponibile!")
            return
        
        gruppo_id = self.group_combo.currentData()
        
        if not gruppo_id:
            return
        
        self.current_group_id = gruppo_id
        
        try:
            db = SessionLocal()
            
            # Ottieni partecipazioni al gruppo
            partecipazioni = db.query(PartecipazioneGruppo).filter(
                PartecipazioneGruppo.gruppo_id == gruppo_id
            ).order_by(PartecipazioneGruppo.posizione_griglia).all()
            
            # Pulisci tabella
            self.group_table.setRowCount(0)
            
            # Popola tabella
            for partecipazione in partecipazioni:
                iscrizione = partecipazione.iscrizione
                pilota = iscrizione.pilota
                categoria = iscrizione.categoria
                
                row = self.group_table.rowCount()
                self.group_table.insertRow(row)
                
                self.group_table.setItem(row, 0, QTableWidgetItem(str(partecipazione.posizione_griglia)))
                self.group_table.setItem(row, 1, QTableWidgetItem(str(iscrizione.numero_gara)))
                self.group_table.setItem(row, 2, QTableWidgetItem(f"{pilota.nome} {pilota.cognome}"))
                self.group_table.setItem(row, 3, QTableWidgetItem(f"{categoria.classe} {categoria.categoria}"))
                
                # Memorizza l'ID dell'iscrizione nella riga per riferimenti futuri
                self.group_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, iscrizione.id)
            
            # Ridimensiona colonne
            self.group_table.resizeColumnsToContents()
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante il caricamento piloti del gruppo: {str(e)}")
        finally:
            db.close()
    
    def create_new_group(self):
        """Crea un nuovo gruppo"""
        if self.event_combo.count() == 0:
            QMessageBox.warning(self, "Avviso", "Nessun evento disponibile!")
            return
        
        evento_id = self.event_combo.currentData()
        session_type = self.session_type_combo.currentText()
        
        if not evento_id:
            return
        
        # Dialog per il nuovo gruppo
        dialog = QDialog(self)
        dialog.setWindowTitle("Nuovo Gruppo")
        dialog.setMinimumWidth(300)
        
        dialog_layout = QVBoxLayout(dialog)
        
        form_layout = QFormLayout()
        
        name_input = QLineEdit()
        name_input.setPlaceholderText("Es. Gruppo A")
        form_layout.addRow("Nome Gruppo:", name_input)
        
        category_combo = QComboBox()
        category_combo.addItem("Nessuna categoria", 0)
        
        # Carica categorie
        try:
            db = SessionLocal()
            categorie = db.query(Categoria).all()
            
            for categoria in categorie:
                category_combo.addItem(f"{categoria.classe} {categoria.categoria}", categoria.id)
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante il caricamento categorie: {str(e)}")
        finally:
            db.close()
        
        form_layout.addRow("Categoria:", category_combo)
        
        limit_spin = QSpinBox()
        limit_spin.setMinimum(1)
        limit_spin.setMaximum(100)
        limit_spin.setValue(40)
        form_layout.addRow("Limite Piloti:", limit_spin)
        
        dialog_layout.addLayout(form_layout)
        
        buttons_layout = QHBoxLayout()
        
        cancel_button = QPushButton("Annulla")
        cancel_button.clicked.connect(dialog.reject)
        buttons_layout.addWidget(cancel_button)
        
        create_button = QPushButton("Crea")
        create_button.clicked.connect(dialog.accept)
        buttons_layout.addWidget(create_button)
        
        dialog_layout.addLayout(buttons_layout)
        
        if dialog.exec() == QDialog.Dialog