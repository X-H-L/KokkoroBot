from hoshino import Service

sv_help = '''
[@pcr速查] 常用网址/图书馆
[@bcr速查] B服萌新攻略
[@日rank] rank推荐表
[@台rank] rank推荐表
[@陆rank] rank推荐表
有新推荐表了记得at蓝红心
[@挖矿15001] 矿场余钻
[@黄骑充电] 黄骑1动规律
[@露娜充电] 露娜充电规律
[@一个顶俩] 台服接龙小游戏
[@谁是霸瞳] 角色别称查询
[@pcr公式] 你游各种计算公式
[@多目标boss机制] 获取多目标boss机制介绍
[@公会战作业] 会战时更新，有作业请私聊蓝红心
[#活动作业]活动时更新，有作业请私聊蓝红心
[@兰德索尔最强/弱七人] 实际上这俩图已经基本过时了，图一乐吧
[@兰德索尔年龄/胸围/学业分布表] 只有年龄表是最新版本
[@露娜塔是啥] 是露娜塔
[@点兔刀是啥] 看看怎么出点兔刀
[@furry分级] furry分级表
'''.strip()

sv = Service('pcr-query', help_=sv_help, bundle='pcr查询')

from .query import *
from .whois import *
from .miner import *
