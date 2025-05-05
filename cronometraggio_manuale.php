<?php
session_start();
if (!isset($_SESSION['user'])) {
    header('Location: login.php');
    exit();
}

require_once '../config/database.php';
$db = new Database();
$data = $db->readData();

$evento_id = $_GET['evento'] ?? 0;
$sessione = $_GET['sessione'] ?? '';

// Cerchiamo l'evento
$evento = null;
foreach($data['eventi'] as $e) {
    if ($e['id'] == $evento_id) {
        $evento = $e;
        break;
    }
}

if (!$evento || empty($sessione)) {
    header('Location: cronometraggio.php');
    exit();
}

// Gestione dei tempi (quando il form viene inviato)
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    if ($_POST['action'] == 'add_time') {
        $numero_gara = $_POST['numero_gara'];
        $tempo = $_POST['tempo'];
        
        // Aggiungiamo il tempo al database
        if (!isset($data['tempi'])) {
            $data['tempi'] = [];
        }
        
        $data['tempi'][] = [
            'id' => count($data['tempi']) + 1,
            'evento_id' => $evento_id,
            'sessione' => $sessione,
            'numero_gara' => $numero_gara,
            'tempo' => $tempo,
            'timestamp' => date('Y-m-d H:i:s')
        ];
        
        $db->saveData($data);
    }
}

// Prendiamo i tempi per questa sessione
$tempi_sessione = [];
foreach($data['tempi'] ?? [] as $tempo) {
    if ($tempo['evento_id'] == $evento_id && $tempo['sessione'] == $sessione) {
        $tempi_sessione[] = $tempo;
    }
}

// Prendiamo tutti i piloti
$piloti = $data['piloti'] ?? [];
?>

<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <title>Cronometraggio Manuale - <?php echo $sessione; ?></title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #0a0a0a;
            color: white;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 30px;
        }
        .timing-panel {
            background: #1a1a1a;
            padding: 30px;
            border-radius: 10px;
            border: 2px solid #FF0000;
        }
        .timing-display {
            font-size: 4em;
            color: #00ff00;
            text-align: center;
            margin: 20px 0;
            background: #000;
            padding: 20px;
            border-radius: 10px;
            font-family: monospace;
        }
        .number-input {
            width: 100%;
            height: 60px;
            font-size: 2em;
            text-align: center;
            background: #333;
            border: 2px solid #FFD700;
            color: white;
            border-radius: 10px;
            margin: 20px 0;
        }
        .action-buttons {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-top: 20px;
        }
        .button {
            padding: 20px;
            font-size: 1.5em;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .button-lap {
            background: #00ff00;
            color: black;
        }
        .button-back {
            background: #666;
            color: white;
        }
        .timing-list {
            background: #1a1a1a;
            padding: 20px;
            border-radius: 10px;
            height: calc(100vh - 100px);
            overflow-y: auto;
        }
        .timing-row {
            background: #2a2a2a;
            margin: 10px 0;
            padding: 15px;
            border-radius: 5px;
            display: grid;
            grid-template-columns: 1fr 2fr 1fr;
            gap: 10px;
            align-items: center;
        }
        .pilot-name {
            font-weight: bold;
            color: #FFD700;
        }
        .lap-time {
            font-family: monospace;
            font-size: 1.2em;
            color: #00ff00;
        }
        .status-bar {
            background: #333;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Pannello Cronometraggio -->
        <div class="timing-panel">
            <h2>Cronometraggio Manuale</h2>
            
            <div class="status-bar">
                <div>
                    <strong>Sessione:</strong> <?php echo $sessione; ?>
                </div>
                <div>
                    <strong>Categoria:</strong> <?php echo implode(', ', $evento['categorie']); ?>
                </div>
            </div>
            
            <div class="timing-display" id="timer">00:00.00</div>
            
            <form method="POST" id="timing-form">
                <input type="hidden" name="action" value="add_time">
                <input type="hidden" name="tempo" id="tempo_input">
                <input type="text" id="number-input" name="numero_gara" class="number-input" 
                       placeholder="Inserisci numero..." autofocus>
                
                <div class="action-buttons">
                    <button type="submit" class="button button-lap" id="submit-btn">
                        REGISTRA (ENTER)
                    </button>
                    <a href="cronometraggio_sessione.php?id=<?php echo $evento_id; ?>" class="button button-back">
                        MENU (ESC)
                    </a>
                </div>
            </form>
        </div>
        
        <!-- Lista Tempi Live -->
        <div class="timing-list">
            <h2>Tempi Live</h2>
            <?php foreach(array_reverse($tempi_sessione) as $tempo): ?>
                <?php
                // Cerchiamo le informazioni del pilota
                $pilota_info = null;
                foreach($piloti as $p) {
                    if ($p['numero_gara'] == $tempo['numero_gara']) {
                        $pilota_info = $p;
                        break;
                    }
                }
                ?>
                <div class="timing-row">
                    <div>
                        <strong>#<?php echo $tempo['numero_gara']; ?></strong>
                    </div>
                    <div class="pilot-name">
                        <?php 
                        if ($pilota_info) {
                            echo $pilota_info['nome'] . ' ' . $pilota_info['cognome'];
                        } else {
                            echo "Pilota #{$tempo['numero_gara']}";
                        }
                        ?>
                    </div>
                    <div class="lap-time">
                        <?php echo $tempo['tempo']; ?>
                    </div>
                </div>
            <?php endforeach; ?>
        </div>
    </div>
    
    <script>
        // Cronometro
        let timer;
        let startTime = Date.now();
        
        // Avvia il timer
        function startTimer() {
            timer = setInterval(updateDisplay, 10);
        }
        
        // Aggiorna display del timer
        function updateDisplay() {
            const elapsed = Date.now() - startTime;
            const minutes = Math.floor(elapsed / 60000);
            const seconds = Math.floor((elapsed % 60000) / 1000);
            const ms = Math.floor((elapsed % 1000) / 10);
            
            document.getElementById('timer').textContent = 
                `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}.${ms.toString().padStart(2, '0')}`;
        }
        
        // Gestione invio form
        document.getElementById('timing-form').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const numberInput = document.getElementById('number-input');
            const number = numberInput.value.trim();
            
            if (!number) return;
            
            // Prendi il tempo attuale
            const elapsed = Date.now() - startTime;
            const minutes = Math.floor(elapsed / 60000);
            const seconds = Math.floor((elapsed % 60000) / 1000);
            const ms = Math.floor((elapsed % 1000) / 10);
            
            const tempo = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}.${ms.toString().padStart(2, '0')}`;
            
            // Imposta il valore nel campo hidden
            document.getElementById('tempo_input').value = tempo;
            
            // Invia il form
            this.submit();
        });
        
        // Gestione tastiera
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                document.getElementById('submit-btn').click();
            }
        });
        
        // Avvia il timer quando la pagina è caricata
        window.onload = startTimer;
    </script>
</body>
</html>