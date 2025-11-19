import asyncio
import aiohttp

async def get_with_retry(url, session, headers, retries=3, delay=2):
    for attempt in range(retries):
        try:
            async with session.get(url, headers=headers) as response:
                if response.ok:
                    return await response.json()
                else:
                    pass
        except aiohttp.ClientError as e:
            pass
        if attempt < retries - 1:
            await asyncio.sleep(delay)
    return None

async def post_with_retry(url, session, headers, data, retries=3, delay=2):
    for attempt in range(retries):
        try:
            async with session.post(url, headers=headers, data=data) as response:
                if response.ok:
                    return await response.json()
                else:
                    pass
        except aiohttp.ClientError as e:
            pass
        if attempt < retries - 1:
            await asyncio.sleep(delay)
    return None