#!/usr/bin/env python3

import argparse
import logging
import threading
import time

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

    ROTATION_TIME = 0.65

    def __init__(self, args):
        self.stopped = False
        self.args = args
        self.init_args()

    def init_args(self) -> None:
        self.attempts = 0

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

        while not self.check_stopped():
            logging.info("Rotating the current ring 9 times...")
            HoldKey(keys_mapping.f, self.ROTATION_TIME * 9)
            if self.check_stopped():
                break
            time.sleep(0.6)
            if self.check_stopped():
                break
            logging.info("Switching ring position to the right")
            PressAndReleaseKey(keys_mapping.f)
            if self.check_stopped():
                break
            time.sleep(0.6)

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
