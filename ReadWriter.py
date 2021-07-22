import asyncio
from time import time


class ReadWriter():
    def __init__(self,
                 reader: asyncio.StreamReader,
                 writer: asyncio.StreamWriter):
        self.reader = reader
        self.writer = writer
        self.locks = {
            "recv": asyncio.Lock(),
            "communicate": asyncio.Lock(),
        }

    async def _recv(self):
        if self.reader.at_eof():
            return -1
        return await self.reader.read(8192)

    async def recv(self, timeout=0.05):
        ret = b""
        prev = time()
        async with self.locks["recv"]:
            while time() - prev < timeout:  # do not come a data during 'timeout'(seconds) to exit loop
                chunk = await self._recv()
                if not chunk:  # disconnected
                    self.writer.close()
                    break

                if chunk != -1:  # recv some data
                    prev = time()
                    ret += chunk
        return ret

    async def communicate(self, data):
        async with self.locks["communicate"]:
            self.writer.write(data)
            await self.writer.drain()
            return await self.recv()
