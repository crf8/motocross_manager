<?php
session_start();
if (!isset($_SESSION['user'])) {
    header('Location: login.php');
    exit();
}

require_once '../config/database.php';
$db = new Database();
$data = $db->readData();
$piloti = $data['piloti'];
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
    </style>
</head>
<body>
    <div class="container">
        <a href="../index.php" class="back-button">← Torna alla Dashboard</a>
        
        <h1>Lista Piloti Iscritti</h1>
        
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
                    <td><?php echo $pilota['classe_eta']; ?></td>
                    <td><?php echo $pilota['email']; ?></td>
                </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
        <?php else: ?>
        <div class="no-piloti">
            <p>😔 Nessun pilota iscritto ancora</p>
            <p>Usa il modulo di iscrizione per aggiungere i primi piloti!</p>
        </div>
        <?php endif; ?>
    </div>
</body>
</html>