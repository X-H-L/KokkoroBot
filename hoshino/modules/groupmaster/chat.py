import random
import requests
import pytz
import json
import os
from datetime import datetime
from nonebot import on_command, CommandSession
from urllib import parse
from hoshino import R, Service, priv, util


# basic function for debug, not included in Service('chat')
@on_command('zai?', aliases=('在?', '在？', '在吗', '在么？', '在嘛', '在嘛？'), only_to_me=True)
async def say_hello(session):
    await session.send('はい！私はいつも貴方の側にいますよ！')


sv = Service('chat', visible=False)
svc = Service('choseone', help_='''拯救选择恐惧症！
[@选择A还是B]帮你做出选择''')
svb = Service('howtobaidu', help_='''拯救懒人群友！
[@百度xxx]让可可萝教你百度xxx''')
svn = Service('nbnhhsh', help_='''能不能好好说话！
[@??]翻译缩写
eg:#??pcr''')
tz = pytz.timezone('Asia/Shanghai')


# =====================prefix======================= #


@svc.on_prefix('选择', only_to_me=True)
async def choseone(bot, ev):
    kw = ev.message.extract_plain_text().strip()
    arr = kw.split('还是')
    arr = [i for i in arr if i != '']
    if len(arr) > 1:
        msg = []
        msg.append('')
        count = 1
        for i in arr:
            if len(i) > 0:
                msg.append(f'{count}，{i}')
                count += 1
        msg.append(f'选择：{random.choice(arr)}')
        await bot.send(ev, '\n'.join(msg), at_sender=True)


@svb.on_prefix('百度', only_to_me=True)
async def howtobaidu(bot, ev):
    msg = []
    kw = ev.message.extract_plain_text().strip()
    if kw == '':
        return
    baiduurl = 'http://api.goubibei.com/baidu/?'
    shorturl = 'http://api.wx.urlfh.com/dwz.php?type=qq&longurl='
    msg.append(f'\n可可罗教你怎么百度{kw}哦')
    data = {
        "kw": kw
    }
    kw = parse.urlencode(data)
    url = baiduurl + kw[3:]
    surl = shorturl + url
    resp = requests.get(surl, timeout=5)
    if resp.status_code == requests.codes.ok:
        res = resp.json()
        if res['code'] == 1:
            if res['ae_url'] is None:
                url = res['longurl']
            else:
                url = res['ae_url']
    msg.append(url)
    await bot.send(ev, '\n'.join(msg), at_sender=True)


@svn.on_suffix(('是啥', '是啥啊', '是啥？', '是啥啊？'), only_to_me=True)
@svn.on_prefix(('??', '？？', '啥是'), only_to_me=True)
async def nbnhhsh(bot, ev):
    kw = ev.message.extract_plain_text().strip()
    if len(kw) > 1 and kw.isalnum():
        body = {"text": kw}
        resp = requests.post(
            'https://lab.magiconch.com/api/nbnhhsh/guess/',
            data=body,
            timeout=5
            )
        if resp.status_code == requests.codes.ok:
            res = resp.json()
            if 'trans' in res[0]:
                msg = f'"{kw}"可能是：\n'+' '.join(res[0]['trans'])
                await bot.send(ev, msg)
            else:
                await bot.send(ev, 'emm...在下也猜不透它的意思')
        else:
            svn.logger.error('查询失败')


@sv.on_prefix(('人生解答', '答案之书'), only_to_me=True)
async def chat_answer(bot, ev):
    try:
        with open(os.path.join(os.path.dirname(__file__), 'data/chat.json'), 'r', encoding='utf8') as f:
            answers = json.load(f)["Theanswer"]
            await bot.send(ev, random.choice(answers), at_sender=True)
    except:
        sv.logger.error('chat_answer读json出错')
        return


# =====================fullmatch======================= #


@sv.on_fullmatch(('沙雕机器人', '垃圾机器人', '辣鸡机器人'))
async def say_sorry(bot, ev):
    await bot.send(ev, 'ごめんなさい！嘤嘤嘤(>……<)')
    await bot.send(ev, R.img('kkl/》《.gif').cqcode)


