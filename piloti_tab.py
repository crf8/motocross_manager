# ui/piloti_tab.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QTableWidget, QTableWidgetItem, QHeaderView,
                            QDialog, QFormLayout, QLineEdit, QDateEdit,
                            QComboBox, QMessageBox, QLabel, QSpinBox, 
                            QTextEdit, QScrollArea)
from PyQt6.QtCore import Qt, QDate
from database.connection import SessionLocal
from database.models import Pilota


class PilotaDialog(QDialog):
    def __init__(self, parent=None, pilota_id=None):
        super().__init__(parent)
        
        self.pilota_id = pilota_id
        self.setWindowTitle("Aggiungi Pilota" if pilota_id is None else "Modifica Pilota")
        self.resize(500, 600)  # Facciamo la finestra un po' più grande
        
        # Creiamo un layout a scorrimento per contenere tutti i campi
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        container = QWidget()
        layout = QFormLayout(container)
        
        # DATI PERSONALI
        layout.addRow(QLabel("<b>DATI PERSONALI</b>"))
        
        self.nome_edit = QLineEdit()
        self.cognome_edit = QLineEdit()
        self.data_nascita_edit = QDateEdit()
        self.data_nascita_edit.setCalendarPopup(True)
        self.data_nascita_edit.setDate(QDate.currentDate().addYears(-16))  # Età predefinita 16 anni
        self.email_edit = QLineEdit()
        self.telefono_edit = QLineEdit()
        self.regione_edit = QComboBox()
        self.regione_edit.addItems(["Lombardia", "Piemonte", "Veneto", "Emilia Romagna", 
                                  "Toscana", "Lazio", "Altre regioni"])
        
        layout.addRow("Nome *:", self.nome_edit)
        layout.addRow("Cognome *:", self.cognome_edit)
        layout.addRow("Data di nascita *:", self.data_nascita_edit)
        layout.addRow("Email:", self.email_edit)
        layout.addRow("Telefono:", self.telefono_edit)
        layout.addRow("Regione:", self.regione_edit)
        
        # DATI LICENZA
        layout.addRow(QLabel(""))  # Spazio
        layout.addRow(QLabel("<b>DATI LICENZA</b>"))
        
        self.moto_club_edit = QLineEdit()
        self.licenza_tipo_combo = QComboBox()
        self.licenza_tipo_combo.addItems(["Elite", "Fuoristrada", "MiniOffroad", "One Event", "Training"])
        self.numero_licenza_edit = QLineEdit()
        self.anno_prima_licenza_edit = QSpinBox()
        self.anno_prima_licenza_edit.setRange(1950, QDate.currentDate().year())
        self.anno_prima_licenza_edit.setValue(QDate.currentDate().year())
        
        layout.addRow("Moto Club:", self.moto_club_edit)
        layout.addRow("Tipo Licenza *:", self.licenza_tipo_combo)
        layout.addRow("Numero Licenza *:", self.numero_licenza_edit)
        layout.addRow("Anno prima licenza:", self.anno_prima_licenza_edit)
        
        # DATI MOTO E CATEGORIA
        layout.addRow(QLabel(""))  # Spazio
        layout.addRow(QLabel("<b>MOTO E CATEGORIA</b>"))
        
        self.marca_moto_edit = QComboBox()
        self.marca_moto_edit.addItems(["Honda", "Yamaha", "Kawasaki", "Suzuki", "KTM", 
                                      "Husqvarna", "GASGAS", "TM", "Beta", "Altra"])
        self.cilindrata_edit = QSpinBox()
        self.cilindrata_edit.setRange(50, 650)
        self.cilindrata_edit.setValue(250)
        self.tipo_motore_combo = QComboBox()
        self.tipo_motore_combo.addItems(["2T", "4T"])
        self.categoria_ranking_combo = QComboBox()
        self.categoria_ranking_combo.addItems(["Elite", "Fast", "Expert", "Rider", "Challenge", 
                                             "Veteran", "Superveteran", "Master"])
        self.numero_gara_edit = QLineEdit()
        
        layout.addRow("Marca moto:", self.marca_moto_edit)
        layout.addRow("Cilindrata:", self.cilindrata_edit)
        layout.addRow("Tipo motore:", self.tipo_motore_combo)
        layout.addRow("Categoria:", self.categoria_ranking_combo)
        layout.addRow("Numero gara:", self.numero_gara_edit)
        
        # DATI TECNICI
        layout.addRow(QLabel(""))  # Spazio
        layout.addRow(QLabel("<b>DATI TECNICI</b>"))
        
        self.transponder_personale_edit = QLineEdit()
        self.ranking_nazionale_edit = QSpinBox()
        self.ranking_nazionale_edit.setRange(0, 5000)
        self.ranking_nazionale_edit.setValue(0)
        self.anni_esperienza_edit = QSpinBox()
        self.anni_esperienza_edit.setRange(0, 50)
        
        layout.addRow("Transponder ID:", self.transponder_personale_edit)
        layout.addRow("Ranking nazionale:", self.ranking_nazionale_edit)
        layout.addRow("Anni esperienza:", self.anni_esperienza_edit)
        
        # NOTE E CAMPI AGGIUNTIVI
        layout.addRow(QLabel(""))  # Spazio
        layout.addRow(QLabel("<b>NOTE</b>"))
        
        self.note_edit = QTextEdit()
        self.note_edit.setMaximumHeight(100)
        
        layout.addRow("Note:", self.note_edit)
        
        # Imposta l'area di scorrimento
        scroll_area.setWidget(container)
        
        # Layout principale con l'area di scorrimento
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll_area)
        
        # Aggiungi i pulsanti in basso
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Salva")
        self.cancel_button = QPushButton("Annulla")
        
        # Collega i pulsanti alle funzioni
        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(button_layout)
        
        # Se stiamo modificando un pilota esistente, carica i suoi dati
        if pilota_id is not None:
            self.load_pilota_data()

