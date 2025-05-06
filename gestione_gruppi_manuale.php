<?php
// Visualizza tutti gli errori per il debug
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

// Iniziamo la sessione
session_start();

// Verifica l'autenticazione dell'utente
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

// Recuperiamo tutti i piloti
$tutti_piloti = $db->readCollection('piloti');

// Recuperiamo le iscrizioni per questo evento
$iscrizioni = $db->readCollection('iscrizioni');
$piloti_iscritti = [];
foreach ($iscrizioni as $iscrizione) {
    if ($iscrizione['evento_id'] == $evento_id) {
        $piloti_iscritti[] = $iscrizione;
    }
}

// Colleghiamo i dati dei piloti alle iscrizioni
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
$gruppi = $db->findDocuments('gruppi', ['evento_id' => $evento_id]);

// Elaborazione delle azioni
$message = '';
$message_type = '';

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    // Gestione delle diverse azioni
    $action = $_POST['action'] ?? '';

    // Creare un nuovo gruppo
    if ($action == 'crea_gruppo') {
        $nome_gruppo = $_POST['nome_gruppo'] ?? '';
        $categoria = $_POST['categoria'] ?? '';
        
        if ($nome_gruppo && $categoria) {
            $nuovo_gruppo = [
                'evento_id' => $evento_id,
                'nome_gruppo' => $nome_gruppo,
                'categoria' => $categoria,
                'piloti' => [] // Il gruppo parte vuoto
            ];
            
            $db->insertDocument('gruppi', $nuovo_gruppo);
            $message = 'Nuovo gruppo creato con successo!';
            $message_type = 'success';
            
            // Aggiorniamo l'elenco dei gruppi
            $gruppi = $db->findDocuments('gruppi', ['evento_id' => $evento_id]);
        } else {
            $message = 'Errore: Nome gruppo e categoria sono richiesti';
            $message_type = 'error';
        }
    }
    
    // Aggiungere pilota a un gruppo
    elseif ($action == 'aggiungi_pilota') {
        $gruppo_id = $_POST['gruppo_id'] ?? 0;
        $pilota_id = $_POST['pilota_id'] ?? 0;
        
        if ($gruppo_id && $pilota_id) {
            // Troviamo il gruppo
            $gruppo = null;
            foreach ($gruppi as $g) {
                if ($g['id'] == $gruppo_id) {
                    $gruppo = $g;
                    break;
                }
            }
            
            if ($gruppo) {
                // Verifichiamo se il pilota è già in un altro gruppo
                foreach ($gruppi as $g) {
                    if (in_array($pilota_id, $g['piloti'])) {
                        // Rimuoviamo il pilota dal gruppo precedente
                        $piloti_aggiornati = array_diff($g['piloti'], [$pilota_id]);
                        $g['piloti'] = array_values($piloti_aggiornati); // Reindicizza l'array
                        $db->updateDocument('gruppi', $g['id'], $g);
                    }
                }
                
                // Aggiungiamo il pilota al nuovo gruppo
                $gruppo['piloti'][] = $pilota_id;
                $db->updateDocument('gruppi', $gruppo_id, $gruppo);
                
                $message = 'Pilota aggiunto al gruppo con successo!';
                $message_type = 'success';
                
                // Aggiorniamo l'elenco dei gruppi
                $gruppi = $db->findDocuments('gruppi', ['evento_id' => $evento_id]);
            } else {
                $message = 'Errore: Gruppo non trovato';
                $message_type = 'error';
            }
        } else {
            $message = 'Errore: ID gruppo e ID pilota sono richiesti';
            $message_type = 'error';
        }
    }
    
    // Rimuovere pilota da un gruppo
    elseif ($action == 'rimuovi_pilota') {
        $gruppo_id = $_POST['gruppo_id'] ?? 0;
        $pilota_id = $_POST['pilota_id'] ?? 0;
        
        if ($gruppo_id && $pilota_id) {
            // Troviamo il gruppo
            $gruppo = null;
            foreach ($gruppi as $g) {
                if ($g['id'] == $gruppo_id) {
                    $gruppo = $g;
                    break;
                }
            }
            
            if ($gruppo) {
                // Rimuoviamo il pilota dal gruppo
                $piloti_aggiornati = array_diff($gruppo['piloti'], [$pilota_id]);
                $gruppo['piloti'] = array_values($piloti_aggiornati); // Reindicizza l'array
                $db->updateDocument('gruppi', $gruppo_id, $gruppo);
                
                $message = 'Pilota rimosso dal gruppo con successo!';
                $message_type = 'success';
                
                // Aggiorniamo l'elenco dei gruppi
                $gruppi = $db->findDocuments('gruppi', ['evento_id' => $evento_id]);
            } else {
                $message = 'Errore: Gruppo non trovato';
                $message_type = 'error';
            }
        } else {
            $message = 'Errore: ID gruppo e ID pilota sono richiesti';
            $message_type = 'error';
        }
    }
    
    // Eliminare un gruppo
    elseif ($action == 'elimina_gruppo') {
        $gruppo_id = $_POST['gruppo_id'] ?? 0;
        
        if ($gruppo_id) {
            $db->deleteDocument('gruppi', $gruppo_id);
            $message = 'Gruppo eliminato con successo!';
            $message_type = 'success';
            
            // Aggiorniamo l'elenco dei gruppi
            $gruppi = $db->findDocuments('gruppi', ['evento_id' => $evento_id]);
        } else {
            $message = 'Errore: ID gruppo richiesto';
            $message_type = 'error';
        }
    }
    
    // Modifica nome/categoria gruppo
    elseif ($action == 'modifica_gruppo') {
        $gruppo_id = $_POST['gruppo_id'] ?? 0;
        $nome_gruppo = $_POST['nome_gruppo'] ?? '';
        $categoria = $_POST['categoria'] ?? '';
        
        if ($gruppo_id && $nome_gruppo && $categoria) {
            // Troviamo il gruppo
            $gruppo = null;
            foreach ($gruppi as $g) {
                if ($g['id'] == $gruppo_id) {
                    $gruppo = $g;
                    break;
                }
            }
            
            if ($gruppo) {
                $gruppo['nome_gruppo'] = $nome_gruppo;
                $gruppo['categoria'] = $categoria;
                $db->updateDocument('gruppi', $gruppo_id, $gruppo);
                
                $message = 'Gruppo modificato con successo!';
                $message_type = 'success';
                
                // Aggiorniamo l'elenco dei gruppi
                $gruppi = $db->findDocuments('gruppi', ['evento_id' => $evento_id]);
            } else {
                $message = 'Errore: Gruppo non trovato';
                $message_type = 'error';
            }
        } else {
            $message = 'Errore: ID gruppo, nome e categoria sono richiesti';
            $message_type = 'error';
        }
    }
    
    // Operazione di drag and drop (spostare un pilota da un gruppo all'altro)
    elseif ($action == 'sposta_pilota') {
        $pilota_id = $_POST['pilota_id'] ?? 0;
        $gruppo_origine_id = $_POST['gruppo_origine_id'] ?? 0;
        $gruppo_destinazione_id = $_POST['gruppo_destinazione_id'] ?? 0;
        
        if ($pilota_id && $gruppo_destinazione_id) {
            // Troviamo i gruppi
            $gruppo_origine = null;
            $gruppo_destinazione = null;
            
            foreach ($gruppi as $g) {
                if ($gruppo_origine_id && $g['id'] == $gruppo_origine_id) {
                    $gruppo_origine = $g;
                }
                if ($g['id'] == $gruppo_destinazione_id) {
                    $gruppo_destinazione = $g;
                }
            }
            
            // Se abbiamo trovato il gruppo di destinazione
            if ($gruppo_destinazione) {
                // Se abbiamo un gruppo di origine, rimuoviamo il pilota da lì
                if ($gruppo_origine) {
                    $piloti_aggiornati = array_diff($gruppo_origine['piloti'], [$pilota_id]);
                    $gruppo_origine['piloti'] = array_values($piloti_aggiornati); // Reindicizza l'array
                    $db->updateDocument('gruppi', $gruppo_origine_id, $gruppo_origine);
                }
                
                // Verifichiamo se il pilota è già in altri gruppi
                foreach ($gruppi as $g) {
                    if ($g['id'] != $gruppo_origine_id && $g['id'] != $gruppo_destinazione_id) {
                        if (in_array($pilota_id, $g['piloti'])) {
                            // Rimuoviamo il pilota da questo gruppo
                            $piloti_aggiornati = array_diff($g['piloti'], [$pilota_id]);
                            $g['piloti'] = array_values($piloti_aggiornati); // Reindicizza l'array
                            $db->updateDocument('gruppi', $g['id'], $g);
                        }
                    }
                }
                
                // Aggiungiamo il pilota al gruppo destinazione
                if (!in_array($pilota_id, $gruppo_destinazione['piloti'])) {
                    $gruppo_destinazione['piloti'][] = $pilota_id;
                    $db->updateDocument('gruppi', $gruppo_destinazione_id, $gruppo_destinazione);
                }
                
                $message = 'Pilota spostato con successo!';
                $message_type = 'success';
                
                // Per richieste AJAX, restituiamo una risposta JSON
                if (isset($_SERVER['HTTP_X_REQUESTED_WITH']) && strtolower($_SERVER['HTTP_X_REQUESTED_WITH']) == 'xmlhttprequest') {
                    header('Content-Type: application/json');
                    echo json_encode(['success' => true, 'message' => $message]);
                    exit();
                }
                
                // Aggiorniamo l'elenco dei gruppi
                $gruppi = $db->findDocuments('gruppi', ['evento_id' => $evento_id]);
            } else {
                $message = 'Errore: Gruppo destinazione non trovato';
                $message_type = 'error';
                
                // Per richieste AJAX, restituiamo una risposta JSON
                if (isset($_SERVER['HTTP_X_REQUESTED_WITH']) && strtolower($_SERVER['HTTP_X_REQUESTED_WITH']) == 'xmlhttprequest') {
                    header('Content-Type: application/json');
                    echo json_encode(['success' => false, 'message' => $message]);
                    exit();
                }
            }
        } else {
            $message = 'Errore: ID pilota e ID gruppo destinazione sono richiesti';
            $message_type = 'error';
            
            // Per richieste AJAX, restituiamo una risposta JSON
            if (isset($_SERVER['HTTP_X_REQUESTED_WITH']) && strtolower($_SERVER['HTTP_X_REQUESTED_WITH']) == 'xmlhttprequest') {
                header('Content-Type: application/json');
                echo json_encode(['success' => false, 'message' => $message]);
                exit();
            }
        }
    }
}

