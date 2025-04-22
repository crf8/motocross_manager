# database/models.py
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, Float, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .connection import Base

class Pilota(Base):
    __tablename__ = "piloti"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    cognome = Column(String, nullable=False)
    data_nascita = Column(Date, nullable=False)
    email = Column(String, unique=True, index=True)
    telefono = Column(String)
    moto_club = Column(String)
    licenza_tipo = Column(String)  # Elite, Fuoristrada, ecc.
    numero_licenza = Column(String, unique=True)
    regione = Column(String)
    
    # Campi aggiuntivi (opzionali)
    anno_prima_licenza = Column(Integer)
    marca_moto = Column(String)
    cilindrata = Column(Integer)
    tipo_motore = Column(String)  # 2T o 4T
    categoria_ranking = Column(String)
    numero_gara = Column(String)
    transponder_personale = Column(String)
    ranking_nazionale = Column(Integer)
    anni_esperienza = Column(Integer)
    note = Column(Text)
    
    # Relazioni
    iscrizioni = relationship("Iscrizione", back_populates="pilota")
    
    def __repr__(self):
        return f"{self.nome} {self.cognome}"

class Categoria(Base):
    __tablename__ = "categorie"

    id = Column(Integer, primary_key=True, index=True)
    classe = Column(String, nullable=False)  # MX1, MX2, 125, ecc.
    categoria = Column(String, nullable=False)  # Elite, Fast, Expert, ecc.
    licenza_richiesta = Column(String)  # Elite, Fuoristrada, ecc.
    eta_min = Column(Integer)
    eta_max = Column(Integer)
    cilindrata_min_2t = Column(Integer)
    cilindrata_max_2t = Column(Integer)
    cilindrata_min_4t = Column(Integer)
    cilindrata_max_4t = Column(Integer)
    
    # Relazioni
    iscrizioni = relationship("Iscrizione", back_populates="categoria")
    
    def __repr__(self):
        return f"{self.classe} {self.categoria}"

class Evento(Base):
    __tablename__ = "eventi"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    data = Column(Date, nullable=False)
    circuito = Column(String, nullable=False)
    moto_club_organizzatore = Column(String)
    tipo = Column(String)  # Campionato, Trofeo, ecc.
    
    # Campi aggiuntivi (opzionali)
    regione = Column(String)
    indirizzo = Column(String)
    lunghezza_pista = Column(Integer)  # in metri
    contatto_organizzatore = Column(String)
    email_organizzatore = Column(String)
    telefono_organizzatore = Column(String)
    
    # Tasse federali
    tic = Column(Float, default=45.0)  # Tassa Iscrizione a Calendario
    tag = Column(Float, default=40.0)  # Tassa Approvazione Gara
    cpa = Column(Float, default=60.0)  # Cassa Fondo Prestazioni Assistenziali
    diritto_segreteria = Column(Float, default=60.0)
    diritto_urgenza = Column(Float, default=0.0)
    
    # Servizi tecnici
    servizio_tecnico = Column(Float, default=350.0)
    servizio_tecnico_supplementare = Column(Float, default=300.0)
    servizio_fonometrico = Column(Float, default=270.0)
    
    # Staff tecnico
    direttore_gara = Column(String)
    commissario_percorso = Column(String)
    medico_gara = Column(String)
    cronometraggio = Column(String)
    
    # Quote e pagamenti
    quota_iscrizione = Column(Float, default=60.0)
    quota_campionato = Column(Float, default=360.0)
    penale_iscrizione_tardiva = Column(Float, default=30.0)
    scadenza_iscrizioni = Column(Date)
    
    # Programma gara
    data_operazioni_preliminari = Column(Date)
    ora_inizio_verifiche = Column(String)
    ora_fine_verifiche = Column(String)
    ora_briefing = Column(String)
    ora_inizio_prove = Column(String)
    ora_inizio_gare = Column(String)
    
    # Note
    note = Column(Text)
    
    # Relazioni
    iscrizioni = relationship("Iscrizione", back_populates="evento")
    gruppi = relationship("Gruppo", back_populates="evento")
    
    def __repr__(self):
        return f"{self.nome} ({self.data})"

class Iscrizione(Base):
    __tablename__ = "iscrizioni"

    id = Column(Integer, primary_key=True, index=True)
    pilota_id = Column(Integer, ForeignKey("piloti.id"), nullable=False)
    evento_id = Column(Integer, ForeignKey("eventi.id"), nullable=False)
    categoria_id = Column(Integer, ForeignKey("categorie.id"), nullable=False)
    numero_gara = Column(Integer)
    transponder_id = Column(String)
    timestamp_iscrizione = Column(DateTime, default=func.now())
    pagamento_effettuato = Column(Boolean, default=False)
    
    # Campi opzionali
    note = Column(Text)
    
    # Relazioni
    pilota = relationship("Pilota", back_populates="iscrizioni")
    evento = relationship("Evento", back_populates="iscrizioni")
    categoria = relationship("Categoria", back_populates="iscrizioni")
    partecipazioni_gruppi = relationship("PartecipazioneGruppo", back_populates="iscrizione")
    lap_times = relationship("LapTime", back_populates="iscrizione")
    penalita = relationship("Penalita", back_populates="iscrizione")
    
    def __repr__(self):
        return f"Iscrizione di {self.pilota} a {self.evento} in {self.categoria}"

