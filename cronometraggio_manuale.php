<?php
session_start();
if (!isset($_SESSION['user'])) {
    header('Location: login.php');
    exit();
}

// Usiamo la nuova classe MongoCompatDB
require_once '../config/MongoCompatDB.php';
$db = new MongoCompatDB();

$evento_id = $_GET['evento'] ?? 0;
$sessione = $_GET['sessione'] ?? '';
$gruppo_id = $_GET['gruppo'] ?? 0;
$categoria_selezionata = $_GET['categoria'] ?? '';
$is_supercampione = isset($_GET['supercampione']) && $_GET['supercampione'] == '1';

// Cerchiamo l'evento
$evento = null;
foreach($db->readCollection('eventi') as $e) {
    if ($e['id'] == $evento_id) {
        $evento = $e;
        break;
    }
}

if (!$evento || empty($sessione)) {
    header('Location: cronometraggio.php');
    exit();
}

// Recuperiamo i gruppi disponibili per questo evento
$gruppi = $db->findDocuments('gruppi', ['evento_id' => $evento_id]);

// Se è selezionato un gruppo, recuperiamo i suoi dettagli
$gruppo_selezionato = null;
$piloti_gruppo = [];
if ($gruppo_id > 0) {
    foreach ($gruppi as $g) {
        if ($g['id'] == $gruppo_id) {
            $gruppo_selezionato = $g;
            break;
        }
    }
}

// Durata predefinita in minuti per la sessione
$durata_predefinita = 15;
if ($sessione == 'manche_1' || $sessione == 'manche_2') {
    $durata_predefinita = 20;
}
// Durata per la supercampione (generalmente più lunga)
if ($is_supercampione) {
    $durata_predefinita = 25; // 25 minuti per la Supercampione
}

// Gestione durata personalizzata
$durata_sessione = isset($_GET['durata']) ? intval($_GET['durata']) : $durata_predefinita;

// Prendiamo tutti i piloti
$tutti_piloti = $db->readCollection('piloti');

// Se abbiamo un gruppo selezionato, filtriamo i piloti di quel gruppo
$piloti = [];
$numeri_gara_validi = [];

if ($gruppo_selezionato) {
    foreach ($tutti_piloti as $pilota) {
        if (in_array($pilota['id'], $gruppo_selezionato['piloti'])) {
            // Se è stata selezionata una categoria, filtriamo per categoria
            if (!empty($categoria_selezionata) && isset($pilota['categoria']) && $pilota['categoria'] != $categoria_selezionata) {
                continue;
            }
            
            // Se è supercampione, filtriamo solo i migliori piloti
            if ($is_supercampione) {
                // I piloti supercampione potrebbero essere identificati da un campo specifico 
                // o in base a qualche criterio (ad esempio, i primi classificati di ogni categoria)
                if (!(isset($pilota['supercampione']) && $pilota['supercampione']) && 
                    !(isset($pilota['ranking']) && $pilota['ranking'] <= 10)) {
                    continue;
                }
            }
            
            $piloti[] = $pilota;
            $numeri_gara_validi[] = $pilota['numero_gara'];
        }
    }
} else {
    foreach ($tutti_piloti as $pilota) {
        // Se è stata selezionata una categoria, filtriamo per categoria
        if (!empty($categoria_selezionata) && isset($pilota['categoria']) && $pilota['categoria'] != $categoria_selezionata) {
            continue;
        }
        
        // Se è supercampione, filtriamo solo i migliori piloti
        if ($is_supercampione) {
            if (!(isset($pilota['supercampione']) && $pilota['supercampione']) && 
                !(isset($pilota['ranking']) && $pilota['ranking'] <= 10)) {
                continue;
            }
        }
        
        $piloti[] = $pilota;
        $numeri_gara_validi[] = $pilota['numero_gara'];
    }
}

// Estraiamo le categorie uniche dai piloti per il menu a tendina
$categorie_disponibili = [];
foreach ($tutti_piloti as $pilota) {
    if (isset($pilota['categoria']) && !in_array($pilota['categoria'], $categorie_disponibili)) {
        $categorie_disponibili[] = $pilota['categoria'];
    }
}
// Aggiungiamo la categoria Supercampione
if (!in_array('Supercampione', $categorie_disponibili)) {
    $categorie_disponibili[] = 'Supercampione';
}
sort($categorie_disponibili);

// Aggiungiamo anche le categorie dell'evento
if (isset($evento['categorie']) && is_array($evento['categorie'])) {
    foreach ($evento['categorie'] as $cat) {
        if (!in_array($cat, $categorie_disponibili)) {
            $categorie_disponibili[] = $cat;
        }
    }
    sort($categorie_disponibili);
}

// Messaggi di errore o conferma
$error_message = '';
$success_message = '';
$salvato_con_successo = false;

// Gestione dei tempi (quando il form viene inviato)
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    if ($_POST['action'] == 'add_time') {
        $numero_gara = $_POST['numero_gara'];
        $tempo = $_POST['tempo'];
        
        // Verifica se il numero di gara è valido
        if (!in_array($numero_gara, $numeri_gara_validi)) {
            $error_message = "Errore: Il numero #$numero_gara non è associato a nessun pilota in questo gruppo";
        } else {
            // Aggiungiamo il tempo al database
            $nuovo_tempo = [
                'evento_id' => $evento_id,
                'sessione' => $sessione,
                'gruppo_id' => $gruppo_id > 0 ? $gruppo_id : null,
                'numero_gara' => $numero_gara,
                'tempo' => $tempo,
                'timestamp' => date('Y-m-d H:i:s'),
                'supercampione' => $is_supercampione ? true : false
            ];
            
            $db->insertDocument('tempi', $nuovo_tempo);
            $success_message = "Tempo registrato con successo per il pilota #$numero_gara";
        }
    }
    else if ($_POST['action'] == 'delete_time') {
        $tempo_id = $_POST['tempo_id'];
        
        // Elimina il tempo dal database
        $db->deleteDocument('tempi', $tempo_id);
        $success_message = "Tempo eliminato con successo";
    }
    else if ($_POST['action'] == 'finish_session') {
        // Aggiorniamo lo stato della sessione
        $session_data = [
            'evento_id' => $evento_id,
            'sessione' => $sessione,
            'gruppo_id' => $gruppo_id > 0 ? $gruppo_id : null,
            'categoria' => $categoria_selezionata,
            'stato' => 'completata',
            'data_completamento' => date('Y-m-d H:i:s'),
            'supercampione' => $is_supercampione ? true : false
        ];
        
        $db->insertDocument('sessioni_completate', $session_data);
        $salvato_con_successo = true;
        $success_message = "Sessione salvata con successo! La classifica è ora disponibile.";
    }
}

