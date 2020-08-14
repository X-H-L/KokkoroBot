import re
import math
import random
import hoshino
from aiocqhttp.exceptions import ActionFailed
from hoshino import Service, priv, util
from hoshino.typing import CQEvent
from nonebot.argparse import ArgumentParser
from nonebot import permission as perm
import nonebot
from nonebot import CommandSession, CQHttpError, on_command
from hoshino.util import DailyNumberLimiter
sv = Service('sleeping-set', help_='''
[@精致睡眠] 8小时精致睡眠(bot需具有群管理权限)
[@给我来一份精致昏睡下午茶套餐] 叫一杯先辈特调红茶(bot需具有群管理权限)
'''.strip())


svm = Service('sleeping-help', use_priv=priv.ADMIN, manage_priv=priv.PYUSER, visible=False, help_='睡眠管理（？）', bundle='master')

@sv.on_fullmatch(('睡眠套餐', '休眠套餐', '精致睡眠', '来一份精致睡眠套餐'), only_to_me=True)
async def sleep_8h(bot, ev):
    await util.silence(ev, 8*60*60, skip_su=False)


@sv.on_rex(r'(来|來)(.*(份|个)(.*)(睡|茶)(.*))套餐', only_to_me=True)
async def sleep(bot, ev: CQEvent):
    base = 0 if '午' in ev.plain_text else 5*60*60
    length = len(ev.plain_text)
    sleep_time = base + round(math.sqrt(length) * 60 * 30 + 60 * random.randint(-15, 15))
    await util.silence(ev, sleep_time, skip_su=False)


@svm.on_prefix('解禁', only_to_me=True)
async def not_sleep(bot, ev):
    if ev.user_id not in bot.config.SUPERUSERS or bot.config.PYUSERS:
        return
    count = 0
    for m in ev.message:
        if m.type == 'at' and m.data['qq'] != 'all':
            uid = int(m.data['qq'])
            try:
                await bot.set_group_ban(self_id=ev.self_id, group_id=ev.group_id, user_id=uid, duration=0)
            except ActionFailed as e:
                hoshino.logger.error(f'解禁失败 retcode={e.retcode}')
            except Exception as e:
                hoshino.logger.exception(e)
            count += 1
    if count:
        await bot.send(ev, f"已为{count}位用户解禁完毕！")


@svm.on_prefix('塞口球', only_to_me=True)
async def must_sleep(bot, ev):
    if ev.user_id not in bot.config.SUPERUSERS or bot.config.PYUSERS:  # master限定
        return
    msg = str(ev.message)
    matchObj = re.match(r'^\[CQ:at,qq=([0-9]+)\] ([0-9]+)个?小?([月星周zZ时分秒HMSDhmsd天]?)钟?期?$', msg)
    if matchObj is not None:
        uid = int(matchObj.group(1))
        if uid in bot.config.SUPERUSERS:
            return
        time = int(matchObj.group(2))
        danwei = matchObj.group(3)
        if not danwei or danwei in '秒sS':
            time = time * 1
        elif danwei in '分mM':
            time = time * 60
        elif danwei in '时hH':
            time = time * 3600
        elif danwei in '天dD':
            time = time * 3600 * 24
        elif danwei in '星周zZ':
            time = time * 3600 * 24 * 7
        elif danwei == '月':
            time = time * 3600 * 24 * 30
        else:
            pass
        try:
            await bot.set_group_ban(self_id=ev.self_id, group_id=ev.group_id, user_id=uid, duration=time)
        except ActionFailed as e:
            hoshino.logger.error(f'禁言失败 retcode={e.retcode}')
        except Exception as e:
            hoshino.logger.exception(e)


lmt = DailyNumberLimiter(1)
@on_command('我不睡了', aliases=('清醒套餐',), permission=perm.PRIVATE, shell_like=True)
async def notwantsleep(session: CommandSession):
    parser = ArgumentParser(session=session)
    parser.add_argument('-g', '--group', type=int, default=0)
    args = parser.parse_args(session.argv)
    ctx = session.ctx
    bot = hoshino.get_bot()
    user_id = ctx['user_id']
    if user_id in priv._black_user:
        return
    if not lmt.check(user_id):
        await session.finish('今天份的清醒套餐已经用掉了哦')
    self_id = ctx["self_id"]
    gid = args.group
    if not gid:
        session.finish('Usage: -g|--group <group_id>, eg:清醒套餐 -g 123456')
    gl = await bot.get_group_list(self_id=self_id)
    allgid = ["{group_id}".format_map(g) for g in gl]
    if str(gid) not in allgid:
        session.finish('唔姆···是在下不知道的群呢')
    self_info = await bot.get_group_member_info(
        group_id=gid,
        user_id=self_id,
    )
    member_list = await bot.get_group_member_list(self_id=self_id, group_id=gid)
    finduser = 0
    for member in member_list:
        if user_id == member['user_id']:
            finduser = 1
            userrole = member['role']
            break
    if finduser:
        if userrole == 'owner':
            session.finish('?')
        elif self_info['role'] == 'member' or (self_info['role'] == userrole):
            session.finish('唔姆···在下也无能为力呢')
        else:
            try:
                await bot.set_group_ban(self_id=self_id, group_id=gid, user_id=user_id, duration=0)
            except ActionFailed as e:
                hoshino.logger.error(f'解禁失败 retcode={e.retcode}')
            except Exception as e:
                hoshino.logger.exception(e)
            if user_id not in bot.config.SUPERUSERS:
                lmt.increase(user_id)
            session.finish('清醒套餐使用成功！')
    else:
        session.finish('唔姆···你好像不在这个群里呢')
