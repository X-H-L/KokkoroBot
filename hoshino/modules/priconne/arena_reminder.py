from hoshino.service import Service

svtw = Service('pcr-arena-reminder-tw', enable_on_default=False, help_='背刺时间提醒(台B)', bundle='pcr订阅')
svjp = Service('pcr-arena-reminder-jp', enable_on_default=False, help_='背刺时间提醒(日)', bundle='pcr订阅')
svexpt = Service('pcr-exp-reminder-tw', enable_on_default=False, help_='提醒买药小助手(台B)', bundle='pcr订阅')
svclant = Service('pcr-clan-reminder-tw', enable_on_default=False, help_='提醒会战小助手(台)', bundle='pcr订阅', visible=False)
msgbc = '主さま、准备好背刺了吗？'
msgexp = '主さま、商店的经验药刷新了哦'
msgclan = '主さま、公会战开始了哦，和伙伴一起努力吧'
msgclanp = '[CQ:image,file=my\kkl\daghuizhanle.jpg]'

@svtw.scheduled_job('cron', hour='14', minute='45')
async def pcr_reminder_tw():
    await svtw.broadcast(msgbc, 'pcr-reminder-tw', 0.2)

@svjp.scheduled_job('cron', hour='13', minute='45')
async def pcr_reminder_jp():
    await svjp.broadcast(msgbc, 'pcr-reminder-jp', 0.2)

@svexpt.scheduled_job('cron', hour='0,6,12,18')
async def pcr_expreminder_tw():
    await svexpt.broadcast(msgexp, 'pcr-expreminder-tw', 0.2)

@svclant.scheduled_job('cron', month='1,3,5,7,8,10,12', day='25-31', hour='5')
async def pcr_clanreminder_tw():
    await svclant.broadcast(msgclanp, 'pcr-clanreminder-tw', 0.2)

@svclant.scheduled_job('cron', month='4,6,9,11', day='24-30', hour='5')
async def pcr_clanreminder_tw():
    await svclant.broadcast(msgclanp, 'pcr-clanreminder-tw', 0.2)

@svclant.scheduled_job('cron', month='2', day='22-28', hour='5')
async def pcr_clanreminder_tw():
    await svclant.broadcast(msgclanp, 'pcr-clanreminder-tw', 0.2)
