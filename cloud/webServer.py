from flask import Flask, request, redirect

import threading
import mqttManager # <- Import corretto!

app = Flask(__name__)

# Avvia il manager MQTT (decommenta se è necessario avviarlo all'accensione del server)
# mqttManager.start()

@app.route("/flippermaxime", methods=["GET", "POST"])
def flippermaxime():
    if request.method == "POST":
        # 1. Recupero i dati dal form
        device_name = request.form.get("name")
        signal_type = request.form.get("type") # Sarà 'subGHz' o 'infrared'
        action = request.form.get("action")    # Sarà 'on' o 'off'

        # 2. Il topic e il nome file corrispondono (es. "subGHz/TV_Sala")
        topic = f"{signal_type}/{device_name}"
        file_name = topic 

        # 3. Invio il comando ad MQTT
        # (Assicurati che send_tag nel tuo mqttManager.py accetti questi parametri)
        if action == "on":
            mqttManager.send_tag(topic, "ON")
        elif action == "off":
            mqttManager.send_tag(topic, "OFF")

        # Ricarica la pagina dopo l'invio del comando
        return redirect("/flippermaxime")

    # Se la richiesta è GET, mostriamo un'interfaccia HTML di base senza bisogno di file esterni.
    # Sostituisci la vecchia variabile html_interface con questa:
    
    html_interface = """
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Flipper Zero Web Controller</title>
        <style>
            :root {
                --flipper-orange: #FF8C00;
                --bg-color: #121212;
                --card-bg: #1E1E1E;
                --text-color: #E0E0E0;
                --input-bg: #2C2C2C;
                --btn-on: #28a745;
                --btn-on-hover: #218838;
                --btn-off: #dc3545;
                --btn-off-hover: #c82333;
            }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: var(--bg-color);
                color: var(--text-color);
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            .card {
                background-color: var(--card-bg);
                padding: 40px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
                width: 100%;
                max-width: 400px;
                border-top: 5px solid var(--flipper-orange);
            }
            .header {
                text-align: center;
                margin-bottom: 30px;
            }
            .header h2 {
                margin: 0;
                color: var(--flipper-orange);
                font-size: 24px;
            }
            .header p {
                margin: 5px 0 0 0;
                font-size: 14px;
                color: #888;
            }
            .form-group {
                margin-bottom: 20px;
            }
            label {
                display: block;
                margin-bottom: 8px;
                font-weight: 600;
                font-size: 14px;
            }
            input[type="text"], select {
                width: 100%;
                padding: 12px;
                border: 1px solid #444;
                border-radius: 8px;
                background-color: var(--input-bg);
                color: white;
                font-size: 16px;
                box-sizing: border-box;
                transition: border-color 0.3s;
            }
            input[type="text"]:focus, select:focus {
                outline: none;
                border-color: var(--flipper-orange);
            }
            .button-group {
                display: flex;
                gap: 15px;
                margin-top: 30px;
            }
            button {
                flex: 1;
                padding: 12px;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                color: white;
                cursor: pointer;
                transition: background-color 0.3s, transform 0.1s;
            }
            button:active {
                transform: scale(0.97);
            }
            .btn-on {
                background-color: var(--btn-on);
            }
            .btn-on:hover {
                background-color: var(--btn-on-hover);
            }
            .btn-off {
                background-color: var(--btn-off);
            }
            .btn-off:hover {
                background-color: var(--btn-off-hover);
            }
            /* Icona Flipper stilizzata */
            .icon {
                font-size: 40px;
                margin-bottom: 10px;
            }
        </style>
    </head>
    <body>
        <div class="card">
            <div class="header">
                <div class="icon">🐬</div>
                <h2>Flipper Controller</h2>
                <p>Gestione payload MQTT</p>
            </div>
            
            <form method="POST">
                <div class="form-group">
                    <label for="name">Nome Device:</label>
                    <input type="text" id="name" name="name" placeholder="es. TV_Sala" required>
                </div>

                <div class="form-group">
                    <label for="type">Topic / Protocollo:</label>
                    <select id="type" name="type">
                        <option value="subghz">📡 subGHz</option>
                        <option value="infrared">🔴 infrared</option>
                    </select>
                </div>

                <div class="button-group">
                    <button type="submit" name="action" value="on" class="btn-on">ON</button>
                    <button type="submit" name="action" value="off" class="btn-off">OFF</button>
                </div>
            </form>
        </div>
    </body>
    </html>
    """
    return html_interface

# Rotta di default che reindirizza subito alla rotta principale
@app.route("/")
def index():
    return redirect("/flippermaxime")


if __name__ == "__main__":
    
    # NOTA SUL CAMBIO PORTA (Da 5000 a 5001):
    # Il progetto è iniziato su ambiente Windows dove la porta 5000 era libera e utilizzabile di default.
    # Passando a macOS (da Monterey in poi), la porta 5000 è occupata dal servizio di sistema "Ricevitore AirPlay".
    # Per evitare conflitti "Address already in use" senza dover modificare le impostazioni di sistema del Mac,
    # la porta del web server è stata spostata sulla 5001.
    
    app.run(
        host="0.0.0.0",
        port=5001
    )