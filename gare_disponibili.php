<?php
// Visualizza tutti gli errori per il debug
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

session_start();
if (!isset($_SESSION['user'])) {
    header('Location: login.php');
    exit();
}

// Includiamo la classe del database
require_once '../config/MongoCompatDB.php';
$db = new MongoCompatDB();

// Recuperiamo l'ID dell'evento dalla URL
$evento_id = $_GET['evento'] ?? 0;
if (!$evento_id) {
    header('Location: cronometraggio.php');
    exit();
}

// Recuperiamo l'evento
$eventi = $db->readCollection('eventi');
$evento = null;
foreach ($eventi as $e) {
    if ($e['id'] == $evento_id) {
        $evento = $e;
        break;
    }
}

if (!$evento) {
    header('Location: cronometraggio.php');
    exit();
}

// Recuperiamo tutti i piloti iscritti a questo evento
$iscrizioni = $db->readCollection('iscrizioni');
$piloti_iscritti = [];
foreach ($iscrizioni as $iscrizione) {
    if ($iscrizione['evento_id'] == $evento_id) {
        $piloti_iscritti[] = $iscrizione;
    }
}

// Recuperiamo i dettagli dei piloti
$tutti_piloti = $db->readCollection('piloti');
$piloti_completi = [];
foreach ($piloti_iscritti as $iscrizione) {
    foreach ($tutti_piloti as $pilota) {
        if ($pilota['id'] == $iscrizione['pilota_id']) {
            // Aggiungiamo la categoria dall'iscrizione al pilota
            $pilota['categoria'] = $iscrizione['categoria'];
            $piloti_completi[] = $pilota;
            break;
        }
    }
}

// Recuperiamo i gruppi esistenti (se presenti)
$gruppi_esistenti = $db->findDocuments('gruppi', ['evento_id' => $evento_id]);

// Funzione per creare gruppi automaticamente
function creaGruppiAutomatici($piloti, $evento_id) {
    // Organizza piloti per categoria
    $piloti_per_categoria = [];
    foreach ($piloti as $pilota) {
        $categoria = $pilota['categoria'];
        if (!isset($piloti_per_categoria[$categoria])) {
            $piloti_per_categoria[$categoria] = [];
        }
        $piloti_per_categoria[$categoria][] = $pilota;
    }
    
    // Per ogni categoria, dividi in gruppi da massimo 40 piloti
    $gruppi = [];
    foreach ($piloti_per_categoria as $categoria => $piloti_categoria) {
        $num_piloti = count($piloti_categoria);
        
        // Se meno di 40 piloti, un solo gruppo
        if ($num_piloti <= 40) {
            $gruppi[] = [
                'evento_id' => $evento_id,
                'categoria' => $categoria,
                'nome_gruppo' => 'Gruppo Unico',
                'piloti' => array_column($piloti_categoria, 'id')
            ];
        } else {
            // Calcola quanti gruppi servono
            $num_gruppi = ceil($num_piloti / 40);
            $piloti_per_gruppo = ceil($num_piloti / $num_gruppi);
            
            // Lettere per i gruppi
            $lettere_gruppi = ['A', 'B', 'C', 'D', 'E', 'F'];
            
            // Dividi i piloti nei gruppi
            $piloti_divisi = array_chunk($piloti_categoria, $piloti_per_gruppo);
            
            // Crea i gruppi
            for ($i = 0; $i < count($piloti_divisi); $i++) {
                $gruppi[] = [
                    'evento_id' => $evento_id,
                    'categoria' => $categoria,
                    'nome_gruppo' => 'Gruppo ' . $lettere_gruppi[$i],
                    'piloti' => array_column($piloti_divisi[$i], 'id')
                ];
            }
        }
    }
    
    return $gruppi;
}

// Gestione del form POST
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    if (isset($_POST['action']) && $_POST['action'] == 'crea_gruppi') {
        // Elimina i gruppi esistenti per questo evento
        foreach ($gruppi_esistenti as $gruppo) {
            $db->deleteDocument('gruppi', $gruppo['id']);
        }
        
        // Crea nuovi gruppi
        $nuovi_gruppi = creaGruppiAutomatici($piloti_completi, $evento_id);
        
        // Salva i gruppi nel database
        foreach ($nuovi_gruppi as $gruppo) {
            $db->insertDocument('gruppi', $gruppo);
        }
        
        // Reindirizza per evitare il problema del refresh
        header("Location: gestione_gruppi.php?evento=$evento_id&success=1");
        exit();
    }
}

// Ottieni i gruppi aggiornati (anche dopo la creazione)
$gruppi = $db->findDocuments('gruppi', ['evento_id' => $evento_id]);
?>

