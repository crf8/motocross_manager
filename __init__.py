# database/__init__.py
from .connection import engine, Base, SessionLocal
from . import models

def init_db():
    """Inizializza il database creando tutte le tabelle definite"""
    Base.metadata.create_all(bind=engine)
    
    # Dopo aver creato le tabelle, inizializza le categorie
    init_categories()

def init_categories():
    """Inizializza le categorie nel database se non esistono già"""
    db = SessionLocal()
    
    # Verifica se ci sono già categorie nel database
    existing_categories = db.query(models.Categoria).count()
    if existing_categories > 0:
        db.close()
        return
    
    # Lista di categorie da creare
    categories = [
        # MX1
        {"classe": "MX1", "categoria": "Elite", "licenza_richiesta": "Elite", 
         "eta_min": 16, "eta_max": None, "cilindrata_min_2t": 251, "cilindrata_max_2t": 500, 
         "cilindrata_min_4t": 290, "cilindrata_max_4t": 650},
        {"classe": "MX1", "categoria": "Fast", "licenza_richiesta": "Fuoristrada", 
         "eta_min": 16, "eta_max": None, "cilindrata_min_2t": 251, "cilindrata_max_2t": 500, 
         "cilindrata_min_4t": 290, "cilindrata_max_4t": 650},
        {"classe": "MX1", "categoria": "Expert", "licenza_richiesta": "Fuoristrada", 
         "eta_min": 16, "eta_max": None, "cilindrata_min_2t": 251, "cilindrata_max_2t": 500, 
         "cilindrata_min_4t": 290, "cilindrata_max_4t": 650},
        {"classe": "MX1", "categoria": "Rider", "licenza_richiesta": "Fuoristrada", 
         "eta_min": 16, "eta_max": None, "cilindrata_min_2t": 251, "cilindrata_max_2t": 500, 
         "cilindrata_min_4t": 290, "cilindrata_max_4t": 650},
        
        # MX2
        {"classe": "MX2", "categoria": "Elite", "licenza_richiesta": "Elite", 
         "eta_min": 14, "eta_max": None, "cilindrata_min_2t": 100, "cilindrata_max_2t": 250, 
         "cilindrata_min_4t": 175, "cilindrata_max_4t": 250},
        {"classe": "MX2", "categoria": "Fast", "licenza_richiesta": "Fuoristrada", 
         "eta_min": 14, "eta_max": None, "cilindrata_min_2t": 100, "cilindrata_max_2t": 250, 
         "cilindrata_min_4t": 175, "cilindrata_max_4t": 250},
        {"classe": "MX2", "categoria": "Expert", "licenza_richiesta": "Fuoristrada", 
         "eta_min": 14, "eta_max": None, "cilindrata_min_2t": 100, "cilindrata_max_2t": 250, 
         "cilindrata_min_4t": 175, "cilindrata_max_4t": 250},
        {"classe": "MX2", "categoria": "Rider", "licenza_richiesta": "Fuoristrada", 
         "eta_min": 14, "eta_max": None, "cilindrata_min_2t": 100, "cilindrata_max_2t": 250, 
         "cilindrata_min_4t": 175, "cilindrata_max_4t": 250},
        
        # 125
        {"classe": "125", "categoria": "Junior", "licenza_richiesta": "MiniOffroad", 
         "eta_min": 13, "eta_max": 17, "cilindrata_min_2t": 100, "cilindrata_max_2t": 125, 
         "cilindrata_min_4t": 100, "cilindrata_max_4t": 125},
        {"classe": "125", "categoria": "Senior", "licenza_richiesta": "Fuoristrada", 
         "eta_min": 16, "eta_max": None, "cilindrata_min_2t": 100, "cilindrata_max_2t": 125, 
         "cilindrata_min_4t": 100, "cilindrata_max_4t": 125},
        
        # Veteran
        {"classe": "MX1", "categoria": "Veteran", "licenza_richiesta": "Fuoristrada", 
         "eta_min": 40, "eta_max": None, "cilindrata_min_2t": 251, "cilindrata_max_2t": 500, 
         "cilindrata_min_4t": 290, "cilindrata_max_4t": 650},
        {"classe": "MX2", "categoria": "Veteran", "licenza_richiesta": "Fuoristrada", 
         "eta_min": 40, "eta_max": None, "cilindrata_min_2t": 100, "cilindrata_max_2t": 250, 
         "cilindrata_min_4t": 175, "cilindrata_max_4t": 250},
    ]
    
    # Aggiungi le categorie al database
    for cat_data in categories:
        categoria = models.Categoria(**cat_data)
        db.add(categoria)
    
    # Commit delle modifiche
    db.commit()
    db.close()