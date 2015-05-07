import sys

from monitor import Monitor


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise Exception("Device required!")

    monitor = Monitor(dev=sys.argv[1])
    monitor.loop()

