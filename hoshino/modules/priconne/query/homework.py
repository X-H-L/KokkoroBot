import time
import os.path
import peewee as pw
from nonebot import get_bot
from nonebot import CommandSession, MessageSegment, on_command
from nonebot.argparse import ArgumentParser
from nonebot import permission as perm
import re
import aiohttp
import nonebot
import asyncio
from hoshino import Service, priv
from hoshino.typing import CQEvent, CQHttpError
answers = {}
sv = Service('homework', manage_priv=priv.ADMIN, enable_on_default=False, help_='''
作业系统
[我问xxx你答yyy]
每个人每个群数据独立，可以用来存东西（bushi），支持图片
[不要回答xxx]'''.strip())
db = pw.SqliteDatabase(
    os.path.join(os.path.dirname(__file__), 'Homework.db')
)


class Homework(pw.Model):
    Boss = pw.IntegerField(default=0)
    titel = pw.TextField()
    content = pw.TextField()
    group = pw.IntegerField(default=0)  # 0 for none and 1 for all
    if_auto = pw.BooleanField(default=False)
    if_dream = pw.BooleanField(default=False)
    if_hide = pw.BooleanField(default=False)
    hide_reason = pw.TextField(default='')
    like = pw.IntegerField(default=0)
    dislike = pw.IntegerField(default=0)
    creator = pw.IntegerField()
    create_time = pw.TimestampField()

    class Meta:
        database = db


class MYfavor(pw.Model):
    likeid = pw.IntegerField(default=0)
    Boss = pw.IntegerField(default=0)
    user_id = pw.IntegerField()
    if_auto = pw.BooleanField(default=False)
    if_dream = pw.BooleanField(default=False)

    class Meta:
        database = db

@sv.on_prefix('把库扬了', only_to_me=True)
async def shanku(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.SUPERUSER):
        return
    Homework.delete().execute()
    MYfavor.delete().execute()
    await bot.send(ev, '已删库')

@sv.on_prefix('上传作业', only_to_me=True)
async def writehomework(bot, ev: CQEvent):
    msg = ev.message
    msgs = str(ev.raw_message)
    matchObj = re.match(r'^.*上传作业([a12345一二三四五])?w?王?(自动|auto|Auto)?(追梦|挂树|春黑)?刀?/([^/]+)/((.|\n|\r)+)$', msgs)
    if matchObj is not None:
        bid = matchObj.group(1)
        ifauto = False
        ifdream = False
        if bid is None:
            bid = 0
        elif bid in '1一':
            bid = 1
        elif bid in '2二':
            bid = 2
        elif bid in '3三':
            bid = 3
        elif bid in '4四':
            bid = 4
        elif bid in '5五':
            bid = 5
        else:
            bid = 0
        if matchObj.group(2) is not None:
            ifauto = True
        if matchObj.group(3) is not None:
            ifdream = True
        workid = Homework.insert(
            Boss=bid,
            titel=matchObj.group(4),
            content=matchObj.group(5),
            group=0,  # 0 for none and 1 for all
            if_auto=ifauto,
            if_dream=ifdream,
            creator=ev.user_id,
            create_time=time.time()
        ).execute()
        for i in msg:
            if i['type'] == 'image':
                await bot.get_image(file=i['data']['file'])
        await bot.send(ev, f'上传成功，作业编号{workid}')
    else:
        await bot.send(ev, '格式好像不太对，再去看看帮助？')

