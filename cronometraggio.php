<?php
session_start();
if (!isset($_SESSION['user'])) {
    header('Location: login.php');
    exit();
}

// Usiamo la nuova classe MongoCompatDB
require_once '../config/MongoCompatDB.php';
$db = new MongoCompatDB();

// Prendiamo tutti gli eventi
$eventi = $db->readCollection('eventi');
$eventi_cronometraggio = [];

// Filtriamo solo gli eventi con data valida
foreach($eventi as $evento) {
    if (isset($evento['data_evento']) && !empty($evento['data_evento'])) {
        if (strtotime($evento['data_evento'])) {
            $eventi_cronometraggio[] = $evento;
        }
    }
}
?>

<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cronometraggio - MX Manager</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #2563eb;
            --accent: #f43f5e;
            --dark: #0f172a;
            --light: #f8fafc;
            --gray: #cbd5e1;
            --text: #1e293b;
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
            text-align: center;
            margin-bottom: 40px;
            padding: 30px 0;
            border-bottom: 2px solid var(--gray);
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            color: var(--primary);
        }
        
        .header p {
            color: var(--text);
            font-size: 1.1rem;
        }
        
        .back-btn {
            display: inline-block;
            margin-bottom: 30px;
            padding: 12px 20px;
            background-color: var(--dark);
            color: white;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 500;
            transition: background-color 0.3s;
        }
        
        .back-btn:hover {
            background-color: #1e293b;
        }
        
        .events-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
        }
        
        .event-card {
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            transition: transform 0.3s, box-shadow 0.3s;
        }
        
        .event-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
        }
        
        .event-header {
            padding: 20px;
            border-bottom: 1px solid var(--gray);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .event-title {
            font-size: 1.3rem;
            font-weight: 700;
        }
        
        .event-type {
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 500;
            background-color: var(--primary);
            color: white;
        }
        
        .event-details {
            padding: 20px;
        }
        
        .detail-row {
            display: flex;
            margin-bottom: 15px;
        }
        
        .detail-label {
            flex: 0 0 120px;
            color: #64748b;
            font-size: 0.9rem;
        }
        
        .detail-value {
            font-weight: 500;
        }
        
        .categories {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 15px;
        }
        
        .category {
            padding: 5px 10px;
            background-color: #f1f5f9;
            border-radius: 4px;
            font-size: 0.85rem;
        }
        
        .timing-btn {
            display: block;
            width: 100%;
            padding: 15px;
            margin-top: 20px;
            border: none;
            background-color: var(--accent);
            color: white;
            text-align: center;
            text-decoration: none;
            font-weight: 700;
            border-radius: 6px;
            transition: background-color 0.3s;
        }
        
        .timing-btn:hover {
            background-color: #e11d48;
        }
        
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .empty-icon {
            font-size: 3rem;
            margin-bottom: 20px;
        }
        
        .empty-state h3 {
            font-size: 1.5rem;
            margin-bottom: 10px;
        }
        
        .empty-state p {
            margin-bottom: 25px;
            color: #64748b;
        }
        
        .create-btn {
            display: inline-block;
            padding: 12px 25px;
            background-color: var(--accent);
            color: white;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 500;
        }
        
        @media (max-width: 768px) {
            .events-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Sistema di Cronometraggio</h1>
            <p>Seleziona un evento per iniziare a cronometrare</p>
        </div>
        
        <a href="../index.php" class="back-btn">← Torna alla Dashboard</a>
        
        <?php if (count($eventi_cronometraggio) > 0): ?>
            <div class="events-grid">
                <?php foreach($eventi_cronometraggio as $evento): ?>
                <div class="event-card">
                    <div class="event-header">
                        <h2 class="event-title"><?php echo htmlspecialchars($evento['nome_evento']); ?></h2>
                        <span class="event-type"><?php echo htmlspecialchars($evento['tipo']); ?></span>
                    </div>
                    
                    <div class="event-details">
                        <div class="detail-row">
                            <div class="detail-label">Data:</div>
                            <div class="detail-value"><?php echo date('d/m/Y', strtotime($evento['data_evento'])); ?></div>
                        </div>
                        
                        <div class="detail-row">
                            <div class="detail-label">Luogo:</div>
                            <div class="detail-value"><?php echo htmlspecialchars($evento['luogo']); ?></div>
                        </div>
                        
                        <div class="detail-row">
                            <div class="detail-label">Categorie:</div>
                            <div class="categories">
                                <?php foreach($evento['categorie'] as $categoria): ?>
                                    <span class="category"><?php echo htmlspecialchars($categoria); ?></span>
                                <?php endforeach; ?>
                            </div>
                        </div>
                        
                        <a href="cronometraggio_sessione.php?id=<?php echo $evento['id']; ?>" class="timing-btn">
                            Avvia Cronometraggio
                        </a>
                    </div>
                </div>
                <?php endforeach; ?>
            </div>
        <?php else: ?>
            <div class="empty-state">
                <div class="empty-icon">⏱️</div>
                <h3>Nessuna gara disponibile</h3>
                <p>Non ci sono eventi programmati al momento.</p>
                <a href="nuova_gara.php" class="create-btn">+ Crea Nuova Gara</a>
            </div>
        <?php endif; ?>
    </div>
</body>
</html>