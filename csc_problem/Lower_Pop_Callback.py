import numpy as np
import pandas as pd

from pymoo.core.callback import Callback
from pymoo.core.algorithm import Algorithm

class Lower_Pop_Callback(Callback):

    def set_upper_generation_and_individual(self, upper_gen, upper_ind_id):
        '''
        Sets upper generation and upper individual.

        Parameters:
        -----------
        upper_gen : int
            The current generation of the upper population.
        upper_ind_id : int
            The current individual of the upper generation this lowe rpopulation belongs to.
        '''
        self.upper_gen = upper_gen
        self.upper_ind_id = upper_ind_id
        print("processed ind ", upper_ind_id, "in upper generation", upper_gen)

    def __init__(self) -> None:
        '''
        This class just is a container that provides a method to update the generation and individual ID of the upper and lower population.
        '''
        super().__init__()

        self.upper_gen = 0
        self.upper_ind_id = 0

        


