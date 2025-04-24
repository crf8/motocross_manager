#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Modulo per la gestione delle statistiche dei piloti nelle gare di motocross.
Questo modulo raccoglie, analizza e visualizza le statistiche relative alle prestazioni
dei piloti nelle diverse competizioni.
"""

import sqlite3
import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import logging

# Configurazione del logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='pilot_statistics.log'
)
logger = logging.getLogger('pilot_statistics')

class PilotStatistics:
    """
    Classe per la gestione delle statistiche dei piloti.
    """
    
    def __init__(self, db_path='motocross.db'):
        """
        Inizializza la classe PilotStatistics.
        
        Args:
            db_path (str): Percorso del database SQLite
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        
        # Creazione della connessione al database
        try:
            self.connect_db()
            logger.info("Connessione al database stabilita con successo")
        except Exception as e:
            logger.error(f"Errore durante la connessione al database: {e}")
            raise
    
    def connect_db(self):
        """
        Stabilisce una connessione al database.
        """
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            logger.error(f"Errore durante la connessione al database: {e}")
            raise
    
    def close_db(self):
        """
        Chiude la connessione al database.
        """
        if self.conn:
            self.conn.close()
            logger.info("Connessione al database chiusa")
    
    def get_pilot_info(self, pilot_id):
        """
        Recupera le informazioni di base di un pilota.
        
        Args:
            pilot_id (int): ID del pilota
            
        Returns:
            dict: Dizionario con le informazioni del pilota
        """
        try:
            query = """
            SELECT *
            FROM pilots
            WHERE id = ?
            """
            self.cursor.execute(query, (pilot_id,))
            pilot_data = self.cursor.fetchone()
            
            if pilot_data:
                columns = [col[0] for col in self.cursor.description]
                pilot_info = dict(zip(columns, pilot_data))
                return pilot_info
            else:
                logger.warning(f"Nessun pilota trovato con ID {pilot_id}")
                return None
        except sqlite3.Error as e:
            logger.error(f"Errore durante il recupero delle informazioni del pilota: {e}")
            return None
    
    def get_pilot_races(self, pilot_id):
        """
        Recupera tutte le gare a cui ha partecipato un pilota.
        
        Args:
            pilot_id (int): ID del pilota
            
        Returns:
            list: Lista di dizionari con le informazioni delle gare
        """
        try:
            query = """
            SELECT r.*
            FROM race_results rr
            JOIN races r ON rr.race_id = r.id
            WHERE rr.pilot_id = ?
            ORDER BY r.date DESC
            """
            self.cursor.execute(query, (pilot_id,))
            races_data = self.cursor.fetchall()
            
            if races_data:
                columns = [col[0] for col in self.cursor.description]
                races = [dict(zip(columns, race)) for race in races_data]
                return races
            else:
                logger.warning(f"Nessuna gara trovata per il pilota con ID {pilot_id}")
                return []
        except sqlite3.Error as e:
            logger.error(f"Errore durante il recupero delle gare del pilota: {e}")
            return []
    
    def get_pilot_results(self, pilot_id):
        """
        Recupera tutti i risultati di un pilota nelle varie gare.
        
        Args:
            pilot_id (int): ID del pilota
            
        Returns:
            list: Lista di dizionari con i risultati del pilota
        """
        try:
            query = """
            SELECT rr.*, r.name as race_name, r.date as race_date
            FROM race_results rr
            JOIN races r ON rr.race_id = r.id
            WHERE rr.pilot_id = ?
            ORDER BY r.date DESC
            """
            self.cursor.execute(query, (pilot_id,))
            results_data = self.cursor.fetchall()
            
            if results_data:
                columns = [col[0] for col in self.cursor.description]
                results = [dict(zip(columns, result)) for result in results_data]
                return results
            else:
                logger.warning(f"Nessun risultato trovato per il pilota con ID {pilot_id}")
                return []
        except sqlite3.Error as e:
            logger.error(f"Errore durante il recupero dei risultati del pilota: {e}")
            return []
    
    def calculate_pilot_statistics(self, pilot_id):
        """
        Calcola le statistiche complete di un pilota.
        
        Args:
            pilot_id (int): ID del pilota
            
        Returns:
            dict: Dizionario con tutte le statistiche del pilota
        """
        try:
            # Recupero dei dati di base del pilota
            pilot_info = self.get_pilot_info(pilot_id)
            if not pilot_info:
                return None
            
            # Recupero dei risultati del pilota
            results = self.get_pilot_results(pilot_id)
            
            # Inizializzazione delle statistiche
            stats = {
                'pilot_id': pilot_id,
                'pilot_name': f"{pilot_info.get('name', '')} {pilot_info.get('surname', '')}",
                'total_races': len(results),
                'wins': 0,
                'podiums': 0,
                'top5': 0,
                'top10': 0,
                'dnf': 0,  # Did Not Finish
                'best_position': float('inf'),
                'worst_position': 0,
                'average_position': 0,
                'total_points': 0,
                'average_points_per_race': 0,
                'best_lap_time': float('inf'),
                'average_lap_time': 0,
                'races_by_category': {},
                'performance_trend': []
            }
            
            # Analisi dei risultati
            total_position = 0
            total_lap_time = 0
            valid_lap_times = 0
            
            for result in results:
                position = result.get('position', 0)
                points = result.get('points', 0)
                lap_time = result.get('best_lap_time')
                category = result.get('category', 'Sconosciuta')
                race_date = result.get('race_date')
                
                # Aggiunta alla lista delle performance per il trend
                if position and race_date:
                    stats['performance_trend'].append({
                        'date': race_date,
                        'position': position,
                        'points': points
                    })
                
                # Conteggio per categoria
                if category:
                    if category not in stats['races_by_category']:
                        stats['races_by_category'][category] = 0
                    stats['races_by_category'][category] += 1
                
                # Aggiornamento delle statistiche
                if position:
                    if position == 1:
                        stats['wins'] += 1
                    if position <= 3:
                        stats['podiums'] += 1
                    if position <= 5:
                        stats['top5'] += 1
                    if position <= 10:
                        stats['top10'] += 1
                    
                    total_position += position
                    
                    if position < stats['best_position']:
                        stats['best_position'] = position
                    
                    if position > stats['worst_position']:
                        stats['worst_position'] = position
                
                # DNF (Did Not Finish)
                if result.get('dnf', 0) == 1:
                    stats['dnf'] += 1
                
                # Punti
                stats['total_points'] += points
                
                # Tempo sul giro
                if lap_time and lap_time > 0:
                    if lap_time < stats['best_lap_time']:
                        stats['best_lap_time'] = lap_time
                    
                    total_lap_time += lap_time
                    valid_lap_times += 1
            
            # Calcolo medie
            if stats['total_races'] > 0:
                stats['average_position'] = total_position / stats['total_races']
                stats['average_points_per_race'] = stats['total_points'] / stats['total_races']
            
            if valid_lap_times > 0:
                stats['average_lap_time'] = total_lap_time / valid_lap_times
            
            # Se non ci sono record per il miglior tempo sul giro, impostiamo a 0
            if stats['best_lap_time'] == float('inf'):
                stats['best_lap_time'] = 0
            
            # Correggiamo il valore della migliore posizione se non è stato aggiornato
            if stats['best_position'] == float('inf'):
                stats['best_position'] = 0
            
            return stats
        
        except Exception as e:
            logger.error(f"Errore durante il calcolo delle statistiche del pilota: {e}")
            return None
    
    def generate_statistics_report(self, pilot_id, output_format='html'):
        """
        Genera un report delle statistiche di un pilota.
        
        Args:
            pilot_id (int): ID del pilota
            output_format (str): Formato di output ('html', 'pdf', 'txt')
            
        Returns:
            str: Percorso del file del report generato
        """
        try:
            stats = self.calculate_pilot_statistics(pilot_id)
            if not stats:
                logger.error(f"Impossibile generare il report per il pilota {pilot_id}: statistiche non disponibili")
                return None
            
            # Creazione directory per i report se non esiste
            reports_dir = 'reports'
            if not os.path.exists(reports_dir):
                os.makedirs(reports_dir)
            
            # Nome del file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{reports_dir}/pilot_{pilot_id}_stats_{timestamp}"
            
            if output_format == 'html':
                # Generazione report HTML
                html_content = self._generate_html_report(stats)
                file_path = f"{filename}.html"
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                logger.info(f"Report HTML generato con successo: {file_path}")
                return file_path
            
            elif output_format == 'txt':
                # Generazione report TXT
                txt_content = self._generate_txt_report(stats)
                file_path = f"{filename}.txt"
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(txt_content)
                
                logger.info(f"Report TXT generato con successo: {file_path}")
                return file_path
            
            else:
                logger.error(f"Formato di output '{output_format}' non supportato")
                return None
        
        except Exception as e:
            logger.error(f"Errore durante la generazione del report: {e}")
            return None
    
    def _generate_html_report(self, stats):
        """
        Genera il contenuto HTML per il report delle statistiche.
        
        Args:
            stats (dict): Statistiche del pilota
            
        Returns:
            str: Contenuto HTML del report
        """
        html = f"""
        <!DOCTYPE html>
        <html lang="it">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Statistiche Pilota - {stats['pilot_name']}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 20px;
                    color: #333;
                }}
                h1, h2, h3 {{
                    color: #2c3e50;
                }}
                .container {{
                    max-width: 1000px;
                    margin: 0 auto;
                    background: #f9f9f9;
                    padding: 20px;
                    border-radius: 5px;
                    box-shadow: 0 0 10px rgba(0,0,0,0.1);
                }}
                .stats-box {{
                    background: white;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    padding: 15px;
                    margin-bottom: 20px;
                }}
                .stat-value {{
                    font-weight: bold;
                    color: #3498db;
                }}
                .stat-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                    gap: 15px;
                }}
                .race-category {{
                    margin-top: 10px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 10px;
                }}
                table, th, td {{
                    border: 1px solid #ddd;
                }}
                th, td {{
                    padding: 8px;
                    text-align: left;
                }}
                th {{
                    background-color: #f2f2f2;
                }}
                footer {{
                    margin-top: 30px;
                    text-align: center;
                    font-size: 0.8em;
                    color: #7f8c8d;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Statistiche Pilota</h1>
                <div class="stats-box">
                    <h2>{stats['pilot_name']}</h2>
                    <p>ID Pilota: <span class="stat-value">{stats['pilot_id']}</span></p>
                    
                    <h3>Statistiche Generali</h3>
                    <div class="stat-grid">
                        <p>Gare totali: <span class="stat-value">{stats['total_races']}</span></p>
                        <p>Vittorie: <span class="stat-value">{stats['wins']}</span></p>
                        <p>Podi: <span class="stat-value">{stats['podiums']}</span></p>
                        <p>Top 5: <span class="stat-value">{stats['top5']}</span></p>
                        <p>Top 10: <span class="stat-value">{stats['top10']}</span></p>
                        <p>DNF: <span class="stat-value">{stats['dnf']}</span></p>
                    </div>
                    
                    <h3>Posizioni e Punti</h3>
                    <div class="stat-grid">
                        <p>Miglior posizione: <span class="stat-value">{stats['best_position']}</span></p>
                        <p>Peggior posizione: <span class="stat-value">{stats['worst_position']}</span></p>
                        <p>Posizione media: <span class="stat-value">{stats['average_position']:.2f}</span></p>
                        <p>Punti totali: <span class="stat-value">{stats['total_points']}</span></p>
                        <p>Media punti per gara: <span class="stat-value">{stats['average_points_per_race']:.2f}</span></p>
                    </div>
                    
                    <h3>Tempi sul Giro</h3>
                    <div class="stat-grid">
                        <p>Miglior tempo sul giro: <span class="stat-value">{stats['best_lap_time'] if stats['best_lap_time'] > 0 else 'N/A'}</span></p>
                        <p>Tempo medio sul giro: <span class="stat-value">{stats['average_lap_time']:.2f if stats['average_lap_time'] > 0 else 'N/A'}</span></p>
                    </div>
                    
                    <h3>Gare per Categoria</h3>
                    <div class="race-category">
        """
        
        # Aggiunta delle categorie
        for category, count in stats['races_by_category'].items():
            html += f"""
                        <p>{category}: <span class="stat-value">{count}</span></p>
            """
        
        html += """
                    </div>
                    
                    <h3>Andamento delle Performance</h3>
                    <table>
                        <tr>
                            <th>Data</th>
                            <th>Posizione</th>
                            <th>Punti</th>
                        </tr>
        """
        
        # Aggiunta delle performance
        for perf in stats['performance_trend']:
            html += f"""
                        <tr>
                            <td>{perf['date']}</td>
                            <td>{perf['position']}</td>
                            <td>{perf['points']}</td>
                        </tr>
            """
        
        html += """
                    </table>
                </div>
                <footer>
                    Report generato automaticamente dal sistema di gestione gare motocross.
                    <br>
                    Data generazione: """ + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + """
                </footer>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _generate_txt_report(self, stats):
        """
        Genera il contenuto TXT per il report delle statistiche.
        
        Args:
            stats (dict): Statistiche del pilota
            
        Returns:
            str: Contenuto TXT del report
        """
        txt = f"""
