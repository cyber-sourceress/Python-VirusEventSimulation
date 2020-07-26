#!/usr/bin/python3
#
# Remilia "Nikki" Grimm
# grimm.remilia@gmail.com
# https://remilia-grimm.github.io
# CS1210: Computer Science Fundamentals
#
# Lecturing Professor:
# Dr. Alberto Maria Segre
# of the University of Iowa
###############################################
#
# Currently putting this old project back
# together from my notes and re-coding
###############################################

from random import random, randint, sample
import matplotlib.pyplot as plt


#
def initiateProbability(p):
    '''Sets probability P to return'''
    return random() <= p


#
# virus model. Each virus has a name, and a coefficient to model transmission rate,
# Model data provided by Dr. Segre
# coefficient for recovery,exposure rate, and infection duration.
# Time scale is adjusted for days for durations
class Virus():
    def __init__(self, name='Bubonic', t=0.95, Ex=2, ID=7, s=0.0):
        self.name = name
        self.t = t  # Transmission likelihood
        self.Ex = Ex  # exposure
        self.ID = ID  # infection duration
        self.s = s  # probability of sustained immunity+
        self.DQ = 0  # Quarantine duration

        def __repr__(self):
            '''Display method for virus instances.'''
            return "<{}: {},{},{}>".format(self.name.title(), self.ID, self.E, self.DQ)

        def quarantine(self, Q):
            '''Establish quarantine of Q days for this virus object.'''
            self.DQ = min(Q, self.ID)


