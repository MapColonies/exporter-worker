from flask import Flask
import logging
app = Flask(__name__)
host_ip = "0.0.0.0"
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
    app.logger.disabled = True
    log = logging.getLogger('werkzeug')
    log.disabled = True
    app.run(host=host_ip)
