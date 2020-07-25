import requests
from nonebot import on_command, CommandSession


@on_command('daily', aliases=('每日一句'), only_to_me=False)
async def daily(session: CommandSession):
    daily_send = await get_daily()
    await session.send(daily_send[0])
    await session.send(daily_send[1])


async def get_daily():
    url = 'http://open.iciba.com/dsapi/'
    res = requests.get(url)
    content_e = res.json()['content']
    content_c = res.json()['note']
    return [content_c, content_e]
