# ui/settings_dialog.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, 
                           QLabel, QLineEdit, QComboBox, QSpinBox, 
                           QCheckBox, QPushButton, QFileDialog, QGroupBox, 
                           QFormLayout, QDialogButtonBox, QColorDialog, QMessageBox)
from PyQt6.QtCore import Qt
import os
import json

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Imposta il titolo della finestra
        self.setWindowTitle("Impostazioni")
        
        # Imposta le dimensioni
        self.resize(600, 400)
        
        # Carica le impostazioni attuali
        self.settings = self.load_settings()
        
        # Crea il layout principale
        main_layout = QVBoxLayout(self)
        
        # Crea il widget a schede per le diverse categorie di impostazioni
        self.tabs = QTabWidget()
        
        # Crea le varie schede di impostazioni
        self.create_general_tab()
        self.create_race_tab()
        self.create_report_tab()
        self.create_user_tab()
        
        # Aggiungi il widget a schede al layout principale
        main_layout.addWidget(self.tabs)
        
        # Crea i pulsanti di conferma/annulla
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | 
                                      QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.save_settings)
        button_box.rejected.connect(self.reject)
        
        # Aggiungi i pulsanti al layout
        main_layout.addWidget(button_box)
    
    def create_general_tab(self):
        """Crea la scheda delle impostazioni generali"""
        tab = QWidget()
        layout = QFormLayout(tab)
        
        # Percorso database
        self.db_path_edit = QLineEdit(self.settings.get('db_path', 'motocross.db'))
        browse_btn = QPushButton("Sfoglia...")
        browse_btn.clicked.connect(self.browse_db_path)
        
        db_layout = QHBoxLayout()
        db_layout.addWidget(self.db_path_edit)
        db_layout.addWidget(browse_btn)
        
        layout.addRow("Percorso database:", db_layout)
        
        # Backup automatico
        self.backup_combo = QComboBox()
        self.backup_combo.addItems(["Mai", "Ogni ora", "Giornaliero", "Settimanale"])
        self.backup_combo.setCurrentText(self.settings.get('auto_backup', 'Mai'))
        layout.addRow("Backup automatico:", self.backup_combo)
        
        # Lingua
        self.language_combo = QComboBox()
        self.language_combo.addItems(["Italiano", "English", "Français", "Español"])
        self.language_combo.setCurrentText(self.settings.get('language', 'Italiano'))
        layout.addRow("Lingua:", self.language_combo)
        
        # Aggiungi la scheda al widget principale
        self.tabs.addTab(tab, "Generale")
    
    def create_race_tab(self):
        """Crea la scheda delle impostazioni gare"""
        tab = QWidget()
        layout = QFormLayout(tab)
        
        # Sistema punteggio
        self.point_system_combo = QComboBox()
        self.point_system_combo.addItems(["FMI Standard", "Personalizzato"])
        self.point_system_combo.setCurrentText(self.settings.get('point_system', 'FMI Standard'))
        layout.addRow("Sistema punteggio:", self.point_system_combo)
        
        # Numero massimo piloti
        self.max_pilots_spin = QSpinBox()
        self.max_pilots_spin.setRange(10, 100)
        self.max_pilots_spin.setValue(self.settings.get('max_pilots', 40))
        layout.addRow("Max piloti per gruppo:", self.max_pilots_spin)
        
        # Durata predefinita prove libere
        self.practice_time_spin = QSpinBox()
        self.practice_time_spin.setRange(5, 60)
        self.practice_time_spin.setValue(self.settings.get('practice_time', 20))
        self.practice_time_spin.setSuffix(" min")
        layout.addRow("Durata prove libere:", self.practice_time_spin)
        
        # Durata predefinita qualifiche
        self.quali_time_spin = QSpinBox()
        self.quali_time_spin.setRange(5, 60)
        self.quali_time_spin.setValue(self.settings.get('quali_time', 20))
        self.quali_time_spin.setSuffix(" min")
        layout.addRow("Durata qualifiche:", self.quali_time_spin)
        
        # Durata predefinita gare
        self.race_time_spin = QSpinBox()
        self.race_time_spin.setRange(10, 120)
        self.race_time_spin.setValue(self.settings.get('race_time', 30))
        self.race_time_spin.setSuffix(" min")
        layout.addRow("Durata gare:", self.race_time_spin)
        
        # Aggiungi la scheda al widget principale
        self.tabs.addTab(tab, "Gare")
    
    def create_report_tab(self):
        """Crea la scheda delle impostazioni report"""
        tab = QWidget()
        layout = QFormLayout(tab)
        
        # Logo personalizzato
        self.logo_path_edit = QLineEdit(self.settings.get('logo_path', ''))
        browse_logo_btn = QPushButton("Sfoglia...")
        browse_logo_btn.clicked.connect(self.browse_logo_path)
        
        logo_layout = QHBoxLayout()
        logo_layout.addWidget(self.logo_path_edit)
        logo_layout.addWidget(browse_logo_btn)
        
        layout.addRow("Logo personalizzato:", logo_layout)
        
        # Informazioni organizzatore
        self.org_name_edit = QLineEdit(self.settings.get('org_name', ''))
        layout.addRow("Nome organizzatore:", self.org_name_edit)
        
        self.org_address_edit = QLineEdit(self.settings.get('org_address', ''))
        layout.addRow("Indirizzo:", self.org_address_edit)
        
        self.org_contact_edit = QLineEdit(self.settings.get('org_contact', ''))
        layout.addRow("Contatti:", self.org_contact_edit)
        
        # Formato esportazione
        self.export_format_combo = QComboBox()
        self.export_format_combo.addItems(["PDF", "Excel", "HTML", "CSV"])
        self.export_format_combo.setCurrentText(self.settings.get('export_format', 'PDF'))
        layout.addRow("Formato esportazione:", self.export_format_combo)
        
        # Percorso salvataggio report
        self.report_path_edit = QLineEdit(self.settings.get('report_path', 'reports'))
        browse_report_btn = QPushButton("Sfoglia...")
        browse_report_btn.clicked.connect(self.browse_report_path)
        
        report_layout = QHBoxLayout()
        report_layout.addWidget(self.report_path_edit)
        report_layout.addWidget(browse_report_btn)
        
        layout.addRow("Cartella report:", report_layout)
        
        # Aggiungi la scheda al widget principale
        self.tabs.addTab(tab, "Report")
    
    def create_user_tab(self):
        """Crea la scheda delle impostazioni utente"""
        tab = QWidget()
        layout = QFormLayout(tab)
        
        # Tema colori
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Chiaro", "Scuro", "Sistema"])
        self.theme_combo.setCurrentText(self.settings.get('theme', 'Sistema'))
        layout.addRow("Tema:", self.theme_combo)
        
        # Dimensione caratteri
        self.font_size_combo = QComboBox()
        self.font_size_combo.addItems(["Piccolo", "Medio", "Grande"])
        self.font_size_combo.setCurrentText(self.settings.get('font_size', 'Medio'))
        layout.addRow("Dimensione caratteri:", self.font_size_combo)
        
        # Suoni notifica
        self.sounds_check = QCheckBox()
        self.sounds_check.setChecked(self.settings.get('notification_sounds', True))
        layout.addRow("Suoni di notifica:", self.sounds_check)
        
        # Elementi per pagina
        self.items_per_page_spin = QSpinBox()
        self.items_per_page_spin.setRange(10, 100)
        self.items_per_page_spin.setValue(self.settings.get('items_per_page', 20))
        layout.addRow("Elementi per pagina:", self.items_per_page_spin)
        
        # Aggiungi la scheda al widget principale
        self.tabs.addTab(tab, "Utente")
    
    def browse_db_path(self):
        """Apre una finestra di dialogo per selezionare il percorso del database"""
        file_path, _ = QFileDialog.getSaveFileName(self, "Seleziona Database", 
                                               self.db_path_edit.text(), 
                                               "Database SQLite (*.db);;Tutti i file (*)")
        if file_path:
            self.db_path_edit.setText(file_path)
    
    def browse_logo_path(self):
        """Apre una finestra di dialogo per selezionare il logo"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleziona Logo", 
                                               self.logo_path_edit.text(), 
                                               "Immagini (*.png *.jpg *.jpeg);;Tutti i file (*)")
        if file_path:
            self.logo_path_edit.setText(file_path)
    
    def browse_report_path(self):
        """Apre una finestra di dialogo per selezionare la cartella dei report"""
        folder_path = QFileDialog.getExistingDirectory(self, "Seleziona Cartella Report", 
                                                  self.report_path_edit.text())
        if folder_path:
            self.report_path_edit.setText(folder_path)
    
    def load_settings(self):
        """Carica le impostazioni dal file"""
        settings_file = 'settings.json'
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_settings(self):
        """Salva le impostazioni nel file"""
        settings = {
            # Generale
            'db_path': self.db_path_edit.text(),
            'auto_backup': self.backup_combo.currentText(),
            'language': self.language_combo.currentText(),
            
            # Gare
            'point_system': self.point_system_combo.currentText(),
            'max_pilots': self.max_pilots_spin.value(),
            'practice_time': self.practice_time_spin.value(),
            'quali_time': self.quali_time_spin.value(),
            'race_time': self.race_time_spin.value(),
            
            # Report
            'logo_path': self.logo_path_edit.text(),
            'org_name': self.org_name_edit.text(),
            'org_address': self.org_address_edit.text(),
            'org_contact': self.org_contact_edit.text(),
            'export_format': self.export_format_combo.currentText(),
            'report_path': self.report_path_edit.text(),
            
            # Utente
            'theme': self.theme_combo.currentText(),
            'font_size': self.font_size_combo.currentText(),
            'notification_sounds': self.sounds_check.isChecked(),
            'items_per_page': self.items_per_page_spin.value()
        }
        
        try:
            with open('settings.json', 'w') as f:
                json.dump(settings, f, indent=4)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Impossibile salvare le impostazioni: {str(e)}")