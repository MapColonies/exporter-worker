from flask import Flask
from src.config import read_config
app = Flask(__name__)
__config = read_config()
host_ip = __config['probe']['host_ip']
readiness = True


@app.route('/health')
def health():
    if readiness is True:
        return 200
    else:
        return 500


def start():
    app.run(host=host_ip)