@sv.on_fullmatch(('老婆', 'waifu', 'laopo'), only_to_me=True)
async def chat_waifu(bot, ev):
    if not priv.check_priv(ev, priv.SUPERUSER):
        await bot.send(ev, R.img('kkl/bielian.jpg').cqcode)
    else:
        await bot.send(ev, 'mua~')


@sv.on_fullmatch('老公', only_to_me=True)
async def chat_laogong(bot, ev):
    await bot.send(ev, R.img('kkl/wenhao2.jpg').cqcode)


@sv.on_fullmatch(('mua', '么', '么么', '么么哒', 'mua~'), only_to_me=True)
async def chat_mua(bot, ev):
    if random.random() < 0.5:
        await bot.send(ev, 'mua~')
    else:
        await bot.send(ev, '笨蛋~', at_sender=True)


@sv.on_fullmatch('来点星奏')
async def seina(bot, ev):
    await bot.send(ev, R.img('星奏.png').cqcode)


@sv.on_fullmatch(('我有个朋友说他好了', '我朋友说他好了', ))
async def ddhaole(bot, ev):
    if random.random() < 0.5:
        await bot.send(ev, '那个朋友是不是你弟弟？')
        await util.silence(ev, 30)
    else:
        await bot.send(ev, R.img('geng/朋友还想看.png').cqcode)


@sv.on_fullmatch('我好了')
async def nihaole(bot, ev):
    if random.random() < 0.5:
        await bot.send(ev, '不许好，憋回去！')
        await util.silence(ev, 30)
    else:
        await bot.send(ev, R.img('geng/好好怪.jpg').cqcode)


@sv.on_fullmatch(('九九归一'))
async def chat_jiujiuguiyi(bot, ev):
    await bot.send(ev, R.img('geng/九九归一.jpg').cqcode)


@sv.on_fullmatch(('生生不息'))
async def chat_shengshengbuxi(bot, ev):
    await bot.send(ev, R.img('geng/生生不息.jpg').cqcode)


@sv.on_fullmatch(('唉', '难顶哦', '难搞哦'))
async def chat_ai(bot, ev):
    await bot.send(ev, R.img('kkl/mamatanqi.jpg').cqcode)


@sv.on_fullmatch(('草草草'))
async def chat_cao3(bot, ev):
    if random.random() < 0.5:
        await bot.send(ev, '不许不许不许草')
    else:
        await bot.send(ev, '该除草了吗')


@sv.on_fullmatch(('已经很晚了'))
async def chat_gaishuile(bot, ev):
    await bot.send(ev, R.img('kkl/gaishuile.jpg').cqcode)


@sv.on_fullmatch(('会战警察来了'))
async def chat_huizhanjingcha(bot, ev):
    await bot.send(ev, R.img(f'geng/会战警察{random.randint(1, 3)}.jpg').cqcode)


@sv.on_fullmatch(('xp调查', 'xp调研'), only_to_me=True)
async def chat_xpdiaocha(bot, ev):
    await bot.send(ev, R.img(f'priconne/tips/xpdiaocha{random.randint(1, 2)}.jpg').cqcode)


@sv.on_fullmatch(('泡面', '给我泡碗面', '泡碗面'), only_to_me=True)
async def chat_paomian(bot, ev):
    await bot.send(ev, R.img('kkl/paomian.gif').cqcode)


@sv.on_fullmatch(('跳舞', 'dance'), only_to_me=True)
async def chat_dance(bot, ev):
    await bot.send(ev, R.img(f'kkl/dance{random.randint(1, 2)}.gif').cqcode)


@sv.on_fullmatch(('hensin', '公主形态'), only_to_me=True)
async def chat_hensin(bot, ev):
    await bot.send(ev, R.img('kkl/hensin.gif').cqcode)


@sv.on_fullmatch(('猜拳', '石头剪刀布'), only_to_me=True)
async def chat_caiquan(bot, ev):
    #await bot.send(ev, f'[CQ:rps]')
    caiquan = ('石头！', '剪刀！', '布！', '✊', '✌', '🖐')
    await bot.send(ev, f'{random.choice(caiquan)}')


