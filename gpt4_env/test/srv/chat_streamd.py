from flask import Flask, request, Response, make_response
import configparser, json, threading
from revChatGPT.V1 import Chatbot

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

# 初始化 Chatbot
chatbot = Chatbot(config={
    "email": _email,
    "password": _password,
    "access_token": _access_token,
    "model": _model,
    "collect_analytics": _collect_analytics
})

def answer(ask_param):
    prev_text = "" 
    conversation_id = ""
    for data in chatbot.ask(**ask_param):
        message = data["message"][len(prev_text):]
        if data["conversation_id"] is not None and not conversation_id.strip():
            conversation_id = data["conversation_id"]
        json_data = json.dumps({"message": message, "conversation_id": conversation_id}, ensure_ascii=False)
        yield f"data: {json_data}\n\n"
        prev_text = data["message"]

@app.route('/api/faqs/chat_stream', methods=['POST'])
def chat_stream():
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

@app.route('/api/faqs/conversationClear', methods=['POST'])
def conversationClear():
    data = request.get_json()
    conversation_id = data.get('conversation_id')
    clear_conversations(conversation_id)
    return jsonify({'conversation_id': f'{conversation_id}'})

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=10067, debug=True)
    #app.run(host="0.0.0.0",port=10067)
