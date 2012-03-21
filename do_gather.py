from gather import setup_receiver
from twisted.internet import reactor

if __name__ == '__main__':
    setup_receiver()
    reactor.run()
