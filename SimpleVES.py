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
    return(random() <= p)


#
# virus model. Each virus has a name, and a coefficient to model transmission rate,
# Model data provided by Dr. Segre
# coefficient for recovery,exposure rate, and infection duration.
class Virus():
    def __init__(self, name='Bubonic', t=0.95, Ex=2, ID=7, s=0.0):
        self.name=name
        self.t=t         # Transmission likelihood
        self.Ex=Ex       # exposure
        self.ID=ID       # infection duration
        self.s=s         # probability of sustained immunity

# Actor model. Model detail provided by Dr. Segre
#
# Each Actor has a susceptibility chance,
# a vaccination state,
# and a counter that is used to model their current state
class Actor():
    def __init__(self, w=0.99):
        self.w = w       # Weakness, susceptibility increases as value gets smaller
        self.v = 1.0     # Vaccination state
        self.s = -1      # Current state affected by virus
        self.virus = None

    # Return True if infectious (i.e., in ID or Ex state)

    def state(self):
        '''if Actor is infectious, return true.'''
        return(self.s > 0)

    # Set the Actor's vaccination value to whatever value you give.
    def vaccinate(self, v):
        '''Vaccination Approx: Complete immunity, v=0 ; No immunity, v=1.'''
        self.v = v

    # Weakness: if an infected is present, initiate Probability ->state
    # ID+Ex incremented by 1: initialize() updates state


    def infect(self, vector, virus):
        '''vector tries to infects self with virus.'''
        if vector.state() and self.s < 0 and initiateProbability(self.w*self.v*virus.t):
            self.s = virus.Ex + virus.ID + 1
            self.virus = virus
            return(True)
        return(False)

    # Actor's state update. Decrease counter if infected.
    # When it becomes 0, initiate a probability
    # If state c=0 else state S c=-1.
    def update(self):
        '''Current Update.'''
        if self.s == 1:
            if not initiateProbability(self.virus.s):
                # deteriorate to weak, c=-1.
                self.s = -1
            else:
                # Sustained immunity, c=0.
                self.s = 0
            # Remove virus value.
            self.virus = None
        elif self.s > 1:
            # Approach recovering state
            # For viruses like SARS2, consider
            # Nonlinear modeling for recovery
            # like weight probability for
            # relapse
            self.s = self.s - 1
            return(True)
        return(False)

# VES is set to run for days set by time t
class EventSimulation():
    def __init__(self, t=500):
        self.rounds = t		# Maximum number of timesteps
        self.Actors = None      # List of Actors in VES
        self.virus = None       # Virus being modeled
        self.record = []       # Tuples of (Ex, ID) record
        self.p = 0.001          # variable parameter, mixing

    # VES has n Actors instantiated and sets the variable parameter

    def populate(self, n, p = 0.01):
        '''instantiates n Actors, with probability p'''
        self.p = p
        self.Actors = []
        for i in range(n):
            self.join(Actor())

    # Add Actor to current VES
    def join(self, Actor):
        '''Add specified Actor to VES.'''
        self.Actors.append(Actor)

    # instantiate virus within VES
    # Phase 1 only allowed for 1(one) virus in class
    def introduce(self, virus):
        '''Add specified virus to current simulation.'''
        self.virus = virus

    # Seed the simulation with k Actors having the specified virus.
    def seed(self, virus, q=1):
        '''Seed a certain number of Actors with a particular virus.'''
        # Add the virus to the simulation.
        self.introduce(virus)
        # ID+Ex increment by 1
        for Actor in sample(self.Actors, q):
            Actor.s = virus.Ex + virus.ID + 1
            Actor.virus = virus

    # The initialize() method performs at most self.rounds
    # iterations, where each round:
    # updates the Actors,
    # counts how many are in Ex and ID states,
    # Determines if the virus wipes out all current hosts,
    # Resulting in early termination
    # infection  spreads according to the variable parameter, p.
    def initialize(self):
        '''Inititate VES.'''
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

    # Plots the self.record elements
    #
    def plot(self):
        plt.title('Viral Event Simulation')
        plt.axis( [0, len(self.record), 0, len(self.Actors)] )
        plt.xlabel('Days')
        plt.ylabel('N')
        plt.plot( [ i for i in range(len(self.record)) ], [ e for (e, i) in self.record ], 'g-', label='Individuals Exposed' )
        plt.plot( [ i for i in range(len(self.record)) ], [ i for (e, i) in self.record ], 'r-', label='Known infected' )
        plt.show()

# Test provided by TA
#
def test(n, m, k, name, time, exposure, ID, sustainedImmunity):
    virus = Virus(name, time, exposure, ID, sustainedImmunity)
    Z = EventSimulation()
    Z.populate(n, m)
    Z.seed(virus, k)
    Z.initialize()
    Z.plot()
    return(Z)

#Test data provided by TA and handout

if __name__ == '__main__':
   test(10, 0.001, 1, 'influenza', 0.99, 2, 7, 0.8)
   test(500, 0.001, 1, 'influenza', 0.95, 2, 7, 0.8)
   test(1000, 0.0005, 3, 'killmenow', 0.99, 3, 5, 1.0)
   test(1000, 0.0005, 3, 'killmelater', 0.99, 4, 10, 0.6)
