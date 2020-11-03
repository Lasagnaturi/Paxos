import queue
import socket
import sys
from connection import mcast_receiver, mcast_sender

def client(config, id):


  print ('-> client ', id)


  s = mcast_sender()
  for value in sys.stdin:
    value = value.strip()
    print ("client",id, ": sending ", value, " to proposers")
    value = "submit " + value + " " + str(id)+ " None None"
    s.sendto(value.encode(), config['proposers'])
  if(id == 1):
    print("Client id: ", id ,", I'm asking to the proposers to start the battle.")
    s.sendto("startPaxos None None None None".encode(), config["proposers"])
  print ("Client ",id," my job is done.")