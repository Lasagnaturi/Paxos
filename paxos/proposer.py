import queue
import socket
from connection import mcast_receiver, mcast_sender

class Proposer():

    id = None
    config = None

    # receiver and sender
    r = None
    s = None

    #PaxosInstances
    instances = {}
    instance = -1

    values = queue.Queue()

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

        if(Proposer.instances[Proposer.instance]['c_rnd'] == rnd):
            Proposer.instances[Proposer.instance]['V'][v_rnd] = v_val
            Proposer.instances[Proposer.instance]['Qa'] += 1
        else:
            print("Be careful, c_rnd = ", Proposer.instances[Proposer.instance]['c_rnd']," and v_rnd = ", v_rnd)

        if(Proposer.instances[Proposer.instance]['Qa']>1 and Proposer.instances[Proposer.instance]['state2A']):
            print("Proposer id ",Proposer.id, " I received the quorum")
            k = max(Proposer.instances[Proposer.instance]['V'].keys())

            if (k == 0):
                Proposer.instances[Proposer.instance]['c_val'] = Proposer.values.get()
            else:
                Proposer.instances[Proposer.instance]['c_val'] = Proposer.instances[Proposer.instance]['V'][k]

            msg = "phase2a " + str(Proposer.instances[Proposer.instance]['c_rnd']) + " " + str(Proposer.instances[Proposer.instance]['c_val']) + " " + str(Proposer.instance)
            Proposer.s.sendto(msg.encode(), Proposer.config['acceptors'])
            Proposer.instances[Proposer.instance]['state2A'] = False



    def phase2b(par1, par2, par3=None):
        # IN THE SLIDES THIS IS THE PHASE 3
        # let's check if I received the quorum again, if yes let's decide this value. yeee
        v_rnd = int(par1)
        v_val = int(par2)
        Proposer.instances[Proposer.instance]['Qa3'] += 1

        if(v_rnd == Proposer.instances[Proposer.instance]['c_rnd']):
            Proposer.instances[Proposer.instance]['received3'] += 1

        if(Proposer.instances[Proposer.instance]['Qa3'] > 1 and Proposer.instances[Proposer.instance]['Qa3'] == Proposer.instances[Proposer.instance]['received3']):
            msg = "decision " + str(v_val)
            Proposer.s.sendto(msg.encode(), Proposer.config['learners'])
            print ("Proposer id: ",Proposer.id, " decided value: ", v_val)

    def submit(par1, par2, par3=None):
        value = int(par1)
        c_id = int(par2)
        # this function allow the proposer to receive values from the client
        print("Submit: I'm the proposer with id ", Proposer.id, "received: ", value, " from client with id:", c_id)
        Proposer.values.put(value)

    def newStackOfVariables():
        # paxos variables
        Qa = 0
        c_rnd = 0
        c_val = None
        paxosStarted = False
        state2A = True
        Qa3 = 0
        received3 = 0
        V = {}

        Proposer.instance += 1
        variables = {'c_val':c_val, 'c_rnd': c_rnd, 'Qa':Qa, 'V':V, 'paxosStarted':paxosStarted,'state2A':state2A, 'Qa3':Qa3, 'received3':received3}
        Proposer.instances[Proposer.instance] = variables

    def startPaxos(par1, par2=None, par3=None):


        # IN THE SLIDES THIS IS THE PHASE 1A
        Proposer.newStackOfVariables()
        if(not Proposer.instances[Proposer.instance]['paxosStarted']):
            Proposer.instances[Proposer.instance]['paxosStarted'] = True

            Proposer.instances[Proposer.instance]['c_rnd'] += 1
            Proposer.instances[Proposer.instance]['c_val'] = Proposer.values.get()

            msg = "phase1a "+str(Proposer.instances[Proposer.instance]['c_rnd'])+ " None " + str(Proposer.instance)
            Proposer.s.sendto(msg.encode(), Proposer.config['acceptors'])


    def proposer(config, id):
        print('-> Proposer', id)
        # Setting up communication and class variables.
        Proposer.config = config
        Proposer.id = id
        Proposer.r = mcast_receiver(config['proposers'])
        Proposer.r.settimeout(30)
        Proposer.s = mcast_sender()
        if(id == 1):
            print("Proposer ", id, " hey, I'm the leader")
            while True:
                try:
                    msg = Proposer.r.recv(2 ** 16)

                except socket.timeout:
                    # se l'attesa è troppo lunga iniziamo un nuovo instance
                    print ("Proposer id", id,": OPS! Timeout exception")
                    break
                phase, par1, par2, par3 = Proposer.parse_msg(msg)
                phase(par1, par2, par3)
        else:
            print("Proposer ",id," sorry, I'm not the leader")

        print("Proposer ", id, " goodbye.")