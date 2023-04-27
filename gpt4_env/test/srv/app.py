from flask import Flask, request, Response
import configparser
import json
from revChatGPT.V1 import Chatbot

app = Flask(__name__)

# 读取配置文件中的变量
config = configparser.ConfigParser()
config.read('../config/config.ini')
access_token = config.get('gpt', 'access_token')
model = config.get('gpt', 'model')
email = config.get('gpt', 'email')
password = config.get('gpt', 'password')
collect_analytics = config.get('gpt', 'collect_analytics')
port = int(config.get('host', 'port'))
debug = config.getboolean('option', 'debug')

# 初始化 Chatbot
chatbot = Chatbot(config={
    "email": email,
    "password": password,
    "access_token": access_token,
    "model": model,
    "collect_analytics": collect_analytics
})

def answer(body):
    prompt = body["prompt"]
    prev_text = ""
    conversation_id = ""
    
    for data in chatbot.ask(prompt):
        message = data["message"][len(prev_text):]
        
        if data["conversation_id"] is not None and not conversation_id.strip():
            conversation_id = data["conversation_id"]
        
        json_data = json.dumps({"message": message, "conversation_id": conversation_id}, ensure_ascii=False)
        yield f"data: {json_data}\n\n"
        
        prev_text = data["message"]

@app.route('/api/faqs/chat_stream', methods=['POST'])
def chat_stream():
    message = request.get_json()
    
    if message is not None and len(message) > 0:
        return Response(answer(message), mimetype='text/event-stream')
    else:
        return 'Empty message'

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10067)
