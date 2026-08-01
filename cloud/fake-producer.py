import paho.mqtt.client as mqtt
import time
import random
import json

# ================= Impostazioni =================
BROKER_ADDRESS = "localhost"  # Indirizzo del broker EMQX locale
BROKER_PORT = 1883            # Porta di default
TOPIC_SUB = "/flippermaxxin"  # Topic a cui iscriversi
TOPIC_PUB = "/subghz/prova"   # Topic su cui pubblicare
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
    
    # Loop principale per pubblicare dati periodici
    while True:
        # Generiamo dati fittizi
        dati_random = {
            "frequenza": random.choice([433.92, 868.35, 315.00]),
            "rssi": random.randint(-100, -30),
            "snr": round(random.uniform(1.0, 10.0), 2),
            "protocollo": random.choice(["NICE", "CAME", "FAAC", "RAW"])
        }
        
        # Convertiamo il dizionario in una stringa JSON
        payload_str = json.dumps(dati_random)
        
        # Pubblichiamo il messaggio
        client.publish(TOPIC_PUB, payload_str, qos=0)
        print(f"[OUT] Pubblicato su {TOPIC_PUB}: {payload_str}")
        
        # Attesa di 5 secondi prima della prossima pubblicazione
        time.sleep(5)

except KeyboardInterrupt:
    # Gestione dell'interruzione manuale (Ctrl+C)
    print("\n\nChiusura del client in corso...")
    client.loop_stop()
    client.disconnect()
    print("Disconnessione completata. Arrivederci!")
except Exception as e:
    print(f"Si è verificato un errore: {e}")