<?php
session_start();

// Prima cosa importante: controlliamo se la persona è loggata
if (!isset($_SESSION['user'])) {
    // Se non è loggata, la mandiamo al login
    // È come quando un buttafuori ti chiede il biglietto!
    header('Location: pages/login.php');
    exit();
}

// E ora... il tuo database! Lo teniamo semplice
require_once './config/database.php';
$db = new Database();
$data = $db->readData();
?>

<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MX Pro - Dashboard</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #6366F1;
            --secondary: #EC4899;
            --accent: #10B981;
            --dark: #0F172A;
            --card: #1E293B;
            --text: #F8FAFC;
            --border: #334155;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Poppins', sans-serif;
            background: var(--dark);
            color: var(--text);
            padding: 2rem;
            min-height: 100vh;
            line-height: 1.6;
        }
        
        .dashboard {
            max-width: 1600px;
            margin: 0 auto;
        }
        
        .hero {
            margin-bottom: 4rem;
            text-align: center;
        }
        
        .logo {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            letter-spacing: -1px;
        }
        
        .logo span {
            color: var(--primary);
        }
        
        .subtitle {
            color: #94A3B8;
            font-size: 1.125rem;
            font-weight: 300;
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 1.5rem;
            margin-top: 3rem;
        }
        
        .card {
            background: var(--card);
            border-radius: 16px;
            padding: 1.5rem;
            position: relative;
            overflow: hidden;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            border: 1px solid var(--border);
        }
        
        .card:hover {
            transform: translateY(-8px);
            box-shadow: 0 24px 48px -12px rgba(0, 0, 0, 0.4);
            border-color: var(--primary);
        }
        
        .card-header {
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 1rem;
        }
        
        .icon {
            width: 48px;
            height: 48px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
        }
        
        .card-title {
            font-size: 1.25rem;
            font-weight: 600;
        }
        
        .card-content {
            margin-bottom: 1.5rem;
        }
        
        .description {
            color: #94A3B8;
            font-size: 0.9375rem;
        }
        
        .button-group {
            display: flex;
            gap: 0.75rem;
            flex-wrap: wrap;
        }
        
        .btn {
            padding: 0.625rem 1.25rem;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 500;
            font-size: 0.875rem;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .btn-primary {
            background: var(--primary);
            color: white;
        }
        
        .btn-primary:hover {
            background: #4F46E5;
            transform: scale(1.05);
        }
        
        .btn-outline {
            border: 1px solid var(--border);
            color: var(--text);
        }
        
        .btn-outline:hover {
            background: var(--border);
        }
        
        .btn-full {
            width: 100%;
            justify-content: center;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            font-weight: 600;
        }
        
        .btn-full:hover {
            opacity: 0.9;
            transform: translateY(-2px);
        }
        
        .glow {
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, var(--primary) 0%, transparent 70%);
            opacity: 0;
            transition: opacity 0.3s;
            pointer-events: none;
        }
        
        .card:hover .glow {
            opacity: 0.1;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
        
        .floating {
            animation: float 6s ease-in-out infinite;
        }
        
        .floating:nth-child(even) {
            animation-delay: -3s;
        }
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="hero">
            <h1 class="logo">MX<span>PRO</span></h1>
            <p class="subtitle">Dashboard di controllo per gestione gare motocross</p>
        </div>
        
        <div class="grid">
            <div class="card floating">
                <div class="glow"></div>
                <div class="card-header">
                    <div class="icon">👥</div>
                    <h2 class="card-title">Piloti</h2>
                </div>
                <div class="card-content">
                    <p class="description">Gestisci registrazioni, profili e categorie dei piloti</p>
                </div>
                <div class="button-group">
                    <a href="pages/iscrizione_pilota.php" class="btn btn-primary">+ Nuovo Pilota</a>
                    <a href="pages/lista_piloti.php" class="btn btn-outline">Visualizza Lista</a>
                </div>
            </div>
            
            <div class="card floating">
                <div class="glow"></div>
                <div class="card-header">
                    <div class="icon">🏁</div>
                    <h2 class="card-title">Eventi</h2>
                </div>
                <div class="card-content">
                    <p class="description">Organizza e gestisci le tue gare di motocross</p>
                </div>
                <div class="button-group">
                    <a href="pages/nuova_gara.php" class="btn btn-primary">+ Nuova Gara</a>
                    <a href="pages/gare_disponibili.php" class="btn btn-outline">Iscrizioni</a>
                </div>
            </div>
            
            <div class="card floating">
                <div class="glow"></div>
                <div class="card-header">
                    <div class="icon">⏱️</div>
                    <h2 class="card-title">Timing</h2>
                </div>
                <div class="card-content">
                    <p class="description">Sistema di cronometraggio in tempo reale</p>
                </div>
                <a href="pages/cronometraggio.php" class="btn btn-full">Avvia Cronometraggio</a>
            </div>
            
            <div class="card floating">
                <div class="glow"></div>
                <div class="card-header">
                    <div class="icon">📊</div>
                    <h2 class="card-title">Risultati</h2>
                </div>
                <div class="card-content">
                    <p class="description">Visualizza classifiche e statistiche</p>
                </div>
                <a href="#" class="btn btn-full">Vedi Classifiche</a>
            </div>
            
            <div class="card floating">
                <div class="glow"></div>
                <div class="card-header">
                    <div class="icon">⚙️</div>
                    <h2 class="card-title">Settings</h2>
                </div>
                <div class="card-content">
                    <p class="description">Configura il sistema secondo le tue esigenze</p>
                </div>
                <a href="#" class="btn btn-full">Configurazione</a>
            </div>
            
            <div class="card floating">
                <div class="glow"></div>
                <div class="card-header">
                    <div class="icon">👋</div>
                    <h2 class="card-title">Logout</h2>
                </div>
                <div class="card-content">
                    <p class="description">Termina la sessione corrente</p>
                </div>
                <a href="pages/logout.php" class="btn btn-full">Disconnetti</a>
            </div>
        </div>
    </div>
</body>
</html>