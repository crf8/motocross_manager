<?php
session_start();
if (!isset($_SESSION['user'])) {
    header('Location: login.php');
    exit();
}

require_once '../config/database.php';
$db = new Database();
$data = $db->readData();

$pilota_id = $_GET['id'];
$pilota = null;

// Cerchiamo il pilota appena iscritto
foreach($data['piloti'] as $p) {
    if ($p['id'] == $pilota_id) {
        $pilota = $p;
        break;
    }
}

if (!$pilota) {
    header('Location: lista_piloti.php');
    exit();
}
?>

<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <title>Iscrizione Completata</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #0a0a0a;
            color: white;
            padding: 20px;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            background: #1a1a1a;
            padding: 30px;
            border-radius: 10px;
            text-align: center;
        }
        h1 {
            color: #FF0000;
            margin-bottom: 20px;
        }
        .success {
            color: #00FF00;
            font-size: 1.5em;
            margin-bottom: 30px;
        }
        .options {
            margin-top: 30px;
        }
        .button-row {
            display: flex;
            gap: 20px;
            justify-content: center;
            margin-bottom: 20px;
        }
        .btn {
            padding: 15px 30px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            color: white;
            text-decoration: none;
        }
        .btn-email {
            background: #0066cc;
        }
        .btn-whatsapp {
            background: #25D366;
        }
        .btn-pdf {
            background: #FF0000;
        }
        .btn-done {
            background: #666;
        }
        .pilot-info {
            border: 1px solid #333;
            padding: 20px;
            margin-bottom: 20px;
            text-align: left;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Iscrizione Completata! 🏁</h1>
        <div class="success">
            ✅ Pilota iscritto con successo!
        </div>
        
        <div class="pilot-info">
            <h3>Dettagli Iscrizione:</h3>
            <p><strong>Nome:</strong> <?php echo $pilota['nome'] . ' ' . $pilota['cognome']; ?></p>
            <p><strong>Numero Gara:</strong> #<?php echo $pilota['numero_gara']; ?></p>
            <p><strong>Categoria:</strong> <?php echo $pilota['categoria']; ?></p>
            <p><strong>Email:</strong> <?php echo $pilota['email']; ?></p>
            <p><strong>Telefono:</strong> <?php echo $pilota['telefono']; ?></p>
        </div>
        
        <h3>Cosa vuoi fare ora?</h3>
        <div class="options">
            <div class="button-row">
                <a href="invia_email.php?id=<?php echo $pilota['id']; ?>" class="btn btn-email">
                    📧 Invia Email
                </a>
                <a href="invia_whatsapp.php?id=<?php echo $pilota['id']; ?>" class="btn btn-whatsapp">
                    📱 Invia WhatsApp
                </a>
            </div>
            
            <div class="button-row">
                <a href="stampa_pdf.php?id=<?php echo $pilota['id']; ?>" class="btn btn-pdf">
                    📄 Stampa PDF
                </a>
                <a href="../index.php" class="btn btn-done">
                    ✓ Fine
                </a>
            </div>
        </div>
    </div>
</body>
</html>