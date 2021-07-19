import asyncio
import signal
import time
import sys
signal.signal(signal.SIGINT, signal.SIG_DFL)
clients = []


class ReadWriter():
    def __init__(self,
                 reader: asyncio.StreamReader,
                 writer: asyncio.StreamWriter):
        self.reader = reader
        self.writer = writer
        self.recv_lock = asyncio.Lock()

    async def _recv(self):
        try:
            async with self.recv_lock:
                return await asyncio.wait_for(self.reader.read(8192), 0.1)
        except asyncio.TimeoutError:
            return -1

    async def recv(self, timeout=0.2):
        ret = b""
        await asyncio.sleep(timeout)
        while True:  # return when do not sent a data while 'timeout'(sec)
            chunk = await self._recv()
            if not chunk:  # disconnected
                self.writer.close()
                break
            if chunk != -1:  # recv some data
                ret += chunk
            else:  # not data -> timeout
                break

            await asyncio.sleep(timeout)

        return ret

    async def communicate(self, data):
        self.writer.write(data)
        await self.writer.drain()
        return await self.recv()


wiiu: ReadWriter = None
handle_lock = asyncio.Lock()
last_client: ReadWriter = None


async def server_handle(r, w):
    global handle_lock, last_client

    client = ReadWriter(r, w)
    addr = client.writer.get_extra_info("peername")

    print("[#] Get connection from {}".format(addr))
    while not client.writer.is_closing():
        clie_data = await client.recv()
        if not clie_data:
            continue
        print("[*] <<< {}".format(clie_data.hex()))

        async with handle_lock:
            last_client = client

            wiiu_data = await wiiu.communicate(clie_data)

            print("[*] >>> {}".format(wiiu_data.hex()))
            client.writer.write(wiiu_data)

    print("[#] Lost connection from {} ".format(addr))


async def wiiu_connecter():
    global wiiu
    (r, w) = await asyncio.open_connection(sys.argv[1], int(sys.argv[2]))
    wiiu = ReadWriter(r, w)
    print("[*] Successfully connected to Wii U Server!")
    return
    while not wiiu.writer.is_closing():
        if handle_lock.locked():
            continue

        wiiu_data = await wiiu.recv()
        if not wiiu_data:
            continue
        print("[*] <<< {}".format(wiiu_data.hex()))
        last_client.writer.write(wiiu_data)
        await asyncio.sleep(0.5)


async def server_serve():
    global server
    server = await asyncio.start_server(server_handle, "", 7331)
    print("[*] Server is listening at {}".format([
        sock.getsockname()
        for sock in server.sockets
    ]))
    await server.serve_forever()


def main():
    global server, wiiu
    if len(sys.argv) != 3:
        print("[Usage] : WES.py <ip> <port>")

    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.gather(
            wiiu_connecter(),
            server_serve()
        ))
    finally:
        wiiu.writer.close()
        server.close()


if __name__ == "__main__":
    main()
