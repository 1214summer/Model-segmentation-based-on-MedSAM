import os
from skimage import io
import torch
from flask import Flask, request, send_file,jsonify
import requests
from flask_restful import Resource
from predict import MedSAMInference
from flask_cors import CORS
import base64
from openai import OpenAI
from messages import AddMsg

client = OpenAI()
app = Flask(__name__)
CORS(app)
inference = MedSAMInference()

#填写你的API_KEY
api_key = ""
base64_img =""

#解码图像
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

#解码图像
def img_stream(img_path):
    """
    工具函数:
    获取本地图片流
    :param img_local_path:文件单张图片的本地绝对路径
    :return: 图片流
    """
    img_stream = ''
    with open(img_path, 'rb') as img_f:
        img_stream = img_f.read()
        img_stream = base64.b64encode(img_stream).decode()
    return img_stream

@app.route('/predict', methods=['POST'])
def predict():
    #获取参数
    img = request.files['image']
    filename = img.filename

    box_coords = request.form.get('box_coords', None)
    prompt = None

    if box_coords:
        prompt = [int(coord) for coord in box_coords.split(',')]
    else:
        return jsonify({"message": "无prompt信息"})

    #保存上传的图片和生成的图片
    img.save('assets/uploads/' + filename)
    segmented_img_path, mask_img_path = inference.run_inference('assets/uploads/' + filename, prompt, "assets/")
    img_base64 = encode_image(segmented_img_path)
    mask_base64 = img_stream(mask_img_path)
    base64_img = img_base64


    #开始向gpt传入图像
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload={
        "model" : "gpt-4-turbo",
        "messages" : [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "请根据框里的图像分析病情"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_img}"
                        }
                    }
                ]
            }
        ],
      "max_tokens" : 800
    }

    #保存上传的图像数据
    content = payload['messages'][0]['content']
    add_meg1 = AddMsg("user", content)
    add_meg1.add()

    #发送请求
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    result = response.json()
    print(result)
    content = result['choices'][0]['message']['content']
    print(content)

    #保存gpt生成的回答
    add_meg2 = AddMsg("assistant",content)
    add_meg2.add()

    return jsonify({"success": '处理成功', "prompt": prompt, "image": img_base64, "mask": mask_base64, "response": result})


@app.route('/chat',methods=['POST'])
def chat():
    data = request.json
    user_text = data.get('text', '')
    user_input = user_text
    mes1 = AddMsg("user",user_input)
    mes1.add()
    messages = mes1.get()
    response = client.chat.completions.create(model="gpt-4-turbo", messages=messages)
    content = response.choices[0].message.content
    print(content)
    mes2 = AddMsg("assistant",content)
    mes2.add()
    # 返回处理结果
    return jsonify({'message': 'Processed data successfully',"response": content})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