# Actor model. Model detail provided by Dr. Segre
#
# Each Actor has a susceptibility chance,
# a vaccination state,
# and a counter that is used to model their current state
class Actor():
    def __init__(self, pg=0, r=[1.0], w=0.99, qc=0.9):
        self.pg = pg  # Peer group tag
        self.SQ = []  # Status of each quarantine
        self.r = r  # Risk, vector for probability of contact
        self.qc = qc  # Probability of complying to quarantine
        self.w = w  # Weakness, susceptibility increases as value gets smaller
        self.V = []  # List of Viruses
        self.sa = []  # Current state affected by virus
        self.v = []  # Vaccination state

    # Return True if infectious (i.e., in ID or Ex state)
    def __repr__(self):
        '''Display method for actor instances.'''
        return "<actor_{}: {}>".format(self.pg, self.sa)

    # Return index for virus in internal data structures. If virus
    # isn't found, add it.
    def index(self, virus):
        '''Return internal index of virus in self.V list; add new if necessary.'''
        try:
            # Got it; return the index.
            return self.V.index(virus)
        except:
            # New virus; add it.
            self.V.append(virus)
            self.SQ.append(False)
            self.w.append(-1)
            self.v.append(1.0)
            return len(self.V) - 1

    def state(self, virus):
        '''if Actor is infectious, return true.'''
        '''Returns (Ex,ID,SQ,S) truth vector for actor wrt virus.'''
        d = self.index(virus)
        if self.sa[d] == 0:
            # Recovered from virus d.
            return False, False, False, False
        elif self.sa[d] < 0:
            # Susceptible to virus d.
            return False, False, False, True
        elif self.sa[d] > virus.I:
            # Exposed to virus d.
            return True, False, False, False
        elif max(self.SQ):
            # Under quarantine for ANY virus, not just virus
            # d. Recall self.SQ is a list of True/False values, so if
            # max is True, then some quarantine is underway.
            return False, False, True, False
        elif self.sa[d] > 0:
            # Infectious with virus d.
            return False, True, False, False

    # Set the Actor's vaccination value to whatever value you give.
    def vaccinate(self, virus, v):
        '''Models vaccination; v=0 denotes full immunity; v=1 denotes no immunity.'''
        d = self.index(virus)
        self.v[d] = v

    # Weakness: if an infected is present, initiate Probability ->state
    # ID+Ex incremented by 1: initialize() updates state
    def infect(self, other, virus):
        '''vector tries to infects self with virus.'''
        d = self.index(virus)
        if self.sa[d] < 0 and initiateProbability(self.w * self.v[d] * self.r[other.g] * virus.t):
            self.sa[d] = virus.Ex + virus.ID + 1
            return (True)
        return (False)

    # def infect(self, vector, virus):

    #   if vector.state() and self.s < 0 and initiateProbability(self.w*self.v*virus.t):
    #      self.s = virus.Ex + virus.ID + 1
    #     self.virus = virus
    #    return(True)
    # return(False)

    # Update the status of the actor. Returns infection status: True
    # if you are infectious and False otherwise. This involves
    # decrementing your internal counter if you are actively
    # infected. When you get to 0, you need to flip a (weighted) coin
    # to decide if the actor goes to state R (c=0) or back to state S
    # (c=-1). You also need to handle quarantine: deciding whether to
    # honor it and then making sure you return False while in ANY
    # quarantine.
    def update(self, virus):
        '''Daily status update.'''
        d = self.index(virus)
        if self.sa[d] <= 0:
            return (False)
        elif self.sa[d] == 1:
            if not initiateProbability(virus.r):
                # Revert to susceptible, c=-1.
                self.sa[d] = -1
            else:
                # Lifelong immunity at recovery, c=0.
                self.sa[d] = 0
        elif self.sa[d] == virus.I + 1 and virus.Q > 0 and initiateProbability(self.qc):
            # actor elects to honor quarantine.
            self.sa[d] = self.sa[d] - 1
            # print('Opting for {} quarantine [{},{},{}]!'.format(virus.name, self.sa[d], virus.I, virus.Q))
            self.SQ[d] = True
            return (False)
        elif self.SQ[d]:
            # actor is currently in quarantine.
            self.sa[d] = self.sa[d] - 1
            if self.sa[d] == virus.ID - virus.Q:
                # print('Expiring {} quarantine [{},{}.{}]!'.format(virus.name, self.sa[d], virus.I, virus.Q))
                self.SQ[d] = False
                return (True)
            return (False)
        else:
            # One day closer to recovery.
            self.sa[d] = self.sa[d] - 1
            return (True)
        return (False)

    # Actor's state update. Decrease counter if infected.
    # When it becomes 0, initiate a probability
    # If state c=0 else state S c=-1.
    # def update(self):
    #    '''Current Update.'''
    #    if self.sa == 1:
    #        if not initiateProbability(self.virus.s):
    #            # deteriorate to weak, c=-1.
    #            self.sa = -1
    #        else:
    #            # Sustained immunity, c=0.
    #            self.sa = 0
    #        # Remove virus value.
    #        self.virus = None
    #    elif self.sa > 1:
    #        # Approach recovering state
    #        # For viruses like SARS2, consider
    #        # Nonlinear modeling for recovery
    #        # like weight probability for
    #        # relapse
    #        self.sa = self.sa - 1
    #        return(True)
    #    return(False)


