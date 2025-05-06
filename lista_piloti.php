<?php
session_start();
if (!isset($_SESSION['user'])) {
    header('Location: login.php');
    exit();
}

// Usiamo la nuova classe MongoCompatDB
require_once '../config/MongoCompatDB.php';
$db = new MongoCompatDB();

// Creiamo la directory se non esiste
$directory = '../data';
if (!is_dir($directory)) {
    mkdir($directory, 0755, true);
}

$piloti = $db->readCollection('piloti');
?>

<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <title>Lista Piloti - Motocross Manager Pro</title>
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
        table {
            width: 100%;
            border-collapse: collapse;
            background: #1a1a1a;
            border-radius: 10px;
            overflow: hidden;
        }
        th, td {
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #333;
        }
        th {
            background: #FF0000;
            color: white;
            font-weight: bold;
        }
        tr:hover {
            background: #2a2a2a;
        }
        .no-piloti {
            text-align: center;
            padding: 50px;
            font-size: 1.2em;
            color: #666;
        }
        .pill {
            background: #333;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.9em;
            margin-right: 5px;
        }
        .status-message {
            padding: 10px;
            margin-bottom: 20px;
            border-radius: 5px;
            text-align: center;
        }
        .success {
            background-color: #004d00;
            color: white;
        }
        .error {
            background-color: #990000;
            color: white;
        }
    </style>
</head>
<body>
    <div class="container">
        <a href="../index.php" class="back-button">← Torna alla Dashboard</a>
        
        <h1>Lista Piloti Iscritti</h1>
        
        <?php
        // Mostriamo eventuali messaggi di stato
        if (isset($_GET['status'])) {
            $status = $_GET['status'];
            if ($status == 'success') {
                echo '<div class="status-message success">Operazione completata con successo!</div>';
            } elseif ($status == 'error') {
                echo '<div class="status-message error">Si è verificato un errore. Riprova.</div>';
            }
        }
        ?>
        
        <?php if (count($piloti) > 0): ?>
        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>Nome</th>
                    <th>N° Gara</th>
                    <th>Categoria</th>
                    <th>Età</th>
                    <th>Contatto</th>
                </tr>
            </thead>
            <tbody>
                <?php foreach($piloti as $index => $pilota): ?>
                <tr>
                    <td><?php echo $index + 1; ?></td>
                    <td><?php echo $pilota['nome'] . ' ' . $pilota['cognome']; ?></td>
                    <td><strong>#<?php echo $pilota['numero_gara']; ?></strong></td>
                    <td><span class="pill"><?php echo $pilota['categoria']; ?></span></td>
                    <td><?php echo $pilota['classe_eta'] ?? 'N/D'; ?></td>
                    <td><?php echo $pilota['email']; ?></td>
                </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
        <?php else: ?>
        <div class="no-piloti">
            <p>😔 Nessun pilota iscritto ancora</p>
            <p>Usa il modulo di iscrizione per aggiungere i primi piloti!</p>
            <p style="margin-top: 20px;">
                <a href="iscrizione_pilota.php" style="background: #FF0000; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                    + Aggiungi Pilota
                </a>
            </p>
        </div>
        <?php endif; ?>
    </div>
    
    <script>
        // Script per far sparire i messaggi di stato dopo 5 secondi
        document.addEventListener('DOMContentLoaded', function() {
            const statusMessages = document.querySelectorAll('.status-message');
            if (statusMessages.length > 0) {
                setTimeout(function() {
                    statusMessages.forEach(function(message) {
                        message.style.opacity = '0';
                        message.style.transition = 'opacity 1s ease-out';
                    });
                }, 5000);
            }
        });
    </script>
</body>
</html>