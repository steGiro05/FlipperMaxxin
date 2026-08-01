import argparse
import json
import os
import signal
import sys
import atexit

from pyflipper import PyFlipper
import paho.mqtt.client as mqtt


class FlipperManager:
    def __init__(self, config_path):
        self.config_path = config_path
        self.flipper = None

    def start(self):
        if not os.path.exists(self.config_path):
            print(f"Configuration file {self.config_path} does not exist.")
            sys.exit(1)

        with open(self.config_path, 'r') as config_file:
            config = config_file.read().strip()
            self.flipper = PyFlipper(com=f"{config}")

    def cleanup(self):
        if self.flipper is not None:
            try:
                serial_obj = getattr(self.flipper, "serial_wrapper", None) \
                    or getattr(self.flipper, "serial", None) \
                    or getattr(self.flipper, "ser", None)
                if serial_obj is not None and hasattr(serial_obj, "close"):
                    serial_obj.close()
                elif hasattr(self.flipper, "close"):
                    self.flipper.close()
            except Exception as e:
                print(f"Error while closing serial connection: {e}")
            finally:
                self.flipper = None
                print("\nClosed connection. Cleaning up.")

    def turn_on(self, label):
        if self.flipper:
            path = f"/ext/subghz/{label}_on.sub"
            print(f"[FlipperManager] TX ON -> {path}")
            print(self.flipper.subghz.tx_from_file(path))
        else:
            print("Flipper is not initialized. Please start the manager first.")

    def turn_off(self, label):
        if self.flipper:
            path = f"/ext/subghz/{label}_off.sub"
            print(f"[FlipperManager] TX OFF -> {path}")
            print(self.flipper.subghz.tx_from_file(path))
        else:
            print("Flipper is not initialized. Please start the manager first.")


class MQTTListener:

    def __init__(self, flipper_manager, broker_host="localhost", broker_port=1883,
                 base_topic="flippermaxxin", username=None, password=None):
        self.flipper_manager = flipper_manager
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.base_topic = base_topic
        self.subghz_topic_filter = f"{self.base_topic}/subghz/+"

        self.client = mqtt.Client()
        if username:
            self.client.username_pw_set(username, password)

        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
        self.client.on_subscribe = self._on_subscribe
        self.client.on_log = self._on_log

    def start(self):
        print(f"[MQTTListener] Connecting to {self.broker_host}:{self.broker_port}")
        self.client.connect(self.broker_host, self.broker_port, keepalive=60)
        self.client.loop_start()

    def stop(self):
        try:
            self.client.loop_stop()
            self.client.disconnect()
        except Exception as e:
            print(f"[MQTTListener] Error while disconnecting: {e}")
        finally:
            print("[MQTTListener] Successfully disconnected.")

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"[MQTTListener] Connected. Subscribing to: {self.subghz_topic_filter}")
            client.subscribe(self.subghz_topic_filter)
        else:
            print(f"[MQTTListener] Connection failed. Error code: {rc}")

    def _on_disconnect(self, client, userdata, rc):
        print(f"[MQTTListener] Disconnected (rc={rc}).")

    def _on_subscribe(self, client, userdata, mid, granted_qos):
        print(f"[MQTTListener] Subscription confirmed (mid={mid}, qos={granted_qos}).")

    def _on_log(self, client, userdata, level, buf):
        # Utile per vedere handshake TLS/auth falliti a basso livello
        print(f"[MQTTListener][paho-log] {buf}")

    def _on_message(self, client, userdata, msg):
        print(f"[MQTTListener] Received message on {msg.topic}: {msg.payload.decode('utf-8', errors='replace')}")
        topic = msg.topic
        payload_raw = msg.payload.decode("utf-8", errors="replace").strip()

        device_path = self._extract_device_path(topic)
        if device_path is None:
            print(f"[MQTTListener] Cannot find topic: {topic}")
            return

        tag = self._extract_tag(payload_raw)
        if tag is None:
            print(f"[MQTTListener] Unrecognized payload on {topic}: {payload_raw!r}")
            return

        print(f"[MQTTListener] Topic={topic} device_path={device_path} tag={tag}")

        if tag == "on":
            self.flipper_manager.turn_on(label=device_path)
        elif tag == "off":
            self.flipper_manager.turn_off(label=device_path)
        else:
            print(f"[MQTTListener] Unrecognized tag: {tag}")

    def _extract_device_path(self, topic):
        prefix = f"{self.base_topic}/subghz/"
        if not topic.startswith(prefix):
            return None
        device_path = topic[len(prefix):]
        return device_path if device_path else None

    def _extract_tag(self, payload_raw):
        lowered = payload_raw.lower()
        if lowered in ("on", "off"):
            return lowered

        try:
            data = json.loads(payload_raw)
            tag = str(data.get("tag", "")).lower()
            if tag in ("on", "off"):
                return tag
        except (json.JSONDecodeError, AttributeError):
            pass

        return None


def main():
    parser = argparse.ArgumentParser(description="Flipper Manager")
    parser.add_argument("--config", type=str, help="Path to the configuration file", required=True)
    parser.add_argument("--mqtt-host", type=str, default=os.environ.get("MQTT_HOST", "localhost"))
    parser.add_argument("--mqtt-port", type=int, default=int(os.environ.get("MQTT_PORT", 1883)))
    parser.add_argument("--mqtt-user", type=str, default=os.environ.get("MQTT_USERNAME"))
    parser.add_argument("--mqtt-pass", type=str, default=os.environ.get("MQTT_PASSWORD"))
    parser.add_argument("--mqtt-topic", type=str,
                         default=os.environ.get('MQTT_TOPIC_PREFIX', 'flippermaxxin'),
                         help="Base topic, es. flipper0 (subscribe to <topic>/subghz/+)")
    args = parser.parse_args()

    print(f"[Config] host={args.mqtt_host} port={args.mqtt_port} topic={args.mqtt_topic} "
          f"user={'<set>' if args.mqtt_user else '<none>'}")

    if not os.path.exists(args.config):
        print(f"Configuration file {args.config} does not exist.")
        sys.exit(1)

    manager = FlipperManager(config_path=args.config)
    manager.start()

    listener = MQTTListener(
        flipper_manager=manager,
        broker_host=args.mqtt_host,
        broker_port=args.mqtt_port,
        base_topic=args.mqtt_topic,
        username=args.mqtt_user,
        password=args.mqtt_pass,
    )
    listener.start()

    def cleanup_all():
        listener.stop()
        manager.cleanup()

    atexit.register(cleanup_all)

    def handle_sigint(signum, frame):
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_sigint)

    while True:
        try:
            print('> ', end='', flush=True)
            command = input()
        except EOFError:
            break

        if command == "q":
            break
        elif command == "on":
            manager.turn_on(label="example_label")  # Replace with actual label
        elif command == "off":
            manager.turn_off(label="example_label")  # Replace with actual label


if __name__ == "__main__":
    main()