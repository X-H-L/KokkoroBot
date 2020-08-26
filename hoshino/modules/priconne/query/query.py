import itertools
from hoshino import util, R
from hoshino.typing import CQEvent
from . import sv
if_ta1 = True
rta_1 = R.img('priconne/quick/rta1.png').cqcode
if_ta2 = True
rta_2 = R.img('priconne/quick/rta2.png').cqcode
if_tf1 = True
rtq_1 = R.img('priconne/quick/rtq1.png').cqcode
rtz_1 = R.img('priconne/quick/rtz1.png').cqcode
rth_1 = R.img('priconne/quick/rth1.png').cqcode
if_tf2 = True
rtq_2 = R.img('priconne/quick/rtq2.png').cqcode
rtz_2 = R.img('priconne/quick/rtz2.png').cqcode
rth_2 = R.img('priconne/quick/rth2.png').cqcode
rjq = R.img('priconne/quick/rjq.png').cqcode
rjz = R.img('priconne/quick/rjz.png').cqcode
rjh = R.img('priconne/quick/rjh.png').cqcode
if_b = True
rba = R.img('priconne/quick/rba.png').cqcode
jpRankn = '18-3'
twRankn = '17-3'
bRankn = '10-3'

ATIP='※建议加入前中后精准定位，eg：#台前rank'
@sv.on_rex(r'^(\*?([日台国陆b])服?([前中后]*)卫?)?rank(表|推荐|指南)?$', only_to_me=True)
async def rank_sheet(bot, ev):
    match = ev['match']
    is_jp = match.group(2) == '日'
    is_tw = match.group(2) == '台'
    if match.group(2) is not None:
        is_cn = match.group(2) in '国陆b'
    else:
        is_cn = False
    if not is_jp and not is_tw and not is_cn:
        await bot.send(ev,
                       f'\n请问您要查询哪个服务器的rank表？\n*#日rank表\n*#台rank表\n*#B服rank表\n{ATIP}',
                       at_sender=True)
        return
    msg = [
        '\n※表格仅供参考，升r有风险，强化需谨慎\n※一切以会长要求为准——',
    ]
    pos = match.group(3)
    if not (pos or is_cn):
        msg.append(ATIP)
    if is_jp:
        msg.append(f'※不定期搬运自图中群号\n※图中广告为原作者推广，与本bot无关\nR{jpRankn} rank表：')
        if not pos or '前' in pos:
            msg.append(str(rjq))
        if not pos or '中' in pos:
            msg.append(str(rjz))
        if not pos or '后' in pos:
            msg.append(str(rjh))
        await bot.send(ev, '\n'.join(msg), at_sender=True)
        await util.silence(ev, 60)
    elif is_tw:
        msg.append(f'R{twRankn} rank表：')
        if if_ta1:
            msg.append(f'{rta_1}')
        if if_ta2:
            msg.append(f'{rta_2}')
        if if_tf1:
            if not pos or '前' in pos:
                msg.append(str(rtq_1))
            if not pos or '中' in pos:
                msg.append(str(rtz_1))
            if not pos or '后' in pos:
                msg.append(str(rth_1))
        if if_tf2:
            if not pos or '前' in pos:
                msg.append(str(rtq_2))
            if not pos or '中' in pos:
                msg.append(str(rtz_2))
            if not pos or '后' in pos:
                msg.append(str(rth_2))
        await bot.send(ev, '\n'.join(msg), at_sender=True)
        await util.silence(ev, 60)
    elif is_cn:
        if not if_b:
            await bot.send(
                ev,
                '\n※B服当前仅开放至金装，r10前无需考虑卡rank\n※暂未发现公开的靠谱rank推荐表\n※装备强化消耗较多mana，如非前排建议不强化\n※关于卡r的原因可发送"bcr速查"研读【为何卡R卡星】一帖',
                at_sender=True)
        else:
            msg.append(f'R{bRankn} rank表：')
            msg.append(str(rba))
            await bot.send(ev, '\n'.join(msg), at_sender=True)
            await util.silence(ev, 60)