@sv.on_fullmatch(('你怎么想', '你怎么看', '你觉得呢'), only_to_me=True)
async def chat_wjd(bot, ev):
    await bot.send(ev, R.img(f'wjuede/wjd{random.randint(1,10)}.jpg').cqcode)


@sv.on_fullmatch(('答一下', '回答一下', '咋办啊', '咋整啊', '优质解答'), only_to_me=True)
async def chat_yzjd(bot, ev):
    await bot.send(ev, R.img(f'yzjd/yzjd{random.randint(1,4)}.jpg').cqcode)


@sv.on_fullmatch('今年剩余', only_to_me=True)
async def chat_jinnianshengyu(bot, ev):
    now = datetime.now(tz)
    start = datetime(now.year, 1, 1)
    nowtime = datetime(now.year, now.month, now.day)
    xiaohao = (nowtime - start).days
    shengyu = int(xiaohao*10/365)
    msg = f'今年已过去{xiaohao}天\n'
    for i in range(shengyu):
        msg += '◼'
    for i in range(10-shengyu):
        msg += '◻'
    await bot.send(ev, msg)


@sv.on_fullmatch(('不愧是你', '不愧是我', 'bksn', 'bksw'))
async def chat_bksn(bot, ev):
    if random.random() < 0.5:
        await bot.send(ev, R.img('taowa/bksn.jpg').cqcode)


@sv.on_fullmatch(('你们好', '你们好啊'))
async def chat_nimenhao(bot, ev):
    if random.random() < 0.5:
        await bot.send(ev, R.img('taowa/nimenhao.jpg').cqcode)


@sv.on_fullmatch(('不要以为这样就赢了'))
async def chat_woshule(bot, ev):
    if random.random() < 0.5:
        await bot.send(ev, R.img('taowa/不要以为这样就赢了.jpg').cqcode)


@sv.on_fullmatch(('彳亍', '行', '行吧'))
async def chat_xing(bot, ev):
    if random.random() < 0.1:
        await bot.send(ev, R.img('taowa/taowaxing.jpg').cqcode)


@sv.on_fullmatch(('觉了', '妈的绝了', '妈的觉了', '绝了'))
async def chat_juele(bot, ev):
    if random.random() < 0.1:
        await bot.send(ev, R.img(f'taowa/juele{random.randint(1, 9)}.jpg').cqcode)


@sv.on_fullmatch(('酸', '酸了', '不过如此', 'xmsl', 'xmswl'))
async def chat_suanle(bot, ev):
    if random.random() < 0.1:
        await bot.send(ev, R.img(f'suan/suan{random.randint(1, 6)}.jpg').cqcode)


@sv.on_fullmatch(('火星'))
async def chat_huoxing(bot, ev):
    if random.random() < 0.1:
        await bot.send(ev, R.img(f'huoxing/火星{random.randint(1, 7)}.jpg').cqcode)


@sv.on_fullmatch(('sb春黑刀'))
async def chat_sbchunhei(bot, ev):
    if random.random() < 0.1:
        await bot.send(ev, R.img('geng/sb春黑刀.jpg').cqcode)


@sv.on_fullmatch(('射了', '🐍了', '社了', '设了'))
async def shejingguanli(bot, ev):
    if random.random() < 0.5:
        await bot.send(ev, '还不可以射哦~')
        await util.silence(ev, 30, skip_su=False)
    else:
        await bot.send(ev, '我来清理干净吧~♪')


@sv.on_fullmatch('啊这')
async def chat_azhe(bot, ev):
    rtest = random.random()
    if rtest < 0.1:
        await bot.send(ev, '啊这')
    elif rtest < 0.2:
        await bot.send(ev, R.img('kkl/oxo1.gif').cqcode)
    elif rtest < 0.4:
        await bot.send(ev, R.img(f'kkl/oxo{random.randint(1, 4)}.jpg').cqcode)


@sv.on_fullmatch(('草', '🌿'))
async def chat_cao(bot, ev):
    rtest = random.random()
    if rtest < 0.2:
        await bot.send(ev, R.img(f'taowa/cao{random.randint(1, 2)}.jpg').cqcode)
    elif rtest < 0.3:
        await bot.send(ev, '草')
    elif rtest < 0.4:
        await bot.send(ev, '不许草')
    elif rtest < 0.5:
        await bot.send(ev, '草野优衣')