STATISTICHE PILOTA
==========================================
Nome: {stats['pilot_name']}
ID Pilota: {stats['pilot_id']}

STATISTICHE GENERALI
------------------------------------------
Gare totali: {stats['total_races']}
Vittorie: {stats['wins']}
Podi: {stats['podiums']}
Top 5: {stats['top5']}
Top 10: {stats['top10']}
DNF: {stats['dnf']}

POSIZIONI E PUNTI
------------------------------------------
Miglior posizione: {stats['best_position']}
Peggior posizione: {stats['worst_position']}
Posizione media: {stats['average_position']:.2f}
Punti totali: {stats['total_points']}
Media punti per gara: {stats['average_points_per_race']:.2f}

TEMPI SUL GIRO
------------------------------------------
Miglior tempo sul giro: {stats['best_lap_time'] if stats['best_lap_time'] > 0 else 'N/A'}
Tempo medio sul giro: {stats['average_lap_time']:.2f if stats['average_lap_time'] > 0 else 'N/A'}

GARE PER CATEGORIA
------------------------------------------
"""
        
        # Aggiunta delle categorie
        for category, count in stats['races_by_category'].items():
            txt += f"{category}: {count}\n"
        
        txt += """
ANDAMENTO DELLE PERFORMANCE
------------------------------------------
Data                  Posizione    Punti
"""
        
        # Aggiunta delle performance
        for perf in stats['performance_trend']:
            txt += f"{perf['date']:<20} {perf['position']:<12} {perf['points']}\n"
        
        txt += f"""
