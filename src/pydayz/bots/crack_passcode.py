#!/usr/bin/env python3

import argparse
import logging
import threading
import time
from datetime import timedelta

import win32com.client as comclt
from pydayz.constants import APPLICATION_WINDOW_NAME

from iocontroller.keymouse import keys_mapping
from iocontroller.keymouse.commands_controller import (
    HoldKey,
    PressAndReleaseKey,
)
from iocontroller.keymouse.key_watcher import KeyWatcher
from iocontroller.window.window_handler import select_window

logging.getLogger(__name__)
logging.root.setLevel(logging.INFO)


class CrackPasscode(object):

    PRE_ROTATION_DELAY = 0.85
    ROTATION_TIME = 0.55
    COOLDOWN_TIME = 0.6

    def __init__(self, args):
        self.stopped = False
        self.args = args
        self.init_args()

    def init_args(self) -> None:

        if not self.args.discs:
            logging.error("Error: `discs` argument is required.")
            exit()

        self.discs = self.args.discs
        if self.discs not in [3, 4]:
            logging.error("Error: `discs` argument has to be 3 or 4.")
            exit()

        if self.args.initial < 0:
            logging.error(
                "Error: initial combination has to be a positive number."
            )
            exit()

        if self.discs == 3 and self.args.initial > 999:
            logging.error(
                "Error: initial combination too big for 3-discs padlock. Range: [0, 999]"
            )
            exit()

        if self.discs == 4 and self.args.initial > 9999:
            logging.error(
                "Error: initial combination too big for 4-discs padlock. Range: [0, 9999]"
            )
            exit()

        self.initial_combination = self.args.initial
        self.current_combination = self.initial_combination

    def watch_keys(self) -> None:
        self.watcher = KeyWatcher(stop_func=self.stop)
        self.watcher.start()

    def start(self) -> None:
        # Select the application window
        try:
            select_window(APPLICATION_WINDOW_NAME)
        except Exception as err:
            logging.error(str(err))
            return

        # Spawn the keywatcher thread
        self.watcher_thread = threading.Thread(target=self.watch_keys, args=())
        # Daemon = True -> kill it when main thread terminates
        self.watcher_thread.setDaemon(True)
        self.watcher_thread.start()

        # Init win32com to inject keys
        self.wsh = comclt.Dispatch("WScript.Shell")
        self.wsh.AppActivate(APPLICATION_WINDOW_NAME)

        self.tries = 0
        self.start_time = time.time()

        logging.info("Press ESC key to stop.")

        self.crack_brute()

        logging.info("Crack passcode stopped")

    def crack_brute(self) -> None:
        logging.info("Brute force attack started")
        logging.info(
            f"Initial combination: {self.format_combination(self.initial_combination)}"
        )
        logging.info(
            "Make sure the current moving disc is the last one (units digit)."
        )

        self.crack_padlock()

        logging.info(
            f"Last tried combination: {self.format_combination(self.current_combination)}."
        )
        logging.info(
            f"Execute `pydayz_crack_passcode --discs {self.discs} --initial {self.current_combination}` to resume it."
        )

    def crack_padlock(self):
        for _ in range(10 ** (self.discs - 1)):
            if self.check_stopped():
                break

            self.show_progress()

            logging.info("Rotating the units disc 9 times...")
            HoldKey(
                keys_mapping.f,
                self.PRE_ROTATION_DELAY + self.ROTATION_TIME * 9,
                self.COOLDOWN_TIME,
            )

            if self.check_stopped():
                break

            logging.info("Switching disc position to the tens digit")
            self.switch_disc(self.discs - 1)

            if self.check_stopped():
                break

            logging.info("Rotating the decimal disc 1 time...")
            HoldKey(
                keys_mapping.f,
                self.PRE_ROTATION_DELAY + self.ROTATION_TIME,
                self.COOLDOWN_TIME,
            )

            self.current_combination += 10

            if self.check_stopped():
                break

            # check and increment the hundreds digit if tens digit is a 0
            if (self.current_combination // 10) % 10 == 0:
                logging.info("Switching disc position to the hundreds digit")
                self.switch_disc(self.discs - 1)

                if self.check_stopped():
                    break

                logging.info("Rotating the hundreds disc 1 time...")
                HoldKey(
                    keys_mapping.f,
                    self.PRE_ROTATION_DELAY + self.ROTATION_TIME,
                    self.COOLDOWN_TIME,
                )

                if self.discs == 3 and self.current_combination >= 1000:
                    self.current_combination -= 1000

                if self.check_stopped():
                    break

                if self.discs == 4:
                    # check and increment the thousands digit if hundreds digit is a 0
                    if (self.current_combination // 100) % 10 == 0:
                        logging.info(
                            "Switching disc position to the thousands digit"
                        )
                        self.switch_disc(self.discs - 1)

                        if self.current_combination >= 10000:
                            self.current_combination -= 10000

                        if self.check_stopped():
                            break

                        logging.info("Rotating the thousands disc 1 time...")
                        HoldKey(
                            keys_mapping.f,
                            self.PRE_ROTATION_DELAY + self.ROTATION_TIME,
                            self.COOLDOWN_TIME,
                        )

                        if self.check_stopped():
                            break

                        logging.info(
                            "Switching disc position to the hundreds digit"
                        )
                        self.switch_disc(1)

                logging.info("Switching disc position to the tens digit")
                self.switch_disc(1)

            logging.info("Switching disc position to the units digit")
            self.switch_disc(1)

    def show_progress(self) -> None:
        elapsed_seconds = time.time() - self.start_time
        total_combinations = 10**self.discs
        guessed_combinations = (
            self.current_combination - self.initial_combination
            if self.current_combination > self.initial_combination
            else total_combinations
            - self.initial_combination
            + self.current_combination
        )
        eta_seconds = (total_combinations - guessed_combinations) * (
            elapsed_seconds / guessed_combinations
        )

        logging.info(
            f"Current combination: {self.format_combination(self.current_combination)}"
        )
        logging.info(
            f"Elapsed time: {str(timedelta(seconds=elapsed_seconds))}"
        )
        logging.info(
            f"ETA: {str(timedelta(seconds=eta_seconds))} | {round((guessed_combinations / total_combinations)*100,2)}%"
        )

    def format_combination(self, combination) -> str:
        return (
            "[" + " ".join(str(combination).zfill(self.discs)[:-1] + "X") + "]"
        )

    def cooldown(self, seconds=COOLDOWN_TIME) -> None:
        time.sleep(seconds)

    def switch_disc(self, times=1) -> None:
        for _ in range(times):
            PressAndReleaseKey(keys_mapping.f, cooldown=0.2)
            if self.check_stopped():
                return

    def stop(self) -> None:
        self.stopped = True

    def check_stopped(self) -> bool:
        if (
            self.args.timeout
            and time.time() - self.start_time >= self.args.timeout
        ):
            logging.info(f"Timeout ({str(self.args.timeout)}s). Stopping...")
            self.key_watcher.shutdown()
            return True
        if self.stopped:
            return True


def get_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--discs",
        default=None,
        help="Number of padlock discs. Allowed are: [3, 4]",
        type=int,
    )
    parser.add_argument(
        "--initial",
        default=0,
        help="Initial combination on the padlock",
        type=int,
    )
    parser.add_argument(
        "--timeout",
        default=None,
        help="Maximum time (in seconds) allowed to the script to run",
        type=int,
    )

    return parser


def main() -> None:
    parser = get_argument_parser()
    args = parser.parse_args()

    crack_passcode = CrackPasscode(args)
    logging.info("Process started.")
    crack_passcode.start()
    logging.info("Process terminated.")


if __name__ == "__main__":
    main()
