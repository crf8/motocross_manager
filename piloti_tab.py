from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QTableWidget, QTableWidgetItem, QPushButton, QDialog, QLineEdit,
                           QDateEdit, QSpinBox, QComboBox, QMessageBox,
                           QHeaderView, QScrollArea, QFrame, QCheckBox)  # Aggiungi QCheckBox qui!
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QIcon


class PilotiTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Creiamo il layout principale
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Aggiungiamo un'etichetta
        title_label = QLabel("Gestione Piloti")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Aggiungiamo la tabella dei piloti
        self.piloti_table = QTableWidget()
        self.piloti_table.setColumnCount(8)
        self.piloti_table.setHorizontalHeaderLabels(["ID", "Nome", "Cognome", "Data Nascita", "Numero", "Categoria", "Moto", "Team"])
        self.piloti_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Stile moderno per la tabella
        self.piloti_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                background-color: white;
                gridline-color: #f0f0f0;
                selection-background-color: #2196F3;
                selection-color: white;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
            }
            QTableWidget::item:selected {
                background-color: #2196F3;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                border: none;
                padding: 10px;
            }
        """)
        
        # Imposta altre proprietà per rendere la tabella più moderna
        self.piloti_table.setShowGrid(False)  # Nascondi la griglia per un look più pulito
        self.piloti_table.setAlternatingRowColors(True)  # Righe alternate di colore
        self.piloti_table.verticalHeader().setVisible(False)  # Nascondi i numeri di riga
        self.piloti_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)  # Seleziona righe intere
        self.piloti_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)  # Disabilita modifica diretta
        layout.addWidget(self.piloti_table)
        
        # Pulsanti per gestire i piloti
        buttons_layout = QHBoxLayout()
        
        self.btn_aggiungi = QPushButton("Aggiungi Pilota")
        self.btn_modifica = QPushButton("Modifica Pilota")
        self.btn_elimina = QPushButton("Elimina Pilota")
        self.btn_statistiche = QPushButton("Statistiche")
        
        self.btn_aggiungi.clicked.connect(self.add_pilota)
        self.btn_modifica.clicked.connect(self.edit_pilota)
        self.btn_elimina.clicked.connect(self.delete_pilota)
        self.btn_statistiche.clicked.connect(self.visualizza_statistiche_pilota_selezionato)
        
        buttons_layout.addWidget(self.btn_aggiungi)
        buttons_layout.addWidget(self.btn_modifica)
        buttons_layout.addWidget(self.btn_elimina)
        buttons_layout.addWidget(self.btn_statistiche)
        
        layout.addLayout(buttons_layout)
        
        # Carichiamo i piloti dal database
        self.load_piloti()


    def setup_buttons(self):
        # Crea un layout per i pulsanti con spazio attorno
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(10, 10, 10, 10)
        buttons_layout.setSpacing(15)  # Più spazio tra i pulsanti
        
        # Stile moderno per i pulsanti
        button_style = """
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1f6aa5;
            }
        """
        
        # Crea i pulsanti con icone
        self.btn_aggiungi = QPushButton("Aggiungi Pilota")
        self.btn_aggiungi.setIcon(QIcon("icons/add.png"))  # Aggiungi icone se le hai
        self.btn_modifica = QPushButton("Modifica Pilota")
        self.btn_modifica.setIcon(QIcon("icons/edit.png"))
        self.btn_elimina = QPushButton("Elimina Pilota")
        self.btn_elimina.setIcon(QIcon("icons/delete.png"))
        self.btn_statistiche = QPushButton("Statistiche")
        self.btn_statistiche.setIcon(QIcon("icons/stats.png"))
        
        # Applica lo stile a tutti i pulsanti
        self.btn_aggiungi.setStyleSheet(button_style)
        self.btn_modifica.setStyleSheet(button_style)
        self.btn_elimina.setStyleSheet(button_style)
        self.btn_statistiche.setStyleSheet(button_style)
        
        # Aggiungi i pulsanti al layout
        buttons_layout.addWidget(self.btn_aggiungi)
        buttons_layout.addWidget(self.btn_modifica)
        buttons_layout.addWidget(self.btn_elimina)
        buttons_layout.addWidget(self.btn_statistiche)
        
        return buttons_layout
        
    def load_piloti(self):
        """Carica i piloti dal database"""
        try:
            # Qui dovremmo connetterci al database e caricare i piloti
            # Per ora lasciamo vuoto o con dati di esempio
            self.piloti_table.setRowCount(0)  # Puliamo la tabella
            
            # Esempio: aggiungiamo un pilota di prova
            row_position = self.piloti_table.rowCount()
            self.piloti_table.insertRow(row_position)
            self.piloti_table.setItem(row_position, 0, QTableWidgetItem("1"))
            self.piloti_table.setItem(row_position, 1, QTableWidgetItem("Mario"))
            self.piloti_table.setItem(row_position, 2, QTableWidgetItem("Rossi"))
            self.piloti_table.setItem(row_position, 3, QTableWidgetItem("01/01/1990"))
            self.piloti_table.setItem(row_position, 4, QTableWidgetItem("46"))
            self.piloti_table.setItem(row_position, 5, QTableWidgetItem("MX1"))
            self.piloti_table.setItem(row_position, 6, QTableWidgetItem("Honda"))
            self.piloti_table.setItem(row_position, 7, QTableWidgetItem("Team A"))
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Impossibile caricare i piloti: {str(e)}")
    
    def add_pilota(self):
        """Apre la finestra di dialogo per aggiungere un pilota"""
        dialog = PilotaDialog(self)
        if dialog.exec():
            # Qui dovremmo salvare il nuovo pilota nel database
            QMessageBox.information(self, "Successo", "Pilota aggiunto con successo!")
            self.load_piloti()  # Ricarichiamo la lista
    
    def edit_pilota(self):
        """Modifica il pilota selezionato"""
        selected_row = self.piloti_table.currentRow()
        if selected_row >= 0:
            # Qui dovremmo aprire il dialog di modifica
            QMessageBox.information(self, "Info", "Funzionalità di modifica da implementare")
        else:
            QMessageBox.warning(self, "Attenzione", "Seleziona un pilota da modificare")
    
    def delete_pilota(self):
        """Elimina il pilota selezionato"""
        selected_row = self.piloti_table.currentRow()
        if selected_row >= 0:
            reply = QMessageBox.question(self, "Conferma", "Sei sicuro di voler eliminare questo pilota?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                # Qui dovremmo eliminare il pilota dal database
                QMessageBox.information(self, "Successo", "Pilota eliminato con successo!")
                self.load_piloti()  # Ricarichiamo la lista
        else:
            QMessageBox.warning(self, "Attenzione", "Seleziona un pilota da eliminare")
    
    def visualizza_statistiche_pilota_selezionato(self):
        """Visualizza le statistiche del pilota selezionato"""
        selected_row = self.piloti_table.currentRow()
        if selected_row >= 0:
            pilota_id = self.piloti_table.item(selected_row, 0).text()
            QMessageBox.information(self, "Statistiche", f"Statistiche del pilota {pilota_id} da implementare")
        else:
            QMessageBox.warning(self, "Attenzione", "Seleziona un pilota per visualizzare le statistiche")

class PilotaDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Aggiungi Pilota")
        self.resize(500, 650)
        
        # Impostiamo uno stile generale più moderno
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel {
                color: #333333;
                font-size: 12px;
                font-weight: bold;
            }
            QLineEdit, QDateEdit, QSpinBox, QComboBox {
                padding: 8px;
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
                min-height: 20px;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
            QPushButton#btn_annulla {
                background-color: #e0e0e0;
                color: #333333;
            }
            QPushButton#btn_annulla:hover {
                background-color: #c7c7c7;
            }
        """)
        
        # Creiamo un layout principale con margini più ampi per un aspetto moderno
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(10)
        self.setLayout(main_layout)
        
        # Titolo in alto
        titolo = QLabel("Informazioni Pilota")
        titolo.setStyleSheet("font-size: 18px; margin-bottom: 15px;")
        titolo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(titolo)
        
        # Creiamo un widget scroll per contenere tutti i campi
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        # Widget che conterrà tutti i campi
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(15)
        
        # Funzione helper per creare i campi
        def add_field(label_text, input_widget, layout):
            field_layout = QVBoxLayout()  # Cambiato in verticale per un look più moderno
            field_layout.setSpacing(5)
            
            label = QLabel(label_text)
            field_layout.addWidget(label)
            field_layout.addWidget(input_widget)
            
            layout.addLayout(field_layout)
        
        # Sezione Dati Personali
        section_personale = QLabel("Dati Personali")
        section_personale.setStyleSheet("font-size: 14px; color: #2196F3; border-bottom: 1px solid #2196F3; padding-bottom: 5px;")
        layout.addWidget(section_personale)
        
        # Nome
        self.nome_input = QLineEdit()
        self.nome_input.setPlaceholderText("Inserisci il nome")
        add_field("Nome:", self.nome_input, layout)
        
        # Cognome
        self.cognome_input = QLineEdit()
        self.cognome_input.setPlaceholderText("Inserisci il cognome")
        add_field("Cognome:", self.cognome_input, layout)
        
        # Data di nascita
        self.data_nascita_input = QDateEdit()
        self.data_nascita_input.setCalendarPopup(True)
        self.data_nascita_input.setDate(QDate.currentDate())
        add_field("Data di Nascita:", self.data_nascita_input, layout)
        
        # Luogo di nascita
        self.luogo_nascita_input = QLineEdit()
        self.luogo_nascita_input.setPlaceholderText("Città di nascita")
        add_field("Luogo di nascita:", self.luogo_nascita_input, layout)

        # Provincia di nascita
        self.provincia_nascita_input = QLineEdit()
        self.provincia_nascita_input.setPlaceholderText("Provincia di nascita (es. MI)")
        add_field("Provincia di nascita:", self.provincia_nascita_input, layout)
        
        # Sezione Contatti
        section_contatti = QLabel("Residenza attuale e Contatti")
        section_contatti.setStyleSheet("font-size: 14px; color: #2196F3; border-bottom: 1px solid #2196F3; padding-bottom: 5px; margin-top: 10px;")
        layout.addWidget(section_contatti)
        
        # Telefono
        self.telefono_input = QLineEdit()
        self.telefono_input.setPlaceholderText("Inserisci il numero di telefono")
        add_field("Telefono:", self.telefono_input, layout)
        
        # Indirizzo
        self.indirizzo_input = QLineEdit()
        self.indirizzo_input.setPlaceholderText("Via e numero civico")
        add_field("Indirizzo:", self.indirizzo_input, layout)
        
        # Layout orizzontale per città e CAP
        city_cap_layout = QHBoxLayout()
        city_cap_layout.setSpacing(10)
        
        # Città
        city_field = QVBoxLayout()
        city_field.setSpacing(5)
        city_label = QLabel("Città:")
        self.citta_input = QLineEdit()
        self.citta_input.setPlaceholderText("Città")
        city_field.addWidget(city_label)
        city_field.addWidget(self.citta_input)
        city_cap_layout.addLayout(city_field, 2)  # 2/3 dello spazio
        
        # CAP
        cap_field = QVBoxLayout()
        cap_field.setSpacing(5)
        cap_label = QLabel("CAP:")
        self.cap_input = QLineEdit()
        self.cap_input.setPlaceholderText("CAP")
        cap_field.addWidget(cap_label)
        cap_field.addWidget(self.cap_input)
        city_cap_layout.addLayout(cap_field, 1)  # 1/3 dello spazio
        
        layout.addLayout(city_cap_layout)
        
        # Provincia
        self.provincia_input = QLineEdit()
        self.provincia_input.setPlaceholderText("Provincia (es. MI)")
        add_field("Provincia:", self.provincia_input, layout)
        
        # Sezione Info Gara
        section_gara = QLabel("Informazioni Gara")
        section_gara.setStyleSheet("font-size: 14px; color: #2196F3; border-bottom: 1px solid #2196F3; padding-bottom: 5px; margin-top: 10px;")
        layout.addWidget(section_gara)
        
        # Numero di Gara
        self.numero_gara_input = QSpinBox()
        self.numero_gara_input.setMinimum(1)
        self.numero_gara_input.setMaximum(999)
        add_field("Numero di Gara:", self.numero_gara_input, layout)
        
        # Categoria
        self.categoria_input = QComboBox()
        self.categoria_input.addItems(["MX1", "MX2", "125", "85", "65", "50", "FEMMINILE", "TRAINING"])
        add_field("Categoria:", self.categoria_input, layout)
        
        # Sottocategorie (da pagina 4-5 del regolamento)
        sottocategoria_layout = QHBoxLayout()
        sottocategoria_label = QLabel("Sottocategoria:")
        self.sottocategoria_input = QComboBox()
        # Aggiungiamo le sottocategorie in base alla categoria principale
        self.sottocategoria_input.addItems(["Elite", "Fast", "Expert", "Rider", "Challenge", 
                                "Master", "Superveteran", "Veteran", "Senior", "Junior", 
                                "Cadetti", "Debuttanti", "Training"])
        sottocategoria_layout.addWidget(sottocategoria_label)
        sottocategoria_layout.addWidget(self.sottocategoria_input)
        layout.addLayout(sottocategoria_layout)

        # Gruppo (A, B, C)
        gruppo_layout = QHBoxLayout()
        gruppo_label = QLabel("Gruppo:")
        self.gruppo_input = QComboBox()
        self.gruppo_input.addItems(["Gruppo A", "Gruppo B", "Gruppo C"])
        gruppo_layout.addWidget(gruppo_label)
        gruppo_layout.addWidget(self.gruppo_input)
        layout.addLayout(gruppo_layout)
        
        # Moto
        self.moto_input = QLineEdit()
        self.moto_input.setPlaceholderText("Marca e modello")
        add_field("Moto:", self.moto_input, layout)
        
        # Cilindrata
        self.cilindrata_input = QLineEdit()
        self.cilindrata_input.setPlaceholderText("es. 450cc")
        add_field("Cilindrata:", self.cilindrata_input, layout)
        
        # Dettagli sulla cilindrata (importante per classi come da tabella pagina 4-5)
        cilindrata_dettaglio_layout = QHBoxLayout()
        cilindrata_dettaglio_label = QLabel("Tipo motore:")
        self.cilindrata_dettaglio_input = QComboBox()
        self.cilindrata_dettaglio_input.addItems(["2T (2 tempi)", "4T (4 tempi)"])
        cilindrata_dettaglio_layout.addWidget(cilindrata_dettaglio_label)
        cilindrata_dettaglio_layout.addWidget(self.cilindrata_dettaglio_input)
        layout.addLayout(cilindrata_dettaglio_layout)

        # Età (importante per categorie come Debuttanti/Junior ecc.)
        eta_layout = QHBoxLayout()
        eta_label = QLabel("Anno di nascita (per categoria):")
        self.eta_input = QSpinBox()
        self.eta_input.setRange(1950, 2020)
        self.eta_input.setValue(2000)
        eta_layout.addWidget(eta_label)
        eta_layout.addWidget(self.eta_input)
        layout.addLayout(eta_layout)
        
        # Team
        self.team_input = QLineEdit()
        self.team_input.setPlaceholderText("Nome del team")
        add_field("Team:", self.team_input, layout)
        
        # Moto Club
        self.motoclub_input = QLineEdit()
        self.motoclub_input.setPlaceholderText("Moto Club di appartenenza")
        add_field("Moto Club:", self.motoclub_input, layout)

        # Sezione Seconda Moto
        section_seconda_moto = QLabel("Seconda Moto (opzionale)")
        section_seconda_moto.setStyleSheet("font-size: 14px; color: #2196F3; border-bottom: 1px solid #2196F3; padding-bottom: 5px; margin-top: 10px;")
        layout.addWidget(section_seconda_moto)

        # Seconda Moto 
        self.seconda_moto_input = QLineEdit()
        self.seconda_moto_input.setPlaceholderText("Marca e modello seconda moto")
        add_field("Seconda Moto:", self.seconda_moto_input, layout)

        # Cilindrata seconda moto
        self.seconda_cilindrata_input = QLineEdit()
        self.seconda_cilindrata_input.setPlaceholderText("es. 250cc")
        add_field("Cilindrata seconda moto:", self.seconda_cilindrata_input, layout)

        # Tipo motore seconda moto
        seconda_cilindrata_dettaglio_layout = QHBoxLayout()
        seconda_cilindrata_dettaglio_label = QLabel("Tipo motore seconda moto:")
        self.seconda_cilindrata_dettaglio_input = QComboBox()
        self.seconda_cilindrata_dettaglio_input.addItems(["2T (2 tempi)", "4T (4 tempi)"])
        seconda_cilindrata_dettaglio_layout.addWidget(seconda_cilindrata_dettaglio_label)
        seconda_cilindrata_dettaglio_layout.addWidget(self.seconda_cilindrata_dettaglio_input)
        layout.addLayout(seconda_cilindrata_dettaglio_layout)
        
        # Sezione Licenza
        section_licenza = QLabel("Licenza FMI")
        section_licenza.setStyleSheet("font-size: 14px; color: #2196F3; border-bottom: 1px solid #2196F3; padding-bottom: 5px; margin-top: 10px;")
        layout.addWidget(section_licenza)
        
        # Numero Licenza
        self.licenza_input = QLineEdit()
        self.licenza_input.setPlaceholderText("Numero di licenza")
        add_field("Licenza:", self.licenza_input, layout)
        
        # Tipo di licenza
        self.tipo_licenza_input = QComboBox()
        self.tipo_licenza_input.addItems(["ELITE", "FUORISTRADA", "MINOFFROAD", "FUORISTRADA ONE EVENT", 
                                      "ESTENSIONE FUORISTRADA", "LICENZA VELOCITA'", "TRAINING"])
        add_field("Tipo Licenza:", self.tipo_licenza_input, layout)
        
        # Campo per la data richiesta numero fisso
        richiesta_numero_layout = QHBoxLayout()
        richiesta_numero_label = QLabel("Richiesta numero fisso:")
        self.richiesta_numero_input = QCheckBox("Richiedo numero fisso per la stagione")
        richiesta_numero_layout.addWidget(richiesta_numero_label)
        richiesta_numero_layout.addWidget(self.richiesta_numero_input)
        layout.addLayout(richiesta_numero_layout)

        # Dettagli specifici per SIGMA-FMI
        sigma_fmi_layout = QHBoxLayout()
        sigma_fmi_label = QLabel("Codice SIGMA-FMI:")
        self.sigma_fmi_input = QLineEdit()
        self.sigma_fmi_input.setPlaceholderText("Inserire codice da portale SIGMA-FMI")
        sigma_fmi_layout.addWidget(sigma_fmi_label)
        sigma_fmi_layout.addWidget(self.sigma_fmi_input)
        layout.addLayout(sigma_fmi_layout)
        
        # Regione
        self.regione_input = QComboBox()
        self.regione_input.addItems(["Lombardia", "Piemonte", "Liguria", "Altre"])
        add_field("Regione:", self.regione_input, layout)
        
        # Data Scadenza Visita Medica
        self.visita_medica_input = QDateEdit()
        self.visita_medica_input.setCalendarPopup(True)
        self.visita_medica_input.setDate(QDate.currentDate().addYears(1))
        add_field("Scadenza Visita Medica:", self.visita_medica_input, layout)
        
        # Dettagli iscrizione campionato/singola gara
        iscrizione_tipo_layout = QHBoxLayout()
        iscrizione_tipo_label = QLabel("Tipo iscrizione:")
        self.iscrizione_tipo_input = QComboBox()
        self.iscrizione_tipo_input.addItems(["Singola gara (€60,00)", "Tutto il campionato (€360,00)"])
        iscrizione_tipo_layout.addWidget(iscrizione_tipo_label)
        iscrizione_tipo_layout.addWidget(self.iscrizione_tipo_input)
        layout.addLayout(iscrizione_tipo_layout)

        # Tappetino ambientale (obbligatorio come da punto 22.1)
        tappetino_layout = QHBoxLayout()
        tappetino_label = QLabel("Tappetino ambientale:")
        self.tappetino_input = QCheckBox("Confermo di avere il tappetino ambientale obbligatorio")
        tappetino_layout.addWidget(tappetino_label)
        tappetino_layout.addWidget(self.tappetino_input)
        layout.addLayout(tappetino_layout)
        
        # Aggiungiamo lo scrollArea al layout principale
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
        
        # Pulsanti in basso
        buttons_layout = QHBoxLayout()
        self.btn_salva = QPushButton("Salva")
        self.btn_annulla = QPushButton("Annulla")
        self.btn_annulla.setObjectName("btn_annulla")  # Per lo stile CSS
        
        self.btn_salva.clicked.connect(self.accept)
        self.btn_annulla.clicked.connect(self.reject)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.btn_annulla)
        buttons_layout.addWidget(self.btn_salva)
        
        main_layout.addLayout(buttons_layout)
    
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

    def view_pilot_statistics(self):
        """Visualizza le statistiche del pilota selezionato"""
        # Ottieni gli indici selezionati nella tabella
        selected_indexes = self.table_piloti.selectedIndexes()
        
        # Controlla se c'è una selezione
        if not selected_indexes:
            QMessageBox.information(self, "Informazione", "Seleziona prima un pilota dalla tabella.")
            return
        
        # Prendi l'ID del pilota selezionato (prima colonna)
        row = selected_indexes[0].row()
        pilot_id = self.table_piloti.item(row, 0).text()
        
        # Ottieni la finestra principale
        main_window = self.window()
        
        # Chiama il metodo per visualizzare le statistiche
        main_window.visualizza_statistiche_pilota(int(pilot_id))