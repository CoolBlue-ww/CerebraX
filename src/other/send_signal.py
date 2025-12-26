import asyncio, os, platform, signal

async def set_sig(self) -> None:
    try:
        await asyncio.wait_for(self.server.serve(), timeout=5)
    except asyncio.TimeoutError:
        system = platform.system()
        if system == 'Windows':
            pid, sig = os.getpid(), signal.CTRL_C_EVENT
            os.kill(pid, sig)
        if system in {'Linux', 'MacOS', 'Darwin'}:
            pid, sig = os.getpid(), signal.SIGTERM
            os.kill(pid, sig)
    return None