TIPs='''Tips:
发送#查作业 -i <作业id>查看作业详细内容
默认查询不追梦作业，如果想看追梦作业请加参数-d
如果想只看auto作业请加参数 -a'''
@on_command('查作业', shell_like=True, only_to_me=True)
async def lookhomework(session: CommandSession):
    parser = ArgumentParser(session=session)
    parser.add_argument('-b', '--boss', type=int, default=0, help='查这个boss有哪些作业')
    parser.add_argument('-a', '--auto', action='store_true', help='是否只看auto')
    parser.add_argument('-d', '--dream', action='store_true', help='是否查看追梦作业')
    parser.add_argument('-H', '--Hiden', action='store_true', help='查看被隐藏作业')  
    parser.add_argument('-i', '--id', type=int, default=0, help='看这个作业')
    args = parser.parse_args(session.argv)
    if session.ctx.detail_type == 'group':
        if not sv.check_enabled(session.ctx['group_id']):
            return
    msg = []
    if args.id:
        homework = Homework.get_or_none(id=args.id)
        if homework is not None:
            msg.append(f'{str(homework.Boss)}王：')
            msg.append(homework.titel)
            x = '○' if homework.if_auto else '×'
            msg.append(f"auto:{x}")
            x = '○' if homework.if_dream else '×'
            msg.append(f"追梦:{x}")
            if homework.if_hide:
                msg.append('======\n⚠该作业已被隐藏！')
                msg.append(f'隐藏原因：{homework.hide_reason}\n======')
            msg.append(homework.content)
            try:
                infoget = await session.bot.get_stranger_info(user_id=homework.creator)
                nickname = infoget['nickname']
            except CQHttpError:
                nickname = '未知'
            msg.append(f'上传者：{nickname}')
            msg.append(f'👍赞：{str(homework.like)} 👎踩：{str(homework.dislike)}')
        else:
            msg.append('没有找到该作业')
    elif args.Hiden:
        workget = Homework.select().where(
                Homework.if_hide == True
            ).order_by(Homework.Boss)
        count = 0
        for m in workget:
            count += 1
            msg.append(f'=========\n{str(m.Boss)}王：')
            msg.append(f'作业id：{m.id}')
            msg.append(m.titel)
            x = '○' if m.if_auto else '×'
            msg.append(f"auto:{x}")
            x = '○' if m.if_dream else '×'
            msg.append(f"追梦:{x}")
            try:
                infoget = await session.bot.get_stranger_info(user_id=m.creator)
                nickname = infoget['nickname']
            except CQHttpError:
                nickname = '未知'
            msg.append(f'上传者：{nickname}')
            msg.append(f'隐藏原因：{m.hide_reason}')
        if not count:
            msg.append('没有被隐藏的作业')
    else:
        if not args.boss:
            workget = Homework.select().where(
                Homework.Boss == 0,
                Homework.if_hide == False
            ).execute()
            count = 0
            msg.append(f'一图流作业：')
            for m in workget:
                count += 1
                msg.append(f'=========\n作业id：{m.id}')
                msg.append(m.titel)
                try:
                    infoget = await session.bot.get_stranger_info(user_id=m.creator)
                    nickname = infoget['nickname']
                except CQHttpError:
                    nickname = '未知'
                msg.append(f'上传者：{nickname}')
                msg.append(f'👍赞：{str(m.like)} 👎踩：{str(m.dislike)}')
            if count:
                msg.append('=========')
            else:
                msg.append(f'没有找到作业x')
            msg.append(TIPs)
            session.finish('\n'.join(msg))
        if args.auto and args.dream:
            workget = Homework.select().where(
                Homework.Boss == args.boss,
                Homework.if_auto == True,
                Homework.if_hide == False
            ).execute()
        elif args.auto:
            workget = Homework.select().where(
                Homework.Boss == args.boss,
                Homework.if_auto == True,
                Homework.if_dream == False,
                Homework.if_hide == False
            ).execute()
        elif args.dream:
            workget = Homework.select().where(
                Homework.Boss == args.boss,
                Homework.if_hide == False
            ).execute()
        else:
            workget = Homework.select().where(
                Homework.Boss == args.boss,
                Homework.if_dream == False,
                Homework.if_hide == False
            ).execute()
        count = 0
        msg.append(f'{args.boss}王作业：')
        for m in workget:
            count += 1
            msg.append(f'=========\n作业id：{m.id}')
            msg.append(m.titel)
            x = '○' if m.if_auto else '×'
            msg.append(f"auto:{x}")
            x = '○' if m.if_dream else '×'
            msg.append(f"追梦:{x}")
            try:
                infoget = await session.bot.get_stranger_info(user_id=m.creator)
                nickname = infoget['nickname']
            except CQHttpError:
                nickname = '未知'
            msg.append(f'上传者：{nickname}')
            msg.append(f'👍赞：{str(m.like)} 👎踩：{str(m.dislike)}')
        if count:
            msg.append(f'=========\n{TIPs}')
        else:
            msg.append(f'没有找到作业x\n{TIPs}')
    await session.send('\n'.join(msg))

@sv.on_prefix('赞作业', only_to_me=True)
async def homework_like(bot, ev):
    await _homework_feedback(bot, ev, 1)

