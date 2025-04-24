# ui/eventi_tab.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QTableWidget, QTableWidgetItem, QHeaderView,
                            QDialog, QFormLayout, QLineEdit, QDateEdit,
                            QComboBox, QMessageBox)
from PyQt6.QtWidgets import (QWidget, ..., QDialog)  # Aggiungi QDialog qui

from database.connection import SessionLocal
from database.models import Evento

class EventiTab(QWidget):
    def __init__(self):
        super().__init__()
        
        # Crea il layout principale (come un contenitore dove metteremo tutto)
        layout = QVBoxLayout(self)
        
        # Crea il layout per i pulsanti (una fila orizzontale)
        button_layout = QHBoxLayout()
        
        # Aggiungi i pulsanti per gestire gli eventi
        self.add_button = QPushButton("Aggiungi Evento")
        self.edit_button = QPushButton("Modifica Evento")
        self.delete_button = QPushButton("Elimina Evento")
        
        # Collega i pulsanti alle funzioni (è come dire al programma cosa fare quando premi un pulsante)
        self.add_button.clicked.connect(self.add_evento)
        self.edit_button.clicked.connect(self.edit_evento)
        self.delete_button.clicked.connect(self.delete_evento)
        
        # Aggiungi i pulsanti al layout
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()  # Questo spinge i pulsanti a sinistra
        
        # Crea la tabella per mostrare gli eventi
        self.eventi_table = QTableWidget()
        self.eventi_table.setColumnCount(5)
        self.eventi_table.setHorizontalHeaderLabels(["ID", "Nome", "Data", "Circuito", "Moto Club Organizzatore"])
        
        # Adatta le colonne alla larghezza del contenuto
        self.eventi_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Aggiungi i layout al layout principale
        layout.addLayout(button_layout)
        layout.addWidget(self.eventi_table)
        
        # Carica gli eventi dal database
        self.load_eventi()
    
    def load_eventi(self):
        """Carica gli eventi dal database nella tabella"""
        # Apriamo una connessione al database (come aprire un libro per leggere)
        db = SessionLocal()
        
        try:
            # Ottieni tutti gli eventi
            eventi = db.query(Evento).all()
            
            # Imposta il numero di righe della tabella
            self.eventi_table.setRowCount(len(eventi))
            
            # Riempi la tabella con i dati
            for i, evento in enumerate(eventi):
                self.eventi_table.setItem(i, 0, QTableWidgetItem(str(evento.id)))
                self.eventi_table.setItem(i, 1, QTableWidgetItem(evento.nome))
                self.eventi_table.setItem(i, 2, QTableWidgetItem(evento.data.strftime("%d/%m/%Y")))
                self.eventi_table.setItem(i, 3, QTableWidgetItem(evento.circuito))
                self.eventi_table.setItem(i, 4, QTableWidgetItem(evento.moto_club_organizzatore or ""))
        
        finally:
            # Chiudi la connessione (ricordati sempre di chiudere il libro quando hai finito!)
            db.close()
    
    def add_evento(self):
        """Apre un dialogo per aggiungere un nuovo evento"""
        dialog = EventoDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Aggiorna la tabella
            self.load_eventi()
    
    def edit_evento(self):
        """Apre un dialogo per modificare un evento selezionato"""
        # Controlla se c'è un evento selezionato
        selected_rows = self.eventi_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Attenzione", "Seleziona un evento da modificare")
            return
        
        # Ottieni l'ID dell'evento dalla prima colonna
        evento_id = int(self.eventi_table.item(selected_rows[0].row(), 0).text())
        
        # Apri il dialogo di modifica
        dialog = EventoDialog(self, evento_id)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Aggiorna la tabella
            self.load_eventi()
    
    def delete_evento(self):
        """Elimina l'evento selezionato"""
        # Controlla se c'è un evento selezionato
        selected_rows = self.eventi_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Attenzione", "Seleziona un evento da eliminare")
            return
        
        # Ottieni l'ID dell'evento dalla prima colonna
        evento_id = int(self.eventi_table.item(selected_rows[0].row(), 0).text())
        
        # Chiedi conferma (è come dire "Sei sicuro? Questa azione non si può annullare!")
        reply = QMessageBox.question(self, "Conferma eliminazione", 
                                     "Sei sicuro di voler eliminare questo evento?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            # Elimina l'evento
            db = SessionLocal()
            try:
                evento = db.query(Evento).get(evento_id)
                if evento:
                    db.delete(evento)
                    db.commit()
                    # Aggiorna la tabella
                    self.load_eventi()
            finally:
                db.close()


class EventoDialog(QDialog):
    def __init__(self, parent=None, evento_id=None):
        super().__init__(parent)
        
        self.evento_id = evento_id
        self.setWindowTitle("Aggiungi Evento" if evento_id is None else "Modifica Evento")
        
        # Crea il layout
        layout = QFormLayout(self)
        
        # Crea i campi per i dati dell'evento
        self.nome_edit = QLineEdit()
        self.data_edit = QDateEdit()
        self.data_edit.setCalendarPopup(True)  # Mostra un piccolo calendario per scegliere la data
        self.data_edit.setDate(QDate.currentDate())  # Imposta la data di oggi come predefinita
        self.circuito_edit = QLineEdit()
        self.moto_club_edit = QLineEdit()
        self.tipo_edit = QComboBox()
        self.tipo_edit.addItems(["Campionato", "Trofeo", "Allenamento"])
        
        # Aggiungi i campi al layout
        layout.addRow("Nome:", self.nome_edit)
        layout.addRow("Data:", self.data_edit)
        layout.addRow("Circuito:", self.circuito_edit)
        layout.addRow("Moto Club Organizzatore:", self.moto_club_edit)
        layout.addRow("Tipo:", self.tipo_edit)
        
        # Aggiungi i pulsanti
        self.save_button = QPushButton("Salva")
        self.cancel_button = QPushButton("Annulla")
        
        # Collega i pulsanti alle funzioni
        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
        # Aggiungi i pulsanti al layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        layout.addRow("", button_layout)
        
        # Se stiamo modificando un evento esistente, carica i suoi dati
        if evento_id is not None:
            self.load_evento_data()
    
    def load_evento_data(self):
        """Carica i dati dell'evento esistente nei campi del form"""
        db = SessionLocal()
        try:
            evento = db.query(Evento).get(self.evento_id)
            if evento:
                self.nome_edit.setText(evento.nome)
                self.data_edit.setDate(QDate.fromString(evento.data.strftime("%Y-%m-%d"), "yyyy-MM-dd"))
                self.circuito_edit.setText(evento.circuito)
                self.moto_club_edit.setText(evento.moto_club_organizzatore or "")
                
                # Trova l'indice del tipo di evento nel combo box
                tipo_index = self.tipo_edit.findText(evento.tipo)
                if tipo_index >= 0:
                    self.tipo_edit.setCurrentIndex(tipo_index)
        finally:
            db.close()
    
    def accept(self):
        """Salva i dati dell'evento nel database"""
        # Controlla che i campi obbligatori siano compilati
        if not self.nome_edit.text() or not self.circuito_edit.text():
            QMessageBox.warning(self, "Campi obbligatori", "I campi Nome e Circuito sono obbligatori")
            return
        
        # Apri una connessione al database
        db = SessionLocal()
        
        try:
            # Se stiamo modificando un evento esistente, caricalo
            if self.evento_id is not None:
                evento = db.query(Evento).get(self.evento_id)
            else:
                # Altrimenti crea un nuovo evento
                evento = Evento()
            
            # Aggiorna i dati dell'evento
            evento.nome = self.nome_edit.text()
            evento.data = self.data_edit.date().toPython()
            evento.circuito = self.circuito_edit.text()
            evento.moto_club_organizzatore = self.moto_club_edit.text()
            evento.tipo = self.tipo_edit.currentText()
            
            # Se è un nuovo evento, aggiungilo al database
            if self.evento_id is None:
                db.add(evento)
            
            # Salva le modifiche
            db.commit()
            
            # Chiudi il dialogo
            super().accept()
            
        except Exception as e:
            # Se c'è un errore, mostra un messaggio
            QMessageBox.critical(self, "Errore", f"Si è verificato un errore: {str(e)}")
            
        finally:
            # Chiudi la connessione
            db.close()