<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gestione Gruppi - <?php echo htmlspecialchars($evento['nome_evento']); ?></title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #2563eb;
            --accent: #f43f5e;
            --dark: #0f172a;
            --light: #f8fafc;
            --gray: #cbd5e1;
            --text: #1e293b;
            --success: #10b981;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Roboto', sans-serif;
            background-color: var(--light);
            color: var(--text);
            line-height: 1.5;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid var(--gray);
        }
        
        .header h1 {
            font-size: 2rem;
            margin-bottom: 10px;
            color: var(--primary);
        }
        
        .event-info {
            background-color: white;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }
        
        .event-info p {
            margin: 5px 0;
        }
        
        .btn-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 20px;
        }
        
        .btn {
            padding: 10px 20px;
            border-radius: 6px;
            font-weight: 500;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
        }
        
        .btn-primary {
            background-color: var(--primary);
            color: white;
            border: none;
        }
        
        .btn-secondary {
            background-color: var(--dark);
            color: white;
        }
        
        .alert {
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 20px;
        }
        
        .alert-success {
            background-color: var(--success);
            color: white;
        }
        
        .groups-container {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        
        .group-card {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }
        
        .group-header {
            background-color: var(--primary);
            color: white;
            padding: 15px;
            font-weight: 500;
            display: flex;
            justify-content: space-between;
        }
        
        .group-body {
            padding: 15px;
        }
        
        .pilot-list {
            max-height: 300px;
            overflow-y: auto;
        }
        
        .pilot-item {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid var(--gray);
        }
        
        .pilot-item:last-child {
            border-bottom: none;
        }
        
        .pilot-number {
            background-color: var(--dark);
            color: white;
            padding: 2px 8px;
            border-radius: 4px;
            font-weight: 500;
        }
        
        .empty-state {
            text-align: center;
            padding: 40px;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        .empty-state h3 {
            font-size: 1.5rem;
            margin-bottom: 10px;
        }
        
        .stats {
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .stat-box {
            flex: 1;
            background-color: white;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        
        .stat-number {
            font-size: 2rem;
            font-weight: 700;
            color: var(--primary);
        }
        
        .stat-label {
            color: var(--text);
            font-size: 0.9rem;
        }
        
        @media (max-width: 768px) {
            .stats {
                flex-direction: column;
            }
            
            .group-card {
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Gestione Gruppi</h1>
            <p>Evento: <?php echo htmlspecialchars($evento['nome_evento']); ?></p>
        </div>
        
        <div class="event-info">
            <p><strong>Data:</strong> <?php echo date('d/m/Y', strtotime($evento['data_evento'])); ?></p>
            <p><strong>Luogo:</strong> <?php echo htmlspecialchars($evento['luogo']); ?></p>
            <p><strong>Categorie:</strong> <?php echo implode(', ', $evento['categorie']); ?></p>
        </div>
        
        <?php if (isset($_GET['success'])): ?>
            <div class="alert alert-success">
                Gruppi creati con successo!
            </div>
        <?php endif; ?>
        
        <div class="btn-row">
            <a href="cronometraggio_sessione.php?id=<?php echo $evento_id; ?>" class="btn btn-secondary">← Torna alle Sessioni</a>
            
            <form method="POST">
                <input type="hidden" name="action" value="crea_gruppi">
                <button type="submit" class="btn btn-primary">Crea Gruppi Automaticamente</button>
            </form>
        </div>
        
        <div class="stats">
            <div class="stat-box">
                <div class="stat-number"><?php echo count($piloti_completi); ?></div>
                <div class="stat-label">Piloti Iscritti</div>
            </div>
            
            <div class="stat-box">
                <div class="stat-number"><?php echo count($gruppi); ?></div>
                <div class="stat-label">Gruppi Creati</div>
            </div>
            
            <div class="stat-box">
                <div class="stat-number">
                    <?php
                    $categorie = [];
                    foreach ($piloti_completi as $pilota) {
                        if (!in_array($pilota['categoria'], $categorie)) {
                            $categorie[] = $pilota['categoria'];
                        }
                    }
                    echo count($categorie);
                    ?>
                </div>
                <div class="stat-label">Categorie</div>
            </div>
        </div>
        
        <?php if (count($gruppi) > 0): ?>
            <div class="groups-container">
                <?php foreach ($gruppi as $gruppo): ?>
                    <div class="group-card">
                        <div class="group-header">
                            <div><?php echo htmlspecialchars($gruppo['nome_gruppo']); ?></div>
                            <div><?php echo htmlspecialchars($gruppo['categoria']); ?></div>
                        </div>
                        <div class="group-body">
                            <p>Numero piloti: <?php echo count($gruppo['piloti']); ?></p>
                            
                            <div class="pilot-list">
                                <?php foreach ($gruppo['piloti'] as $pilota_id): ?>
                                    <?php
                                    // Troviamo i dettagli del pilota
                                    $pilota_info = null;
                                    foreach ($tutti_piloti as $pilota) {
                                        if ($pilota['id'] == $pilota_id) {
                                            $pilota_info = $pilota;
                                            break;
                                        }
                                    }
                                    
                                    if ($pilota_info):
                                    ?>
                                    <div class="pilot-item">
                                        <div>
                                            <?php echo htmlspecialchars($pilota_info['nome'] . ' ' . $pilota_info['cognome']); ?>
                                        </div>
                                        <div class="pilot-number">
                                            #<?php echo htmlspecialchars($pilota_info['numero_gara']); ?>
                                        </div>
                                    </div>
                                    <?php endif; ?>
                                <?php endforeach; ?>
                            </div>
                        </div>
                    </div>
                <?php endforeach; ?>
            </div>
        <?php else: ?>
            <div class="empty-state">
                <h3>Nessun gruppo creato</h3>
                <p>Clicca su "Crea Gruppi Automaticamente" per generare i gruppi secondo il regolamento.</p>
            </div>
        <?php endif; ?>
    </div>
</body>
</html>