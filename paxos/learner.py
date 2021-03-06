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
  r2 = None
  s = None

  values = []
  instances = []

  temp_values = []
  temp_instances = []

  def parse_msg(msg):
    phase, par1, par2 = msg.decode().split()
    module = __import__("learner")
    cls = getattr(module, "Learner")
    phase = getattr(cls, phase)
    return phase, par1, par2

  def catch_up(value, instance):
    # print("catch up chiamato ")
    #print("value", value, "instance", instance)
    if instance > 0 and instance-1 not in Learner.instances:
      msg = "getOlderValue " + str(instance-1) + " None None None"
      Learner.s.sendto(msg.encode(), Learner.config['proposers'])
      #print("ritorno false")
      return False
    #print("ritorno true")
    return True

  def store(value, instance):
    #print("ATTENZIONEEE ENTRO IN STORE")
    if(instance not in Learner.instances):
      Learner.values.append(value)
      Learner.instances.append(instance)
      print(value)
      sys.stdout.flush()


  def decision(par1, par2):
    #print("decision chiamato ")
    value = int(par1)
    instance = int(par2)
    #print("lenght ", len(Learner.values))
    if (not Learner.catch_up(value, instance)):
      #print("catch up necessario ")
      Learner.temp_values.append(value)
      Learner.temp_instances.append(instance)

    elif(len(Learner.values) == 0 or value != Learner.values[-1]):
      #print("non serve il catch")
      Learner.store(value, instance)

      temp_inst = instance+1
      while temp_inst in Learner.temp_instances:
        index = Learner.temp_instances.index(temp_inst)
        val = Learner.temp_values[index]
        Learner.temp_instances.remove(temp_inst)
        Learner.temp_values.remove(val)
        Learner.store(val, temp_inst)
        temp_inst += 1
    #else:
      #print("posso tornare senza fare nulla")
    # #print("Learner id:", Learner.id," decided value: ", value)

  def learner(config, id):
    #print('-> learner', id)
    Learner.config = config
    Learner.id = id
    Learner.r = mcast_receiver(config['learners'])
    Learner.r2 = mcast_receiver(config['learners'])
    Learner.r2.settimeout(15)
    Learner.s = mcast_sender()

    while True:
      # try:
        # #print("uagliò sto aspettando la decisione")
      msg = Learner.r.recv(2**16)
      # #print("ricevuto un un messaggiooo")
      # except socket.timeout:
        # #print ("Learner id", id, ": OPS! Timeout exception")
        # break
      phase, par1, par2 = Learner.parse_msg(msg)
      phase(par1, par2)