// Prendiamo i tempi per questa sessione e gruppo (se selezionato)
$tempi_query = [
    'evento_id' => $evento_id,
    'sessione' => $sessione
];

// Se c'è un gruppo selezionato, filtriamo per gruppo
if ($gruppo_id > 0) {
    $tempi_query['gruppo_id'] = $gruppo_id;
}

// Se è supercampione, filtriamo solo i tempi della supercampione
if ($is_supercampione) {
    $tempi_query['supercampione'] = true;
}

$tempi_sessione = $db->findDocuments('tempi', $tempi_query);

// Calcoliamo statistiche dei tempi per pilota
$tempi_piloti = [];
foreach ($tempi_sessione as $tempo) {
    $numero_gara = $tempo['numero_gara'];
    
    if (!isset($tempi_piloti[$numero_gara])) {
        $tempi_piloti[$numero_gara] = [
            'tempi' => [],
            'media' => 0,
            'migliore' => null,
            'numero_gara' => $numero_gara
        ];
    }
    
    $tempi_piloti[$numero_gara]['tempi'][] = $tempo;
    
    // Convertiamo il tempo in secondi per i calcoli
    list($minuti, $resto) = explode(':', $tempo['tempo']);
    list($secondi, $millisecondi) = explode('.', $resto);
    $tempo_secondi = ($minuti * 60) + $secondi + ($millisecondi / 100);
    
    // Aggiorniamo il tempo migliore se necessario
    if ($tempi_piloti[$numero_gara]['migliore'] === null || $tempo_secondi < $tempi_piloti[$numero_gara]['migliore_secondi']) {
        $tempi_piloti[$numero_gara]['migliore'] = $tempo['tempo'];
        $tempi_piloti[$numero_gara]['migliore_secondi'] = $tempo_secondi;
        $tempi_piloti[$numero_gara]['migliore_id'] = $tempo['id'];
    }
}

// Calcoliamo le medie e conteggio giri
foreach ($tempi_piloti as $numero_gara => &$dati) {
    $totale_secondi = 0;
    $count = count($dati['tempi']);
    
    foreach ($dati['tempi'] as $tempo) {
        list($minuti, $resto) = explode(':', $tempo['tempo']);
        list($secondi, $millisecondi) = explode('.', $resto);
        $tempo_secondi = ($minuti * 60) + $secondi + ($millisecondi / 100);
        
        $totale_secondi += $tempo_secondi;
    }
    
    if ($count > 0) {
        $media_secondi = $totale_secondi / $count;
        $minuti_media = floor($media_secondi / 60);
        $secondi_media = floor($media_secondi % 60);
        $millisecondi_media = round(($media_secondi - floor($media_secondi)) * 100);
        
        $dati['media'] = sprintf("%02d:%02d.%02d", $minuti_media, $secondi_media, $millisecondi_media);
        $dati['media_secondi'] = $media_secondi;
        $dati['num_giri'] = $count;
    }
    
    // Aggiungiamo anche il nome del pilota per riferimento
    foreach ($piloti as $pilota) {
        if ($pilota['numero_gara'] == $numero_gara) {
            $dati['nome_pilota'] = $pilota['nome'] . ' ' . $pilota['cognome'];
            $dati['categoria'] = $pilota['categoria'] ?? 'N/D';
            break;
        }
    }
}
unset($dati); // Rompiamo il riferimento

// Troviamo il giro più veloce della sessione
$giro_piu_veloce = null;
$tempo_piu_veloce = PHP_INT_MAX;
$pilota_piu_veloce = null;

foreach ($tempi_piloti as $numero_gara => $dati) {
    if (isset($dati['migliore_secondi']) && $dati['migliore_secondi'] < $tempo_piu_veloce) {
        $tempo_piu_veloce = $dati['migliore_secondi'];
        $giro_piu_veloce = $dati['migliore'];
        $pilota_piu_veloce = $dati;
    }
}

// Ordiniamo i tempi in base al tempo migliore
uasort($tempi_piloti, function($a, $b) {
    if (!isset($a['migliore_secondi']) && !isset($b['migliore_secondi'])) {
        return 0;
    }
    if (!isset($a['migliore_secondi'])) {
        return 1;
    }
    if (!isset($b['migliore_secondi'])) {
        return -1;
    }
    return $a['migliore_secondi'] <=> $b['migliore_secondi'];
});

// Recuperiamo anche tutti i piloti per la classifica completa
// indipendentemente se hanno tempi registrati o meno
$tutti_piloti_classifica = [];
foreach ($piloti as $pilota) {
    if (!empty($categoria_selezionata) && isset($pilota['categoria']) && $pilota['categoria'] != $categoria_selezionata && $categoria_selezionata != 'Supercampione') {
        continue;
    }
    
    // Se stiamo visualizzando la supercampione, includiamo solo i piloti supercampione
    if ($is_supercampione) {
        if (!(isset($pilota['supercampione']) && $pilota['supercampione']) && 
            !(isset($pilota['ranking']) && $pilota['ranking'] <= 10)) {
            continue;
        }
    }
    
    $numero_gara = $pilota['numero_gara'];
    if (!isset($tempi_piloti[$numero_gara])) {
        $tutti_piloti_classifica[$numero_gara] = [
            'nome_pilota' => $pilota['nome'] . ' ' . $pilota['cognome'],
            'numero_gara' => $numero_gara,
            'categoria' => $pilota['categoria'] ?? 'N/D',
            'tempi' => [],
            'migliore' => null,
            'media' => "00:00.00",
            'num_giri' => 0
        ];
    }
}

// Combiniamo i piloti con tempi e quelli senza tempi
$classifica_completa = $tempi_piloti + $tutti_piloti_classifica;

