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
    Qa = 0
    c_rnd = 0
    c_val = None
    values = queue.Queue()
    paxosStarted = False
    k = 0
    V = {}

    def parse_msg(msg):
        phase, par1, par2, par3 = msg.decode().split()
        module = __import__("proposer")
        cls = getattr(module, "Proposer")
        phase = getattr(cls, phase)
        return phase, int(par1), int(par2), int(par3)

    def phase1b(par1, par2=None, par3=None):
        # IN THE SLIDES THIS IS THE PHASE 2A
        rnd = par1
        v_rnd = par2
        v_val = par3
        Proposer.k = max(Proposer.k, v_rnd)
        Proposer.V[v_rnd] = v_val
        if (Proposer.c_rnd == rnd):
            Qa += 1
        if(Qa > 1):
            if(Proposer.k == 0):
                Proposer.c_val = Proposer.values.get()
            else:
                Proposer.c_val = Proposer.V[k]
            msg = "phase2a " + str(Proposer.c_rnd) + " " + str(Proposer.c_val)
            Proposer.s.sendto(msg.encode(), Proposer.config['acceptors'])

    def phase2b(par1, par2=None, par3=None):
        # # IN THE SLIDES THIS IS THE PHASE 3
        print ("phase2b")

    def submit(par1, par2=None, par3=None):
        # this function allow the proposer to receive values from the client
        print("Submit: I proposer with id ", Proposer.id, "received: ", par1, " from client with id:", par2 )
        Proposer.values.put(par1)

    def startPaxos(par1, par2=None, par3=None):
        # IN THE SLIDES THIS IS THE PHASE 1A
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
            except socket.timeout:
                print ("Proposed id", id,": OPS! Timeout exception")
                break
        phase, par1, par2, par3 = Proposer.parse_msg(msg)
        phase(par1, par2, par3)
