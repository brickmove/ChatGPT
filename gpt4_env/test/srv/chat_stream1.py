from flask import Flask, request, jsonify, Response, make_response
import configparser
from revChatGPT.V1 import Chatbot
import json, os, time

app = Flask(__name__)

# 读取配置文件中的 access_token 变量
config = configparser.ConfigParser()
config.read('../config/config.ini')
_access_token = config.get('gpt', 'access_token')
_model = config.get('gpt', 'model')
_email = config.get('gpt', 'email')
_password = config.get('gpt', 'password')
_collect_analytics = config.get('gpt', 'collect_analytics')
_port = config.get('host', 'port')
_debug = config.get('option', 'debug')
#os.environ['CHATGPT_BASE_URL'] = 'http://127.0.0.1:28997/'
#os.environ['CHATGPT_BASE_URL'] = 'http://13.58.240.216:28997/api/'

diff_time = 0
# 初始化 Chatbot
chatbot = Chatbot(config={
    "email": _email,
    "password": _password,
    "access_token": _access_token,
    "model": _model,
    "collect_analytics": _collect_analytics
})

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

def answer(ask_param):
    prev_text = ""
    conversation_id = ""
    global diff_time
    for data in chatbot.ask(**ask_param):
        message = data["message"][len(prev_text):]
        if data["conversation_id"] is not None and not conversation_id.strip():
            conversation_id = data["conversation_id"]
        json_data = json.dumps({"message": message, "conversation_id": conversation_id}, ensure_ascii=False)
        yield f"data: {json_data}\n\n"
        print("json_data: ", json_data, "time: ", time.time() - diff_time, "s")
        diff_time = time.time()
        prev_text = data["message"]

@app.route('/api/faqs/chat_stream', methods=['POST'])
def chat_stream():
    print("*******start time: ", time.time(), "s********")
    global diff_time
    diff_time = time.time()
    
    body = request.get_json()
    prompt = body.get('prompt')
    conversation_id = body.get('conversation_id')
    model = body.get('model')
    collect_analytics = body.get('collect_analytics')
    parent_id = body.get('parent_id')
    timeout = body.get('timeout')
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
    if body is not None and len(body) > 0:
        response = make_response(answer(ask_param), 200)
        response.headers["Content-Type"] = "text/event-stream"
        response.headers["Cache-Control"] = "no-cache"
        return response
    else:
        return 'Empty message'

@app.route('/api/faqs/chat_list', methods=['GET'])
def conversationList():
    conversation_ids = chatbot.get_conversations();
    return jsonify({'result': f'{conversation_ids}'})

@app.route('/api/faqs/chat_clear', methods=['POST'])
def conversationClear():
    data = request.get_json()
    conversation_id = data.get('conversation_id')
    chatbot.clear_conversations(conversation_id)
    return jsonify({'conversation_id': f'{conversation_id}'})

@app.route('/api/faqs/chat_del', methods=['DELETE'])
def conversationDel():
    data = request.get_json()
    conversation_id = data.get('conversation_id')
    chatbot.delete_conversation(conversation_id)
    return jsonify({'conversation_id': f'{conversation_id}'})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=_port, debug=_debug)