// Riordiniamo la classifica completa (piloti con tempi in cima, poi gli altri)
uasort($classifica_completa, function($a, $b) {
    // Se entrambi hanno migliore_secondi, ordiniamo per tempo migliore
    if (isset($a['migliore_secondi']) && isset($b['migliore_secondi'])) {
        return $a['migliore_secondi'] <=> $b['migliore_secondi'];
    }
    
    // Se solo a ha migliore_secondi, a viene prima
    if (isset($a['migliore_secondi'])) {
        return -1;
    }
    
    // Se solo b ha migliore_secondi, b viene prima
    if (isset($b['migliore_secondi'])) {
        return 1;
    }
    
    // Se nessuno ha tempi, ordiniamo per numero di gara
    return $a['numero_gara'] <=> $b['numero_gara'];
});

// Funzione per formattare il nome della sessione
function formatSessione($sessione) {
    switch ($sessione) {
        case 'prove_libere': return 'Prove Libere';
        case 'qualifiche': return 'Qualifiche';
        case 'manche_1': return 'Manche 1';
        case 'manche_2': return 'Manche 2';
        case 'supercampione': return 'Supercampione';
        default: return ucfirst(str_replace('_', ' ', $sessione));
    }
}

// Stato del cronometro (iniziato o no)
$cronometro_avviato = false;
if (isset($_GET['cronometro_avviato']) && $_GET['cronometro_avviato'] == '1') {
    $cronometro_avviato = true;
}
?>

