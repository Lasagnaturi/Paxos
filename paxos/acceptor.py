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
  instances = {}


  def parse_msg(msg):
    phase, par1, par2, instance = msg.decode().split()
    module = __import__("acceptor")
    cls = getattr(module, "Acceptor")
    phase = getattr(cls, phase)
    return phase, par1, par2, instance

  def phase1a(par1, par2=None, instance=None):
    # IN THE SLIDES THIS IS THE PHASE 1B
    c_rnd = int(par1)
    print("Acceptor id", Acceptor.id ,": instance ",instance," phase1a, I received a proposal with c-rnd: ", c_rnd)
    if (c_rnd > Acceptor.instances[instance]['rnd']):
      print("Acceptor id", Acceptor.id, ": instance ",instance," phase1a I accept the proposal with c-rnd: ", c_rnd)

      Acceptor.instances[instance]['rnd'] = c_rnd
      msg = "phase1b " + str(Acceptor.instances[instance]['rnd']) + " " + str(Acceptor.instances[instance]['v_rnd']) + " " + str(Acceptor.instances[instance]['v_val']) + " " + str(instance)
      Acceptor.s.sendto(msg.encode(), Acceptor.config['proposers'])
    # else The acceptor ignore the request

  def phase2a(par1, par2=None, instance=None):
    # IN THE SLIDES THIS IS THE PHASE 2B
    c_rnd = int(par1)
    c_val = int(par2)

    if(c_rnd >= Acceptor.instances[instance]['rnd']):
      Acceptor.instances[instance]['v_rnd'] = c_rnd
      Acceptor.instances[instance]['v_val'] = c_val
      msg = "phase2b " + str(Acceptor.instances[instance]['v_rnd'])+ " " + str(Acceptor.instances[instance]['v_val']) + " None " + str(instance)
      Acceptor.s.sendto(msg.encode(), Acceptor.config['proposers'])

  def decision(par1, par2=None, instance=None):
    print ("decision")

  def newStackOfVariables(instance):
    rnd = 0
    v_rnd = 0
    v_val = None
    variables = {'rnd':rnd, 'v_rnd':v_rnd, 'v_val':v_val}
    Acceptor.instances[instance] = variables

  # Setting up communication and class variables.
  def acceptor(config, id):
    print('-> acceptor', id)
    Acceptor.config = config
    Acceptor.id = id
    Acceptor.r = mcast_receiver(config['acceptors'])
    # Acceptor.r.settimeout(15)
    Acceptor.s = mcast_sender()

    state = {}


    while True:
      try:
        msg = Acceptor.r.recv(2**16)
      except socket.timeout:
        print ("Acceptor id", id, ": OPS! Timeout exception")
        # break
      phase, par1, par2, instance = Acceptor.parse_msg(msg)
      if not instance in Acceptor.instances:
        Acceptor.newStackOfVariables(instance)
      phase(par1, par2, instance)
