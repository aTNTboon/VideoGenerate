

import re
import re

import re

def num_and_math_to_chinese(s: str) -> str:
    """
    将数字、百分比、小数和数学符号转换为中文表达
    支持：
    - 整数、0~99999
    - 小数
    - 百分比
    - 常用数学符号：+ - * / = < > <= >= != == 
    """

    digit_map = "零一二三四五六七八九"
    unit_map = ["", "十", "百", "千", "万"]

    def int_to_cn(n: int) -> str:
        if n == 0:
            return digit_map[0]
        res = ""
        str_n = str(n)
        length = len(str_n)
        zero_flag = False
        for i, ch in enumerate(str_n):
            num = int(ch)
            pos = length - i - 1
            if num == 0:
                zero_flag = True
            else:
                if zero_flag:
                    res += digit_map[0]
                    zero_flag = False
                res += digit_map[num] + unit_map[pos]
        if res.startswith("一十"):
            res = res[1:]
        if res.endswith("零"):
            res = res[:-1]
        return res

    s = s.strip()

    # 先处理负数
    negative = False
    if s.startswith("-"):
        negative = True
        s = s[1:]

    # 替换百分比
    if s.endswith("%"):
        s = s.rstrip("%")
        return ("负" if negative else "") + "百分之" + num_and_math_to_chinese(s)

    # 替换数学符号（先长符号，避免被短符号覆盖）
    symbol_map = {
        "<=": "小于等于",
        ">=": "大于等于",
        "!=": "不等于",
        "==": "等于",
        "<": "小于",
        ">": "大于",
        "+": "加",
        "-": "杠",
        "*": "乘",
        "/": "除",
        "=": "等于",
    }

    # 用正则安全替换
    for sym, cn in sorted(symbol_map.items(), key=lambda x: -len(x[0])):  # 长的先替换
        s = s.replace(sym, cn)

    # 处理小数点
    if "." in s:
        parts = s.split(".")
        integer_part = parts[0]
        decimal_part = parts[1]
        cn_integer = int_to_cn(int(integer_part)) if integer_part.isdigit() else integer_part
        cn_decimal = "".join(digit_map[int(d)] for d in decimal_part if d.isdigit())
        return ("负" if negative else "") + cn_integer + "点" + cn_decimal

    # 处理整数
    if s.isdigit():
        n = int(s)
        return ("负" if negative else "") + int_to_cn(n)

    return ("负" if negative else "") + s



def self_parse(text,uid,theme_id):
        text = text.strip()
        m = re.search(r"<theme>(\d+)</theme>", text)

        if(theme_id<0): 
            if m:
                theme_id = int(m.group(1))
        m=re.search(r'<story>(.*)</story>', text,re.DOTALL)
        if not m:
            raise Exception("no story")
        scenes_txt=m.group(1)
        if not scenes_txt:
            raise Exception('no scene')
        scenes = re.findall(r'<scene\s+mood="(\d+)">(.*?)</scene>', scenes_txt, re.DOTALL)
        new_scenes = []
        for mood, content in scenes:
            mood_cn = num_and_math_to_chinese(mood)  # 将数字转换为中文
            # 替换内容里的数字、百分比、小数点
            def replace_number(match):
                return num_and_math_to_chinese(match.group())
            
            content_cn = re.sub(r'\d+(\.\d+)?%?', replace_number, content)
            new_scenes.append((mood_cn, content_cn))
        json_list = []
        for mood, scene_text in new_scenes:
            json_list.append({
                "uid": uid,
                "theme_id": theme_id,
                "mood": int(mood),
                "scene": scene_text.strip()
            })
        return json_list


if __name__ == '__main__':
    uid=1
    json={}
    json= self_parse(
        """
<theme>2</theme> <mood>2</mood> <story> <scene mood="2">2022年的秋天，淅淅沥沥的小雨从灰色的天空落下，打湿了城市街道。胡同里，十七八岁的少年庆尘和一位老爷子坐在超市雨棚下对弈，雨棚之外一片灰暗，雨水把地面浸成浅黑色，雨棚下却留着一块干净的净土。棋盘上杀机毕露，少年平静地提醒老头“将军”，老头无奈认输。庆尘拿了20块钱，坐回棋盘旁复盘，两人之间形成了一种奇异的默契——庆尘教棋，老头输钱学棋。</scene>

<scene mood="2">雨仍飘落，胡同里的路人、公交、孩子和妇人交错出现，庆尘却像时间长河里抽取存档一般，把每一个细节都记在脑海。他认真复盘，讲解弃马十三招的精髓，老头陷入沉思。庆尘淡然地回答老头的问题，谈笑之间显得像老师一样，而老头也全然接受。</scene>

<scene mood="2">雨渐停，胡同尽头出现了一对带着孩子的夫妻，手里提着蛋糕盒。庆尘看到他们的喜悦神色后默默离开，留下老头坐在雨棚下。夫妻对话中流露出庆尘与父母之间微妙的关系：母亲张婉芳为他生活费，他却依然精打细算地生活，父亲赌博且不负责任，老头调侃他的独立和自立。</scene>

<scene mood="2">庆尘回到家，76平米的老式公寓里昏暗沉静。他掏出手机拨打父亲，却得到敷衍的回答。他低头看着手臂上白色倒计时——倒计时5:58:13，像嵌在血肉里的荧光纹路，无声地提醒他将迎来未知事件。庆尘开始为倒计时做准备，买粮食、药品、工具，安排好厨房的刀具，布置家里以应对可能的危险。他清楚，唯一能依靠的只有自己。</scene>

<scene mood="2">夜色渐浓，庆尘在都市街道上骑自行车准备寻人，经过酒店、小区和桥梁，最终拨打110举报赌博行为，放下心来回家。他重新检视准备工作，考虑是否去人多的地方，但最终选择留在家里等待。倒计时剩余不到半小时，他写下遗书，做好心理准备。随着最后的倒计时结束，屋子里的时间、光线和空间突然静止，庆尘手握剔骨刀环视四周，书桌、房间消失，陷入黑暗。</scene>

<scene mood="2">在黑暗中，世界碎片重新拼凑，庆尘发现自己置身陌生环境，手中的剔骨刀消失，手臂上的白色纹路变为“回归倒计时48:00:00”，他明白自己获得了新的两天时间，仿佛重新开始新的未知旅程。</scene> </story>



"""
         ,uid,-1)
    print(json)