import os
import random
from collections import defaultdict

from hoshino import Service, priv, util, R
from hoshino.typing import *
from hoshino.util import DailyNumberLimiter, concat_pic, pic2b64, silence

from .. import chara
from .gachapro import Gachapro

try:
    import ujson as json
except:
    import json


sv_help = '''
[@来发十连] 转蛋模拟
[@来发单抽] 转蛋模拟
[@来一井] 4w5钻！
[@查看卡池] 模拟卡池&出率
[@切换卡池] 更换模拟卡池
'''.strip()
sv = Service('gachapro', help_=sv_help, bundle='pcr娱乐')
FAIL_LIST = [
    f'抽卡被宫子拦住了！\n{R.img("priconne/gachafail/buding.jpg").cqcode}',
    f'主さま,花凛小姐有事不在\n{R.img("priconne/gachafail/kkl.jpg").cqcode}',
    f'奇怪的东西混进了卡池！\n{R.img(f"priconne/gachafail/jojo{random.randint(1, 2)}.gif").cqcode}',
    f'触发了奇怪的动画！\n{R.img("priconne/gachafail/naoyixue.gif").cqcode}',
    '为什么会失败呢？原因征集中！有好玩的脑洞请告诉蓝红心！',
    '为什么会失败呢？原因征集中！有好玩的脑洞请告诉蓝红心！'
]
GACHA_FAIL_NOTICE = f'\n抽卡失败了！\n{random.choice(FAIL_LIST)}\n本次抽卡无消耗'


gacha_10_aliases = ('pcr十连',)
gacha_1_aliases = ('pcr单抽',)
gacha_300_aliases = ('抽干家底', '砸井')

@sv.on_fullmatch(('卡池资讯', '查看卡池', '看看卡池', '康康卡池', '卡池資訊', '看看up', '看看UP'), only_to_me=True)
async def gacha_info(bot, ev: CQEvent):
    gid = str(ev.group_id)
    gacha = Gacha(_group_pool[gid])
    up_chara = gacha.up
    if sv.bot.config.USE_CQPRO:
        up_chara = map(lambda x: str(
            chara.fromname(x, star=3).icon.cqcode) + x, up_chara)
    up_chara = '\n'.join(up_chara)
    await bot.send(ev, f"本期卡池主打的角色：\n{up_chara}\nUP角色合计={(gacha.up_prob/10):.1f}% 3★出率={(gacha.s3_prob)/10:.1f}%")


async def check_if_fail(bot, ev: CQEvent, p):
    if random.random() < p:
        await bot.finish(ev, GACHA_FAIL_NOTICE, at_sender=True)

@sv.on_prefix(gacha_1_aliases, only_to_me=True)
async def gacha_1(bot, ev: CQEvent):

    await check_jewel_num(bot, ev)
    await check_if_fail(bot, ev, 0.1)
    jewel_limit.increase(ev.user_id, 150)

    gid = str(ev.group_id)
    gacha = Gacha(_group_pool[gid])
    chara, hiishi = gacha.gacha_one(gacha.up_prob, gacha.s3_prob, gacha.s2_prob)
    if 100 == hiishi:
        silence_time = 5 * 60
    elif 50 == hiishi:
        silence_time = 1 * 60
    else:
        silence_time = 0

    res = f'{chara.name} {"★"*chara.star}'
    if sv.bot.config.USE_CQPRO:
        res = f'{chara.icon.cqcode} {res}'
    if silence_time:
        await silence(ev, silence_time, skip_su=False)
    await bot.send(ev, f'素敵な仲間が増えますよ！\n{res}', at_sender=True)


