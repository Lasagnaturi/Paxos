import queue
import socket
import sys
from connection import mcast_receiver, mcast_sender

class Learner():

  id = None
  config = None
  decided_values = [None]

  # receiver and sender
  r = None
  s = None

  def parse_msg(msg):
    phase, par1 = msg.decode().split()
    module = __import__("learner")
    cls = getattr(module, "Learner")
    phase = getattr(cls, phase)
    return phase, par1

  def decision(par1):
    value = int(par1)
    if(value != Learner.decided_values[-1]):
      Learner.decided_values.append(value)
      print("Learner id:", Learner.id," decided value: ", value)

  def learner(config, id):
    print('-> learner', id)
    Learner.config = config
    Learner.id = id
    Learner.r = mcast_receiver(config['learners'])
    Learner.r.settimeout(30)
    Learner.s = mcast_sender()

    while True:
      try:
        # print("uagliò sto aspettando la decisione")
        msg = Learner.r.recv(2**16)
      except socket.timeout:
        print ("Learner id", id, ": OPS! Timeout exception")
        break
      phase, par1 = Learner.parse_msg(msg)
      phase(par1)
      # print("uagliò qua non arriva nu cazzc")
    #
    # r = mcast_receiver(config['learners'])
    # while True:
    #   msg = r.recv(2**16)
    #   print (msg)
    #   sys.stdout.flush()