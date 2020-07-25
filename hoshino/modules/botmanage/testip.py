import asyncio
import re
import sys
import time

import aiohttp
from aiocache import cached
from nonebot import CommandSession, on_command


if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    if not hasattr(time, 'clock'):
        time.clock = time.time
import aioping

async def icmp_ping(host):
    try:
        delay = 1000 * await aioping.ping(host)
        return f'ICMP延迟{delay:.0f}毫秒'

    except TimeoutError:
        return f'ICMP超时'


@cached()
async def ip_location(ip):
    try:
        async with aiohttp.request("GET", url=f'http://freeapi.ipip.net/{ip}') as response:
            assert response.status == 200
            return '地区：' + ''.join(await response.json())
    except Exception as e:
        print(e)
        return '地区：未知'


async def prob_tcp(host, port, duration=4, delay=0.5):
    if port is None:
        return ''
    start_time = time.time()
    tmax = start_time + duration
    while time.time() < tmax:
        try:
            _reader, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=5)
            writer.close()
            await writer.wait_closed()
            return 'TCP延迟{:.0f}毫秒'.format((time.time() - start_time)*1000)
        except:
            if delay:
                await asyncio.sleep(delay)
    return 'TCP超时'


@on_command('testip', only_to_me=False)
async def test_ip(session:CommandSession):
    if session.current_arg is None:
        await session.send('testip ip <port>')
        return
    args = session.current_arg.split()
    good_input = False
    if len(args) == 1:
        ip = args[0]
        port = None
        if re.match(r'^\d{1,3}(?:\.\d{1,3}){3}$',ip):
            good_input = True
    elif len(args) == 2:
        ip,port = args
        if re.match(r'^\d{1,3}(?:\.\d{1,3}){3}$',ip) and port.isdigit():
            good_input = True
    if not good_input:
        await session.send('testip ip <port>')
        return
    results = await asyncio.gather(
        icmp_ping(ip),
        prob_tcp(ip,port),
        ip_location(ip),
    )
    await session.send('\n'.join((r for r in results if r)))
