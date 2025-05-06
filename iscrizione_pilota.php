<?php
session_start();
if (!isset($_SESSION['user'])) {
    header('Location: login.php');
    exit();
}

// Controlliamo se il form è stato inviato
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    // Usiamo la nuova classe MongoCompatDB
    require_once '../config/MongoCompatDB.php';
    $db = new MongoCompatDB();
    
    // Raccogliamo i dati dal form
    $nuovo_pilota = [
        'nome' => $_POST['nome'] ?? '',
        'cognome' => $_POST['cognome'] ?? '',
        'data_nascita' => $_POST['data_nascita'] ?? '',
        'numero_gara' => $_POST['numero_gara'] ?? '',
        'categoria' => $_POST['categoria'] ?? '',
        'email' => $_POST['email'] ?? '',
        'telefono' => $_POST['telefono'] ?? '',
        'moto_club' => $_POST['moto_club'] ?? '',
        'licenza_fmi' => $_POST['licenza_fmi'] ?? '',
        'classe_eta' => $_POST['classe_eta'] ?? ''
    ];
    
    // Inseriamo il nuovo pilota nel database
    $pilota_id = $db->insertDocument('piloti', $nuovo_pilota);
    
    // Redirect alla pagina di completamento
    header('Location: iscrizione_completata.php?id=' . $pilota_id);
    exit();
}
?>

<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Iscrizione Pilota - FMI Lombardia 2025</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Montserrat:wght@700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --fmi-blue: #0066cc;
            --fmi-red: #e30613;
            --fmi-green: #00a651;
            --bg-primary: #f5e6d3; /* Marrone chiaro */
            --bg-card: #f9f3ec; /* Marrone molto chiaro */
            --bg-brown: #8b5a2b; /* Marrone scuro */
            --text-primary: #2c1810; /* Marrone scurissimo */
            --text-secondary: #5c4033; /* Marrone medio */
            --border-light: #d4bfa3; /* Marrone chiaro chiaro */
            --border-medium: #b59578; /* Marrone medio medio */
            --success: #16a34a;
            --warning: #ea580c;
            --info: #0891b2;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
            min-height: 100vh;
        }

        .header {
            background: linear-gradient(135deg, var(--bg-brown) 0%, var(--fmi-red) 50%, var(--bg-brown) 100%);
            padding: 2rem 1rem;
            text-align: center;
            color: white;
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
            background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='40' height='40' viewBox='0 0 40 40'%3E%3Cg fill-opacity='0.1'%3E%3Cpolygon fill='%23fff' points='0 40 40 0 40 40'/%3E%3C/g%3E%3C/svg%3E");
            background-size: cover;
        }

        .header-content {
            position: relative;
            z-index: 1;
            max-width: 1200px;
            margin: 0 auto;
        }

        .logo-container {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 1rem;
            margin-bottom: 1rem;
        }

        .logo {
            font-family: 'Montserrat', sans-serif;
            font-size: 3rem;
            font-weight: 800;
            letter-spacing: -1px;
        }

        .year-badge {
            background: rgba(255, 255, 255, 0.2);
            padding: 0.25rem 1rem;
            border-radius: 50px;
            font-size: 1rem;
            font-weight: 600;
        }

        .subtitle {
            font-size: 1.25rem;
            opacity: 0.9;
            margin-bottom: 2rem;
        }

        .main-container {
            max-width: 1000px;
            margin: -4rem auto 4rem;
            padding: 0 1rem;
            position: relative;
            z-index: 2;
        }

        .form-card {
            background: var(--bg-card);
            border-radius: 16px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            padding: 2rem;
            margin-bottom: 2rem;
        }

        .section-header {
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 1.5rem;
        }

        .section-icon {
            width: 48px;
            height: 48px;
            border-radius: 12px;
            background: var(--bg-brown);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
        }

        .section-title {
            font-family: 'Montserrat', sans-serif;
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--text-primary);
        }

        .form-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
        }

        .form-group {
            position: relative;
        }

        label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 500;
            color: var(--text-primary);
            font-size: 0.875rem;
        }

        input, select {
            width: 100%;
            padding: 0.75rem;
            border: 2px solid var(--border-light);
            border-radius: 8px;
            font-size: 1rem;
            transition: all 0.3s ease;
        }

        input:focus, select:focus {
            outline: none;
            border-color: var(--bg-brown);
            box-shadow: 0 0 0 3px rgba(139, 90, 43, 0.2);
        }

        .info-box {
            background: #f5eadf;
            border-left: 4px solid var(--bg-brown);
            padding: 1rem;
            margin: 1.5rem 0;
            border-radius: 0 8px 8px 0;
        }

        .info-box h4 {
            color: var(--bg-brown);
            margin-bottom: 0.5rem;
            font-weight: 600;
        }

        .info-box ul {
            list-style-position: inside;
            color: var(--text-secondary);
        }

        .category-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }

        .category-card {
            background: var(--bg-primary);
            border: 2px solid var(--border-light);
            border-radius: 8px;
            padding: 1rem;
            text-align: center;
            transition: all 0.3s ease;
            cursor: pointer;
        }

        .category-card:hover {
            border-color: var(--bg-brown);
            transform: translateY(-2px);
        }

        .category-card.selected {
            border-color: var(--fmi-blue);
            background: #f0f7ff;
        }

        .submit-button {
            width: 100%;
            padding: 1rem;
            background: linear-gradient(135deg, var(--bg-brown) 0%, var(--fmi-red) 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 1.125rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-top: 2rem;
        }

        .submit-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px -5px rgba(0, 0, 0, 0.25);
        }

        .progress-indicator {
            display: flex;
            justify-content: center;
            gap: 0.5rem;
            margin-bottom: 2rem;
        }

        .progress-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--border-medium);
            transition: all 0.3s ease;
        }

        .progress-dot.active {
            background: var(--bg-brown);
            transform: scale(1.5);
        }

        @media (max-width: 768px) {
            .header {
                padding: 1.5rem 1rem;
            }

            .logo {
                font-size: 2rem;
            }

            .main-container {
                margin-top: -2rem;
            }

            .form-grid {
                grid-template-columns: 1fr;
            }

            .section-header {
                flex-direction: column;
                text-align: center;
            }
        }
    </style>
