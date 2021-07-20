import asyncio
from time import time


class ReadWriter():
    def __init__(self,
                 reader: asyncio.StreamReader,
                 writer: asyncio.StreamWriter):
        self.reader = reader
        self.writer = writer
        self.lock = asyncio.Lock()

    async def _recv(self):
        try:
            async with self.lock:
                return await asyncio.wait_for(self.reader.read(8192), 0.1)
        except asyncio.TimeoutError:
            return -1

    async def recv(self, timeout=0.2):
        ret = b""
        prev = time()
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
        async with self.lock:
            self.writer.write(data)
            await self.writer.drain()
            await asyncio.sleep(0.1)
            return await self.recv()