@sv.on_prefix('踩作业', only_to_me=True)
async def homework_dislike(bot, ev):
    await _homework_feedback(bot, ev, -1)

rex_qkey = re.compile(r'^[0-9]+$')
async def _homework_feedback(bot, ev: CQEvent, action: int):
    action_tip = '赞' if action > 0 else '踩'
    qkey = ev.message.extract_plain_text().strip()
    if not qkey:
        await bot.finish(ev, f'请发送"#{action_tip}作业+作业id"，如"#{action_tip}作业1"', at_sender=True)
    if not rex_qkey.match(qkey):
        await bot.finish(ev, f'您要点{action_tip}的作业id不合法', at_sender=True)
    try:
        homework = Homework.get_or_none(id=int(qkey))
        if homework is not None:
            if action > 0:
                homework.like += 1
            else:
                homework.dislike += 1
            homework.save()
            await bot.send(ev, '感谢您的反馈！', at_sender=True)
        else:
            bot.finish(ev, '没有找到这个作业')
    except KeyError:
        await bot.finish(ev, '好像出错了，可是为啥', at_sender=True)


rex_hkey = re.compile(r'^([0-9]+)(原因[:：]?(.+))?$')
@sv.on_prefix('隐藏作业', only_to_me=True)
async def hide_homework(bot, ev):
    hkey = ev.message.extract_plain_text().strip()
    if not hkey:
        await bot.finish(ev, '请发送"#隐藏作业+作业id(+原因：xxx)"，如"#隐藏作业1原因：已有优化版本"，原因可省略', at_sender=True)
    match = rex_hkey.match(hkey)
    if not match:
        await bot.finish(ev, '您要隐藏的作业id或原因的格式不合法', at_sender=True)
    try:
        homework = Homework.get_or_none(id=int(match.group(1)))
        if homework is not None:
            if ev.user_id != homework.creator and not priv.check_priv(ev, priv.ADMIN):
                await bot.finish(ev, '作业上传者或管理员才可以隐藏作业')
            homework.if_hide = True
            if match.group(3) is not None:
                homework.hide_reason = match.group(3)
            homework.save()
        else:
            bot.finish(ev, '没有找到这个作业')
    except KeyError:
        await bot.finish(ev, '好像出错了，可是为啥', at_sender=True)
    await bot.send(ev, '已隐藏', at_sender=True)

@on_command('收藏作业', shell_like=True, only_to_me=True)
async def favor_homework(session: CommandSession):
    parser = ArgumentParser(session=session)
    parser.add_argument('-i', '--id', type=int, default=0, help='要收藏的作业序号')
    args = parser.parse_args(session.argv)
    if session.ctx.detail_type == 'group':
        if not sv.check_enabled(session.ctx['group_id']):
            return
    if not args.id:
        await session.finish('Usage: -i|--id <homework_id>')
    homework = Homework.get_or_none(id=args.id)
    if homework is not None:
        if homework.if_hide:
            await session.finish('这个作业被隐藏了哦')
        if MYfavor.get_or_none(MYfavor.user_id == session.ctx['user_id'], MYfavor.likeid == args.id) is not None:
            await session.finish('已经添加过啦')
        MYfavor.insert(
            Boss=homework.Boss,
            if_auto=homework.if_auto,
            if_dream=homework.if_dream,
            user_id=session.ctx['user_id'],
            likeid=homework.id
        ).execute()
        await session.send('已收藏')
    else:
        await session.finish('没有找到这个作业')