@sv.on_fullmatch(('就这', '就这？', '就这?', '九折', '九折？', '九折?'))
async def chat_jiuzhe(bot, ev):
    rtest = random.random()
    if rtest < 0.2:
        await bot.send(ev, R.img('taowa/jiuzhe.jpg').cqcode)
    elif rtest < 0.3:
        await bot.send(ev, '就这')
    elif rtest < 0.35:
        await bot.send(ev, '你来')


@sv.on_fullmatch(('?', '？', '¿'))
async def chat_wenhao(bot, ev):
    rtest = random.random()
    if rtest < 0.1:
        await bot.send(ev, R.img('taowa/wenhao.jpg').cqcode)
    elif rtest < 0.15:
        await bot.send(ev, '?')
    elif rtest < 0.2:
        await bot.send(ev, '？')
    elif rtest < 0.25:
        await bot.send(ev, '¿ ')
    elif rtest < 0.3:
        await bot.send(ev, R.img('maimeng/wenhao.jpg').cqcode)


# =====================keyword======================= #


@sv.on_keyword(('上号', '网抑云', '到点了'))
async def music163_sentences(bot, ctx):
    now = datetime.now(tz)
    if not (0 <= now.hour <= 1):
        # await bot.send(ev, '还没到点呢')
        return
    if random.random() < 0.1:
        await bot.finish(ctx, R.img(f'wyy/notwyy{random.randint(1, 7)}.jpg').cqcode)
    if random.random() < 0.5+1:
        resp = requests.get('http://api.heerdev.top/nemusic/random', timeout=5)
        if resp.status_code == requests.codes.ok:
            res = resp.json()
            sentences = res['text']
            # await bot.send(ctx, sentences)
        else:
            await bot.finish(ctx, '上号失败，我很抱歉。查询出错，请稍后重试。')
    else:
        resp = requests.get('https://api.lo-li.icu/wyy/', timeout=5)
        if resp.status_code == requests.codes.ok:
            sentences = resp.text
            # await bot.finish(ctx, sentences)
        else:
            await bot.finish(ctx, '上号失败，我很抱歉。查询出错，请稍后重试。')
    if random.random() < 0.5:
        wyypic = R.img(f'wyy/wyy{random.randint(1, 42)}.jpg').cqcode
        sentences = f'{wyypic}\n' + sentences
    await bot.send(ctx, sentences)

@sv.on_keyword(('sonet', '搜内', '骚内', '馊内'))
async def chat_sonet(bot, ctx):
    if random.random() < 0.05:
        await bot.send(ctx, R.img(f'sonet{random.randint(1, 2)}.jpg').cqcode)


@sv.on_keyword(('有作业吗'))
async def chat_zuoye(bot, ctx):
    if random.random() < 0.05:
        await bot.send(ctx, R.img('kkl/zuoye.jpg').cqcode)


@sv.on_keyword(('蓝绿修改器'))
async def chat_xiugaiqi(bot, ctx):
    if random.random() < 0.15:
        await bot.send(ctx, R.img(f'geng/修改器{random.randint(1, 3)}.jpg').cqcode)


@sv.on_keyword(('我是萌新'))
async def chat_shenmemx(bot, ctx):
    if random.random() < 0.05:
        await bot.send(ctx, R.img('geng/什么萌新.jpg').cqcode)


@sv.on_keyword(('摸了'))
async def chat_mole(bot, ctx):
    if random.random() < 0.05:
        await bot.send(ctx, R.img('geng/摸了.jpg').cqcode)


@sv.on_keyword(('紫电一闪'))
async def chat_zidianyishan(bot, ctx):
    if random.random() < 0.9:
        await bot.send(ctx, R.img('geng/紫电一闪.gif').cqcode)


@sv.on_keyword(('怎么又要打会战'))
async def chat_zenmeyouyaoda(bot, ctx):
    if random.random() < 0.8:
        await bot.send(ctx, R.img('geng/怎么又要打会战.jpg').cqcode)


@sv.on_keyword(('该用的时候不用'))
async def chat_gaiyongdeshihou(bot, ctx):
    if random.random() < 0.8:
        await bot.send(ctx, R.img('geng/该用的时候不用.jpg').cqcode)


