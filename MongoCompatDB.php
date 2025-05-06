<?php
/**
 * Classe compatibile con MongoDB che usa file JSON
 */
class MongoCompatDB {
    // Percorso del nuovo file JSON
    private $file_path;
    
    /**
     * Costruttore - Si occupa di inizializzare
     */
    public function __construct() {
        // Imposta il percorso assoluto
        $this->file_path = dirname(__DIR__) . '/data/motocross_data_nuovo.json';
        
        // Verifica che la directory esista, se non esiste la crea
        $directory = dirname($this->file_path);
        if (!is_dir($directory)) {
            mkdir($directory, 0755, true);
        }
        
        // Verifica che il file esista
        if (!file_exists($this->file_path)) {
            // Se non esiste, crea un file vuoto
            $data_iniziale = [
                'piloti' => [],
                'eventi' => [],
                'iscrizioni' => [],
                'gruppi' => [],
                'tempi' => []
            ];
            file_put_contents($this->file_path, json_encode($data_iniziale, JSON_PRETTY_PRINT));
        }
    }
    
    /**
     * Legge tutti i documenti da una collezione
     */
    public function readCollection($collection) {
        $data = $this->readData();
        return isset($data[$collection]) ? $data[$collection] : [];
    }
    
    /**
     * Inserisce un nuovo documento
     */
    public function insertDocument($collection, $document) {
        $data = $this->readData();
        
        // Se la collezione non esiste, la creiamo
        if (!isset($data[$collection])) {
            $data[$collection] = [];
        }
        
        // Genera un ID se non esiste
        if (!isset($document['id'])) {
            $ids = array_column($data[$collection], 'id');
            $document['id'] = empty($ids) ? 1 : max($ids) + 1;
        }
        
        // Aggiungi il documento
        $data[$collection][] = $document;
        
        // Salva i dati
        $this->saveData($data);
        
        return $document['id'];
    }
    
    /**
     * Aggiorna un documento esistente
     */
    public function updateDocument($collection, $id, $document) {
        $data = $this->readData();
        
        // Se la collezione non esiste, fallisce
        if (!isset($data[$collection])) {
            return false;
        }
        
        // Cerca il documento
        foreach ($data[$collection] as $key => $item) {
            if ($item['id'] == $id) {
                // Mantiene l'ID originale
                $document['id'] = $id;
                
                // Aggiorna il documento
                $data[$collection][$key] = $document;
                
                // Salva i dati
                $this->saveData($data);
                
                return true;
            }
        }
        
        return false;
    }
    
    /**
     * Elimina un documento
     */
    public function deleteDocument($collection, $id) {
        $data = $this->readData();
        
        // Se la collezione non esiste, fallisce
        if (!isset($data[$collection])) {
            return false;
        }
        
        // Cerca il documento
        foreach ($data[$collection] as $key => $item) {
            if ($item['id'] == $id) {
                // Rimuove il documento
                unset($data[$collection][$key]);
                
                // Riordina l'array (per mantenere gli indici numerici)
                $data[$collection] = array_values($data[$collection]);
                
                // Salva i dati
                $this->saveData($data);
                
                return true;
            }
        }
        
        return false;
    }
    
    /**
     * Cerca documenti con criteri specifici
     */
    public function findDocuments($collection, $filter = []) {
        $data = $this->readData();
        
        // Se la collezione non esiste, restituisce un array vuoto
        if (!isset($data[$collection])) {
            return [];
        }
        
        // Se non ci sono filtri, restituisce tutti i documenti
        if (empty($filter)) {
            return $data[$collection];
        }
        
        // Filtra i documenti
        $results = [];
        foreach ($data[$collection] as $document) {
            $match = true;
            
            // Controlla ogni criterio di filtro
            foreach ($filter as $key => $value) {
                if (!isset($document[$key]) || $document[$key] != $value) {
                    $match = false;
                    break;
                }
            }
            
            // Se il documento corrisponde, aggiungilo ai risultati
            if ($match) {
                $results[] = $document;
            }
        }
        
        return $results;
    }
    
    /**
     * Legge tutti i dati
     */
    public function readData() {
        if (!file_exists($this->file_path)) {
            return [
                'piloti' => [],
                'eventi' => [],
                'iscrizioni' => [],
                'gruppi' => [],
                'tempi' => []
            ];
        }
        $json = file_get_contents($this->file_path);
        return json_decode($json, true);
    }
    
    /**
     * Salva tutti i dati
     */
    public function saveData($data) {
        $json = json_encode($data, JSON_PRETTY_PRINT);
        file_put_contents($this->file_path, $json);
        return true;
    }
}
?>