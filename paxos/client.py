import queue
import socket
import sys
import time
from connection import mcast_receiver, mcast_sender

def client(config, id):


  print ('-> client ', id)


  s = mcast_sender()
  i = 0
  for value in sys.stdin:
    if (i%100 == 0):
      if(id == 1):
        # print("IDDDDD ", i)
        s.sendto("startPaxos None None None None".encode(), config["proposers"])
        print("Client id: ", id ,", I'm asking to the proposers to start the battle.")
      time.sleep(0.5)
    
    

    i+=1
    value = value.strip()
    print ("client",id, ": sending ", value, " to proposers")
    value = "submit " + value + " " + str(id)+ " None None"
    s.sendto(value.encode(), config['proposers'])
  time.sleep(5)
  #if(id == 1):
  s.sendto("startPaxos None None None None".encode(), config["proposers"])
  print("Client id: ", id ,", I'm asking to the proposers to start the battle.")

  print ("Client ",id," my job is done.")