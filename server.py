import asyncio
from .ReadWriter import ReadWriter
from . import wiiu


def hex_to_str(raw: bytes):
    msg = raw.hex()
    if len(msg) > 80:
        msg = msg[0:80]
        msg += "...more than {}bytes".format(len(raw)-40)
    return msg


last_client: ReadWriter = None


async def handler(r, w):
    global last_client
    client = ReadWriter(r, w)
    addr = client.writer.get_extra_info("peername")

    print("[#] Get connection from {}".format(addr))
    while not client.writer.is_closing():
        clie_data = await client.recv()
        if not clie_data:
            continue
        print("[*] <<< {}".format(hex_to_str(clie_data)))

        if clie_data[0] == 0x05 and int.from_bytes(clie_data[1:5], "big") < 0x010000000:
            print("[*] --> b0 (memory protect)")
            client.writer.write(b"\xb0")
            await client.writer.drain()
            continue

        wiiu_data = await wiiu.wiiu.communicate(clie_data)
        if not wiiu_data:
            last_client = client
        print("[*] >>> {}".format(hex_to_str(wiiu_data)))
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
