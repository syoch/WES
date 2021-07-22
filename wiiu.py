import asyncio
from .ReadWriter import ReadWriter
import sys

wiiu: ReadWriter = None


async def main():
    global wiiu
    (r, w) = await asyncio.open_connection(sys.argv[1], int(sys.argv[2]))
    wiiu = ReadWriter(r, w)
    print("[*] Successfully connected to Wii U Server!")

    from . import server
    while True:
        await asyncio.sleep(0.1)
        if wiiu.locks["communicate"].locked():
            continue
        if not server.last_client:
            continue

        data = await wiiu._recv()
        if data == -1:
            continue
        server.last_client.writer.write(data)


def exit():
    if wiiu:
        wiiu.writer.close()