@on_command('我的收藏', shell_like=True, only_to_me=True)
async def look_favorwork(session: CommandSession):
    parser = ArgumentParser(session=session)
    parser.add_argument('-b', '--boss', type=int, default=-1, help='查这个boss有哪些作业')
    parser.add_argument('-a', '--auto', action='store_true', help='是否只看auto')
    parser.add_argument('-d', '--dream', action='store_true', help='是否查看追梦作业')
    args = parser.parse_args(session.argv)
    if session.ctx.detail_type == 'group':
        if not sv.check_enabled(session.ctx['group_id']):
            return
    msg = []
    count = 0
    for favor in MYfavor.select().where(MYfavor.user_id == session.ctx['user_id']).order_by(MYfavor.Boss):
        if args.auto and not favor.if_auto:
            continue
        if not args.dream and favor.if_dream:
            continue
        homework = Homework.get_or_none(id=favor.likeid)
        if homework is not None:
            if args.boss != -1 and args.boss != homework.Boss:
                continue
            if homework.if_hide:
                continue
            count += 1
            msg.append('========')
            if homework.Boss > 0:
                msg.append(f'{str(homework.Boss)}王：')
                msg.append(homework.titel)
                x = '○' if homework.if_auto else '×'
                msg.append(f"auto:{x}")
                x = '○' if homework.if_dream else '×'
                msg.append(f"追梦:{x}")
            else:
                msg.append('一图流：')
            msg.append(homework.content)
            try:
                infoget = await session.bot.get_stranger_info(user_id=homework.creator)
                nickname = infoget['nickname']
            except CQHttpError:
                nickname = '未知'
            msg.append(f'上传者：{nickname}')
            msg.append(f'👍赞：{str(homework.like)} 👎踩：{str(homework.dislike)}')
    if not count:
        msg.append('什么也没有查到')
    msg.append('默认查询不追梦作业，如果想看追梦作业请加参数-d\n如果想只看auto作业请加参数 -a')
    await session.send('\n'.join(msg))


@on_command('取消收藏', shell_like=True, only_to_me=True)
async def favor_homework(session: CommandSession):
    parser = ArgumentParser(session=session)
    parser.add_argument('-i', '--id', type=int, default=0, help='要取消收藏的作业序号')
    args = parser.parse_args(session.argv)
    if session.ctx.detail_type == 'group':
        if not sv.check_enabled(session.ctx['group_id']):
            return
    if not args.id:
        await session.finish('Usage: -i|--id <homework_id>')
    if MYfavor.get_or_none(MYfavor.user_id == session.ctx['user_id'], MYfavor.likeid == args.id) is not None:
        MYfavor.delete().where(MYfavor.user_id == session.ctx['user_id'], MYfavor.likeid == args.id).execute()
        await session.send('已取消收藏')
    else:
        await session.finish('没有找到这个收藏')

Homeworkhelp='''这是帮助手册）
注意空格注意空格，那几个允许私聊的指令，指令的每一部分都需要空格隔开
========
#上传作业[作业基本情况]/[作业简单描述]/[作业内容]
这个指令只能群聊使用
作业基本情况可以为空，为空视作一图流作业
作业基本情况的格式是boss序号+auto（如果是auto）+追梦（如果是追梦）
eg：“一王”指一王手动不追梦作业，“一王auto”指一王auto稳定作业
作业简单描述不能为空，不能含有“/”，请写一下配队和预期伤害之类的，一图流就写一下来源
作业内容就是具体内容，这部分可以带图
========
#查作业
⚠这个指令可以私聊，私聊时不需要前缀
参数介绍：
-h 简单帮助
-b <boss_id> 看哪个boss的作业的索引，不指定将查询一图流
-a 是否只看auto
-d 是否看追梦作业
-i <homework_id> 查看这个编号的作业的具体内容
使用例子：
#查作业 -i 1 查看1号作业具体内容
#查作业 -b 1 查看1王作业索引
先查索引，根据索引提供的id查看具体内容
========
#隐藏作业+作业序号（+原因：xxx）
这个指令只能群聊使用
隐藏指定作业，因为修改很麻烦，直接隐藏原来的上传一个新的吧
只有上传者和管理员可以隐藏
原因可以不加
========
#赞作业+序号
#踩作业+序号
评价作业
========
#收藏作业 -i <homework_id>
⚠这个指令可以私聊，私聊时不加前缀
收藏指定序号的作业
========
#我的收藏
⚠这个指令可以私聊，私聊时不加前缀
无参数时显示所有收藏的作业的信息和内容
也可以加一些限制参数
-b 看哪个boss 设为0是一图流
-a,-d作用同查作业的-a和-d
========
#取消收藏 -i <homework_id>
⚠这个指令可以私聊，私聊时不加前缀
取消这个收藏'''

@on_command('help作业', only_to_me=True)
async def helphomework(session: CommandSession):
    await session.send(Homeworkhelp)

def init():
    if not os.path.exists(os.path.join(os.path.dirname(__file__), 'Homework.db')):
        db.connect()
        db.create_tables([Homework])
        db.create_tables([MYfavor])
        db.close()


init()
