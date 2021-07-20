import asyncio
from .ReadWriter import ReadWriter
import sys

wiiu: ReadWriter = None


async def main():
    global wiiu
    (r, w) = await asyncio.open_connection(sys.argv[1], int(sys.argv[2]))
    wiiu = ReadWriter(r, w)
    print("[*] Successfully connected to Wii U Server!")


def exit():
    wiiu.writer.close()
