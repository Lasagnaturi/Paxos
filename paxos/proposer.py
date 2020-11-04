import queue
import socket
import time
from connection import mcast_receiver, mcast_sender

class Proposer():

    id = None
    config = None

    # receiver and sender
    r = None
    s = None

    #PaxosInstances
    instances = {}
    max_instance = -1
    state = []

    # values = queue.Queue()
    values = []
    numberofvalues = 0

    def parse_msg(msg):
        phase, par1, par2, par3, instance = msg.decode().split()
        module = __import__("proposer")
        cls = getattr(module, "Proposer")
        phase = getattr(cls, phase)

        return phase, par1, par2, par3, instance

    def phase1b(par1, par2=None, par3=None, instance=None):
        # IN THE SLIDES THIS IS THE PHASE 2A
        instance = int(instance)
        rnd = int(par1)
        v_rnd = int(par2)
        try:
            v_val = int(par3)
        except ValueError:
            v_val = None
        if(Proposer.instances[instance]['c_rnd'] == rnd):
            Proposer.instances[instance]['V'][v_rnd] = v_val
            Proposer.instances[instance]['Qa'] += 1
        else:
            print("Be careful, c_rnd = ", Proposer.instances[instance]['c_rnd']," and v_rnd = ", v_rnd)
        if(Proposer.instances[instance]['Qa']>1 and Proposer.instances[instance]['state2A']):
            print("Proposer id ",Proposer.id, " instance : ",instance," I received the quorum")
            k = max(Proposer.instances[instance]['V'].keys())

            if (k == 0):
                print("cerco un valore nella queue")
                Proposer.instances[instance]['c_val'] = Proposer.values[0]
                #.get(timeout=2)
                Proposer.values = Proposer.values[1:len(Proposer.values)]
                print("ottengo un valore dalla queue ")
                # Proposer.numberofvalues-=1
            else:
                Proposer.instances[instance]['c_val'] = Proposer.instances[instance]['V'][k]

            msg = "phase2a " + str(Proposer.instances[instance]['c_rnd']) + " " + str(Proposer.instances[instance]['c_val']) + " " + str(instance)
            Proposer.s.sendto(msg.encode(), Proposer.config['acceptors'])
            Proposer.instances[instance]['state2A'] = False


    def phase2b(par1, par2, par3=None, instance=None):

        # IN THE SLIDES THIS IS THE PHASE 3
        # let's check if I received the quorum again, if yes let's decide this value. yeee\
        
        print ("Proposer id: ",Proposer.id, " instance ", instance, " phase 3 ho ricevuto la conferma finale")

        instance = int(instance)
        v_rnd = int(par1)
        v_val = int(par2)
        Proposer.instances[instance]['Qa3'] += 1

        if(v_rnd == Proposer.instances[instance]['c_rnd']):
            Proposer.instances[instance]['received3'] += 1

        if(Proposer.instances[instance]['Qa3'] > 1 and not Proposer.instances[instance]['isComplete'] and Proposer.instances[instance]['Qa3'] == Proposer.instances[instance]['received3']):
            msg = "decision " + str(v_val) + " " + str(instance)
            Proposer.s.sendto(msg.encode(), Proposer.config['learners'])

            print ("Proposer id: ",Proposer.id, " instance ", instance, " decided value: ", v_val)
            Proposer.state.append((v_val,instance))
            Proposer.instances[instance]['isComplete'] = True
            # Since the value has been accepted, I start a new instance with the next value to be proposed
           
            Proposer.startPaxos(instance='None')

        print("finito fase 3 ")


    def submit(par1, par2, par3=None, instance=None):
        value = int(par1)
        c_id = int(par2)
        # this function allow the proposer to receive values from the client
        print("Submit: I'm the proposer with id ", Proposer.id, "received: ", value, " from client with id:", c_id)
        Proposer.values.append(value)
        Proposer.numberofvalues += 1 

    def newStackOfVariables(par1=None):
        # paxos variables
        Qa = 0
        c_rnd = 0
        c_val = None
        paxosStarted = False
        state2A = True
        Qa3 = 0
        received3 = 0
        V = {}
        isComplete = False

        # if Proposer.max_instance > 0:
        Proposer.max_instance += 1
        variables = {'c_val':c_val, 'c_rnd': c_rnd, 'Qa':Qa, 'V':V, 'paxosStarted':paxosStarted,'state2A':state2A, 'Qa3':Qa3, 'received3':received3, 'isComplete':isComplete}
        Proposer.instances[Proposer.max_instance] = variables
        Proposer.numberofvalues-=1

        return Proposer.max_instance

    chiamate_paxos = 0
    def startPaxos(par1=None, par2=None, par3=None, instance="None"):
        # print("ATTENZIONE START PAXOS CHIAMATO")
        print("instance ", instance)
        # IN THE SLIDES THIS IS THE PHASE 1A

        # if there are value to be proposed I initialize a new instance, if it is not passed as argument.
        if instance == "None":
            
            if(Proposer.numberofvalues == 0):
                return
            Proposer.chiamate_paxos+=1  
            print('CHIAMATAAA', Proposer.chiamate_paxos, "con instance", instance, "e lenght di values", len(Proposer.values), "e number of values ", Proposer.numberofvalues)
            instance = Proposer.newStackOfVariables()

        # if the instance is passed as argument, i'll start a new round, otherwise I start the new one created above
        # print("condition ", not Proposer.instances[instance]['paxosStarted'])
        # print("paxos starte" ,Proposer.instances[instance]['paxosStarted'])
        if(not Proposer.instances[instance]['paxosStarted']):
            Proposer.instances[instance]['paxosStarted'] = True
            Proposer.instances[instance]['c_rnd'] += 1
            msg = "phase1a " + str(Proposer.instances[instance]['c_rnd']) + " None " + str(instance)
            Proposer.s.sendto(msg.encode(), Proposer.config['acceptors'])


    def getOlderValue(par1=None, par2=None, par3=None, instance="None"):
        inst = int(par1)
        val = None
        for k in Proposer.state:
            if(k[1] == inst):
                val = k[0]
                break

        msg = "decision " + str(val) + " " + str(inst)
        Proposer.s.sendto(msg.encode(), Proposer.config['learners'])


    def proposer(config, id):
        print('-> Proposer', id)
        # Setting up communication and class variables.
        Proposer.config = config
        Proposer.id = id
        Proposer.r = mcast_receiver(config['proposers'])
        Proposer.r.settimeout(5)
        Proposer.s = mcast_sender()

        if(id == 2):
            print("Proposer ",id," sorry, I'm not the leader goodbye.")
            exit()

        print("Proposer ", id, " hey, I'm the leader")
        while True:
            while True:
                try:
                    # print("proposer aspetto un messaggio")
                    msg = Proposer.r.recv(2 ** 16)
                    # print("ricevuto")
                    break
                except socket.timeout:
                    # print("nessun messaggio ricevuto")

                    if(len(Proposer.instances.keys()) != 0):
                        instance = max(Proposer.instances.keys())
                        if not Proposer.instances[instance]['isComplete']:

                            Proposer.instances[instance]['paxosStarted'] = False
                            Proposer.instances[instance]['Qa'] = 0
                            Proposer.instances[instance]['Qa3'] = 0
                            Proposer.instances[instance]['received3'] = 0
                            Proposer.instances[instance]['V'] = {}
                            Proposer.instances[instance]['state2A'] = True
                            Proposer.startPaxos(instance=instance)

                        elif(len(Proposer.values)>0):
                            Proposer.startPaxos(instance='None')

                    else:

                        if(len(Proposer.values)>0):
                            # print('aoo')
                            Proposer.startPaxos(instance='None')
                        else:
                            # print('aiii')
                            print("Proposer ", id, " sorry, I haven't received values from the client, I'll try again in 5 seconds.")
                            time.sleep(5)

            phase, par1, par2, par3, instance = Proposer.parse_msg(msg)
            phase(par1, par2, par3, instance)
        

        print("Proposer ", id, " goodbye.")