from bluepy.btle import UUID, DefaultDelegate, Peripheral, BTLEException
import itertools
import struct
import sys
import time
import argparse
from nuimo import NuimoScanner, Nuimo, NuimoConsoleLoggerDelegate

def connect(addr):
    nuimo = Nuimo(addr)
    nuimo.set_delegate(NuimoConsoleLoggerDelegate(nuimo))

    # Connect to Nuimo
    print("Trying to connect to %s. Press Ctrl+C to cancel." % addr)
    try:
        nuimo.connect()
    except BTLEException:
        print("Failed to connect to %s. Make sure to:\n  1. Disable the Bluetooth device: hciconfig hci0 down\n  2. Enable the Bluetooth device: hciconfig hci0 up\n  3. Enable BLE: btmgmt le on\n  4. Pass the right MAC address: hcitool lescan | grep Nuimo" % nuimo.macAddress)
        sys.exit()
    print("Connected. Waiting for input events...")

    # Display some LEDs matrices and wait for notifications
    nuimo.displayLedMatrix(
        "         " +
        " ***     " +
        " *  * *  " +
        " *  *    " +
        " ***  *  " +
        " *    *  " +
        " *    *  " +
        " *    *  " +
        "         ", 2.0)
    time.sleep(2)
    nuimo.displayLedMatrix(
        " **   ** " +
        " * * * * " +
        "  *****  " +
        "  *   *  " +
        " * * * * " +
        " *  *  * " +
        " * * * * " +
        "  *   *  " +
        "   ***   ", 20.0)

    try:
        while True:
            nuimo.waitForNotifications()
    except BTLEException as e:
        print("Connection error:", e)
    except KeyboardInterrupt:
        print("Program aborted")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('cmd', help="command to run", choices=["search", "connect"])
    parser.add_argument('-d', help="device to connect to",required=False)
    args = parser.parse_args()

    if args.cmd == "search":
        def callback(addr):
            connect(addr)
        scanner = NuimoScanner()
        scanner.start(callback)
    else:
        connect(args.d)

