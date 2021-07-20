import asyncio
from .ReadWriter import ReadWriter
from .wiiu import wiiu

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

        async with handle_lock:

            wiiu_data = await wiiu.communicate(clie_data)

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
