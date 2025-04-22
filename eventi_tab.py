# ui/eventi_tab.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox)
from PyQt6.QtCore import Qt

from database.connection import SessionLocal
from database.models import Evento
from .evento_dialog import EventoDialog  # Importiamo la classe dal nuovo file

class EventiTab(QWidget):
    def __init__(self):
        super().__init__()
        
        # Layout principale
        layout = QVBoxLayout(self)
        
        # Layout pulsanti
        button_layout = QHBoxLayout()
        
        # Pulsanti
        self.add_button = QPushButton("Aggiungi Evento")
        self.edit_button = QPushButton("Modifica Evento")
        self.delete_button = QPushButton("Elimina Evento")
        
        # Colleghiamo i pulsanti alle funzioni
        self.add_button.clicked.connect(self.add_evento)
        self.edit_button.clicked.connect(self.edit_evento)
        self.delete_button.clicked.connect(self.delete_evento)
        
        # Aggiungiamo i pulsanti al layout
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()
        
        # Tabella eventi
        self.eventi_table = QTableWidget()
        self.eventi_table.setColumnCount(5)
        self.eventi_table.setHorizontalHeaderLabels([
            "ID", "Nome Evento", "Data", "Circuito", "Moto Club Organizzatore"
        ])
        
        # Adattiamo le colonne
        self.eventi_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Aggiungiamo i layout al layout principale
        layout.addLayout(button_layout)
        layout.addWidget(self.eventi_table)
        
        # Carichiamo gli eventi
        self.load_eventi()
    
    def load_eventi(self):
        """Carica gli eventi dal database nella tabella"""
        db = SessionLocal()
        
        try:
            eventi = db.query(Evento).all()
            
            self.eventi_table.setRowCount(len(eventi))
            
            for i, evento in enumerate(eventi):
                self.eventi_table.setItem(i, 0, QTableWidgetItem(str(evento.id)))
                self.eventi_table.setItem(i, 1, QTableWidgetItem(evento.nome))
                self.eventi_table.setItem(i, 2, QTableWidgetItem(evento.data.strftime("%d/%m/%Y")))
                self.eventi_table.setItem(i, 3, QTableWidgetItem(evento.circuito))
                self.eventi_table.setItem(i, 4, QTableWidgetItem(evento.moto_club_organizzatore or ""))
        
        finally:
            db.close()
    
    def add_evento(self):
        """Apre un dialogo per aggiungere un nuovo evento"""
        dialog = EventoDialog(self)  # Usiamo la classe importata
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_eventi()
    
    def edit_evento(self):
        """Apre un dialogo per modificare un evento selezionato"""
        selected_rows = self.eventi_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Attenzione", "Seleziona un evento da modificare")
            return
        
        evento_id = int(self.eventi_table.item(selected_rows[0].row(), 0).text())
        
        dialog = EventoDialog(self, evento_id)  # Usiamo la classe importata
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_eventi()
    
    def delete_evento(self):
        """Elimina l'evento selezionato"""
        selected_rows = self.eventi_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Attenzione", "Seleziona un evento da eliminare")
            return
        
        evento_id = int(self.eventi_table.item(selected_rows[0].row(), 0).text())
        
        reply = QMessageBox.question(self, "Conferma eliminazione", 
                                    "Sei sicuro di voler eliminare questo evento?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            db = SessionLocal()
            try:
                evento = db.query(Evento).get(evento_id)
                if evento:
                    db.delete(evento)
                    db.commit()
                    self.load_eventi()
            finally:
                db.close()