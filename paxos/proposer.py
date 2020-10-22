import queue
import socket
from connection import mcast_receiver, mcast_sender

class Proposer():

    id = None
    config = None

    # receiver and sender
    r = None
    s = None

    # paxos variables
    c_rnd = 0
    c_val = None
    values = queue.Queue()
    paxosStarted = False
    k = 0
    V = []

    def parse_msg(msg):
        phase, par1, par2, par3 = msg.decode().split()
        module = __import__("proposer")
        cls = getattr(module, "Proposer")
        phase = getattr(cls, phase)
        return phase, par1, par2, par3

    def phase1b(par1, par2=None, par3=None):
        rnd = par1
        v_rnd = par2
        v_val = par3

        Proposer.k = max(Proposer.k, v_rnd)
        if(v_rnd == k):
            Proposer.V.append((v_rnd, v_val))
        

    def phase2b(par1, par2=None, par3=None):
        print ("phase2b")

    def submit(par1, par2=None, par3=None):
        print("Submit: I proposer with id ", Proposer.id, "received: ", par1, " from client with id:", par2 )
        Proposer.values.put(par1)

    def startPaxos(par1, par2=None, par3=None):
        if(not Proposer.paxosStarted):
            Proposer.paxosStarted = True
            Proposer.c_rnd+=1
            msg = "phase1a "+str(Proposer.c_rnd)+ " None"
            Proposer.s.sendto(msg.encode(), Proposer.config['acceptors'])


    def proposer(config, id):
        print('-> Proposer', id)
        # Setting up communication and class variables.
        Proposer.config = config
        Proposer.id = id
        Proposer.r = mcast_receiver(config['proposers'])
        Proposer.r.settimeout(15)
        Proposer.s = mcast_sender()


        while True:
            try:
                msg = Proposer.r.recv(2 ** 16)
                phase, par1 , par2, par3 = Proposer.parse_msg(msg)
                phase(par1 , par2, par3)
            except socket.timeout:
                print ("Proposed id", id,": OPS! Timeout exception")
                break