</head>
<body>
    <header class="header">
        <div class="header-content">
            <div class="logo-container">
                <span class="logo">FMI LOMBARDIA</span>
                <span class="year-badge">2025</span>
            </div>
            <p class="subtitle">Iscrizione al Campionato Regionale Motocross</p>
        </div>
    </header>

    <main class="main-container">
        <div class="progress-indicator">
            <div class="progress-dot active"></div>
            <div class="progress-dot"></div>
            <div class="progress-dot"></div>
            <div class="progress-dot"></div>
            <div class="progress-dot"></div>
        </div>

        <form method="POST">
            <!-- Dati Personali -->
            <div class="form-card">
                <div class="section-header">
                    <div class="section-icon">👤</div>
                    <h2 class="section-title">Dati Personali</h2>
                </div>
                
                <div class="form-grid">
                    <div class="form-group">
                        <label>Nome *</label>
                        <input type="text" name="nome" required>
                    </div>
                    <div class="form-group">
                        <label>Cognome *</label>
                        <input type="text" name="cognome" required>
                    </div>
                    <div class="form-group">
                        <label>Data di Nascita *</label>
                        <input type="date" name="data_nascita" required>
                    </div>
                    <div class="form-group">
                        <label>Luogo di Nascita *</label>
                        <input type="text" name="luogo_nascita" required>
                    </div>
                    <div class="form-group">
                        <label>Codice Fiscale *</label>
                        <input type="text" name="codice_fiscale" pattern="[A-Za-z]{6}[0-9]{2}[A-Za-z][0-9]{2}[A-Za-z][0-9]{3}[A-Za-z]" required>
                    </div>
                </div>
            </div>

            <!-- Licenza FMI -->
            <div class="form-card">
                <div class="section-header">
                    <div class="section-icon">🆔</div>
                    <h2 class="section-title">Licenza FMI</h2>
                </div>
                
                <div class="form-grid">
                    <div class="form-group">
                        <label>Tipo Licenza *</label>
                        <select name="licenza_fmi" required>
                            <option value="">Seleziona tipo licenza</option>
                            <option value="elite">Elite</option>
                            <option value="fuoristrada">Fuoristrada</option>
                            <option value="one_event">One Event</option>
                            <option value="training">Training</option>
                            <option value="noleggio">Noleggio</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Numero Tessera</label>
                        <input type="text" name="numero_tessera">
                    </div>
                    <div class="form-group">
                        <label>Moto Club *</label>
                        <input type="text" name="moto_club" required>
                    </div>
                </div>

                <div class="info-box">
                    <h4>Informazioni Licenze</h4>
                    <ul>
                        <li>Elite: €375 annuale, per MX1/MX2 internazionali</li>
                        <li>Fuoristrada: €255 annuale, per campionati nazionali</li>
                        <li>One Event: €70 giorno, licenza temporanea</li>
                        <li>Training: solo allenamenti privati</li>
                    </ul>
                </div>
            </div>

            <!-- Numero di Gara -->
            <div class="form-card">
                <div class="section-header">
                    <div class="section-icon">#️⃣</div>
                    <h2 class="section-title">Numero di Gara</h2>
                </div>
                
                <div class="form-grid">
                    <div class="form-group">
                        <label>Numero Desiderato *</label>
                        <input type="number" name="numero_gara" min="1" max="999" required>
                    </div>
                    <div class="form-group">
                        <label>Posizione Preferita</label>
                        <select name="posizione_numero">
                            <option value="">Indifferente</option>
                            <option value="posteriore">Posteriore (default)</option>
                            <option value="laterale">Laterale</option>
                        </select>
                    </div>
                </div>

                <div class="info-box">
                    <h4>Numeri Fissi 2025</h4>
                    <p>Richiedi il tuo numero fisso entro il 15/02/2025 (€20) su gestionenumeri.mgmtiming.it</p>
                </div>
            </div>

            <!-- Categoria -->
            <div class="form-card">
                <div class="section-header">
                    <div class="section-icon">🏁</div>
                    <h2 class="section-title">Categoria di Gara</h2>
                </div>
                
                <div class="form-group">
                    <label>Seleziona la tua categoria *</label>
                    <select name="categoria" required>
                        <option value="">Seleziona categoria</option>
                        <option value="MX1">MX1 (250-450cc 4T)</option>
                        <option value="MX2">MX2 (125cc 2T, 250cc 4T)</option>
                        <option value="125">125cc Junior</option>
                        <option value="Femminile">Femminile</option>
                        <option value="Master">Master (40+ anni)</option>
                        <option value="Veteran">Veteran (45+ anni)</option>
                        <option value="Superveteran">Superveteran (50+ anni)</option>
                    </select>
                </div>

                <div class="form-group">
                    <label>Classe Età</label>
                    <select name="classe_eta">
                        <option value="">Seleziona classe</option>
                        <option value="Junior">Junior (fino a 18 anni)</option>
                        <option value="Senior">Senior (19-39 anni)</option>
                        <option value="Master">Master (40+ anni)</option>
                        <option value="Veteran">Veteran (45+ anni)</option>
                        <option value="Superveteran">Superveteran (50+ anni)</option>
                    </select>
                </div>
            </div>

            <!-- Contatti -->
            <div class="form-card">
                <div class="section-header">
                    <div class="section-icon">📞</div>
                    <h2 class="section-title">Informazioni di Contatto</h2>
                </div>
                
                <div class="form-grid">
                    <div class="form-group">
                        <label>Email *</label>
                        <input type="email" name="email" required>
                    </div>
                    <div class="form-group">
                        <label>Telefono *</label>
                        <input type="tel" name="telefono" required>
                    </div>
                    <div class="form-group">
                        <label>Indirizzo Residenza *</label>
                        <input type="text" name="indirizzo" required>
                    </div>
                    <div class="form-group">
                        <label>Cap *</label>
                        <input type="text" name="cap" pattern="[0-9]{5}" required>
                    </div>
                    <div class="form-group">
                        <label>Provincia *</label>
                        <input type="text" name="provincia" required>
                    </div>
                </div>
            </div>

            <!-- Privacy e Consensi -->
            <div class="form-card">
                <div class="section-header">
                    <div class="section-icon">⚖️</div>
                    <h2 class="section-title">Privacy e Consensi</h2>
                </div>
                
                <div class="form-group">
                    <label>
                        <input type="checkbox" name="privacy_obbligatorio" required>
                        Accetto il trattamento dei dati personali (Obbligatorio) *
                    </label>
                </div>
                
                <div class="form-group">
                    <label>
                        <input type="checkbox" name="privacy_marketing">
                        Accetto comunicazioni promozionali (Facoltativo)
                    </label>
                </div>

                <div class="info-box">
                    <h4>Informazioni Privacy</h4>
                    <p>I dati saranno trattati secondo la normativa GDPR. Informativa completa disponibile sul sito FMI Lombardia.</p>
                </div>
            </div>

            <button type="submit" class="submit-button">
                Completa Iscrizione
            </button>
        </form>
    </main>

    <script>
        // Gestione progress indicator
        function updateProgress() {
            const sections = document.querySelectorAll('.form-card');
            const dots = document.querySelectorAll('.progress-dot');
            
            let currentSection = 0;
            
            sections.forEach((section, index) => {
                const rect = section.getBoundingClientRect();
                if (rect.top >= 0 && rect.top <= window.innerHeight / 2) {
                    currentSection = index;
                }
            });
            
            dots.forEach((dot, index) => {
                if (index === currentSection) {
                    dot.classList.add('active');
                } else {
                    dot.classList.remove('active');
                }
            });
        }

        // Aggiorna il progresso durante lo scroll
        window.addEventListener('scroll', updateProgress);
        
        // Validazione form
        document.querySelector('form').addEventListener('submit', function(e) {
            // Verifica che tutti i campi obbligatori siano compilati
            const requiredFields = document.querySelectorAll('[required]');
            let valid = true;
            
            requiredFields.forEach(field => {
                if (!field.value) {
                    valid = false;
                    field.style.borderColor = '#e30613';
                } else {
                    field.style.borderColor = '';
                }
            });
            
            if (!valid) {
                e.preventDefault();
                alert('Per favore, compila tutti i campi obbligatori.');
            }
        });
    </script>
</body>
</html>