@sv.on_rex(r'^(兰德索尔|pcr)?(年龄|胸围|学业|胸部|岁数|欧派|大小)(统计|分布|表)表?$', only_to_me=True)
async def pcrfenbubiao(bot, ev):
    is_n = ev.match.group(2) in '年龄岁数'
    is_x = ev.match.group(2) in '胸围胸部欧派大小'
    is_s = ev.match.group(2) == '学业'
    if is_n:
        await bot.send(ev, R.img('priconne/tips/pcrnianlingbiao.jpg').cqcode)
    elif is_x:
        await bot.send(ev, R.img('priconne/tips/xiongwei.png').cqcode)
    elif is_s:
        await bot.send(ev, R.img('priconne/tips/xueniantuice.jpg').cqcode)


@sv.on_fullmatch(('jjc', 'JJC', 'JJC作业', 'JJC作业网', 'JJC数据库', 'jjc作业', 'jjc作业网', 'jjc数据库'))
async def say_arina_database(bot, ev):
    await bot.send(ev,'公主连接Re:Dive 竞技场编成数据库\n日文：https://nomae.net/arenadb \n中文：https://pcrdfans.com/battle')


@sv.on_fullmatch(('furry', 'furry分级', '喜欢羊驼很怪吗', '喜欢羊驼有多怪'), only_to_me=True)
async def furryrank(bot, ev):
    await bot.send(ev, R.img('priconne/tips/furry.jpg').cqcode)


OTHER_KEYWORDS = '【日rank】【台rank】【b服rank】【jjc作业网】【黄骑充电表】【一个顶俩】【多目标boss机制】【pcr公式】'
PCR_SITES = f'''
【繁中wiki/兰德索尔图书馆】pcredivewiki.tw
【体力规划工具/可可萝笔记】https://kokkoro-notes.lolita.id/#
【刷图规划工具/quest-helper】https://expugn.github.io/priconne-quest-helper/
【日文wiki/GameWith】gamewith.jp/pricone-re
【日文wiki/AppMedia】appmedia.jp/priconne-redive
【竞技场作业库(中文)】pcrdfans.com/battle
【竞技场作业库(日文)】nomae.net/arenadb
【论坛/NGA社区】bbs.nga.cn/thread.php?fid=-10308342
【iOS实用工具/初音笔记】bbs.nga.cn/read.php?tid=14878762
【安卓实用工具/静流笔记】bbs.nga.cn/read.php?tid=20499613
【台服卡池千里眼】bbs.nga.cn/read.php?tid=16986067
【日官网】priconne-redive.jp
【台官网】www.princessconnect.so-net.tw
【pcr美术资源】https://redive.estertion.win/
【pc美术资源】priconestory.nekonikoban.org
===其他查询关键词===
{OTHER_KEYWORDS}
※B服速查请输入【bcr速查】'''

BCR_SITES = f'''
【妈宝骑士攻略(懒人攻略合集)】bbs.nga.cn/read.php?tid=20980776
【机制详解】bbs.nga.cn/read.php?tid=19104807
【初始推荐】bbs.nga.cn/read.php?tid=20789582
【术语黑话】bbs.nga.cn/read.php?tid=18422680
【角色点评】bbs.nga.cn/read.php?tid=20804052
【秘石规划】bbs.nga.cn/read.php?tid=20101864
【卡池亿里眼】bbs.nga.cn/read.php?tid=20816796
【为何卡R卡星】bbs.nga.cn/read.php?tid=20732035
【推图阵容推荐】bbs.nga.cn/read.php?tid=21010038

===其他查询关键词===
{OTHER_KEYWORDS}
※日台服速查请输入【pcr速查】'''