@sv.on_keyword(('英雄可不能临阵逃脱啊'))
async def chat_yongxiongbuneng(bot, ctx):
    await bot.send(ctx, R.img('geng/英雄可不能临阵逃脱啊.jpg').cqcode)


@sv.on_keyword(('auto', '凹凸'))
async def chat_wtmauto(bot, ctx):
    if random.random() < 0.1:
        await bot.send(ctx, R.img('geng/wtmzjauto.jpg').cqcode)


@sv.on_keyword(('毒池'))
async def chat_duchi(bot, ctx):
    if random.random() < 0.5:
        await bot.send(ctx, R.img('geng/这池子不行.jpg').cqcode)


@sv.on_keyword(('再氪傻逼'))
async def chat_zaikesb(bot, ctx):
    if random.random() < 0.5:
        await bot.send(ctx, R.img('geng/再氪傻逼.jpg').cqcode)


@sv.on_keyword(('量子色图', '量子涩图'))
async def chat_liangzisetu(bot, ctx):
    if random.random() < 0.5:
        await bot.send(ctx, R.img('geng/量子色图.jpg').cqcode)


@sv.on_keyword(('限定连发'))
async def chat_xdlf(bot, ctx):
    if random.random() < 0.5:
        await bot.send(ctx, R.img('geng/限定连发.jpg').cqcode)


@sv.on_keyword(('确实', '有一说一', 'u1s1', 'yysy'))
async def chat_queshi(bot, ctx):
    if random.random() < 0.1:
        await bot.send(ctx, R.img(f'taowa/qs{random.randint(1, 6)}.jpg').cqcode)


@sv.on_keyword(('优依说一', 'yui说一', 'yui:1', 'yui：1', '优衣说一'))
async def chat_yuiqueshi(bot, ctx):
    if random.random() < 0.5:
        await bot.send(ctx, R.img('taowa/qs3.jpg').cqcode)


@sv.on_keyword(('呐'))
async def chat_ne(bot, ctx):
    if random.random() < 0.1:
        await bot.send(ctx, R.img('taowa/taowane.jpg').cqcode)
    elif random.random() < 0.1:
        await bot.send(ctx, R.img('maimeng/ne.jpg').cqcode)


@sv.on_keyword(('为啥'))
async def chat_weisha(bot, ctx):
    if random.random() < 0.05:
        await bot.send(ctx, R.img('taowa/weisha.jpg').cqcode)
    elif random.random() < 0.05:
        await bot.send(ctx, R.img(f'yzjd/yzjd{random.randint(1,4)}.jpg').cqcode)


@sv.on_keyword(('内鬼'))
async def chat_neigui(bot, ctx):
    if random.random() < 0.3:
        await bot.send(ctx, R.img('taowa/wuneigui.jpg').cqcode)


@sv.on_keyword(('+19', '九银一金', '9银1金', '19母'))
async def chat_jia19(bot, ctx):
    if random.random() < 0.05:
        await bot.send(ctx, R.img(f'+19/19{random.randint(1, 5)}.jpg').cqcode)


@sv.on_keyword(('挂树', '树上'))
async def chat_guashu(bot, ctx):
    if random.random() < 0.05:
        await bot.send(ctx, R.img(f'geng/guashu{random.randint(1, 2)}.jpg').cqcode)


@sv.on_keyword(('会战'))
async def chat_clanba(bot, ctx):
    if random.random() < 0.001:
        await bot.send(ctx, R.img('geng/我的天啊你看看都几度了.jpg').cqcode)
    elif random.random() < 0.001:
        await bot.send(ctx, R.img('geng/我的天啊你看看都几点了.jpg').cqcode)
    elif random.random() < 0.001:
        await bot.send(ctx, R.img('geng/我要打团战zzz.jpg').cqcode)
    elif random.random() < 0.001:
        await bot.send(ctx, R.img('geng/buxiangdahuiz.jpg').cqcode)
    elif random.random() < 0.001:
        await bot.send(ctx, R.img('kuaijiehuifu/huizhan.jpg').cqcode)