// MIGLIORIA: Prendiamo le categorie direttamente dall'evento
$categorie_disponibili = $evento['categorie'];

// Aggiungiamo anche eventuali categorie dai piloti per sicurezza
foreach ($piloti_completi as $pilota) {
    if (!in_array($pilota['categoria'], $categorie_disponibili)) {
        $categorie_disponibili[] = $pilota['categoria'];
    }
}

// Piloti che non sono in nessun gruppo
$piloti_senza_gruppo = $piloti_completi;
foreach ($gruppi as $gruppo) {
    foreach ($gruppo['piloti'] as $pilota_id) {
        foreach ($piloti_senza_gruppo as $key => $pilota) {
            if ($pilota['id'] == $pilota_id) {
                unset($piloti_senza_gruppo[$key]);
                break;
            }
        }
    }
}
// Reindicizza l'array
$piloti_senza_gruppo = array_values($piloti_senza_gruppo);
?>

<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gestione Manuale Gruppi - <?php echo htmlspecialchars($evento['nome_evento']); ?></title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #2563eb;
            --primary-dark: #1d4ed8;
            --secondary: #f43f5e;
            --secondary-dark: #e11d48;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --dark: #0f172a;
            --light: #f8fafc;
            --gray-100: #f1f5f9;
            --gray-200: #e2e8f0;
            --gray-300: #cbd5e1;
            --gray-400: #94a3b8;
            --gray-500: #64748b;
            --gray-600: #475569;
            --gray-700: #334155;
            --gray-800: #1e293b;
            --text: #0f172a;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Poppins', sans-serif;
            background-color: var(--light);
            color: var(--text);
            line-height: 1.5;
        }
        
        .container {
            max-width: 1600px;
            margin: 0 auto;
            padding: 1.5rem;
        }
        
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid var(--gray-200);
        }
        
        .title {
            font-size: 1.5rem;
            font-weight: 600;
            color: var(--dark);
        }
        
        .nav-buttons {
            display: flex;
            gap: 1rem;
        }
        
        .btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 0.5rem 1.25rem;
            border-radius: 0.375rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
            text-decoration: none;
            gap: 0.5rem;
        }
        
        .btn-primary {
            background-color: var(--primary);
            color: white;
            border: none;
        }
        
        .btn-primary:hover {
            background-color: var(--primary-dark);
        }
        
        .btn-secondary {
            background-color: var(--gray-700);
            color: white;
            border: none;
        }
        
        .btn-secondary:hover {
            background-color: var(--gray-800);
        }
        
        .btn-danger {
            background-color: var(--danger);
            color: white;
            border: none;
        }
        
        .btn-danger:hover {
            background-color: #dc2626;
        }
        
        .btn-success {
            background-color: var(--success);
            color: white;
            border: none;
        }
        
        .btn-success:hover {
            background-color: #059669;
        }
        
        .event-info {
            background-color: white;
            border-radius: 0.5rem;
            padding: 1.5rem;
            margin-bottom: 2rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        
        .event-title {
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: var(--dark);
        }
        
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
        }
        
        .info-item {
            display: flex;
            flex-direction: column;
        }
        
        .info-label {
            font-size: 0.875rem;
            color: var(--gray-500);
            margin-bottom: 0.25rem;
        }
        
        .info-value {
            font-weight: 600;
            color: var(--dark);
        }
        
        .alert {
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1.5rem;
            animation: fadeIn 0.5s;
        }
        
        .alert-success {
            background-color: #d1fae5;
            color: #065f46;
            border-left: 4px solid var(--success);
        }
        
        .alert-error {
            background-color: #fee2e2;
            color: #b91c1c;
            border-left: 4px solid var(--danger);
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .management-area {
            display: grid;
            grid-template-columns: 300px 1fr;
            gap: 1.5rem;
        }
        
        .sidebar {
            background-color: white;
            border-radius: 0.5rem;
            padding: 1.5rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        
        .sidebar-title {
            font-size: 1.125rem;
            font-weight: 600;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid var(--gray-200);
        }
        
        .form-group {
            margin-bottom: 1rem;
        }
        
        label {
            display: block;
            margin-bottom: 0.5rem;
            font-size: 0.875rem;
            font-weight: 500;
            color: var(--gray-700);
        }
        
        input, select {
            width: 100%;
            padding: 0.625rem;
            border: 1px solid var(--gray-300);
            border-radius: 0.375rem;
            font-size: 0.875rem;
            color: var(--text);
            transition: border-color 0.2s;
        }
        
        input:focus, select:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
        }
        
        .groups-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 1.5rem;
        }
        
        .group-card {
            background-color: white;
            border-radius: 0.5rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            display: flex;
            flex-direction: column;
            height: 100%;
            min-height: 300px;
        }
        
        .group-header {
            background-color: var(--primary);
            color: white;
            padding: 1rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .group-title {
            font-weight: 600;
        }
        
        .group-actions {
            display: flex;
            gap: 0.5rem;
        }
        
        .group-action {
            width: 28px;
            height: 28px;
            border-radius: 0.25rem;
            background-color: rgba(255, 255, 255, 0.1);
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: background-color 0.2s;
        }
        
        .group-action:hover {
            background-color: rgba(255, 255, 255, 0.2);
        }
        
        .group-body {
            flex: 1;
            padding: 1rem;
            display: flex;
            flex-direction: column;
        }
        
        .group-info {
            display: flex;
            justify-content: space-between;
            padding-bottom: 0.75rem;
            margin-bottom: 0.75rem;
            border-bottom: 1px solid var(--gray-200);
        }
        
        .info-badge {
            background-color: var(--gray-100);
            color: var(--gray-700);
            padding: 0.25rem 0.75rem;
            border-radius: 0.25rem;
            font-size: 0.75rem;
            font-weight: 600;
        }
        
        .pilot-list {
            flex: 1;
            overflow: auto;
            min-height: 150px;
            max-height: 300px;
        }
        
        .pilot-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.5rem;
            border-radius: 0.25rem;
            margin-bottom: 0.25rem;
            transition: background-color 0.2s;
            cursor: grab;
            border: 1px solid transparent;
        }
        
        .pilot-item:hover {
            background-color: var(--gray-100);
            border: 1px dashed var(--primary);
        }
        
        .pilot-item.dragging {
            opacity: 0.5;
            background-color: var(--gray-200);
            border: 1px dashed var(--primary);
        }
        
        .pilot-info {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .pilot-number {
            background-color: var(--primary);
            color: white;
            width: 32px;
            height: 32px;
            border-radius: 0.25rem;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            font-size: 0.875rem;
        }
        
        .pilot-name {
            font-size: 0.875rem;
            font-weight: 500;
        }
        
        .pilot-actions {
            display: flex;
            gap: 0.25rem;
        }
        
        .pilot-action {
            width: 24px;
            height: 24px;
            border-radius: 0.25rem;
            background-color: var(--gray-200);
            color: var(--gray-700);
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 0.75rem;
        }
        
        .pilot-action:hover {
            background-color: var(--danger);
            color: white;
        }
        
        .drop-area {
            border: 2px dashed var(--gray-300);
            border-radius: 0.5rem;
            padding: 1rem;
            text-align: center;
            color: var(--gray-500);
            margin-top: 0.5rem;
            transition: all 0.2s;
            min-height: 100px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .drop-area.highlight {
            border-color: var(--primary);
            background-color: rgba(37, 99, 235, 0.05);
        }
        
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.5);
            z-index: 1000;
            align-items: center;
            justify-content: center;
        }
        
        .modal.active {
            display: flex;
        }
        
        .modal-content {
            background-color: white;
            border-radius: 0.5rem;
            padding: 1.5rem;
            width: 400px;
            max-width: 90%;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }
        
        .modal-title {
            font-size: 1.25rem;
            font-weight: 600;
        }
        
        .modal-close {
            background: none;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            color: var(--gray-500);
        }
        
        .modal-close:hover {
            color: var(--gray-700);
        }
        
        .modal-footer {
            display: flex;
            justify-content: flex-end;
            gap: 0.75rem;
            margin-top: 1.5rem;
        }
        
        .empty-state {
            text-align: center;
            padding: 3rem 1rem;
            color: var(--gray-500);
        }
        
        .empty-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
            color: var(--gray-400);
        }
        
        .empty-text {
            margin-bottom: 1.5rem;
        }
        
        .loading {
            position: fixed;
            top: 1rem;
            right: 1rem;
            background-color: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 0.25rem;
            display: none;
            z-index: 1100;
        }
        
        /* MIGLIORIA: Card per i piloti disponibili */
        .available-pilots-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 0.5rem;
            margin-top: 0.5rem;
            max-height: 400px;
            overflow-y: auto;
        }
        
        .available-pilot-card {
            background-color: var(--gray-100);
            border-radius: 0.375rem;
            padding: 0.5rem;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 0.5rem;
            cursor: grab;
            transition: all 0.2s;
            border: 1px solid transparent;
        }
        
        .available-pilot-card:hover {
            transform: translateY(-2px);
            border-color: var(--primary);
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        .available-pilot-card.dragging {
            opacity: 0.5;
            border: 1px dashed var(--primary);
        }
        
        .available-pilot-number {
            background-color: var(--primary);
            color: white;
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex; align-items: center;
            justify-content: center;
            font-weight: 600;
        }
        
        .available-pilot-name {
            font-size: 0.75rem;
            text-align: center;
            font-weight: 500;
        }
        
        .pilot-category {
            font-size: 0.7rem;
            color: var(--gray-500);
            background-color: var(--gray-200);
            padding: 0.15rem 0.5rem;
            border-radius: 2rem;
        }
        
        .instructions {
            background-color: var(--gray-100);
            border-left: 4px solid var(--primary);
            padding: 1rem;
            margin: 1rem 0;
            font-size: 0.875rem;
            color: var(--gray-700);
            border-radius: 0 0.375rem 0.375rem 0;
        }
        
        .drag-instructions {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-top: 0.5rem;
        }
        
        .drag-icon {
            font-size: 1.2rem;
            color: var(--gray-500);
        }
        
        @media (max-width: 768px) {
            .management-area {
                grid-template-columns: 1fr;
            }
            
            .groups-container {
                grid-template-columns: 1fr;
            }
            
            .available-pilots-grid {
                grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="title">Gestione Manuale Gruppi</div>
            
            <div class="nav-buttons">
                <a href="gestione_gruppi.php?evento=<?php echo $evento_id; ?>" class="btn btn-secondary">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                        <path fill-rule="evenodd" d="M15 8a.5.5 0 0 0-.5-.5H2.707l3.147-3.146a.5.5 0 1 0-.708-.708l-4 4a.5.5 0 0 0 0 .708l4 4a.5.5 0 0 0 .708-.708L2.707 8.5H14.5A.5.5 0 0 0 15 8z"/>
                    </svg>
                    Torna a Gestione Gruppi
                </a>
                <a href="cronometraggio_sessione.php?id=<?php echo $evento_id; ?>" class="btn btn-primary">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                        <path d="M8 3.5a.5.5 0 0 0-1 0V9a.5.5 0 0 0 .252.434l3.5 2a.5.5 0 0 0 .496-.868L8 8.71V3.5z"/>
                        <path d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm7-8A7 7 0 1 1 1 8a7 7 0 0 1 14 0z"/>
                    </svg>
                    Torna a Cronometraggio
                </a>
            </div>
        </div>
        
        <!-- Info Evento -->
        <div class="event-info">
            <h2 class="event-title"><?php echo htmlspecialchars($evento['nome_evento']); ?></h2>
            <div class="info-grid">
                <div class="info-item">
                    <div class="info-label">Data</div>
                    <div class="info-value"><?php echo date('d/m/Y', strtotime($evento['data_evento'])); ?></div>
                </div>
                <div class="info-item">
                    <div class="info-label">Luogo</div>
                    <div class="info-value"><?php echo htmlspecialchars($evento['luogo']); ?></div>
                </div>
                <div class="info-item">
                    <div class="info-label">Tipo</div>
                    <div class="info-value"><?php echo ucfirst(htmlspecialchars($evento['tipo'])); ?></div>
                </div>
                <div class="info-item">
                    <div class="info-label">Categorie</div>
                    <div class="info-value"><?php echo implode(', ', $evento['categorie']); ?></div>
                </div>
            </div>
        </div>
        
        <!-- Messaggi di Stato -->
        <?php if ($message): ?>
        <div class="alert alert-<?php echo $message_type; ?>">
            <?php echo htmlspecialchars($message); ?>
        </div>
        <?php endif; ?>
        
        <!-- Istruzioni per l'utente -->
        <div class="instructions">
            <strong>Come gestire i gruppi:</strong>
            <ul>
                <li>Crea un nuovo gruppo usando il modulo a sinistra</li>
                <li>Trascina i piloti dall'elenco "Piloti disponibili" ai gruppi creati</li>
                <li>Puoi anche trascinare i piloti da un gruppo all'altro</li>
                <li>Usa l'icona <svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" fill="currentColor" viewBox="0 0 16 16">
                        <path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"/>
                    </svg> per rimuovere un pilota da un gruppo</li>
            </ul>
            
            <div class="drag-instructions">
                <div class="drag-icon">🖱️</div>
                <div>Trascina i piloti usando drag & drop</div>
            </div>
        </div>
        
        <!-- Area Gestione -->
        <div class="management-area">
            <!-- Sidebar per Controlli -->
            <div class="sidebar">
                <h3 class="sidebar-title">Nuovo Gruppo</h3>
                <form method="POST">
                    <input type="hidden" name="action" value="crea_gruppo">
                    
                    <div class="form-group">
                        <label for="nome_gruppo">Nome Gruppo</label>
                        <input type="text" id="nome_gruppo" name="nome_gruppo" placeholder="Es: Gruppo A" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="categoria">Categoria</label>
                        <select id="categoria" name="categoria" required>
                            <option value="">Seleziona Categoria</option>
                            <?php foreach ($categorie_disponibili as $categoria): ?>
                            <option value="<?php echo htmlspecialchars($categoria); ?>"><?php echo htmlspecialchars($categoria); ?></option>
                            <?php endforeach; ?>
                        </select>
                    </div>
                    
                    <button type="submit" class="btn btn-primary" style="width: 100%;">
                        Crea Nuovo Gruppo
                    </button>
                </form>
                
                <h3 class="sidebar-title" style="margin-top: 2rem;">Piloti disponibili</h3>
                <?php if (count($piloti_completi) > 0): ?>
                <div class="available-pilots-grid">
                    <?php foreach ($piloti_completi as $pilota): ?>
                    <div class="available-pilot-card" draggable="true" data-pilota-id="<?php echo $pilota['id']; ?>">
                        <div class="available-pilot-number"><?php echo $pilota['numero_gara']; ?></div>
                        <div class="available-pilot-name"><?php echo htmlspecialchars($pilota['nome'] . ' ' . $pilota['cognome']); ?></div>
                        <div class="pilot-category"><?php echo htmlspecialchars($pilota['categoria']); ?></div>
                    </div>
                    <?php endforeach; ?>
                </div>
                <div style="text-align: center; margin-top: 0.5rem; font-size: 0.75rem; color: var(--gray-500);">
                    I piloti già assegnati a un gruppo rimangono disponibili ma saranno rimossi dal gruppo precedente se trascinati in un nuovo gruppo.
                </div>
                <?php else: ?>
                <div class="empty-state" style="padding: 1rem;">
                    Non ci sono piloti iscritti a questo evento
                </div>
                <?php endif; ?>
            </div>
            
            <!-- Container Gruppi -->
            <div class="groups-container">
                <?php if (count($gruppi) > 0): ?>
                    <?php foreach ($gruppi as $gruppo): ?>
                    <div class="group-card" data-gruppo-id="<?php echo $gruppo['id']; ?>">
                        <div class="group-header">
                            <div class="group-title"><?php echo htmlspecialchars($gruppo['nome_gruppo']); ?></div>
                            <div class="group-actions">
                                <div class="group-action" onclick="openEditModal(<?php echo $gruppo['id']; ?>, '<?php echo htmlspecialchars($gruppo['nome_gruppo']); ?>', '<?php echo htmlspecialchars($gruppo['categoria']); ?>')">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" fill="currentColor" viewBox="0 0 16 16">
                                        <path d="m13.498.795.149-.149a1.207 1.207 0 1 1 1.707 1.708l-.149.148a1.5 1.5 0 0 1-.059 2.059L4.854 14.854a.5.5 0 0 1-.233.131l-4 1a.5.5 0 0 1-.606-.606l1-4a.5.5 0 0 1 .131-.232l9.642-9.642a.5.5 0 0 0-.642.056L6.854 4.854a.5.5 0 1 1-.708-.708L9.44.854A1.5 1.5 0 0 1 11.5.796a1.5 1.5 0 0 1 1.998-.001z"/>
                                    </svg>
                                </div>
                                <div class="group-action" onclick="openDeleteModal(<?php echo $gruppo['id']; ?>, '<?php echo htmlspecialchars($gruppo['nome_gruppo']); ?>')">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" fill="currentColor" viewBox="0 0 16 16">
                                        <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/>
                                        <path fill-rule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"/>
                                    </svg>
                                </div>
                            </div>
                        </div>
                        <div class="group-body">
                            <div class="group-info">
                                <div class="info-badge">
                                    <?php echo htmlspecialchars($gruppo['categoria']); ?>
                                </div>
                                <div class="info-badge">
                                    <?php echo count($gruppo['piloti']); ?> piloti
                                </div>
                            </div>
                            
                            <div class="pilot-list" data-droppable="true" data-gruppo-id="<?php echo $gruppo['id']; ?>">
                                <?php 
                                $piloti_gruppo = [];
                                foreach ($gruppo['piloti'] as $pilota_id) {
                                    foreach ($tutti_piloti as $pilota) {
                                        if ($pilota['id'] == $pilota_id) {
                                            $piloti_gruppo[] = $pilota;
                                            break;
                                        }
                                    }
                                }
                                
                                if (count($piloti_gruppo) > 0):
                                ?>
                                    <?php foreach ($piloti_gruppo as $pilota): ?>
                                    <div class="pilot-item" draggable="true" data-pilota-id="<?php echo $pilota['id']; ?>">
                                        <div class="pilot-info">
                                            <div class="pilot-number"><?php echo $pilota['numero_gara']; ?></div>
                                            <div class="pilot-name"><?php echo htmlspecialchars($pilota['nome'] . ' ' . $pilota['cognome']); ?></div>
                                        </div>
                                        <div class="pilot-actions">
                                            <form method="POST" style="display: inline;">
                                                <input type="hidden" name="action" value="rimuovi_pilota">
                                                <input type="hidden" name="gruppo_id" value="<?php echo $gruppo['id']; ?>">
                                                <input type="hidden" name="pilota_id" value="<?php echo $pilota['id']; ?>">
                                                <button type="submit" class="pilot-action" title="Rimuovi dal gruppo">
                                                    <svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" fill="currentColor" viewBox="0 0 16 16">
                                                        <path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"/>
                                                    </svg>
                                                </button>
                                            </form>
                                        </div>
                                    </div>
                                    <?php endforeach; ?>
                                <?php else: ?>
                                    <div class="drop-area">
                                        Trascina qui i piloti per aggiungerli al gruppo
                                    </div>
                                <?php endif; ?>
                            </div>
                        </div>
                    </div>
                    <?php endforeach; ?>
                <?php else: ?>
                    <div class="empty-state">
                        <div class="empty-icon">👥</div>
                        <h3>Nessun gruppo creato</h3>
                        <p class="empty-text">Usa il pannello a sinistra per creare il tuo primo gruppo</p>
                    </div>
                <?php endif; ?>
            </div>
        </div>
    </div>
    
    <!-- Modal Modifica Gruppo -->
    <div class="modal" id="edit-modal">
        <div class="modal-content">
            <div class="modal-header">
                <h3 class="modal-title">Modifica Gruppo</h3>
                <button type="button" class="modal-close" onclick="closeModal('edit-modal')">&times;</button>
            </div>
            <form method="POST">
                <input type="hidden" name="action" value="modifica_gruppo">
                <input type="hidden" name="gruppo_id" id="edit-gruppo-id">
                
                <div class="form-group">
                    <label for="edit-nome-gruppo">Nome Gruppo</label>
                    <input type="text" id="edit-nome-gruppo" name="nome_gruppo" required>
                </div>
                
                <div class="form-group">
                    <label for="edit-categoria">Categoria</label>
                    <select id="edit-categoria" name="categoria" required>
                        <?php foreach ($categorie_disponibili as $categoria): ?>
                        <option value="<?php echo htmlspecialchars($categoria); ?>"><?php echo htmlspecialchars($categoria); ?></option>
                        <?php endforeach; ?>
                    </select>
                </div>
                
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="closeModal('edit-modal')">Annulla</button>
                    <button type="submit" class="btn btn-primary">Salva Modifiche</button>
                </div>
            </form>
        </div>
    </div>
    
    <!-- Modal Elimina Gruppo -->
    <div class="modal" id="delete-modal">
        <div class="modal-content">
            <div class="modal-header">
                <h3 class="modal-title">Elimina Gruppo</h3>
                <button type="button" class="modal-close" onclick="closeModal('delete-modal')">&times;</button>
            </div>
            <p>Sei sicuro di voler eliminare il gruppo <strong id="delete-gruppo-nome"></strong>?</p>
            <p>Tutti i piloti assegnati a questo gruppo verranno rimossi.</p>
            
            <form method="POST">
                <input type="hidden" name="action" value="elimina_gruppo">
                <input type="hidden" name="gruppo_id" id="delete-gruppo-id">
                
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="closeModal('delete-modal')">Annulla</button>
                    <button type="submit" class="btn btn-danger">Elimina</button>
                </div>
            </form>
        </div>
    </div>
    
    <!-- Loading Indicator -->
    <div class="loading" id="loading-indicator">Operazione in corso...</div>
    
    <script>
        // Funzioni per gestire i modal
        function openEditModal(id, nome, categoria) {
            document.getElementById('edit-gruppo-id').value = id;
            document.getElementById('edit-nome-gruppo').value = nome;
            document.getElementById('edit-categoria').value = categoria;
            document.getElementById('edit-modal').classList.add('active');
        }
        
        function openDeleteModal(id, nome) {
            document.getElementById('delete-gruppo-id').value = id;
            document.getElementById('delete-gruppo-nome').textContent = nome;
            document.getElementById('delete-modal').classList.add('active');
        }
        
        function closeModal(id) {
            document.getElementById(id).classList.remove('active');
        }
        
        // Drag and Drop
        document.addEventListener('DOMContentLoaded', function() {
            const pilotItems = document.querySelectorAll('.pilot-item, .available-pilot-card');
            const dropTargets = document.querySelectorAll('[data-droppable="true"]');
            const dropAreas = document.querySelectorAll('.drop-area');
            
            let draggedElement = null;
            let sourceGroupId = null;
            
            // Per ogni elemento draggable
            pilotItems.forEach(item => {
                item.addEventListener('dragstart', function(e) {
                    draggedElement = this;
                    
                    // Troviamo il contenitore genitore (il gruppo)
                    const parentGroup = this.closest('[data-droppable="true"]');
                    if (parentGroup) {
                        sourceGroupId = parentGroup.dataset.gruppoId;
                    } else {
                        sourceGroupId = null; // Pilota non assegnato
                    }
                    
                    this.classList.add('dragging');
                    
                    // Salviamo l'ID del pilota nel dataTransfer
                    e.dataTransfer.setData('text/plain', this.dataset.pilotaId);
                    
                    // Mostriamo tutte le aree di drop
                    dropAreas.forEach(area => {
                        area.style.display = 'flex';
                    });
                });
                
                item.addEventListener('dragend', function() {
                    this.classList.remove('dragging');
                    
                    // Nascondiamo le aree di drop vuote
                    dropAreas.forEach(area => {
                        const parentList = area.closest('.pilot-list');
                        if (parentList && parentList.querySelectorAll('.pilot-item').length > 0) {
                            area.style.display = 'none';
                        }
                    });
                });
            });
            
            // Per ogni area di drop
            dropTargets.forEach(target => {
                target.addEventListener('dragover', function(e) {
                    e.preventDefault();
                    this.classList.add('highlight');
                    
                    // Evidenzia anche l'area di drop se presente
                    const dropArea = this.querySelector('.drop-area');
                    if (dropArea) {
                        dropArea.classList.add('highlight');
                    }
                });
                
                target.addEventListener('dragleave', function() {
                    this.classList.remove('highlight');
                    
                    // Rimuovi evidenziazione dall'area di drop
                    const dropArea = this.querySelector('.drop-area');
                    if (dropArea) {
                        dropArea.classList.remove('highlight');
                    }
                });
                
                target.addEventListener('drop', function(e) {
                    e.preventDefault();
                    this.classList.remove('highlight');
                    
                    // Rimuovi evidenziazione dall'area di drop
                    const dropArea = this.querySelector('.drop-area');
                    if (dropArea) {
                        dropArea.classList.remove('highlight');
                        dropArea.style.display = 'none';
                    }
                    
                    const pilotaId = e.dataTransfer.getData('text/plain');
                    const targetGroupId = this.dataset.gruppoId;
                    
                    // Non fare nulla se il pilota viene rilasciato nello stesso gruppo
                    if (sourceGroupId === targetGroupId) {
                        return;
                    }
                    
                    // Mostra l'indicatore di caricamento
                    document.getElementById('loading-indicator').style.display = 'block';
                    
                    // Prepara i dati per la richiesta
                    const formData = new FormData();
                    formData.append('action', 'sposta_pilota');
                    formData.append('pilota_id', pilotaId);
                    formData.append('gruppo_origine_id', sourceGroupId || 0); // 0 se il pilota non era assegnato
                    formData.append('gruppo_destinazione_id', targetGroupId);
                    
                    // Invia la richiesta AJAX
                    fetch(window.location.href, {
                        method: 'POST',
                        body: formData,
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest'
                        }
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            // Se il successo, ricarichiamo la pagina per aggiornare tutto
                            window.location.reload();
                        } else {
                            // Mostra un messaggio di errore
                            alert(data.message || 'Si è verificato un errore');
                        }
                    })
                    .catch(error => {
                        console.error('Errore:', error);
                        alert('Si è verificato un errore durante lo spostamento del pilota');
                    })
                    .finally(() => {
                        // Nascondi l'indicatore di caricamento
                        document.getElementById('loading-indicator').style.display = 'none';
                    });
                });
            });
        });
    </script>
</body>
</html>