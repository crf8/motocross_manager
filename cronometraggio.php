<?php
session_start();
if (!isset($_SESSION['user'])) {
    header('Location: login.php');
    exit();
}

require_once '../config/database.php';
$db = new Database();
$data = $db->readData();

// IMPORTANTE: Modifica qui per vedere TUTTE le gare
$eventi = $data['eventi'] ?? [];
$eventi_cronometraggio = [];

// Controlliamo ogni gara e la mostriamo solo se ha una data valida
foreach($eventi as $evento) {
    // Controlliamo che l'evento abbia una data
    if (isset($evento['data_evento']) && !empty($evento['data_evento'])) {
        $data_evento = $evento['data_evento'];
        
        // Se la data è valida, la mostriamo
        if (strtotime($data_evento)) {
            $eventi_cronometraggio[] = $evento;
        }
    }
}
?>

<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <title>Cronometraggio Gare - MX Pro</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Montserrat:wght@800&display=swap" rel="stylesheet">
    <style>
        :root {
            /* Palette di colori moderna */
            --primary: #3B82F6;
            --secondary: #EF4444;
            --accent: #10B981;
            --dark: #1E293B;
            --card-bg: #FFFFFF;
            --text-primary: #1E293B;
            --text-secondary: #64748B;
            --border: #E2E8F0;
            --success: #22C55E;
            --warning: #F59E0B;
            --background: #F8FAFC;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', sans-serif;
            background: var(--background);
            color: var(--text-primary);
            padding: 2rem;
            line-height: 1.6;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        /* Header modernizzato */
        .header {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            padding: 3rem 2rem;
            border-radius: 24px;
            margin-bottom: 2rem;
            color: white;
            text-align: center;
            position: relative;
            overflow: hidden;
        }
        
        .header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(45deg, transparent 49%, rgba(255,255,255,0.1) 50%, transparent 51%);
            background-size: 20px 20px;
        }
        
        .header-content {
            position: relative;
            z-index: 1;
        }
        
        .header h1 {
            font-family: 'Montserrat', sans-serif;
            font-size: 3rem;
            font-weight: 800;
            margin-bottom: 1rem;
            text-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        
        .header p {
            font-size: 1.25rem;
            opacity: 0.9;
        }
        
        .back-button {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            background: var(--dark);
            color: white;
            padding: 0.75rem 1.5rem;
            text-decoration: none;
            border-radius: 12px;
            font-weight: 500;
            margin-bottom: 2rem;
            transition: all 0.3s ease;
        }
        
        .back-button:hover {
            background: #334155;
            transform: translateX(-4px);
        }
        
        /* Grid moderno per le gare */
        .events-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
            gap: 1.5rem;
            margin-top: 2rem;
        }
        
        .event-card {
            background: var(--card-bg);
            border-radius: 16px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            padding: 1.5rem;
            transition: all 0.3s ease;
            border: 1px solid var(--border);
        }
        
        .event-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 24px -4px rgba(0, 0, 0, 0.15);
            border-color: var(--primary);
        }
        
        .event-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }
        
        .event-title {
            font-size: 1.75rem;
            font-weight: 700;
            color: var(--primary);
        }
        
        .event-type {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 50px;
            font-size: 0.875rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .event-details {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1rem;
            margin-bottom: 1.5rem;
        }
        
        .detail-item {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            color: var(--text-secondary);
        }
        
        .detail-icon {
            width: 40px;
            height: 40px;
            border-radius: 10px;
            background: var(--background);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.25rem;
        }
        
        .categories-pills {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-bottom: 1.5rem;
        }
        
        .category-pill {
            background: var(--background);
            color: var(--text-primary);
            padding: 0.25rem 0.75rem;
            border-radius: 50px;
            font-size: 0.875rem;
            font-weight: 500;
        }
        
        .timing-button {
            width: 100%;
            background: linear-gradient(135deg, var(--accent), var(--primary));
            color: white;
            padding: 1rem;
            border: none;
            border-radius: 12px;
            font-size: 1.125rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            position: relative;
            overflow: hidden;
        }
        
        .timing-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 24px -4px rgba(16, 185, 129, 0.4);
        }
        
        .timing-button::after {
            content: '→';
            position: absolute;
            right: 1rem;
            top: 50%;
            transform: translateY(-50%);
            transition: all 0.3s ease;
        }
        
        .timing-button:hover::after {
            transform: translateY(-50%) translateX(4px);
        }
        
        /* Empty state moderno */
        .empty-state {
            background: var(--card-bg);
            border-radius: 16px;
            padding: 4rem 2rem;
            text-align: center;
            margin-top: 3rem;
            border: 2px dashed var(--border);
        }
        
        .empty-icon {
            width: 80px;
            height: 80px;
            background: var(--background);
            border-radius: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 1.5rem;
            font-size: 2rem;
        }
        
        .empty-state h3 {
            font-size: 1.875rem;
            margin-bottom: 0.5rem;
            color: var(--text-primary);
        }
        
        .empty-state p {
            color: var(--text-secondary);
            margin-bottom: 2rem;
        }
        
        .create-event-btn {
            background: linear-gradient(135deg, var(--secondary), var(--primary));
            color: white;
            padding: 1rem 2rem;
            text-decoration: none;
            border-radius: 12px;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            transition: all 0.3s ease;
        }
        
        .create-event-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 24px -4px rgba(239, 68, 68, 0.4);
        }
        
        /* Responsive design */
        @media (max-width: 768px) {
            .header h1 {
                font-size: 2rem;
            }
            
            .events-grid {
                grid-template-columns: 1fr;
            }
            
            .event-details {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <a href="../index.php" class="back-button">
            ← Torna alla Dashboard
        </a>
        
        <div class="header">
            <div class="header-content">
                <h1>Sistema di Cronometraggio</h1>
                <p>Seleziona una gara per iniziare il timing</p>
            </div>
        </div>
        
        <?php if (count($eventi_cronometraggio) > 0): ?>
            <div class="events-grid">
                <?php foreach($eventi_cronometraggio as $evento): ?>
                <div class="event-card">
                    <div class="event-header">
                        <h2 class="event-title"><?php echo htmlspecialchars($evento['nome_evento']); ?></h2>
                        <span class="event-type"><?php echo htmlspecialchars($evento['tipo']); ?></span>
                    </div>
                    
                    <div class="event-details">
                        <div class="detail-item">
                            <div class="detail-icon">📅</div>
                            <div>
                                <small>Data</small><br>
                                <strong><?php echo date('d/m/Y', strtotime($evento['data_evento'])); ?></strong>
                            </div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-icon">📍</div>
                            <div>
                                <small>Località</small><br>
                                <strong><?php echo htmlspecialchars($evento['luogo']); ?></strong>
                            </div>
                        </div>
                    </div>
                    
                    <div class="categories-pills">
                        <?php foreach($evento['categorie'] as $categoria): ?>
                            <span class="category-pill"><?php echo htmlspecialchars($categoria); ?></span>
                        <?php endforeach; ?>
                    </div>
                    
                    <a href="cronometraggio_sessione.php?id=<?php echo $evento['id']; ?>" class="timing-button">
                        Avvia Cronometraggio
                    </a>
                </div>
                <?php endforeach; ?>
            </div>
        <?php else: ?>
            <div class="empty-state">
                <div class="empty-icon">⏱️</div>
                <h3>Nessuna gara disponibile</h3>
                <p>Non ci sono eventi al momento. Crea una nuova gara per iniziare.</p>
                <a href="nuova_gara.php" class="create-event-btn">
                    ➕ Crea Nuova Gara
                </a>
            </div>
        <?php endif; ?>
    </div>
</body>
</html>