@sv.on_prefix(gacha_10_aliases, only_to_me=True)
async def gacha_10(bot, ev: CQEvent):
    SUPER_LUCKY_LINE = 170

    await check_jewel_num(bot, ev)
    await check_if_fail(bot, ev, 0.15)
    jewel_limit.increase(ev.user_id, 1500)

    gid = str(ev.group_id)
    gacha = Gacha(_group_pool[gid])
    result, hiishi, count = gacha.gacha_ten()
    up = count['up']
    s3 = count['s3']
    s2 = count['s2']
    s1 = count['s1']
    silence_time = (5*up+s3) * 60 if hiishi < SUPER_LUCKY_LINE else (5 * up + s3) * 120

    if sv.bot.config.USE_CQPRO:
        res1 = chara.gen_team_pic(result[:5], star_slot_verbose=False)
        res2 = chara.gen_team_pic(result[5:], star_slot_verbose=False)
        res3 = f'{up + s3}虹{s2}金{s1}银，{up}up'
        res = concat_pic([res1, res2])
        res = pic2b64(res)
        res = MessageSegment.image(res)
        result = [f'{c.name}{"★"*c.star}' for c in result]
        res1 = ' '.join(result[0:5])
        res2 = ' '.join(result[5:])
        res = f'{res}\n{res3}\n{res1}\n{res2}'
    else:
        result = [f'{c.name}{"★"*c.star}' for c in result]
        res1 = ' '.join(result[0:5])
        res2 = ' '.join(result[5:])
        res = f'{res1}\n{res2}'

    if hiishi >= SUPER_LUCKY_LINE:
        await bot.send(ev, '恭喜海豹！おめでとうございます！')
    await bot.send(ev, f'素敵な仲間が増えますよ！\n{res}\n', at_sender=True)
    if silence_time:
        await silence(ev, silence_time, skip_su=False)


@sv.on_prefix(gacha_300_aliases, only_to_me=True)
async def gacha_300(bot, ev: CQEvent):

    await check_tenjo_num(bot, ev)
    await check_if_fail(bot, ev, 0.2)
    tenjo_limit.increase(ev.user_id)

    gid = str(ev.group_id)
    gacha = Gacha(_group_pool[gid])
    result = gacha.gacha_tenjou()
    up = len(result['up'])
    s3 = len(result['s3'])
    s2 = len(result['s2'])
    s1 = len(result['s1'])

    res = [*(result['up']), *(result['s3'])]
    random.shuffle(res)
    lenth = len(res)
    if lenth <= 0:
        res = "竟...竟然没有3★？！"
    else:
        step = 4
        pics = []
        for i in range(0, lenth, step):
            j = min(lenth, i + step)
            pics.append(chara.gen_team_pic(res[i:j], star_slot_verbose=False))
        res = concat_pic(pics)
        res = pic2b64(res)
        res = MessageSegment.image(res)

    msg = [
        f"\n素敵な仲間が増えますよ！ {res}",
        f"★★★×{up+s3} ★★×{s2} ★×{s1}",
        f"获得记忆碎片×{100*up}与女神秘石×{50*(up+s3) + 10*s2 + s1}！\n第{result['first_up_pos']}抽首次获得up角色" if up else f"获得女神秘石{50*(up+s3) + 10*s2 + s1}个！"
    ]

    if up == 0 and s3 == 0:
        msg.append("太惨了，主さま咱们还是退款删游吧...")
    elif up == 0 and s3 > 7:
        msg.append("up呢？我的up呢？")
    elif up == 0 and s3 <= 3:
        msg.append("主さま，梦幻包考虑一下？我会更加努力的打工的！")
    elif up == 0:
        msg.append("据说天井的概率只有12.16%")
    elif up <= 2:
        if result['first_up_pos'] < 50:
            msg.append("主さま,可不要随便向伙伴分享这次结果哦，会伤到运气不佳的伙伴的")
        elif result['first_up_pos'] < 100:
            msg.append("已经可以了，主さま已经很欧了")
        elif result['first_up_pos'] > 290:
            msg.append("标 准 结 局")
        elif result['first_up_pos'] > 250:
            msg.append("补井还是不补井，这是一个问题...")
        else:
            msg.append("期望之内，亚洲水平")
    elif up == 3:
        msg.append("抽井母五一气呵成！多出30等专武～")
    elif up >= 4:
        msg.append("记忆碎片一大堆！您是托吧？")

    await bot.send(ev, '\n'.join(msg), at_sender=True)
    if s3 < 7:
        silence_time = (120*up + 60*(up+s3)) * up
    else:
        silence_time = (120*up + 60*(up+s3)) * (up + 1)
    if silence_time:
        await silence(ev, silence_time, skip_su=False)


@sv.on_prefix('氪金', only_to_me=True)
async def kakin(bot, ev: CQEvent):
    if ev.user_id not in bot.config.SUPERUSERS or bot.config.PYUSERS:
        return
    count = 0
    for m in ev.message:
        if m.type == 'at' and m.data['qq'] != 'all':
            uid = int(m.data['qq'])
            jewel_limit.reset(uid)
            tenjo_limit.reset(uid)
            count += 1
    if count:
        await bot.send(ev, f"已为{count}位用户充值完毕！谢谢惠顾～")
