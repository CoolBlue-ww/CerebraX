import typing

print(type(typing))

import httpx

c = httpx.AsyncClient()

from playwright.async_api import async_playwright

import asyncio

async def main():
    a = async_playwright()
    p = await a.start()
    if p.__class__.__name__ == 'AsyncPlaywright':
        print("Async Playwright")
    print(p.__class__.__name__ )


asyncio.run(main())



