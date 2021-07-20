import asyncio
import signal
import sys
from . import server as server
from . import wiiu as wiiu
signal.signal(signal.SIGINT, signal.SIG_DFL)


def main():
    global server, wiiu
    if len(sys.argv) != 3:
        print("[Usage] : WES.py <ip> <port>")

    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.gather(
            wiiu.main(),
            server.main()
        ))
    finally:
        wiiu.exit()
        server.exit()


if __name__ == "__main__":
    main()
