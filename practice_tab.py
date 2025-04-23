# ui/practice_tab.py
# Aggiungi queste importazioni all'inizio del file
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLabel, QComboBox, QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QMessageBox, QSpinBox,
    QDialog, QListWidget, QListWidgetItem, QSplitter
)
from PyQt6.QtCore import Qt

from database.connection import SessionLocal
from database.models import Evento, Iscrizione, Pilota, Categoria, Gruppo, PartecipazioneGruppo

class PracticeTab(QWidget):
    """Scheda per organizzare i gruppi delle prove libere"""
    
    def __init__(self):
        super().__init__()
        
        # Creiamo il layout principale - pensa a questo come a una scatola in cui metteremo tutto
        layout = QVBoxLayout(self)
        
        # Aggiungiamo un titolo in cima
        title_label = QLabel("Organizzazione Prove Libere")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Selettori per evento
        selectors_layout = QFormLayout()
        
        # Dropdown per scegliere l'evento
        self.event_combo = QComboBox()
        selectors_layout.addRow("Evento:", self.event_combo)
        
        layout.addLayout(selectors_layout)
        
        # Bottoni per le azioni
        buttons_layout = QHBoxLayout()
        
        # Bottone per caricare gli iscritti
        self.load_button = QPushButton("Carica Iscritti")
        self.load_button.clicked.connect(self.load_entries)
        buttons_layout.addWidget(self.load_button)
        
        # Bottone per creare i gruppi automaticamente
        self.create_groups_button = QPushButton("Crea Gruppi Automaticamente")
        self.create_groups_button.clicked.connect(self.create_groups)
        buttons_layout.addWidget(self.create_groups_button)
        self.edit_groups_button = QPushButton("Modifica Gruppi Manualmente")
        self.edit_groups_button.clicked.connect(self.edit_groups_manually)
        buttons_layout.addWidget(self.edit_groups_button)
        
        layout.addLayout(buttons_layout)
        
        # Tabella che mostra gli iscritti
        self.entries_table = QTableWidget(0, 5)  # 0 righe, 5 colonne
        self.entries_table.setHorizontalHeaderLabels([
            "ID", "Pilota", "Categoria", "Licenza", "Gruppo"
        ])
        self.entries_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.entries_table)
        
        # Tabella che mostrerà i gruppi creati
        self.groups_table = QTableWidget(0, 3)  # 0 righe, 3 colonne
        self.groups_table.setHorizontalHeaderLabels([
            "Gruppo", "Numero Piloti", "Durata"
        ])
        self.groups_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.groups_table)
        
        # Carichiamo gli eventi nel dropdown
        self.load_events()
        
    def load_events(self):
        """Carica gli eventi nel dropdown"""
        try:
            db = SessionLocal()
            
            # Prendiamo tutti gli eventi dal database
            eventi = db.query(Evento).all()
            
            self.event_combo.clear()
            for evento in eventi:
                # Formattiamo il nome dell'evento con la data
                self.event_combo.addItem(f"{evento.nome} ({evento.data})", evento.id)
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante il caricamento eventi: {str(e)}")
        finally:
            db.close()
    
    def load_entries(self):
        """Carica gli iscritti all'evento selezionato"""
        evento_id = self.event_combo.currentData()
        
        if not evento_id:
            QMessageBox.warning(self, "Attenzione", "Seleziona un evento!")
            return
        
        try:
            db = SessionLocal()
            
            # Prendiamo tutti gli iscritti per questo evento
            iscrizioni = db.query(Iscrizione).filter(Iscrizione.evento_id == evento_id).all()
            
            self.entries_table.setRowCount(len(iscrizioni))
            
            for i, iscrizione in enumerate(iscrizioni):
                self.entries_table.setItem(i, 0, QTableWidgetItem(str(iscrizione.id)))
                self.entries_table.setItem(i, 1, QTableWidgetItem(f"{iscrizione.pilota.cognome} {iscrizione.pilota.nome}"))
                self.entries_table.setItem(i, 2, QTableWidgetItem(f"{iscrizione.categoria.classe} {iscrizione.categoria.categoria}"))
                self.entries_table.setItem(i, 3, QTableWidgetItem(iscrizione.pilota.licenza_tipo))
                
                # Verifichiamo se il pilota è già in un gruppo per le prove libere
                partecipazione = db.query(PartecipazioneGruppo).join(Gruppo).filter(
                    PartecipazioneGruppo.iscrizione_id == iscrizione.id,
                    Gruppo.tipo_sessione == "Prove Libere"
                ).first()
                
                if partecipazione:
                    self.entries_table.setItem(i, 4, QTableWidgetItem(partecipazione.gruppo.nome))
                else:
                    self.entries_table.setItem(i, 4, QTableWidgetItem("-"))
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante il caricamento iscritti: {str(e)}")
        finally:
            db.close()

    def create_groups(self):
        """Crea i gruppi per le prove libere secondo il regolamento FMI"""
        evento_id = self.event_combo.currentData()
        
        if not evento_id:
            QMessageBox.warning(self, "Attenzione", "Seleziona un evento!")
            return
        
        try:
            db = SessionLocal()
            
            # Prendiamo tutte le iscrizioni per questo evento
            iscrizioni = db.query(Iscrizione).filter(Iscrizione.evento_id == evento_id).all()
            
            if not iscrizioni:
                QMessageBox.warning(self, "Attenzione", "Non ci sono iscritti per questo evento!")
                return
            
            # Organizziamo gli iscritti per categoria
            iscrizioni_per_categoria = {}
            for iscrizione in iscrizioni:
                categoria_nome = f"{iscrizione.categoria.classe} {iscrizione.categoria.categoria}"
                if categoria_nome not in iscrizioni_per_categoria:
                    iscrizioni_per_categoria[categoria_nome] = []
                iscrizioni_per_categoria[categoria_nome].append(iscrizione)
            
            # Creiamo le liste dei gruppi secondo le regole del regolamento
            gruppi = []
            
            # Gruppo MX1/MX2 Elite/Fast/Expert
            gruppo_mx_top = []
            for nome_cat, iscritti in iscrizioni_per_categoria.items():
                if ("MX1" in nome_cat or "MX2" in nome_cat) and ("Elite" in nome_cat or "Fast" in nome_cat or "Expert" in nome_cat):
                    gruppo_mx_top.extend(iscritti)
            
            if gruppo_mx_top:
                gruppi.append({
                    "nome": "Gruppo A - Elite/Fast/Expert",
                    "iscritti": gruppo_mx_top,
                    "durata": "5 min + 15 min qualifiche",
                    "tipo_sessione": "Prove Libere"
                })
            
            # Gruppo MX1/MX2 Rider
            gruppo_mx_rider = []
            for nome_cat, iscritti in iscrizioni_per_categoria.items():
                if ("MX1" in nome_cat or "MX2" in nome_cat) and "Rider" in nome_cat:
                    gruppo_mx_rider.extend(iscritti)
            
            if gruppo_mx_rider:
                gruppi.append({
                    "nome": "Gruppo A - Rider",
                    "iscritti": gruppo_mx_rider,
                    "durata": "5 min + 15 min qualifiche",
                    "tipo_sessione": "Prove Libere"
                })
            
            # Gruppo Challenge/Veteran/Superveteran/Master
            gruppo_challenge_veteran = []
            for nome_cat, iscritti in iscrizioni_per_categoria.items():
                if "Challenge" in nome_cat or "Veteran" in nome_cat or "Master" in nome_cat:
                    gruppo_challenge_veteran.extend(iscritti)
            
            if gruppo_challenge_veteran:
                gruppi.append({
                    "nome": "Gruppo B - Challenge/Veteran",
                    "iscritti": gruppo_challenge_veteran,
                    "durata": "5 min + 15 min qualifiche",
                    "tipo_sessione": "Prove Libere"
                })
            
            # Gruppo 125
            gruppo_125 = []
            for nome_cat, iscritti in iscrizioni_per_categoria.items():
                if "125" in nome_cat and "Senior" in nome_cat:
                    gruppo_125.extend(iscritti)
            
            if gruppo_125:
                gruppi.append({
                    "nome": "Gruppo A - 125 Senior",
                    "iscritti": gruppo_125,
                    "durata": "5 min + 15 min qualifiche",
                    "tipo_sessione": "Prove Libere"
                })
            
            # Gruppo 125 Junior
            gruppo_125_junior = []
            for nome_cat, iscritti in iscrizioni_per_categoria.items():
                if "125" in nome_cat and "Junior" in nome_cat:
                    gruppo_125_junior.extend(iscritti)
            
            if gruppo_125_junior:
                gruppi.append({
                    "nome": "Gruppo A - 125 Junior",
                    "iscritti": gruppo_125_junior,
                    "durata": "5 min + 15 min qualifiche",
                    "tipo_sessione": "Prove Libere"
                })
            
            # Gruppo Minicross
            gruppo_minicross = []
            for nome_cat, iscritti in iscrizioni_per_categoria.items():
                if any(x in nome_cat for x in ["Debuttanti", "Cadetti", "Junior", "Senior"]) and not "125" in nome_cat:
                    gruppo_minicross.extend(iscritti)
            
            if gruppo_minicross:
                gruppi.append({
                    "nome": "Gruppo Minicross",
                    "iscritti": gruppo_minicross,
                    "durata": "5 min + 15 min qualifiche",
                    "tipo_sessione": "Prove Libere"
                })
            
            # Gruppo Femminile
            gruppo_femminile = []
            for nome_cat, iscritti in iscrizioni_per_categoria.items():
                if "Femminile" in nome_cat:
                    gruppo_femminile.extend(iscritti)
            
            if gruppo_femminile:
                gruppi.append({
                    "nome": "Gruppo Femminile",
                    "iscritti": gruppo_femminile,
                    "durata": "5 min + 15 min qualifiche",
                    "tipo_sessione": "Prove Libere"
                })
            
            # Salviamo i gruppi nel database
            for gruppo in gruppi:
                # Creiamo o aggiorniamo il gruppo nel database
                gruppo_db = db.query(Gruppo).filter(
                    Gruppo.evento_id == evento_id,
                    Gruppo.nome == gruppo["nome"],
                    Gruppo.tipo_sessione == gruppo["tipo_sessione"]
                ).first()
                
                if not gruppo_db:
                    gruppo_db = Gruppo(
                        evento_id=evento_id,
                        nome=gruppo["nome"],
                        tipo_sessione=gruppo["tipo_sessione"]
                    )
                    db.add(gruppo_db)
                    db.flush()  # Per ottenere l'ID
                else:
                    # Se il gruppo esiste già, rimuoviamo le vecchie partecipazioni
                    db.query(PartecipazioneGruppo).filter(
                        PartecipazioneGruppo.gruppo_id == gruppo_db.id
                    ).delete()
                
                # Aggiungiamo i piloti al gruppo
                for posizione, iscrizione in enumerate(gruppo["iscritti"], 1):
                    partecipazione = PartecipazioneGruppo(
                        gruppo_id=gruppo_db.id,
                        iscrizione_id=iscrizione.id,
                        posizione_griglia=posizione  # Usiamo un numero progressivo
                    )
                    db.add(partecipazione)
            
            db.commit()
            
            # Aggiorniamo le tabelle
            self.update_groups_table(gruppi)
            self.load_entries()  # Ricarica gli iscritti per mostrare a quale gruppo appartengono
            
            QMessageBox.information(self, "Gruppi Creati", f"Creati {len(gruppi)} gruppi per le prove libere!")
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante la creazione dei gruppi: {str(e)}")
        finally:
            db.close()

    def update_groups_table(self, gruppi):
        """Aggiorna la tabella dei gruppi"""
        self.groups_table.setRowCount(len(gruppi))
        
        for i, gruppo in enumerate(gruppi):
            self.groups_table.setItem(i, 0, QTableWidgetItem(gruppo["nome"]))
            self.groups_table.setItem(i, 1, QTableWidgetItem(str(len(gruppo["iscritti"]))))
            self.groups_table.setItem(i, 2, QTableWidgetItem(gruppo["durata"]))
    
    def edit_groups_manually(self):
        """Apre una finestra per modificare manualmente i gruppi"""
        evento_id = self.event_combo.currentData()
        
        if not evento_id:
            QMessageBox.warning(self, "Attenzione", "Seleziona un evento!")
            return
        
        try:
            db = SessionLocal()
            
            # Otteniamo tutti i gruppi per questo evento
            gruppi = db.query(Gruppo).filter(
                Gruppo.evento_id == evento_id,
                Gruppo.tipo_sessione == "Prove Libere"
            ).all()
            
            if not gruppi:
                QMessageBox.warning(self, "Attenzione", "Non ci sono ancora gruppi creati per questo evento. Crea prima i gruppi automaticamente.")
                return
            
            # Creiamo una finestra di dialogo
            dialog = QDialog(self)
            dialog.setWindowTitle("Modifica Gruppi Manualmente")
            dialog.resize(800, 600)  # Facciamo una finestra grande
            
            # Layout principale
            layout = QVBoxLayout(dialog)
            
            # Aggiungiamo un'etichetta di istruzioni
            instructions = QLabel("Seleziona un pilota dalla lista di sinistra e scegli a quale gruppo assegnarlo usando il menu a tendina. Clicca 'Sposta' per confermare.")
            layout.addWidget(instructions)
            
            # Creiamo uno splitter (divider) per avere due sezioni affiancate
            splitter = QSplitter()
            layout.addWidget(splitter)
            
            # Pannello di sinistra: lista piloti
            left_panel = QWidget()
            left_layout = QVBoxLayout(left_panel)
            
            # Lista piloti
            pilot_label = QLabel("Piloti Iscritti:")
            left_layout.addWidget(pilot_label)
            
            self.pilots_list = QListWidget()
            left_layout.addWidget(self.pilots_list)
            
            # Otteniamo tutti i piloti iscritti
            iscrizioni = db.query(Iscrizione).filter(Iscrizione.evento_id == evento_id).all()
            
            # Riempiamo la lista dei piloti
            for iscrizione in iscrizioni:
                pilota = iscrizione.pilota
                categoria = iscrizione.categoria
                
                # Troviamo a quale gruppo appartiene questo pilota
                partecipazione = db.query(PartecipazioneGruppo).join(Gruppo).filter(
                    PartecipazioneGruppo.iscrizione_id == iscrizione.id,
                    Gruppo.tipo_sessione == "Prove Libere"
                ).first()
                
                gruppo_nome = partecipazione.gruppo.nome if partecipazione else "Nessun gruppo"
                
                # Creiamo un elemento nella lista
                item_text = f"{pilota.cognome} {pilota.nome} - {categoria.classe} {categoria.categoria} - {gruppo_nome}"
                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, iscrizione.id)  # Salviamo l'ID dell'iscrizione
                self.pilots_list.addItem(item)
            
            splitter.addWidget(left_panel)
            
            # Pannello di destra: selettore gruppo e bottone
            right_panel = QWidget()
            right_layout = QVBoxLayout(right_panel)
            
            # Informazioni sul pilota selezionato
            self.selected_pilot_info = QLabel("Seleziona un pilota")
            right_layout.addWidget(self.selected_pilot_info)
            
            # Selettore gruppo
            group_label = QLabel("Sposta nel gruppo:")
            right_layout.addWidget(group_label)
            
            self.group_combo = QComboBox()
            for gruppo in gruppi:
                self.group_combo.addItem(gruppo.nome, gruppo.id)
            right_layout.addWidget(self.group_combo)
            
            # Bottone per spostare
            self.move_button = QPushButton("Sposta nel Gruppo")
            self.move_button.clicked.connect(self.move_pilot_to_group)
            right_layout.addWidget(self.move_button)
            
            # Lista dei piloti nel gruppo selezionato
            group_pilots_label = QLabel("Piloti nel gruppo selezionato:")
            right_layout.addWidget(group_pilots_label)
            
            self.group_pilots_list = QListWidget()
            right_layout.addWidget(self.group_pilots_list)
            
            # Aggiorniamo la lista quando cambia il gruppo selezionato
            self.group_combo.currentIndexChanged.connect(self.update_group_pilots)
            
            # Aggiorniamo le info quando cambia il pilota selezionato
            self.pilots_list.currentItemChanged.connect(self.update_pilot_info)
            
            splitter.addWidget(right_panel)
            
            # Bottone per salvare le modifiche
            save_button = QPushButton("Salva Modifiche")
            save_button.clicked.connect(dialog.accept)
            layout.addWidget(save_button)
            
            # Salviamo gli oggetti utili per dopo
            dialog.db = db
            dialog.iscrizioni = iscrizioni
            dialog.gruppi = gruppi
            
            # Mostriamo la finestra di dialogo
            if dialog.exec() == QDialog.DialogCode.Accepted:
                # Ricarica la tabella degli iscritti
                self.load_entries()
                QMessageBox.information(self, "Modifiche Salvate", "I gruppi sono stati aggiornati con successo!")
            else:
                # Chiudiamo la connessione al database
                db.close()
        
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Si è verificato un errore: {str(e)}")
            db.close()

    def update_pilot_info(self, current, previous):
        """Aggiorna le informazioni sul pilota selezionato"""
        if current:
            iscrizione_id = current.data(Qt.ItemDataRole.UserRole)
            for iscrizione in self.sender().parent().parent().parent().db.iscrizioni:
                if iscrizione.id == iscrizione_id:
                    pilota = iscrizione.pilota
                    categoria = iscrizione.categoria
                    
                    info_text = f"Pilota: {pilota.cognome} {pilota.nome}\nCategoria: {categoria.classe} {categoria.categoria}\nLicenza: {pilota.licenza_tipo}"
                    self.selected_pilot_info.setText(info_text)
                    break

    def update_group_pilots(self):
        """Aggiorna la lista dei piloti nel gruppo selezionato"""
        gruppo_id = self.group_combo.currentData()
        
        if not gruppo_id:
            return
        
        # Otteniamo tutti i piloti in questo gruppo
        partecipazioni = self.sender().parent().parent().parent().db.query(PartecipazioneGruppo).filter(
            PartecipazioneGruppo.gruppo_id == gruppo_id
        ).all()
        
        # Puliamo la lista
        self.group_pilots_list.clear()
        
        # Riempiamo la lista con i piloti di questo gruppo
        for partecipazione in partecipazioni:
            iscrizione = partecipazione.iscrizione
            pilota = iscrizione.pilota
            categoria = iscrizione.categoria
            
            item_text = f"{pilota.cognome} {pilota.nome} - {categoria.classe} {categoria.categoria}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, iscrizione.id)
            self.group_pilots_list.addItem(item)

    def move_pilot_to_group(self):
        """Sposta il pilota selezionato nel gruppo selezionato"""
        # Otteniamo il pilota selezionato
        pilot_item = self.pilots_list.currentItem()
        if not pilot_item:
            QMessageBox.warning(self, "Attenzione", "Seleziona un pilota da spostare!")
            return
        
        iscrizione_id = pilot_item.data(Qt.ItemDataRole.UserRole)
        
        # Otteniamo il gruppo selezionato
        gruppo_id = self.group_combo.currentData()
        if not gruppo_id:
            QMessageBox.warning(self, "Attenzione", "Seleziona un gruppo dove spostare il pilota!")
            return
        
        try:
            db = self.sender().parent().parent().parent().db
            
            # Verifichiamo se il pilota è già in un gruppo
            partecipazione = db.query(PartecipazioneGruppo).join(Gruppo).filter(
                PartecipazioneGruppo.iscrizione_id == iscrizione_id,
                Gruppo.tipo_sessione == "Prove Libere"
            ).first()
            
            if partecipazione:
                # Se è già assegnato, aggiorniamo il gruppo
                partecipazione.gruppo_id = gruppo_id
            else:
                # Altrimenti creiamo una nuova partecipazione
                partecipazione = PartecipazioneGruppo(
                    gruppo_id=gruppo_id,
                    iscrizione_id=iscrizione_id,
                    posizione_griglia=0  # Posizione temporanea
                )
                db.add(partecipazione)
            
            # Salviamo le modifiche
            db.commit()
            
            # Aggiorniamo la lista dei piloti e l'interfaccia
            pilot_name = pilot_item.text().split(" - ")[0]
            gruppo_nome = self.group_combo.currentText()
            
            pilot_item.setText(f"{pilot_name} - {gruppo_nome}")
            
            # Aggiorniamo la lista dei piloti nel gruppo
            self.update_group_pilots()
            
            QMessageBox.information(self, "Pilota Spostato", f"Il pilota è stato spostato nel gruppo {gruppo_nome}")
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Si è verificato un errore: {str(e)}")