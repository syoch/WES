import asyncio
from .ReadWriter import ReadWriter
from . import wiiu

handle_lock = asyncio.Lock()


async def handler(r, w):
    global handle_lock

    client = ReadWriter(r, w)
    addr = client.writer.get_extra_info("peername")

    print("[#] Get connection from {}".format(addr))
    while not client.writer.is_closing():
        clie_data = await client.recv()
        if not clie_data:
            continue
        print("[*] <<< {}".format(clie_data.hex()))

        if clie_data[0] == 0x05 and int.from_bytes(clie_data[1:5], "big") < 0x010000000:
            print("[*] --> b0 (memory protect)")
            client.writer.write(b"\xb0")
            await client.writer.drain()
            await asyncio.sleep(0.1)
            continue

        async with handle_lock:
            wiiu_data = await wiiu.wiiu.communicate(clie_data)

            print("[*] >>> {}".format(wiiu_data.hex()))
            client.writer.write(wiiu_data)

    print("[#] Lost connection from {} ".format(addr))


async def main():
    global server
    server = await asyncio.start_server(handler, "", 7331)
    print("[*] Server is listening at {}".format([
        sock.getsockname()
        for sock in server.sockets
    ]))
    await server.serve_forever()


def exit():
    server.close()