# VES is set to run for days set by time t
class EventSimulation():
    def __init__(self, D=500, p=0.001, pvector=[[1.0]]):
        self.steps = D  # Maximum number of timesteps
        self.p = p  # Mixing parameter for this simulation
        self.pvector = pvector  # Probability vector for contact
        self.actors = []  # List of actors in the simulation
        self.V = []  # virus being simulated
        self.record = []  # History of (E, I, R, V) tuples
        self.events = []  # Dictionary of delayed events, keyed by day

    def __repr__(self):
        '''Display method for EventSimulation instances.'''
        return "<EventSimulation_{}: {}>".format(len(self.actors), self.V)

    # Populates the simulation with n actors from group g.
    def populate(self, n, g=0):
        '''Populate simulation with n actors from group g.'''
        for i in range(n):
            self.join(Actor(g, self.pvector[g]))

    # Add actor to current VES.
    def join(self, actor):
        '''Add specified actor to current simulation.'''
        self.actors.append(actor)

    # instantiate virus within VES
    # Phase 1 only allowed for 1(one) virus in class
    def introduce(self, virus):
        '''Add specified virus to current simulation.'''
        self.V.append(virus)

    # Seed the simulation with k actors having the specified virus.
    def seed(self, virus, k=1):
        '''Seed a certain number of actors with a particular virus.'''
        # I+E+1, because my first step in run() is to update state.
        for actor in sample(self.actors, k):
            d = actor.index(virus)
            actor.c[d] = virus.E + virus.I + 1

    # The initialize() method performs at most self.rounds
    # iterations, where each round:
    # updates the Actors,
    # counts how many are in Ex and ID states,
    # Determines if the virus wipes out all current hosts,
    # Resulting in early termination
    # infection  spreads according to the variable parameter, p.
    def initialize(self):
        '''Inititate VES.'''
        for i in range(self.steps):
            # Initiate daily queue
            for event in self.events:
                if event[0] == i:
                    if event[1] == 'quarantine':
                        # Establish Quarantine duration

                        event[2].Q = event[3]
                        print('{}: Initiating {} the quarantine event.'.format(i, event[2].name))
                    elif event[1] == 'Introduce Vaccine':
                        # Step through and vaccinate each actor with
                        # probability event[3] and vaccine
                        # effectiveness 1-event[4].
                        for actor in self.actors:
                            if initiateProbability(event[3]):
                                actor.vaccinate(event[2], 1.0 - event[4])
                        print('{}: Beginning treating for {}.'.format(i, event[2].name))
                    elif event[1] == 'seed':
                        # Infect event[3] actors with virus

                        self.seed(event[2], event[3])
                        print('{}: Seeding {} actors with {}.'.format(i, event[3], event[2].name))
            # Notes from Dr. Segre:
            # Keep track of each virus vector for inclusion in record.
            states = []
            # Keep track of early termination when no disease is
            # left. Assume none is left to start with, then change
            # this to True when you encounter an infected actor.
            contagion = False
            # Note from Dr. Segre:
            # Update each virus. If there aren't any left, exit
            # early.  Note that virus is the outer loop and actor
            # contacts are the inner loop. A better solution might
            # well reverse these, so that all the virus being run
            # in the same simulation would play out over exactly the
            # same actor contact pattern. Would require a fair bit of
            # rewriting.
            for virus in self.V:
                # First, update actors wrt to this virus.
                for actor in self.actors:
                    actor.update(virus)
                # Dr. Segre's modeling
                # Next, create a state vector for this virus to
                # drive this cycle. Determining who is infected first
                # avoids letting the infection infect a friend's
                # friend in one pass. Each entry is (Ex, ID, DQ, S).
                state = [a.state(virus) for a in self.actors]
                # Append (E, IvQ, Q, S) to record.
                states.append((len([s for s in state if s[0]]),  # Ex
                               len([s for s in state if (s[1] or s[2])]),  # ID or Q
                               len([s for s in state if s[2]]),  # DQ
                               len([s for s in state if s[3]])))  # S
                # Provided that the virus persists, continue.
                if sum([sum(x[:3]) for x in state]) > 0:
                    contagion = True
                # Each infectious actor attempts to spread.
                for p in range(len(self.actors)):
                    if state[p][0] or state[p][1]:
                        # actor p is infectious and not under quarantine.
                        for q in range(len(self.actors)):
                            if state[q][3]:
                                # actor q is susceptible.
                                if initiateProbability(self.p):
                                    self.actors[q].infect(self.actors[p], virus)
            # Append counts to .record.
            self.record.append(states)
            # Terminate early if no contagion this iteration and there are no remaining
            # events on the schedule.
            if not contagion and not [True for event in self.events if event[0] > i]:
                break
        # Done.
        return (self.record)

    '''
    def initialize(self):
        
        for i in range(self.rounds):
            # Evaluate each Actor,
            # Establishing which are exposed or infected
            communicable = [ a for a in self.Actors if a.update() ]
            # Update record with exposed and infection values
            self.record.append((len([ a for a in communicable if a.s > self.virus.ID ]),
                                len([ a for a in communicable if a.s <= self.virus.ID ])))
            # Early termination if vector Actors are reduced to 0
            # Code below was provided by TA
            if self.record[-1] == (0, 0):
                return(i)
            for a1 in communicable:
                for a2 in self.Actors:
                    if initiateProbability(self.p):
                        a2.infect(a1, self.virus)
        # Return record of (Ex, ID) tuples.
        return(self.record)
    
    def plot(self):
        plt.title('Viral Event Simulation')
        plt.axis( [0, len(self.record), 0, len(self.Actors)] )
        plt.xlabel('Days')
        plt.ylabel('N')
        plt.plot( [ i for i in range(len(self.record)) ], [ e for (e, i) in self.record ], 'g-', label='Individuals Exposed' )
        plt.plot( [ i for i in range(len(self.record)) ], [ i for (e, i) in self.record ], 'r-', label='Known infected' )
        plt.show()
    '''

    # Guidance from lecture notes and office hours used here
    # This method plots the pandemic curve from the self.record variable.
    def plot(self, virus):
        '''Produce a pandemic curve for the simulation.'''
        d = self.V.index(virus)
        plt.title('{}'.format(virus.name.title()))
        plt.axis([0, len(self.record), 0, len(self.actors)])
        plt.xlabel('Days')
        plt.ylabel('N')
        plt.plot([i for i in range(len(self.record))], [s[d][3] for s in self.record], 'g-', label='Susceptible')
        plt.plot([i for i in range(len(self.record))], [s[d][0] for s in self.record], 'y-', label='Exposed')
        plt.plot([i for i in range(len(self.record))], [s[d][1] for s in self.record], 'r-', label='Infected')
        plt.plot([i for i in range(len(self.record))], [s[d][2] for s in self.record], 'b-', label='Quarantine')
        plt.legend(prop={'size': 'small'})
        plt.show()

    # Institute a quarantine order for virus at specified time.
    def order(self, time, virus, Q):
        '''Put a quarantine order in place.'''
        self.events.append((time, 'quarantine', virus, Q))

    # Start a vaccination campaign for virus at specified time.
    def campaign(self, time, virus, coverage, v):
        '''Institute a vaccination campaign.'''
        self.events.append((time, 'vaccinate', virus, coverage, v))

    # Introduce some infecteds with virus at specified time.
    def infect(self, time, virus, k):
        '''Introduce some infecteds.'''
        self.events.append((time, 'seed', virus, k))

    # This method is used by the interactive simulation function as
    # well as the configuration file reader.
    def process(self, cmd):
        if cmd[0] == 'add':
            # add 100 0
            self.populate(int(cmd[1]), int(cmd[2]))
        elif cmd[0] == 'virus':
            # virus influenza 0.95 2 7 0
            self.introduce(Virus(cmd[1], float(cmd[2]), int(cmd[3]), int(cmd[4]), float(cmd[5])))
        elif cmd[0] == 'seed':
            # seed 10 influenza 1
            self.infect(int(cmd[1]), [d for d in self.V if d.name == cmd[2]][0], int(cmd[3]))
        # elif cmd[0] == 'infect':
        #    # infect 13 influenza 20
        #    self.infect(int(cmd[1]), [ d for d in self.V if d.name==cmd[2] ][0], int(cmd[3]))
        elif cmd[0] == 'quarantine':
            # order 25 influenza Q
            self.order(int(cmd[1]), [d for d in self.V if d.name == cmd[2]][0], int(cmd[3]))
        # elif cmd[0] == 'order':
        #    # order 25 influenza Q
        #    self.order(int(cmd[1]), [ d for d in self.V if d.name==cmd[2] ][0], int(cmd[3]))
        elif cmd[0] == 'campaign':
            # campaign 100 influenza coverage v
            self.campaign(int(cmd[1]), [d for d in self.V if d.name == cmd[2]][0], float(cmd[3]), float(cmd[4]))
        elif cmd[0] == 'plot':
            # plot influenza
            self.plot([d for d in self.V if d.name == cmd[1]][0])
        elif cmd[0] == 'initialize':
            self.initialize()

    # This method reads interactive simulation commands from a config
    # file instead.
    def config(self, filename):
        try:
            file = open(filename, 'r')
            # Read in a command
            for line in file:
                self.process(line.split())
        except:
            print('Error in configuration file.')
            # !error?


