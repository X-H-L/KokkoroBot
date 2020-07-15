import time
import os.path
import peewee as pw
from nonebot import get_bot
from nonebot import CommandSession, MessageSegment
from nonebot import permission as perm
import re
import aiohttp
import nonebot
import asyncio
''' from .data import Question '''
from hoshino import Service, priv
answers = {}
sv = Service('QA', manage_priv=priv.ADMIN, enable_on_default=False, help_='''
我问你答
[我问xxx你答yyy]
每个人每个群数据独立，可以用来存东西（bushi），支持图片
[不要回答xxx]'''.strip())
db = pw.SqliteDatabase(
    os.path.join(os.path.dirname(__file__), 'qa.db')
)


class Question(pw.Model):
    quest = pw.TextField()
    answer = pw.TextField()
    rep_group = pw.IntegerField(default=0)  # 0 for none and 1 for all
    rep_member = pw.IntegerField(default=0)
    allow_private = pw.BooleanField(default=False)
    creator = pw.IntegerField()
    create_time = pw.TimestampField()

    class Meta:
        database = db
        primary_key = pw.CompositeKey('quest', 'rep_group', 'rep_member')



def union(group_id, user_id):
    return (group_id << 32) | user_id


# recovery from database
for qu in Question.select():
    if qu.quest not in answers:
        answers[qu.quest] = {}
    answers[qu.quest][union(qu.rep_group, qu.rep_member)] = qu.answer


async def get_image_from_msg(message: str):
    bot = nonebot.get_bot()
    async def download(url):
        try:
            save_path = os.path.join(bot.config.CQ_DATA_PATH,'image')
            filename = re.findall(r'(?<=-)[^-]*?(?=/)',url)[0]+'.jpg'
            filename = os.path.join(save_path,filename)
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with  session.get(url) as resp:
                    content = await resp.read()
                    with open(filename,'wb') as f:
                        f.write(content)
                        f.close()
        except Exception as ex:
            print(ex)
    url_list = re.findall(r'http.*?term=\d',message)
    for url in url_list:
        print('url',url)
        asyncio.run_coroutine_threadsafe(download(url),loop=bot.loop)

@sv.on_message('group')
async def handle(bot, context):
    message = context['raw_message']
    mssg = str(context['message'].copy())
    if message.startswith('我问'):
        msg = message[2:].split('你答', 1)
        if len(msg) == 1:
            await bot.send(context, '发送“我问xxx你答yyy”我才能记住', at_sender=False)
            return
        q, a = msg
        if q not in answers:
            answers[q] = {}
        answers[q][union(context['group_id'], context['user_id'])] = a
        Question.replace(
            quest=q,
            rep_group=context['group_id'],
            rep_member=context['user_id'],
            answer=a,
            creator=context['user_id'],
            create_time=time.time(),
        ).execute()
        await bot.send(context, f'好的我记住了', at_sender=False)
        await get_image_from_msg(mssg)
        return
    elif message.startswith('大家问') or message.startswith('有人问'):
        if not priv.check_priv(context, priv.SUPERUSER):
            await bot.send(context, f'只有管理员才可以用{message[:3]}', at_sender=False)
            return
        msg = message[3:].split('你答', 1)
        if len(msg) == 1:
            await bot.send(context, f'发送“{message[:3]}xxx你答yyy”我才能记住', at_sender=False)
            return
        q, a = msg
        if q not in answers:
            answers[q] = {}
        answers[q][union(context['group_id'], 1)] = a
        Question.replace(
            quest=q,
            rep_group=context['group_id'],
            rep_member=1,
            answer=a,
            creator=context['user_id'],
            create_time=time.time(),
        ).execute()
        await bot.send(context, f'好的我记住了', at_sender=False)
        await get_image_from_msg(mssg)
        return
    elif message.startswith('不要回答'):
        q = context['raw_message'][4:]
        ans = answers.get(q)
        if ans is None:
            await bot.send(context, f'我不记得有这个问题', at_sender=False)
            return

        specific = union(context['group_id'], context['user_id'])
        a = ans.get(specific)
        if a:
            Question.delete().where(
                Question.quest == q,
                Question.rep_group == context['group_id'],
                Question.rep_member == context['user_id'],
            ).execute()
            del ans[specific]
            if not ans:
                del answers[q]
            await bot.send(context, f'我不再回答“{a}”了', at_sender=False)
            return

        if not priv.check_priv(context, priv.SUPERUSER):
            await bot.send(context, f'只有管理员可以删除别人的问题', at_sender=False)
            return

        wild = union(context['group_id'], 1)
        a = ans.get(wild)
        if a:
            Question.delete().where(
                Question.quest == q,
                Question.rep_group == context['group_id'],
                Question.rep_member == 1,
            ).execute()
            del ans[wild]
            if not ans:
                del answers[q]
            await bot.send(context, f'我不再回答“{a}”了', at_sender=False)
            return
    elif message == ('查看qa') or message == ('查看QA'):
        if priv.check_priv(context, priv.SUPERUSER):
            gid = context.get('group_id',1)
            msg = [f"群{gid}问答一览："]
            i=0
            for b in Question.select().where(Question.rep_group == context['group_id']).order_by(Question.rep_member):
                i=i+1
                if b.rep_member == 1:
                    name = '有人问'
                else:
                    info = await bot.get_group_member_info(group_id=int(b.rep_group), user_id=int(b.rep_member))
                    await bot.send(context, str(info), at_sender=False)
                    name = info['card']
                    if name == '':
                        name = info['nickname']
                    name += '(' + str(info['user_id']) + ')'
                msg.append(f"{name}:{b.quest}|{b.answer}")  
                if i%10==0:
                    await bot.send(context, '\n'.join(msg), at_sender=False)
                    msg = [f"第{(i//10)+1}页："]
            await bot.send(context, '\n'.join(msg), at_sender=False)
            return

@sv.on_message('group')
async def answer(bot, context):
    ans = answers.get(context['raw_message'])
    if ans:
        # 回复优先级，有人问>我问
        a = ans.get(union(context['group_id'], 1))
        if a:
            await bot.send(context, f'{a}', at_sender=False)
            return
        else:
            a = ans.get(union(context['group_id'], context['user_id']))
            if a:
                await bot.send(context, f'{a}', at_sender=False)
                return

def init():
    if not os.path.exists(os.path.join(os.path.dirname(__file__), 'qa.db')):
        db.connect()
        db.create_tables([Question])
        db.close()


init()