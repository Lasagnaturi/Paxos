import queue
import socket
from connection import mcast_receiver, mcast_sender

def learner(config, id):
  r = mcast_receiver(config['learners'])
  while True:
    msg = r.recv(2**16)
    print (msg)
    sys.stdout.flush()