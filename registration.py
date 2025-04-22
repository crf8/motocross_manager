# ui/registration.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLabel, QLineEdit, QDateEdit, QComboBox, QPushButton,
    QSpinBox, QMessageBox, QTableWidget, QTableWidgetItem
)
from PyQt6.QtCore import Qt, QDate

from database.connection import SessionLocal
from database.models import Pilota

class RegistrationForm(QWidget):
    def __init__(self):
        super().__init__()
        
        # Layout principale
        self.layout = QVBoxLayout(self)
        
        # Titolo
        self.title_label = QLabel("Registrazione Piloti")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.layout.addWidget(self.title_label)
        
        # Form layout
        self.form_layout = QFormLayout()
        
        # Campi del form
        self.nome_input = QLineEdit()
        self.form_layout.addRow("Nome:", self.nome_input)
        
        self.cognome_input = QLineEdit()
        self.form_layout.addRow("Cognome:", self.cognome_input)
        
        self.data_nascita_input = QDateEdit()
        self.data_nascita_input.setDisplayFormat("dd/MM/yyyy")
        self.data_nascita_input.setCalendarPopup(True)
        self.data_nascita_input.setDate(QDate.currentDate().addYears(-18))  # Default 18 anni fa
        self.form_layout.addRow("Data di Nascita:", self.data_nascita_input)
        
        self.email_input = QLineEdit()
        self.form_layout.addRow("Email:", self.email_input)
        
        self.telefono_input = QLineEdit()
        self.form_layout.addRow("Telefono:", self.telefono_input)
        
        self.moto_club_input = QLineEdit()
        self.form_layout.addRow("Moto Club:", self.moto_club_input)
        
        self.licenza_tipo_input = QComboBox()
        self.licenza_tipo_input.addItems([
            "Elite", "Fuoristrada", "MiniOffroad", 
            "Fuoristrada One Event", "Estensione Fuoristrada", 
            "Licenza Velocità", "Training"
        ])
        self.form_layout.addRow("Tipo Licenza:", self.licenza_tipo_input)
        
        self.numero_licenza_input = QLineEdit()
        self.form_layout.addRow("Numero Licenza:", self.numero_licenza_input)
        
        self.regione_input = QComboBox()
        self.regione_input.addItems([
            "Lombardia", "Piemonte", "Veneto", "Emilia Romagna",
            "Toscana", "Lazio", "Campania", "Puglia", "Sicilia",
            "Sardegna", "Liguria", "Marche", "Abruzzo", "Calabria",
            "Trentino Alto Adige", "Friuli Venezia Giulia", "Umbria",
            "Molise", "Valle d'Aosta", "Basilicata"
        ])
        self.form_layout.addRow("Regione:", self.regione_input)
        
        # Aggiungi il form layout al layout principale
        self.layout.addLayout(self.form_layout)
        
        # Bottoni
        self.button_layout = QHBoxLayout()
        
        self.clear_button = QPushButton("Pulisci")
        self.clear_button.clicked.connect(self.clear_form)
        self.button_layout.addWidget(self.clear_button)
        
        self.save_button = QPushButton("Salva")
        self.save_button.clicked.connect(self.save_pilot)
        self.button_layout.addWidget(self.save_button)
        
        self.layout.addLayout(self.button_layout)
        
        # Tabella piloti registrati
        self.piloti_table = QTableWidget(0, 5)  # 0 righe, 5 colonne
        self.piloti_table.setHorizontalHeaderLabels(["ID", "Nome", "Cognome", "Data Nascita", "Licenza"])
        self.layout.addWidget(self.piloti_table)
        
        # Popola tabella con dati esistenti
        self.load_pilots()
    
    def clear_form(self):
        """Pulisce tutti i campi del form"""
        self.nome_input.clear()
        self.cognome_input.clear()
        self.data_nascita_input.setDate(QDate.currentDate().addYears(-18))
        self.email_input.clear()
        self.telefono_input.clear()
        self.moto_club_input.clear()
        self.licenza_tipo_input.setCurrentIndex(0)
        self.numero_licenza_input.clear()
        self.regione_input.setCurrentIndex(0)
    
    def save_pilot(self):
        """Salva i dati del pilota nel database"""
        # Verifica campi obbligatori
        if not self.nome_input.text() or not self.cognome_input.text() or not self.numero_licenza_input.text():
            QMessageBox.warning(self, "Errore", "Nome, cognome e numero licenza sono obbligatori!")
            return
        
        # Crea nuovo pilota
        try:
            db = SessionLocal()
            nuovo_pilota = Pilota(
                nome=self.nome_input.text(),
                cognome=self.cognome_input.text(),
                data_nascita=self.data_nascita_input.date().toPyDate(),
                email=self.email_input.text(),
                telefono=self.telefono_input.text(),
                moto_club=self.moto_club_input.text(),
                licenza_tipo=self.licenza_tipo_input.currentText(),
                numero_licenza=self.numero_licenza_input.text(),
                regione=self.regione_input.currentText()
            )
            
            db.add(nuovo_pilota)
            db.commit()
            db.refresh(nuovo_pilota)
            
            QMessageBox.information(self, "Successo", f"Pilota {nuovo_pilota.nome} {nuovo_pilota.cognome} registrato con successo!")
            self.clear_form()
            self.load_pilots()  # Ricarica tabella piloti
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante il salvataggio: {str(e)}")
        finally:
            db.close()
    
    def load_pilots(self):
        """Carica i piloti dal database nella tabella"""
        try:
            db = SessionLocal()
            piloti = db.query(Pilota).all()
            
            # Configura tabella
            self.piloti_table.setRowCount(len(piloti))
            
            # Popola tabella
            for row, pilota in enumerate(piloti):
                self.piloti_table.setItem(row, 0, QTableWidgetItem(str(pilota.id)))
                self.piloti_table.setItem(row, 1, QTableWidgetItem(pilota.nome))
                self.piloti_table.setItem(row, 2, QTableWidgetItem(pilota.cognome))
                self.piloti_table.setItem(row, 3, QTableWidgetItem(str(pilota.data_nascita)))
                self.piloti_table.setItem(row, 4, QTableWidgetItem(pilota.licenza_tipo))
            
            # Ridimensiona colonne
            self.piloti_table.resizeColumnsToContents()
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante il caricamento piloti: {str(e)}")
        finally:
            db.close()