# 编写人: Bonnie
# 开发时间：2024/4/22 21:43
messages = [
    {"role": "system", "content": "你现在是一个图像诊断医生,需要对用户提供的图像进行病情分析，特别是针对标注处的框里的内容"},
]

class AddMsg:
    def __init__(self,role,content):
        self.content = content
        self.role = role


    def add(self):
        messages.append({"role": self.role, "content": self.content})

    def get(self):
        return messages

