<?php
session_start();
if (!isset($_SESSION['user'])) {
    header('Location: login.php');
    exit();
}

// Piste complete aggiornate
$piste_lombardia = [
    // Bergamo
    ['nome' => 'Ponte Nossa', 'citta' => 'Ponte Nossa (BG)', 'categoria' => 2, 'lunghezza' => 1630, 'omologazione' => 'FMI', 'terreno' => 'duro con roccia', 'moto_club' => 'Ponte Nossa'],
    ['nome' => 'Tribulina - MC Ponte Nossa', 'citta' => 'Tribulina (BG)', 'categoria' => 2, 'lunghezza' => 1630, 'omologazione' => 'FMI', 'terreno' => 'terra', 'moto_club' => 'Ponte Nossa'],
    
    // Brescia
    ['nome' => 'Covo - MXE.45', 'citta' => 'Covo (BS)', 'categoria' => 2, 'lunghezza' => 1560, 'omologazione' => 'FMI', 'terreno' => 'terra', 'moto_club' => 'MXE.45'],
    ['nome' => 'Darfo Boario', 'citta' => 'Darfo Boario Terme (BS)', 'categoria' => 3, 'lunghezza' => 1200, 'omologazione' => 'FMI/UISP', 'terreno' => 'sabbia/terra', 'moto_club' => 'Darfo'],
    ['nome' => 'Galaello', 'citta' => 'Preseglie (BS)', 'categoria' => 1, 'lunghezza' => 1750, 'omologazione' => 'FMI/UISP', 'terreno' => 'duro', 'moto_club' => 'Gruppo Sportivo Galaello'],
    ['nome' => 'Gambara', 'citta' => 'Seriola di Asola (BS)', 'categoria' => 3, 'lunghezza' => 1900, 'omologazione' => 'UISP/AICS', 'terreno' => 'sabbia/terra', 'moto_club' => 'Gambara'],
    ['nome' => 'Pudiano - Barbariga', 'citta' => 'Barbariga (BS)', 'categoria' => 4, 'lunghezza' => 1500, 'omologazione' => 'UISP', 'terreno' => 'terra sabbia', 'moto_club' => 'ASD Motocross La Boschina'],
    ['nome' => 'Rezzato', 'citta' => 'Rezzato (BS)', 'categoria' => 2, 'lunghezza' => 1400, 'omologazione' => 'FMI/UISP', 'terreno' => 'duro', 'moto_club' => 'UISP Brescia'],
    ['nome' => 'Serle', 'citta' => 'Serle (BS)', 'categoria' => 3, 'lunghezza' => 1500, 'omologazione' => 'FMI/UISP', 'terreno' => 'duro', 'moto_club' => 'Le Valli Serle'],
    ['nome' => 'Verolanuova', 'citta' => 'Verolanuova (BS)', 'categoria' => 2, 'lunghezza' => 1600, 'omologazione' => 'FMI/UISP', 'terreno' => 'terra', 'moto_club' => 'Verolese'],
    ['nome' => 'Vestone', 'citta' => 'Vestone (BS)', 'categoria' => 2, 'lunghezza' => 3300, 'omologazione' => 'FMI/UISP', 'terreno' => 'terra sabbia', 'moto_club' => 'Vestone'],
    
    // Cremona
    ['nome' => 'Cremona', 'citta' => 'Cremona (CR)', 'categoria' => 2, 'lunghezza' => 1800, 'omologazione' => 'FMI/UISP/CSEN', 'terreno' => 'sabbia', 'moto_club' => 'Cremona'],
    ['nome' => 'Credera Rubbiano', 'citta' => 'Credera Rubbiano (CR)', 'categoria' => 2, 'lunghezza' => 1730, 'omologazione' => 'FMI/ASI/UISP/AICS', 'terreno' => 'sabbia', 'moto_club' => 'Zeta MX Park'],
    ['nome' => 'Crotta d\'Adda', 'citta' => 'Crotta d\'Adda (CR)', 'categoria' => 3, 'lunghezza' => 1700, 'omologazione' => 'FMI/UISP', 'terreno' => 'sabbia', 'moto_club' => 'Gamma'],
    
    // Lodi
    ['nome' => 'Lodi - Emilio Marchi', 'citta' => 'Lodi (LO)', 'categoria' => 3, 'lunghezza' => 1650, 'omologazione' => 'FMI/UISP/ASI', 'terreno' => 'medio duro', 'moto_club' => 'Lodi'],
    
    // Mantova
    ['nome' => 'Canneto', 'citta' => 'Canneto (MN)', 'categoria' => 5, 'lunghezza' => 1200, 'omologazione' => 'FMI/UISP/CSEN/AICS', 'terreno' => 'terra-sabbia', 'moto_club' => 'Canneto'],
    ['nome' => 'Castiglione Stiviere', 'citta' => 'Castiglione Stiviere (MN)', 'categoria' => 2, 'lunghezza' => 2000, 'omologazione' => 'FMI/UISP', 'terreno' => 'duro con sassi', 'moto_club' => 'Castiglione'],
    ['nome' => 'Mantova', 'citta' => 'Mantova (MN)', 'categoria' => 1, 'lunghezza' => 1950, 'omologazione' => 'FMI/UISP', 'terreno' => 'sabbia/terra', 'moto_club' => 'Mantovano T.Nuvolari'],
    ['nome' => 'MX Park Medole', 'citta' => 'Medole (MN)', 'categoria' => 3, 'lunghezza' => 1950, 'omologazione' => 'UISP/FMI/CSEN', 'terreno' => 'terra-sabbia', 'moto_club' => 'ASD Motoclub MX Park Medole'],
    ['nome' => 'Rivarolo Mantovano', 'citta' => 'Rivarolo Mantovano (MN)', 'categoria' => 3, 'lunghezza' => 1600, 'omologazione' => 'FMI/UISP/CSEN', 'terreno' => 'sabbia/terra', 'moto_club' => 'Rivarolese'],
    ['nome' => 'Viadana - Ivo Mortini', 'citta' => 'Viadana (MN)', 'categoria' => 2, 'lunghezza' => 1550, 'omologazione' => 'UISP', 'terreno' => 'terra', 'moto_club' => 'Viadana - Asd Motocross Viadana'],
    
    // Milano
    ['nome' => 'Ceriano Laghetto il Vallone', 'citta' => 'Ceriano Laghetto (MI)', 'categoria' => 1, 'lunghezza' => 1860, 'omologazione' => 'FMI/UISP/ASI', 'terreno' => 'terra', 'moto_club' => 'Ceriano'],
    
    // Pavia
    ['nome' => 'Dorno', 'citta' => 'Dorno (PV)', 'categoria' => 3, 'lunghezza' => 1700, 'omologazione' => 'FMI/UISP/ASI', 'terreno' => 'sabbia/terra', 'moto_club' => 'Dorno'],
    ['nome' => 'Ottobiano Motorsport', 'citta' => 'Ottobiano (PV)', 'categoria' => 1, 'lunghezza' => 1650, 'omologazione' => 'FMI/ASI/ASC', 'terreno' => 'sabbia', 'moto_club' => '8biano'],
    ['nome' => 'Max land MX Raceway', 'citta' => 'Chignolo Po (PV)', 'categoria' => 1, 'lunghezza' => 1800, 'omologazione' => 'UISP/ASI/AICS', 'terreno' => 'terra sabbia', 'moto_club' => 'Max Land MX'],
    
    // Sondrio
    ['nome' => 'Tovo', 'citta' => 'Tovo (SO)', 'categoria' => 4, 'lunghezza' => 1420, 'omologazione' => 'FMI/ASI', 'terreno' => 'terra-sabbia', 'moto_club' => 'Tovo'],
    
    // Varese
    ['nome' => 'Gorla Minore', 'citta' => 'Gorla Minore (VA)', 'categoria' => 4, 'lunghezza' => 1200, 'omologazione' => 'FMI/ASI', 'terreno' => 'terra', 'moto_club' => 'Gorla'],
    ['nome' => 'Motocross Malpensa', 'citta' => 'Gallarate (VA)', 'categoria' => 1, 'lunghezza' => 1635, 'omologazione' => 'FMI 1° livello', 'terreno' => 'duro argilloso', 'moto_club' => 'MotoClub M.V. Gallarate'],
];

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    require_once '../config/database.php';
    $db = new Database();
    $data = $db->readData();
    
    $new_id = count($data['eventi']) + 1;
    
    $evento = [
        'id' => $new_id,
        'nome_evento' => $_POST['nome_evento'],
        'tipo' => $_POST['tipo_evento'],
        'data_evento' => $_POST['data_evento'],
        'luogo' => $_POST['luogo'],
        'categorie' => $_POST['categorie'],
        'quota_prima' => $_POST['quota_prima'],
        'ora_prove_libere' => $_POST['ora_prove_libere'],
        'ora_qualifiche' => $_POST['ora_qualifiche'],
        'ora_gare' => $_POST['ora_gare'],
        // Staff medico
        'staff_medico' => [
            'direttore_medico_gara' => $_POST['direttore_medico_gara'],
            'medici_gara' => $_POST['medici_gara'],
            'rianimatore' => $_POST['rianimatore'],
            'traumatologo' => $_POST['traumatologo'],
            'ambulanza' => $_POST['ambulanza']
        ],
        // Staff tecnico
        'staff_tecnico' => [
            'direttore_gara' => $_POST['direttore_gara'],
            'vice_direttore' => $_POST['vice_direttore'],
            'commissari' => $_POST['commissari'],
            'sbandieratori' => $_POST['sbandieratori'],
            'giudice_partenza' => $_POST['giudice_partenza'],
            'cronometristi' => $_POST['cronometristi'],
            'addetti_percorso' => $_POST['addetti_percorso']
        ],
        // Documenti
        'documenti' => [
            'autorizzazione_comunale' => $_POST['autorizzazione_comunale'],
            'rc_gare' => $_POST['rc_gare'],
            'nulla_osta' => $_POST['nulla_osta'],
            'servizio_cronometraggio' => $_POST['servizio_cronometraggio']
        ]
    ];
    
    $data['eventi'][] = $evento;
    $db->saveData($data);
    
    header('Location: ../index.php');
    exit();
}
?>
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gestione Eventi FMI Lombardia 2025</title>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        /* [Previous CSS remains the same] */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        :root {
            --bg-primary: #0A0B0E;
            --bg-card: #1A1C24;
            --bg-input: #252831;
            --accent: #3B82F6;
            --accent-hover: #2563EB;
            --text-primary: #FFFFFF;
            --text-secondary: #94A3B8;
            --border-color: #343A46;
            --glass: rgba(255, 255, 255, 0.05);
            --gradient: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
            --shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        }
        
        body {
            font-family: 'Outfit', sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 1rem;
            line-height: 1.5;
            background-image: radial-gradient(at 85% 0%, rgb(59, 130, 246, 0.1), transparent 40%),
                            radial-gradient(at 0% 0%, rgb(37, 99, 235, 0.1), transparent 40%);
        }
        
        .container {
            max-width: 1600px;
            margin: 0 auto;
        }
        
        .glass-card {
            background: var(--bg-card);
            backdrop-filter: blur(24px);
            -webkit-backdrop-filter: blur(24px);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            transition: all 0.3s ease;
        }
        
        .glass-card:hover {
            border-color: var(--accent);
            transform: translateY(-2px);
            box-shadow: var(--shadow);
        }
        
        h2 {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.5rem;
            margin-bottom: 1.5rem;
            color: var(--text-primary);
        }
        
        .form-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1rem;
        }
        
        .form-group {
            margin-bottom: 1.5rem;
        }
        
        label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 500;
            color: var(--text-primary);
        }
        
        input, select {
            width: 100%;
            padding: 0.75rem 1rem;
            background: var(--bg-input);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            color: var(--text-primary);
            font-size: 0.9375rem;
            transition: all 0.3s ease;
        }
        
        input:focus, select:focus {
            outline: none;
            border-color: var(--accent);
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
        }
        
        .regulation-info {
            background: var(--glass);
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1.5rem;
            font-size: 0.875rem;
            color: var(--text-secondary);
        }
        
        .regulation-info h4 {
            color: var(--text-primary);
            margin-bottom: 0.5rem;
        }
        
        .submit-btn {
            background: var(--gradient);
            color: white;
            border: none;
            padding: 1rem 2rem;
            border-radius: 12px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .submit-btn:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow);
        }
        
        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .glass-card {
            animation: slideUp 0.5s ease-out forwards;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 style="text-align: center; margin-bottom: 2rem; font-family: 'Space Grotesk', sans-serif; font-size: 2.5rem;">
            Gestione Eventi FMI Lombardia 2025
        </h1>
        
        <form method="POST">
            <!-- Informazioni Base -->
            <div class="glass-card">
                <h2>Informazioni Base</h2>
                <div class="form-grid">
                    <div class="form-group">
                        <label>Nome Evento</label>
                        <input type="text" name="nome_evento" required>
                    </div>
                    <div class="form-group">
                        <label>Tipo Evento</label>
                        <select name="tipo_evento" required>
                            <option value="">Seleziona</option>
                            <option value="campionato">Campionato</option>
                            <option value="trofeo">Trofeo</option>
                            <option value="sociale">Gara Sociale</option>
                            <option value="allenamento">Allenamento</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Data</label>
                        <input type="date" name="data_evento" required>
                    </div>
                    <div class="form-group">
                        <label>Pista</label>
                        <select name="luogo" required>
                            <option value="">Seleziona pista</option>
                            <?php foreach ($piste_lombardia as $pista): ?>
                                <option value="<?php echo $pista['nome']; ?>">
                                    <?php echo $pista['nome']; ?> - <?php echo $pista['lunghezza']; ?>m (Cat. <?php echo $pista['categoria']; ?>)
                                </option>
                            <?php endforeach; ?>
                        </select>
                    </div>
                </div>
            </div>
            
            <!-- Staff Medico -->
            <div class="glass-card">
                <h2>Staff Medico</h2>
                <div class="regulation-info">
                    <h4>Requisiti Regolamento FMI</h4>
                    <p>Obbligatori: 2 medici (traumatologo + rianimatore)</p>
                    <p>Servizio specializzato: traumatologo/rianimatore presente dalla prima prova alla classifica</p>
                    <p>Costi: €350-650 per giornata secondo servizi</p>
                </div>
                <div class="form-grid">
                    <div class="form-group">
                        <label>Direttore Medico di Gara</label>
                        <input type="text" name="direttore_medico_gara" required>
                    </div>
                    <div class="form-group">
                        <label>Numero Medici Gara</label>
                        <input type="number" name="medici_gara" value="2" min="2" required>
                    </div>
                    <div class="form-group">
                        <label>Rianimatore</label>
                        <input type="text" name="rianimatore" required>
                    </div>
                    <div class="form-group">
                        <label>Traumatologo</label>
                        <input type="text" name="traumatologo" required>
                    </div>
                    <div class="form-group">
                        <label>Servizio Ambulanza</label>
                        <select name="ambulanza" required>
                            <option value="">Seleziona</option>
                            <option value="presente">Presente in pista</option>
                            <option value="reperibile">Reperibile</option>
                        </select>
                    </div>
                </div>
            </div>
            
            <!-- Staff Tecnico -->
            <div class="glass-card">
                <h2>Staff Tecnico e Commissari</h2>
                <div class="regulation-info">
                    <h4>Ufficiali di Gara Obbligatori</h4>
                    <p>Direttore di Gara: designato dal Co.Re Lombardia</p>
                    <p>Commissari: abbigliamento protettivo obbligatorio (casco bianco CE)</p>
                    <p>Addetti al percorso: con tessera FMI valida</p>
                </div>
                <div class="form-grid">
                    <div class="form-group">
                        <label>Direttore di Gara</label>
                        <input type="text" name="direttore_gara" required>
                    </div>
                    <div class="form-group">
                        <label>Vice Direttore</label>
                        <input type="text" name="vice_direttore">
                    </div>
                    <div class="form-group">
                        <label>Numero Commissari</label>
                        <input type="number" name="commissari" min="4" value="6" required>
                    </div>
                    <div class="form-group">
                        <label>Sbandieratori</label>
                        <input type="number" name="sbandieratori" min="2" value="4" required>
                    </div>
                    <div class="form-group">
                        <label>Giudice alla Partenza</label>
                        <input type="text" name="giudice_partenza" required>
                    </div>
                    <div class="form-group">
                        <label>Cronometristi</label>
                        <input type="text" name="cronometristi" value="MGM Timing" required>
                    </div>
                    <div class="form-group">
                        <label>Addetti al Percorso</label>
                        <input type="number" name="addetti_percorso" min="8" value="10" required>
                    </div>
                </div>
            </div>
            
            <!-- Documenti -->
            <div class="glass-card">
                <h2>Documenti e Autorizzazioni</h2>
                <div class="regulation-info">
                    <h4>Documenti Obbligatori per Regolamento</h4>
                    <p>• Autorizzazione amministrazione comunale: €45</p>
                    <p>• RC Gare obbligatoria</p>
                    <p>• Nulla osta regolamento particolare (Co.Re)</p>
                    <p>• Servizio cronometraggio (MGM Timing)</p>
                </div>
                <div class="form-grid">
                    <div class="form-group">
                        <label>Autorizzazione Comunale</label>
                        <select name="autorizzazione_comunale" required>
                            <option value="">Stato</option>
                            <option value="richiesta">Richiesta in corso</option>
                            <option value="ottenuta">Ottenuta</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Assicurazione RC Gare</label>
                        <select name="rc_gare" required>
                            <option value="">Stato</option>
                            <option value="attivazione">In attivazione</option>
                            <option value="attiva">Attiva</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Nulla Osta Co.Re</label>
                        <select name="nulla_osta" required>
                            <option value="">Stato</option>
                            <option value="richiesto">Richiesto</option>
                            <option value="ottenuto">Ottenuto</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Servizio Cronometraggio</label>
                        <select name="servizio_cronometraggio" required>
                            <option value="">Seleziona</option>
                            <option value="mgm_timing">MGM Timing</option>
                            <option value="altro">Altro servizio approvato</option>
                        </select>
                    </div>
                </div>
            </div>
            
            <!-- Categorie -->
            <div class="glass-card">
                <h2>Categorie</h2>
                <div class="form-group">
                    <label>Seleziona Categorie</label>
                    <select name="categorie[]" multiple size="10" required>
                        <option value="MX1">MX1</option>
                        <option value="MX2">MX2</option>
                        <option value="125">125</option>
                        <option value="Femminile">Femminile</option>
                        <option value="Master">Master</option>
                        <option value="Veteran">Veteran</option>
                        <option value="Superveteran">Superveteran</option>
                    </select>
                </div>
            </div>
            
            <button type="submit" class="submit-btn">
                Crea Evento
            </button>
        </form>
    </div>
</body>
</html>