@sv.on_fullmatch(('pcr速查', 'pcr图书馆', '图书馆'), only_to_me=True)
async def pcr_sites(bot, ev: CQEvent):
    await bot.send(ev, PCR_SITES, at_sender=True)
    await util.silence(ev, 60)


@sv.on_fullmatch(('bcr速查', 'bcr攻略'), only_to_me=True)
async def bcr_sites(bot, ev: CQEvent):
    await bot.send(ev, BCR_SITES, at_sender=True)
    await util.silence(ev, 60)


YUKARI_SHEET_ALIAS = map(
    lambda x: ''.join(x),
    itertools.product(('黄骑', '酒鬼', '黃騎'), ('充电', '充电表', '充能', '充能表')))
YUKARI_SHEET = f'''
{R.img('priconne/tips/huangqichongdian.jpg').cqcode}
※大圈是1动充电对象 PvP测试
※黄骑四号位例外较多
※对面羊驼或中后卫坦 有可能歪
※我方羊驼算一号位
※图片搬运自漪夢奈特'''


@sv.on_fullmatch(YUKARI_SHEET_ALIAS, only_to_me=True)
async def yukari_sheet(bot, ev):
    await bot.send(ev, YUKARI_SHEET, at_sender=True)
    await util.silence(ev, 60)


LUNA_SHEET_ALIAS = map(
    lambda x: ''.join(x),
    itertools.product(('露娜', 'scw', 'luna'), ('充电', '充电表', '充能', '充能表')))
LUNA_SHEET = f'''
{R.img('priconne/tips/lunatp1.jpg').cqcode}
{R.img('priconne/tips/lunatp2.jpg').cqcode}'''


@sv.on_fullmatch(LUNA_SHEET_ALIAS, only_to_me=True)
async def luna_sheet(bot, ev):
    await bot.send(ev, LUNA_SHEET, at_sender=True)
    await util.silence(ev, 60)


DRAGON_TOOL = f'''
拼音对照表：{R.img('priconne/KyaruMiniGame/注音文字.jpg').cqcode}{R.img('priconne/KyaruMiniGame/接龙.jpg').cqcode}
龍的探索者們小遊戲單字表 https://hanshino.nctu.me/online/KyaruMiniGame
镜像 https://hoshino.monster/KyaruMiniGame
网站内有全词条和搜索，或需科学上网'''


@sv.on_fullmatch(('一个顶俩', '拼音接龙', '韵母接龙'), only_to_me=True)
async def dragon(bot, ev):
    await bot.send(ev, DRAGON_TOOL, at_sender=True)
    await util.silence(ev, 60)


