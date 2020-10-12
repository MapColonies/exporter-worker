from flask import Flask
from src.config import read_config
app = Flask(__name__)
__config = read_config()
host_ip = __config['probe']['host_ip']
liveness = True
readiness = True


@app.route('/worker/liveness')
def liveness_check():
    if liveness is True:
        return "Ok", 200
    else:
        return "Internal Error", 500


@app.route('/worker/readiness')
def readiness_check():
    if readiness is True:
        return "Ok", 200
    else:
        return "Internal Error", 500


def start():
    app.run(host=host_ip)
