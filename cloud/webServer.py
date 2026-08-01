from flask import Flask, request, redirect

import paho.mqtt.client as mqtt

client = None

# ================= Settings =================
BROKER_ADDRESS = "localhost"  
BROKER_PORT = 1883            
BASE_TOPIC = "flippermaxxin"                     
# ================================================

class MQTTClient:
    def __init__(self, broker_address, broker_port):
        self.broker_address = broker_address
        self.broker_port = broker_port

        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

    def start(self):
        try:
            self.client.connect(self.broker_address, self.broker_port, keepalive=60)
            self.client.loop_start()
            print("MQTT client started and running in background.")
        except Exception as e:
            print(f"❌ Failed to connect to MQTT broker: {e}")

    def publish(self, topic, payload):
        try:
            print(f"[OUT] Publishing to {topic}: {payload}")
            self.client.publish(topic, payload, qos=0)
            print(f"[OUT] Published to {topic}: {payload}")
        except Exception as e:
            print(f"❌ Failed to publish message: {e}")

app = Flask(__name__)

@app.route("/flippermaxxin", methods=["GET", "POST"])
def flippermaxxin():
    if request.method == "POST":
        device_name = request.form.get("name")
        signal_type = request.form.get("type") 
        action = request.form.get("action")    

        topic = f"{BASE_TOPIC}/{signal_type}/{device_name}"

        if action == "on":
            client.publish(topic, "on")
        elif action == "off":
            client.publish(topic, "off")

        return redirect("/flippermaxxin")

    
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
            
            <form method="POST" id="deviceForm">
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

        <script>
        document.getElementById('deviceForm').addEventListener('submit', function (e) {
            e.preventDefault();

            const form = e.target;
            const submitter = e.submitter; 
            const formData = new FormData(form);
            if (submitter && submitter.name) {
                formData.append(submitter.name, submitter.value);
            }

            const targetUrl = form.getAttribute('action') || window.location.pathname;

            fetch(targetUrl, {
                method: 'POST',
                body: formData
            })
            .then(res => res.text())
            .then(() => {
            })
            .catch(err => console.error('Errore invio comando:', err));
        });
        </script>
    </body>
    </html>
    """
    return html_interface

# Rotta di default che reindirizza subito alla rotta principale
@app.route("/")
def index():
    return redirect("/flippermaxxin")


if __name__ == "__main__":
    
    # NOTE ABOUT THE PORT CHANGE (From 5000 to 5001):
    # The project started in a Windows environment, where port 5000 was free and usable by default.
    # After moving to macOS (Monterey onward), port 5000 is used by the system service "AirPlay Receiver".
    # To avoid "Address already in use" conflicts without changing macOS system settings,
    # the web server port was moved to 5001.
    client = MQTTClient(BROKER_ADDRESS, BROKER_PORT)
    client.start()
    app.run(
        host="0.0.0.0",
        port=5001,
    )

    client.client.loop_stop()