Duomubiao = f'''
=========
Boss 本体-
=========
1. 这是一个虚拟概念，并不是一个真正的可攻击目标。
2. 它负责将自身的一些属性共享给各个部位以及定义整体的行动模式。
3. 它没有抗性。
(对于本期的天秤座，存在三个目标，分别为本体部位和秤的两端，本文所使用的“Boss 本体”和”本体部位“并不等同。)
=========
Boss 部位-
=========
1. 这是一个实体，一个可被攻击的目标。
2. 它拥有区别于本体的属性。
3. 它拥有自己的抗性。(虽然目前各部位抗性都是一样的，但是理论上不同部位也可以拥有不同的抗性)
=========
Break-
=========
1. Break 是针对 Boss 部位的机制，不同部位的 Break 互不干扰。
2. 当某个部位的 HP 归 0 后，即进入 Break 状态。
3. Break 状态持续一定时间后(不同部位 Break 持续时间可能不同，但天秤座三个部位均为 20 秒)，将会恢复成正常状态。
4. Break 可以根据 Boss 部位脚下的圈的颜色来判断是何种状态。随着血量降低颜色由黄至红逐渐加深；Break 文字弹出瞬间，并且固定为灰色代表进入 Break 状态；Break 结束后恢复成黄色。
5. Break 会导致 Boss 本体受到一定的 Debuff，不同部位带来的 Debuff 通常也不相同，Debuff 通常是攻击或防御降低。
=========
属性机制-
=========
1. HP
Boss 本体负责定义自身的整体 HP，例如本期天秤座 Boss，其本体 HP 为 1500 万。当攻击 Boss 部位时，本体的 HP 将会下降等量数值。
Boss 部位也拥有 HP，这个 HP 通常是一个较小的数值(比如几万至几十万)，当这个数值归 0 后，该部位就会进入 Break 状态。当该部位恢复到正常状态时，其 HP 也会恢复原本的最大值。
当 Boss 部位处于 Break 状态时，它的 HP 会锁定为 0，继续承受伤害将直接降低 Boss 本体的 HP。
2. TP 上升、TP 轻减
这两个属性由 Boss 本体负责，Boss 部位不参与。
当 Boss 部位的某个动作是“恢复自身 X 点 TP”，并不是给该部位恢复，而是直接恢复到 Boss 本体上，同时也会参考 Boss 本体的 TP 上升进行加成。
当 Boss 部位进行行动时，所获得的 TP 参考 Boss 本体的 TP 上升进行加成。
3. 攻击间隔、攻击范围、移动速度
这些属性由 Boss 本体负责，Boss 部位不参与。
4. 攻击、防御、暴击、回避、命中、回复量上升
这些属性由 Boss 部位负责，Boss 本体的这些属性没有意义。
=========
Buff、Debuff 、承受我方技能的机制-
=========
1. Boss 本体负责接收 Buff 和 Debuff，并将属性加减应用于所有部位。
比如部位 A 500 防御，部位 B 400 防御，此时 Boss 中了一个防御降低 100 的 Debuff，那么部位 A 为 400 防御，部位 B 为 300 防御。
2. 当范围效果作用于多目标 Boss 时(例如娜娜卡范围减防)，Boss 并不会根据部位数量产生多个 Debuff 效果，而是只生效一个。
3. 只对单一目标生效的技能(目前只有水狼有)，对多目标 Boss 无效，无论各部位是不是 Break。
4. 各种控制类和持续伤害类技能，由 Boss 部位进行抗性判定，由 Boss 本体负责接收效果。例如一个单体毒伤技能是否有效，要看被打到的部位的抗性，如果判定有效 Boss 本体就会中毒。如果是群体毒技能，Boss 本体只会中一层毒。
5. 场地类 Debuff 技能，同单目标 Debuff 技能，不会吃多层。
6. 场地类伤害技能，如龙姬的技能 2，按照多目标计算。
7. 因目标数量改变技能系数的技能，如水狗 UB，由覆盖到的部位数量进行加成。
==========
行动模式和 Boss 自身的技能机制-
==========
1. 行动模式由 Boss 本体负责。
2. 多目标 Boss 的所有行动都会指定一个实施部位，目前绝不会是 Boss 本体。
3. Boss 本体定义了技能列表和技能等级。
4. Boss 部位只会使用部位所独有的技能，目前不存在部位 A 和部位 B 都能使用某技能 X 的情况。
5. 技能计算伤害时，通常要代入技能等级和单位属性，此时就要代入 Boss 本体所定义的技能等级和实施部位所定义的属性。
===其他查询关键词===
{OTHER_KEYWORDS}
※日台服速查请输入【pcr速查】'''


@sv.on_fullmatch(('多目标boss机制文字'), only_to_me=True)
async def duomubiao(bot, ev):
    await bot.send(ev, Duomubiao, at_sender=True)
    await util.silence(ev, 60)


Duomubiaourl = f'''
原文很长很长，怕刷屏可以直接去这里看https://ngabbs.com/read.php?tid=18623761
不想开浏览器要在群里看的话请发送#多目标boss机制文字
===其他查询关键词===
{OTHER_KEYWORDS}
※日台服速查请输入【pcr速查】'''


