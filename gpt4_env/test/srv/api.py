# api.py
from flask import Flask, jsonify, request, Response, stream_with_context
import json, configparser
from revChatGPT.V1 import Chatbot

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

app = Flask(__name__)

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
    prompt = data.get('prompt')
    conversation_id = data.get('conversation_id')
    model = data.get('model')
    collect_analytics = data.get('collect_analytics')
    parent_id = data.get('parent_id')
    timeout = data.get('timeout')
    prev_text = ""
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

    for data in chatbot.ask(ask_param):
        message = data["message"][len(prev_text):]
        yield f"data: {json.dumps({'answer': message}, ensure_ascii=False)}\n\n"
        prev_text = data["message"]

@app.route('/api/faqs/chat_stream', methods=['POST'])
def chat_stream():
    message = request.get_json()
    if message is not None and len(message) > 0:
        def generate_response():
            prev_text = ""
            conversation_id = ""
            prompt = message.get('prompt')
            for data in chatbot.ask(prompt):
                response = data["message"][len(prev_text):]
                prev_text = data["message"]
                if data["conversation_id"] is not None and not conversation_id.strip():
                    conversation_id = data["conversation_id"]
                    insert_conversation(conversation_id)
                    print(f"conversation_id: {conversation_id}")
                json_data = json.dumps({"answer": response, "conversation_id": conversation_id}, ensure_ascii=False)
                event = f"{json_data}\n\n"
                yield event
            yield 'event: close\ndata: Chatbot closed.\n\n'

        # 使用 stream_with_context() 方法将 SSE 事件立即发送到客户端
        return Response(stream_with_context(generate_response()), mimetype='text/event-stream')
    else:
        return 'Empty message'

@app.route('/api/faqs/conversationList', methods=['GET'])
def conversationList():
    conversation_ids = chatbot.get_conversations();
    return jsonify({'result': f'{conversation_ids}'})

@app.route('/api/faqs/conversationClear', methods=['POST'])
def conversationClear():
    data = request.get_json()
    conversation_id = data.get('conversation_id')
    clear_conversations(conversation_id)
    return jsonify({'conversation_id': f'{conversation_id}'})

@app.route('/api/faqs/conversationDel', methods=['DELETE'])
def conversationDel():
    data = request.get_json()
    conversation_id = data.get('conversation_id')
    delete_conversation(conversation_id)
    return jsonify({'conversation_id': f'{conversation_id}'})