def ves():
    # Current simulation object
    S = None
    # Read in a command
    cmd = []
    while not cmd:
        cmd = input('sim> ').split()
    # Keep going while input is not 'quit'.
    while cmd[0] != 'quit':
        if cmd[0] == 'create':
            # Careful: need to "undo" any inadvertent splitting of the
            # contact matrix, hence the join().
            S = EventSimulation(int(cmd[1]), float(cmd[2]), eval(''.join(cmd[3:])))
        elif S is None:
            print('No simulation object: try "create" first.')
        else:
            S.process(cmd)
        # Read in next command
        cmd = []
        while not cmd:
            cmd = input('sim> ').split()
    return (S)


# Tests provided by requirements and Dr. Segre
# A few simple tests
def test0():
    s = EventSimulation()
    s.populate(3)
    d = Virus('flu', 0.1, 2, 7, 1)
    s.introduce(d)
    s.infect(1, d, 1)
    s.order(1, d, 6)
    s.initialize()
    s.plot(d)
    return (s)


# No quarantine
def test1():
    # new 500 0.001 [[1.0]]
    s = EventSimulation()
    # add 1000 0
    s.populate(1000)
    # virus influenza 0.95 2 7 0
    d1 = Virus('influenza', 0.95, 2, 7, 0.9)
    s.introduce(d1)
    # seed 0 influenza 3
    s.infect(0, d1, 3)
    s.initialize()
    # plot influenza
    s.plot(d1)
    return (s)


