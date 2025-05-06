<?php
session_start();
if (!isset($_SESSION['user'])) {
    header('Location: login.php');
    exit();
}

// Usiamo la nuova classe MongoCompatDB
require_once '../config/MongoCompatDB.php';
$db = new MongoCompatDB();

$evento_id = $_GET['id'] ?? 0;
$evento = null;

// Cerchiamo la gara
foreach($db->readCollection('eventi') as $e) {
    if ($e['id'] == $evento_id) {
        $evento = $e;
        break;
    }
}

if (!$evento) {
    header('Location: gare_disponibili.php');
    exit();
}

// Se il form è stato inviato
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    // Creiamo una nuova iscrizione
    $iscrizione = [
        'evento_id' => $evento_id,
        'pilota_id' => $_POST['pilota_id'],
        'categoria' => $_POST['categoria'],
        'data_iscrizione' => date('Y-m-d'),
        'stato' => 'confermata'
    ];
    
    // Salviamo l'iscrizione
    $nuova_iscrizione_id = $db->insertDocument('iscrizioni', $iscrizione);
    
    // Andiamo alla pagina di conferma
    header('Location: iscrizione_confermata.php?id=' . $nuova_iscrizione_id);
    exit();
}

$piloti = $db->readCollection('piloti');
?>

<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <title>Iscrizione Gara - Motocross Manager Pro</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #0a0a0a;
            color: white;
            padding: 20px;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
        }
        h1 {
            color: #FF0000;
            text-align: center;
            margin-bottom: 30px;
        }
        .event-info {
            background: #1a1a1a;
            border: 2px solid #FFD700;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
        }
        .form-section {
            background: #1a1a1a;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #FFD700;
            font-weight: bold;
        }
        select {
            width: 100%;
            padding: 12px;
            background: #333;
            border: 1px solid #FF0000;
            color: white;
            border-radius: 5px;
            font-size: 16px;
        }
        .submit-button {
            background: linear-gradient(to right, #FF0000, #FF4500);
            color: white;
            border: none;
            padding: 15px 30px;
            font-size: 18px;
            border-radius: 5px;
            cursor: pointer;
            width: 100%;
            transition: all 0.3s;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Iscrizione a: <?php echo $evento['nome_evento']; ?></h1>
        
        <!-- Informazioni evento -->
        <div class="event-info">
            <h2>📋 Dettagli Evento</h2>
            <p><strong>Data:</strong> <?php echo date('d/m/Y', strtotime($evento['data_evento'])); ?></p>
            <p><strong>Località:</strong> <?php echo $evento['luogo']; ?></p>
            <p><strong>Tipo:</strong> <?php echo $evento['tipo']; ?></p>
            <p><strong>Quota di iscrizione:</strong> €<?php echo $evento['quota_prima']; ?></p>
        </div>
        
        <form method="POST">
            <!-- Selezione pilota -->
            <div class="form-section">
                <h3>Seleziona il tuo profilo pilota</h3>
                <div class="form-group">
                    <label>Seleziona Pilota:</label>
                    <select name="pilota_id" required>
                        <option value="">-- Seleziona --</option>
                        <?php foreach($piloti as $pilota): ?>
                        <option value="<?php echo $pilota['id']; ?>">
                            <?php echo $pilota['nome'] . ' ' . $pilota['cognome'] . ' - #' . $pilota['numero_gara']; ?>
                        </option>
                        <?php endforeach; ?>
                    </select>
                </div>
            </div>
            
            <!-- Selezione categoria -->
            <div class="form-section">
                <h3>Seleziona Categoria</h3>
                <div class="form-group">
                    <label>Categoria di Gara:</label>
                    <select name="categoria" required>
                        <option value="">-- Seleziona --</option>
                        <?php foreach($evento['categorie'] as $cat): ?>
                        <option value="<?php echo $cat; ?>"><?php echo $cat; ?></option>
                        <?php endforeach; ?>
                    </select>
                </div>
            </div>
            
            <button type="submit" class="submit-button">
                COMPLETA ISCRIZIONE
            </button>
        </form>
    </div>
</body>
</html>