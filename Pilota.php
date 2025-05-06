<?php
// Questo file definisce cos'è un pilota
class Pilota {
    public $id;
    public $nome;
    public $cognome;
    public $numero_gara;
    public $tempi = [];
    
    public function __construct($nome, $cognome, $numero_gara) {
        $this->nome = $nome;
        $this->cognome = $cognome;
        $this->numero_gara = $numero_gara;
    }
    
    public function aggiungi_tempo($tempo) {
        $this->tempi[] = $tempo;
    }
    
    public function mostra_info() {
        return "Pilota #{$this->numero_gara}: {$this->nome} {$this->cognome}";
    }
}
?>