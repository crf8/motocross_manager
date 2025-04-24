from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                            QTableWidgetItem, QPushButton, QLabel, QComboBox,
                            QMessageBox, QDialog, QFormLayout)

# Qui importiamo SessionLocal dal modulo database
from database import SessionLocal  # Questa è la modifica importante!
from database.models import Iscrizione, Pilota, Evento
class IscrizioniTab(QWidget):
    def __init__(self):
        super().__init__()
        
        # Layout principale
        layout = QVBoxLayout(self)
        
        # Layout pulsanti
        button_layout = QHBoxLayout()
        
        # Pulsanti
        self.add_button = QPushButton("Nuova Iscrizione")
        self.edit_button = QPushButton("Modifica Iscrizione")
        self.delete_button = QPushButton("Elimina Iscrizione")
        
        # Colleghiamo i pulsanti alle funzioni
        self.add_button.clicked.connect(self.add_iscrizione)
        self.edit_button.clicked.connect(self.edit_iscrizione)
        self.delete_button.clicked.connect(self.delete_iscrizione)
        
        # Aggiungiamo i pulsanti al layout
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()
        
        # Tabella iscrizioni
        self.iscrizioni_table = QTableWidget()
        self.iscrizioni_table.setColumnCount(6)
        self.iscrizioni_table.setHorizontalHeaderLabels([
            "ID", "Pilota", "Evento", "Categoria", "Numero Gara", "Pagamento"
        ])
        
        # Adattiamo le colonne
        self.iscrizioni_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Aggiungiamo i layout al layout principale
        layout.addLayout(button_layout)
        layout.addWidget(self.iscrizioni_table)
        
        # Carichiamo le iscrizioni
        self.load_iscrizioni()
    
    def load_iscrizioni(self):
        """Carica le iscrizioni dal database nella tabella"""
        db = SessionLocal()
        
        try:
            iscrizioni = db.query(Iscrizione).all()
            
            self.iscrizioni_table.setRowCount(len(iscrizioni))
            
            for i, iscrizione in enumerate(iscrizioni):
                self.iscrizioni_table.setItem(i, 0, QTableWidgetItem(str(iscrizione.id)))
                self.iscrizioni_table.setItem(i, 1, QTableWidgetItem(f"{iscrizione.pilota.cognome} {iscrizione.pilota.nome}"))
                self.iscrizioni_table.setItem(i, 2, QTableWidgetItem(iscrizione.evento.nome))
                self.iscrizioni_table.setItem(i, 3, QTableWidgetItem(f"{iscrizione.categoria.classe} {iscrizione.categoria.categoria}"))
                self.iscrizioni_table.setItem(i, 4, QTableWidgetItem(str(iscrizione.numero_gara)))
                self.iscrizioni_table.setItem(i, 5, QTableWidgetItem("Sì" if iscrizione.pagamento_effettuato else "No"))
        
        finally:
            db.close()
    
    def add_iscrizione(self):
        """Apre un dialogo per aggiungere una nuova iscrizione"""
        dialog = IscrizioneDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_iscrizioni()
    
    def edit_iscrizione(self):
        """Apre un dialogo per modificare un'iscrizione selezionata"""
        selected_rows = self.iscrizioni_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Attenzione", "Seleziona un'iscrizione da modificare")
            return
        
        iscrizione_id = int(self.iscrizioni_table.item(selected_rows[0].row(), 0).text())
        
        dialog = IscrizioneDialog(self, iscrizione_id)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_iscrizioni()
    
    def delete_iscrizione(self):
        """Elimina l'iscrizione selezionata"""
        selected_rows = self.iscrizioni_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Attenzione", "Seleziona un'iscrizione da eliminare")
            return
        
        iscrizione_id = int(self.iscrizioni_table.item(selected_rows[0].row(), 0).text())
        
        reply = QMessageBox.question(self, "Conferma eliminazione", 
                                   "Sei sicuro di voler eliminare questa iscrizione?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            db = SessionLocal()
            try:
                iscrizione = db.query(Iscrizione).get(iscrizione_id)
                if iscrizione:
                    db.delete(iscrizione)
                    db.commit()
                    self.load_iscrizioni()
            finally:
                db.close()

class IscrizioneDialog(QDialog):
    def __init__(self, parent=None, iscrizione_id=None):
        super().__init__(parent)
        
        self.iscrizione_id = iscrizione_id
        self.setWindowTitle("Nuova Iscrizione" if iscrizione_id is None else "Modifica Iscrizione")
        self.resize(600, 500)
        
        # Layout principale
        layout = QVBoxLayout(self)
        
        # Form layout per i dati dell'iscrizione
        form_layout = QFormLayout()
        
        # SELEZIONE PILOTA
        layout.addWidget(QLabel("<b>DATI PILOTA</b>"))
        
        self.pilota_combo = QComboBox()
        self.load_piloti()  # Carichiamo i piloti nel combo box
        
        form_layout.addRow("Pilota *:", self.pilota_combo)
        
        # Mostriamo i dettagli del pilota selezionato
        self.pilota_details_label = QLabel("Seleziona un pilota per vedere i dettagli")
        form_layout.addRow("Dettagli:", self.pilota_details_label)
        
        # Colleghiamo il cambio di pilota all'aggiornamento dei dettagli
        self.pilota_combo.currentIndexChanged.connect(self.update_pilota_details)
        
        # SELEZIONE EVENTO
        layout.addWidget(QLabel("<b>DATI EVENTO</b>"))
        
        self.evento_combo = QComboBox()
        self.load_eventi()  # Carichiamo gli eventi nel combo box
        
        form_layout.addRow("Evento *:", self.evento_combo)
        
        # Mostriamo i dettagli dell'evento selezionato
        self.evento_details_label = QLabel("Seleziona un evento per vedere i dettagli")
        form_layout.addRow("Dettagli:", self.evento_details_label)
        
        # Colleghiamo il cambio di evento all'aggiornamento dei dettagli
        self.evento_combo.currentIndexChanged.connect(self.update_evento_details)
        
        # SELEZIONE CATEGORIA
        layout.addWidget(QLabel("<b>CATEGORIA E DATI GARA</b>"))
        
        self.categoria_combo = QComboBox()
        self.load_categorie()  # Carichiamo le categorie nel combo box
        
        form_layout.addRow("Categoria *:", self.categoria_combo)
        
        # Campi per i dati specifici della gara
        self.numero_gara_edit = QLineEdit()
        self.numero_gara_edit.setPlaceholderText("Inserisci il numero di gara")
        
        self.transponder_edit = QLineEdit()
        self.transponder_edit.setPlaceholderText("Opzionale - ID del transponder")
        
        form_layout.addRow("Numero gara *:", self.numero_gara_edit)
        form_layout.addRow("Transponder ID:", self.transponder_edit)
        
        # PAGAMENTO
        layout.addWidget(QLabel("<b>DATI PAGAMENTO</b>"))
        
        self.pagamento_check = QCheckBox("Pagamento effettuato")
        form_layout.addRow("Stato:", self.pagamento_check)
        
        self.importo_label = QLabel("Importo: 60,00 €")  # Valore predefinito
        form_layout.addRow("", self.importo_label)
        
        # NOTE
        layout.addWidget(QLabel("<b>NOTE</b>"))
        
        self.note_edit = QTextEdit()
        self.note_edit.setMaximumHeight(100)
        self.note_edit.setPlaceholderText("Note opzionali sull'iscrizione...")
        
        form_layout.addRow("Note:", self.note_edit)
        
        # Aggiungiamo il form layout al layout principale
        layout.addLayout(form_layout)
        
        # Pulsanti
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Salva")
        self.cancel_button = QPushButton("Annulla")
        
        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        # Se stiamo modificando un'iscrizione esistente, carichiamo i suoi dati
        if iscrizione_id is not None:
            self.load_iscrizione_data()
    
    def load_piloti(self):
        """Carica la lista dei piloti nel combo box"""
        db = SessionLocal()
        
        try:
            piloti = db.query(Pilota).order_by(Pilota.cognome, Pilota.nome).all()
            
            self.pilota_combo.clear()
            self.pilota_combo.addItem("Seleziona un pilota...", None)
            
            for pilota in piloti:
                display_text = f"{pilota.cognome} {pilota.nome} - {pilota.numero_licenza}"
                self.pilota_combo.addItem(display_text, pilota.id)
        
        finally:
            db.close()
    
    def load_eventi(self):
        """Carica la lista degli eventi nel combo box"""
        db = SessionLocal()
        
        try:
            # Carichiamo solo gli eventi futuri
            today = QDate.currentDate().toPython()
            eventi = db.query(Evento).filter(Evento.data >= today).order_by(Evento.data).all()
            
            self.evento_combo.clear()
            self.evento_combo.addItem("Seleziona un evento...", None)
            
            for evento in eventi:
                data_str = evento.data.strftime("%d/%m/%Y")
                display_text = f"{evento.nome} - {data_str}"
                self.evento_combo.addItem(display_text, evento.id)
        
        finally:
            db.close()
    
    def load_categorie(self):
        """Carica la lista delle categorie nel combo box"""
        db = SessionLocal()
        
        try:
            categorie = db.query(Categoria).order_by(Categoria.classe, Categoria.categoria).all()
            
            self.categoria_combo.clear()
            self.categoria_combo.addItem("Seleziona una categoria...", None)
            
            for categoria in categorie:
                display_text = f"{categoria.classe} {categoria.categoria}"
                self.categoria_combo.addItem(display_text, categoria.id)
        
        finally:
            db.close()
    
    def update_pilota_details(self):
        """Aggiorna i dettagli del pilota selezionato"""
        pilota_id = self.pilota_combo.currentData()
        
        if not pilota_id:
            self.pilota_details_label.setText("Seleziona un pilota per vedere i dettagli")
            return
        
        db = SessionLocal()
        
        try:
            pilota = db.query(Pilota).get(pilota_id)
            
            if pilota:
                eta = QDate.currentDate().year() - pilota.data_nascita.year()
                details = f"Età: {eta} anni | Licenza: {pilota.licenza_tipo} ({pilota.numero_licenza}) | Moto Club: {pilota.moto_club}"
                self.pilota_details_label.setText(details)
                
                # Se è possibile, suggeriamo un numero di gara
                if hasattr(pilota, 'numero_gara') and pilota.numero_gara:
                    self.numero_gara_edit.setText(pilota.numero_gara)
        
        finally:
            db.close()
    
    def update_evento_details(self):
        """Aggiorna i dettagli dell'evento selezionato"""
        evento_id = self.evento_combo.currentData()
        
        if not evento_id:
            self.evento_details_label.setText("Seleziona un evento per vedere i dettagli")
            return
        
        db = SessionLocal()
        
        try:
            evento = db.query(Evento).get(evento_id)
            
            if evento:
                data_str = evento.data.strftime("%d/%m/%Y")
                details = f"Data: {data_str} | Circuito: {evento.circuito} | Organizzatore: {evento.moto_club_organizzatore}"
                self.evento_details_label.setText(details)
                
                # Aggiorniamo l'importo in base all'evento
                if hasattr(evento, 'quota_iscrizione') and evento.quota_iscrizione:
                    self.importo_label.setText(f"Importo: {evento.quota_iscrizione:.2f} €")
                else:
                    self.importo_label.setText("Importo: 60,00 €")  # Valore predefinito
        
        finally:
            db.close()
    
    def load_iscrizione_data(self):
        """Carica i dati dell'iscrizione esistente"""
        db = SessionLocal()
        
        try:
            iscrizione = db.query(Iscrizione).get(self.iscrizione_id)
            
            if iscrizione:
                # Impostiamo il pilota
                index = self.pilota_combo.findData(iscrizione.pilota_id)
                if index >= 0:
                    self.pilota_combo.setCurrentIndex(index)
                
                # Impostiamo l'evento
                index = self.evento_combo.findData(iscrizione.evento_id)
                if index >= 0:
                    self.evento_combo.setCurrentIndex(index)
                
                # Impostiamo la categoria
                index = self.categoria_combo.findData(iscrizione.categoria_id)
                if index >= 0:
                    self.categoria_combo.setCurrentIndex(index)
                
                # Impostiamo gli altri campi
                self.numero_gara_edit.setText(str(iscrizione.numero_gara) if iscrizione.numero_gara else "")
                self.transponder_edit.setText(iscrizione.transponder_id or "")
                self.pagamento_check.setChecked(iscrizione.pagamento_effettuato)
                
                # Note
                if hasattr(iscrizione, 'note') and iscrizione.note:
                    self.note_edit.setText(iscrizione.note)
        
        finally:
            db.close()
    
    def accept(self):
        """Salva i dati dell'iscrizione nel database"""
        # Verifichiamo che i campi obbligatori siano compilati
        pilota_id = self.pilota_combo.currentData()
        evento_id = self.evento_combo.currentData()
        categoria_id = self.categoria_combo.currentData()
        numero_gara = self.numero_gara_edit.text().strip()
        
        if not pilota_id or not evento_id or not categoria_id or not numero_gara:
            QMessageBox.warning(self, "Campi obbligatori", "I campi Pilota, Evento, Categoria e Numero gara sono obbligatori")
            return
        
        # Verifichiamo che il numero di gara non sia già assegnato per lo stesso evento
        db = SessionLocal()
        
        try:
            # Controlla se il numero di gara è già usato nell'evento
            existing = db.query(Iscrizione).filter(
                Iscrizione.evento_id == evento_id,
                Iscrizione.numero_gara == numero_gara
            ).first()
            
            if existing and (not self.iscrizione_id or existing.id != self.iscrizione_id):
                QMessageBox.warning(self, "Numero già assegnato", 
                                   f"Il numero {numero_gara} è già assegnato per questo evento")
                return
            
            # Verifichiamo che il pilota non sia già iscritto all'evento
            existing = db.query(Iscrizione).filter(
                Iscrizione.pilota_id == pilota_id,
                Iscrizione.evento_id == evento_id
            ).first()
            
            if existing and (not self.iscrizione_id or existing.id != self.iscrizione_id):
                QMessageBox.warning(self, "Pilota già iscritto", 
                                   "Questo pilota è già iscritto a questo evento")
                return
            
            # Se stiamo modificando un'iscrizione esistente, la carichiamo
            if self.iscrizione_id:
                iscrizione = db.query(Iscrizione).get(self.iscrizione_id)
            else:
                # Altrimenti creiamo una nuova iscrizione
                iscrizione = Iscrizione()
                iscrizione.timestamp_iscrizione = QDateTime.currentDateTime().toPython()
            
            # Aggiorniamo i dati dell'iscrizione
            iscrizione.pilota_id = pilota_id
            iscrizione.evento_id = evento_id
            iscrizione.categoria_id = categoria_id
            iscrizione.numero_gara = int(numero_gara)
            iscrizione.transponder_id = self.transponder_edit.text().strip() or None
            iscrizione.pagamento_effettuato = self.pagamento_check.isChecked()
            
            # Note aggiuntive
            if hasattr(iscrizione, 'note'):
                iscrizione.note = self.note_edit.toPlainText()
            
            # Se è una nuova iscrizione, la aggiungiamo al database
            if not self.iscrizione_id:
                db.add(iscrizione)
            
            # Salviamo le modifiche
            db.commit()
            
            # Chiudiamo il dialogo
            super().accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Si è verificato un errore: {str(e)}")
            
        finally:
            db.close()