import random
import re
import os
from time import time
from hoshino import Service
import hoshino
import json
from os import path
sv = Service('random-title', help_='''随机头衔
[@bot随机头衔]获得一个随机头衔
[@bot申请头衔]后跟自己想要的头衔
'''.strip())

Timecd = 86400  # 这是一天
last_req = {}


@sv.on_keyword('随机头衔', only_to_me=True)
async def random_title(bot, ev):
    if await check_is_owner(bot, ev):  # 判断自己是不是群主，不是就忽略
        user_id = ev.user_id
        if pohaicheck(ev.group_id, user_id):  # 判断是否被迫害，是的话忽略
            return
        await check_cd(bot, ev, Timecd/12)  # 判断是否cd
        await bot.set_group_special_title(
            group_id=ev.group_id,
            user_id=user_id,
            special_title=rand_title(),
        )


@sv.on_prefix(('申请头衔', '我想要头衔', '想要头衔'), only_to_me=True)
async def set_title(bot, ev):
    if await check_is_owner(bot, ev):
        user_id = ev.user_id
        if pohaicheck(ev.group_id, user_id):
            return
        s = ev.message
        await check_cd(bot, ev, Timecd)
        await bot.set_group_special_title(
            group_id=ev.group_id,
            user_id=user_id,
            special_title=str(s),
        )


@sv.on_prefix(('设置头衔'), only_to_me=True)  # 设置头衔并加入迫害列表
async def suset_title(bot, ev):
    if await check_is_owner(bot, ev):
        if ev.user_id not in bot.config.SUPERUSERS or bot.config.PYUSERS:  # master限定
            return
        msg = str(ev.message)
        matchObj = re.match(r'^\[CQ:at,qq=([0-9]+)\] (.*)$', msg)
        if matchObj is not None:
            uid = int(matchObj.group(1))
            s = str(matchObj.group(2))
            await bot.set_group_special_title(
                group_id=ev.group_id,
                user_id=uid,
                special_title=s,
            )
            pohaiadd(ev.group_id, uid)




@sv.on_prefix(('不迫害', '不再迫害'), only_to_me=True)
async def no_pohai(bot, ev):
    if await check_is_owner(bot, ev):
        if ev.user_id not in bot.config.SUPERUSERS or bot.config.PYUSERS:
            return
        count = 0
        for m in ev.message:
            if m.type == 'at' and m.data['qq'] != 'all':
                uid = int(m.data['qq'])
                if nopohai(ev.group_id, uid):
                    count += 1
        if count:
            await bot.send(ev, f"已解除{count}位用户的迫害～")


def rand_name(length=2):
    word = ''
    for _ in range(length):
        a = random.randint(0xb0, 0xd7)
        if a == 0xd7:
            b = random.randint(0xa1, 0xf9)
        else:
            b = random.randint(0xa1, 0xfe)
        val = f'{a:x}{b:x}'
        word += bytes.fromhex(val).decode('gb2312')
    if random.random() < 0.9:
        return word
    else:
        return '随机头衔'


def rand_title():
    r = random.random()
    if r < 0.9:
        length = 2
    elif r < 0.99:
        length = 3
    else:
        length = 4
    return rand_name(length)


async def check_cd(bot, ev, addcd):
    global last_req
    now = time()
    if(last_req.get(ev.user_id, 0) > now):
        cd = int(last_req.get(ev.user_id, 0) - now)
        scd = f'{str(int(cd/3600))}h{str(int((cd%3600)/60))}min{str(int((cd%3600)%60))}s'
        await bot.finish(ev, f'新头衔要好好佩戴哦(cd:{scd})', at_sender=True)
    last_req[ev.user_id] = now + addcd  # 冷却10000秒


async def check_is_owner(bot, ev):
    self_info = await bot.get_group_member_info(
        group_id=ev.group_id,
        user_id=ev.self_id,
    )
    if self_info['role'] == 'owner':
        return True
    else:
        return False


josnpath = os.path.join(os.path.dirname(__file__), 'pohailist.json')
if not path.exists(josnpath):
    content = '''{
    "1111111": []
}'''
    with open(josnpath, 'w') as file:
        file.write(content)


def save_config(config: dict):
    try:
        with open(josnpath, 'w', encoding='utf8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as ex:
        print(ex)
        return False


def load_config():
    try:
        with open(josnpath, 'r', encoding='utf8') as f:
            config = json.load(f)
            return config
    except:
        return {}


pohailist = load_config()  # 读列表


def pohaiadd(group_id, user_id):  # 加入迫害列表
    if user_id in hoshino.config.SUPERUSERS or hoshino.config.PYUSERS:
        return
    if str(group_id) not in pohailist:
        pohailist[str(group_id)] = [user_id]
    elif user_id not in pohailist[str(group_id)]:
        pohailist[str(group_id)].append(user_id)
    else:
        return
    save_config(pohailist)


def pohaicheck(group_id, user_id):  # 检查是否受迫害
    if user_id in hoshino.config.SUPERUSERS or hoshino.config.PYUSERS:
        return False
    if str(group_id) not in pohailist:
        pohailist[str(group_id)] = []
        save_config(pohailist)
        return False
    elif user_id not in pohailist[str(group_id)]:
        return False
    return True


def nopohai(group_id, user_id):
    if str(group_id) not in pohailist:
        pohailist[str(group_id)] = []
        save_config(pohailist)
        return False
    elif user_id not in pohailist[str(group_id)]:
        return False
    else:
        pohailist[str(group_id)].remove(user_id)
        save_config(pohailist)
        return True
