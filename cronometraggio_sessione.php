<?php
session_start();
if (!isset($_SESSION['user'])) {
    header('Location: login.php');
    exit();
}

require_once '../config/database.php';
$db = new Database();
$data = $db->readData();

$evento_id = $_GET['id'] ?? 0;
$evento = null;

// Cerchiamo l'evento
foreach($data['eventi'] as $e) {
    if ($e['id'] == $evento_id) {
        $evento = $e;
        break;
    }
}

if (!$evento) {
    header('Location: cronometraggio.php');
    exit();
}
?>

<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <title>Sistema di Cronometraggio - <?php echo $evento['nome_evento']; ?></title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #0a0a0a;
            color: white;
            padding: 20px;
        }
        .container {
            max-width: 1600px;
            margin: 0 auto;
        }
        .header {
            background: rgba(26, 26, 26, 0.9);
            padding: 20px 0;
            margin-bottom: 40px;
            border-bottom: 2px solid #FF0000;
        }
        h1 {
            text-align: center;
            color: #FF0000;
            font-size: 3em;
            text-shadow: 0 0 10px rgba(255, 0, 0, 0.5);
        }
        .event-info {
            background: #1a1a1a;
            border: 2px solid #FFD700;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 40px;
        }
        .event-info h2 {
            color: #FFD700;
            margin-bottom: 10px;
        }
        .session-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 25px;
            margin-bottom: 50px;
        }
        .session-card {
            background: #1a1a1a;
            border: 3px solid #666;
            border-radius: 20px;
            padding: 25px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
        }
        .session-card:hover {
            transform: translateY(-10px);
            border-color: #FF0000;
            box-shadow: 0 15px 30px rgba(255, 0, 0, 0.2);
        }
        .session-icon {
            font-size: 3em;
            margin-bottom: 15px;
        }
        .session-card h3 {
            font-size: 1.5em;
            margin-bottom: 8px;
        }
        .session-time {
            font-size: 1.2em;
            margin-bottom: 15px;
            color: #888;
        }
        .timing-btn {
            background: linear-gradient(to right, #FF0000, #FF4500);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>⏱️ Sistema di Cronometraggio</h1>
    </div>

    <div class="container">
        <a href="cronometraggio.php" style="background: #666; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin-bottom: 20px;">← Torna alla Lista Eventi</a>

        <div class="event-info">
            <h2>🏁 Evento: <?php echo $evento['nome_evento']; ?></h2>
            <p><strong>Data:</strong> <?php echo date('d/m/Y', strtotime($evento['data_evento'])); ?></p>
            <p><strong>Località:</strong> <?php echo $evento['luogo']; ?></p>
            <p><strong>Categorie:</strong> <?php echo implode(', ', $evento['categorie']); ?></p>
        </div>
        
        <h2 style="margin-bottom: 20px; color: #FFD700; font-size: 1.8em;">Sessioni Disponibili</h2>
        <div class="session-grid">
            <div class="session-card">
                <div class="session-icon">🚥</div>
                <h3>Prove Libere</h3>
                <p class="session-time"><?php echo $evento['ora_prove_libere']; ?></p>
                <a href="cronometraggio_manuale.php?evento=<?php echo $evento_id; ?>&sessione=prove_libere" class="timing-btn">
                    Cronometra Sessione
                </a>
            </div>
            
            <div class="session-card">
                <div class="session-icon">🎯</div>
                <h3>Qualifiche</h3>
                <p class="session-time"><?php echo $evento['ora_qualifiche']; ?></p>
                <a href="cronometraggio_manuale.php?evento=<?php echo $evento_id; ?>&sessione=qualifiche" class="timing-btn">
                    Cronometra Sessione
                </a>
            </div>
            
            <div class="session-card">
                <div class="session-icon">🏆</div>
                <h3>Manche 1</h3>
                <p class="session-time"><?php echo $evento['ora_gare']; ?></p>
                <a href="cronometraggio_manuale.php?evento=<?php echo $evento_id; ?>&sessione=manche_1" class="timing-btn">
                    Cronometra Sessione
                </a>
            </div>
            
            <div class="session-card">
                <div class="session-icon">🏁</div>
                <h3>Manche 2</h3>
                <p class="session-time">15:30</p>
                <a href="cronometraggio_manuale.php?evento=<?php echo $evento_id; ?>&sessione=manche_2" class="timing-btn">
                    Cronometra Sessione
                </a>
            </div>
        </div>
    </div>
</body>
</html>