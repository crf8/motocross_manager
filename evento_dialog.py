# ui/evento_dialog.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QFormLayout, QLineEdit, QDateEdit, QTimeEdit,
                            QComboBox, QMessageBox, QLabel, QSpinBox, 
                            QTextEdit, QScrollArea, QCheckBox, QGridLayout, QWidget)
from PyQt6.QtCore import Qt, QDate, QTime

from database.connection import SessionLocal
from database.models import Evento

class EventoDialog(QDialog):
    def __init__(self, parent=None, evento_id=None):
        super().__init__(parent)
        
        self.evento_id = evento_id
        self.setWindowTitle("Aggiungi Evento" if evento_id is None else "Modifica Evento")
        self.resize(600, 700)  # Finestra più grande
        
        # Area di scorrimento per molti campi
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        container = QWidget()
        layout = QFormLayout(container)
        
        # INFORMAZIONI GENERALI
        layout.addRow(QLabel("<b>INFORMAZIONI GENERALI</b>"))
        
        self.nome_edit = QLineEdit()
        self.data_edit = QDateEdit()
        self.data_edit.setCalendarPopup(True)
        self.data_edit.setDate(QDate.currentDate())
        self.tipo_evento_combo = QComboBox()
        self.tipo_evento_combo.addItems([
            "Campionato Regionale Motocross", 
            "Campionato Regionale Minicross",
            "Trofeo", 
            "Challenge",
            "Campionato Femminile",
            "Allenamento"
        ])
        
        layout.addRow("Nome evento *:", self.nome_edit)
        layout.addRow("Data *:", self.data_edit)
        layout.addRow("Tipo evento:", self.tipo_evento_combo)
        
        # INFORMAZIONI CIRCUITO
        layout.addRow(QLabel(""))
        layout.addRow(QLabel("<b>INFORMAZIONI CIRCUITO</b>"))
        
        self.circuito_edit = QLineEdit()
        self.regione_combo = QComboBox()
        self.regione_combo.addItems(["Lombardia", "Piemonte", "Veneto", "Emilia Romagna", 
                                    "Toscana", "Lazio", "Altre regioni"])
        self.indirizzo_edit = QLineEdit()
        self.lunghezza_pista_spin = QSpinBox()
        self.lunghezza_pista_spin.setRange(0, 5000)
        self.lunghezza_pista_spin.setSuffix(" metri")
        
        layout.addRow("Nome circuito *:", self.circuito_edit)
        layout.addRow("Regione:", self.regione_combo)
        layout.addRow("Indirizzo:", self.indirizzo_edit)
        layout.addRow("Lunghezza pista:", self.lunghezza_pista_spin)
        
        # INFORMAZIONI ORGANIZZATORE (dal regolamento FMI)
        layout.addRow(QLabel(""))
        layout.addRow(QLabel("<b>INFORMAZIONI ORGANIZZATORE</b>"))
        
        self.moto_club_edit = QLineEdit()
        self.contatto_organizzatore_edit = QLineEdit()
        self.email_organizzatore_edit = QLineEdit()
        self.telefono_organizzatore_edit = QLineEdit()
        
        layout.addRow("Moto Club organizzatore *:", self.moto_club_edit)
        layout.addRow("Persona di contatto:", self.contatto_organizzatore_edit)
        layout.addRow("Email:", self.email_organizzatore_edit)
        layout.addRow("Telefono:", self.telefono_organizzatore_edit)
        
        # TASSE FEDERALI (come da regolamento FMI)
        layout.addRow(QLabel(""))
        layout.addRow(QLabel("<b>TASSE FEDERALI</b>"))
        
        self.tic_spin = QSpinBox()
        self.tic_spin.setRange(0, 200)
        self.tic_spin.setValue(45)
        self.tic_spin.setSuffix(" €")
        
        self.tag_spin = QSpinBox()
        self.tag_spin.setRange(0, 200)
        self.tag_spin.setValue(40)
        self.tag_spin.setSuffix(" €")
        
        self.cpa_spin = QSpinBox()
        self.cpa_spin.setRange(0, 200)
        self.cpa_spin.setValue(60)
        self.cpa_spin.setSuffix(" €")
        
        self.diritto_segreteria_spin = QSpinBox()
        self.diritto_segreteria_spin.setRange(0, 200)
        self.diritto_segreteria_spin.setValue(60)
        self.diritto_segreteria_spin.setSuffix(" €")
        
        layout.addRow("TIC - Tassa Iscrizione a Calendario:", self.tic_spin)
        layout.addRow("TAG - Tassa Approvazione Gara:", self.tag_spin)
        layout.addRow("CPA - Cassa Fondo Prestazioni Assistenziali:", self.cpa_spin)
        layout.addRow("Diritto di Segreteria:", self.diritto_segreteria_spin)
        
        # SERVIZI TECNICI (dal regolamento)
        layout.addRow(QLabel(""))
        layout.addRow(QLabel("<b>SERVIZI TECNICI</b>"))
        
        self.diritto_urgenza_spin = QSpinBox()
        self.diritto_urgenza_spin.setRange(0, 200)
        self.diritto_urgenza_spin.setSuffix(" €")
        
        self.servizio_tecnico_spin = QSpinBox()
        self.servizio_tecnico_spin.setRange(0, 1000)
        self.servizio_tecnico_spin.setValue(350)
        self.servizio_tecnico_spin.setSuffix(" €")
        
        self.servizio_tecnico_supp_spin = QSpinBox()
        self.servizio_tecnico_supp_spin.setRange(0, 1000)
        self.servizio_tecnico_supp_spin.setValue(300)
        self.servizio_tecnico_supp_spin.setSuffix(" €")
        
        self.servizio_fonometrico_spin = QSpinBox()
        self.servizio_fonometrico_spin.setRange(0, 1000)
        self.servizio_fonometrico_spin.setValue(270)
        self.servizio_fonometrico_spin.setSuffix(" €")
        
        layout.addRow("Diritto di Urgenza:", self.diritto_urgenza_spin)
        layout.addRow("Diritto Servizio Tecnico (1-2 gg):", self.servizio_tecnico_spin)
        layout.addRow("Servizio Tecnico Supplementare:", self.servizio_tecnico_supp_spin)
        layout.addRow("Servizio Fonometrico:", self.servizio_fonometrico_spin)
        
        # STAFF TECNICO (come da regolamento FMI)
        layout.addRow(QLabel(""))
        layout.addRow(QLabel("<b>STAFF TECNICO</b>"))
        
        self.direttore_gara_edit = QLineEdit()
        self.commissario_percorso_edit = QLineEdit()
        self.medico_gara_edit = QLineEdit()
        self.cronometraggio_edit = QLineEdit()
        
        layout.addRow("Direttore di Gara (DDG):", self.direttore_gara_edit)
        layout.addRow("Commissario di Percorso:", self.commissario_percorso_edit)
        layout.addRow("Medico di Gara:", self.medico_gara_edit)
        layout.addRow("Servizio Cronometraggio:", self.cronometraggio_edit)
        
        # QUOTE E PAGAMENTI (dal regolamento FMI)
        layout.addRow(QLabel(""))
        layout.addRow(QLabel("<b>QUOTE E PAGAMENTI</b>"))
        
        self.quota_iscrizione_spin = QSpinBox()
        self.quota_iscrizione_spin.setRange(0, 200)
        self.quota_iscrizione_spin.setValue(60)
        self.quota_iscrizione_spin.setSuffix(" €")
        
        self.quota_campionato_spin = QSpinBox()
        self.quota_campionato_spin.setRange(0, 1000)
        self.quota_campionato_spin.setValue(360)
        self.quota_campionato_spin.setSuffix(" €")
        
        self.penale_iscrizione_tardiva_spin = QSpinBox()
        self.penale_iscrizione_tardiva_spin.setRange(0, 100)
        self.penale_iscrizione_tardiva_spin.setValue(30)
        self.penale_iscrizione_tardiva_spin.setSuffix(" €")
        
        self.scadenza_iscrizioni_edit = QDateEdit()
        self.scadenza_iscrizioni_edit.setCalendarPopup(True)
        # Impostiamo la scadenza al venerdì prima dell'evento (come da regolamento)
        default_date = self.data_edit.date()
        days_to_friday = (default_date.dayOfWeek() - 5) % 7
        if days_to_friday == 0:  # Se è già venerdì, prendiamo il venerdì precedente
            days_to_friday = 7
        self.scadenza_iscrizioni_edit.setDate(default_date.addDays(-days_to_friday))
        
        layout.addRow("Quota iscrizione singola gara:", self.quota_iscrizione_spin)
        layout.addRow("Quota iscrizione tutto il campionato:", self.quota_campionato_spin)
        layout.addRow("Penale iscrizione tardiva (50%):", self.penale_iscrizione_tardiva_spin)
        layout.addRow("Scadenza iscrizioni (venerdì prima):", self.scadenza_iscrizioni_edit)
        
        # PROGRAMMA GARA (come da regolamento FMI)
        layout.addRow(QLabel(""))
        layout.addRow(QLabel("<b>PROGRAMMA GARA</b>"))
        
        self.data_operazioni_preliminari_edit = QDateEdit()
        self.data_operazioni_preliminari_edit.setCalendarPopup(True)
        self.data_operazioni_preliminari_edit.setDate(self.data_edit.date())
        
        self.ora_inizio_verifiche_edit = QTimeEdit()
        self.ora_inizio_verifiche_edit.setTime(QTime(7, 30))  # Come da regolamento
        
        self.ora_fine_verifiche_edit = QTimeEdit()
        self.ora_fine_verifiche_edit.setTime(QTime(9, 0))
        
        self.ora_briefing_edit = QTimeEdit()
        self.ora_briefing_edit.setTime(QTime(9, 15))
        
        self.ora_inizio_prove_edit = QTimeEdit()
        self.ora_inizio_prove_edit.setTime(QTime(9, 30))
        
        self.ora_inizio_gare_edit = QTimeEdit()
        self.ora_inizio_gare_edit.setTime(QTime(13, 0))
        
        layout.addRow("Data operazioni preliminari:", self.data_operazioni_preliminari_edit)
        layout.addRow("Inizio verifiche (7:30 - 8:30):", self.ora_inizio_verifiche_edit)
        layout.addRow("Fine verifiche:", self.ora_fine_verifiche_edit)
        layout.addRow("Briefing piloti:", self.ora_briefing_edit)
        layout.addRow("Inizio prove libere/qualifiche:", self.ora_inizio_prove_edit)
        layout.addRow("Inizio gare:", self.ora_inizio_gare_edit)
        
        # CATEGORIE AMMESSE (dal regolamento FMI)
        layout.addRow(QLabel(""))
        layout.addRow(QLabel("<b>CATEGORIE AMMESSE</b>"))
        
        # Creiamo un layout a griglia per le categorie
        categorie_layout = QGridLayout()
        
        # MX1
        categorie_layout.addWidget(QLabel("<b>MX1</b>"), 0, 0)
        self.mx1_elite_check = QCheckBox("Elite")
        self.mx1_fast_check = QCheckBox("Fast")
        self.mx1_expert_check = QCheckBox("Expert")
        self.mx1_rider_check = QCheckBox("Rider")
        self.mx1_challenge_check = QCheckBox("Challenge")
        self.mx1_veteran_check = QCheckBox("Veteran")
        self.mx1_superveteran_check = QCheckBox("Superveteran")
        self.mx1_master_check = QCheckBox("Master")
        
        mx1_layout = QVBoxLayout()
        mx1_layout.addWidget(self.mx1_elite_check)
        mx1_layout.addWidget(self.mx1_fast_check)
        mx1_layout.addWidget(self.mx1_expert_check)
        mx1_layout.addWidget(self.mx1_rider_check)
        mx1_layout.addWidget(self.mx1_challenge_check)
        mx1_layout.addWidget(self.mx1_veteran_check)
        mx1_layout.addWidget(self.mx1_superveteran_check)
        mx1_layout.addWidget(self.mx1_master_check)
        
        mx1_widget = QWidget()
        mx1_widget.setLayout(mx1_layout)
        categorie_layout.addWidget(mx1_widget, 1, 0)
        
        # MX2
        categorie_layout.addWidget(QLabel("<b>MX2</b>"), 0, 1)
        self.mx2_elite_check = QCheckBox("Elite")
        self.mx2_fast_check = QCheckBox("Fast")
        self.mx2_expert_check = QCheckBox("Expert")
        self.mx2_rider_check = QCheckBox("Rider")
        self.mx2_challenge_check = QCheckBox("Challenge")
        self.mx2_veteran_check = QCheckBox("Veteran")
        self.mx2_superveteran_check = QCheckBox("Superveteran")
        self.mx2_master_check = QCheckBox("Master")
        
        mx2_layout = QVBoxLayout()
        mx2_layout.addWidget(self.mx2_elite_check)
        mx2_layout.addWidget(self.mx2_fast_check)
        mx2_layout.addWidget(self.mx2_expert_check)
        mx2_layout.addWidget(self.mx2_rider_check)
        mx2_layout.addWidget(self.mx2_challenge_check)
        mx2_layout.addWidget(self.mx2_veteran_check)
        mx2_layout.addWidget(self.mx2_superveteran_check)
        mx2_layout.addWidget(self.mx2_master_check)
        
        mx2_widget = QWidget()
        mx2_widget.setLayout(mx2_layout)
        categorie_layout.addWidget(mx2_widget, 1, 1)
        
        # 125
        categorie_layout.addWidget(QLabel("<b>125</b>"), 0, 2)
        self.cat125_senior_check = QCheckBox("Senior")
        self.cat125_junior_check = QCheckBox("Junior")
        
        cat125_layout = QVBoxLayout()
        cat125_layout.addWidget(self.cat125_senior_check)
        cat125_layout.addWidget(self.cat125_junior_check)
        
        cat125_widget = QWidget()
        cat125_widget.setLayout(cat125_layout)
        categorie_layout.addWidget(cat125_widget, 1, 2)
        
        # Altre categorie
        categorie_layout.addWidget(QLabel("<b>Altre</b>"), 0, 3)
        self.femminile_check = QCheckBox("Femminile")
        self.minicross_debuttanti_check = QCheckBox("Minicross Debuttanti")
        self.minicross_cadetti_check = QCheckBox("Minicross Cadetti")
        self.minicross_junior_check = QCheckBox("Minicross Junior")
        self.minicross_senior_check = QCheckBox("Minicross Senior")
        self.training_check = QCheckBox("Training")
        
        altre_layout = QVBoxLayout()
        altre_layout.addWidget(self.femminile_check)
        altre_layout.addWidget(self.minicross_debuttanti_check)
        altre_layout.addWidget(self.minicross_cadetti_check)
        altre_layout.addWidget(self.minicross_junior_check)
        altre_layout.addWidget(self.minicross_senior_check)
        altre_layout.addWidget(self.training_check)
        
        altre_widget = QWidget()
        altre_widget.setLayout(altre_layout)
        categorie_layout.addWidget(altre_widget, 1, 3)
        
        # Aggiungiamo il layout delle categorie al layout principale
        categorie_container = QWidget()
        categorie_container.setLayout(categorie_layout)
        layout.addRow(categorie_container)
        
        # INFORMAZIONI DURATA GARE (dal regolamento FMI)
        layout.addRow(QLabel(""))
        layout.addRow(QLabel("<b>DURATA GARE (minuti+2 giri)</b>"))
        
        durata_layout = QGridLayout()
        
        durata_layout.addWidget(QLabel("MX1/MX2 Elite/Fast/Expert (Gruppo A):"), 0, 0)
        self.durata_gruppo_a_elite_spin = QSpinBox()
        self.durata_gruppo_a_elite_spin.setRange(10, 30)
        self.durata_gruppo_a_elite_spin.setValue(17)  # Come da regolamento
        self.durata_gruppo_a_elite_spin.setSuffix(" min + 2 giri")
        durata_layout.addWidget(self.durata_gruppo_a_elite_spin, 0, 1)
        
        durata_layout.addWidget(QLabel("MX1/MX2 Rider (Gruppo A):"), 1, 0)
        self.durata_gruppo_a_rider_spin = QSpinBox()
        self.durata_gruppo_a_rider_spin.setRange(10, 30)
        self.durata_gruppo_a_rider_spin.setValue(15)  # Come da regolamento
        self.durata_gruppo_a_rider_spin.setSuffix(" min + 2 giri")
        durata_layout.addWidget(self.durata_gruppo_a_rider_spin, 1, 1)
        
        durata_layout.addWidget(QLabel("Gruppo B:"), 2, 0)
        self.durata_gruppo_b_spin = QSpinBox()
        self.durata_gruppo_b_spin.setRange(10, 30)
        self.durata_gruppo_b_spin.setValue(13)  # Come da regolamento
        self.durata_gruppo_b_spin.setSuffix(" min + 2 giri")
        durata_layout.addWidget(self.durata_gruppo_b_spin, 2, 1)
        
        durata_layout.addWidget(QLabel("Gruppo C:"), 3, 0)
        self.durata_gruppo_c_spin = QSpinBox()
        self.durata_gruppo_c_spin.setRange(10, 30)
        self.durata_gruppo_c_spin.setValue(11)  # Come da regolamento
        self.durata_gruppo_c_spin.setSuffix(" min + 2 giri")
        durata_layout.addWidget(self.durata_gruppo_c_spin, 3, 1)
        
        durata_layout.addWidget(QLabel("125 Junior:"), 4, 0)
        self.durata_125_junior_spin = QSpinBox()
        self.durata_125_junior_spin.setRange(10, 30)
        self.durata_125_junior_spin.setValue(17)  # Come da regolamento
        self.durata_125_junior_spin.setSuffix(" min + 2 giri")
        durata_layout.addWidget(self.durata_125_junior_spin, 4, 1)
        
        durata_layout.addWidget(QLabel("Minicross Debuttanti:"), 5, 0)
        self.durata_minicross_debuttanti_spin = QSpinBox()
        self.durata_minicross_debuttanti_spin.setRange(5, 20)
        self.durata_minicross_debuttanti_spin.setValue(8)  # Come da regolamento
        self.durata_minicross_debuttanti_spin.setSuffix(" min + 2 giri")
        durata_layout.addWidget(self.durata_minicross_debuttanti_spin, 5, 1)
        
        durata_layout.addWidget(QLabel("Minicross Cadetti:"), 6, 0)
        self.durata_minicross_cadetti_spin = QSpinBox()
        self.durata_minicross_cadetti_spin.setRange(5, 20)
        self.durata_minicross_cadetti_spin.setValue(10)  # Come da regolamento
        self.durata_minicross_cadetti_spin.setSuffix(" min + 2 giri")
        durata_layout.addWidget(self.durata_minicross_cadetti_spin, 6, 1)
        
        durata_container = QWidget()
        durata_container.setLayout(durata_layout)
        layout.addRow(durata_container)
        
        # NOTE AGGIUNTIVE
        layout.addRow(QLabel(""))
        layout.addRow(QLabel("<b>NOTE AGGIUNTIVE</b>"))
        
        self.note_edit = QTextEdit()
        self.note_edit.setMaximumHeight(100)
        layout.addRow("Note:", self.note_edit)
        
        # Imposta l'area di scorrimento
        scroll_area.setWidget(container)
        
        # Layout principale
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll_area)
        
        # Pulsanti
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Salva")
        self.cancel_button = QPushButton("Annulla")
        
        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(button_layout)
        
        # Se stiamo modificando un evento esistente, carichiamo i suoi dati
        if evento_id is not None:
            self.load_evento_data()