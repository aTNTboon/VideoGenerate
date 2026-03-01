import gc
import torch
import whisper
import re
from MyCode.util.Subtitle_Util.Base_Subtitle_Util import Base_Subtitle_Util
from MyCode.Setting import Setting


import numpy as np


def npfloat16_to_srt_time(seconds: np.float16) -> str:
    """
    将 np.float16 秒数转为 SRT 时间格式 HH:MM:SS,mmm
    """
    # 转为 Python float 以保证计算精度
    sec = float(seconds)

    hours = int(sec // 3600)
    minutes = int((sec % 3600) // 60)
    secs = int(sec % 60)
    millis = int(round((sec - int(sec)) * 1000))

    # 处理可能的 1000 毫秒进位
    if millis >= 1000:
        millis -= 1000
        secs += 1
    if secs >= 60:
        secs -= 60
        minutes += 1
    if minutes >= 60:
        minutes -= 60
        hours += 1

    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


import numpy as np
import torch


class Get_SubTitle_Util(Base_Subtitle_Util):
    def __init__(self):
        pass

    def close(self):
        if hasattr(self, "model"):
            del self.model
            self.model = None

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    def generate_src(self, videoName: str, content: str) -> str:
        srt_path = f"/article/subtitle/{videoName}.srt"

        # 生成 SRT 内容（单条字幕）
        srt_content = f"""{content}"""

        # 写入文件
        with open(srt_path, "w", encoding="utf-8") as f:
            f.write(srt_content)

        return srt_path


if __name__ == "__main__":
    wu = Get_SubTitle_Util()
    wu.generate_src(
        "1769600064_0",
        "刺耳的刹车声撕裂午后的宁静时，林衍正盯着手机银行里三位数的余额发呆。重型卡车的阴影像天幕坍塌般覆来，他甚至能看清司机惊慌变形的脸，以及自己飞离地面时，口袋里刚皱巴巴塞进去的兼职工资条。“叮——检测到致命创伤触发，因果结算启动。”冰冷的机械音直接砸进脑海，没有丝毫缓冲。林衍的意识停留在失重的瞬间，眼前却突兀弹出一块半透明的蓝色面板，像极了他上班摸鱼时看的股票交易软件，只是上面的内容足以让任何人心胆俱裂。【结算单编号：SY-二零二六零一二七-零零一】【目标结果：林衍，男性，二四岁，即时性多器官衰竭死亡】【触发原因：机动车撞击（第三方过失）】【阵列记录：监控三二四一号、路人目击×三、生物体征衰减九八百分号】【到账时点：当前时刻（延迟倒计时：零零:零零:零三）】【是否启用“结果延期”功能？】倒计时的红色数字疯狂跳动，每一下都像敲在心脏上。林衍大脑一片空白，求生的本能压过了对这诡异面板的疑惑——管它是什么，只要能活。他几乎是凭着本能在意识里呐喊：“启用！”",
    )


#'面板瞬间刷新，新增一串可操作选项，冰冷的机械音又添了几分戏谑，像是在看一场荒诞的赌局：“套利系统绑定成功，新手权限解锁。当前可延期对象：即时死亡。请选择延期时长，时长对应即时消耗与未来倍率。”【延期时长选项】一. 一小时：消耗当前寿命一天，未来结算倍率一.零（无加成）二. 二四小时：消耗当前寿命三天，未来结算倍率一.二（死亡痛苦加成二零百分号）三. 七天：消耗当前寿命一零天，未来结算倍率一.五（触发单次因果反噬预警）林衍的意识飞速冷静下来。他是个刚毕业半年的职场菜鸟，兼着两份工还完房租就所剩无几，早已习惯在精打细算里抠生活，这种关乎生死的“成本核算”，竟让他莫名找回了核对报销单的理智。一小时太短，刚够确认处境却没时间做任何准备；七天虽足，但一零天寿命的消耗和一.五倍倍率风险太高，他甚至不知道未来该怎么抵消这份加成。“选二四小时！”【确认选择：延期时长二四小时。即时消耗扣除：寿命三天（剩余寿命：六二年一八七天）。未来结算倍率一.二。】【到账时点更新：二零二六年一月二八日一四:三七:二一】'
#'1769600064_1'

#'面板消散的瞬间，失重感骤然消失，剧烈的疼痛如同潮水般席卷全身。林衍重重摔在冰冷的路面上，肋骨断裂的钝痛让他蜷缩成一团，嘴里涌出腥甜的血液，但他却死死盯着自己能动的手指——他还活着。周围早已围满了路人，有人打一二零，有人对着卡车司机指指点点，混乱的声音里，林衍的脑海里再次响起系统的声音，这次的语气带着明显的调侃：“新手提示：延迟仅改写结果到账时点，不抵消过程伤害哦。当前肉体伤害未触发结算，是否顺带延期？消耗：寿命一天，倍率维持一.零。”林衍咬着牙摇头。疼痛是提醒，也是筹码。他现在要的不是止痛，是时间。救护车的鸣笛声由远及近，他躺在担架上被抬起来时，目光扫过路边的银行广告牌——“合理规划负债，享受时间红利”。一个疯狂的念头在他心里滋生。死亡可以延期，那债务呢？那些压得他喘不过气的房租、网贷，是不是也能像这笔“死亡账单”一样，拆成未来的“现金流”？'
#'1769600064_2'
