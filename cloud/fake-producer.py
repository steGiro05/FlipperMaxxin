import paho.mqtt.client as mqtt
import time
import random
import json

# ================= Impostazioni =================
BROKER_ADDRESS = "localhost"  # Indirizzo del broker EMQX locale
BROKER_PORT = 1883            # Porta di default
BASE_TOPIC = "flippermaxxin"                     # Deve combaciare col base_topic del dispatcher (NIENTE slash iniziale)
TOPIC_SUB = f"{BASE_TOPIC}/#"                     # Ci iscriviamo a tutto l'albero per debug
TOPIC_PUB = f"{BASE_TOPIC}/subghz/prova"          # Deve essere <base_topic>/subghz/<device_path>
# ================================================

# Callback: eseguita quando il client si connette con successo al broker
def on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code == 0:
        print(f"✅ Connesso al broker MQTT ({BROKER_ADDRESS}:{BROKER_PORT})")
        # Effettuiamo la sottoscrizione una volta connessi
        client.subscribe(TOPIC_SUB)
        print(f"📡 Sottoscrizione effettuata sul topic: {TOPIC_SUB}")
    else:
        print(f"❌ Connessione fallita. Codice di errore: {reason_code}")

# Callback: eseguita quando arriva un messaggio su un topic sottoscritto
def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode("utf-8")
        print(f"\n[IN] Messaggio ricevuto su {msg.topic}:\n    > {payload}")
    except Exception as e:
        print(f"\n[IN] Errore di decodifica sul topic {msg.topic}: {e}")

# Inizializzazione del client MQTT (Utilizziamo la Callback API v2 per Paho 2.0+)
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

# Assegnazione delle funzioni di callback
client.on_connect = on_connect
client.on_message = on_message

print("Avvio del client MQTT...")

try:
    # Connessione al broker
    client.connect(BROKER_ADDRESS, BROKER_PORT, keepalive=60)
    
    # Avviamo il loop di rete in un thread in background
    # Questo permette di ricevere messaggi senza bloccare il ciclo while sottostante
    client.loop_start()
    
    # Loop principale: alterna comandi on/off compatibili col dispatcher
    toggle = True
    while True:
        tag = "on" if toggle else "off"
        toggle = not toggle

        payload_str = json.dumps({"tag": tag})

        client.publish(TOPIC_PUB, payload_str, qos=0)
        print(f"[OUT] Pubblicato su {TOPIC_PUB}: {payload_str}")

        time.sleep(5)

except KeyboardInterrupt:
    # Gestione dell'interruzione manuale (Ctrl+C)
    print("\n\nChiusura del client in corso...")
    client.loop_stop()
    client.disconnect()
    print("Disconnessione completata. Arrivederci!")
except Exception as e:
    print(f"Si è verificato un errore: {e}")