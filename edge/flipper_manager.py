import argparse, os, sys, signal, atexit
from pyflipper import PyFlipper


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
            # print(f"Starting Flipper Manager with config: {config}")
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
                print(f"Attenzione: errore durante la chiusura della seriale: {e}")
            finally:
                self.flipper = None
                print("\nConnessione seriale chiusa. Uscita pulita.")

    def turn_on(self, label):
        if self.flipper:
            print(self.flipper.subghz.tx_from_file("/ext/subghz/F_socket0_on.sub"))
        else:
            print("Flipper is not initialized. Please start the manager first.")

    def turn_off(self, label):
        if self.flipper:
            print(self.flipper.subghz.tx_from_file("/ext/subghz/F_socket0_off.sub"))
        else:
            print("Flipper is not initialized. Please start the manager first.")


def main():
    parser = argparse.ArgumentParser(description="Flipper Manager")
    parser.add_argument("--config", type=str, help="Path to the configuration file", required=True)
    args = parser.parse_args()

    if not os.path.exists(args.config):
        print(f"Configuration file {args.config} does not exist.")
        sys.exit(1)

    manager = FlipperManager(config_path=args.config)
    manager.start()

    atexit.register(manager.cleanup)

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
            manager.cleanup()
            break
        elif command == "on":
            manager.turn_on(label="example_label")  # Replace with actual label
        elif command == "off":
            manager.turn_off(label="example_label")  # Replace with actual label


if __name__ == "__main__":
    main()