# Early but short quarantine
def test2():
    # new 500 0.001 [[1.0]]
    s = EventSimulation()
    # add 1000 0
    s.populate(1000)
    # virus influenza 0.95 2 7 0
    d1 = Virus('influenza', 0.95, 2, 7, 0.9)
    s.introduce(d1)
    # seed 0 influenza 3
    s.infect(0, d1, 3)
    # order influenza 7
    s.order(0, d1, 3)
    s.initialize()
    # plot influenza
    s.plot(d1)
    return (s)


# Early and longer quarantine
def test3():
    # new 500 0.001 [[1.0]]
    s = EventSimulation()
    # add 1000 0
    s.populate(1000)
    # virus influenza 0.95 2 7 0
    d1 = Virus('influenza', 0.95, 2, 7, 0.9)
    s.introduce(d1)
    # seed 0 influenza 3
    s.infect(0, d1, 3)
    # order influenza 7
    s.order(0, d1, 7)
    s.initialize()
    # plot influenza
    s.plot(d1)
    return (s)


# Late but longer quarantine
def test4():
    # new 500 0.001 [[1.0]]
    s = EventSimulation()
    # add 1000 0
    s.populate(1000)
    # virus influenza 0.95 2 7 0
    d1 = Virus('influenza', 0.95, 2, 7, 0.9)
    s.introduce(d1)
    # seed 0 influenza 3
    s.infect(0, d1, 3)
    # order influenza 7
    s.order(25, d1, 7)
    s.initialize()
    # plot influenza
    s.plot(d1)
    return (s)


# Multiple groups
def test5():
    # new 500 0.001 [[1.0,0.5,0.5],[0.5,1.0,0.5],[0.5,0.5,1.0]]
    s = EventSimulation(500, 0.001, [[1.0, 0.5, 0.5], [0.5, 1.0, 0.5], [0.5, 0.5, 1.0]])
    # add 100 0
    s.populate(100, 0)
    # add 50 1
    s.populate(50, 1)
    # add 200 2
    s.populate(200, 2)
    # virus influenza 0.95 2 7 0
    d1 = Virus('influenza', 0.95, 2, 7, 0)
    s.introduce(d1)
    # virus mumps 0.99 17 10 0.99
    d2 = Virus('mumps', 0.99, 17, 10, 0.99)
    s.introduce(d2)
    # seed 0 influenza 3
    s.infect(0, d1, 3)
    # seed 24 mumps 10
    s.infect(100, d2, 10)
    # order mumps 10
    s.order(118, d2, 10)
    # initialize
    s.initialize()
    # plot influenza
    s.plot(d1)
    # plot mumps
    s.plot(d2)
    return (s)
