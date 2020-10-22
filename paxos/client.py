import queue
import socket
import sys
from connection import mcast_receiver, mcast_sender

def client(config, id):


  print ('-> client ', id)
  s = mcast_sender()
  #
  # f = open("../values.txt", "r")
  # values = []
  #
  # while (True):
  #   value = f.readline()
  #   if (value == ""):
  #     break
  #   values.append(value)
  #
  # for value in values:
  #   value = value.strip()
  #   print ("client: sending %s to proposers" % (value))
  #   s.sendto(value, config['proposers'])
  # print ('client done.')

  s = mcast_sender()
  for value in sys.stdin:
    value = value.strip()
    print ("client: sending ", value, " to proposers")
    value = "submit " + value + " " + str(id)+ " None"
    s.sendto(value.encode(), config['proposers'])
  s.sendto("startPaxos None None None".encode(), config['proposers'])
  print ('client done.')