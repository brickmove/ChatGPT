from flask import Flask, Response, request, jsonify
import json, configparser, os
from revChatGPT.V1 import Chatbot

app = Flask(__name__)
config = configparser.ConfigParser()
config.read('../config/config.ini')
_access_token = config.get('gpt', 'access_token')
_model = config.get('gpt', 'model')
_email = config.get('gpt', 'email')
_password = config.get('gpt', 'password')
_collect_analytics = config.get('gpt', 'collect_analytics')
_port = config.get('host', 'port')
_debug = config.get('option', 'debug')

# 初始化 Chatbot
chatbot = Chatbot(config={
    "email": _email,
    "password": _password,
    "access_token": _access_token,
    "model": _model,
    "collect_analytics": _collect_analytics
})

os.environ['CHATGPT_BASE_URL'] = 'http://13.58.240.216:28997/'
@app.route('/api/faqs/chat', methods=['POST'])
def chat():
    # 从请求参数中获取要查询的文本
    data = request.get_json()
    prompt = data.get('prompt')
    conversation_id = data.get('conversation_id')
    model = data.get('model')
    collect_analytics = data.get('collect_analytics')
    parent_id = data.get('parent_id')
    timeout = data.get('timeout')

    ask_param = {'prompt': prompt}
    if model is not None:
        chatbot.config['model'] = model

    if collect_analytics is not None:
        chatbot.config['collect_analytics'] = collect_analytics

    if conversation_id is not None:
        ask_param['conversation_id'] = conversation_id

    if parent_id is not None:
        ask_param['parent_id'] = parent_id

    if timeout is not None:
        ask_param['timeout'] = timeout

    # 向 Chatbot 发送问题并获取回答
    prev_text = ""
    answer = ""
    conv_id = ""
    for data in chatbot.ask(**ask_param):
        message = data["message"][len(prev_text):]
        answer += message
        prev_text = data["message"]
        conv_id = data["conversation_id"]
    
    if conversation_id is None:
        conversation_id = conv_id

    # 返回回答
    return jsonify({'answer': f'{answer}', 'conversation_id': f'{conversation_id}'})

def answer(body):
    input_text = body["prompt"]
    prev_text = ""
    
    for data in chatbot.ask(input_text):
        message = data["message"][len(prev_text):]
        yield f"data: {json.dumps({'answer': message}, ensure_ascii=False)}\n\n"
        prev_text = data["message"]

@app.route('/stream', methods=['POST'])
def stream():
    body = request.json
    return Response(answer(body), content_type='text/event-stream')

if __name__ == '__main__':
    #app.run(host="127.0.0.1", port=10066, debug=True)
    app.run(host="0.0.0.0", port=10066, debug=True)
