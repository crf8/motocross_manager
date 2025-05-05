<?php
session_start();

// Se c'è una richiesta di login
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    $username = $_POST['username'];
    $password = $_POST['password'];
    
    // Controllo semplice per ora
    if ($username == 'admin' && $password == 'motocross123') {
        $_SESSION['user'] = 'admin';
        header('Location: ../index.php');
        exit();
    }
}
?>

<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <title>Login - Motocross Manager</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #0a0a0a;
            color: white;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .login-box {
            background: #1a1a1a;
            padding: 40px;
            border-radius: 10px;
            text-align: center;
        }
        input {
            margin: 10px;
            padding: 10px;
            width: 200px;
            font-size: 16px;
        }
        button {
            background: #FF0000;
            color: white;
            border: none;
            padding: 10px 20px;
            margin-top: 20px;
            cursor: pointer;
            font-size: 16px;
        }
    </style>
</head>
<body>
    <div class="login-box">
        <h1>🏁 Motocross Manager</h1>
        <form method="POST">
            <div>
                <input type="text" name="username" placeholder="Username" required>
            </div>
            <div>
                <input type="password" name="password" placeholder="Password" required>
            </div>
            <button type="submit">Entra</button>
        </form>
    </div>
</body>
</html>