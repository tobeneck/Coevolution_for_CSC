import numpy as np

from pymoo.core.crossover import Crossover
from pymoo.util.misc import crossover_mask


class MaterialSourcing_Crossover(Crossover):

    def __init__(self, material_blocks, **kwargs):
        super().__init__(2, 2, **kwargs)

        self.material_blocks = material_blocks #this is a list containing for each genome to which material it corresponds
        self.unique_materials =np.unique(material_blocks)
        self.n_unique_materials = len(self.unique_materials)

    def _do(self, _, X, **kwargs):
        _, n_matings, n_var = X.shape
        
        #generate for each material block if we swap
        R = np.random.random((n_matings, self.n_unique_materials)) < 0.5 

        #create the crossover mask from the swapping information
        M = np.zeros((n_matings, n_var), dtype=bool)
        for i in range(n_matings):
            for j in range(n_var):
                M[i,j] = R[ i, int(self.material_blocks[j]) - 1 ]
            

        _X = crossover_mask(X, M)
        return _X