class LapTime(Base):
    __tablename__ = "lap_times"

    id = Column(Integer, primary_key=True, index=True)
    iscrizione_id = Column(Integer, ForeignKey("iscrizioni.id"), nullable=False)
    sessione_tipo = Column(String, nullable=False)  # "Prove Libere", "Qualifiche", "Gara1", "Gara2"
    numero_giro = Column(Integer, nullable=False)
    tempo_ms = Column(Integer, nullable=False)  # Tempo in millisecondi
    timestamp = Column(DateTime, default=func.now())
    
    # Relazioni
    iscrizione = relationship("Iscrizione", back_populates="lap_times")
    
    def __repr__(self):
        return f"Giro {self.numero_giro} - {self.formato_tempo()}"
    
    def formato_tempo(self):
        """Formatta il tempo in millisecondi come MM:SS.mmm"""
        secs = self.tempo_ms // 1000
        mins = secs // 60
        secs %= 60
        msecs = self.tempo_ms % 1000
        return f"{mins:02d}:{secs:02d}.{msecs:03d}"

class Gruppo(Base):
    __tablename__ = "gruppi"

    id = Column(Integer, primary_key=True, index=True)
    evento_id = Column(Integer, ForeignKey("eventi.id"), nullable=False)
    nome = Column(String, nullable=False)  # "Gruppo A", "Gruppo B", ecc.
    categoria_id = Column(Integer, ForeignKey("categorie.id"))
    tipo_sessione = Column(String, nullable=False)  # "Prove Libere", "Qualifiche", "Gara 1", "Gara 2", "Supercampione"
    limite_piloti = Column(Integer, default=40)  # Numero massimo di piloti nel gruppo
    
    # Relazioni
    evento = relationship("Evento", back_populates="gruppi")
    categoria = relationship("Categoria")
    partecipazioni = relationship("PartecipazioneGruppo", back_populates="gruppo")
    
    def __repr__(self):
        return f"{self.nome} - {self.tipo_sessione}"

class PartecipazioneGruppo(Base):
    __tablename__ = "partecipazioni_gruppi"

    id = Column(Integer, primary_key=True, index=True)
    gruppo_id = Column(Integer, ForeignKey("gruppi.id"), nullable=False)
    iscrizione_id = Column(Integer, ForeignKey("iscrizioni.id"), nullable=False)
    posizione_griglia = Column(Integer)  # Posizione di partenza in griglia
    
    # Relazioni
    gruppo = relationship("Gruppo", back_populates="partecipazioni")
    iscrizione = relationship("Iscrizione", back_populates="partecipazioni_gruppi")
    
    def __repr__(self):
        return f"Partecipazione: {self.iscrizione.pilota.nome} {self.iscrizione.pilota.cognome} in {self.gruppo.nome}"

class Risultato(Base):
    __tablename__ = "risultati"
    
    id = Column(Integer, primary_key=True, index=True)
    iscrizione_id = Column(Integer, ForeignKey("iscrizioni.id"), nullable=False)
    gruppo_id = Column(Integer, ForeignKey("gruppi.id"), nullable=False)
    sessione_tipo = Column(String, nullable=False)  # "Qualifiche", "Gara1", "Gara2"
    posizione = Column(Integer)
    punti = Column(Integer)
    best_lap_time = Column(Integer)  # Miglior tempo in millisecondi
    
    # Relazioni
    iscrizione = relationship("Iscrizione")
    gruppo = relationship("Gruppo")
    
    def __repr__(self):
        return f"Risultato: {self.iscrizione.pilota.cognome} - Pos {self.posizione} - {self.sessione_tipo}"
    
    # database/models.py
# Aggiungi alla fine del file

class Penalita(Base):
    __tablename__ = "penalita"
    
    id = Column(Integer, primary_key=True, index=True)
    iscrizione_id = Column(Integer, ForeignKey("iscrizioni.id"), nullable=False)
    sessione_tipo = Column(String, nullable=False)  # "Prove Libere", "Qualifiche", "Gara 1", "Gara 2", ecc.
    gruppo_id = Column(Integer, ForeignKey("gruppi.id"))
    
    tipo_infrazione = Column(String, nullable=False)  # Es. "Bandiera gialla", "Taglio percorso", ecc.
    descrizione = Column(Text)
    
    # Tipo di penalità
    posizioni_penalita = Column(Integer, default=0)  # Numero di posizioni di penalità
    tempo_penalita = Column(Integer, default=0)  # Penalità in secondi
    esclusione = Column(Boolean, default=False)  # Se True, il pilota è escluso dalla sessione
    
    # Cancellazione miglior tempo (per le qualifiche)
    cancella_miglior_tempo = Column(Boolean, default=False)
    
    data_ora = Column(DateTime, default=func.now())
    
    # Relazioni
    iscrizione = relationship("Iscrizione", back_populates="penalita")
    gruppo = relationship("Gruppo")
    
    def __repr__(self):
        return f"Penalità: {self.tipo_infrazione} per {self.iscrizione.pilota.cognome}"