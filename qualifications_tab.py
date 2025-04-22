# ui/qualifications_tab.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLabel, QComboBox, QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QMessageBox, QSplitter
)
from PyQt6.QtCore import Qt

from database.connection import SessionLocal
from database.models import Evento, Iscrizione, Pilota, Categoria, Gruppo, PartecipazioneGruppo, LapTime
from ui.timing_system import TimingSystem  # Riutilizziamo il sistema di cronometraggio

class QualificationsTab(QWidget):
    """Scheda per gestire le qualifiche"""
    
    def __init__(self):
        super().__init__()
        
        # Layout principale
        layout = QVBoxLayout(self)
        
        # Titolo
        title_label = QLabel("Gestione Qualifiche")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Selettori per evento e gruppo
        selectors_layout = QFormLayout()
        
        self.event_combo = QComboBox()
        selectors_layout.addRow("Evento:", self.event_combo)
        
        self.group_combo = QComboBox()
        selectors_layout.addRow("Gruppo:", self.group_combo)
        
        layout.addLayout(selectors_layout)
        
        # Bottone per caricare le qualifiche
        load_button = QPushButton("Carica Qualifiche")
        load_button.clicked.connect(self.load_qualifications)
        layout.addWidget(load_button)
        
        # Cronometraggio
        self.timing_system = TimingSystem()
        layout.addWidget(self.timing_system)
        
        # Bottone per generare i gruppi di gara basati sui tempi
        create_race_groups_button = QPushButton("Crea Gruppi di Gara dalle Qualifiche")
        create_race_groups_button.clicked.connect(self.create_race_groups)
        layout.addWidget(create_race_groups_button)
        
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
            
            # Colleghiamo la selezione dell'evento al caricamento dei gruppi
            self.event_combo.currentIndexChanged.connect(self.load_groups)
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante il caricamento eventi: {str(e)}")
        finally:
            db.close()
    
    def load_groups(self):
        """Carica i gruppi per l'evento selezionato"""
        evento_id = self.event_combo.currentData()
        
        if not evento_id:
            return
        
        try:
            db = SessionLocal()
            
            # Ottieni tutti i gruppi per questo evento
            gruppi = db.query(Gruppo).filter(
                Gruppo.evento_id == evento_id,
                Gruppo.tipo_sessione == "Prove Libere"  # Usiamo gli stessi gruppi delle prove libere
            ).all()
            
            self.group_combo.clear()
            for gruppo in gruppi:
                self.group_combo.addItem(gruppo.nome, gruppo.id)
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante il caricamento gruppi: {str(e)}")
        finally:
            db.close()
    
    def load_qualifications(self):
        """Configura il sistema di cronometraggio per le qualifiche"""
        gruppo_id = self.group_combo.currentData()
        
        if not gruppo_id:
            QMessageBox.warning(self, "Attenzione", "Seleziona un gruppo!")
            return
        
        # Passiamo l'evento e il gruppo selezionati al sistema di cronometraggio
        self.timing_system.event_combo.setCurrentIndex(self.event_combo.currentIndex())
        
        # Troviamo l'indice del gruppo nel combo box del sistema di cronometraggio
        for i in range(self.timing_system.group_combo.count()):
            if self.timing_system.group_combo.itemData(i) == gruppo_id:
                self.timing_system.group_combo.setCurrentIndex(i)
                break
        
        # Impostiamo il tipo di sessione su "Qualifiche"
        for i in range(self.timing_system.session_type_combo.count()):
            if self.timing_system.session_type_combo.itemText(i) == "Qualifiche":
                self.timing_system.session_type_combo.setCurrentIndex(i)
                break
        
        # Carichiamo i piloti del gruppo nel sistema di cronometraggio
        self.timing_system.load_group_riders()
    
    def create_race_groups(self):
        """Crea i gruppi di gara basati sui tempi delle qualifiche"""
        evento_id = self.event_combo.currentData()
        
        if not evento_id:
            QMessageBox.warning(self, "Attenzione", "Seleziona un evento!")
            return
        
        try:
            db = SessionLocal()
            
            # Ottieni tutti i tempi delle qualifiche per questo evento e ordina per tempo migliore
            query = """
            SELECT i.id, i.pilota_id, i.categoria_id, i.numero_gara, MIN(lt.tempo_ms) as best_time
            FROM iscrizioni i
            JOIN lap_times lt ON lt.iscrizione_id = i.id
            WHERE i.evento_id = :evento_id AND lt.sessione_tipo = 'Qualifiche'
            GROUP BY i.id
            ORDER BY best_time
            """
            
            results = db.execute(query, {"evento_id": evento_id}).fetchall()
            
            if not results:
                QMessageBox.warning(self, "Attenzione", "Non ci sono tempi di qualifica registrati per questo evento!")
                return
            
            # Raggruppiamo i piloti in base alle categorie
            piloti_per_categoria = {}
            
            for row in results:
                iscrizione_id, pilota_id, categoria_id, numero_gara, best_time = row
                
                # Ottieni la categoria
                categoria = db.query(Categoria).get(categoria_id)
                categoria_key = f"{categoria.classe} {categoria.categoria}"
                
                if categoria_key not in piloti_per_categoria:
                    piloti_per_categoria[categoria_key] = []
                
                piloti_per_categoria[categoria_key].append({
                    "iscrizione_id": iscrizione_id,
                    "pilota_id": pilota_id,
                    "categoria_id": categoria_id,
                    "numero_gara": numero_gara,
                    "best_time": best_time
                })
            
            # Creiamo i gruppi di gara basati sulla qualifica
            gruppi_creati = []
            
            # Regole di divisione in gruppi secondo il regolamento FMI
            # Esempio: i primi 40 piloti di MX1/MX2 vanno nel Gruppo A, i successivi nel B, ecc.
            
            # MX1/MX2 Elite/Fast/Expert - Gruppo A
            mx_top_a = []
            for categoria, piloti in piloti_per_categoria.items():
                if ("MX1" in categoria or "MX2" in categoria) and ("Elite" in categoria or "Fast" in categoria or "Expert" in categoria):
                    mx_top_a.extend(piloti[:40])  # Massimo 40 piloti nel gruppo A
            
            if mx_top_a:
                gruppi_creati.append({
                    "nome": "Gruppo A - Elite/Fast/Expert",
                    "piloti": mx_top_a,
                    "tipo_sessione": "Gara 1"
                })
            
            # MX1/MX2 Elite/Fast/Expert in eccesso - Gruppo B
            mx_top_b = []
            for categoria, piloti in piloti_per_categoria.items():
                if ("MX1" in categoria or "MX2" in categoria) and ("Elite" in categoria or "Fast" in categoria or "Expert" in categoria):
                    mx_top_b.extend(piloti[40:])  # Piloti oltre i primi 40
            
            if mx_top_b:
                gruppi_creati.append({
                    "nome": "Gruppo B - Elite/Fast/Expert",
                    "piloti": mx_top_b,
                    "tipo_sessione": "Gara 1"
                })
            
            # ... (simile per le altre categorie)
            
            # Salviamo i gruppi nel database
            for gruppo_info in gruppi_creati:
                # Verifichiamo se il gruppo esiste già
                gruppo_esistente = db.query(Gruppo).filter(
                    Gruppo.evento_id == evento_id,
                    Gruppo.nome == gruppo_info["nome"],
                    Gruppo.tipo_sessione == gruppo_info["tipo_sessione"]
                ).first()
                
                if gruppo_esistente:
                    # Eliminiamo le vecchie partecipazioni
                    db.query(PartecipazioneGruppo).filter(
                        PartecipazioneGruppo.gruppo_id == gruppo_esistente.id
                    ).delete()
                    
                    gruppo = gruppo_esistente
                else:
                    # Creiamo un nuovo gruppo
                    gruppo = Gruppo(
                        evento_id=evento_id,
                        nome=gruppo_info["nome"],
                        tipo_sessione=gruppo_info["tipo_sessione"]
                    )
                    db.add(gruppo)
                    db.flush()
                
                # Aggiungiamo i piloti al gruppo
                for posizione, pilota in enumerate(gruppo_info["piloti"], 1):
                    partecipazione = PartecipazioneGruppo(
                        gruppo_id=gruppo.id,
                        iscrizione_id=pilota["iscrizione_id"],
                        posizione_griglia=posizione  # La posizione in griglia è basata sul tempo di qualifica
                    )
                    db.add(partecipazione)
            
            db.commit()
            
            QMessageBox.information(self, "Gruppi Creati", 
                                  f"Creati {len(gruppi_creati)} gruppi di gara basati sui tempi di qualifica!")
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante la creazione dei gruppi: {str(e)}")
        finally:
            db.close()