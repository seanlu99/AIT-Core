import sys
from handler import Handler

sys.modules['ait.serv'].DEFAULT_XSUB_URL = "tcp://*:5559"
sys.modules['ait.serv'].DEFAULT_XPUB_URL = "tcp://*:5560"
