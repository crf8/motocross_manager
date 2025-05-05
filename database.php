<?php
class Database {
    private $file_path = '../data/motocross_data.json';
    
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
    
    public function saveData($data) {
        $json = json_encode($data, JSON_PRETTY_PRINT);
        file_put_contents($this->file_path, $json);
    }
}
?>