<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cronometraggio <?php echo formatSessione($sessione); ?><?php echo $is_supercampione ? ' - Supercampione' : ''; ?> - MX Pro</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Roboto+Mono:wght@400;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary: #ff3e00;
            --primary-dark: #d93500;
            --primary-light: #ff6e40;
            --secondary: #0066ff;
            --secondary-dark: #0050cc;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --dark: #1e1e1e;
            --darker: #121212;
            --light: #ffffff;
            --gray-100: #f8f9fa;
            --gray-200: #e9ecef;
            --gray-300: #dee2e6;
            --gray-400: #ced4da;
            --gray-500: #adb5bd;
            --gray-600: #6c757d;
            --gray-700: #495057;
            --gray-800: #343a40;
            --box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
            --gold: #FFD700;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Poppins', sans-serif;
            background-color: var(--darker);
            color: var(--light);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        .navbar {
            background-color: var(--dark);
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        
        .navbar-brand {
            font-weight: 700;
            font-size: 1.5rem;
            color: var(--light);
            text-decoration: none;
        }
        
        .navbar-brand span {
            color: var(--primary);
        }
        
        .container {
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 1.5rem;
            max-width: 1600px;
            margin: 0 auto;
            padding: 1.5rem;
            flex: 1;
        }
        
        .timing-panel {
            background-color: var(--dark);
            border-radius: 15px;
            padding: 1.5rem;
            box-shadow: var(--box-shadow);
            border: 2px solid <?php echo $is_supercampione ? 'var(--gold)' : 'var(--primary)'; ?>;
            display: flex;
            flex-direction: column;
        }
        
        .panel-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid var(--gray-700);
        }
        
        .panel-title {
            font-size: 1.5rem;
            font-weight: 600;
        }
        
        .status-pill {
            padding: 0.5rem 1rem;
            border-radius: 50px;
            font-size: 0.875rem;
            font-weight: 600;
            background-color: <?php echo $is_supercampione ? 'var(--gold)' : 'var(--primary)'; ?>;
            color: <?php echo $is_supercampione ? 'var(--dark)' : 'var(--light)'; ?>;
        }
        
        .supercampione-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            background: linear-gradient(135deg, var(--gold), #FFA500);
            color: var(--dark);
            padding: 0.5rem 1rem;
            border-radius: 50px;
            font-weight: 700;
            font-size: 0.9rem;
            box-shadow: 0 4px 8px rgba(255, 215, 0, 0.3);
            margin-left: 1rem;
        }
        
        .status-bar {
            background-color: var(--darker);
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1.5rem;
            display: flex;
            justify-content: space-between;
            font-size: 0.875rem;
            flex-wrap: wrap;
            gap: 0.5rem;
        }
        
        .status-item {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .status-icon {
            width: 24px;
            height: 24px;
            background-color: var(--gray-700);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.75rem;
        }
        
        .timer-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            margin-bottom: 1.5rem;
        }
        
        .timing-display {
            font-family: 'Roboto Mono', monospace;
            font-size: 4rem;
            font-weight: 700;
            text-align: center;
            background-color: var(--darker);
            color: <?php echo $is_supercampione ? 'var(--gold)' : 'var(--success)'; ?>;
            padding: 2rem;
            border-radius: 10px;
            width: 100%;
            letter-spacing: 2px;
            text-shadow: 0 0 10px <?php echo $is_supercampione ? 'rgba(255, 215, 0, 0.5)' : 'rgba(16, 185, 129, 0.5)'; ?>;
            position: relative;
            overflow: hidden;
        }
        
        .countdown-display {
            font-family: 'Roboto Mono', monospace;
            font-size: 1.5rem;
            font-weight: 600;
            background-color: <?php echo $is_supercampione ? 'var(--gold)' : 'var(--primary)'; ?>;
            color: <?php echo $is_supercampione ? 'var(--dark)' : 'white'; ?>;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            margin-top: 1rem;
            margin-bottom: 1rem;
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 0.5rem;
        }
        
        .countdown-display.warning {
            background-color: var(--warning);
            animation: pulse 1s infinite;
        }
        
        .countdown-display.danger {
            background-color: var(--danger);
            animation: pulse 0.5s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.7; }
            100% { opacity: 1; }
        }
        
        .timing-display::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(to right, transparent, <?php echo $is_supercampione ? 'var(--gold)' : 'var(--success)'; ?>, transparent);
            animation: scanline 2s linear infinite;
        }
        
        @keyframes scanline {
            0% {
                transform: translateY(0);
            }
            100% {
                transform: translateY(100px);
            }
        }
        
        .group-selector {
            margin-bottom: 1.5rem;
        }
        
        .group-selector label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 500;
        }
        
        .group-selector select {
            width: 100%;
            padding: 0.75rem;
            border-radius: 8px;
            background-color: var(--darker);
            border: 1px solid var(--gray-700);
            color: var(--light);
            font-size: 1rem;
            font-family: 'Poppins', sans-serif;
        }
        
        .settings-panel {
            background-color: var(--darker);
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1.5rem;
        }
        
        .settings-title {
            font-size: 1rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: var(--gray-300);
        }
        
        .settings-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
        }
        
        .settings-item label {
            display: block;
            font-size: 0.875rem;
            margin-bottom: 0.25rem;
        }
        
        .settings-item input, .settings-item select {
            width: 100%;
            padding: 0.5rem;
            border-radius: 4px;
            background-color: var(--dark);
            border: 1px solid var(--gray-700);
            color: var(--light);
        }
        
        .message {
            padding: 0.75rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            font-size: 0.875rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .message-error {
            background-color: rgba(239, 68, 68, 0.2);
            border-left: 4px solid var(--danger);
        }
        
        .message-success {
            background-color: rgba(16, 185, 129, 0.2);
            border-left: 4px solid var(--success);
        }
        
        .number-input {
            margin-bottom: 1.5rem;
        }
        
        .number-input label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 500;
        }
        
        .number-input input {
            width: 100%;
            padding: 1rem;
            border-radius: 8px;
            background-color: var(--darker);
            border: 2px solid <?php echo $is_supercampione ? 'var(--gold)' : 'var(--primary)'; ?>;
            color: var(--light);
            font-size: 2rem;
            text-align: center;
            font-family: 'Roboto Mono', monospace;
            letter-spacing: 2px;
        }
        
        .action-buttons {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
            margin-top: auto;
        }
        
        .btn {
            padding: 1rem;
            border-radius: 8px;
            font-weight: 600;
            font-size: 1.125rem;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
            border: none;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            text-decoration: none;
        }
        
        .btn-primary {
            background-color: var(--success);
            color: var(--light);
        }
        
        .btn-primary:hover {
            background-color: #0da271;
            transform: translateY(-3px);
        }
        
        .btn-secondary {
            background-color: var(--gray-700);
            color: var(--light);
        }
        
        .btn-secondary:hover {
            background-color: var(--gray-600);
            transform: translateY(-3px);
        }
        
        .btn-danger {
            background-color: var(--danger);
            color: var(--light);
        }
        
        .btn-danger:hover {
            background-color: #dc2626;
        }
        
        .btn-start {
            background-color: <?php echo $is_supercampione ? 'var(--gold)' : 'var(--secondary)'; ?>;
            color: <?php echo $is_supercampione ? 'var(--dark)' : 'white'; ?>;
            margin-top: 1rem;
            width: 100%;
            font-size: 1.25rem;
            padding: 1.25rem;
        }
        
        .btn-start:hover {
            background-color: <?php echo $is_supercampione ? '#FFB700' : 'var(--secondary-dark)'; ?>;
            transform: translateY(-3px);
        }
        
        .btn-finish {
            background-color: <?php echo $is_supercampione ? 'var(--gold)' : 'var(--primary)'; ?>;
            color: <?php echo $is_supercampione ? 'var(--dark)' : 'white'; ?>;
            margin-top: 1rem;
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }
        
        .btn-finish:hover {
            background-color: <?php echo $is_supercampione ? '#FFB700' : 'var(--primary-dark)'; ?>;
            transform: translateY(-3px);
        }
        
        .btn-finish i {
            font-size: 1.25rem;
        }
        
        .timing-list {
            background-color: var(--dark);
            border-radius: 15px;
            padding: 1.5rem;
            box-shadow: var(--box-shadow);
            overflow: hidden;
            display: flex;
            flex-direction: column;
            <?php if ($is_supercampione): ?>
            border: 2px solid var(--gold);
            <?php endif; ?>
        }
        
        .list-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid var(--gray-700);
        }
        
        .list-title {
            font-size: 1.5rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .list-controls {
            display: flex;
            gap: 0.5rem;
        }
        
        .control-btn {
            background-color: var(--gray-700);
            color: var(--light);
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            border: none;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .control-btn:hover {
            background-color: var(--gray-600);
        }
        
        .list-content {
            flex: 1;
            overflow-y: auto;
            padding-right: 0.5rem;
        }
        
        .list-content::-webkit-scrollbar {
            width: 8px;
        }
        
        .list-content::-webkit-scrollbar-track {
            background: var(--darker);
            border-radius: 10px;
        }
        
        .list-content::-webkit-scrollbar-thumb {
            background: var(--gray-700);
            border-radius: 10px;
        }
        
        .timing-row {
            display: grid;
            grid-template-columns: auto 1fr auto auto auto;
            gap: 1rem;
            padding: 1rem;
            background-color: var(--darker);
            border-radius: 8px;
            margin-bottom: 0.75rem;
            align-items: center;
            transition: all 0.3s;
            border-left: 4px solid transparent;
        }
        
        .timing-row:hover {
            transform: translateX(5px);
            border-left-color: <?php echo $is_supercampione ? 'var(--gold)' : 'var(--primary)'; ?>;
        }
        
        .pilot-number {
            background-color: <?php echo $is_supercampione ? 'var(--gold)' : 'var(--primary)'; ?>;
            color: <?php echo $is_supercampione ? 'var(--dark)' : 'var(--light)'; ?>;
            width: 40px;
            height: 40px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
        }
        
        .pilot-name {
            font-weight: 500;
        }
        
        .lap-time {
            font-family: 'Roboto Mono', monospace;
            font-weight: 700;
            color: <?php echo $is_supercampione ? 'var(--gold)' : 'var(--success)'; ?>;
            font-size: 1.25rem;
        }
        
        .best-time {
            color: var(--warning);
            position: relative;
        }
        
        .best-time::after {
            content: '★';
            position: absolute;
            top: -8px;
            right: -12px;
            font-size: 0.875rem;
            color: var(--warning);
        }
        
        .timing-timestamp {
            color: var(--gray-500);
            font-size: 0.75rem;
        }
        
        .timing-actions {
            display: flex;
            gap: 0.5rem;
        }
        
        .timing-action {
            background: var(--gray-800);
            color: var(--gray-400);
            border: none;
            width: 28px;
            height: 28px;
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .timing-action:hover {
            background: var(--danger);
            color: white;
        }
        
        .no-results {
            text-align: center;
            padding: 2rem;
            color: var(--gray-500);
        }
        
        .no-results-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
        }
        
        .stats-panel {
            background-color: var(--darker);
            border-radius: 8px;
            padding: 1rem;
            margin-top: 1.5rem;
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }
        
        .stats-title {
            font-size: 1rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: var(--gray-300);
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
        }
        
        .stat-card {
            background-color: var(--dark);
            border-radius: 8px;
            padding: 0.75rem;
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
        }
        
        .stat-value {
            font-size: 1.5rem;
            font-weight: 700;
            color: <?php echo $is_supercampione ? 'var(--gold)' : 'var(--success)'; ?>;
            margin-bottom: 0.25rem;
        }
        
        .stat-label {
            font-size: 0.75rem;
            color: var(--gray-400);
        }
        
        .best-lap-highlight {
            background-color: rgba(245, 158, 11, 0.1);
            border: 1px solid var(--warning);
        }
        
        .best-lap-info {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.75rem;
            background-color: rgba(245, 158, 11, 0.1);
            border-radius: 8px;
            margin-bottom: 1rem;
        }
        
        .best-lap-icon {
            font-size: 1.5rem;
            color: var(--warning);
        }
        
        .best-lap-time {
            font-family: 'Roboto Mono', monospace;
            font-weight: 700;
            font-size: 1.25rem;
            color: var(--warning);
        }
        
        .best-lap-pilot {
            margin-left: auto;
            font-size: 0.875rem;
            color: var(--gray-300);
        }
        
        .leaderboard {
            margin-top: 1.5rem;
        }
        
        .leaderboard-title {
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: var(--gray-300);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .leaderboard-table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .leaderboard-table th {
            text-align: left;
            padding: 0.75rem;
            color: var(--gray-400);
            border-bottom: 1px solid var(--gray-700);
            font-size: 0.875rem;
            font-weight: 500;
        }
        
        .leaderboard-table td {
            padding: 0.75rem;
            border-bottom: 1px solid var(--gray-800);
        }
        
        .leaderboard-table tr:hover {
            background-color: rgba(255, 255, 255, 0.03);
        }
        
        .position {
            font-weight: 700;
            color: <?php echo $is_supercampione ? 'var(--gold)' : 'var(--primary)'; ?>;
            width: 40px;
        }
        
        .position-1 {
            color: gold;
        }
        
        .position-2 {
            color: silver;
        }
        
        .position-3 {
            color: #cd7f32; /* bronze */
        }

        .no-time {
            color: var(--gray-500);
            font-style: italic;
        }
        
        .success-badge {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            background-color: var(--success);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 50px;
            font-weight: 600;
            animation: fadeIn 0.5s ease-out;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .category-filter {
            display: flex;
            gap: 1rem;
            margin-bottom: 1.5rem;
            align-items: center;
        }
        
        .category-filter label {
            font-weight: 500;
            color: var(--gray-300);
        }
        
        .category-filter select {
            flex: 1;
            padding: 0.5rem;
            border-radius: 6px;
            background-color: var(--darker);
            border: 1px solid var(--gray-700);
            color: var(--light);
        }
        
        .timer-controls {
            display: flex;
            flex-direction: column;
            gap: 1rem;
            margin-top: 1rem;
        }
        
        .timer-status {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            background-color: var(--darker);
            padding: 1rem;
            border-radius: 8px;
            font-weight: 600;
            color: var(--gray-300);
        }
        
        .timer-status.running {
            color: var(--success);
        }
        
        .timer-status.paused {
            color: var(--warning);
        }
        
        .disabled {
            opacity: 0.6;
            cursor: not-allowed;
            pointer-events: none;
        }
        
        .supercampione-toggle {
            display: flex;
            align-items: center;
            gap: 1rem;
            padding: 1rem;
            background-color: var(--darker);
            border-radius: 8px;
            margin-bottom: 1.5rem;
            border: 1px solid var(--gold);
        }
        
        .toggle-label {
            flex: 1;
            font-weight: 600;
            color: var(--gold);
        }
        
        .toggle-switch {
            position: relative;
            display: inline-block;
            width: 60px;
            height: 30px;
        }
        
        .toggle-switch input {
            opacity: 0;
            width: 0;
            height: 0;
        }
        
        .slider {
            position: absolute;
            cursor: pointer;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: var(--gray-700);
            transition: .4s;
            border-radius: 30px;
        }
        
        .slider:before {
            position: absolute;
            content: "";
            height: 22px;
            width: 22px;
            left: 4px;
            bottom: 4px;
            background-color: white;
            transition: .4s;
            border-radius: 50%;
        }
        
        input:checked + .slider {
            background-color: var(--gold);
        }
        
        input:checked + .slider:before {
            transform: translateX(30px);
        }
        
        @media (max-width: 1200px) {
            .container {
                grid-template-columns: 1fr;
            }
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 1rem;
            }
            
            .timing-display {
                font-size: 3rem;
            }
            
            .action-buttons {
                grid-template-columns: 1fr;
            }
            
            .timing-row {
                grid-template-columns: auto 1fr auto;
            }
            
            .timing-timestamp {
                display: none;
            }
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <a href="../index.php" class="navbar-brand">MX<span>PRO</span></a>
        <div>
            <span><?php echo htmlspecialchars($evento['nome_evento']); ?></span>
            <?php if ($is_supercampione): ?>
            <span class="supercampione-badge">
                <i class="fas fa-trophy"></i> SUPERCAMPIONE
            </span>
            <?php endif; ?>
        </div>
    </nav>

    <div class="container">
        <!-- Pannello Cronometraggio -->
        <div class="timing-panel">
            <div class="panel-header">
                <div class="panel-title">Cronometraggio</div>
                <div class="status-pill"><?php echo formatSessione($sessione); ?></div>
            </div>
            
            <div class="status-bar">
                <div class="status-item">
                    <div class="status-icon">🏁</div>
                    <span><?php echo implode(', ', $evento['categorie']); ?></span>
                </div>
                <?php if ($gruppo_selezionato): ?>
                <div class="status-item">
                    <div class="status-icon">👥</div>
                    <span><?php echo htmlspecialchars($gruppo_selezionato['nome_gruppo']); ?> - <?php echo htmlspecialchars($gruppo_selezionato['categoria']); ?></span>
                </div>
                <?php endif; ?>
                <?php if (!empty($categoria_selezionata)): ?>
                <div class="status-item">
                    <div class="status-icon">🏆</div>
                    <span>Categoria: <?php echo htmlspecialchars($categoria_selezionata); ?></span>
                </div>
                <?php endif; ?>
            </div>
            
            <!-- Modalità Supercampione Toggle -->
            <div class="supercampione-toggle">
                <span class="toggle-label">
                    <i class="fas fa-trophy"></i> Modalità Supercampione
                </span>
                <label class="toggle-switch">
                    <input type="checkbox" id="supercampione-toggle" <?php echo $is_supercampione ? 'checked' : ''; ?> onchange="toggleSupercampione()">
                    <span class="slider"></span>
                </label>
            </div>
            
            <!-- Messaggi di errore o successo -->
            <?php if ($error_message): ?>
            <div class="message message-error">
                <i class="fas fa-exclamation-triangle"></i>
                <?php echo htmlspecialchars($error_message); ?>
            </div>
            <?php endif; ?>
            
            <?php if ($success_message): ?>
            <div class="message message-success">
                <i class="fas fa-check-circle"></i>
                <?php echo htmlspecialchars($success_message); ?>
            </div>
            <?php endif; ?>
            
            <?php if ($salvato_con_successo): ?>
            <div class="message message-success">
                <i class="fas fa-check-circle"></i>
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <div class="success-badge">
                        <i class="fas fa-check"></i>
                        <span>Salvato con Successo!</span>
                    </div>
                </div>
            </div>
            <?php endif; ?>
            
            <div class="timer-container">
                <div class="timing-display" id="timer"><?php echo $cronometro_avviato ? '00:00.00' : '--:--:--'; ?></div>
                <div class="countdown-display" id="countdown">
                    <span>⏱️</span>
                    <span id="countdown-time"><?php echo $durata_sessione; ?>:00</span>
                </div>
            </div>
            
            <!-- Pannello impostazioni -->
            <div class="settings-panel">
                <div class="settings-title">Impostazioni Sessione</div>
                <form id="settings-form" action="" method="GET">
                    <input type="hidden" name="evento" value="<?php echo $evento_id; ?>">
                    <input type="hidden" name="sessione" value="<?php echo $sessione; ?>">
                    <input type="hidden" name="gruppo" value="<?php echo $gruppo_id; ?>">
                    <input type="hidden" name="supercampione" value="<?php echo $is_supercampione ? '1' : '0'; ?>">
                    <div class="settings-grid">
                        <div class="settings-item">
                            <label for="durata">Durata (min)</label>
                            <input type="number" id="durata" name="durata" value="<?php echo $durata_sessione; ?>" min="1" max="60">
                        </div>
                        <div class="settings-item">
                            <label for="categoria">Categoria</label>
                            <select id="categoria" name="categoria">
                                <option value="">Tutte le categorie</option>
                                <?php foreach ($categorie_disponibili as $cat): ?>
                                <option value="<?php echo htmlspecialchars($cat); ?>" <?php if ($categoria_selezionata == $cat) echo 'selected'; ?>>
                                    <?php echo htmlspecialchars($cat); ?>
                                </option>
                                <?php endforeach; ?>
                            </select>
                        </div>
                        <div class="settings-item" style="grid-column: span 2;">
                            <button type="submit" class="btn btn-secondary" style="width: 100%; padding: 0.5rem;">
                                <i class="fas fa-sync-alt"></i> Aggiorna Impostazioni
                            </button>
                        </div>
                    </div>
                </form>
            </div>
            
            <?php if (count($gruppi) > 0): ?>
            <!-- Selezione Gruppo -->
            <div class="group-selector">
                <label for="group-select">Seleziona Gruppo</label>
                <form method="GET" id="group-form">
                    <input type="hidden" name="evento" value="<?php echo $evento_id; ?>">
                    <input type="hidden" name="sessione" value="<?php echo $sessione; ?>">
                    <input type="hidden" name="durata" value="<?php echo $durata_sessione; ?>">
                    <input type="hidden" name="categoria" value="<?php echo $categoria_selezionata; ?>">
                    <input type="hidden" name="supercampione" value="<?php echo $is_supercampione ? '1' : '0'; ?>">
                    <select name="gruppo" id="group-select" onchange="document.getElementById('group-form').submit()">
                        <option value="0">Tutti i piloti</option>
                        <?php foreach ($gruppi as $gruppo): ?>
                        <option value="<?php echo $gruppo['id']; ?>" <?php if ($gruppo_id == $gruppo['id']) echo 'selected'; ?>>
                            <?php echo htmlspecialchars($gruppo['nome_gruppo']); ?> - <?php echo htmlspecialchars($gruppo['categoria']); ?>
                        </option>
                        <?php endforeach; ?>
                    </select>
                </form>
            </div>
            <?php endif; ?>
            
            <?php if (!$cronometro_avviato): ?>
            <!-- Pulsante per avviare il cronometro -->
            <div class="timer-controls">
                <div class="timer-status">
                    <i class="fas fa-hourglass-start"></i>
                    <span>Pronto per iniziare<?php echo $is_supercampione ? ' la SUPERCAMPIONE' : ''; ?></span>
                </div>
                
                <form id="start-timer-form" action="" method="GET">
                    <input type="hidden" name="evento" value="<?php echo $evento_id; ?>">
                    <input type="hidden" name="sessione" value="<?php echo $sessione; ?>">
                    <input type="hidden" name="gruppo" value="<?php echo $gruppo_id; ?>">
                    <input type="hidden" name="categoria" value="<?php echo $categoria_selezionata; ?>">
                    <input type="hidden" name="durata" value="<?php echo $durata_sessione; ?>">
                    <input type="hidden" name="cronometro_avviato" value="1">
                    <input type="hidden" name="supercampione" value="<?php echo $is_supercampione ? '1' : '0'; ?>">
                    
                    <button type="submit" class="btn btn-start">
                        <i class="fas fa-play"></i> INIZIA CRONOMETRAGGIO
                    </button>
                </form>
            </div>
            <?php else: ?>
            <form method="POST" id="timing-form">
                <input type="hidden" name="action" value="add_time">
                <input type="hidden" name="tempo" id="tempo_input">
                
                <div class="number-input">
                    <label for="number-input">Numero Pilota</label>
                    <input type="text" id="number-input" name="numero_gara" placeholder="#" autofocus>
                </div>
                
                <div class="action-buttons">
                    <button type="submit" class="btn btn-primary" id="submit-btn">
                        <i class="fas fa-stopwatch"></i> REGISTRA (ENTER)
                    </button>
                    <a href="cronometraggio_sessione.php?id=<?php echo $evento_id; ?>" class="btn btn-secondary">
                        <i class="fas fa-times"></i> MENU (ESC)
                    </a>
                </div>
            </form>
            
            <!-- Pulsante per terminare la sessione -->
            <form method="POST">
                <input type="hidden" name="action" value="finish_session">
                <button type="submit" class="btn btn-finish" id="finish-btn" onclick="return confirm('Sei sicuro di voler terminare la sessione? Questo genererà la classifica finale.')">
                    <i class="fas fa-flag-checkered"></i> TERMINA SESSIONE E SALVA CLASSIFICA
                </button>
            </form>
            <?php endif; ?>
        </div>
        
        <!-- Lista Tempi Live -->
        <div class="timing-list">
            <div class="list-header">
                <div class="list-title">
                    <i class="fas fa-chart-line"></i>
                    Rilevamento Tempi
                    <?php if ($is_supercampione): ?>
                    <span class="supercampione-badge" style="font-size: 0.8rem;">SUPERCAMPIONE</span>
                    <?php endif; ?>
                </div>
                <div class="list-controls">
                    <button class="control-btn" title="Aggiorna" onclick="window.location.reload()">
                        <i class="fas fa-sync-alt"></i>
                    </button>
                </div>
            </div>
            
            <div class="list-content">
                <?php if ($giro_piu_veloce): ?>
                <div class="best-lap-info">
                    <div class="best-lap-icon">🏆</div>
                    <div>
                        <div>Giro più veloce</div>
                        <div class="best-lap-time"><?php echo $giro_piu_veloce; ?></div>
                    </div>
                    <div class="best-lap-pilot">
                        #<?php echo $pilota_piu_veloce['numero_gara']; ?> <?php echo htmlspecialchars($pilota_piu_veloce['nome_pilota'] ?? ''); ?>
                    </div>
                </div>
                <?php endif; ?>

                <?php if (count($tempi_sessione) > 0): ?>
                    <?php 
                    // Ordina i tempi sessione dal più recente al più vecchio
                    usort($tempi_sessione, function($a, $b) {
                        return strtotime($b['timestamp']) - strtotime($a['timestamp']);
                    });
                    
                    foreach($tempi_sessione as $tempo): 
                        // Determina se è il tempo migliore del pilota
                        $is_best_time = false;
                        $numero_gara = $tempo['numero_gara'];
                        if (isset($tempi_piloti[$numero_gara]) && 
                            isset($tempi_piloti[$numero_gara]['migliore_id']) && 
                            $tempi_piloti[$numero_gara]['migliore_id'] == $tempo['id']) {
                            $is_best_time = true;
                        }
                        
                        // Cerchiamo le informazioni del pilota
                        $pilota_info = null;
                        foreach($piloti as $p) {
                            if ($p['numero_gara'] == $tempo['numero_gara']) {
                                $pilota_info = $p;
                                break;
                            }
                        }
                        
                        // Se abbiamo filtrato per categoria, verifichiamo
                        if (!empty($categoria_selezionata) && $pilota_info && isset($pilota_info['categoria']) && $pilota_info['categoria'] != $categoria_selezionata && $categoria_selezionata != 'Supercampione') {
                            continue;
                        }
                    ?>
                        <div class="timing-row <?php if ($is_best_time) echo 'best-lap-highlight'; ?>">
                            <div class="pilot-number">
                                #<?php echo $tempo['numero_gara']; ?>
                            </div>
                            <div class="pilot-name">
                                <?php 
                                if ($pilota_info) {
                                    echo htmlspecialchars($pilota_info['nome'] . ' ' . $pilota_info['cognome']);
                                } else {
                                    echo "Pilota #" . $tempo['numero_gara'];
                                }
                                ?>
                            </div>
                            <div class="lap-time <?php if ($is_best_time) echo 'best-time'; ?>">
                                <?php echo $tempo['tempo']; ?>
                            </div>
                            <div class="timing-timestamp">
                                <?php 
                                $timestamp = new DateTime($tempo['timestamp']);
                                echo $timestamp->format('H:i:s'); 
                                ?>
                            </div>
                            <div class="timing-actions">
                                <form method="POST" onsubmit="return confirm('Sei sicuro di voler eliminare questo tempo?');">
                                    <input type="hidden" name="action" value="delete_time">
                                    <input type="hidden" name="tempo_id" value="<?php echo $tempo['id']; ?>">
                                    <button type="submit" class="timing-action" title="Elimina tempo">
                                        <i class="fas fa-trash-alt"></i>
                                    </button>
                                </form>
                            </div>
                        </div>
                    <?php endforeach; ?>
                <?php else: ?>
                    <div class="no-results">
                        <div class="no-results-icon"><?php echo $is_supercampione ? '🏆' : '⏱️'; ?></div>
                        <p>Nessun tempo registrato</p>
                        <p>I tempi appariranno qui quando inizierai il cronometraggio</p>
                    </div>
                <?php endif; ?>
            </div>
            
            <!-- Leaderboard in tempo reale -->
            <div class="leaderboard">
                <h3 class="leaderboard-title">
                    <i class="fas fa-trophy"></i>
                    Classifica Provvisoria
                    <?php if ($is_supercampione): ?>
                    <span class="supercampione-badge" style="font-size: 0.8rem;">SUPERCAMPIONE</span>
                    <?php endif; ?>
                </h3>
                
                <div class="category-filter">
                    <label>Filtra per categoria:</label>
                    <form method="GET" id="categoria-filter-form">
                        <input type="hidden" name="evento" value="<?php echo $evento_id; ?>">
                        <input type="hidden" name="sessione" value="<?php echo $sessione; ?>">
                        <input type="hidden" name="gruppo" value="<?php echo $gruppo_id; ?>">
                        <input type="hidden" name="durata" value="<?php echo $durata_sessione; ?>">
                        <input type="hidden" name="cronometro_avviato" value="<?php echo $cronometro_avviato ? '1' : '0'; ?>">
                        <input type="hidden" name="supercampione" value="<?php echo $is_supercampione ? '1' : '0'; ?>">
                        
                        <select name="categoria" onchange="document.getElementById('categoria-filter-form').submit()">
                            <option value="">Tutte le categorie</option>
                            <?php foreach ($categorie_disponibili as $cat): ?>
                            <option value="<?php echo htmlspecialchars($cat); ?>" <?php if ($categoria_selezionata == $cat) echo 'selected'; ?>>
                                <?php echo htmlspecialchars($cat); ?>
                            </option>
                            <?php endforeach; ?>
                        </select>
                    </form>
                </div>
                
                <table class="leaderboard-table">
                    <thead>
                        <tr>
                            <th>Pos.</th>
                            <th>Pilota</th>
                            <th>Categoria</th>
                            <th>Miglior Tempo</th>
                            <th>Media</th>
                            <th>Giri</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php 
                        $position = 1;
                        foreach($classifica_completa as $numero_gara => $dati):
                            // Se abbiamo filtrato per categoria, verifichiamo
                            if (!empty($categoria_selezionata) && isset($dati['categoria']) && $dati['categoria'] != $categoria_selezionata && $categoria_selezionata != 'Supercampione') {
                                continue;
                            }
                        ?>
                            <tr>
                                <td class="position position-<?php echo ($position <= 3) ? $position : ''; ?>"><?php echo $position; ?>°</td>
                                <td>
                                    <strong>#<?php echo $numero_gara; ?></strong> 
                                    <?php echo htmlspecialchars($dati['nome_pilota'] ?? 'Pilota #' . $numero_gara); ?>
                                </td>
                                <td><?php echo htmlspecialchars($dati['categoria'] ?? 'N/D'); ?></td>
                                <td class="lap-time <?php if (isset($dati['migliore']) && $dati['migliore'] === $giro_piu_veloce) echo 'best-time'; ?>">
                                    <?php echo isset($dati['migliore']) ? $dati['migliore'] : '<span class="no-time">Nessun tempo</span>'; ?>
                                </td>
                                <td><?php echo isset($dati['media']) ? $dati['media'] : '--:--:--'; ?></td>
                                <td><?php echo isset($dati['num_giri']) ? $dati['num_giri'] : '0'; ?></td>
                            </tr>
                        <?php 
                            $position++;
                        endforeach; 
                        ?>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    
    <script>
        // Cronometro
        let timer;
        let startTime = Date.now();
        let countdownTimer;
        let countdownSeconds = <?php echo $durata_sessione * 60; ?>;
        let cronometroAvviato = <?php echo $cronometro_avviato ? 'true' : 'false'; ?>;
        
        // Avvia il timer
        function startTimer() {
            if (cronometroAvviato) {
                timer = setInterval(updateDisplay, 10);
                startCountdown();
                
                // Abilita il form di registrazione
                if (document.getElementById('timing-form')) {
                    document.getElementById('timing-form').classList.remove('disabled');
                    document.getElementById('number-input').focus();
                }
            }
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
        
        // Avvia il countdown
        function startCountdown() {
            updateCountdown();
            countdownTimer = setInterval(updateCountdown, 1000);
        }
        
        // Aggiorna display del countdown
        function updateCountdown() {
            if (countdownSeconds <= 0) {
                clearInterval(countdownTimer);
                document.getElementById('countdown-time').textContent = "FINE!";
                document.getElementById('countdown').classList.add('danger');
                
                // Riproduci un suono o mostra un alert
                alert("Tempo scaduto!");
                
                return;
            }
            
            const minutes = Math.floor(countdownSeconds / 60);
            const seconds = countdownSeconds % 60;
            
            document.getElementById('countdown-time').textContent = 
                `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
                
            // Aggiorna la classe per lo stile
            if (countdownSeconds <= 60) {
                document.getElementById('countdown').classList.add('danger');
            } else if (countdownSeconds <= 180) {
                document.getElementById('countdown').classList.add('warning');
            }
            
            countdownSeconds--;
        }
        
        // Gestione invio form
        if (document.getElementById('timing-form')) {
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
                
                // Verifica se il numero di gara è valido (già verificato lato server, ma diamo un feedback immediato)
                const numeri_validi = <?php echo json_encode($numeri_gara_validi); ?>;
                if (!numeri_validi.includes(number)) {
                    alert(`Attenzione: Il numero #${number} non è associato a nessun pilota in questo gruppo. Il tempo non verrà registrato.`);
                    numberInput.value = '';
                    numberInput.focus();
                    return;
                }
                
                // Invia il form
                this.submit();
            });
        }
        
        // Gestione tastiera
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && document.getElementById('submit-btn')) {
                e.preventDefault();
                document.getElementById('submit-btn').click();
            } else if (e.key === 'Escape') {
                window.location.href = 'cronometraggio_sessione.php?id=<?php echo $evento_id; ?>';
            }
        });
        
        // Funzione per toggle supercampione
        function toggleSupercampione() {
            const isChecked = document.getElementById('supercampione-toggle').checked;
            window.location.href = 'cronometraggio_manuale.php?evento=<?php echo $evento_id; ?>&sessione=<?php echo $sessione; ?>&gruppo=<?php echo $gruppo_id; ?>&categoria=<?php echo $categoria_selezionata; ?>&durata=<?php echo $durata_sessione; ?>&supercampione=' + (isChecked ? '1' : '0');
        }
        
        // Avvia il timer quando la pagina è caricata
        window.onload = startTimer;
        
        // Auto-refresh della pagina ogni 30 secondi per aggiornare i dati
        <?php if (count($tempi_sessione) > 0): ?>
        setTimeout(function() {
            window.location.reload();
        }, 30000);
        <?php endif; ?>
    </script>
</body>
</html>