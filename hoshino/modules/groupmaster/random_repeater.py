import random
import hoshino
import requests
import io
import os
from hoshino import Service, util
from hoshino.typing import CQEvent, CQHttpError, Message
from PIL import Image, ImageSequence
sv = Service('random-repeater', help_='随机复读机pro')

PROB_A = 1.4
group_stat = {}     # group_id: (last_msg, is_repeated, p)

'''
不复读率 随 复读次数 指数级衰减
从第2条复读，即第3条重复消息开始有几率触发复读

a 设为一个略大于1的小数，最好不要超过2，建议1.6
复读概率计算式：p_n = 1 - 1/a^n
递推式：p_n+1 = 1 - (1 - p_n) / a
'''
@sv.on_message()
async def random_repeater(bot, ev: CQEvent):
    group_id = ev.group_id
    msg = ev.message

    if group_id not in group_stat:
        group_stat[group_id] = (msg, False, 0)
        return

    last_msg, is_repeated, p = group_stat[group_id]
    if check_repeater(last_msg, msg):     # 群友正在复读   
        if not is_repeated:     # 机器人尚未复读过，开始测试复读
            hoshino.logger.debug(f"{group_id} 群友正在复读，当前参与概率：{p}")
            if random.random() < p:    # 概率测试通过，复读并设flag
                try:
                    group_stat[group_id] = (msg, True, 0)
                    await _repeater(bot, ev, 0.3)
                except CQHttpError as e:
                    hoshino.logger.error(f'复读失败: {type(e)}')
                    hoshino.logger.exception(e)
            else:                      # 概率测试失败，蓄力
                p = 1 - (1 - p) / PROB_A
                group_stat[group_id] = (msg, False, p)
        else:
            hoshino.logger.debug(f"{group_id} 群友还在复读")
    else:   # 不是复读，重置
        if random.random() < 0.0001:
            await bot.send(ev, str(msg))
            group_stat[group_id] = (msg, True, 0)
        else:
            group_stat[group_id] = (msg, False, 0)


def _test_a(a):
    '''
    该函数打印prob_n用于选取调节a
    注意：由于依指数变化，a的轻微变化会对概率有很大影响
    '''
    p0 = 0
    for _ in range(10):
        p0 = (p0 - 1) / a + 1
        print(p0)


def check_repeater(lastmsg, msg):
    if str(lastmsg) == str(msg):
        return True
    else:
        lenth = len(lastmsg)
        if lenth == len(msg):
            for i in range(lenth):
                if lastmsg[i]['type'] != msg[i]['type']:
                    return False
                elif lastmsg[i]['type'] == 'image':
                    if lastmsg[i]['data']['file'] != msg[i]['data']['file']:
                        return False
                else:
                    if lastmsg[i]['data'] != msg[i]['data']:
                        return False
            return True
    return False


async def _repeater(bot, ev, if_daduan=0):
    if random.random() < if_daduan:
        await bot.send(ev, '不许复读！')
        hoshino.logger.debug(f"{ev.group_id} 打断了一次复读")
        return
    imgcount = 0
    for i in ev.message:
        if i['type'] == 'image':
            img = i['data']['url']
            imgname = i['data']['file']
            imgcount += 1
        else:
            imgcount = 0
            break
    if imgcount == 1:
        image = Image.open(io.BytesIO(requests.get(img, timeout=20).content))
        imgpath = os.path.join(os.path.dirname(__file__), f'data\\repeater\\{imgname}')
        turnAround = random.randint(0, 6)
        if image.format == 'GIF':
            imgpath += '.gif'
            if image.is_animated:
                frames = [f.transpose(turnAround).copy() for f in ImageSequence.Iterator(image)]
                if random.random() < 0.5:
                    frames.reverse() # 内置列表倒序方法
                frames[0].save(imgpath, save_all=True, append_images=frames[1:])
        else:
            imgpath += '.jpg'
            image.transpose(turnAround).save(imgpath)
        await bot.send(ev, f'[CQ:image,file=file:///{imgpath}]')
        hoshino.logger.debug(f"{ev.group_id} 对单图片进行了特殊复读")
    else:
        textcount = 0
        for i in ev.message:
            if i['type'] == 'text' or 'emoji':
                textcount += 1
            else:
                textcount = 0
                break
        msg = str(util.filt_message(ev.message))
        if textcount == 1:
            if random.random() < 0.05:
                msg = msg[::-1]
            elif random.random() < 0.05:
                lmsg = list(msg)
                random.shuffle(lmsg)
                msg = ''.join(lmsg)
        await bot.send(ev, msg)
        hoshino.logger.debug(f"{ev.group_id} 进行了一次复读")


NOTAOWA_WORD = (
    'bili', 'Bili', 'BILI', '哔哩', '啤梨', 'mu', 'pili', 'dili',
    '是不', '批里', 'nico', '滴哩', 'BiLi', '不会吧', '20'
)

lasttaowa = {}


@sv.on_message()
async def taowabot(bot, ev: CQEvent):
    group_id = ev.group_id
    if group_id not in lasttaowa:
        lasttaowa[group_id] = ('', 0)
    is_taowa = 0
    for m in ev.message:
        if m.type in 'atimageface':
            lasttaowa[group_id] = ('', 0)
            return
    msg = str(ev.message)
    ltbegin = 0
    lefttaowa = ''
    while ltbegin <= len(msg) / 2:
        ltbegin = msg.find(msg[0], ltbegin+1)
        if ltbegin == -1:
            break
        lefttaowa = msg[0:ltbegin]
        if len(lefttaowa.lstrip(msg[0])) == 0 or len(lefttaowa.rstrip('"：:“')) == 0:
            continue
        if msg.startswith(lefttaowa.rstrip('"：:“'), ltbegin):
            is_taowa = 1
            break
    if is_taowa:
        if lefttaowa in NOTAOWA_WORD:
            return
        lastt, taowacount = lasttaowa[group_id]
        if lefttaowa != lastt:
            lasttaowa[group_id] = (lefttaowa, 0)
        else:
            if taowacount == 0:
                await bot.send(ev, '禁止套娃!')
            taowacount += 1
            lasttaowa[group_id] = (lefttaowa, taowacount)
            return
        if (lefttaowa[ltbegin - 1] == '"') & (msg[len(msg) - 1] == '"'):
            msg = msg + '"'
        if (lefttaowa[ltbegin - 1] == '“') & (msg[len(msg) - 1] == '”'):
            msg = msg + '”'
        if (lefttaowa[0] == '《') & (msg[len(msg) - 1] == '》') & (lefttaowa[ltbegin - 1] != '》'):
            msg = msg + '》'
        msg = lefttaowa + msg
        await bot.send(ev, util.filt_message(msg))
    else:
        lasttaowa[group_id] = ('', 0)

# TODO:《论《论《套娃》的危害》的危害》如何套娃
