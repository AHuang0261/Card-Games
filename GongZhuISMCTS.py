from GongZhuEngine import *
import GongZhuEngine
import numpy as np
import copy

'''ToDo

The randomization adds some additional subtlty to the tree that I don't wanna deal w right now. The main benefit is for bluffing which may not be important just yet maybe in the next version
Also, now that I'm working on it, I don't see how the random set has valid "next options" cause it generates random values. Maybe I need to set the hands after playing that card
Need to come up with an intelligent scoring system. Maybe a second term that rewards knockouts and punishes knocking self out
See Tree Policy for more comments
'''
class ISMCTSNode():
    #state -> POVGongZhuEngine object, Parent, ISMCTSNode object, parent action GZCard object
    def __init__(self, state, parent = None, parent_action = None):
        self.state = state
        self.parent = parent
        self.parent_action = parent_action
        self.children = []
        self.number_of_visits = 0
        self.results = 0
        self.untried_actions = []
    
    def get_untried_actions(self):
        
        curr_hand = self.state.players[self.state.current_player].hand
        if self.state.is_leader: return curr_hand
        
        legal_cards = []        
        for card in curr_hand:
            if self.state.check_card(card):
                legal_cards.append(card)
        return legal_cards

    def calc_results(self):
        pass

    def expand(self):
        action = self.untried_actions.pop()
        next_state = self.state.next_state(action) 
        child = ISMCTSNode(next_state, parent = self, parent_action= action)
        self.children.append(child)
        return child
    
    #simulate possible game from current game state
    def rollout(self):
        current_state = self.state.copy()
        while not current_state.is_round_over():
            # print(self.state.pov_hand)
            action = current_state.random_select()
            current_state = current_state.next_state(action)

            if current_state is None:
                print("Error: next_state is None after action", action)
                break
        # print(f"Game score: {current_state.score_game()}")
        return current_state.score_game()
    
    def backpropagate(self, result):
        self.number_of_visits += 1
        self.results += result #!change this to be correct
        if self.parent:
            self.parent.backpropagate(result)

    def is_fully_expanded(self):
        return len(self.untried_actions) == 0
    
    def best_child(self, explore_weight = 0.1):
        # print(f"Children: {self.children}")
        choice_scores = [c.results/c.number_of_visits + explore_weight * np.sqrt(np.log(self.number_of_visits) / c.number_of_visits) for c in self.children]
        return self.children[np.argmax(choice_scores)]

    '''
    Not sure what the algorithm is supposed to be. If I'm supposed to expand all the way down the tree then I need to make sure I'm properly handling the state.
    However, back of envlope calculation of [Prod (k)]^4 for k in {1,...,13} suggestsw that this tree is too big E39 for k = 13, E14 for k = 7
    Might only look at next action and remove while loop

    '''

    def tree_policy(self, is_all_random):
        self.state.set_hands(is_all_random)
        selected_node = self
        if is_all_random: #Deal with this later
            self.untried_actions = self.get_untried_actions()
        
        # print(f"Untried actions: {self.untried_actions}")
        if not self.is_fully_expanded():
            return self.expand()
        else:
            selected_node = selected_node.best_child(explore_weight=0.1)
        # print(f"Action: {selected_node.parent_action}")
        return selected_node

    # def tree_policy(self, is_all_random):
    #     current_node = self
    #     if current_node.parent == None:
    #         self.state.set_hands(is_all_random)
    #     while not current_node.is_terminal_node():
    #         if is_all_random: #Deal with this later
    #             self.untried_actions = self.get_untried_actions()
    #         print(f"Untried actions: {self.untried_actions}")
    #         if not current_node.is_fully_expanded():
    #             return current_node.expand()
    #         else:
    #             current_node = current_node.best_child(explore_weight=0.1)
    #     print(f"Action: {current_node.parent_action}")
    #     return current_node

    def is_terminal_node(self):
        return self.state.is_round_over()
    
    def best_action(self):
        initial_state = self.state.copy()
        self.untried_actions = self.get_untried_actions()
        simulations = 1000 #1000 sims takes abt 300 ms
        if len(self.untried_actions) > 4: simulations = 250 * len(self.untried_actions)
        # first_non_random = True
        for i in range(simulations):
            # print(f"Iteration {i}")
            # print(f"\nIteration: {i} Operated Node: {self} State object: {self.state} Children: {self.children} {len(self.children)}")
            # print(f"\nIteration: {i} Operated Node: {self} ")
            self.state = initial_state.copy()
            # node_copy = ISMCTSNode(state_copy, self.parent, self.parent_action)
            # v = self.tree_policy(i < simulations * 0.3) 
            # if first_non_random:
            #     self.untried_actions = self.get_untried_actions()
            #     first_non_random = False
            v = self.tree_policy(False)
            reward = v.rollout()
            v.backpropagate(reward)
            # print(v)
        
        # print(f"Self Children: {len(self.children)} v children{len(v.children)}")
        print(f"Best Child Action {self.best_child(explore_weight=0.0).parent_action}")
        return self.best_child(explore_weight=0.0).parent_action

        # for i in range(simulations):
        # # Create a deep copy of the current state before running a simulation
        #     copied_state = copy.deepcopy(self.state)
        #     copied_node = ISMCTSNode(copied_state, parent=self.parent, parent_action=self.parent_action)
            
        #     v = copied_node.tree_policy(i < simulations * 0.3)
        #     reward = v.rollout()
        #     v.backpropagate(reward)
    
        # return self.best_child(explore_weight=0.0)