nyb_player = f'''{R.img('geng/newyearburst.gif').cqcode}
正在播放：New Year Burst
──●━━━━ 1:05/1:30
⇆ ㅤ◁ ㅤㅤ❚❚ ㅤㅤ▷ ㅤ↻
'''.strip()


@sv.on_keyword(('春黑', '新黑'))
async def new_year_burst(bot, ev):
    if random.random() < 0.02:
        await bot.send(ev, nyb_player)


# =====================rex======================= #


@sv.on_rex(r'^(果(\S)?然(\S)?)?是?就?(\S)?我(\S)?(果(\S)?然(\S)?)?还?(\S)?是?(\S)?你?(\S)?群?(\S)?里?(\S)?(最|太|(一(\S)?个))(\S)?((垃(\S)?圾)|(辣(\S)?鸡)|菜|弱)(\S)?(的|了)(\S)?$')
async def chat_yinyang(bot, ev):
    if random.random() < 0.5:
        await bot.send(ev, '主人是最强的！')
    else:
        await bot.send(ev, '没关系，不管实力如何在下都会追随主人的！')


@sv.on_rex(r'^(兰德索尔)?最([强弱])[7七]人$', only_to_me=True)
async def chat_zui7ren(bot, ev):
    pos = ev['match'].group(2)
    if '强' in pos:
        await bot.send(ev, R.img('priconne/tips/zuiqian7.jpg').cqcode)
    elif '弱' in pos:
        await bot.send(ev, R.img('priconne/tips/zuiruo7.jpg').cqcode)


@sv.on_rex(r'^(((什么)|啥)是)?露娜塔(是(啥|(什么)))?$', only_to_me=True)
async def chat_lunanota(bot, ev):
    await bot.send(ev, R.img('priconne/tips/lunanota.jpg').cqcode)


@sv.on_rex(r'^(((什么)|啥)是)?(会长我想出)?点兔刀(是(啥|(什么)))?$', only_to_me=True)
async def chat_diantudao(bot, ev):
    await bot.send(ev, R.img('priconne/tips/diantudao.jpg').cqcode)


@sv.on_rex(r'(不会吧[?？！!]?)+')
async def chat_bhbbhb(bot, ev):
    await bot.send(ev, R.img('kkl/bhbbhb.jpg').cqcode)


@sv.on_rex(r'^喵[喵？！?!]*$')
async def chat_catchat(bot, ev):
    p = 1
    msg = '喵'
    while p > 0:
        if random.random() > p:
            break
        msg += random.choice(('喵', '喵', '?', '!'))
        p -= 0.2
    await bot.send(ev, msg)

""" @sv.on_rex(r'(.*)[123](.*)')
async def chat_caiquan2(bot, ev):
    await bot.send(ev, 'ev.match.group(0)')
    await bot.send(ev, 'ev.match.group(1)')
    await bot.send(ev, 'ev.match.group(2)')
    await bot.send(ev, '[CQ:rps]') """


# =====================keyword======================= #

@sv.on_prefix('快捷回复', only_to_me=True)
async def kuaijiehuifu(bot, ev):
    s = ev.message.extract_plain_text().strip()
    msg = ["快捷回复"]
    if not s:
        msg.append("现在的快捷回复有\n哦\n漏刀\n沉船\n狗叫\n快开车\n会战")
    elif s == '哦':
        msg.append(str(R.img('kuaijiehuifu/o.png').cqcode))
    elif s == '漏刀':
        msg.append(str(R.img('kuaijiehuifu/loudao.jpg').cqcode))
    elif s == '沉船':
        msg.append(str(R.img('kuaijiehuifu/chenchuan.png').cqcode))
    elif s == '狗叫':
        msg.append(str(R.img('kuaijiehuifu/goujiao.jpg').cqcode))
    elif s == '快开车':
        msg.append(str(R.img('kuaijiehuifu/setu.jpg').cqcode))
    elif s == '会战':
        msg.append(str(R.img('kuaijiehuifu/huizhan.jpg').cqcode))
    else:
        msg.append("现在的快捷回复有\n哦\n漏刀\n沉船\n狗叫\n快开车\n会战")
        # return
    await bot.send(ev, '\n'.join(msg))
