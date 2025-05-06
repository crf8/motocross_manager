<?php
session_start();
if (!isset($_SESSION['user'])) {
    header('Location: login.php');
    exit();
}

// Usiamo la nuova classe MongoCompatDB
require_once '../config/MongoCompatDB.php';
$db = new MongoCompatDB();

$evento_id = $_GET['id'] ?? 0;
$evento = null;

// Cerchiamo l'evento
foreach($db->readCollection('eventi') as $e) {
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
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sistema di Cronometraggio - <?php echo htmlspecialchars($evento['nome_evento']); ?></title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Montserrat:wght@700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #ff3e00;
            --primary-dark: #d93500;
            --primary-light: #ff6e40;
            --secondary: #0066ff;
            --secondary-dark: #0050cc;
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
            --success: #00b894;
            --warning: #fdcb6e;
            --box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Poppins', sans-serif;
            background-color: var(--gray-100);
            color: var(--dark);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        .navbar {
            background-color: var(--darker);
            color: var(--light);
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        
        .navbar-brand {
            font-family: 'Montserrat', sans-serif;
            font-weight: 800;
            font-size: 1.5rem;
            color: var(--light);
            text-decoration: none;
        }
        
        .navbar-brand span {
            color: var(--primary);
        }
        
        .nav-links {
            display: flex;
            gap: 1.5rem;
        }
        
        .nav-link {
            color: var(--gray-400);
            text-decoration: none;
            font-weight: 500;
            transition: color 0.3s;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .nav-link:hover {
            color: var(--primary);
        }
        
        .active {
            color: var(--primary);
            position: relative;
        }
        
        .active::after {
            content: '';
            position: absolute;
            bottom: -5px;
            left: 0;
            right: 0;
            height: 2px;
            background-color: var(--primary);
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
            flex: 1;
        }
        
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
        }
        
        .page-title {
            font-family: 'Montserrat', sans-serif;
            font-weight: 800;
            font-size: 2rem;
            color: var(--dark);
            margin-bottom: 0.5rem;
        }
        
        .breadcrumb {
            color: var(--gray-600);
            margin-bottom: 2rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .breadcrumb a {
            color: var(--gray-600);
            text-decoration: none;
        }
        
        .breadcrumb a:hover {
            color: var(--primary);
        }
        
        .back-btn {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            background-color: var(--dark);
            color: var(--light);
            padding: 0.75rem 1.5rem;
            border-radius: 50px;
            text-decoration: none;
            font-weight: 500;
            transition: all 0.3s;
            border: none;
            cursor: pointer;
        }
        
        .back-btn:hover {
            background-color: var(--primary);
            transform: translateX(-5px);
        }
        
        .event-card {
            background-color: var(--light);
            border-radius: 15px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: var(--box-shadow);
            border-left: 5px solid var(--primary);
        }
        
        .event-title {
            font-family: 'Montserrat', sans-serif;
            font-weight: 700;
            font-size: 1.5rem;
            color: var(--dark);
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }
        
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin-top: 1.5rem;
        }
        
        .info-item {
            display: flex;
            align-items: flex-start;
            gap: 0.75rem;
        }
        
        .info-icon {
            width: 40px;
            height: 40px;
            background-color: var(--gray-100);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.25rem;
            color: var(--primary);
            flex-shrink: 0;
        }
        
        .info-content {
            flex-grow: 1;
        }
        
        .info-label {
            color: var(--gray-600);
            font-size: 0.875rem;
            margin-bottom: 0.25rem;
        }
        
        .info-value {
            font-weight: 600;
            color: var(--dark);
        }
        
        .action-buttons {
            display: flex;
            justify-content: flex-end;
            gap: 1rem;
            margin-top: 1.5rem;
        }
        
        .session-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-top: 2.5rem;
        }
        
        .session-card {
            background-color: var(--light);
            border-radius: 15px;
            overflow: hidden;
            box-shadow: var(--box-shadow);
            transition: all 0.3s;
            display: flex;
            flex-direction: column;
            height: 100%;
        }
        
        .session-card:hover {
            transform: translateY(-10px);
        }
        
        .session-card:hover .session-timer {
            transform: scale(1.1);
        }
        
        .session-header {
            background: linear-gradient(to right, var(--primary), var(--primary-dark));
            color: var(--light);
            padding: 1.5rem;
            text-align: center;
            position: relative;
        }
        
        .session-header::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 10px;
            background: repeating-linear-gradient(
                -45deg,
                rgba(0, 0, 0, 0.1),
                rgba(0, 0, 0, 0.1) 10px,
                rgba(0, 0, 0, 0.2) 10px,
                rgba(0, 0, 0, 0.2) 20px
            );
        }
        
        .session-timer {
            width: 100px;
            height: 100px;
            background-color: var(--darker);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: -50px auto 1rem;
            border: 5px solid var(--light);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
            position: relative;
            z-index: 2;
            transition: all 0.3s;
            font-size: 2.5rem;
        }
        
        .prove-libere .session-timer {
            background-color: var(--success);
        }
        
        .qualifiche .session-timer {
            background-color: var(--warning);
        }
        
        .manche-1 .session-timer {
            background-color: var(--secondary);
        }
        
        .manche-2 .session-timer {
            background-color: var(--primary);
        }
        
        .session-body {
            padding: 2rem;
            text-align: center;
            display: flex;
            flex-direction: column;
            flex-grow: 1;
            justify-content: space-between;
        }
        
        .session-title {
            font-family: 'Montserrat', sans-serif;
            font-weight: 700;
            font-size: 1.25rem;
            margin-bottom: 1rem;
        }
        
        .session-time {
            color: var(--gray-600);
            margin-bottom: 1.5rem;
            font-size: 0.875rem;
        }
        
        .session-btn {
            display: inline-block;
            background: linear-gradient(to right, var(--secondary), var(--secondary-dark));
            color: var(--light);
            padding: 0.75rem 1.5rem;
            border-radius: 50px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s;
            border: none;
            cursor: pointer;
            margin-top: auto;
        }
        
        .session-btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 5px 15px rgba(0, 102, 255, 0.3);
        }
        
        .session-stats {
            display: flex;
            justify-content: center;
            gap: 1rem;
            margin: 1rem 0 1.5rem;
        }
        
        .stat {
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        
        .stat-value {
            font-weight: 700;
            font-size: 1.5rem;
            color: var(--dark);
        }
        
        .stat-label {
            font-size: 0.75rem;
            color: var(--gray-600);
        }
        
        .footer {
            background-color: var(--darker);
            color: var(--gray-500);
            text-align: center;
            padding: 1.5rem;
            font-size: 0.875rem;
        }
        
        @media (max-width: 768px) {
            .navbar {
                flex-direction: column;
                gap: 1rem;
                padding: 1rem;
                text-align: center;
            }
            
            .nav-links {
                flex-wrap: wrap;
                justify-content: center;
            }
            
            .container {
                padding: 1rem;
            }
            
            .header {
                flex-direction: column;
                align-items: flex-start;
                gap: 1rem;
            }
            
            .session-grid {
                grid-template-columns: 1fr;
            }
            
            .info-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <a href="../index.php" class="navbar-brand">MX<span>PRO</span></a>
        <div class="nav-links">
            <a href="../index.php" class="nav-link">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                    <path d="M8.707 1.5a1 1 0 0 0-1.414 0L.646 8.146a.5.5 0 0 0 .708.708L8 2.207l6.646 6.647a.5.5 0 0 0 .708-.708L13 5.793V2.5a.5.5 0 0 0-.5-.5h-1a.5.5 0 0 0-.5.5v1.293L8.707 1.5Z"/>
                    <path d="m8 3.293 6 6V13.5a1.5 1.5 0 0 1-1.5 1.5h-9A1.5 1.5 0 0 1 2 13.5V9.293l6-6Z"/>
                </svg>
                Dashboard
            </a>
            <a href="gare_disponibili.php" class="nav-link">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                    <path d="M14.5 3a.5.5 0 0 1 .5.5v9a.5.5 0 0 1-.5.5h-13a.5.5 0 0 1-.5-.5v-9a.5.5 0 0 1 .5-.5h13zm-13-1A1.5 1.5 0 0 0 0 3.5v9A1.5 1.5 0 0 0 1.5 14h13a1.5 1.5 0 0 0 1.5-1.5v-9A1.5 1.5 0 0 0 14.5 2h-13z"/>
                    <path d="M7 5.5a.5.5 0 0 1 .5-.5h5a.5.5 0 0 1 0 1h-5a.5.5 0 0 1-.5-.5zm-1.496-.854a.5.5 0 0 1 0 .708l-1.5 1.5a.5.5 0 0 1-.708 0l-.5-.5a.5.5 0 1 1 .708-.708l.146.147 1.146-1.147a.5.5 0 0 1 .708 0zM7 9.5a.5.5 0 0 1 .5-.5h5a.5.5 0 0 1 0 1h-5a.5.5 0 0 1-.5-.5zm-1.496-.854a.5.5 0 0 1 0 .708l-1.5 1.5a.5.5 0 0 1-.708 0l-.5-.5a.5.5 0 0 1 .708-.708l.146.147 1.146-1.147a.5.5 0 0 1 .708 0z"/>
                </svg>
                Eventi
            </a>
            <a href="lista_piloti.php" class="nav-link">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                    <path d="M15 14s1 0 1-1-1-4-5-4-5 3-5 4 1 1 1 1h8Zm-7.978-1A.261.261 0 0 1 7 12.996c.001-.264.167-1.03.76-1.72C8.312 10.629 9.282 10 11 10c1.717 0 2.687.63 3.24 1.276.593.69.758 1.457.76 1.72l-.008.002a.274.274 0 0 1-.014.002H7.022ZM11 7a2 2 0 1 0 0-4 2 2 0 0 0 0 4Zm3-2a3 3 0 1 1-6 0 3 3 0 0 1 6 0ZM6.936 9.28a5.88 5.88 0 0 0-1.23-.247A7.35 7.35 0 0 0 5 9c-4 0-5 3-5 4 0 .667.333 1 1 1h4.216A2.238 2.238 0 0 1 5 13c0-1.01.377-2.042 1.09-2.904.243-.294.526-.569.846-.816ZM4.92 10A5.493 5.493 0 0 0 4 13H1c0-.26.164-1.03.76-1.724.545-.636 1.492-1.256 3.16-1.275ZM1.5 5.5a3 3 0 1 1 6 0 3 3 0 0 1-6 0Zm3-2a2 2 0 1 0 0 4 2 2 0 0 0 0-4Z"/>
                </svg>
                Piloti
            </a>
            <a href="cronometraggio.php" class="nav-link active">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                    <path d="M8 3.5a.5.5 0 0 0-1 0V9a.5.5 0 0 0 .252.434l3.5 2a.5.5 0 0 0 .496-.868L8 8.71V3.5z"/>
                    <path d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm7-8A7 7 0 1 1 1 8a7 7 0 0 1 14 0z"/>
                </svg>
                Cronometraggio
            </a>
        </div>
    </nav>

    <div class="container">
        <div class="breadcrumb">
            <a href="../index.php">Home</a> &gt;
            <a href="cronometraggio.php">Cronometraggio</a> &gt;
            <span><?php echo htmlspecialchars($evento['nome_evento']); ?></span>
        </div>
        
        <div class="header">
            <div>
                <h1 class="page-title">Sistema di Cronometraggio</h1>
                <p>Seleziona una sessione per l'evento</p>
            </div>
            
            <a href="cronometraggio.php" class="back-btn">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                    <path fill-rule="evenodd" d="M15 8a.5.5 0 0 0-.5-.5H2.707l3.147-3.146a.5.5 0 1 0-.708-.708l-4 4a.5.5 0 0 0 0 .708l4 4a.5.5 0 0 0 .708-.708L2.707 8.5H14.5A.5.5 0 0 0 15 8z"/>
                </svg>
                Torna alla Lista Eventi
            </a>
        </div>
        
        <div class="event-card">
            <h2 class="event-title">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                    <path d="M12.643 15C13.979 15 15 13.845 15 12.5V5H1v7.5C1 13.845 2.021 15 3.357 15h9.286zM5.5 7h5a.5.5 0 0 1 0 1h-5a.5.5 0 0 1 0-1zM.8 1a.8.8 0 0 0-.8.8V3a.8.8 0 0 0 .8.8h14.4A.8.8 0 0 0 16 3V1.8a.8.8 0 0 0-.8-.8H.8z"/>
                </svg>
                <?php echo htmlspecialchars($evento['nome_evento']); ?>
            </h2>
            
            <div class="info-grid">
                <div class="info-item">
                    <div class="info-icon">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
                            <path d="M11 6.5a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-1a.5.5 0 0 1-.5-.5v-1zm-3 0a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-1a.5.5 0 0 1-.5-.5v-1zm-5 3a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-1a.5.5 0 0 1-.5-.5v-1zm3 0a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-1a.5.5 0 0 1-.5-.5v-1z"/>
                            <path d="M3.5 0a.5.5 0 0 1 .5.5V1h8V.5a.5.5 0 0 1 1 0V1h1a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V3a2 2 0 0 1 2-2h1V.5a.5.5 0 0 1 .5-.5zM1 4v10a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V4H1z"/>
                        </svg>
                    </div>
                    <div class="info-content">
                        <div class="info-label">Data</div>
                        <div class="info-value"><?php echo date('d/m/Y', strtotime($evento['data_evento'])); ?></div>
                    </div>
                </div>
                
                <div class="info-item">
                    <div class="info-icon">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
                            <path d="M8 16s6-5.686 6-10A6 6 0 0 0 2 6c0 4.314 6 10 6 10zm0-7a3 3 0 1 1 0-6 3 3 0 0 1 0 6z"/>
                        </svg>
                    </div>
                    <div class="info-content">
                        <div class="info-label">Località</div>
                        <div class="info-value"><?php echo htmlspecialchars($evento['luogo']); ?></div>
                    </div>
                </div>
                
                <div class="info-item">
                    <div class="info-icon">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
                            <path d="M7 7V1.414a1 1 0 0 1 2 0V2h5a1 1 0 0 1 .8.4l.975 1.3a.5.5 0 0 1 0 .6L14.8 5.6a1 1 0 0 1-.8.4H9v10H7v-5H2a1 1 0 0 1-.8-.4L.225 9.3a.5.5 0 0 1 0-.6L1.2 7.4A1 1 0 0 1 2 7h5zm1 3V8H2l-.75 1L2 10h6zm0-5h6l.75-1L14 3H8v2z"/>
                        </svg>
                    </div>
                    <div class="info-content">
                        <div class="info-label">Tipo</div>
                        <div class="info-value"><?php echo ucfirst(htmlspecialchars($evento['tipo'])); ?></div>
                    </div>
                </div>
                
                <div class="info-item">
                    <div class="info-icon">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
                            <path d="M8 8a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm2-3a2 2 0 1 1-4 0 2 2 0 0 1 4 0zm4 8c0 1-1 1-1 1H3s-1 0-1-1 1-4 6-4 6 3 6 4zm-1-.004c-.001-.246-.154-.986-.832-1.664C11.516 10.68 10.289 10 8 10c-2.29 0-3.516.68-4.168 1.332-.678.678-.83 1.418-.832 1.664h10z"/>
                        </svg>
                    </div>
                    <div class="info-content">
                        <div class="info-label">Categorie</div>
                        <div class="info-value"><?php echo implode(', ', $evento['categorie']); ?></div>
                    </div>
                </div>
            </div>
            
            <div class="action-buttons">
                <a href="gestione_gruppi.php?evento=<?php echo $evento_id; ?>" class="session-btn">
                    Gestione Gruppi
                </a>
            </div>
        </div>
        
        <h2 class="page-title" style="font-size: 1.5rem; margin-top: 2rem;">Sessioni Disponibili</h2>
        
        <div class="session-grid">
            <div class="session-card">
                <div class="session-header prove-libere">
                    <h3>Prove Libere</h3>
                </div>
                <div class="session-timer">🚥</div>
                <div class="session-body">
                    <div>
                        <div class="session-title">Sessione di Prova</div>
                        <div class="session-time"><?php echo $evento['ora_prove_libere'] ?? 'Orario non specificato'; ?></div>
                    </div>
                    
                    <div class="session-stats">
                        <div class="stat">
                            <div class="stat-value">15</div>
                            <div class="stat-label">Minuti</div>
                        </div>
                        <div class="stat">
                            <div class="stat-value">40</div>
                            <div class="stat-label">Piloti</div>
                        </div>
                    </div>
                    
                    <a href="cronometraggio_manuale.php?evento=<?php echo $evento_id; ?>&sessione=prove_libere" class="session-btn">
                        Avvia Cronometraggio
                    </a>
                </div>
            </div>
            
            <div class="session-card">
                <div class="session-header qualifiche">
                    <h3>Qualifiche</h3>
                </div>
                <div class="session-timer">🎯</div>
                <div class="session-body">
                    <div>
                        <div class="session-title">Sessione Cronometrata</div>
                        <div class="session-time"><?php echo $evento['ora_qualifiche'] ?? 'Orario non specificato'; ?></div>
                        <div class="session-stats">
                        <div class="stat">
                            <div class="stat-value">15</div>
                            <div class="stat-label">Minuti</div>
                        </div>
                        <div class="stat">
                            <div class="stat-value">40</div>
                            <div class="stat-label">Piloti</div>
                        </div>
                    </div>
                    
                    <a href="cronometraggio_manuale.php?evento=<?php echo $evento_id; ?>&sessione=qualifiche" class="session-btn">
                        Avvia Cronometraggio
                    </a>
                </div>
            </div>
            
            <div class="session-card">
                <div class="session-header manche-1">
                    <h3>Manche 1</h3>
                </div>
                <div class="session-timer">🏆</div>
                <div class="session-body">
                    <div>
                        <div class="session-title">Prima Gara</div>
                        <div class="session-time"><?php echo $evento['ora_gare'] ?? 'Orario non specificato'; ?></div>
                    </div>
                    
                    <div class="session-stats">
                        <div class="stat">
                            <div class="stat-value">20</div>
                            <div class="stat-label">Minuti</div>
                        </div>
                        <div class="stat">
                            <div class="stat-value">2</div>
                            <div class="stat-label">Giri</div>
                        </div>
                    </div>
                    
                    <a href="cronometraggio_manuale.php?evento=<?php echo $evento_id; ?>&sessione=manche_1" class="session-btn">
                        Avvia Cronometraggio
                    </a>
                </div>
            </div>
            
            <div class="session-card">
                <div class="session-header manche-2">
                    <h3>Manche 2</h3>
                </div>
                <div class="session-timer">🏁</div>
                <div class="session-body">
                    <div>
                        <div class="session-title">Seconda Gara</div>
                        <div class="session-time">15:30</div>
                    </div>
                    
                    <div class="session-stats">
                        <div class="stat">
                            <div class="stat-value">20</div>
                            <div class="stat-label">Minuti</div>
                        </div>
                        <div class="stat">
                            <div class="stat-value">2</div>
                            <div class="stat-label">Giri</div>
                        </div>
                    </div>
                    
                    <a href="cronometraggio_manuale.php?evento=<?php echo $evento_id; ?>&sessione=manche_2" class="session-btn">
                        Avvia Cronometraggio
                    </a>
                </div>
            </div>
        </div>
    </div>
    
    <footer class="footer">
        <p>&copy; <?php echo date('Y'); ?> MX Pro - Sistema di Cronometraggio Professionale per Motocross</p>
    </footer>
    
    <script>
        // Animazione scroll fluido per link interni
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                
                document.querySelector(this.getAttribute('href')).scrollIntoView({
                    behavior: 'smooth'
                });
            });
        });
    </script>
</body>
</html>