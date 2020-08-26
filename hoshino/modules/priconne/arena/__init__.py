import re
import time
from collections import defaultdict

import hoshino
from hoshino import Service, R
from hoshino.typing import *
from hoshino.util import FreqLimiter, concat_pic, pic2b64

from .. import chara

sv_help = '''
[@怎么拆] 接防守队角色名 查询竞技场解法，加上地区前缀可以过滤，如台怎么拆
[@点赞] 接作业id 评价作业
[@点踩] 接作业id 评价作业
'''.strip()
sv = Service('pcr-arena', help_=sv_help, bundle='pcr查询')

from . import arena

lmt = FreqLimiter(5)

sorrypic = R.img('kkl/》《.jpg').cqcode
sorrypicgif = R.img('kkl/》《.gif').cqcode
jjcerror = R.img('jjcerror.jpg').cqcode

aliases = ('怎么拆', '怎么解', '怎么打', '如何拆', '如何解', '如何打', 'jjc查询')
aliases_b = tuple('b' + a for a in aliases) + tuple('B' + a for a in aliases)
aliases_tw = tuple('台' + a for a in aliases)
aliases_jp = tuple('日' + a for a in aliases)

@sv.on_prefix(aliases, only_to_me=True)
async def arena_query(bot, ev):
    await _arena_query(bot, ev, region=1)

@sv.on_prefix(aliases_b, only_to_me=True)
async def arena_query_b(bot, ev):
    await _arena_query(bot, ev, region=2)

@sv.on_prefix(aliases_tw, only_to_me=True)
async def arena_query_tw(bot, ev):
    await _arena_query(bot, ev, region=3)

@sv.on_prefix(aliases_jp, only_to_me=True)
async def arena_query_jp(bot, ev):
    await _arena_query(bot, ev, region=4)



async def _arena_query(bot, ev: CQEvent, region: int):
    #await bot.finish(ev, f'{jjcerror}\n站长把key回收了，功能暂时无法使用，请自行去网站查询\n公主连接Re:Dive 竞技场编成数据库\n日文：https://nomae.net/arenadb \n中文：https://pcrdfans.com/battle', at_sender=True)
    arena.refresh_quick_key_dic()
    uid = ev.user_id

    if not lmt.check(uid):
        await bot.finish(ev, f'主人您查询得太快了，在下已经跟不上了><\n{sorrypicgif}', at_sender=True)
    lmt.start_cd(uid)

    # 处理输入数据
    defen = ev.message.extract_plain_text()
    defen = re.sub(r'[?？，,_]', '', defen)
    defen, unknown = chara.roster.parse_team(defen)

    if unknown:
        _, name, score = chara.guess_id(unknown)
        if score < 70 and not defen:
            return  # 忽略无关对话
        msg = f'唔……在下并不记得有叫"{unknown}"的伙伴呢\n有想补充的昵称可以通过[@来杯咖啡]指令登记一下，说清楚是给谁' if score < 70 else f'唔……“{unknown}”？ 请问主人指的是{name}吗（{score}%）'
        await bot.finish(ev, msg)
    if not defen:
        await bot.finish(ev, '查询请发送"怎么拆+防守队伍"，无需+号', at_sender=True)
    if len(defen) > 5:
        await bot.finish(ev, '编队不能多于5名角色哦', at_sender=True)
    if len(defen) < 5:
        await bot.finish(ev, '由于数据库限制，少于5名角色的检索条件请移步pcrdfans.com进行查询', at_sender=True)
    if len(defen) != len(set(defen)):
        await bot.finish(ev, '编队中含重复角色哦', at_sender=True)
    if any(chara.is_npc(i) for i in defen):
        await bot.finish(ev, '编队中含未实装角色哦', at_sender=True)
    if 1004 in defen:
        await bot.send(ev, '\n⚠️主人正在查询普通版炸弹人哦\n※万圣版可用万圣炸弹人/瓜炸等别称', at_sender=True)

    # 执行查询
    sv.logger.info('Doing query...')
    res = await arena.do_query(defen, uid, region)
    sv.logger.info('Got response!')

    # 处理查询结果
    if res is None:
        await bot.finish(ev, f'查询出错，请联系维护组调教><\n{sorrypicgif}\n请先移步pcrdfans.com进行查询', at_sender=True)
    if not len(res):
        await bot.finish(ev, f'抱歉没有查询到解法><\n{sorrypic}\n※没有作业说明随便拆 发挥你的想象力～★\n作业上传请前往pcrdfans.com', at_sender=True)
    res = res[:min(6, len(res))]    # 限制显示数量，截断结果

    # 发送回复
    sv.logger.info('Arena generating picture...')
    atk_team = [ chara.gen_team_pic(entry['atk']) for entry in res ]
    atk_team = concat_pic(atk_team)
    atk_team = pic2b64(atk_team)
    atk_team = str(MessageSegment.image(atk_team))
    sv.logger.info('Arena picture ready!')
    # 纯文字版
    # atk_team = '\n'.join(map(lambda entry: ' '.join(map(lambda x: f"{x.name}{x.star if x.star else ''}{'专' if x.equip else ''}" , entry['atk'])) , res))

    details = [ " ".join([
        f"赞{e['up']}+{e['my_up']}" if e['my_up'] else f"赞{e['up']}",
        f"踩{e['down']}+{e['my_down']}" if e['my_down'] else f"踩{e['down']}",
        e['qkey'],
        "主人曾经赞过" if e['user_like'] > 0 else "主人曾经踩过" if e['user_like'] < 0 else ""
    ]) for e in res ]

    defen = [ chara.fromid(x).name for x in defen ]
    defen = f"防守方【{' '.join(defen)}】"
    at = str(MessageSegment.at(ev.user_id))

    msg = [
        defen,
        f'已为主人{at}查询到以下进攻方案：',
        str(atk_team),
        f'作业评价：',
        *details,
        '※发送"#点赞/点踩"可进行评价'
    ]
    if region == 1:
        msg.append('※使用"b怎么拆"或"台怎么拆"可按服过滤')
    msg.append('Support by pcrdfans_com')

    sv.logger.debug('Arena sending result...')
    await bot.send(ev, '\n'.join(msg))
    sv.logger.debug('Arena result sent!')


@sv.on_prefix('点赞', only_to_me=True)
async def arena_like(bot, ev):
    await _arena_feedback(bot, ev, 1)


@sv.on_prefix('点踩', only_to_me=True)
async def arena_dislike(bot, ev):
    await _arena_feedback(bot, ev, -1)


rex_qkey = re.compile(r'^[0-9a-zA-Z]{5}$')
async def _arena_feedback(bot, ev: CQEvent, action:int):
    action_tip = '赞' if action > 0 else '踩'
    qkey = ev.message.extract_plain_text().strip()
    if not qkey:
        await bot.finish(ev, f'请发送"#点{action_tip}+作业id"，如"#点{action_tip}ABCDE"，不分大小写', at_sender=True)
    if not rex_qkey.match(qkey):
        await bot.finish(ev, f'您要点{action_tip}的作业id不合法', at_sender=True)
    try:
        await arena.do_like(qkey, ev.user_id, action)
    except KeyError:
        await bot.finish(ev, '在下找到的作业里好像没有这个id呢，主人只能评价您最近查询过的作业哦', at_sender=True)
    await bot.send(ev, '感谢您的反馈！', at_sender=True)