==========================================
Report generato automaticamente dal sistema di gestione gare motocross.
Data generazione: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
"""
        
        return txt
    
    def visualize_pilot_performance(self, pilot_id, chart_type='position_trend'):
        """
        Crea visualizzazioni grafiche delle performance del pilota.
        
        Args:
            pilot_id (int): ID del pilota
            chart_type (str): Tipo di grafico ('position_trend', 'points_trend', 'category_distribution')
            
        Returns:
            str: Percorso del file dell'immagine generata
        """
        try:
            stats = self.calculate_pilot_statistics(pilot_id)
            if not stats:
                logger.error(f"Impossibile creare visualizzazioni per il pilota {pilot_id}: statistiche non disponibili")
                return None
            
            # Creazione directory per i grafici se non esiste
            charts_dir = 'charts'
            if not os.path.exists(charts_dir):
                os.makedirs(charts_dir)
            
            # Nome del file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{charts_dir}/pilot_{pilot_id}_{chart_type}_{timestamp}.png"
            
            plt.figure(figsize=(10, 6))
            
            if chart_type == 'position_trend':
                # Grafico dell'andamento delle posizioni
                if not stats['performance_trend']:
                    logger.warning(f"Nessun dato disponibile per il grafico position_trend del pilota {pilot_id}")
                    return None
                
                # Convertiamo le date in oggetti datetime e ordiniamole
                dates = [datetime.strptime(perf['date'], "%Y-%m-%d") if isinstance(perf['date'], str) else perf['date'] 
                         for perf in stats['performance_trend']]
                positions = [perf['position'] for perf in stats['performance_trend']]
                
                # Ordiniamo i dati per data
                data = sorted(zip(dates, positions))
                dates = [d[0] for d in data]
                positions = [d[1] for d in data]
                
                plt.plot(dates, positions, marker='o', linestyle='-', color='b')
                plt.gca().invert_yaxis()  # Invertiamo l'asse y per avere la posizione 1 in alto
                plt.title(f"Andamento delle posizioni - {stats['pilot_name']}")
                plt.xlabel("Data")
                plt.ylabel("Posizione")
                plt.grid(True)
                plt.xticks(rotation=45)
                plt.tight_layout()
                
            elif chart_type == 'points_trend':
                # Grafico dell'andamento dei punti
                if not stats['performance_trend']:
                    logger.warning(f"Nessun dato disponibile per il grafico points_trend del pilota {pilot_id}")
                    return None
                
                # Convertiamo le date in oggetti datetime e ordiniamole
                dates = [datetime.strptime(perf['date'], "%Y-%m-%d") if isinstance(perf['date'], str) else perf['date'] 
                         for perf in stats['performance_trend']]
                points = [perf['points'] for perf in stats['performance_trend']]
                
                # Ordiniamo i dati per data
                data = sorted(zip(dates, points))
                dates = [d[0] for d in data]
                points = [d[1] for d in data]
                
                plt.plot(dates, points, marker='o', linestyle='-', color='g')
                plt.title(f"Andamento dei punti - {stats['pilot_name']}")
                plt.xlabel("Data")
                plt.ylabel("Punti")
                plt.grid(True)
                plt.xticks(rotation=45)
                plt.tight_layout()
                
            elif chart_type == 'category_distribution':
                # Grafico della distribuzione delle gare per categoria
                if not stats['races_by_category']:
                    logger.warning(f"Nessun dato disponibile per il grafico category_distribution del pilota {pilot_id}")
                    return None
                
                categories = list(stats['races_by_category'].keys())
                counts = list(stats['races_by_category'].values())
                
                plt.bar(categories, counts, color='skyblue')
                plt.title(f"Distribuzione delle gare per categoria - {stats['pilot_name']}")
                plt.xlabel("Categoria")
                plt.ylabel("Numero di gare")
                plt.xticks(rotation=45)
                plt.tight_layout()
                
            else:
                logger.error(f"Tipo di grafico '{chart_type}' non supportato")
                return None
            
            plt.savefig(filename)
            plt.close()
            
            logger.info(f"Grafico '{chart_type}' generato con successo: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Errore durante la creazione della visualizzazione: {e}")
            return None
    
    def compare_pilots(self, pilot_ids):
        """
        Confronta le statistiche di due o più piloti.
        
        Args:
            pilot_ids (list): Lista di ID dei piloti da confrontare
            
        Returns:
            dict: Dizionario con i dati di confronto
        """
        try:
            if len(pilot_ids) < 2:
                logger.error("È necessario specificare almeno due ID pilota per il confronto")
                return None
            
            # Recupero statistiche di ogni pilota
            pilots_stats = {}
            for pilot_id in pilot_ids:
                stats = self.calculate_pilot_statistics(pilot_id)
                if stats:
                    pilots_stats[pilot_id] = stats
            
            if len(pilots_stats) < 2:
                logger.error("Impossibile recuperare statistiche sufficienti per il confronto")
                return None
            
            # Preparazione del confronto
            comparison = {
                'pilots': pilots_stats,
                'comparison_metrics': {
                    'wins': {},
                    'podiums': {},
                    'top5': {},
                    'best_position': {},
                    'average_position': {},
                    'total_points': {},
                    'average_points_per_race': {},
                    'best_lap_time': {}
                }
            }
            
            # Calcolo metriche di confronto
            for metric in comparison['comparison_metrics'].keys():
                for pilot_id, stats in pilots_stats.items():
                    comparison['comparison_metrics'][metric][pilot_id] = stats.get(metric, 0)
            
            return comparison
        
        except Exception as e:
            logger.error(f"Errore durante il confronto dei piloti: {e}")
            return None
    
    def generate_comparison_chart(self, pilot_ids, metric='average_points_per_race'):
        """
        Genera un grafico di confronto tra piloti basato su una metrica specifica.
        
        Args:
            pilot_ids (list): Lista di ID dei piloti da confrontare
            metric (str): Metrica da utilizzare per il confronto
            
        Returns:
            str: Percorso del file dell'immagine generata
        """
        try:
            comparison = self.compare_pilots(pilot_ids)
            if not comparison:
                return None
            
            # Creazione directory per i grafici se non esiste
            charts_dir = 'charts'
            if not os.path.exists(charts_dir):
                os.makedirs(charts_dir)
            
            # Nome del file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pilot_ids_str = '_'.join(map(str, pilot_ids))
            filename = f"{charts_dir}/comparison_{metric}_{pilot_ids_str}_{timestamp}.png"
            
            # Preparazione dati per il grafico
            pilot_names = [f"{stats['pilot_name']}" for pilot_id, stats in comparison['pilots'].items()]
            metric_values = [comparison['comparison_metrics'][metric].get(pilot_id, 0) for pilot_id in pilot_ids]
            
            # Creazione grafico
            plt.figure(figsize=(10, 6))
            bars = plt.bar(pilot_names, metric_values, color='skyblue')
            
            # Aggiunta valori sopra le barre
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                        f'{height:.2f}' if isinstance(height, float) else str(height),
                        ha='center', va='bottom')
            
            plt.title(f"Confronto piloti - {metric.replace('_', ' ').title()}")
            plt.xlabel("Pilota")
            plt.ylabel(metric.replace('_', ' ').title())
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            plt.savefig(filename)
            plt.close()
            
            logger.info(f"Grafico di confronto generato con successo: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Errore durante la generazione del grafico di confronto: {e}")
            return None
    
    def get_season_statistics(self, season_year=None):
        """
        Recupera le statistiche generali di una stagione.
        
        Args:
            season_year (int): Anno della stagione (se None, usa l'anno corrente)
            
        Returns:
            dict: Dizionario con le statistiche della stagione
        """
        try:
            if not season_year:
                season_year = datetime.now().year
            
            # Definizione dell'intervallo della stagione
            start_date = f"{season_year}-01-01"
            end_date = f"{season_year}-12-31"
            
            # Query per recuperare tutte le gare della stagione
            races_query = """
            SELECT *
            FROM races
            WHERE date BETWEEN ? AND ?
            ORDER BY date
            """
            self.cursor.execute(races_query, (start_date, end_date))
            races_data = self.cursor.fetchall()
            
            if not races_data:
                logger.warning(f"Nessuna gara trovata per la stagione {season_year}")
                return None
            
            # Inizializzazione delle statistiche della stagione
            season_stats = {
                'year': season_year,
                'total_races': len(races_data),
                'total_pilots': 0,
                'races': [],
                'most_successful_pilots': [],
                'category_stats': {},
                'venue_stats': {}
            }
            
            # Elaborazione delle informazioni sulle gare
            race_ids = []
            for race_data in races_data:
                columns = [col[0] for col in self.cursor.description]
                race = dict(zip(columns, race_data))
                race_ids.append(race['id'])
                
                # Aggiunta della gara alla lista
                season_stats['races'].append({
                    'id': race['id'],
                    'name': race['name'],
                    'date': race['date'],
                    'venue': race.get('venue', 'Sconosciuto'),
                    'num_participants': 0  # Sarà aggiornato più tardi
                })
                
                # Statistiche per sede
                venue = race.get('venue', 'Sconosciuto')
                if venue not in season_stats['venue_stats']:
                    season_stats['venue_stats'][venue] = 0
                season_stats['venue_stats'][venue] += 1
            
            # Recupero di tutti i risultati delle gare della stagione
            if race_ids:
                placeholders = ','.join(['?' for _ in race_ids])
                results_query = f"""
                SELECT rr.*, p.name as pilot_name, p.surname as pilot_surname, p.id as pilot_id, r.name as race_name
                FROM race_results rr
                JOIN pilots p ON rr.pilot_id = p.id
                JOIN races r ON rr.race_id = r.id
                WHERE rr.race_id IN ({placeholders})
                """
                self.cursor.execute(results_query, race_ids)
                results_data = self.cursor.fetchall()
                
                # Elaborazione dei risultati
                pilot_points = {}  # ID pilota -> punti totali
                pilots_set = set()  # Set di ID piloti unici
                
                # Aggiorniamo il numero di partecipanti per ogni gara
                race_participants = {}  # ID gara -> numero di partecipanti
                
                for result_data in results_data:
                    columns = [col[0] for col in self.cursor.description]
                    result = dict(zip(columns, result_data))
                    
                    pilot_id = result['pilot_id']
                    race_id = result['race_id']
                    category = result.get('category', 'Sconosciuta')
                    points = result.get('points', 0)
                    
                    # Conteggio partecipanti per gara
                    if race_id not in race_participants:
                        race_participants[race_id] = set()
                    race_participants[race_id].add(pilot_id)
                    
                    # Conteggio piloti unici
                    pilots_set.add(pilot_id)
                    
                    # Somma punti per pilota
                    if pilot_id not in pilot_points:
                        pilot_points[pilot_id] = 0
                    pilot_points[pilot_id] += points
                    
                    # Statistiche per categoria
                    if category not in season_stats['category_stats']:
                        season_stats['category_stats'][category] = 0
                    season_stats['category_stats'][category] += 1
                
                # Aggiorniamo il numero di partecipanti per ogni gara
                for race in season_stats['races']:
                    if race['id'] in race_participants:
                        race['num_participants'] = len(race_participants[race['id']])
                
                # Impostazione del numero totale di piloti
                season_stats['total_pilots'] = len(pilots_set)
                
                # Calcolo dei piloti con più punti
                sorted_pilots = sorted(pilot_points.items(), key=lambda x: x[1], reverse=True)
                
                # Recupero delle informazioni dei primi 10 piloti
                top_pilots = []
                for pilot_id, points in sorted_pilots[:10]:  # Prendiamo i primi 10
                    # Recupero info del pilota
                    pilot_query = "SELECT name, surname FROM pilots WHERE id = ?"
                    self.cursor.execute(pilot_query, (pilot_id,))
                    pilot_data = self.cursor.fetchone()
                    
                    if pilot_data:
                        pilot_name = f"{pilot_data[0]} {pilot_data[1]}"
                        top_pilots.append({
                            'id': pilot_id,
                            'name': pilot_name,
                            'points': points
                        })
                
                season_stats['most_successful_pilots'] = top_pilots
            
            return season_stats
        
        except Exception as e:
            logger.error(f"Errore durante il recupero delle statistiche della stagione: {e}")
            return None
    
    def generate_season_report(self, season_year=None, output_format='html'):
        """
        Genera un report delle statistiche di una stagione.
        
        Args:
            season_year (int): Anno della stagione (se None, usa l'anno corrente)
            output_format (str): Formato di output ('html', 'txt')
            
        Returns:
            str: Percorso del file del report generato
        """
        try:
            stats = self.get_season_statistics(season_year)
            if not stats:
                logger.error(f"Impossibile generare il report per la stagione {season_year}: statistiche non disponibili")
                return None
            
            # Creazione directory per i report se non esiste
            reports_dir = 'reports'
            if not os.path.exists(reports_dir):
                os.makedirs(reports_dir)
            
            # Nome del file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{reports_dir}/season_{stats['year']}_report_{timestamp}"
            
            if output_format == 'html':
                # Generazione report HTML
                html_content = self._generate_season_html_report(stats)
                file_path = f"{filename}.html"
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                logger.info(f"Report HTML della stagione generato con successo: {file_path}")
                return file_path
            
            elif output_format == 'txt':
                # Generazione report TXT
                txt_content = self._generate_season_txt_report(stats)
                file_path = f"{filename}.txt"
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(txt_content)
                
                logger.info(f"Report TXT della stagione generato con successo: {file_path}")
                return file_path
            
            else:
                logger.error(f"Formato di output '{output_format}' non supportato")
                return None
        
        except Exception as e:
            logger.error(f"Errore durante la generazione del report della stagione: {e}")
            return None
    
    def _generate_season_html_report(self, stats):
        """
        Genera il contenuto HTML per il report delle statistiche della stagione.
        
        Args:
            stats (dict): Statistiche della stagione
            
        Returns:
            str: Contenuto HTML del report
        """
        html = f"""
        <!DOCTYPE html>
        <html lang="it">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Statistiche Stagione {stats['year']}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 20px;
                    color: #333;
                }}
                h1, h2, h3 {{
                    color: #2c3e50;
                }}
                .container {{
                    max-width: 1000px;
                    margin: 0 auto;
                    background: #f9f9f9;
                    padding: 20px;
                    border-radius: 5px;
                    box-shadow: 0 0 10px rgba(0,0,0,0.1);
                }}
                .stats-box {{
                    background: white;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    padding: 15px;
                    margin-bottom: 20px;
                }}
                .stat-value {{
                    font-weight: bold;
                    color: #3498db;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 10px;
                }}
                table, th, td {{
                    border: 1px solid #ddd;
                }}
                th, td {{
                    padding: 8px;
                    text-align: left;
                }}
                th {{
                    background-color: #f2f2f2;
                }}
                footer {{
                    margin-top: 30px;
                    text-align: center;
                    font-size: 0.8em;
                    color: #7f8c8d;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Statistiche Stagione {stats['year']}</h1>
                <div class="stats-box">
                    <h2>Panoramica Generale</h2>
                    <p>Gare totali: <span class="stat-value">{stats['total_races']}</span></p>
                    <p>Piloti totali: <span class="stat-value">{stats['total_pilots']}</span></p>
                    
                    <h3>Classifica Piloti</h3>
                    <table>
                        <tr>
                            <th>Posizione</th>
                            <th>Pilota</th>
                            <th>Punti</th>
                        </tr>
        """
        
        # Aggiunta dei piloti di maggior successo
        for i, pilot in enumerate(stats['most_successful_pilots']):
            html += f"""
                        <tr>
                            <td>{i+1}</td>
                            <td>{pilot['name']}</td>
                            <td>{pilot['points']}</td>
                        </tr>
            """
        
        html += """
                    </table>
                    
                    <h3>Gare della Stagione</h3>
                    <table>
                        <tr>
                            <th>Data</th>
                            <th>Nome</th>
                            <th>Sede</th>
                            <th>Partecipanti</th>
                        </tr>
        """
        
        # Aggiunta delle gare
        for race in stats['races']:
            html += f"""
                        <tr>
                            <td>{race['date']}</td>
                            <td>{race['name']}</td>
                            <td>{race['venue']}</td>
                            <td>{race['num_participants']}</td>
                        </tr>
            """
        
        html += """
                    </table>
                    
                    <h3>Statistiche per Categoria</h3>
                    <table>
                        <tr>
                            <th>Categoria</th>
                            <th>Numero di Gare</th>
                        </tr>
        """
        
        # Aggiunta delle categorie
        for category, count in stats['category_stats'].items():
            html += f"""
                        <tr>
                            <td>{category}</td>
                            <td>{count}</td>
                        </tr>
            """
        
        html += """
                    </table>
                    
                    <h3>Statistiche per Sede</h3>
                    <table>
                        <tr>
                            <th>Sede</th>
                            <th>Numero di Gare</th>
                        </tr>
        """
        
        # Aggiunta delle sedi
        for venue, count in stats['venue_stats'].items():
            html += f"""
                        <tr>
                            <td>{venue}</td>
                            <td>{count}</td>
                        </tr>
            """
        
        html += f"""
                    </table>
                </div>
                <footer>
                    Report generato automaticamente dal sistema di gestione gare motocross.
                    <br>
                    Data generazione: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
                </footer>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _generate_season_txt_report(self, stats):
        """
        Genera il contenuto TXT per il report delle statistiche della stagione.
        
        Args:
            stats (dict): Statistiche della stagione
            
        Returns:
            str: Contenuto TXT del report
        """
        txt = f"""
STATISTICHE STAGIONE {stats['year']}
==========================================

PANORAMICA GENERALE
------------------------------------------
Gare totali: {stats['total_races']}
Piloti totali: {stats['total_pilots']}

CLASSIFICA PILOTI
------------------------------------------
"""
        
        # Aggiunta dei piloti di maggior successo
        for i, pilot in enumerate(stats['most_successful_pilots']):
            txt += f"{i+1}. {pilot['name']} - {pilot['points']} punti\n"
        
        txt += """
GARE DELLA STAGIONE
------------------------------------------
Data                  Nome                  Sede                  Partecipanti
"""
        
        # Aggiunta delle gare
        for race in stats['races']:
            txt += f"{race['date']:<20} {race['name']:<20} {race['venue']:<20} {race['num_participants']}\n"
        
        txt += """
STATISTICHE PER CATEGORIA
------------------------------------------
Categoria             Numero di Gare
"""
        
        # Aggiunta delle categorie
        for category, count in stats['category_stats'].items():
            txt += f"{category:<20} {count}\n"
        
        txt += """
STATISTICHE PER SEDE
------------------------------------------
Sede                  Numero di Gare
"""
        
        # Aggiunta delle sedi
        for venue, count in stats['venue_stats'].items():
            txt += f"{venue:<20} {count}\n"
        
        txt += f"""
==========================================
Report generato automaticamente dal sistema di gestione gare motocross.
Data generazione: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
"""
        
        return txt

    def export_pilot_statistics_to_csv(self, pilot_id):
        """
        Esporta le statistiche di un pilota in formato CSV.
        
        Args:
            pilot_id (int): ID del pilota
            
        Returns:
            str: Percorso del file CSV generato
        """
        try:
            stats = self.calculate_pilot_statistics(pilot_id)
            if not stats:
                logger.error(f"Impossibile esportare statistiche per il pilota {pilot_id}: dati non disponibili")
                return None
            
            # Creazione directory per i CSV se non esiste
            csv_dir = 'exports'
            if not os.path.exists(csv_dir):
                os.makedirs(csv_dir)
            
            # Nome del file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{csv_dir}/pilot_{pilot_id}_stats_{timestamp}.csv"
            
            # Creazione del DataFrame
            main_stats = {
                'ID Pilota': stats['pilot_id'],
                'Nome': stats['pilot_name'],
                'Gare Totali': stats['total_races'],
                'Vittorie': stats['wins'],
                'Podi': stats['podiums'],
                'Top 5': stats['top5'],
                'Top 10': stats['top10'],
                'DNF': stats['dnf'],
                'Miglior Posizione': stats['best_position'],
                'Peggior Posizione': stats['worst_position'],
                'Posizione Media': stats['average_position'],
                'Punti Totali': stats['total_points'],
                'Media Punti per Gara': stats['average_points_per_race'],
                'Miglior Tempo sul Giro': stats['best_lap_time'],
                'Tempo Medio sul Giro': stats['average_lap_time']
            }
            
            # Dataframe delle statistiche principali
            df_main = pd.DataFrame([main_stats])
            
            # Dataframe delle performance
            df_performances = pd.DataFrame(stats['performance_trend'])
            
            # Esportazione CSV delle statistiche principali
            df_main.to_csv(filename, index=False)
            
            # Esportazione CSV delle performance
            perf_filename = f"{csv_dir}/pilot_{pilot_id}_performances_{timestamp}.csv"
            df_performances.to_csv(perf_filename, index=False)
            
            logger.info(f"Statistiche del pilota esportate con successo: {filename}, {perf_filename}")
            return filename
        
        except Exception as e:
            logger.error(f"Errore durante l'esportazione delle statistiche in CSV: {e}")
            return None
    
    def analyze_pilot_improvement(self, pilot_id, start_date=None, end_date=None):
        """
        Analizza il miglioramento del pilota in un determinato periodo.
        
        Args:
            pilot_id (int): ID del pilota
            start_date (str): Data di inizio in formato YYYY-MM-DD
            end_date (str): Data di fine in formato YYYY-MM-DD
            
        Returns:
            dict: Dizionario con le statistiche di miglioramento
        """
        try:
            # Se non vengono fornite date, prendi l'intero periodo disponibile
            if not end_date:
                end_date = datetime.now().strftime("%Y-%m-%d")
            
            # Recupera i risultati del pilota nel periodo specificato
            query = """
            SELECT rr.*, r.name as race_name, r.date as race_date
            FROM race_results rr
            JOIN races r ON rr.race_id = r.id
            WHERE rr.pilot_id = ? AND (? IS NULL OR r.date >= ?) AND r.date <= ?
            ORDER BY r.date
            """
            self.cursor.execute(query, (pilot_id, start_date, start_date, end_date))
            results_data = self.cursor.fetchall()
            
            if not results_data:
                logger.warning(f"Nessun risultato trovato per il pilota {pilot_id} nel periodo specificato")
                return None
            
            columns = [col[0] for col in self.cursor.description]
            results = [dict(zip(columns, result)) for result in results_data]
            
            # Inizializzazione delle statistiche di miglioramento
            improvement_stats = {
                'pilot_id': pilot_id,
                'start_date': start_date if start_date else results[0]['race_date'],
                'end_date': end_date,
                'num_races': len(results),
                'position_trend': [],
                'points_trend': [],
                'lap_time_trend': [],
                'first_position': None,
                'last_position': None,
                'position_improvement': None,
                'first_points': None,
                'last_points': None,
                'points_improvement': None,
                'first_lap_time': None,
                'last_lap_time': None,
                'lap_time_improvement': None
            }
            
            # Analisi dei risultati
            valid_positions = []
            valid_points = []
            valid_lap_times = []
            
            for result in results:
                race_date = result['race_date']
                position = result.get('position')
                points = result.get('points', 0)
                lap_time = result.get('best_lap_time')
                
                # Raccolta dei dati di trend
                if position:
                    improvement_stats['position_trend'].append({
                        'date': race_date,
                        'value': position
                    })
                    valid_positions.append(position)
                
                improvement_stats['points_trend'].append({
                    'date': race_date,
                    'value': points
                })
                valid_points.append(points)
                
                if lap_time and lap_time > 0:
                    improvement_stats['lap_time_trend'].append({
                        'date': race_date,
                        'value': lap_time
                    })
                    valid_lap_times.append(lap_time)
            
            # Calcolo dei miglioramenti
            if valid_positions:
                improvement_stats['first_position'] = valid_positions[0]
                improvement_stats['last_position'] = valid_positions[-1]
                improvement_stats['position_improvement'] = improvement_stats['first_position'] - improvement_stats['last_position']
            
            if valid_points:
                improvement_stats['first_points'] = valid_points[0]
                improvement_stats['last_points'] = valid_points[-1]
                improvement_stats['points_improvement'] = improvement_stats['last_points'] - improvement_stats['first_points']
            
            if valid_lap_times:
                improvement_stats['first_lap_time'] = valid_lap_times[0]
                improvement_stats['last_lap_time'] = valid_lap_times[-1]
                improvement_stats['lap_time_improvement'] = improvement_stats['first_lap_time'] - improvement_stats['last_lap_time']
            
            return improvement_stats
        
        except Exception as e:
            logger.error(f"Errore durante l'analisi del miglioramento del pilota: {e}")
            return None