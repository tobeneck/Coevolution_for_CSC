import numpy as np
import pandas as pd

from pymoo.core.algorithm import Algorithm

from csc_problem.Lower_Pop_Callback import Lower_Pop_Callback

class CSC_Coevolution_Callback(Lower_Pop_Callback):

    def __init__(self) -> None:
        super().__init__()

        self.column_names = ["upper_gen", "upper_ind", "lower_gen", "lower_ind", "f_1", "f_2"]
        self.fitness_data = pd.DataFrame(columns=self.column_names)

    def notify(self, algorithm: Algorithm):
        #build the data to be saved
        fitness = algorithm.pop.get("F") * -1 #make it a maximization problem again
        current_gen_fitness_data = np.array( 
            [ np.append( np.array([self.upper_gen, self.upper_ind_id, algorithm.n_gen - 1, ind_id]), f ) for ind_id, f in enumerate(fitness)]
            )
        current_gen_fitness_data = pd.DataFrame(current_gen_fitness_data, columns=self.column_names)

        #save it to a dataframe
        self.fitness_data = pd.concat([self.fitness_data, current_gen_fitness_data], ignore_index=True)

        


