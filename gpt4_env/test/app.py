# app.py
from srv import api, init

app = Flask(__name__)
  
if __name__ == '__main__':
    app.run(host="127.0.0.1", port=_port, debug=_debug)

