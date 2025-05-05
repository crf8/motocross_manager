<?php
session_start();
if (!isset($_SESSION['user'])) {
    header('Location: login.php');
    exit();
}

require_once '../config/database.php';
$db = new Database();
$data = $db->readData();
$eventi = $data['eventi'] ?? [];
?>

<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <title>Gare Disponibili - Motocross Manager Pro</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #3B82F6;
            --secondary: #EF4444;
            --accent: #10B981;
            --dark: #0F172A;
            --light: #94A3B8;
            --border: #E2E8F0;
            --card-bg: #FFFFFF;
            --background: #F8FAFC;
            --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', sans-serif;
            background: var(--background);
            color: var(--dark);
            min-height: 100vh;
            padding: 1.5rem;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem 0;
        }
        
        /* Header moderno */
        .page-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 3rem;
        }
        
        h1 {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 3rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--secondary), var(--primary));
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            display: flex;
            align-items: center;
            gap: 1rem;
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
            transition: all 0.3s ease;
            box-shadow: var(--shadow);
        }
        
        .back-button:hover {
            background: #1E293B;
            transform: translateX(-4px);
        }
        
        /* Griglia delle gare */
        .races-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
            gap: 1.5rem;
            margin-top: 2rem;
        }
        
        .race-card {
            background: var(--card-bg);
            border-radius: 16px;
            box-shadow: var(--shadow);
            border: 1px solid var(--border);
            padding: 1.5rem;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .race-card:hover {
            transform: translateY(-8px);
            box-shadow: var(--shadow-lg);
        }
        
        .race-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 6px;
            background: linear-gradient(to right, var(--primary), var(--secondary));
        }
        
        .race-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
        }
        
        .race-title {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--dark);
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }
        
        .race-title .emoji {
            font-size: 1.75rem;
        }
        
        .race-type {
            background: linear-gradient(135deg, var(--primary), var(--accent));
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 50px;
            text-transform: uppercase;
            font-size: 0.875rem;
            font-weight: 600;
            letter-spacing: 0.5px;
        }
        
        .race-info {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1rem;
            margin-bottom: 1.5rem;
        }
        
        .info-item {
            background: var(--background);
            padding: 1rem;
            border-radius: 12px;
            text-align: center;
        }
        
        .info-label {
            color: var(--light);
            font-size: 0.875rem;
            font-weight: 500;
            margin-bottom: 0.25rem;
        }
        
        .info-value {
            font-weight: 700;
            color: var(--dark);
            font-size: 1.125rem;
        }
        
        .categories-info {
            margin-bottom: 1.5rem;
        }
        
        .categories-info h4 {
            margin-bottom: 0.75rem;
            color: var(--dark);
            font-weight: 600;
        }
        
        .categories-grid {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }
        
        .category-pill {
            background: var(--background);
            color: var(--dark);
            padding: 0.5rem 1rem;
            border-radius: 50px;
            font-size: 0.875rem;
            font-weight: 500;
            border: 1px solid var(--border);
        }
        
        .iscrivi-button {
            width: 100%;
            background: linear-gradient(135deg, var(--secondary), var(--primary));
            color: white;
            border: none;
            padding: 1rem;
            border-radius: 12px;
            cursor: pointer;
            text-decoration: none;
            text-align: center;
            display: inline-block;
            font-weight: 600;
            font-size: 1.125rem;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .iscrivi-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 24px -8px rgba(239, 68, 68, 0.6);
        }
        
        .iscrivi-button::after {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 5px;
            height: 5px;
            background: rgba(255, 255, 255, 0.5);
            opacity: 0;
            border-radius: 100%;
            transform: scale(1, 1) translate(-50%);
            transform-origin: 50% 50%;
        }
        
        .iscrivi-button:focus::after {
            animation: ripple 1s ease-out;
        }
        
        @keyframes ripple {
            0% {
                transform: scale(0, 0);
                opacity: 1;
            }
            20% {
                transform: scale(25, 25);
                opacity: 1;
            }
            100% {
                opacity: 0;
                transform: scale(40, 40);
            }
        }
        
        /* Empty state migliorato */
        .empty-state {
            text-align: center;
            padding: 5rem 2rem;
            background: var(--card-bg);
            border-radius: 16px;
            margin-top: 3rem;
            box-shadow: var(--shadow);
            border: 2px dashed var(--border);
        }
        
        .empty-icon {
            width: 100px;
            height: 100px;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            border-radius: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 1.5rem;
            font-size: 3rem;
        }
        
        .empty-state h3 {
            color: var(--dark);
            font-size: 1.875rem;
            margin-bottom: 0.5rem;
            font-family: 'Space Grotesk', sans-serif;
        }
        
        .empty-state p {
            color: var(--light);
            margin-bottom: 2rem;
            font-size: 1.125rem;
        }
        
        .create-race-btn {
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
        
        .create-race-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 24px -8px rgba(239, 68, 68, 0.6);
        }
        
        /* Responsive design */
        @media (max-width: 768px) {
            body {
                padding: 1rem;
            }
            
            h1 {
                font-size: 2rem;
            }
            
            .races-grid {
                grid-template-columns: 1fr;
            }
            
            .race-info {
                grid-template-columns: 1fr;
            }
            
            .page-header {
                flex-direction: column;
                gap: 1rem;
                text-align: center;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="page-header">
            <h1><span class="emoji">🏁</span> Gare Disponibili</h1>
            <a href="../index.php" class="back-button">← Torna alla Dashboard</a>
        </div>
        
        <?php if (count($eventi) > 0): ?>
            <div class="races-grid">
                <?php foreach($eventi as $evento): ?>
                <div class="race-card">
                    <div class="race-header">
                        <h2 class="race-title">
                            <?php 
                            // Emoji personalizzate per tipo di gara
                            $emoji = '🏍️'; // Default
                            if ($evento['tipo'] == 'campionato') $emoji = '🏆';
                            elseif ($evento['tipo'] == 'trofeo') $emoji = '🎯';
                            elseif ($evento['tipo'] == 'sociale') $emoji = '🚀';
                            elseif ($evento['tipo'] == 'allenamento') $emoji = '💪';
                            ?>
                            <span class="emoji"><?php echo $emoji; ?></span>
                            <?php echo htmlspecialchars($evento['nome_evento']); ?>
                        </h2>
                        <span class="race-type"><?php echo htmlspecialchars($evento['tipo']); ?></span>
                    </div>
                    
                    <div class="race-info">
                        <div class="info-item">
                            <div class="info-label">Data</div>
                            <div class="info-value"><?php echo date('d/m/Y', strtotime($evento['data_evento'])); ?></div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Località</div>
                            <div class="info-value"><?php echo htmlspecialchars($evento['luogo']); ?></div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Quote</div>
                            <div class="info-value">€<?php echo $evento['quota_prima']; ?></div>
                        </div>
                    </div>
                    
                    <div class="categories-info">
                        <h4>Categorie Ammesse</h4>
                        <div class="categories-grid">
                            <?php foreach($evento['categorie'] as $categoria): ?>
                                <span class="category-pill">
                                    <?php echo htmlspecialchars($categoria); ?>
                                </span>
                            <?php endforeach; ?>
                        </div>
                    </div>
                    
                    <a href="iscrizione_gara.php?id=<?php echo $evento['id']; ?>" class="iscrivi-button">
                        ISCRIVITI ORA
                    </a>
                </div>
                <?php endforeach; ?>
            </div>
        <?php else: ?>
            <div class="empty-state">
                <div class="empty-icon">🏁</div>
                <h3>Nessuna gara disponibile</h3>
                <p>Al momento non ci sono gare programmate.</p>
                <a href="nuova_gara.php" class="create-race-btn">
                    ➕ Crea Nuova Gara
                </a>
            </div>
        <?php endif; ?>
    </div>
</body>
</html>