@sv.on_fullmatch(('多目标boss机制', '多目标boss'), only_to_me=True)
async def duomubiaourl(bot, ev):
    await bot.send(ev, Duomubiaourl, at_sender=True)


pcrgshelp = f'''
-你游的各种计算公式-
搬运自https://ngabbs.com/read.php?tid=15533965
=======指令=======
【#pcr公式+[条目]】查阅相关说明，如#pcr公式tp上升
【#pcr公式list】查看所有条目
=====热门条目=====
[tp上升]
[暴伤]
===其他查询关键词===
{OTHER_KEYWORDS}
※日台服速查请输入【pcr速查】'''
pcrFORMULA = {
    '攻击力':
    '''物理攻击力 / 魔法攻击力
攻击力是角色对于 0 防御的敌人造成的实际伤害值''',
    '防御力':
    '''物理防御力 / 魔法防御力
防御力计算公式为：
受到的伤害 = 敌方攻击力 / (1 + 防御 / 100)
简单说就是 100 防御等于 50% 免伤，200 防御约等于 66.67% 免伤
防御力没有负数，破甲技能最多降低敌方防御力至 0''',
    '回避':
    '''回避
回避计算公式为：
回避几率 = 1 / (1 + 100 / 面板回避)
假设角色面板回避是 100 则回避几率为 50%，面板回避为 200 回避率约为 66.67%''',
    '命中':
    '''命中
考虑命中后的回避几率公式为：
回避几率 = 1 / (1 + 100 / (面板回避 - 敌方命中))
简单说就是敌方有多少面板命中就相当于降低了自己多少面板回避
另外回避没有负数，命中最多降低敌方回避至 0''',
    'hp':
    '''HP / 有效物理 HP / 有效魔法 HP
HP 本来没什么好解释的，但是在这里稍微提一下有效 HP 的概念
有效 HP 可以简单理解为总计可以吸收多少敌方伤害量(计算防御前)
有效魔法 HP = HP(1 + 魔法防御力 / 100)
(不考虑敌方命中的)有效物理 HP = HP (1 + 物理防御力 / 100)(1 + 面板躲闪 / 100)
(考虑敌方命中的)有效物理 HP = HP(1 + 物理防御力 / 100)(1 + (面板躲闪 - 敌方命中) / 100)
通过有效 HP 可以很容易的量化对比一个角色升 Rank 后是不是变硬了''',
    '回复量上升':
    '''回复量上升
受到的治疗 = 原始治疗量 × (1 + 回复技能施法者的回复量上升 / 100)
需要特别注意的一点，回复量只受施法者本身的回复量上升影响，和被治疗者的回复量上升无关
另外还要注意一点，只有直接治疗技能才享受回复量上升
秋乃(红毛)、美里(圣母)、泳装女仆等人的 HOT 型治疗技能均不受回复量上升影响
黑骑吸收盾类技能不受回复量上升影响
HP 吸收带来的治疗不受回复量上升影响''',
    '加速减速类技能':
    '''加速减速类技能
此类技能不受攻击力和技能等级影响，且无法叠加，后生效的会无条件覆盖之前的，且加减速之间也会相互覆盖。
Cy 设计此类技能时往往会附带其他效果，作为升级技能的奖励，比如亚里沙减速本身也附带伤害，升级时伤害提高但是减速永远只减 20%''',
    '行动控制类技能':
    '''行动控制类技能
行动控制类包含击晕、冻结、麻痹、束缚、睡眠、石化等，此类技能没有特别说的，基本上都是一个固定时间的控制，对于此类技能 Cy 通常会设计额外的伤害效果作为升级奖励
但是此类技能存在一个命中几率的东西，比如大家经常吐槽的打花被连捆，打猪被连晕
控制类技能命中几率计算公式为：
命中几率 = 1 - (目标角色等级 - 技能等级) / 100
--------------
实战计算:
会战 Boss 花(二周目)的束缚技能等级是 75，注意技能等级是独立的不一定等于 Boss 等级
那么束缚效果打在 110 级的玩家身上命中率为
1 - (110 - 75) / 100 = 65%''',
    '黑暗类技能':
    '''黑暗类技能
每个黑暗效果具有一个黑暗强度数值，强度数值越低实际效果越强(比如 1 强度代表 99% Miss)
镜子、狐狸的黑暗强度为 40
みそぎ(炸弹、熊孩子)的黑暗强度为 70
Boss 方的独眼巨人黑暗强度为 50

黑暗强度的计算方式为
第一步先进行敌我双方的命中-闪避判定，公式为：
回避几率 = 1 / (1 + 100 / (面板回避 - 敌方命中))
随机数小于回避几率时直接判定为 Miss，否则进行黑暗强度判定，公式为：
黑暗生效几率 = (100 - 黑暗强度) / 100
随机数小于黑暗生效几率时，判定为 Miss''',
    'tp减轻':
    '''TP 轻减
TP 轻减效果为当使用大招时 TP 不变为 0 而是变为：
TP 轻减 / 100 × 1000
注意，TP 轻减与被敌人偷取 TP 时是否减少毫无关系''',
    '自动回复':
    '''TP 自动回复 / HP 自动回复
这两个属性基本是无关紧要的属性，只影响杀死每波敌人之后获取的 TP / HP 量''',
    '暴伤':
    '''物理暴击伤害 / 魔法暴击伤害
这两个属性不在人物面板中，但是确实是存在的
现阶段只存在于技能提供的 Buff 中
注意这两个属性和妹弓、镜华等人的技能说明中的暴击伤害是不同的，为了区别我们将技能说明中的暴击伤害称作“技能暴伤倍率”，将人物属性中的暴击伤害称作“角色暴伤加成”
最后 伤害公式为：
实际暴击伤害 = 基础技能伤害 × 技能暴伤倍率 × (1 + 角色暴伤加成)
实际暴击伤害(平A) = 角色面板攻击 × 2 × (1 + 角色暴伤加成)
对于绝大多数没有特别说明的技能，其技能暴伤倍率和平A一样等于 2
实战计算：
假设一个角色技能暴伤倍率是 4，她身上有两个角色暴伤 Buff 分别是 30% 50%
实际暴击伤害 = 基础技能伤害 × 4 × (1 + 30% + 50%)
该角色暴击时的伤害将达到 7.2 倍基础伤害''',
    '直接伤害类技能':
    '''直接伤害类技能基本公式：
原始伤害数值 = A × 攻击力 + B + C × 技能等级
实际伤害数值 = 原始伤害数值 / (1 + 目标防御力 / 100)
对于魔法系角色攻击力取魔法攻击力，物理系角色攻击力取物理攻击力
系数 A B C 因技能而异，如亚里沙第二次大招 A = 6.4 B = 80 C = 80，狗的大招 A = 4.8 B = 60 C = 60''',
    'dot类技能':
    '''DOT 类技能公式
DOT 类技能不计算防御力，且目前 DOT 类技能也不受攻击力影响，其基本公式为：
对于整数持续时间：
实际伤害数值 = (B + C × 技能等级) × (持续时间秒数 - 1)
对于非整数持续时间：
实际伤害数值 = (B + C × 技能等级) × floor(持续时间秒数)
floor 代表向下取整，系数 A B C 因技能而异''',
    '治疗类技能':
    '''治疗类技能
那些技能可以使用这个公式请参考属性篇中的回复量上升部分
治疗类技能基本公式：
实际治疗数值 = (A × 攻击力 + B + C × 技能等级) × (1 + 施法者的回复量上升 / 100)
对于魔法系角色攻击力取魔法攻击力，物理系角色攻击力取物理攻击力
系数 A B C 因技能而异''',
    '属性升降类技能':
    '''属性升降类技能(加速减速类除外)
此类技能不受攻击力加成
需要额外注意的一点，目前属性升降类技能是可以叠加的
基本公式为：
属性升降数值 = B + C × 技能等级
系数 A B C 因技能而异''',
    'tp上升':
    '''TP 上升
TP 上升是大家最关心的技能，每次升级 Rank 最头疼的属性之一，实际上还有一些暂时没有探明的部分，希望有大神能不吝赐教
角色的 TP 最大值为 1000
TP 上升影响所有获取 TP 手段，计算公式为:
实际获得 TP = 基础值 × (100 + TP 上升) / 100
根据日文wiki的数据 [[https://rwiki.jp/priconne_redive/%E8%A8%88%E7%AE%97%E5%BC%8F]]对该部分进行更新
其中 TP 来源分以下几种，对应的基础值计算方法如下
a) 被伤害时 TP 基础值 = (被伤害 HP / 最大 HP) × 0.5 × 1000
b) 击杀单位时获取 TP 基础值 = 200
c) 行动时获取 TP 基础值 = 90
d) 受到 TP 回复类技能影响时，基础值 = 技能的面板值
TP 上升存在断点，当角色不会受伤时，只有 TP 上升达到以下数值时才会让 UB 提前：12、24、39、59。''',
    '暴击':
    '''魔法暴击 / 物理暴击
暴击几率 = 面板暴击×0.05×0.01×自己等级 / 敌方等级
对于同等级敌人，可以简化为 100 暴击面板对应 5% 暴击几率''',
    'hp吸收':
    '''HP 吸收
实际吸收率 = 面板 HP 吸收 / (100 + 敌方等级 + 面板 HP 吸收)
实际吸收量 = 伤害量 × 实际吸收率
和一般的递减公式不同，HP 吸收中敌方等级也参与了计算
这里提一下妹法的大招，妹法大招的本质是在下一次攻击上附加一次大数值的 HP 吸收
110 级的妹法其数值为 440 HP 吸收，如果以 100 级敌方为目标，实际吸收率为 68.75%''',
    'HOT类技能':
    '''HOT 类技能
这类技能不受回复量上升影响
HOT 类技能基本公式为：
对于整数持续时间：
实际治疗数值 = (A × 攻击力 + B + C × 技能等级) × (持续时间秒数 - 1)
对于非整数持续时间：
实际治疗数值 = (A × 攻击力 + B + C × 技能等级) × floor(持续时间秒数)
系数 A B C 因技能而异''',
    '护盾类技能':
    '''护盾类技能
护盾类技能还可以细分为无效类护盾和吸收类护盾，区别就是是否将吸收的部分转化为治疗，目前已知的护盾类技能不受攻击力加成
护盾类技能基本公式：
实际吸收量或无效量 = B + C × 技能等级
系数 A B C 因技能而异''',
    'list':
    f'''-你游的各种计算公式-
※搬运自https://ngabbs.com/read.php?tid=15533965
=====属性说明=====
[攻击力] [防御力]
[回避] [命中]
[hp] [hp吸收]
[回复量上升] [自动回复]
[暴击] [暴伤]
[tp上升] [tp减轻]
=====技能说明=====
[直接伤害类技能]
[DOT类技能]
[治疗类技能]
[HOT类技能]
[护盾类技能]
[属性升降类技能](加速减速类除外)
[加速减速类技能]
[行动控制类技能]
[黑暗类技能]
============
【#pcr公式+[条目]】查阅相关说明，如#pcr公式tp上升
===其他查询关键词===
{OTHER_KEYWORDS}
※日台服速查请输入【pcr速查】'''
}


@sv.on_prefix(('pcr公式'), only_to_me=True)
async def pcrgongshi(bot, ev):
    keyword = ev.message.extract_plain_text()
    if not keyword:
        await bot.send(ev, pcrgshelp, at_sender=True)
    else:
        msg = pcrFORMULA.get(keyword)
        if msg is not None:
            await bot.send(ev, msg)
        else:
            pass
