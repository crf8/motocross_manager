        # Grafico confronto con media categoria
        ax2 = self.category_comparison_chart.figure.subplots()
        
        # Per semplicità, generiamo alcuni dati di confronto
        # In una implementazione reale, questi dati verrebbero dal database
        
        # Circuiti in cui il pilota ha corso
        circuits = list(set([eventi_tempi[e]['circuito'] for e in events_list]))
        
        # Tempi migliori del pilota su questi circuiti
        pilot_best_times = []
        category_avg_times = []
        
        for circuit in circuits:
            # Trova il miglior tempo del pilota su questo circuito
            pilot_best = float('inf')
            for event in events_list:
                if eventi_tempi[event]['circuito'] == circuit:
                    for session_type, laps in eventi_tempi[event]['sessioni'].items():
                        valid_times = [lap['tempo_ms'] for lap in laps if lap['tempo_ms'] > 0]
                        if valid_times:
                            circuit_best = min(valid_times)
                            if circuit_best < pilot_best:
                                pilot_best = circuit_best
            
            if pilot_best < float('inf'):
                pilot_best_times.append(pilot_best / 1000)  # Converti in secondi
                
                # Genera un tempo medio di categoria (simulato)
                # In una implementazione reale, questo verrebbe calcolato dalle statistiche
                import random
                category_avg = pilot_best / 1000 * random.uniform(0.95, 1.05)
                category_avg_times.append(category_avg)
            else:
                continue  # Skip this circuit if no valid time
        
        # Crea il grafico a barre
        if pilot_best_times and len(circuits) == len(pilot_best_times):
            x = range(len(circuits))
            width = 0.35
            
            ax2.bar([i - width/2 for i in x], pilot_best_times, width, label=f'{pilota.nome} {pilota.cognome}', color='blue')
            ax2.bar([i + width/2 for i in x], category_avg_times, width, label='Media Categoria', color='orange')
            
            ax2.set_xticks(x)
            ax2.set_xticklabels(circuits, rotation=45, ha='right')
            ax2.set_ylabel('Tempo (secondi)')
            ax2.set_title('Confronto Tempi con Media Categoria')
            ax2.legend()
            
            # Aggiusta layout
            self.category_comparison_chart.figure.tight_layout()
            self.category_comparison_chart.draw()
        
        # Popola la tabella dei tempi
        self.lap_times_table.setRowCount(0)
        
        for event_idx, event in enumerate(events_list):
            event_data = eventi_tempi[event]
            
            # Migliori tempi per ogni sessione
            best_times = {}
            avg_times = {}
            
            for session, laps in event_data['sessioni'].items():
                valid_times = [lap['tempo_ms'] for lap in laps if lap['tempo_ms'] > 0]
                if valid_times:
                    best_times[session] = min(valid_times)
                    avg_times[session] = sum(valid_times) / len(valid_times)
            
            # Trova il miglior tempo tra tutte le sessioni
            if best_times:
                best_overall = min(best_times.values())
                
                # Formatta i tempi
                mins = int(best_overall // 60000)
                secs = int((best_overall % 60000) // 1000)
                msecs = int(best_overall % 1000)
                best_time_text = f"{mins:01d}:{secs:02d}.{msecs:03d}"
                
                # Calcola la media dei tempi medi
                if avg_times:
                    avg_overall = sum(avg_times.values()) / len(avg_times)
                    mins = int(avg_overall // 60000)
                    secs = int((avg_overall % 60000) // 1000)
                    msecs = int(avg_overall % 1000)
                    avg_time_text = f"{mins:01d}:{secs:02d}.{msecs:03d}"
                else:
                    avg_time_text = "-"
                
                # Differenza con media categoria (simulata)
                if event_idx < len(category_avg_times):
                    cat_avg_sec = category_avg_times[event_idx]
                    best_sec = best_overall / 1000
                    diff_sec = best_sec - cat_avg_sec
                    diff_text = f"{diff_sec:+.3f}s"
                else:
                    diff_text = "-"
                
                # Aggiungi alla tabella
                row = self.lap_times_table.rowCount()
                self.lap_times_table.insertRow(row)
                
                self.lap_times_table.setItem(row, 0, QTableWidgetItem(event))
                self.lap_times_table.setItem(row, 1, QTableWidgetItem(event_data['circuito']))
                self.lap_times_table.setItem(row, 2, QTableWidgetItem(event_data['data'].strftime("%d/%m/%Y")))
                self.lap_times_table.setItem(row, 3, QTableWidgetItem(best_time_text))
                self.lap_times_table.setItem(row, 4, QTableWidgetItem(avg_time_text))
                self.lap_times_table.setItem(row, 5, QTableWidgetItem(diff_text))
                
                # Colora la riga in base alla differenza
                if diff_text != "-":
                    if diff_sec < -0.5:  # Meglio della media
                        color = QColor(200, 255, 200)  # Verde chiaro
                    elif diff_sec > 0.5:  # Peggio della media
                        color = QColor(255, 200, 200)  # Rosso chiaro
                    else:
                        color = QColor(255, 255, 200)  # Giallo chiaro
                    
                    for col in range(self.lap_times_table.columnCount()):
                        item = self.lap_times_table.item(row, col)
                        if item:
                            item.setBackground(color)
        
        # Ridimensiona colonne
        self.lap_times_table.resizeColumnsToContents()
    
    def _update_races_tab(self, db, pilota, eventi_ordinati):
        """Aggiorna la tab Dettaglio Gare con i dati del pilota"""
        # Svuota la tabella
        self.races_table.setRowCount(0)
        
        # Popola la tabella con i dati degli eventi
        for event_name, event_data in eventi_ordinati:
            row = self.races_table.rowCount()
            self.races_table.insertRow(row)
            
            # Estrai i dati dell'evento
            evento_nome = event_data['nome']
            data = event_data['data'].strftime("%d/%m/%Y")
            circuito = event_data['circuito']
            
            # Posizioni e gruppo
            qual_pos = event_data.get('posizione_qual', '-')
            race1_pos = event_data.get('posizione_gara1', '-')
            race2_pos = event_data.get('posizione_gara2', '-')
            gruppo = "Gruppo A"  # Default, da sostituire con dati reali
            punti = event_data.get('punti', 0)
            note = ""
            
            # Popola la riga
            self.races_table.setItem(row, 0, QTableWidgetItem(evento_nome))
            self.races_table.setItem(row, 1, QTableWidgetItem(data))
            self.races_table.setItem(row, 2, QTableWidgetItem(circuito))
            self.races_table.setItem(row, 3, QTableWidgetItem(gruppo))
            self.races_table.setItem(row, 4, QTableWidgetItem(str(qual_pos) if qual_pos != '-' else '-'))
            self.races_table.setItem(row, 5, QTableWidgetItem(str(race1_pos) if race1_pos != '-' else '-'))
            self.races_table.setItem(row, 6, QTableWidgetItem(str(race2_pos) if race2_pos != '-' else '-'))
            self.races_table.setItem(row, 7, QTableWidgetItem(str(punti)))
            self.races_table.setItem(row, 8, QTableWidgetItem(note))
            
            # Colora le celle delle posizioni
            for col, pos in [(4, qual_pos), (5, race1_pos), (6, race2_pos)]:
                if pos != '-' and pos is not None:
                    item = self.races_table.item(row, col)
                    if pos <= 3:
                        color = QColor(200, 255, 200)  # Verde per podio
                    elif pos <= 10:
                        color = QColor(255, 255, 200)  # Giallo per top 10
                    item.setBackground(color)
        
        # Ridimensiona colonne
        self.races_table.resizeColumnsToContents()
        
        # Seleziona la prima riga se presente
        if self.races_table.rowCount() > 0:
            self.races_table.selectRow(0)
            self.update_race_details()
    
    def update_race_details(self):
        """Aggiorna i dettagli della gara selezionata"""
        selected_rows = self.races_table.selectedItems()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        
        # Estrai i dati dalla tabella
        evento = self.races_table.item(row, 0).text()
        data = self.races_table.item(row, 1).text()
        circuito = self.races_table.item(row, 2).text()
        gruppo = self.races_table.item(row, 3).text()
        qual_pos = self.races_table.item(row, 4).text()
        race1_pos = self.races_table.item(row, 5).text()
        race2_pos = self.races_table.item(row, 6).text()
        punti = self.races_table.item(row, 7).text()
        
        # Aggiorna i campi dei dettagli
        self.race_detail_event.setText(evento)
        self.race_detail_date.setText(data)
        self.race_detail_circuit.setText(circuito)
        
        # Dati simulati aggiuntivi
        import random
        meteo = random.choice(["Soleggiato", "Nuvoloso", "Pioggia leggera", "Umido", "Caldo", "Asciutto"])
        self.race_detail_weather.setText(meteo)
        
        partecipanti = random.randint(20, 40)
        self.race_detail_participants.setText(str(partecipanti))
        
        # Dettagli qualifiche
        self.qual_position.setText(qual_pos)
        
        if qual_pos != '-':
            tempo_qual = f"1:{random.randint(30, 59)}.{random.randint(0, 999):03d}"
            distacco_qual = f"+{random.uniform(0, 5):.3f}s" if int(qual_pos) > 1 else "-"
        else:
            tempo_qual = "-"
            distacco_qual = "-"
        
        self.qual_best_time.setText(tempo_qual)
        self.qual_gap.setText(distacco_qual)
        self.qual_group.setText(gruppo)
        
        # Dettagli gare
        self.race1_position.setText(race1_pos)
        self.race2_position.setText(race2_pos)
        
        if race1_pos != '-':
            distacco_race1 = f"+{random.uniform(0, 30):.3f}s" if int(race1_pos) > 1 else "-"
        else:
            distacco_race1 = "-"
        
        if race2_pos != '-':
            distacco_race2 = f"+{random.uniform(0, 30):.3f}s" if int(race2_pos) > 1 else "-"
        else:
            distacco_race2 = "-"
        
        self.race1_gap.setText(distacco_race1)
        self.race2_gap.setText(distacco_race2)
        self.total_points.setText(punti)
        
        # Note
        note_options = [
            "",
            "Ottima prestazione con partenza aggressiva.",
            "Difficoltà in partenza, buon recupero.",
            "Caduta durante il primo giro.",
            "Problemi meccanici.",
            "Penalità di 3 posizioni per taglio percorso.",
            "Miglior tempo sul giro della categoria.",
            "Ritiro per problemi tecnici."
        ]
        
        note = random.choice(note_options)
        self.race_notes.setText(note)
    
    def _update_penalties_tab(self, db, pilota):
        """Aggiorna la tab Penalità con i dati del pilota"""
        # Query per ottenere le penalità
        penalties_query = """
            SELECT p.data_ora, e.nome as evento_nome, p.sessione_tipo,
                   p.tipo_infrazione, p.posizioni_penalita, p.tempo_penalita,
                   p.esclusione, p.cancella_miglior_tempo, p.descrizione
            FROM penalita p
            JOIN iscrizioni i ON p.iscrizione_id = i.id
            JOIN eventi e ON i.evento_id = e.id
            WHERE i.pilota_id = :pilota_id
            ORDER BY p.data_ora DESC
        """
        
        penalties = db.execute(penalties_query, {"pilota_id": pilota.id}).fetchall()
        
        # Svuota la tabella
        self.penalties_table.setRowCount(0)
        
        # Contatori per le statistiche
        total_penalties = 0
        penalty_types = {}
        points_lost = 0
        
        # Popola la tabella con le penalità
        for penalty in penalties:
            row = self.penalties_table.rowCount()
            self.penalties_table.insertRow(row)
            
            # Estrai i dati della penalità
            data = penalty.data_ora.strftime("%d/%m/%Y")
            evento = penalty.evento_nome
            sessione = penalty.sessione_tipo
            infrazione = penalty.tipo_infrazione
            
            # Determina il tipo di penalità
            if penalty.esclusione:
                penalita = "Esclusione"
                impatto = "Squalifica dalla sessione"
            elif penalty.posizioni_penalita > 0:
                penalita = f"{penalty.posizioni_penalita} posizioni"
                impatto = f"Retrocessione di {penalty.posizioni_penalita} posizioni"
                points_lost += penalty.posizioni_penalita * 5  # Stima: 5 punti per posizione
            elif penalty.tempo_penalita > 0:
                penalita = f"{penalty.tempo_penalita} secondi"
                impatto = f"Penalità di {penalty.tempo_penalita} secondi"
                points_lost += penalty.tempo_penalita * 2  # Stima: 2 punti per secondo
            elif penalty.cancella_miglior_tempo:
                penalita = "Cancellazione miglior tempo"
                impatto = "Perdita del miglior tempo in qualifica"
                points_lost += 10  # Stima: 10 punti
            else:
                penalita = "Altro"
                impatto = "Vedi note"
            
            # Aggiornamento contatori statistiche
            total_penalties += 1
            if infrazione in penalty_types:
                penalty_types[infrazione] += 1
            else:
                penalty_types[infrazione] = 1
            
            # Popola la riga
            self.penalties_table.setItem(row, 0, QTableWidgetItem(data))
            self.penalties_table.setItem(row, 1, QTableWidgetItem(evento))
            self.penalties_table.setItem(row, 2, QTableWidgetItem(sessione))
            self.penalties_table.setItem(row, 3, QTableWidgetItem(infrazione))
            self.penalties_table.setItem(row, 4, QTableWidgetItem(penalita))
            self.penalties_table.setItem(row, 5, QTableWidgetItem(impatto))
            self.penalties_table.setItem(row, 6, QTableWidgetItem(penalty.descrizione or ""))
            
            # Colora la riga in base alla gravità
            if penalty.esclusione:
                color = QColor(255, 150, 150)  # Rosso più intenso
            elif penalty.posizioni_penalita > 3 or penalty.tempo_penalita > 10:
                color = QColor(255, 200, 200)  # Rosso chiaro
            else:
                color = QColor(255, 235, 210)  # Arancione chiaro
            
            for col in range(self.penalties_table.columnCount()):
                item = self.penalties_table.item(row, col)
                if item:
                    item.setBackground(color)
        
        # Ridimensiona colonne
        self.penalties_table.resizeColumnsToContents()
        
        # Aggiorna statistiche
        self.total_penalties.setText(str(total_penalties))
        self.penalty_points.setText(str(points_lost))
        
        # Infrazione più comune
        if penalty_types:
            most_common_type = max(penalty_types.items(), key=lambda x: x[1])
            self.most_common.setText(f"{most_common_type[0]} ({most_common_type[1]} volte)")
        else:
            self.most_common.setText("-")
        
        # Tendenza (miglioramento o peggioramento)
        if penalties:
            from datetime import timedelta
            
            # Dividi le penalità in prima e seconda metà temporalmente
            sorted_penalties = sorted(penalties, key=lambda p: p.data_ora)
            mid_point = sorted_penalties[len(sorted_penalties)//2].data_ora
            
            first_half = sum(1 for p in sorted_penalties if p.data_ora < mid_point)
            second_half = len(sorted_penalties) - first_half
            
            if second_half < first_half:
                trend = f"In miglioramento ({first_half} → {second_half})"
            elif second_half > first_half:
                trend = f"In peggioramento ({first_half} → {second_half})"
            else:
                trend = f"Stabile ({first_half} → {second_half})"
                
            self.penalty_trend.setText(trend)
        else:
            self.penalty_trend.setText("-")
        
        # Grafico a torta dei tipi di penalità
        if penalty_types:
            ax = self.penalties_pie_chart.figure.subplots()
            
            labels = list(penalty_types.keys())
            sizes = list(penalty_types.values())
            
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
            
            self.penalties_pie_chart.figure.tight_layout()
            self.penalties_pie_chart.draw()
    
    def compare_with_pilot(self):
        """Confronta il pilota corrente con un altro pilota"""
        pilot1_id = self.pilot_combo.currentData()
        pilot2_id = self.compare_pilot_combo.currentData()
        
        if not pilot1_id or not pilot2_id:
            QMessageBox.warning(self, "Attenzione", "Seleziona entrambi i piloti!")
            return
        
        if pilot1_id == pilot2_id:
            QMessageBox.warning(self, "Attenzione", "Seleziona due piloti diversi!")
            return
        
        try:
            db = SessionLocal()
            
            # Ottieni i dati dei piloti
            pilota1 = db.query(Pilota).get(pilot1_id)
            pilota2 = db.query(Pilota).get(pilot2_id)
            
            if not pilota1 or not pilota2:
                QMessageBox.warning(self, "Attenzione", "Uno o entrambi i piloti non trovati!")
                return
            
            # Query per ottenere i risultati dei due piloti
            query = """
            SELECT e.nome as evento_nome, e.data, e.circuito,
                   i.pilota_id, r.sessione_tipo, r.posizione, r.punti, r.best_lap_time
            FROM risultati r
            JOIN iscrizioni i ON r.iscrizione_id = i.id
            JOIN eventi e ON i.evento_id = e.id
            JOIN gruppi g ON r.gruppo_id = g.id
            WHERE i.pilota_id IN (:pilot1_id, :pilot2_id)
            AND r.sessione_tipo IN ('Gara 1', 'Gara 2')
            ORDER BY e.data, r.sessione_tipo
            """
            
            results = db.execute(query, {"pilot1_id": pilot1_id, "pilot2_id": pilot2_id}).fetchall()
            
            # Se non ci sono risultati, mostra un messaggio
            if not results:
                QMessageBox.warning(self, "Nessun Dato", "Non ci sono dati di gara per confrontare questi piloti!")
                return
            
            # Organizza i dati per pilota
            pilot1_data = {
                "events": [],
                "positions": [],
                "points": [],
                "best_times": [],
                "total_points": 0,
                "wins": 0,
                "podiums": 0,
                "avg_position": 0
            }
            
            pilot2_data = {
                "events": [],
                "positions": [],
                "points": [],
                "best_times": [],
                "total_points": 0,
                "wins": 0,
                "podiums": 0,
                "avg_position": 0
            }
            
            # Eventi in cui entrambi hanno partecipato (per confronto diretto)
            common_events = {}
            
            for result in results:
                if result.pilota_id == pilot1_id:
                    pilot_data = pilot1_data
                else:
                    pilot_data = pilot2_data
                
                # Chiave evento
                event_key = f"{result.evento_nome} - {result.sessione_tipo}"
                
                if event_key not in pilot_data["events"]:
                    pilot_data["events"].append(event_key)
                    
                    if result.posizione:
                        pilot_data["positions"].append(result.posizione)
                        
                        if result.posizione == 1:
                            pilot_data["wins"] += 1
                        if result.posizione <= 3:
                            pilot_data["podiums"] += 1
                    else:
                        pilot_data["positions"].append(None)
                    
                    pilot_data["points"].append(result.punti or 0)
                    pilot_data["total_points"] += result.punti or 0
                    
                    if result.best_lap_time:
                        pilot_data["best_times"].append(result.best_lap_time)
                
                # Traccia gli eventi comuni per il confronto testa a testa
                event_common_key = f"{result.evento_nome} - {result.data.strftime('%d/%m/%Y')} - {result.sessione_tipo}"
                
                if event_common_key not in common_events:
                    common_events[event_common_key] = {
                        "nome": result.evento_nome,
                        "data": result.data,
                        "sessione": result.sessione_tipo
                    }
                
                if result.pilota_id == pilot1_id:
                    common_events[event_common_key]["pos1"] = result.posizione
                else:
                    common_events[event_common_key]["pos2"] = result.posizione
            
            # Calcola media posizioni
            if pilot1_data["positions"]:
                valid_positions = [p for p in pilot1_data["positions"] if p is not None]
                if valid_positions:
                    pilot1_data["avg_position"] = sum(valid_positions) / len(valid_positions)
            
            if pilot2_data["positions"]:
                valid_positions = [p for p in pilot2_data["positions"] if p is not None]
                if valid_positions:
                    pilot2_data["avg_position"] = sum(valid_positions) / len(valid_positions)
            
            # Trova il miglior tempo
            if pilot1_data["best_times"]:
                pilot1_data["best_time"] = min(pilot1_data["best_times"])
            else:
                pilot1_data["best_time"] = None
                
            if pilot2_data["best_times"]:
                pilot2_data["best_time"] = min(pilot2_data["best_times"])
            else:
                pilot2_data["best_time"] = None
            
            # Calcola tempo medio
            if pilot1_data["best_times"]:
                pilot1_data["avg_time"] = sum(pilot1_data["best_times"]) / len(pilot1_data["best_times"])
            else:
                pilot1_data["avg_time"] = None
                
            if pilot2_data["best_times"]:
                pilot2_data["avg_time"] = sum(pilot2_data["best_times"]) / len(pilot2_data["best_times"])
            else:
                pilot2_data["avg_time"] = None
            
            # Conteggio penalità
            penalties_query = """
                SELECT COUNT(*) as count
                FROM penalita p
                JOIN iscrizioni i ON p.iscrizione_id = i.id
                WHERE i.pilota_id = :pilota_id
            """
            
            p1_penalties = db.execute(penalties_query, {"pilota_id": pilot1_id}).fetchone()
            p2_penalties = db.execute(penalties_query, {"pilota_id": pilot2_id}).fetchone()
            
            pilot1_data["penalties"] = p1_penalties[0] if p1_penalties else 0
            pilot2_data["penalties"] = p2_penalties[0] if p2_penalties else 0
            
            # Aggiorna le statistiche di confronto nella UI
            self._update_comparison_statistics(pilota1, pilota2, pilot1_data, pilot2_data)
            
            # Aggiorna i grafici di confronto
            self._update_comparison_charts(pilota1, pilota2, pilot1_data, pilot2_data)
            
            # Aggiorna la tabella di confronto testa a testa
            self._update_head_to_head_table(pilota1, pilota2, common_events)
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante il confronto: {str(e)}")
        finally:
            db.close()
    
    def _update_comparison_statistics(self, pilota1, pilota2, pilot1_data, pilot2_data):
        """Aggiorna le statistiche di confronto nella UI"""
        # Formatta i tempi
        if pilot1_data["best_time"]:
            mins = int(pilot1_data["best_time"] // 60000)
            secs = int((pilot1_data["best_time"] % 60000) // 1000)
            msecs = int(pilot1_data["best_time"] % 1000)
            best_time1 = f"{mins:01d}:{secs:02d}.{msecs:03d}"
        else:
            best_time1 = "-"
            
        if pilot2_data["best_time"]:
            mins = int(pilot2_data["best_time"] // 60000)
            secs = int((pilot2_data["best_time"] % 60000) // 1000)
            msecs = int(pilot2_data["best_time"] % 1000)
            best_time2 = f"{mins:01d}:{secs:02d}.{msecs:03d}"
        else:
            best_time2 = "-"
            
        if pilot1_data["avg_time"]:
            mins = int(pilot1_data["avg_time"] // 60000)
            secs = int((pilot1_data["avg_time"] % 60000) // 1000)
            msecs = int(pilot1_data["avg_time"] % 1000)
            avg_time1 = f"{mins:01d}:{secs:02d}.{msecs:03d}"
        else:
            avg_time1 = "-"
            
        if pilot2_data["avg_time"]:
            mins = int(pilot2_data["avg_time"] // 60000)
            secs = int((pilot2_data["avg_time"] % 60000) // 1000)
            msecs = int(pilot2_data["avg_time"] % 1000)
            avg_time2 = f"{mins:01d}:{secs:02d}.{msecs:03d}"
        else:
            avg_time2 = "-"
        
        # Aggiorna i valori nelle etichette
        points_row = self._add_comparison_row(None, "Punti Totali:", str(pilot1_data["total_points"]), str(pilot2_data["total_points"]))
        pos_row = self._add_comparison_row(None, "Posizione Media:", f"{pilot1_data['avg_position']:.1f}" if pilot1_data["avg_position"] else "-", 
                                         f"{pilot2_data['avg_position']:.1f}" if pilot2_data["avg_position"] else "-")
        wins_row = self._add_comparison_row(None, "Vittorie:", str(pilot1_data["wins"]), str(pilot2_data["wins"]))
        podiums_row = self._add_comparison_row(None, "Podi:", str(pilot1_data["podiums"]), str(pilot2_data["podiums"]))
        best_time_row = self._add_comparison_row(None, "Miglior Tempo:", best_time1, best_time2)
        avg_time_row = self._add_comparison_row(None, "Tempo Medio:", avg_time1, avg_time2)
        penalties_row = self._# ui/pilot_detailed_stats.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLabel, QComboBox, QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QMessageBox, QTabWidget, 
    QSplitter, QFrame, QFileDialog, QGroupBox, QDialog,
    QTextEdit, QDialogButtonBox
)
from PyQt6.QtCore import Qt, QDate, QUrl, QSize
from PyQt6.QtGui import QColor, QPainter, QImage, QPixmap, QFont, QDesktopServices
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
import os
import csv
import tempfile
import webbrowser
from datetime import datetime

from database.connection import SessionLocal
from database.models import Evento, Iscrizione, Pilota, Categoria, Gruppo, PartecipazioneGruppo, LapTime, Risultato, Penalita

class PilotDetailedStatsWidget(QWidget):
    """Widget per visualizzare le statistiche dettagliate di un pilota"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Layout principale
        self.layout = QVBoxLayout(self)
        
        # Titolo
        self.title_label = QLabel("Statistiche Dettagliate Pilota")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.layout.addWidget(self.title_label)
        
        # Selettore pilota
        selector_layout = QHBoxLayout()
        
        self.pilot_label = QLabel("Seleziona Pilota:")
        self.pilot_label.setStyleSheet("font-weight: bold;")
        selector_layout.addWidget(self.pilot_label)
        
        self.pilot_combo = QComboBox()
        self.pilot_combo.setMinimumWidth(300)
        selector_layout.addWidget(self.pilot_combo)
        
        self.season_combo = QComboBox()
        self.season_combo.addItems(["Stagione 2025", "Stagione 2024"])
        selector_layout.addWidget(QLabel("Stagione:"))
        selector_layout.addWidget(self.season_combo)
        
        self.load_button = QPushButton("Carica Statistiche")
        self.load_button.clicked.connect(self.load_statistics)
        selector_layout.addWidget(self.load_button)
        
        selector_layout.addStretch(1)
        
        self.layout.addLayout(selector_layout)
        
        # Header con info pilota
        self.pilot_info_frame = QFrame()
        self.pilot_info_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.pilot_info_frame.setStyleSheet("background-color: #f0f0f0; border-radius: 5px; padding: 10px;")
        
        pilot_info_layout = QHBoxLayout(self.pilot_info_frame)
        
        # Parte sinistra: info pilota
        left_info = QVBoxLayout()
        
        self.pilot_name_label = QLabel("Nome Pilota")
        self.pilot_name_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #003366;")
        left_info.addWidget(self.pilot_name_label)
        
        pilot_details = QFormLayout()
        self.category_label = QLabel("-")
        self.license_label = QLabel("-")
        self.team_label = QLabel("-")
        self.bike_label = QLabel("-")
        
        pilot_details.addRow("Categoria:", self.category_label)
        pilot_details.addRow("Licenza:", self.license_label)
        pilot_details.addRow("Team/Moto Club:", self.team_label)
        pilot_details.addRow("Moto:", self.bike_label)
        
        left_info.addLayout(pilot_details)
        pilot_info_layout.addLayout(left_info)
        
        # Parte destra: statistiche riassuntive
        right_info = QHBoxLayout()
        
        # Box per le statistiche principali
        self.races_box = self._create_stat_box("Gare Disputate", "0")
        self.podiums_box = self._create_stat_box("Podi", "0")
        self.wins_box = self._create_stat_box("Vittorie", "0")
        self.points_box = self._create_stat_box("Punti Totali", "0")
        self.best_pos_box = self._create_stat_box("Miglior Risultato", "-")
        
        right_info.addWidget(self.races_box)
        right_info.addWidget(self.podiums_box)
        right_info.addWidget(self.wins_box)
        right_info.addWidget(self.points_box)
        right_info.addWidget(self.best_pos_box)
        
        pilot_info_layout.addLayout(right_info)
        
        # Nascondi l'header finché non vengono caricati i dati
        self.pilot_info_frame.setVisible(False)
        self.layout.addWidget(self.pilot_info_frame)
        
        # Pulsanti per le azioni
        actions_layout = QHBoxLayout()
        
        self.export_pdf_button = QPushButton("Esporta come PDF")
        self.export_pdf_button.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_FileDialogDetailedView))
        self.export_pdf_button.clicked.connect(self.export_to_pdf)
        self.export_pdf_button.setEnabled(False)
        actions_layout.addWidget(self.export_pdf_button)
        
        self.export_csv_button = QPushButton("Esporta come CSV")
        self.export_csv_button.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_FileDialogDetailedView))
        self.export_csv_button.clicked.connect(self.export_to_csv)
        self.export_csv_button.setEnabled(False)
        actions_layout.addWidget(self.export_csv_button)
        
        self.share_email_button = QPushButton("Condividi via Email")
        self.share_email_button.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_MessageBoxInformation))
        self.share_email_button.clicked.connect(self.share_via_email)
        self.share_email_button.setEnabled(False)
        actions_layout.addWidget(self.share_email_button)
        
        self.share_whatsapp_button = QPushButton("Condividi via WhatsApp")
        self.share_whatsapp_button.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_MessageBoxQuestion))
        self.share_whatsapp_button.clicked.connect(self.share_via_whatsapp)
        self.share_whatsapp_button.setEnabled(False)
        actions_layout.addWidget(self.share_whatsapp_button)
        
        actions_layout.addStretch(1)
        
        self.layout.addLayout(actions_layout)
        
        # Tab widget per le statistiche dettagliate
        self.tabs = QTabWidget()
        
        # Tab 1: Panoramica
        self.overview_tab = QWidget()
        self._setup_overview_tab()
        self.tabs.addTab(self.overview_tab, "Panoramica")
        
        # Tab 2: Analisi Tempi
        self.times_tab = QWidget()
        self._setup_times_tab()
        self.tabs.addTab(self.times_tab, "Analisi Tempi")
        
        # Tab 3: Dettaglio Gare
        self.races_tab = QWidget()
        self._setup_races_tab()
        self.tabs.addTab(self.races_tab, "Dettaglio Gare")
        
        # Tab 4: Penalità
        self.penalties_tab = QWidget()
        self._setup_penalties_tab()
        self.tabs.addTab(self.penalties_tab, "Penalità")
        
        # Tab 5: Confronto con Altri
        self.comparison_tab = QWidget()
        self._setup_comparison_tab()
        self.tabs.addTab(self.comparison_tab, "Confronto con Altri")
        
        # Nascondi i tab finché non vengono caricati i dati
        self.tabs.setVisible(False)
        self.layout.addWidget(self.tabs)
        
        # Carica la lista dei piloti
        self.load_pilots()
    
    def _create_stat_box(self, title, value):
        """Crea un box per le statistiche principali"""
        box = QFrame()
        box.setFrameShape(QFrame.Shape.StyledPanel)
        box.setStyleSheet("background-color: #e6f2ff; border-radius: 5px; padding: 5px; margin: 2px;")
        
        layout = QVBoxLayout(box)
        
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-weight: bold; color: #003366;")
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #003366;")
        layout.addWidget(value_label)
        
        # Salviamo il riferimento al valore per aggiornarlo facilmente
        box.value_label = value_label
        
        return box
    
    def _setup_overview_tab(self):
        """Configura la tab di panoramica"""
        layout = QVBoxLayout(self.overview_tab)
        
        # Splitter per dividere la schermata
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Colonna sinistra: grafici
        left_column = QWidget()
        left_layout = QVBoxLayout(left_column)
        
        # Grafico 1: Andamento posizioni
        self.positions_chart_container = QGroupBox("Andamento Posizioni")
        positions_layout = QVBoxLayout(self.positions_chart_container)
        
        self.positions_chart = FigureCanvas(plt.Figure(figsize=(5, 4)))
        positions_layout.addWidget(self.positions_chart)
        
        left_layout.addWidget(self.positions_chart_container)
        
        # Grafico 2: Punti per gara
        self.points_chart_container = QGroupBox("Punti per Gara")
        points_layout = QVBoxLayout(self.points_chart_container)
        
        self.points_chart = FigureCanvas(plt.Figure(figsize=(5, 4)))
        points_layout.addWidget(self.points_chart)
        
        left_layout.addWidget(self.points_chart_container)
        
        splitter.addWidget(left_column)
        
        # Colonna destra: statistiche e info aggiuntive
        right_column = QWidget()
        right_layout = QVBoxLayout(right_column)
        
        # Statistiche di stagione
        self.season_stats_group = QGroupBox("Statistiche di Stagione")
        season_stats_layout = QFormLayout(self.season_stats_group)
        
        self.season_total_races = QLabel("0")
        self.season_completed_races = QLabel("0")
        self.season_current_position = QLabel("-")
        self.season_points_leader = QLabel("-")
        self.season_points_gap = QLabel("-")
        self.season_avg_position = QLabel("-")
        self.season_consistency = QLabel("-")
        
        season_stats_layout.addRow("Gare in calendario:", self.season_total_races)
        season_stats_layout.addRow("Gare completate:", self.season_completed_races)
        season_stats_layout.addRow("Posizione attuale:", self.season_current_position)
        season_stats_layout.addRow("Punti al leader:", self.season_points_leader)
        season_stats_layout.addRow("Distacco dal pilota davanti:", self.season_points_gap)
        season_stats_layout.addRow("Posizione media:", self.season_avg_position)
        season_stats_layout.addRow("Indice di costanza:", self.season_consistency)
        
        right_layout.addWidget(self.season_stats_group)
        
        # Prossima gara
        self.next_race_group = QGroupBox("Prossima Gara")
        next_race_layout = QFormLayout(self.next_race_group)
        
        self.next_race_name = QLabel("-")
        self.next_race_date = QLabel("-")
        self.next_race_circuit = QLabel("-")
        self.next_race_history = QLabel("-")
        
        next_race_layout.addRow("Evento:", self.next_race_name)
        next_race_layout.addRow("Data:", self.next_race_date)
        next_race_layout.addRow("Circuito:", self.next_race_circuit)
        next_race_layout.addRow("Risultati precedenti:", self.next_race_history)
        
        right_layout.addWidget(self.next_race_group)
        
        # Suggerimenti miglioramento
        self.improvement_group = QGroupBox("Aree di Miglioramento")
        improvement_layout = QVBoxLayout(self.improvement_group)
        
        self.improvement_text = QTextEdit()
        self.improvement_text.setReadOnly(True)
        self.improvement_text.setMaximumHeight(100)
        improvement_layout.addWidget(self.improvement_text)
        
        right_layout.addWidget(self.improvement_group)
        
        splitter.addWidget(right_column)
        
        layout.addWidget(splitter)
    
    def _setup_times_tab(self):
        """Configura la tab di analisi dei tempi"""
        layout = QVBoxLayout(self.times_tab)
        
        # Splitter principale
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Parte superiore: Grafico evoluzione tempi
        upper_widget = QWidget()
        upper_layout = QVBoxLayout(upper_widget)
        
        times_evolution_group = QGroupBox("Evoluzione Tempi sul Giro durante la Stagione")
        times_evolution_layout = QVBoxLayout(times_evolution_group)
        
        self.times_evolution_chart = FigureCanvas(plt.Figure(figsize=(8, 3)))
        times_evolution_layout.addWidget(self.times_evolution_chart)
        
        upper_layout.addWidget(times_evolution_group)
        
        splitter.addWidget(upper_widget)
        
        # Parte inferiore: divisa in due colonne
        lower_widget = QWidget()
        lower_layout = QHBoxLayout(lower_widget)
        
        # Colonna sinistra: Statistiche tempi e grafico confronto
        left_column = QVBoxLayout()
        
        # Box statistiche tempo
        time_stats_group = QGroupBox("Statistiche Tempi")
        time_stats_layout = QFormLayout(time_stats_group)
        
        self.best_lap_overall = QLabel("-")
        self.best_lap_where = QLabel("-")
        self.avg_lap_time = QLabel("-")
        self.lap_consistency = QLabel("-")
        self.best_sector_times = QLabel("-")
        self.worst_sector_times = QLabel("-")
        
        time_stats_layout.addRow("Miglior giro assoluto:", self.best_lap_overall)
        time_stats_layout.addRow("Ottenuto in:", self.best_lap_where)
        time_stats_layout.addRow("Tempo medio sul giro:", self.avg_lap_time)
        time_stats_layout.addRow("Costanza tempo giro:", self.lap_consistency)
        time_stats_layout.addRow("Settori migliori:", self.best_sector_times)
        time_stats_layout.addRow("Settori da migliorare:", self.worst_sector_times)
        
        left_column.addWidget(time_stats_group)
        
        # Grafico confronto con media categoria
        comparison_group = QGroupBox("Confronto con Media Categoria")
        comparison_layout = QVBoxLayout(comparison_group)
        
        self.category_comparison_chart = FigureCanvas(plt.Figure(figsize=(5, 4)))
        comparison_layout.addWidget(self.category_comparison_chart)
        
        left_column.addWidget(comparison_group)
        
        lower_layout.addLayout(left_column)
        
        # Colonna destra: Tabella tempi dettagliati
        right_column = QVBoxLayout()
        
        lap_times_group = QGroupBox("Tempi Dettagliati")
        lap_times_layout = QVBoxLayout(lap_times_group)
        
        self.lap_times_table = QTableWidget(0, 6)
        self.lap_times_table.setHorizontalHeaderLabels([
            "Evento", "Circuito", "Data", "Miglior Tempo", "Media", "Diff. Categoria"
        ])
        self.lap_times_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        lap_times_layout.addWidget(self.lap_times_table)
        
        right_column.addWidget(lap_times_group)
        
        lower_layout.addLayout(right_column)
        
        lower_widget.setLayout(lower_layout)
        
        splitter.addWidget(lower_widget)
        
        # Imposta il rapporto del divider
        splitter.setSizes([300, 500])
        
        layout.addWidget(splitter)
    
    def _setup_races_tab(self):
        """Configura la tab di dettaglio delle gare"""
        layout = QVBoxLayout(self.races_tab)
        
        # Tabella con tutte le gare
        self.races_table = QTableWidget(0, 9)
        self.races_table.setHorizontalHeaderLabels([
            "Evento", "Data", "Circuito", "Gruppo", "Pos. Qual.", "Pos. Gara 1", 
            "Pos. Gara 2", "Punteggio", "Note"
        ])
        self.races_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.races_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        layout.addWidget(QLabel("Risultati di tutte le gare"))
        layout.addWidget(self.races_table)
        
        # Dettagli gara selezionata
        race_details_group = QGroupBox("Dettagli Gara Selezionata")
        race_details_layout = QVBoxLayout(race_details_group)
        
        race_info_layout = QHBoxLayout()
        
        # Prima colonna: informazioni gara
        left_info = QFormLayout()
        
        self.race_detail_event = QLabel("-")
        self.race_detail_date = QLabel("-")
        self.race_detail_circuit = QLabel("-")
        self.race_detail_weather = QLabel("-")
        self.race_detail_participants = QLabel("-")
        
        left_info.addRow("Evento:", self.race_detail_event)
        left_info.addRow("Data:", self.race_detail_date)
        left_info.addRow("Circuito:", self.race_detail_circuit)
        left_info.addRow("Condizioni:", self.race_detail_weather)
        left_info.addRow("Partecipanti:", self.race_detail_participants)
        
        race_info_layout.addLayout(left_info)
        
        # Seconda colonna: risultati qualifiche
        middle_info = QFormLayout()
        
        self.qual_position = QLabel("-")
        self.qual_best_time = QLabel("-")
        self.qual_gap = QLabel("-")
        self.qual_group = QLabel("-")
        
        middle_info.addRow("Pos. Qualifica:", self.qual_position)
        middle_info.addRow("Miglior tempo:", self.qual_best_time)
        middle_info.addRow("Distacco:", self.qual_gap)
        middle_info.addRow("Gruppo:", self.qual_group)
        
        race_info_layout.addLayout(middle_info)
        
        # Terza colonna: risultati gare
        right_info = QFormLayout()
        
        self.race1_position = QLabel("-")
        self.race1_gap = QLabel("-")
        self.race2_position = QLabel("-")
        self.race2_gap = QLabel("-")
        self.total_points = QLabel("-")
        
        right_info.addRow("Pos. Gara 1:", self.race1_position)
        right_info.addRow("Distacco G1:", self.race1_gap)
        right_info.addRow("Pos. Gara 2:", self.race2_position)
        right_info.addRow("Distacco G2:", self.race2_gap)
        right_info.addRow("Punti totali:", self.total_points)
        
        race_info_layout.addLayout(right_info)
        
        race_details_layout.addLayout(race_info_layout)
        
        # Note sulla gara
        self.race_notes = QTextEdit()
        self.race_notes.setReadOnly(True)
        self.race_notes.setMaximumHeight(80)
        race_details_layout.addWidget(QLabel("Note:"))
        race_details_layout.addWidget(self.race_notes)
        
        layout.addWidget(race_details_group)
        
        # Collega la selezione della tabella all'aggiornamento dei dettagli
        self.races_table.itemSelectionChanged.connect(self.update_race_details)
    
    def _setup_penalties_tab(self):
        """Configura la tab delle penalità"""
        layout = QVBoxLayout(self.penalties_tab)
        
        # Tabella con tutte le penalità
        self.penalties_table = QTableWidget(0, 7)
        self.penalties_table.setHorizontalHeaderLabels([
            "Data", "Evento", "Sessione", "Tipo Infrazione", "Penalità", "Impatto", "Note"
        ])
        self.penalties_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(QLabel("Elenco di tutte le penalità ricevute"))
        layout.addWidget(self.penalties_table)
        
        # Statistiche penalità
        penalties_stats_group = QGroupBox("Statistiche Penalità")
        penalties_stats_layout = QVBoxLayout(penalties_stats_group)
        
        # Grafici e statistiche
        stats_layout = QHBoxLayout()
        
        # Grafico torta dei tipi di penalità
        pie_container = QWidget()
        pie_layout = QVBoxLayout(pie_container)
        pie_layout.addWidget(QLabel("Tipi di Infrazione"))
        
        self.penalties_pie_chart = FigureCanvas(plt.Figure(figsize=(4, 4)))
        pie_layout.addWidget(self.penalties_pie_chart)
        
        stats_layout.addWidget(pie_container)
        
        # Statistiche numeriche
        penalties_info = QFormLayout()
        
        self.total_penalties = QLabel("0")
        self.penalty_points = QLabel("0")
        self.most_common = QLabel("-")
        self.penalty_trend = QLabel("-")
        
        penalties_info.addRow("Penalità totali:", self.total_penalties)
        penalties_info.addRow("Punti persi per penalità:", self.penalty_points)
        penalties_info.addRow("Infrazione più comune:", self.most_common)
        penalties_info.addRow("Tendenza:", self.penalty_trend)
        
        penalties_container = QWidget()
        penalties_container.setLayout(penalties_info)
        stats_layout.addWidget(penalties_container)
        
        penalties_stats_layout.addLayout(stats_layout)
        
        layout.addWidget(penalties_stats_group)
    
    def _setup_comparison_tab(self):
        """Configura la tab di confronto con altri piloti"""
        layout = QVBoxLayout(self.comparison_tab)
        
        # Selettore pilota per confronto
        selector_layout = QHBoxLayout()
        
        selector_layout.addWidget(QLabel("Confronta con:"))
        
        self.compare_pilot_combo = QComboBox()
        self.compare_pilot_combo.setMinimumWidth(300)
        selector_layout.addWidget(self.compare_pilot_combo)
        
        self.compare_button = QPushButton("Confronta")
        self.compare_button.clicked.connect(self.compare_with_pilot)
        selector_layout.addWidget(self.compare_button)
        
        selector_layout.addStretch(1)
        
        layout.addLayout(selector_layout)
        
        # Griglia 2x2 di grafici per il confronto
        grid_layout = QVBoxLayout()
        
        # Prima riga: due grafici affiancati
        row1_layout = QHBoxLayout()
        
        # Grafico 1: Confronto punti
        points_comparison_group = QGroupBox("Confronto Punti")
        points_comparison_layout = QVBoxLayout(points_comparison_group)
        
        self.points_comparison_chart = FigureCanvas(plt.Figure(figsize=(5, 4)))
        points_comparison_layout.addWidget(self.points_comparison_chart)
        
        row1_layout.addWidget(points_comparison_group)
        
        # Grafico 2: Confronto posizioni
        positions_comparison_group = QGroupBox("Confronto Posizioni")
        positions_comparison_layout = QVBoxLayout(positions_comparison_group)
        
        self.positions_comparison_chart = FigureCanvas(plt.Figure(figsize=(5, 4)))
        positions_comparison_layout.addWidget(self.positions_comparison_chart)
        
        row1_layout.addWidget(positions_comparison_group)
        
        grid_layout.addLayout(row1_layout)
        
        # Seconda riga: due elementi affiancati
        row2_layout = QHBoxLayout()
        
        # Grafico 3: Confronto tempi
        times_comparison_group = QGroupBox("Confronto Tempi")
        times_comparison_layout = QVBoxLayout(times_comparison_group)
        
        self.times_comparison_chart = FigureCanvas(plt.Figure(figsize=(5, 4)))
        times_comparison_layout.addWidget(self.times_comparison_chart)
        
        row2_layout.addWidget(times_comparison_group)
        
        # Statistiche di confronto
        stats_comparison_group = QGroupBox("Dati Confronto")
        stats_comparison_layout = QFormLayout(stats_comparison_group)
        
        # Prima una riga di intestazione
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Statistiche"))
        
        pilot1_label = QLabel("Pilota 1")
        pilot1_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(pilot1_label)
        
        pilot2_label = QLabel("Pilota 2")
        pilot2_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(pilot2_label)
        
        stats_comparison_layout.addRow("", header_layout)
        
        # Statistiche di confronto
        self._add_comparison_row(stats_comparison_layout, "Punti Totali:", "0", "0")
        self._add_comparison_row(stats_comparison_layout, "Posizione Media:", "0", "0")
        self._add_comparison_row(stats_comparison_layout, "Vittorie:", "0", "0")
        self._add_comparison_row(stats_comparison_layout, "Podi:", "0", "0")
        self._add_comparison_row(stats_comparison_layout, "Miglior Tempo:", "-", "-")
        self._add_comparison_row(stats_comparison_layout, "Tempo Medio:", "-", "-")
        self._add_comparison_row(stats_comparison_layout, "Penalità:", "0", "0")
        
        row2_layout.addWidget(stats_comparison_group)
        
        grid_layout.addLayout(row2_layout)
        
        layout.addLayout(grid_layout)
        
        # Tabella confronto testa a testa
        self.head_to_head_table = QTableWidget(0, 5)
        self.head_to_head_table.setHorizontalHeaderLabels([
            "Evento", "Data", "Pos. Pilota 1", "Pos. Pilota 2", "Vincitore"
        ])
        self.head_to_head_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(QLabel("Confronti diretti nelle stesse gare"))
        layout.addWidget(self.head_to_head_table)
    
    def _add_comparison_row(self, form_layout, label_text, value1, value2):
        """Aggiunge una riga di confronto con due valori"""
        row_layout = QHBoxLayout()
        
        # Spazio per far posto all'etichetta del FormLayout
        row_layout.addStretch(1)
        
        # Due valori affiancati
        value1_label = QLabel(value1)
        value1_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        row_layout.addWidget(value1_label)
        
        value2_label = QLabel(value2)
        value2_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        row_layout.addWidget(value2_label)
        
        # Aggiungiamo alla form
        form_layout.addRow(label_text, row_layout)
        
        # Salviamo i riferimenti alle etichette di valore per aggiornarle facilmente
        row_layout.value1_label = value1_label
        row_layout.value2_label = value2_label
        
        return row_layout
    
    def load_pilots(self):
        """Carica la lista dei piloti nei combobox"""
        try:
            db = SessionLocal()
            
            # Ottieni tutti i piloti
            piloti = db.query(Pilota).order_by(Pilota.cognome, Pilota.nome).all()
            
            self.pilot_combo.clear()
            self.compare_pilot_combo.clear()
            
            for pilota in piloti:
                display_text = f"{pilota.cognome} {pilota.nome}"
                self.pilot_combo.addItem(display_text, pilota.id)
                self.compare_pilot_combo.addItem(display_text, pilota.id)
            
            # Se ci sono almeno due piloti, seleziona il secondo per il confronto
            if self.compare_pilot_combo.count() > 1:
                self.compare_pilot_combo.setCurrentIndex(1)
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante il caricamento piloti: {str(e)}")
        finally:
            db.close()
    
    def load_statistics(self):
        """Carica tutte le statistiche del pilota selezionato"""
        pilot_id = self.pilot_combo.currentData()
        
        if not pilot_id:
            QMessageBox.warning(self, "Attenzione", "Seleziona un pilota!")
            return
        
        try:
            db = SessionLocal()
            
            # Ottieni i dati del pilota
            pilota = db.query(Pilota).get(pilot_id)
            
            if not pilota:
                QMessageBox.warning(self, "Attenzione", "Pilota non trovato!")
                return
            
            # Mostriamo i widget nascosti
            self.pilot_info_frame.setVisible(True)
            self.tabs.setVisible(True)
            
            # Abilitiamo i pulsanti di esportazione/condivisione
            self.export_pdf_button.setEnabled(True)
            self.export_csv_button.setEnabled(True)
            self.share_email_button.setEnabled(True)
            self.share_whatsapp_button.setEnabled(True)
            
            # Aggiorniamo le info del pilota nell'header
            self.pilot_name_label.setText(f"{pilota.nome} {pilota.cognome}")
            
            # Aggiorniamo le altre informazioni del pilota
            categoria_text = pilota.categoria_ranking if hasattr(pilota, 'categoria_ranking') and pilota.categoria_ranking else "Non specificata"
            self.category_label.setText(categoria_text)
            
            self.license_label.setText(f"{pilota.licenza_tipo} ({pilota.numero_licenza})")
            self.team_label.setText(pilota.moto_club or "Non specificato")
            
            moto_text = f"{pilota.marca_moto} {pilota.cilindrata}cc {pilota.tipo_motore}" if hasattr(pilota, 'marca_moto') and pilota.marca_moto else "Non specificata"
            self.bike_label.setText(moto_text)
            
            # Ottieni tutti i risultati del pilota
            query = """
            SELECT e.nome as evento_nome, e.data, e.circuito, r.sessione_tipo, 
                   r.posizione, r.punti, r.best_lap_time, r.id, g.nome as gruppo_nome,
                   g.categoria_id
            FROM risultati r
            JOIN iscrizioni i ON r.iscrizione_id = i.id
            JOIN eventi e ON i.evento_id = e.id
            JOIN gruppi g ON r.gruppo_id = g.id
            WHERE i.pilota_id = :pilota_id
            ORDER BY e.data, r.sessione_tipo
            """
            
            results = db.execute(query, {"pilota_id": pilot_id}).fetchall()
            
            # Prepariamo i dati statistici
            total_races = 0
            podiums = 0
            wins = 0
            total_points = 0
            best_position = 999
            
            # Variabili per il grafico delle posizioni
            events = []
            positions_qual = []
            positions_race1 = []
            positions_race2 = []
            race_points = []
            
            # Struttura per tenere traccia degli eventi
            eventi_dict = {}
            
            for result in results:
                # Contiamo solo le gare effettive (non qualifiche o prove libere)
                if result.sessione_tipo in ['Gara 1', 'Gara 2']:
                    # Aggiorna statistiche
                    total_races += 1
                    total_points += result.punti or 0
                    
                    if result.posizione:
                        if result.posizione <= 3:
                            podiums += 1
                        if result.posizione == 1:
                            wins += 1
                        if result.posizione < best_position:
                            best_position = result.posizione
                
                # Teniamo traccia degli eventi per i grafici
                event_key = f"{result.evento_nome} ({result.data.strftime('%d/%m/%Y')})"
                if event_key not in eventi_dict:
                    eventi_dict[event_key] = {
                        'data': result.data,
                        'nome': result.evento_nome,
                        'circuito': result.circuito,
                        'punti': 0
                    }
                
                # Aggiungiamo dati diversi in base al tipo di sessione
                if result.sessione_tipo == 'Qualifiche':
                    eventi_dict[event_key]['posizione_qual'] = result.posizione
                elif result.sessione_tipo == 'Gara 1':
                    eventi_dict[event_key]['posizione_gara1'] = result.posizione
                    eventi_dict[event_key]['punti'] += result.punti or 0
                elif result.sessione_tipo == 'Gara 2':
                    eventi_dict[event_key]['posizione_gara2'] = result.posizione
                    eventi_dict[event_key]['punti'] += result.punti or 0
            
            # Convertiamo il dizionario in liste ordinate per i grafici
            eventi_ordinati = sorted(eventi_dict.items(), key=lambda x: x[1]['data'])
            
            for event_name, event_data in eventi_ordinati:
                events.append(event_name)
                positions_qual.append(event_data.get('posizione_qual', None))
                positions_race1.append(event_data.get('posizione_gara1', None))
                positions_race2.append(event_data.get('posizione_gara2', None))
                race_points.append(event_data.get('punti', 0))
            
            # Aggiorniamo i box delle statistiche
            self.races_box.value_label.setText(str(total_races))
            self.podiums_box.value_label.setText(str(podiums))
            self.wins_box.value_label.setText(str(wins))
            self.points_box.value_label.setText(str(total_points))
            
            if best_position < 999:
                self.best_pos_box.value_label.setText(f"{best_position}°")
            else:
                self.best_pos_box.value_label.setText("-")
            
            # Ora popoliamo le varie tab con i dati
            
            # Aggiorna tab Panoramica
            self._update_overview_tab(db, pilota, eventi_ordinati, positions_qual, positions_race1, positions_race2, race_points)
            
            # Aggiorna tab Analisi Tempi
            self._update_times_tab(db, pilota, eventi_ordinati)
            
            # Aggiorna tab Dettaglio Gare
            self._update_races_tab(db, pilota, eventi_ordinati)
            
            # Aggiorna tab Penalità
            self._update_penalties_tab(db, pilota)
            
            QMessageBox.information(self, "Statistiche Caricate", f"Statistiche di {pilota.nome} {pilota.cognome} caricate con successo!")
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante il caricamento statistiche: {str(e)}")
        finally:
            db.close()
    
    def _update_overview_tab(self, db, pilota, eventi_ordinati, positions_qual, positions_race1, positions_race2, race_points):
        """Aggiorna la tab Panoramica con i dati del pilota"""
        # Grafico andamento posizioni
        ax1 = self.positions_chart.figure.subplots()
        
        # Estrai i nomi degli eventi e le posizioni (rimuovi None)
        events = [event[0] for event in eventi_ordinati]
        pos_qual = [p if p else float('nan') for p in positions_qual]
        pos_race1 = [p if p else float('nan') for p in positions_race1]
        pos_race2 = [p if p else float('nan') for p in positions_race2]
        
        x = range(len(events))
        
        # Crea il grafico linee
        if any(not np.isnan(p) for p in pos_qual):
            ax1.plot(x, pos_qual, marker='o', linestyle='-', color='blue', label='Qualifiche')
        if any(not np.isnan(p) for p in pos_race1):
            ax1.plot(x, pos_race1, marker='s', linestyle='-', color='red', label='Gara 1')
        if any(not np.isnan(p) for p in pos_race2):
            ax1.plot(x, pos_race2, marker='^', linestyle='-', color='green', label='Gara 2')
        
        # Inverti l'asse y (1° in alto)
        ax1.invert_yaxis()
        
        # Aggiungi etichette
        ax1.set_xticks(x)
        ax1.set_xticklabels([e[:10] + '...' for e in events], rotation=45, ha='right')
        ax1.set_ylabel('Posizione')
        ax1.set_title('Andamento Posizioni')
        ax1.grid(True, linestyle='--', alpha=0.7)
        ax1.legend()
        
        # Aggiusta layout
        self.positions_chart.figure.tight_layout()
        self.positions_chart.draw()
        
        # Grafico punti per gara
        ax2 = self.points_chart.figure.subplots()
        
        # Crea il grafico a barre per i punti
        bars = ax2.bar(x, race_points, color='purple', alpha=0.7)
        
        # Aggiungi le etichette sui punti
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax2.annotate(f'{height}', 
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3),  # 3 punti sopra la barra
                            textcoords="offset points",
                            ha='center', va='bottom')
        
        # Aggiungi etichette
        ax2.set_xticks(x)
        ax2.set_xticklabels([e[:10] + '...' for e in events], rotation=45, ha='right')
        ax2.set_ylabel('Punti')
        ax2.set_title('Punti per Gara')
        ax2.grid(True, linestyle='--', alpha=0.7)
        
        # Aggiusta layout
        self.points_chart.figure.tight_layout()
        self.points_chart.draw()
        
        # Aggiorniamo le statistiche di stagione
        season = self.season_combo.currentText()[-4:]  # Prendiamo l'anno
        
        # Calcola il totale delle gare in calendario
        total_races_query = """
            SELECT COUNT(DISTINCT e.id) as total_races
            FROM eventi e
            WHERE strftime('%Y', e.data) = :year
        """
        total_races_result = db.execute(total_races_query, {"year": season}).fetchone()
        total_races = total_races_result[0] if total_races_result else 0
        self.season_total_races.setText(str(total_races))
        
        # Calcola le gare completate
        completed_races = len(set([e[1]['nome'] for e in eventi_ordinati if str(e[1]['data'].year) == season]))
        self.season_completed_races.setText(str(completed_races))
        
        # Posizione attuale (da costruire con una query che calcola la classifica)
        # Per semplicità, qui usiamo una posizione fissa di esempio
        current_position = "5°"
        self.season_current_position.setText(current_position)
        
        # Punti al leader (da calcolare)
        points_gap = "45"
        self.season_points_leader.setText(points_gap)
        
        # Distacco dal pilota davanti
        points_to_next = "12"
        self.season_points_gap.setText(points_to_next)
        
        # Posizione media
        valid_positions = [p for p in positions_race1 + positions_race2 if p is not None]
        avg_position = sum(valid_positions) / len(valid_positions) if valid_positions else 0
        self.season_avg_position.setText(f"{avg_position:.1f}")
        
        # Indice di costanza (deviazione standard, più è basso più il pilota è costante)
        if len(valid_positions) > 1:
            import numpy as np
            consistency = np.std(valid_positions)
            consistency_text = f"{consistency:.2f} (Ottima)" if consistency < 2 else \
                              f"{consistency:.2f} (Buona)" if consistency < 4 else \
                              f"{consistency:.2f} (Media)" if consistency < 6 else \
                              f"{consistency:.2f} (Variabile)"
        else:
            consistency_text = "N/D (dati insufficienti)"
        
        self.season_consistency.setText(consistency_text)
        
        # Prossima gara
        next_race_query = """
            SELECT e.nome, e.data, e.circuito
            FROM eventi e
            WHERE e.data > CURRENT_DATE
            ORDER BY e.data
            LIMIT 1
        """
        next_race = db.execute(next_race_query).fetchone()
        
        if next_race:
            self.next_race_name.setText(next_race[0])
            self.next_race_date.setText(next_race[1].strftime("%d/%m/%Y"))
            self.next_race_circuit.setText(next_race[2])
            
            # Storia del pilota su questo circuito
            history_query = """
                SELECT r.sessione_tipo, r.posizione
                FROM risultati r
                JOIN iscrizioni i ON r.iscrizione_id = i.id
                JOIN eventi e ON i.evento_id = e.id
                WHERE i.pilota_id = :pilota_id
                AND e.circuito = :circuito
                AND r.sessione_tipo IN ('Gara 1', 'Gara 2')
                ORDER BY e.data DESC
            """
            
            history_results = db.execute(history_query, 
                                          {"pilota_id": pilota.id, 
                                           "circuito": next_race[2]}).fetchall()
            
            if history_results:
                history_text = ", ".join([f"{r.sessione_tipo}: {r.posizione}°" for r in history_results])
                self.next_race_history.setText(history_text)
            else:
                self.next_race_history.setText("Prima volta su questo circuito")
        else:
            self.next_race_name.setText("Nessuna gara in programma")
            self.next_race_date.setText("-")
            self.next_race_circuit.setText("-")
            self.next_race_history.setText("-")
        
        # Suggerimenti di miglioramento
        suggestions = []
        
        # Analizziamo i dati per generare suggerimenti personalizzati
        if len(valid_positions) > 0:
            # Controlla le partenze (differenza tra posizione qualifica e gara)
            qual_vs_race = []
            for q, r1 in zip(positions_qual, positions_race1):
                if q is not None and r1 is not None:
                    qual_vs_race.append(r1 - q)
            
            if qual_vs_race:
                avg_start_diff = sum(qual_vs_race) / len(qual_vs_race)
                if avg_start_diff > 2:
                    suggestions.append("Lavorare sulle partenze: la posizione media in gara 1 è significativamente peggiore rispetto alle qualifiche.")
                elif avg_start_diff < -2:
                    suggestions.append("Ottimi spunti in partenza: la posizione media in gara 1 è migliore rispetto alle qualifiche.")
            
            # Controlla la costanza tra gara 1 e gara 2
            race1_vs_race2 = []
            for r1, r2 in zip(positions_race1, positions_race2):
                if r1 is not None and r2 is not None:
                    race1_vs_race2.append(r2 - r1)
            
            if race1_vs_race2:
                avg_race_diff = sum(race1_vs_race2) / len(race1_vs_race2)
                if avg_race_diff > 2:
                    suggestions.append("Migliorare la resistenza: le prestazioni tendono a peggiorare in gara 2.")
                elif avg_race_diff < -2:
                    suggestions.append("Ottima progressione: le prestazioni tendono a migliorare in gara 2.")
            
            # Altri suggerimenti basati sulle statistiche
            if consistency > 4:
                suggestions.append("Lavorare sulla costanza: le prestazioni variano significativamente tra le gare.")
            
            # Trend recente (ultime 3 gare)
            recent_positions = [p for p in positions_race1[-3:] + positions_race2[-3:] if p is not None]
            if len(recent_positions) >= 3:
                recent_avg = sum(recent_positions) / len(recent_positions)
                overall_avg = avg_position
                
                if recent_avg < overall_avg - 1:
                    suggestions.append("Ottimo trend recente: le ultime gare mostrano un miglioramento rispetto alla media stagionale.")
                elif recent_avg > overall_avg + 1:
                    suggestions.append("Attenzione al trend recente: le ultime gare mostrano prestazioni sotto la media stagionale.")
        
        # Se non abbiamo suggerimenti, aggiungiamo un messaggio generico
        if not suggestions:
            suggestions.append("Dati insufficienti per fornire suggerimenti dettagliati.")
        
        # Aggiunge il testo dei suggerimenti
        self.improvement_text.setHtml("<ul><li>" + "</li><li>".join(suggestions) + "</li></ul>")
    
    def _update_times_tab(self, db, pilota, eventi_ordinati):
        """Aggiorna la tab Analisi Tempi con i dati del pilota"""
        # Query per ottenere tutti i tempi sul giro
        lap_times_query = """
            SELECT e.nome as evento_nome, e.data, e.circuito, lt.sessione_tipo,
                   lt.numero_giro, lt.tempo_ms, lt.timestamp
            FROM lap_times lt
            JOIN iscrizioni i ON lt.iscrizione_id = i.id
            JOIN eventi e ON i.evento_id = e.id
            WHERE i.pilota_id = :pilota_id
            ORDER BY e.data, lt.sessione_tipo, lt.numero_giro
        """
        
        lap_times = db.execute(lap_times_query, {"pilota_id": pilota.id}).fetchall()
        
        # Se non ci sono tempi, mostriamo un messaggio
        if not lap_times:
            QMessageBox.information(self, "Nessun Dato", "Non sono disponibili dati sui tempi per questo pilota.")
            return
        
        # Organizziamo i dati per evento e sessione
        eventi_tempi = {}
        
        for lt in lap_times:
            event_key = f"{lt.evento_nome} - {lt.data.strftime('%d/%m/%Y')}"
            
            if event_key not in eventi_tempi:
                eventi_tempi[event_key] = {
                    'circuito': lt.circuito,
                    'data': lt.data,
                    'sessioni': {}
                }
            
            if lt.sessione_tipo not in eventi_tempi[event_key]['sessioni']:
                eventi_tempi[event_key]['sessioni'][lt.sessione_tipo] = []
            
            eventi_tempi[event_key]['sessioni'][lt.sessione_tipo].append({
                'giro': lt.numero_giro,
                'tempo_ms': lt.tempo_ms,
                'timestamp': lt.timestamp
            })
        
        # Troviamo il miglior tempo assoluto e il tempo medio
        best_time_ms = float('inf')
        best_time_event = ""
        best_time_circuit = ""
        
        all_valid_times = []
        
        for event_key, event_data in eventi_tempi.items():
            for session_type, laps in event_data['sessioni'].items():
                # Consideriamo solo i giri validi (escludiamo outlier)
                valid_times = [lap['tempo_ms'] for lap in laps if lap['tempo_ms'] > 0]
                
                if valid_times:
                    session_best = min(valid_times)
                    all_valid_times.extend(valid_times)
                    
                    if session_best < best_time_ms:
                        best_time_ms = session_best
                        best_time_event = event_key
                        best_time_circuit = event_data['circuito']
        
        # Calcoliamo la media e la deviazione standard
        avg_time_ms = sum(all_valid_times) / len(all_valid_times) if all_valid_times else 0
        
        if len(all_valid_times) > 1:
            import numpy as np
            std_dev = np.std(all_valid_times)
            consistency = (1 - (std_dev / avg_time_ms)) * 100  # Più è alto, più è costante
        else:
            consistency = 0
        
        # Formatta i tempi per la visualizzazione
        if best_time_ms < float('inf'):
            mins = int(best_time_ms // 60000)
            secs = int((best_time_ms % 60000) // 1000)
            msecs = int(best_time_ms % 1000)
            best_time_text = f"{mins:01d}:{secs:02d}.{msecs:03d}"
        else:
            best_time_text = "-"
        
        if avg_time_ms > 0:
            mins = int(avg_time_ms // 60000)
            secs = int((avg_time_ms % 60000) // 1000)
            msecs = int(avg_time_ms % 1000)
            avg_time_text = f"{mins:01d}:{secs:02d}.{msecs:03d}"
        else:
            avg_time_text = "-"
        
        # Aggiorniamo le statistiche
        self.best_lap_overall.setText(best_time_text)
        self.best_lap_where.setText(f"{best_time_event}, {best_time_circuit}")
        self.avg_lap_time.setText(avg_time_text)
        
        # Formatta il valore di consistenza
        if consistency > 0:
            if consistency > 95:
                consistency_text = f"{consistency:.1f}% (Eccellente)"
            elif consistency > 90:
                consistency_text = f"{consistency:.1f}% (Ottima)"
            elif consistency > 85:
                consistency_text = f"{consistency:.1f}% (Buona)"
            else:
                consistency_text = f"{consistency:.1f}% (Migliorabile)"
        else:
            consistency_text = "N/D (dati insufficienti)"
        
        self.lap_consistency.setText(consistency_text)
        
        # Per semplicità, questi campi conterrebbero dati più dettagliati in una implementazione completa
        self.best_sector_times.setText("Dati settori non disponibili")
        self.worst_sector_times.setText("Dati settori non disponibili")
        
        # Grafico evoluzione tempi
        ax1 = self.times_evolution_chart.figure.subplots()
        
        # Prepariamo i dati per il grafico
        events_list = list(eventi_tempi.keys())
        events_list.sort(key=lambda e: eventi_tempi[e]['data'])
        
        # Raccogliamo i migliori tempi per ogni evento e sessione
        best_times_qual = []
        best_times_race = []
        
        for event in events_list:
            # Miglior tempo qualifiche
            if 'Qualifiche' in eventi_tempi[event]['sessioni']:
                qual_times = [lap['tempo_ms'] for lap in eventi_tempi[event]['sessioni']['Qualifiche'] if lap['tempo_ms'] > 0]
                if qual_times:
                    best_times_qual.append(min(qual_times))
                else:
                    best_times_qual.append(None)
            else:
                best_times_qual.append(None)
            
            # Miglior tempo gare (considera sia Gara 1 che Gara 2)
            race_best = None
            for session in ['Gara 1', 'Gara 2']:
                if session in eventi_tempi[event]['sessioni']:
                    race_times = [lap['tempo_ms'] for lap in eventi_tempi[event]['sessioni'][session] if lap['tempo_ms'] > 0]
                    if race_times:
                        session_best = min(race_times)
                        if race_best is None or session_best < race_best:
                            race_best = session_best
            
            best_times_race.append(race_best)
        
        # X-axis per i grafici
        x = range(len(events_list))
        
        # Converti in secondi per il grafico e gestisci i None
        best_times_qual_sec = [t/1000 if t is not None else float('nan') for t in best_times_qual]
        best_times_race_sec = [t/1000 if t is not None else float('nan') for t in best_times_race]
        
        # Crea il grafico linee
        if any(not np.isnan(t) for t in best_times_qual_sec):
            ax1.plot(x, best_times_qual_sec, marker='o', linestyle='-', color='blue', label='Qualifiche')
        if any(not np.isnan(t) for t in best_times_race_sec):
            ax1.plot(x, best_times_race_sec, marker='s', linestyle='-', color='red', label='Gare')
        
        # Aggiungi etichette
        ax1.set_xticks(x)
        ax1.set_xticklabels([e[:10] + '...' for e in events_list], rotation=45, ha='right')
        ax1.set_ylabel('Tempo (secondi)')
        ax1.set_title('Evoluzione Tempi sul Giro')
        ax1.grid(True, linestyle='--', alpha=0.7)
        ax1.legend()
        
        # Aggiusta layout
        self.times_evolution_chart.figure.tight_layout()
        self.times_evolution_chart.draw()
        
        # Grafico confronto con media categoria
        ax2 = self.category_comparison_chart.figure