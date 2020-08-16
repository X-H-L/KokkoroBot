import os
from datetime import datetime
from hoshino import Service
from PIL import Image, ImageFont, ImageDraw
import base64
sv = Service('nowtime', enable_on_default=True, help_='[@报时] 看看现在几点')

@sv.on_keyword(('报时', '几点了', '现在几点', '几点钟啦', '几点啦'), only_to_me=True)
async def showtime(bot, ev):
    now = datetime.now()
    hour = now.hour
    minute = now.minute
    hour_str = f' {hour}' if hour < 10 else str(hour)
    minute_str = f' {minute}' if minute < 10 else str(minute)
    template_path = os.path.join(os.path.dirname(__file__), 'data/nowtime/template.jpg')
    save_path = os.path.join(os.path.dirname(__file__), 'data/nowtime/nowtime.jpg')
    add_text(template_path, save_path, f'{hour_str}点{minute_str}分', textsize=95, textfill='black', position=(305, 255))  # 修改此行调整文字大小位置
    '''
    textsize文字大小
    textfill 文字颜色，black 黑色，blue蓝色，white白色，yellow黄色，red红色
    position是距离图片左上角偏移量，第一个数是宽方向，第二个数是高方向
    f'{hour_str}\n点\n{minute_str}\n分\n了\n !' 代表报时文本，已设置为竖排，\n为换行  
    '''
    base64_str = pic_to_b64(save_path)
    reply = f'[CQ:image,file={base64_str}]'
    await bot.send(ev, reply, at_sender=False)

def add_text(template_path, save_path, text: str, textsize: int, font='data/nowtime/msyh.ttf', textfill='black', position: tuple = (0, 0)):
    #textsize 文字大小
    #font 字体，默认微软雅黑
    #textfill 文字颜色，默认黑色
    #position 文字偏移（0,0）位置，图片左上角为起点
    font_path = os.path.join(os.path.dirname(__file__), font)
    print(font_path)
    img_font = ImageFont.truetype(font=font_path, size=textsize)
    with Image.open(template_path) as img:
        draw = ImageDraw.Draw(img)
        draw.text(xy=position, text=text, font=img_font, fill=textfill)
        # save_path = save_path
        img.save(save_path)

def pic_to_b64(pic_path: str) -> str:
    with open(pic_path, 'rb') as f:
        base64_str = base64.b64encode(f.read()).decode()
    return 'base64://' + base64_str
