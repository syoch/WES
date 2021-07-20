import asyncio


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
