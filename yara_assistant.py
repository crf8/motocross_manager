# ui/yara_assistant.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                           QTextEdit, QLineEdit, QListWidget, QSplitter, QFrame,
                           QTabWidget, QWidget, QScrollArea, QMessageBox)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPixmap, QFont

class YaraAssistant(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Configurazione della finestra
        self.setWindowTitle("Yara - Il tuo assistente virtuale")
        self.resize(700, 500)
        
        # Carica i database
        self.knowledge_base = self.load_knowledge_base()
        self.tutorial_database = self.load_tutorial_database()
        
        # Crea l'interfaccia utente
        self.setup_ui()
    
    def setup_ui(self):
        """Configura l'interfaccia utente dell'assistente"""
        # Layout principale
        main_layout = QVBoxLayout(self)
        
        # Intestazione
        header_layout = QHBoxLayout()
        
        # Titolo e descrizione
        title_layout = QVBoxLayout()
        title_label = QLabel("Yara")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        subtitle_label = QLabel("Il tuo assistente virtuale per la gestione gare motocross")
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        main_layout.addLayout(header_layout)
        
        # Contenuto principale (suddiviso in tabs)
        self.tabs = QTabWidget()
        self.setup_search_tab()
        self.setup_categories_tab()
        self.setup_tutorials_tab()
        self.setup_guide_tab()
        main_layout.addWidget(self.tabs)
        
        # Pulsanti inferiori
        buttons_layout = QHBoxLayout()
        self.close_button = QPushButton("Chiudi")
        self.close_button.clicked.connect(self.close)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.close_button)
        
        main_layout.addLayout(buttons_layout)
    
    def setup_search_tab(self):
        """Configura la scheda di ricerca"""
        search_tab = QWidget()
        layout = QVBoxLayout(search_tab)
        
        # Campo di ricerca
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cerca aiuto o fai una domanda...")
        self.search_input.returnPressed.connect(self.perform_search)
        search_layout.addWidget(self.search_input)
        
        self.search_button = QPushButton("Cerca")
        self.search_button.clicked.connect(self.perform_search)
        search_layout.addWidget(self.search_button)
        
        layout.addLayout(search_layout)
        
        # Area risultati
        self.results_area = QTextEdit()
        self.results_area.setReadOnly(True)
        self.results_area.setHtml("<p>Ciao, sono Yara! Fai una domanda o cerca un argomento per ricevere aiuto.</p>"
                                 "<p>Esempi:</p>"
                                 "<ul>"
                                 "<li>Come aggiungo un nuovo pilota?</li>"
                                 "<li>Come creo un nuovo evento?</li>"
                                 "<li>Come genero la classifica finale?</li>"
                                 "</ul>")
        layout.addWidget(self.results_area)
        
        self.tabs.addTab(search_tab, "Cerca")
    
    def setup_categories_tab(self):
        """Configura la scheda delle categorie"""
        categories_tab = QWidget()
        layout = QHBoxLayout(categories_tab)
        
        # Lista delle categorie
        self.categories_list = QListWidget()
        self.categories_list.addItems([
            "Guida introduttiva",
            "Gestione piloti",
            "Eventi e gare",
            "Iscrizioni",
            "Prove libere",
            "Qualifiche",
            "Gestione gruppi",
            "Classifiche e risultati",
            "Backup e sicurezza",
            "Impostazioni"
        ])
        self.categories_list.currentRowChanged.connect(self.show_category_content)
        
        # Contenuto della categoria
        self.category_content = QTextEdit()
        self.category_content.setReadOnly(True)
        
        # Splitter per ridimensionare le sezioni
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.categories_list)
        splitter.addWidget(self.category_content)
        splitter.setSizes([200, 500])
        
        layout.addWidget(splitter)
        
        self.tabs.addTab(categories_tab, "Categorie")
    
    def setup_tutorials_tab(self):
        """Configura la scheda dei tutorial passo-passo"""
        tutorials_tab = QWidget()
        layout = QVBoxLayout(tutorials_tab)
        
        # Titolo
        title_label = QLabel("Tutorial Passo-Passo")
        title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(title_label)
        
        # Descrizione
        description = QLabel("Seleziona un tutorial dalla lista per imparare come completare un'operazione dall'inizio alla fine.")
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Splitter per la lista e i contenuti
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Lista tutorial
        self.tutorials_list = QListWidget()
        self.populate_tutorials_list()
        self.tutorials_list.currentRowChanged.connect(self.show_tutorial_content)
        splitter.addWidget(self.tutorials_list)
        
        # Contenuto tutorial
        self.tutorial_content = QTextEdit()
        self.tutorial_content.setReadOnly(True)
        splitter.addWidget(self.tutorial_content)
        
        splitter.setSizes([200, 500])
        layout.addWidget(splitter)
        
        self.tabs.addTab(tutorials_tab, "Tutorial")
    
    def setup_guide_tab(self):
        """Configura la scheda guida rapida"""
        guide_tab = QWidget()
        layout = QVBoxLayout(guide_tab)
        
        # Titolo
        title = QLabel("Guida Rapida")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Contenuto della guida in uno scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        guide_content = QWidget()
        guide_layout = QVBoxLayout(guide_content)
        
        # Aggiunta di sezioni della guida
        self.add_guide_section(guide_layout, "Per iniziare", 
                              "MX Manager è un software completo per la gestione di gare di motocross. "
                              "Per iniziare, dovresti prima configurare i piloti e poi creare un evento.")
        
        self.add_guide_section(guide_layout, "Gestione Piloti", 
                              "Nella scheda 'Piloti' puoi aggiungere, modificare ed eliminare i dati dei piloti. "
                              "Ogni pilota deve avere un nome, cognome e categoria. "
                              "Puoi anche visualizzare le statistiche complete dei piloti.")
        
        self.add_guide_section(guide_layout, "Creazione Eventi", 
                              "Per creare un nuovo evento, vai alla scheda 'Eventi' e clicca su 'Aggiungi Evento'. "
                              "Inserisci i dettagli come nome, data e luogo dell'evento.")
        
        self.add_guide_section(guide_layout, "Iscrizioni", 
                              "Una volta creato l'evento, puoi gestire le iscrizioni nella scheda 'Iscrizioni'. "
                              "Qui puoi selezionare quali piloti parteciperanno all'evento.")
        
        self.add_guide_section(guide_layout, "Gestione della Gara", 
                              "Nelle schede 'Prove Libere', 'Qualifiche' e 'Gruppi di Gara' puoi gestire "
                              "tutti gli aspetti della competizione, dal cronometraggio alla formazione dei gruppi.")
        
        self.add_guide_section(guide_layout, "Classifiche", 
                              "Al termine della gara, puoi generare automaticamente le classifiche nella "
                              "scheda 'Classifiche e Statistiche'.")
        
        scroll_area.setWidget(guide_content)
        layout.addWidget(scroll_area)
        
        self.tabs.addTab(guide_tab, "Guida Rapida")
    
    def add_guide_section(self, layout, title, content):
        """Aggiunge una sezione alla guida rapida"""
        section_frame = QFrame()
        section_frame.setFrameShape(QFrame.Shape.StyledPanel)
        section_layout = QVBoxLayout(section_frame)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        section_layout.addWidget(title_label)
        
        content_label = QLabel(content)
        content_label.setWordWrap(True)
        section_layout.addWidget(content_label)
        
        layout.addWidget(section_frame)
        layout.addSpacing(10)
    
    def populate_tutorials_list(self):
        """Popola la lista dei tutorial disponibili"""
        tutorials = [
            "Configurazione Iniziale del Software",
            "Organizzazione Completa di un Evento",
            "Gestione delle Iscrizioni e Pagamenti",
            "Configurazione e Gestione Prove Libere",
            "Qualifiche e Formazione Gruppi",
            "Gestione di una Giornata di Gara",
            "Elaborazione Risultati e Classifiche",
            "Backup e Gestione Database"
        ]
        self.tutorials_list.addItems(tutorials)
    
    def perform_search(self):
        """Esegue la ricerca nel database delle conoscenze"""
        query = self.search_input.text().strip().lower()
        if not query:
            return
        
        results = self.search_knowledge_base(query)
        if results:
            self.display_search_results(results)
        else:
            self.results_area.setHtml("<p>Nessun risultato trovato per la tua ricerca.</p>"
                                    "<p>Prova a riformulare la domanda o consulta le categorie "
                                    "nella scheda 'Categorie' per trovare l'aiuto di cui hai bisogno.</p>")
    
    def search_knowledge_base(self, query):
        """Cerca nella base di conoscenza le risposte alla query"""
        # Esempio semplificato, in una versione reale useremmo un sistema più sofisticato
        results = []
        keywords = query.split()
        
        for article in self.knowledge_base:
            score = 0
            # Controllo se la query esatta è nel titolo o nel contenuto
            if query in article['title'].lower():
                score += 10
            if query in article['content'].lower():
                score += 5
            
            # Controllo le parole chiave
            for keyword in keywords:
                if keyword in article['title'].lower():
                    score += 3
                if keyword in article['content'].lower():
                    score += 1
                if keyword in article['keywords']:
                    score += 2
            
            if score > 0:
                results.append((article, score))
        
        # Ordina i risultati per punteggio e prendi i primi 5
        results.sort(key=lambda x: x[1], reverse=True)
        return [item[0] for item in results[:5]]
    
    def display_search_results(self, results):
        """Mostra i risultati della ricerca"""
        html = "<h3>Risultati della ricerca:</h3>"
        
        for result in results:
            html += f"<div style='margin-bottom: 15px; padding: 10px; background-color: #f5f5f5;'>"
            html += f"<h4>{result['title']}</h4>"
            html += f"<p>{result['content']}</p>"
            html += "</div>"
        
        self.results_area.setHtml(html)
    
    def show_category_content(self, row):
        """Mostra il contenuto della categoria selezionata"""
        if row < 0:
            return
        
        category = self.categories_list.item(row).text()
        
        # Cerca tutti gli articoli in questa categoria
        articles = [article for article in self.knowledge_base 
                   if category in article['categories']]
        
        if not articles:
            self.category_content.setHtml(f"<h3>{category}</h3><p>Nessun contenuto disponibile per questa categoria.</p>")
            return
        
        html = f"<h3>{category}</h3>"
        
        for article in articles:
            html += f"<div style='margin-bottom: 15px;'>"
            html += f"<h4>{article['title']}</h4>"
            html += f"<p>{article['content']}</p>"
            html += "</div>"
        
        self.category_content.setHtml(html)
    
    def show_tutorial_content(self, row):
        """Mostra il contenuto del tutorial selezionato"""
        if row < 0:
            return
        
        tutorial_name = self.tutorials_list.item(row).text()
        tutorial = self.get_tutorial_by_name(tutorial_name)
        
        if not tutorial:
            self.tutorial_content.setHtml("<p>Tutorial non disponibile.</p>")
            return
        
        html = f"<h2>{tutorial['title']}</h2>"
        html += f"<p><i>{tutorial['description']}</i></p>"
        
        # Aggiungi i passaggi del tutorial
        html += "<h3>Procedura:</h3>"
        html += "<ol>"
        for i, step in enumerate(tutorial['steps']):
            html += f"<li><b>Passo {i+1}:</b> {step['title']}<br>{step['description']}</li>"
        html += "</ol>"
        
        # Aggiungi suggerimenti e note
        if tutorial.get('tips'):
            html += "<h3>Suggerimenti:</h3><ul>"
            for tip in tutorial['tips']:
                html += f"<li>{tip}</li>"
            html += "</ul>"
        
        self.tutorial_content.setHtml(html)
    
    def get_tutorial_by_name(self, name):
        """Recupera un tutorial dal database dei tutorial"""
        for tutorial in self.tutorial_database:
            if tutorial['title'] == name:
                return tutorial
        return None
    
    def load_knowledge_base(self):
        """Carica il database delle conoscenze"""
        return [
            # GUIDA INTRODUTTIVA
            {
                'title': 'Benvenuto in MX Manager',
                'content': 'MX Manager è un software completo per la gestione di gare di motocross. '
                          'Questo assistente ti aiuterà a utilizzare tutte le funzionalità del programma. '
                          'Puoi cercare informazioni specifiche o esplorare le varie categorie di aiuto.',
                'categories': ['Guida introduttiva'],
                'keywords': ['benvenuto', 'introduzione', 'guida', 'inizio', 'nuovo']
            },
            {
                'title': 'Panoramica delle funzionalità',
                'content': 'MX Manager offre una serie completa di strumenti per gestire eventi di motocross: '
                          '• Gestione anagrafica piloti\n'
                          '• Creazione e gestione eventi\n'
                          '• Gestione iscrizioni\n'
                          '• Organizzazione prove libere\n'
                          '• Gestione qualifiche e cronometraggio\n'
                          '• Creazione e gestione gruppi di gara\n'
                          '• Gestione penalità\n'
                          '• Generazione classifiche e statistiche\n'
                          '• Backup e ripristino dati',
                'categories': ['Guida introduttiva'],
                'keywords': ['panoramica', 'funzionalità', 'funzioni', 'caratteristiche', 'strumenti']
            },
            {
                'title': 'Come navigare nell\'interfaccia',
                'content': 'L\'interfaccia di MX Manager è organizzata in schede accessibili dalla parte superiore della finestra. '
                          'Ogni scheda contiene funzioni specifiche per una particolare area di gestione. '
                          'I menu "File" e "Opzioni" in alto forniscono accesso a funzionalità aggiuntive come '
                          'backup, impostazioni e questo assistente.',
                'categories': ['Guida introduttiva'],
                'keywords': ['interfaccia', 'navigare', 'schede', 'menu', 'utilizzare']
            },

            # GESTIONE PILOTI
            {
                'title': 'Come aggiungere un nuovo pilota',
                'content': 'Per aggiungere un nuovo pilota, vai alla scheda "Piloti" e clicca sul pulsante "Aggiungi Pilota". '
                          'Compila tutti i campi richiesti come nome, cognome, data di nascita, moto club e numero di licenza. '
                          'La licenza deve essere un numero valido emesso dalla federazione. '
                          'Clicca su "Salva" per confermare e aggiungere il pilota al database.',
                'categories': ['Gestione piloti'],
                'keywords': ['pilota', 'aggiungere', 'nuovo', 'inserire', 'creare']
            },
            {
                'title': 'Come modificare un pilota esistente',
                'content': 'Per modificare i dati di un pilota esistente, vai alla scheda "Piloti", seleziona il pilota '
                          'che vuoi modificare dalla tabella e clicca sul pulsante "Modifica Pilota". Aggiorna i dati '
                          'necessari nel modulo che appare e clicca su "Salva". Puoi modificare qualsiasi campo '
                          'tranne l\'ID che è generato automaticamente dal sistema.',
                'categories': ['Gestione piloti'],
                'keywords': ['pilota', 'modificare', 'aggiornare', 'cambiare', 'dati']
            },
            {
                'title': 'Come eliminare un pilota',
                'content': 'Per eliminare un pilota, vai alla scheda "Piloti", seleziona il pilota che vuoi rimuovere '
                          'dalla tabella e clicca sul pulsante "Elimina Pilota". Ti verrà chiesta una conferma '
                          'prima di procedere con l\'eliminazione. Nota: l\'eliminazione è permanente ma '
                          'i risultati storici associati al pilota verranno mantenuti nel database.',
                'categories': ['Gestione piloti'],
                'keywords': ['pilota', 'eliminare', 'cancellare', 'rimuovere', 'togliere']
            },
            {
                'title': 'Come visualizzare le statistiche di un pilota',
                'content': 'Per visualizzare le statistiche complete di un pilota, vai alla scheda "Piloti", '
                          'seleziona il pilota dalla tabella e clicca sul pulsante "Visualizza Statistiche". '
                          'Apparirà una finestra con tutti i dati statistici del pilota: gare disputate, vittorie, '
                          'podi, punti totali, media punti per gara e altro. Puoi generare un report in formato HTML '
                          'o visualizzare grafici delle performance.',
                'categories': ['Gestione piloti', 'Classifiche e statistiche'],
                'keywords': ['statistiche', 'pilota', 'risultati', 'performance', 'dati']
            },
            {
                'title': 'Come cercare un pilota',
                'content': 'Puoi cercare rapidamente un pilota nella scheda "Piloti" utilizzando il campo di ricerca '
                          'sopra la tabella. Digita parte del nome, cognome o numero di licenza per filtrare '
                          'istantaneamente l\'elenco. Puoi anche ordinare la tabella cliccando sulle intestazioni '
                          'delle colonne.',
                'categories': ['Gestione piloti'],
                'keywords': ['pilota', 'cercare', 'trovare', 'ricerca', 'filtrare']
            },

            # EVENTI E GARE
            {
                'title': 'Come creare un nuovo evento',
                'content': 'Per creare un nuovo evento, vai alla scheda "Eventi" e clicca sul pulsante "Aggiungi Evento". '
                          'Inserisci il nome dell\'evento, la data, il luogo e altre informazioni richieste. '
                          'Puoi anche specificare le categorie di gara incluse nell\'evento e il formato della competizione. '
                          'Gli eventi sono il contenitore principale per tutte le gare, qualifiche e classifiche.',
                'categories': ['Eventi e gare'],
                'keywords': ['evento', 'gara', 'creare', 'nuovo', 'aggiungere']
            },
            {
                'title': 'Come modificare un evento esistente',
                'content': 'Per modificare un evento esistente, vai alla scheda "Eventi", seleziona l\'evento dalla tabella '
                          'e clicca su "Modifica Evento". Puoi aggiornare qualsiasi informazione come nome, data o luogo. '
                          'Se l\'evento è già iniziato, alcune opzioni potrebbero essere limitate per preservare '
                          'l\'integrità dei dati già registrati.',
                'categories': ['Eventi e gare'],
                'keywords': ['evento', 'modificare', 'aggiornare', 'cambiare', 'editing']
            },
            {
                'title': 'Come eliminare un evento',
                'content': 'Per eliminare un evento, vai alla scheda "Eventi", seleziona l\'evento dalla lista e clicca '
                          'su "Elimina Evento". Ti sarà chiesta una conferma poiché questa azione eliminerà anche '
                          'tutte le iscrizioni, i risultati delle prove, delle qualifiche e delle gare associate. '
                          'Questa operazione non può essere annullata.',
                'categories': ['Eventi e gare'],
                'keywords': ['evento', 'eliminare', 'cancellare', 'rimuovere', 'togliere']
            },
            {
                'title': 'Come gestire le sessioni di gara',
                'content': 'Ogni evento può avere diverse sessioni di gara (manche). Per configurare le sessioni, '
                          'vai alla scheda "Eventi", seleziona l\'evento e clicca su "Gestione Sessioni". '
                          'Puoi definire il numero di manche, la durata di ciascuna, e i criteri di assegnazione '
                          'punti. Puoi anche impostare orari specifici per ciascuna sessione.',
                'categories': ['Eventi e gare'],
                'keywords': ['sessioni', 'manche', 'gare', 'configurare', 'impostare']
            },

            # ISCRIZIONI
            {
                'title': 'Come gestire le iscrizioni a un evento',
                'content': 'Per gestire le iscrizioni, vai alla scheda "Iscrizioni". Seleziona l\'evento '
                          'dal menu a tendina, poi seleziona i piloti che desideri iscrivere dall\'elenco a sinistra '
                          'e usa il pulsante ">" per aggiungerli agli iscritti. Puoi filtrare i piloti '
                          'per categoria o per moto club per trovarli più facilmente.',
                'categories': ['Iscrizioni', 'Eventi e gare'],
                'keywords': ['iscrizione', 'pilota', 'evento', 'partecipare', 'aggiungere']
            },
            {
                'title': 'Come gestire le quote di iscrizione',
                'content': 'Puoi registrare il pagamento delle quote di iscrizione nella scheda "Iscrizioni". '
                          'Seleziona un pilota già iscritto e clicca su "Gestione Pagamento". '
                          'Puoi registrare l\'importo pagato, la data e il metodo di pagamento. '
                          'Il sistema tiene traccia di chi ha già pagato e chi deve ancora farlo.',
                'categories': ['Iscrizioni'],
                'keywords': ['quota', 'pagamento', 'iscrizione', 'soldi', 'tassa']
            },
            {
                'title': 'Come importare iscrizioni da file',
                'content': 'Per importare iscrizioni da un file esterno, vai alla scheda "Iscrizioni" e clicca su '
                          '"Importa Iscrizioni". Puoi importare file CSV o Excel con un formato specifico. '
                          'Il sistema verificherà che i piloti esistano nel database e ti chiederà come gestire '
                          'eventuali discrepanze o piloti non trovati.',
                'categories': ['Iscrizioni'],
                'keywords': ['importare', 'iscrizioni', 'file', 'csv', 'excel']
            },
            {
                'title': 'Come verificare lo stato delle iscrizioni',
                'content': 'Per verificare lo stato complessivo delle iscrizioni, vai alla scheda "Iscrizioni" e '
                          'seleziona l\'evento desiderato. Nella parte inferiore della schermata troverai '
                          'un riepilogo con il numero totale di iscritti, suddivisi per categoria, '
                          'e lo stato dei pagamenti. Puoi anche esportare questo report.',
                'categories': ['Iscrizioni'],
                'keywords': ['verifica', 'stato', 'iscrizioni', 'riepilogo', 'report']
            },

            # PROVE LIBERE
            {
                'title': 'Come organizzare turni di prove libere',
                'content': 'Per organizzare le prove libere, vai alla scheda "Prove Libere" e seleziona l\'evento. '
                          'Clicca su "Crea Turni" per impostare i vari turni di prove. Puoi definire '
                          'orari, durata e numero massimo di piloti per ciascun turno. Il sistema può '
                          'suggerire una distribuzione ottimale dei piloti nei vari turni.',
                'categories': ['Prove libere'],
                'keywords': ['prove', 'libere', 'turni', 'organizzare', 'creare']
            },
            {
                'title': 'Come registrare i tempi nelle prove libere',
                'content': 'Per registrare i tempi durante le prove libere, vai alla scheda "Prove Libere", '
                          'seleziona l\'evento e il turno. Clicca su "Avvia Cronometraggio" per entrare nella '
                          'modalità di registrazione tempi. Puoi inserire manualmente i tempi per ciascun pilota '
                          'o utilizzare un sistema di cronometraggio elettronico integrato se disponibile.',
                'categories': ['Prove libere'],
                'keywords': ['cronometraggio', 'tempi', 'prove', 'libere', 'registrare']
            },
            {
                'title': 'Come analizzare i risultati delle prove libere',
                'content': 'Per analizzare i risultati delle prove libere, vai alla scheda "Prove Libere", '
                          'seleziona l\'evento e il turno completato, poi clicca su "Analisi Tempi". '
                          'Qui potrai vedere i migliori tempi di ciascun pilota, confrontare le prestazioni '
                          'e visualizzare grafici con l\'evoluzione dei tempi durante la sessione.',
                'categories': ['Prove libere'],
                'keywords': ['analisi', 'risultati', 'prove', 'libere', 'tempi']
            },

            # QUALIFICHE
            {
                'title': 'Come impostare le sessioni di qualifica',
                'content': 'Per impostare le sessioni di qualifica, vai alla scheda "Qualifiche" e seleziona l\'evento. '
                          'Clicca su "Configura Qualifiche" per definire il formato delle qualifiche: puoi scegliere '
                          'tra qualifiche a tempo (superpole) o batterie di qualificazione. Imposta la durata, '
                          'il numero di piloti per sessione e i criteri di avanzamento.',
                'categories': ['Qualifiche'],
                'keywords': ['qualifiche', 'impostare', 'configurare', 'sessioni', 'formato']
            },
            {
                'title': 'Come gestire il cronometraggio delle qualifiche',
                'content': 'Per gestire il cronometraggio delle qualifiche, vai alla scheda "Qualifiche", '
                          'seleziona l\'evento e la sessione, poi clicca su "Avvia Cronometraggio". '
                          'Registra i tempi per ciascun pilota. Il sistema mostrerà automaticamente '
                          'la classifica in tempo reale, evidenziando i piloti qualificati in base '
                          'ai criteri impostati per l\'evento.',
                'categories': ['Qualifiche'],
                'keywords': ['cronometraggio', 'qualifiche', 'tempi', 'registrare', 'misurare']
            },
            {
                'title': 'Come correggere i tempi di qualifica',
                'content': 'Per correggere tempi di qualifica già registrati, vai alla scheda "Qualifiche", '
                          'seleziona l\'evento e la sessione, poi clicca su "Modifica Tempi". '
                          'Puoi selezionare il pilota e correggere il tempo registrato. '
                          'Il sistema terrà traccia delle modifiche nel registro degli eventi '
                          'per garantire la trasparenza delle operazioni.',
                'categories': ['Qualifiche'],
                'keywords': ['correggere', 'modificare', 'tempi', 'qualifica', 'aggiustare']
            },

            # GESTIONE GRUPPI DI GARA
            {
                'title': 'Come creare gruppi di gara automatici',
                'content': 'Per creare automaticamente i gruppi di gara, vai alla scheda "Gruppi di Gara" e seleziona '
                          'l\'evento e la categoria. Imposta il metodo di raggruppamento (in base alle qualifiche '
                          'o ad altri criteri) e il numero massimo di piloti per gruppo. Clicca su "Genera Gruppi" '
                          'e il sistema creerà automaticamente i gruppi ottimali.',
                'categories': ['Gestione gruppi'],
                'keywords': ['gruppi', 'generare', 'automatici', 'creare', 'suddividere']
            },
            {
                'title': 'Come modificare manualmente i gruppi di gara',
                'content': 'Per modificare manualmente i gruppi di gara, vai alla scheda "Gruppi di Gara", '
                          'seleziona l\'evento e i gruppi già creati, poi clicca su "Modifica Gruppi". '
                          'Puoi spostare i piloti tra i gruppi usando drag and drop o i pulsanti di spostamento. '
                          'Il sistema verificherà che non vengano superati i limiti massimi per gruppo.',
                'categories': ['Gestione gruppi'],
                'keywords': ['gruppi', 'modificare', 'manuale', 'spostare', 'piloti']
            },
            {
                'title': 'Come assegnare numeri di gara ai piloti',
                'content': 'Per assegnare numeri di gara ai piloti, vai alla scheda "Gruppi di Gara", seleziona '
                          'l\'evento e il gruppo, poi clicca su "Assegna Numeri". Puoi assegnare numeri '
                          'manualmente o lasciare che il sistema li assegni automaticamente in base '
                          'alle posizioni di qualifica o ad altri criteri. I numeri possono essere '
                          'stampati per le tabelle portanumero.',
                'categories': ['Gestione gruppi'],
                'keywords': ['numeri', 'gara', 'assegnare', 'tabelle', 'portanumero']
            },
            {
                'title': 'Come gestire la griglia di partenza',
                'content': 'Per gestire la griglia di partenza, vai alla scheda "Gruppi di Gara", seleziona '
                          'l\'evento, il gruppo e la manche, poi clicca su "Griglia di Partenza". '
                          'Puoi impostare l\'ordine di ingresso al cancello in base ai risultati '
                          'delle qualifiche o manualmente. Puoi anche stampare la griglia di partenza '
                          'da consegnare agli ufficiali di gara.',
                'categories': ['Gestione gruppi'],
                'keywords': ['griglia', 'partenza', 'cancello', 'ordine', 'posizione']
            },

            # GESTIONE PENALITÀ
            {
                'title': 'Come registrare penalità durante una gara',
                'content': 'Per registrare penalità durante una gara, vai alla scheda "Gestione Penalità", '
                          'seleziona l\'evento, la manche e il pilota interessato. Clicca su "Aggiungi Penalità" '
                          'e seleziona il tipo di penalità (tempo, posizioni o squalifica), la motivazione e '
                          'l\'entità. Le penalità verranno automaticamente considerate nel calcolo dei risultati finali.',
                'categories': ['Gestione Penalità'],
                'keywords': ['penalità', 'registrare', 'squalifica', 'tempo', 'posizioni']
            },
            {
                'title': 'Come visualizzare tutte le penalità di un evento',
                'content': 'Per visualizzare tutte le penalità assegnate in un evento, vai alla scheda '
                          '"Gestione Penalità" e seleziona l\'evento. Nel pannello inferiore vedrai '
                          'l\'elenco completo delle penalità, con possibilità di filtrare per pilota, '
                          'tipo di penalità o manche. Puoi anche stampare questo report per la direzione gara.',
                'categories': ['Gestione Penalità'],
                'keywords': ['penalità', 'elenco', 'visualizzare', 'report', 'lista']
            },
            {
                'title': 'Come modificare o annullare una penalità',
                'content': 'Per modificare o annullare una penalità già assegnata, vai alla scheda "Gestione Penalità", '
                          'seleziona l\'evento e trova la penalità nell\'elenco. Clicca su "Modifica" per '
                          'cambiare i dettagli o su "Annulla" per rimuoverla. Ogni modifica viene registrata '
                          'nel log del sistema per tracciabilità e conformità con i regolamenti sportivi.',
                'categories': ['Gestione Penalità'],
                'keywords': ['penalità', 'modificare', 'annullare', 'rimuovere', 'cambiare']
            },

            # CLASSIFICHE E STATISTICHE
            {
                'title': 'Come generare classifiche di gara',
                'content': 'Per generare la classifica di una gara, vai alla scheda "Classifiche e Statistiche" '
                          'e seleziona l\'evento, la categoria e la manche. Clicca su "Genera Classifica" '
                          'e il sistema elaborerà automaticamente i risultati considerando l\'ordine di arrivo, '
                          'i giri completati, eventuali penalità e il sistema di punteggio configurato. '
                          'Puoi stampare o esportare la classifica in vari formati.',
                'categories': ['Classifiche e statistiche'],
                'keywords': ['classifica', 'gara', 'generare', 'calcolare', 'risultati']
            },
            {
                'title': 'Come calcolare la classifica generale di un evento',
                'content': 'Per calcolare la classifica generale di un evento con più manche, vai alla scheda '
                          '"Classifiche e Statistiche", seleziona l\'evento e la categoria, poi clicca su '
                          '"Classifica Generale". Il sistema sommerà i punti ottenuti nelle varie manche '
                          'secondo i criteri configurati (tutte le manche valide, scarto del peggior risultato, ecc.) '
                          'e genererà la classifica finale dell\'evento.',
                'categories': ['Classifiche e statistiche'],
                'keywords': ['classifica', 'generale', 'evento', 'finale', 'somma']
            },
            {
                'title': 'Come visualizzare statistiche dettagliate di gara',
                'content': 'Per visualizzare statistiche dettagliate di una gara, vai alla scheda "Classifiche e Statistiche", '
                          'seleziona l\'evento e la manche, poi clicca su "Statistiche Dettagliate". '
                          'Potrai vedere analisi come distacchi, giri veloci, evoluzione delle posizioni durante la gara, '
                          'e altre metriche avanzate. Queste informazioni possono essere visualizzate in forma di grafici e tabelle.',
                'categories': ['Classifiche e statistiche'],
                'keywords': ['statistiche', 'dettagliate', 'analisi', 'gara', 'grafici']
            },
            {
                'title': 'Come esportare risultati e classifiche',
                'content': 'Per esportare risultati e classifiche, vai alla scheda "Classifiche e Statistiche", '
                          'genera la classifica desiderata e clicca su "Esporta". Puoi scegliere il formato '
                          '(PDF, Excel, CSV, HTML) e la destinazione. Puoi anche configurare l\'aspetto '
                          'dei report, aggiungere loghi personalizzati e includere informazioni aggiuntive.',
                'categories': ['Classifiche e statistiche'],
                'keywords': ['esportare', 'risultati', 'classifiche', 'pdf', 'excel']
            },
            {
                'title': 'Come pubblicare i risultati online',
                'content': 'Per pubblicare i risultati online, vai alla scheda "Classifiche e Statistiche", '
                          'genera la classifica desiderata e clicca su "Pubblica Online". Se hai configurato '
                          'le impostazioni di pubblicazione (nelle preferenze), i risultati verranno caricati '
                          'automaticamente sul sito web collegato o esportati in un formato compatibile con '
                          'varie piattaforme di pubblicazione risultati.',
                'categories': ['Classifiche e statistiche'],
                'keywords': ['pubblicare', 'online', 'risultati', 'web', 'internet']
            },

            # BACKUP E SICUREZZA
            {
                'title': 'Come fare un backup del database',
                'content': 'Per creare un backup del database, clicca sul menu "File" e seleziona "Backup Database". '
                          'Scegli la posizione dove salvare il file di backup e clicca su "Salva". '
                          'È consigliabile fare backup regolari per evitare la perdita di dati. '
                          'Puoi anche configurare backup automatici nelle impostazioni del programma.',
                'categories': ['Backup e sicurezza'],
                'keywords': ['backup', 'database', 'salvare', 'dati', 'sicurezza']
            },
            {
                'title': 'Come ripristinare un database da backup',
                'content': 'Per ripristinare un database da un backup precedente, clicca sul menu "File" e seleziona '
                          '"Ripristina Database". Seleziona il file di backup (.db o .backup) e conferma '
                          'l\'operazione. Attenzione: questa operazione sovrascriverà tutti i dati attuali! '
                          'È consigliabile fare un backup prima del ripristino, se ci sono dati nuovi da preservare.',
                'categories': ['Backup e sicurezza'],
                'keywords': ['ripristinare', 'backup', 'database', 'recuperare', 'dati']
            },
            {
                'title': 'Come configurare backup automatici',
                'content': 'Per configurare backup automatici, vai al menu "Opzioni", seleziona "Impostazioni" '
                          'e apri la scheda "Generale". Nella sezione backup, puoi attivare i backup automatici '
                          'e configurare la frequenza (ogni ora, giornaliero, settimanale), la posizione di '
                          'salvataggio e il numero di backup da mantenere prima di sovrascrivere i più vecchi.',
                'categories': ['Backup e sicurezza', 'Impostazioni'],
                'keywords': ['backup', 'automatico', 'configurare', 'pianificare', 'regolare']
            },

            # IMPOSTAZIONI
            {
                'title': 'Come configurare le impostazioni generali',
                'content': 'Per configurare le impostazioni generali, vai al menu "Opzioni" e seleziona "Impostazioni". '
                          'Nella scheda "Generale" puoi impostare il percorso del database, la lingua dell\'interfaccia, '
                          'le opzioni di backup e altre preferenze di base. Queste impostazioni influenzano '
                          'il comportamento generale del programma.',
                'categories': ['Impostazioni'],
                'keywords': ['impostazioni', 'generali', 'configurare', 'preferenze', 'opzioni']
            },
            {
                'title': 'Come configurare il sistema di punteggio',
                'content': 'Per configurare il sistema di punteggio, vai al menu "Opzioni", seleziona "Impostazioni" '
                          'e apri la scheda "Gare". Qui puoi selezionare un sistema di punteggio predefinito '
                          '(come FMI Standard) o creare un sistema personalizzato definendo i punti '
                          'per ciascuna posizione. Puoi anche configurare regole speciali come punteggio doppio '
                          'per l\'ultima manche o punti bonus per il giro veloce.',
                'categories': ['Impostazioni', 'Classifiche e statistiche'],
                'keywords': ['punteggio', 'sistema', 'punti', 'configurare', 'posizioni']
            },
            {
                'title': 'Come personalizzare i report e le stampe',
                'content': 'Per personalizzare i report e le stampe, vai al menu "Opzioni", seleziona "Impostazioni" '
                          'e apri la scheda "Report". Qui puoi caricare un logo personalizzato, inserire '
                          'le informazioni dell\'organizzatore, e scegliere i formati predefiniti per l\'esportazione. '
                          'Puoi anche personalizzare l\'aspetto dei report selezionando i colori, '
                          'i font e le informazioni da includere.',
                'categories': ['Impostazioni', 'Classifiche e statistiche'],
                'keywords': ['report', 'personalizzare', 'stampe', 'logo', 'formato']
            },
            {
                'title': 'Come configurare l\'interfaccia utente',
                'content': 'Per configurare l\'aspetto dell\'interfaccia utente, vai al menu "Opzioni", seleziona '
                          '"Impostazioni" e apri la scheda "Utente". Qui puoi scegliere il tema (chiaro, scuro o '
                          'di sistema), la dimensione dei caratteri, e altre preferenze visive. '
                          'Puoi anche attivare o disattivare i suoni di notifica e configurare il numero di '
                          'elementi visualizzati nelle liste e tabelle.',
                'categories': ['Impostazioni'],
                'keywords': ['interfaccia', 'tema', 'aspetto', 'configurare', 'visualizzazione']
            }
        ]
    
    def load_tutorial_database(self):
        """Carica il database dei tutorial"""
        return [
            {
                'title': 'Configurazione Iniziale del Software',
                'description': 'Guida completa alla prima configurazione di MX Manager per iniziare a utilizzarlo nel modo più efficiente.',
                'steps': [
                    {
                        'title': 'Impostare le preferenze di base',
                        'description': 'Vai al menu "Opzioni" > "Impostazioni" e nella scheda "Generale" configura il percorso del database, la lingua e le impostazioni di backup automatico.'
                    },
                    {
                        'title': 'Personalizzare le impostazioni utente',
                        'description': 'Nella scheda "Utente" delle impostazioni, scegli il tema dell\'interfaccia, la dimensione dei caratteri e altre preferenze visive che preferisci.'
                    },
                    {
                        'title': 'Configurare il sistema di punteggio',
                        'description': 'Nella scheda "Gare" delle impostazioni, seleziona il sistema di punteggio standard o crea uno personalizzato che userai per tutte le tue competizioni.'
                    },
                    {
                        'title': 'Personalizzare i report',
                        'description': 'Nella scheda "Report" delle impostazioni, carica il logo della tua organizzazione e inserisci i dettagli che verranno inclusi in tutti i report e le stampe.'
                    },
                    {
                        'title': 'Importare piloti esistenti',
                        'description': 'Vai alla scheda "Piloti" e usa la funzione "Importa Piloti" se hai già un elenco di piloti in formato CSV o Excel. In alternativa, inizia ad aggiungerli manualmente.'
                    }
                ],
                'tips': [
                    'Dedica tempo a configurare correttamente le impostazioni all\'inizio per evitare di doverle modificare in seguito.',
                    'Crea subito una cartella dedicata per i backup e imposta backup automatici regolari.',
                    'Se hai una connessione internet stabile, attiva gli aggiornamenti automatici per avere sempre l\'ultima versione.'
                ]
            },
            {
                'title': 'Organizzazione Completa di un Evento',
                'description': 'Tutorial completo che ti guida attraverso tutti i passaggi necessari per organizzare un evento di motocross dall\'inizio alla fine.',
                'steps': [
                    {
                        'title': 'Creare un nuovo evento',
                        'description': 'Vai alla scheda "Eventi" e clicca su "Aggiungi Evento". Inserisci il nome, la data, il luogo e tutte le altre informazioni richieste. Seleziona le categorie che parteciperanno.'
                    },
                    {
                        'title': 'Definire le sessioni di gara',
                        'description': 'Nella scheda "Eventi", seleziona l\'evento appena creato e clicca su "Gestione Sessioni". Configura il numero di manche, la durata e l\'orario di ciascuna sessione.'
                    },
                    {
                        'title': 'Configurare le iscrizioni',
                        'description': 'Vai alla scheda "Iscrizioni", seleziona l\'evento e inizia ad aggiungere i piloti. Puoi impostare una quota di iscrizione e una data di chiusura delle iscrizioni.'
                    },
                    {
                        'title': 'Pianificare le prove libere',
                        'description': 'Nella scheda "Prove Libere", crea i turni di prove libere, assegnando orari e durata per ciascuna categoria. Distribuisci i piloti nei vari turni in modo equilibrato.'
                    },
                    {
                        'title': 'Configurare le qualifiche',
                        'description': 'Vai alla scheda "Qualifiche" e imposta il formato delle qualifiche per ciascuna categoria. Definisci i criteri di qualificazione e avanzamento.'
                    },
                    {
                        'title': 'Preparare i gruppi di gara',
                        'description': 'Nella scheda "Gruppi di Gara", configura come verranno formati i gruppi in base ai risultati delle qualifiche o ad altri criteri. Imposta il numero massimo di piloti per gruppo.'
                    },
                    {
                        'title': 'Preparare le classifiche',
                        'description': 'Nella scheda "Classifiche e Statistiche", verifica che il sistema di punteggio sia corretto e prepara i modelli di report che verranno utilizzati.'
                    }
                ],
                'tips': [
                    'Prepara un calendario dettagliato dell\'evento e condividilo con staff e piloti in anticipo.',
                    'Prevedi del tempo extra tra le sessioni per gestire eventuali ritardi.',
                    'Verifica che tutte le categorie abbiano impostazioni appropriate per il loro livello.'
                ]
            },
            {
                'title': 'Gestione delle Iscrizioni e Pagamenti',
                'description': 'Come gestire in modo efficiente le iscrizioni dei piloti e tenere traccia dei pagamenti delle quote di iscrizione.',
                'steps': [
                    {
                        'title': 'Aprire le iscrizioni',
                        'description': 'Vai alla scheda "Iscrizioni", seleziona l\'evento e clicca su "Apri Iscrizioni". Imposta la data di apertura e chiusura e le quote di iscrizione per ciascuna categoria.'
                    },
                    {
                        'title': 'Aggiungere iscritti manualmente',
                        'description': 'Nella scheda "Iscrizioni", usa il pulsante ">" per spostare i piloti dall\'elenco a sinistra (tutti i piloti) a quello a destra (iscritti). Puoi filtrare l\'elenco per categoria o moto club.'
                    },
                    {
                        'title': 'Importare iscritti da file',
                        'description': 'Se hai ricevuto iscrizioni via email o altro sistema, clicca su "Importa Iscrizioni" e seleziona il file CSV o Excel. Verifica che il formato sia corretto seguendo il modello fornito.'
                    },
                    {
                        'title': 'Registrare i pagamenti',
                        'description': 'Seleziona un pilota dall\'elenco iscritti e clicca su "Gestione Pagamento". Inserisci l\'importo pagato, la data e il metodo di pagamento. Aggiungi eventuali note.'
                    },
                    {
                        'title': 'Verificare lo stato delle iscrizioni',
                        'description': 'Usa la funzione "Riepilogo Iscrizioni" per vedere quanti piloti sono iscritti per categoria e quanti hanno completato il pagamento. Identifica rapidamente i pagamenti mancanti.'
                    },
                    {
                        'title': 'Generare la lista iscritti',
                        'description': 'Clicca su "Esporta Iscritti" per generare un file PDF o Excel con l\'elenco completo degli iscritti, utile per verifiche e controlli alla segreteria di gara.'
                    }
                ],
                'tips': [
                    'Aggiorna regolarmente lo stato dei pagamenti per avere sempre la situazione sotto controllo.',
                    'Invia promemoria automatici ai piloti che non hanno ancora pagato la quota di iscrizione.',
                    'Prepara un foglio di calcolo separato per tracciare le entrate e le spese dell\'evento.'
                ]
            },
            {
                'title': 'Configurazione e Gestione Prove Libere',
                'description': 'Come organizzare e gestire efficacemente le sessioni di prove libere, incluso il cronometraggio e l\'analisi dei tempi.',
                'steps': [
                    {
                        'title': 'Pianificare i turni di prove libere',
                        'description': 'Vai alla scheda "Prove Libere", seleziona l\'evento e clicca su "Crea Turni". Definisci quanti turni avere per categoria, la durata di ciascuno e gli orari.'
                    },
                    {
                        'title': 'Assegnare i piloti ai turni',
                        'description': 'Dopo aver creato i turni, seleziona un turno e clicca su "Assegna Piloti". Puoi assegnarli manualmente o lasciare che il sistema li distribuisca automaticamente in modo equilibrato.'
                    },
                    {
                        'title': 'Preparare il cronometraggio',
                        'description': 'Prima dell\'inizio delle prove, seleziona il turno e clicca su "Prepara Cronometraggio". Verifica che l\'elenco dei piloti sia corretto e che tutto sia pronto per registrare i tempi.'
                    },
                    {
                        'title': 'Registrare i tempi sul giro',
                        'description': 'Durante il turno, usa l\'interfaccia di cronometraggio per registrare i tempi di ciascun pilota. Puoi inserirli manualmente o importarli da un sistema di cronometraggio elettronico.'
                    },
                    {
                        'title': 'Analizzare i risultati delle prove',
                        'description': 'Dopo la fine del turno, clicca su "Analisi Tempi" per vedere statistiche dettagliate: migliori tempi, confronto tra piloti, evoluzione dei tempi durante la sessione, ecc.'
                    },
                    {
                        'title': 'Generare report dei tempi',
                        'description': 'Clicca su "Genera Report" per creare un documento con i tempi di tutti i piloti, ordinati dal più veloce al più lento. Puoi stamparlo o pubblicarlo per informare i piloti.'
                    }
                ],
                'tips': [
                    'Assicurati di avere orologi sincronizzati se usi più punti di cronometraggio.',
                    'Prevedi più personale durante le prove libere, quando spesso molti piloti sono in pista contemporaneamente.',
                    'Usa codici colore o simboli nei report per evidenziare i piloti più veloci o quelli che hanno fatto grandi miglioramenti.'
                ]
            },
            {
                'title': 'Qualifiche e Formazione Gruppi',
                'description': 'Guida completa alla gestione delle sessioni di qualifica e alla creazione dei gruppi di gara in base ai risultati.',
                'steps': [
                    {
                        'title': 'Impostare il formato delle qualifiche',
                        'description': 'Vai alla scheda "Qualifiche", seleziona l\'evento e clicca su "Configura Qualifiche". Scegli tra formato a tempo (superpole) o batterie di qualificazione per ciascuna categoria.'
                    },
                    {
                        'title': 'Preparare le sessioni di qualifica',
                        'description': 'Definisci la durata di ciascuna sessione, l\'ordine di partenza (casuale o basato su risultati precedenti) e i criteri di qualificazione per le gare finali.'
                    },
                    {
                        'title': 'Gestire il cronometraggio delle qualifiche',
                        'description': 'Durante le qualifiche, usa l\'interfaccia di cronometraggio per registrare i tempi di ogni giro. Il sistema mostrerà automaticamente la classifica in tempo reale.'
                    },
                    {
                        'title': 'Verificare i risultati delle qualifiche',
                        'description': 'Al termine delle qualifiche, controlla i risultati e gestisci eventuali reclami o correzioni. Conferma i risultati finali quando tutto è corretto.'
                    },
                    {
                        'title': 'Creare i gruppi di gara',
                        'description': 'Vai alla scheda "Gruppi di Gara", seleziona l\'evento e la categoria, poi clicca su "Genera Gruppi". Scegli il metodo di raggruppamento (in base alle qualifiche o altro criterio).'
                    },
                    {
                        'title': 'Verificare e modificare i gruppi',
                        'description': 'Controlla i gruppi generati automaticamente e, se necessario, clicca su "Modifica Gruppi" per apportare modifiche manuali (ad esempio per separare piloti dello stesso team).'
                    },
                    {
                        'title': 'Assegnare i numeri di gara',
                        'description': 'Seleziona ciascun gruppo e clicca su "Assegna Numeri" per attribuire i numeri di gara. Puoi lasciar fare al sistema o impostarli manualmente in base a specifiche esigenze.'
                    },
                    {
                        'title': 'Pubblicare i gruppi di gara',
                        'description': 'Clicca su "Pubblica Gruppi" per generare il documento ufficiale con i gruppi di gara e l\'ordine di ingresso al cancello. Puoi stamparlo o pubblicarlo online.'
                    }
                ],
                'tips': [
                    'In caso di molti partecipanti, considera di fare pre-qualifiche per ridurre il numero di piloti nelle sessioni principali.',
                    'Prepara sempre un piano B per le qualifiche in caso di maltempo o altri imprevisti.',
                    'Comunica chiaramente il formato delle qualifiche durante il briefing dei piloti per evitare confusione.'
                ]
            },
            {
                'title': 'Gestione di una Giornata di Gara',
                'description': 'Come gestire efficientemente tutte le attività durante il giorno della gara, dal briefing piloti alle premiazioni finali.',
                'steps': [
                    {
                        'title': 'Preparare la giornata di gara',
                        'description': 'Stampa tutti i documenti necessari: elenco iscritti, gruppi di gara, schedule del giorno. Verifica che tutto il personale conosca i propri compiti e orari.'
                    },
                    {
                        'title': 'Gestire le verifiche tecniche',
                        'description': 'Nella scheda "Iscrizioni", usa la funzione "Verifica Tecnica" per registrare quali piloti hanno superato i controlli tecnici e sono autorizzati a partecipare.'
                    },
                    {
                        'title': 'Condurre il briefing piloti',
                        'description': 'Usa la scheda "Eventi" e seleziona "Briefing Piloti" per accedere a una checklist di argomenti da coprire durante il briefing. Registra presenze e note importanti.'
                    },
                    {
                        'title': 'Gestire la griglia di partenza',
                        'description': 'Per ciascuna manche, vai alla scheda "Gruppi di Gara" e usa la funzione "Griglia di Partenza" per gestire l\'ingresso al cancello secondo l\'ordine prestabilito.'
                    },
                    {
                        'title': 'Registrare i risultati della gara',
                        'description': 'Durante o dopo ciascuna manche, vai alla scheda "Classifiche e Statistiche" per inserire l\'ordine di arrivo, i giri completati e altri dati pertinenti.'
                    },
                    {
                        'title': 'Gestire penalità e reclami',
                        'description': 'Usa la scheda "Gestione Penalità" per registrare eventuali sanzioni o decisioni della direzione gara. Documenta accuratamente motivazioni e riferimenti al regolamento.'
                    },
                    {
                        'title': 'Generare classifiche provvisorie',
                        'description': 'Dopo ciascuna manche, genera e pubblica le classifiche provvisorie. Imposta un tempo per eventuali reclami prima di confermarle come definitive.'
                    },
                    {
                        'title': 'Preparare la cerimonia di premiazione',
                        'description': 'Al termine dell\'evento, vai alla scheda "Classifiche e Statistiche" e usa la funzione "Podio" per generare l\'elenco dei piloti da premiare per ciascuna categoria.'
                    }
                ],
                'tips': [
                    'Assegna una persona dedicata al monitoraggio del programma orario per gestire eventuali ritardi.',
                    'Usa la funzione di annunci per comunicare cambiamenti o informazioni importanti a tutti i partecipanti.',
                    'Mantieni sempre un backup fisico (carta) dei dati più importanti, come le classifiche, in caso di problemi tecnici.'
                ]
            },
            {
                'title': 'Elaborazione Risultati e Classifiche',
                'description': 'Come gestire in modo accurato e efficiente i risultati delle gare e generare le classifiche finali per l\'evento e il campionato.',
                'steps': [
                    {
                        'title': 'Inserire i risultati delle manche',
                        'description': 'Vai alla scheda "Classifiche e Statistiche", seleziona l\'evento, la categoria e la manche. Inserisci l\'ordine di arrivo dei piloti, eventuali ritiri o squalifiche.'
                    },
                    {
                        'title': 'Verificare e correggere i risultati',
                        'description': 'Dopo l\'inserimento, controlla attentamente tutti i dati. Se necessario, usa la funzione "Modifica Risultati" per correggere eventuali errori di inserimento.'
                    },
                    {
                        'title': 'Generare la classifica di manche',
                        'description': 'Clicca su "Genera Classifica Manche" per calcolare i punti assegnati a ciascun pilota secondo il sistema di punteggio configurato. Verifica che i calcoli siano corretti.'
                    },
                    {
                        'title': 'Applicare eventuali penalità',
                        'description': 'Vai alla scheda "Gestione Penalità" per applicare eventuali sanzioni che influenzano la classifica. Le penalità verranno automaticamente considerate nei punteggi finali.'
                    },
                    {
                        'title': 'Calcolare la classifica generale dell\'evento',
                        'description': 'Nella scheda "Classifiche e Statistiche", clicca su "Classifica Generale" per combinare i risultati di tutte le manche e calcolare la classifica finale dell\'evento.'
                    },
                    {
                        'title': 'Generare statistiche dettagliate',
                        'description': 'Usa la funzione "Analisi Dettagliata" per generare statistiche complete dell\'evento: giri veloci, distacchi, evoluzione delle posizioni durante la gara, ecc.'
                    },
                    {
                        'title': 'Esportare e pubblicare i risultati',
                        'description': 'Clicca su "Esporta Risultati" per generare file in vari formati (PDF, Excel, HTML). Usa "Pubblica Online" per caricare automaticamente i risultati sul sito web collegato.'
                    },
                    {
                        'title': 'Aggiornare la classifica del campionato',
                        'description': 'Se l\'evento fa parte di un campionato, vai alla sezione "Campionato" e clicca su "Aggiorna Classifica" per incorporare i nuovi risultati nella classifica generale del campionato.'
                    }
                ],
                'tips': [
                    'Fai sempre una doppia verifica dei risultati prima di pubblicarli ufficialmente.',
                    'Conserva i documenti originali con i risultati firmati dai commissari di gara per eventuali verifiche future.',
                    'Genera report statistici dettagliati per fornire contenuti interessanti per sito web, social media e comunicati stampa.'
                ]
            },
            {
                'title': 'Backup e Gestione Database',
                'description': 'Come proteggere i tuoi dati e gestire il database in modo sicuro ed efficiente, prevenendo perdite di dati e mantenendo prestazioni ottimali.',
                'steps': [
                    {
                        'title': 'Configurare backup automatici',
                        'description': 'Vai al menu "Opzioni" > "Impostazioni" > scheda "Generale" e configura i backup automatici. Imposta frequenza, percorso di salvataggio e numero di copie da mantenere.'
                    },
                    {
                        'title': 'Eseguire backup manuali',
                        'description': 'Prima e dopo eventi importanti, esegui un backup manuale dal menu "File" > "Backup Database". Scegli una posizione sicura e dai al file un nome che includa la data.'
                    },
                    {
                        'title': 'Verificare l\'integrità del database',
                        'description': 'Periodicamente, usa la funzione "File" > "Verifica Database" per controllare che non ci siano corruzioni o inconsistenze nei dati. Risolvi eventuali problemi segnalati.'
                    },
                    {
                        'title': 'Ottimizzare le prestazioni del database',
                        'description': 'Dopo molti eventi, usa la funzione "File" > "Ottimizza Database" per migliorare le prestazioni. Questa operazione riorganizza i dati e recupera spazio non utilizzato.'
                    },
                    {
                        'title': 'Archiviare eventi passati',
                        'description': 'Per mantenere il database principale snello, usa la funzione "File" > "Archivia Eventi" per spostare eventi vecchi in un database separato, mantenendoli accessibili ma senza appesantire il sistema.'
                    },
                    {
                        'title': 'Ripristinare da un backup',
                        'description': 'In caso di problemi, vai al menu "File" > "Ripristina Database" e seleziona un backup recente. Conferma di voler sovrascrivere il database attuale con la versione di backup.'
                    },
                    {
                        'title': 'Esportare dati per backup esterni',
                        'description': 'Periodicamente, usa "File" > "Esporta Dati" per salvare copie dei dati principali in formati standard come CSV o Excel, che possono essere conservati come backup aggiuntivo.'
                    }
                ],
                'tips': [
                    'Conserva sempre backup in almeno due posizioni fisiche diverse (PC locale, disco esterno, cloud).',
                    'Dopo aggiornamenti del software, esegui sempre un backup prima di utilizzare la nuova versione.',
                    'Implementa una strategia di rotazione dei backup per avere sempre copie di diverse date disponibili.'
                ]
            }
        ]