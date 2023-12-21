"""
QLearner
  		  	   		  		 		  		  		    	 		 		   		 		  
Engineer: Colten Appleby
"""

import numpy as np
class QLearner(object):
    """  		  	   		  		 		  		  		    	 		 		   		 		  
    This is a Q learner object.  		  	   		  		 		  		  		    	 		 		   		 		  
  		  	   		  		 		  		  		    	 		 		   		 		  
    :param num_states: The number of states to consider.  		  	   		  		 		  		  		    	 		 		   		 		  
    :type num_states: int  		  	   		  		 		  		  		    	 		 		   		 		  
    :param num_actions: The number of actions available..  		  	   		  		 		  		  		    	 		 		   		 		  
    :type num_actions: int  		  	   		  		 		  		  		    	 		 		   		 		  
    :param alpha: The learning rate used in the update rule. Should range between 0.0 and 1.0 with 0.2 as a typical value.  		  	   		  		 		  		  		    	 		 		   		 		  
    :type alpha: float  		  	   		  		 		  		  		    	 		 		   		 		  
    :param gamma: The discount rate used in the update rule. Should range between 0.0 and 1.0 with 0.9 as a typical value.  		  	   		  		 		  		  		    	 		 		   		 		  
    :type gamma: float  		  	   		  		 		  		  		    	 		 		   		 		  
    :param rar: Random action rate: the probability of selecting a random action at each step. Should range between 0.0 (no random actions) to 1.0 (always random action) with 0.5 as a typical value.  		  	   		  		 		  		  		    	 		 		   		 		  
    :type rar: float  		  	   		  		 		  		  		    	 		 		   		 		  
    :param radr: Random action decay rate, after each update, rar = rar * radr. Ranges between 0.0 (immediate decay to 0) and 1.0 (no decay). Typically 0.99.  		  	   		  		 		  		  		    	 		 		   		 		  
    :type radr: float  		  	   		  		 		  		  		    	 		 		   		 		  
    :param dyna: The number of dyna updates for each regular update. When Dyna is used, 200 is a typical value.  		  	   		  		 		  		  		    	 		 		   		 		  
    :type dyna: int  		  	   		  		 		  		  		    	 		 		   		 		  
    :param verbose: If “verbose” is True, your code can print out information for debugging.  		  	   		  		 		  		  		    	 		 		   		 		  
    :type verbose: bool  		  	   		  		 		  		  		    	 		 		   		 		  
    """
    def __init__(
        self,
        num_states=100,
        num_actions=4,
        alpha=0.2,
        gamma=0.9,
        rar=0.5,
        radr=0.999,
        dyna=0,
        verbose=False,
    ):
        """
        Constructor method
        """
        self.a = None
        self.s = None
        self.verbose = verbose
        self.num_actions = num_actions
        self.num_states = num_states
        self.alpha = alpha
        self.gamma = gamma
        self.rar = rar
        self.radr = radr
        self.dyna = dyna
        self.Q = np.zeros(shape=(num_states, num_actions))
        self.T = np.full(shape=(num_states, num_actions, num_states), fill_value=0.0001)
        self.R = np.zeros(shape=(num_states, num_actions))
        self.moves = []


    def author(self):
        return "cappleby3"

    def querysetstate(self, s):
        """  		  	   		  		 		  		  		    	 		 		   		 		  
        Update the state without updating the Q-table  		  	   		  		 		  		  		    	 		 		   		 		  
  		  	   		  		 		  		  		    	 		 		   		 		  
        :param s: The new state  		  	   		  		 		  		  		    	 		 		   		 		  
        :type s: int  		  	   		  		 		  		  		    	 		 		   		 		  
        :return: The selected action  		  	   		  		 		  		  		    	 		 		   		 		  
        :rtype: int  		  	   		  		 		  		  		    	 		 		   		 		  
        """
        self.s = s
        self.a = np.random.randint(0, self.num_actions)
        # self.a = self.get_action(s)
        if self.verbose: print(f"s = {s}, a = {self.a}")
        return self.a

    def get_action(self, state):
        if np.random.rand() <= self.rar:
            return np.random.randint(0, self.num_actions)
        else:
            return np.argmax(self.Q[state])

    def update_Q(self, state, action, s_prime, reward):
        self.Q[state, action] = ((1-self.alpha) * self.Q[state, action]
                                 + self.alpha * (reward + self.gamma * np.max(self.Q[s_prime])))

    def hallucinate(self):
        for i in range(0, self.dyna):
            state, action, s_prime, reward = self.moves[np.random.randint(0, len(self.moves))]
            self.update_Q(state, action, s_prime, reward)

    def query(self, s_prime, r):
        """  		  	   		  		 		  		  		    	 		 		   		 		  
        Update the Q table and return an action  		  	   		  		 		  		  		    	 		 		   		 		  
  		  	   		  		 		  		  		    	 		 		   		 		  
        :param s_prime: The new state  		  	   		  		 		  		  		    	 		 		   		 		  
        :type s_prime: int  		  	   		  		 		  		  		    	 		 		   		 		  
        :param r: The immediate reward  		  	   		  		 		  		  		    	 		 		   		 		  
        :type r: float  		  	   		  		 		  		  		    	 		 		   		 		  
        :return: The selected action  		  	   		  		 		  		  		    	 		 		   		 		  
        :rtype: int  		  	   		  		 		  		  		    	 		 		   		 		  
        """

        """      
        1. We are first going to update the model. Hey this is what happened last turn
        - The model knows the previous location and the last action (saved above)
        - Now it was given the new location, and the reward
        --> Update the model! with the previous move we gained this reward
        
        2. Now we need to generate a new action, and update our saved information
        """

        self.update_Q(self.s, self.a, s_prime, r)

        self.moves.append([self.s, self.a, s_prime, r])
        self.hallucinate()

        self.a = self.get_action(s_prime)
        self.s = s_prime
        self.rar *= self.radr

        if self.verbose:
            print(f"s = {s_prime}, a = {self.a}, r={r}")

        return self.a

    def save_to_csv(self, filename):
        # np.save(filename, self.Q)
        np.savetxt(filename, self.Q, delimiter=",")

    def save_to_npy(self, filename):
        np.save(filename, self.Q)

    def load_existing_model(self, filename):
        self.Q = np.load(filename)

if __name__ == "__main__":
    print("Remember Q from Star Trek? Well, this isn't him")
