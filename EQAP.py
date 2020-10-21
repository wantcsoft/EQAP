from EQAPBox import EQAPBox
import app
from threading import Thread


def startWeb():
    app.app.run(host='0.0.0.0', port=5000)

def startEQAP():
    eqap = EQAPBox()
    eqap.Start()


if __name__ == '__main__':

    webThread = Thread(target=startWeb, args=())
    EQAPThread = Thread(target=startEQAP, args=())
    webThread.start()
    EQAPThread.start()


