import argparse, os, sys
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
            self.flipper.debug.on()

    def turn_on(self, label):
        if self.flipper:
            print(self.flipper.subghz.tx_from_file(f"/ext/subghz/_socket0_off.sub"))
        else:
            print("Flipper is not initialized. Please start the manager first." )

def main(): 

    parser = argparse.ArgumentParser(description="Flipper Manager")
    parser.add_argument("--config", type=str, help="Path to the configuration file", required=True)
    args = parser.parse_args()

    if not os.path.exists(args.config):
        print(f"Configuration file {args.config} does not exist.")
        sys.exit(1)

    # Load configuration and start the Flipper Manager
    with open(args.config, 'r') as config_file:
        config = config_file.read().strip()
        # print(f"Starting Flipper Manager with config: {config}")
        manager = FlipperManager(config_path=args.config)
        manager.start()
        while True:
            print ('> ', end='', flush=True)
            command = input()
            if (command == "q"):
                break 
            elif (command == "on"):
                manager.turn_on(label="example_label")  # Replace with actual label


if __name__ == "__main__":
    main()