class PilotiTab(QWidget):
    def __init__(self):
        super().__init__()
        
        # Crea il layout principale
        layout = QVBoxLayout(self)
        
        # Crea il layout per i pulsanti
        button_layout = QHBoxLayout()
        
        # Aggiungi i pulsanti
        self.add_button = QPushButton("Aggiungi Pilota")
        self.edit_button = QPushButton("Modifica Pilota")
        self.delete_button = QPushButton("Elimina Pilota")
        
        # Collega i pulsanti alle funzioni
        self.add_button.clicked.connect(self.add_pilota)
        self.edit_button.clicked.connect(self.edit_pilota)
        self.delete_button.clicked.connect(self.delete_pilota)
        
        # Aggiungi i pulsanti al layout
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()
        
        # Crea la tabella
        self.piloti_table = QTableWidget()
        self.piloti_table.setColumnCount(7)  # Aumentiamo il numero di colonne
        self.piloti_table.setHorizontalHeaderLabels(["ID", "Nome", "Cognome", "Data Nascita", 
                                                      "Moto Club", "Licenza", "Numero"])
        
        # Adatta le colonne alla larghezza del contenuto
        self.piloti_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Aggiungi i layout al layout principale
        layout.addLayout(button_layout)
        layout.addWidget(self.piloti_table)
        
        # Carica i dati
        self.load_piloti()
    
    def load_piloti(self):
        """Carica i piloti dal database nella tabella"""
        # Crea una sessione del database
        db = SessionLocal()
        
        try:
            # Ottieni tutti i piloti
            piloti = db.query(Pilota).all()
            
            # Imposta il numero di righe della tabella
            self.piloti_table.setRowCount(len(piloti))
            
            # Riempi la tabella con i dati
            for i, pilota in enumerate(piloti):
                self.piloti_table.setItem(i, 0, QTableWidgetItem(str(pilota.id)))
                self.piloti_table.setItem(i, 1, QTableWidgetItem(pilota.nome))
                self.piloti_table.setItem(i, 2, QTableWidgetItem(pilota.cognome))
                self.piloti_table.setItem(i, 3, QTableWidgetItem(pilota.data_nascita.strftime("%d/%m/%Y")))
                self.piloti_table.setItem(i, 4, QTableWidgetItem(pilota.moto_club))
                self.piloti_table.setItem(i, 5, QTableWidgetItem(pilota.licenza_tipo))
                self.piloti_table.setItem(i, 6, QTableWidgetItem(pilota.numero_gara if hasattr(pilota, 'numero_gara') else ""))
        
        finally:
            # Chiudi la sessione
            db.close()

    def add_pilota(self):
        """Apre un dialogo per aggiungere un nuovo pilota"""
        dialog = PilotaDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Aggiorna la tabella
            self.load_piloti()
    
    def edit_pilota(self):
        """Apre un dialogo per modificare un pilota selezionato"""
        # Ottieni l'indice della riga selezionata
        selected_rows = self.piloti_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Attenzione", "Seleziona un pilota da modificare")
            return
        
        # Ottieni l'ID del pilota dalla prima colonna
        pilota_id = int(self.piloti_table.item(selected_rows[0].row(), 0).text())
        
        # Apri il dialogo di modifica
        dialog = PilotaDialog(self, pilota_id)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Aggiorna la tabella
            self.load_piloti()
    
    def delete_pilota(self):
        """Elimina il pilota selezionato"""
        # Ottieni l'indice della riga selezionata
        selected_rows = self.piloti_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Attenzione", "Seleziona un pilota da eliminare")
            return
        
        # Ottieni l'ID del pilota dalla prima colonna
        pilota_id = int(self.piloti_table.item(selected_rows[0].row(), 0).text())
        
        # Chiedi conferma
        reply = QMessageBox.question(self, "Conferma eliminazione", 
                                     "Sei sicuro di voler eliminare questo pilota?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            # Elimina il pilota
            db = SessionLocal()
            try:
                pilota = db.query(Pilota).get(pilota_id)
                if pilota:
                    db.delete(pilota)
                    db.commit()
                    # Aggiorna la tabella
                    self.load_piloti()
            finally:
                db.close()

    
    
    def load_pilota_data(self):
        """Carica i dati del pilota esistente nei campi del form"""
        db = SessionLocal()
        try:
            pilota = db.query(Pilota).get(self.pilota_id)
            if pilota:
                # Dati personali
                self.nome_edit.setText(pilota.nome)
                self.cognome_edit.setText(pilota.cognome)
                self.data_nascita_edit.setDate(QDate.fromString(pilota.data_nascita.strftime("%Y-%m-%d"), "yyyy-MM-dd"))
                self.email_edit.setText(pilota.email or "")
                self.telefono_edit.setText(pilota.telefono or "")
                
                # Trova l'indice della regione nel combo box
                regione_index = self.regione_edit.findText(pilota.regione)
                if regione_index >= 0:
                    self.regione_edit.setCurrentIndex(regione_index)
                
                # Dati licenza
                self.moto_club_edit.setText(pilota.moto_club or "")
                
                # Trova l'indice del tipo di licenza nel combo box
                licenza_index = self.licenza_tipo_combo.findText(pilota.licenza_tipo)
                if licenza_index >= 0:
                    self.licenza_tipo_combo.setCurrentIndex(licenza_index)
                
                self.numero_licenza_edit.setText(pilota.numero_licenza or "")
                
                # Dati aggiuntivi (se esistono)
                if hasattr(pilota, 'anno_prima_licenza') and pilota.anno_prima_licenza:
                    self.anno_prima_licenza_edit.setValue(pilota.anno_prima_licenza)
                    
                if hasattr(pilota, 'marca_moto') and pilota.marca_moto:
                    marca_index = self.marca_moto_edit.findText(pilota.marca_moto)
                    if marca_index >= 0:
                        self.marca_moto_edit.setCurrentIndex(marca_index)
                        
                if hasattr(pilota, 'cilindrata') and pilota.cilindrata:
                    self.cilindrata_edit.setValue(pilota.cilindrata)
                    
                if hasattr(pilota, 'tipo_motore') and pilota.tipo_motore:
                    motore_index = self.tipo_motore_combo.findText(pilota.tipo_motore)
                    if motore_index >= 0:
                        self.tipo_motore_combo.setCurrentIndex(motore_index)
                        
                if hasattr(pilota, 'categoria_ranking') and pilota.categoria_ranking:
                    categoria_index = self.categoria_ranking_combo.findText(pilota.categoria_ranking)
                    if categoria_index >= 0:
                        self.categoria_ranking_combo.setCurrentIndex(categoria_index)
                        
                if hasattr(pilota, 'numero_gara') and pilota.numero_gara:
                    self.numero_gara_edit.setText(pilota.numero_gara)
                    
                if hasattr(pilota, 'transponder_personale') and pilota.transponder_personale:
                    self.transponder_personale_edit.setText(pilota.transponder_personale)
                    
                if hasattr(pilota, 'ranking_nazionale') and pilota.ranking_nazionale:
                    self.ranking_nazionale_edit.setValue(pilota.ranking_nazionale)
                    
                if hasattr(pilota, 'anni_esperienza') and pilota.anni_esperienza:
                    self.anni_esperienza_edit.setValue(pilota.anni_esperienza)
                    
                if hasattr(pilota, 'note') and pilota.note:
                    self.note_edit.setPlainText(pilota.note)
        finally:
            db.close()
    
    def accept(self):
        """Salva i dati del pilota nel database"""
        # Controlla che i campi obbligatori siano compilati
        if not self.nome_edit.text() or not self.cognome_edit.text() or not self.numero_licenza_edit.text():
            QMessageBox.warning(self, "Campi obbligatori", "I campi Nome, Cognome e Numero Licenza sono obbligatori")
            return
        
        # Crea una sessione del database
        db = SessionLocal()
        
        try:
            # Se stiamo modificando un pilota esistente, caricalo
            if self.pilota_id is not None:
                pilota = db.query(Pilota).get(self.pilota_id)
            else:
                # Altrimenti crea un nuovo pilota
                pilota = Pilota()
            
            # Aggiorna i dati del pilota
            pilota.nome = self.nome_edit.text()
            pilota.cognome = self.cognome_edit.text()
            pilota.data_nascita = self.data_nascita_edit.date().toPython()
            pilota.email = self.email_edit.text()
            pilota.telefono = self.telefono_edit.text()
            pilota.regione = self.regione_edit.currentText()
            
            pilota.moto_club = self.moto_club_edit.text()
            pilota.licenza_tipo = self.licenza_tipo_combo.currentText()
            pilota.numero_licenza = self.numero_licenza_edit.text()
            
            # Salviamo i nuovi campi, verificando prima che esistano nel modello
            # (se non esistono, verranno aggiunti in modo "dinamico" a questo oggetto)
            pilota.anno_prima_licenza = self.anno_prima_licenza_edit.value()
            pilota.marca_moto = self.marca_moto_edit.currentText()
            pilota.cilindrata = self.cilindrata_edit.value()
            pilota.tipo_motore = self.tipo_motore_combo.currentText()
            pilota.categoria_ranking = self.categoria_ranking_combo.currentText()
            pilota.numero_gara = self.numero_gara_edit.text()
            pilota.transponder_personale = self.transponder_personale_edit.text()
            pilota.ranking_nazionale = self.ranking_nazionale_edit.value()
            pilota.anni_esperienza = self.anni_esperienza_edit.value()
            pilota.note = self.note_edit.toPlainText()
            
            # Se è un nuovo pilota, aggiungilo al database
            if self.pilota_id is None:
                db.add(pilota)
            
            # Salva le modifiche
            db.commit()
            
            # Chiudi il dialogo
            super().accept()
            
        except Exception as e:
            # Se c'è un errore, mostra un messaggio
            QMessageBox.critical(self, "Errore", f"Si è verificato un errore: {str(e)}")
            
        finally:
            # Chiudi la sessione
            db.close()