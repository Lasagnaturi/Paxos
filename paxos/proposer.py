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
    state2A = True
    Qa3 = 0
    received3 = 0
    V = {}

    def parse_msg(msg):
        phase, par1, par2, par3 = msg.decode().split()
        module = __import__("proposer")
        cls = getattr(module, "Proposer")
        phase = getattr(cls, phase)

        return phase, par1, par2, par3

    def phase1b(par1, par2=None, par3=None):
        # IN THE SLIDES THIS IS THE PHASE 2A

        rnd = int(par1)
        v_rnd = int(par2)
        try:
            v_val = int(par3)
        except ValueError:
            v_val = None

        if(Proposer.c_rnd == rnd):
            Proposer.V[v_rnd] = v_val
            Proposer.Qa += 1
        else:
            print("Be careful, c_rnd = ",Proposer.c_rnd," and v_rnd = ", v_rnd)

        if(Proposer.Qa>1 and Proposer.state2A):
            print("Proposer id ",Proposer.id, " I received the quorum azzz")
            k = max(Proposer.V.keys())
            # print("k vale: ", k)
            # print("V contiene: ",Proposer.V)
            if (k == 0):
                Proposer.c_val = Proposer.values.get()
            else:
                Proposer.c_val = Proposer.V[k]

            msg = "phase2a " + str(Proposer.c_rnd) + " " + str(Proposer.c_val)
            Proposer.s.sendto(msg.encode(), Proposer.config['acceptors'])
            Proposer.state2A = False



    def phase2b(par1, par2, par3=None):
        # IN THE SLIDES THIS IS THE PHASE 3
        # let's check if I received the quorum again, if yes let's decide this value. yeee
        v_rnd = int(par1)
        v_val = int(par2)
        Proposer.Qa3 += 1

        if(v_rnd == Proposer.c_rnd):
            Proposer.received3 +=1

        if(Proposer.Qa3 > 1 and Proposer.Qa3 == Proposer.received3):
            msg = "decision " + str(v_val)
            Proposer.s.sendto(msg.encode(), Proposer.config['learners'])
            print ("Proposer id: ",Proposer.id, " decided value: ", v_val)

    def submit(par1, par2, par3=None):
        value = int(par1)
        c_id = int(par2)
        # this function allow the proposer to receive values from the client
        print("Submit: I'm the proposer with id ", Proposer.id, "received: ", value, " from client with id:", c_id)
        Proposer.values.put(value)

    def startPaxos(par1, par2=None, par3=None):
        # IN THE SLIDES THIS IS THE PHASE 1A
        if(not Proposer.paxosStarted):
            Proposer.paxosStarted = True
            Proposer.c_rnd += 1
            Proposer.c_val = Proposer.values.get()

            # resetting values of previous attemps
            Proposer.V = {}
            Proposer.Qa = 0


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
        if(id == 1):
            print("Proposer ", id, " hey, I'm the leader")
            while True:
                try:
                    msg = Proposer.r.recv(2 ** 16)

                except socket.timeout:
                    print ("Proposer id", id,": OPS! Timeout exception")
                    break
                phase, par1, par2, par3 = Proposer.parse_msg(msg)
                phase(par1, par2, par3)
        else:
            print("Proposer ",id," sorry, I'm not the leader")

        print("Proposer ", id, " goodbye.")