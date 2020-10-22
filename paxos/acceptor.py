import queue
import socket
from connection import mcast_receiver, mcast_sender

class Acceptor():

  id = None
  config = None

  # receiver and sender
  r = None
  s = None

  # Paxos variables
  rnd = 0
  v_rnd = 0
  v_val = None

  def parse_msg(msg):
    phase, par1, par2 = msg.decode().split()
    module = __import__("acceptor")
    cls = getattr(module, "Acceptor")
    phase = getattr(cls, phase)
    return phase, int(par1), int(par2)

  def phase1a(par1, par2=None):
    c_rnd = par1
    print("phase1a, ho ricevuto una proposta con c-rnd: ", c_rnd)
    if (c_rnd > Acceptor.rnd):
      Acceptor.rnd = c_rnd
      msg = "phase1b " + str(Acceptor.rnd) + " " + str(Acceptor.v_rnd) + " " + str(Acceptor.v_val)
      Acceptor.s.sendto(msg.encode(), Acceptor.config['proposers'])
  #    else The acceptor ignore the request

  def phase2a(par1, par2=None):
    print("phase2a")

  def decision(par1, par2=None):
    print ("decision")

  # Setting up communication and class variables.
  def acceptor(config, id):
    print('-> acceptor', id)
    Acceptor.config = config
    Acceptor.id = id
    Acceptor.r = mcast_receiver(config['acceptors'])
    Acceptor.r.settimeout(15)
    Acceptor.s = mcast_sender()

    state = {}


    while True:
      try:
        msg = Acceptor.r.recv(2**16)
      except socket.timeout:
        print ("Proposed id", id, ": OPS! Timeout exception")
        break
      phase, par1, par2 = Acceptor.parse_msg(msg)
      phase(par1, par2)
