import asyncio
from .ReadWriter import ReadWriter
import sys
from .server import last_client

wiiu: ReadWriter = None


async def main():
    global wiiu
    (r, w) = await asyncio.open_connection(sys.argv[1], int(sys.argv[2]))
    wiiu = ReadWriter(r, w)
    print("[*] Successfully connected to Wii U Server!")
    while True:
        if wiiu.locks["communicate"].locked():
            continue
        data = wiiu.recv()
        last_client.writer.write(data)


def exit():
    wiiu.writer.close()
