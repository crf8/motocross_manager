<?php
session_start();
if (!isset($_SESSION['user'])) {
    header('Location: login.php');
    exit();
}

require_once '../config/database.php';
$db = new Database();
$data = $db->readData();

// Prendiamo tutte le iscrizioni
$iscrizioni = $data['iscrizioni'] ?? [];
$piloti = $data['piloti'] ?? [];
$eventi = $data['eventi'] ?? [];

// Colleghiamo le informazioni (è come mettere insieme i pezzi del puzzle!)
$iscrizioni_complete = [];
foreach($iscrizioni as $iscrizione) {
    // Troviamo il pilota
    $pilota = null;
    foreach($piloti as $p) {
        if ($p['id'] == $iscrizione['pilota_id']) {
            $pilota = $p;
            break;
        }
    }
    
    // Troviamo l'evento
    $evento = null;
    foreach($eventi as $e) {
        if ($e['id'] == $iscrizione['evento_id']) {
            $evento = $e;
            break;
        }
    }
    
    // Se abbiamo trovato entrambi, aggiungiamo alla lista
    if ($pilota && $evento) {
        $iscrizioni_complete[] = [
            'iscrizione' => $iscrizione,
            'pilota' => $pilota,
            'evento' => $evento
        ];
    }
}
?>

<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <title>Le Mie Iscrizioni - Motocross Manager Pro</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #0a0a0a;
            color: white;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 {
            color: #FF0000;
            text-align: center;
            margin-bottom: 30px;
        }
        .back-button {
            background: #666;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 5px;
            display: inline-block;
            margin-bottom: 20px;
        }
        .iscrizioni-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
        }
        .iscrizione-card {
            background: #1a1a1a;
            border: 2px solid #333;
            border-radius: 10px;
            padding: 20px;
            transition: all 0.3s;
        }
        .iscrizione-card:hover {
            border-color: #FF0000;
            transform: translateY(-5px);
        }
        .evento-title {
            color: #FFD700;
            font-size: 1.3em;
            margin-bottom: 10px;
        }
        .info-item {
            display: flex;
            justify-content: space-between;
            padding: 5px 0;
            border-bottom: 1px solid #333;
        }
        .info-item:last-child {
            border-bottom: none;
        }
        .label {
            color: #888;
        }
        .value {
            font-weight: bold;
        }
        .status-confirmed {
            color: #00FF00;
            font-weight: bold;
        }
        .empty-state {
            text-align: center;
            padding: 50px;
            background: #1a1a1a;
            border-radius: 10px;
            margin-top: 30px;
        }
        .empty-state h3 {
            color: #FF0000;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <a href="../index.php" class="back-button">← Torna alla Dashboard</a>
        
        <h1>Le Mie Iscrizioni</h1>
        
        <?php if (count($iscrizioni_complete) > 0): ?>
            <div class="iscrizioni-grid">
                <?php foreach($iscrizioni_complete as $item): ?>
                    <div class="iscrizione-card">
                        <div class="evento-title">
                            <?php 
                            $emoji = '🏍️';
                            if ($item['evento']['tipo'] == 'campionato') $emoji = '🏆';
                            elseif ($item['evento']['tipo'] == 'trofeo') $emoji = '🎯';
                            elseif ($item['evento']['tipo'] == 'sociale') $emoji = '🚀';
                            elseif ($item['evento']['tipo'] == 'allenamento') $emoji = '💪';
                            echo $emoji . ' ';
                            echo $item['evento']['nome_evento'];
                            ?>
                        </div>
                        
                        <div class="info-item">
                            <span class="label">Data:</span>
                            <span class="value"><?php echo date('d/m/Y', strtotime($item['evento']['data_evento'])); ?></span>
                        </div>
                        
                        <div class="info-item">
                            <span class="label">Località:</span>
                            <span class="value"><?php echo $item['evento']['luogo']; ?></span>
                        </div>
                        
                        <div class="info-item">
                            <span class="label">Pilota:</span>
                            <span class="value"><?php echo $item['pilota']['nome'] . ' ' . $item['pilota']['cognome'] . ' (#' . $item['pilota']['numero_gara'] . ')'; ?></span>
                        </div>
                        
                        <div class="info-item">
                            <span class="label">Categoria:</span>
                            <span class="value"><?php echo $item['iscrizione']['categoria']; ?></span>
                        </div>
                        
                        <div class="info-item">
                            <span class="label">Stato:</span>
                            <span class="value status-confirmed">CONFERMATA</span>
                        </div>
                    </div>
                <?php endforeach; ?>
            </div>
        <?php else: ?>
            <div class="empty-state">
                <h3>Nessuna iscrizione attiva</h3>
                <p>Non hai ancora iscrizioni confermate.</p>
                <a href="gare_disponibili.php" style="color: #FFD700;">
                    Vedi Gare Disponibili →
                </a>
            </div>
        <?php endif; ?>
    </div>
</body>
</html>