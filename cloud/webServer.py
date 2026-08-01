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
    # In futuro, potrai spostare questo blocco in un file dentro la cartella /templates
    html_interface = """
    <!DOCTYPE html>
    <html>
    <head><title>Controllo Flipper Zero</title></head>
    <body style="font-family: Arial; margin: 40px;">
        <h2>Gestione Dispositivi Flipper Zero</h2>
        <form method="POST">
            <label><strong>Nome Device:</strong></label><br>
            <input type="text" name="name" placeholder="es. TV_Sala" required><br><br>

            <label><strong>Topico (Tipo di segnale):</strong></label><br>
            <select name="type">
                <option value="subGHz">subGHz</option>
                <option value="infrared">infrared</option>
            </select><br><br>

            <button type="submit" name="action" value="on" style="background: green; color: white; padding: 10px 20px;">ON</button>
            <button type="submit" name="action" value="off" style="background: red; color: white; padding: 10px 20px;">OFF</button>
        </form>
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