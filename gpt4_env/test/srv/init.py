# init.py
import json, threading

# 初始化对话列表
conversation_ids = []

# 定时器任务函数，每隔一段时间清理 conversation_ids 列表
def clean_conversation_ids():
    global conversation_ids
    threading.Timer(60*60*24*7, clean_conversation_ids).start()  # 每隔 24 * 7 小时运行一次
    conversation_ids = [c_id for c_id in conversation_ids if c_id.strip()]


# 启动定时器任务
#clean_conversation_ids()

def insert_conversation(id):
    global conversation_ids
    convids = chatbot.get_conversations()
    data_list = json.loads(convids)['result']
    data_dict = {data['id']: {'create_time': data['create_time'], 'update_time': data['update_time'], 'title': data['title']} for data in data_list}
    if data_dict:
        conversation_ids.append(data_dict)

def init_conversation():
    global conversation_ids
    convids = chatbot.get_conversations()
    conversation_ids = json.loads(convids)['result']