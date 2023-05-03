import numpy as np

from pymoo.core.mutation import Mutation

import sys
sys.path.append("..")
from csc_problem.MaterialSourcing_Problem import MaterialSourcing_Problem

class MaterialSourcing_Mutation(Mutation):
    def __init__(self, material_blocks, sigma = 0, scale=0.25):
        super().__init__()

        self.material_blocks = material_blocks
        self.unique_materials =np.unique(material_blocks)
        self.n_unique_materials = len(self.unique_materials)
        self.sigma = sigma
        self.scale = scale

    def _do(self, problem:MaterialSourcing_Problem, X, **kwargs):

        # for each individual
        for i in range(len(X)):

            #chose a random material block that should be mutated
            material_block_to_mutate = np.random.choice(self.unique_materials)
            current_block = np.where(self.material_blocks == material_block_to_mutate)[0]

            #we can not mutate a block that only contains one material (that should not exist anyway!)
            if len(current_block) == 1:
                continue

            #select a random gene in this block
            block_index = np.random.randint( 0, len(current_block) )
            genome_to_mutate = current_block[block_index]
            other_genes_in_material_block = np.delete(current_block, block_index)
            
            #calculate the change potential. This is either the current amount that is sourced at the selected supplier, or how much can be sourced at the rest of the suppliers
            change_potential = min( X[i, genome_to_mutate], np.sum(problem.Cap[other_genes_in_material_block]) - np.sum(X[i][other_genes_in_material_block]) )

            
            #cahculate the amount to be decreaced:
            random_change = abs(np.random.normal(self.sigma, self.scale)) 
            amount_to_decreace = round( random_change * change_potential )

            #handle exeptions:
            if amount_to_decreace > X[i, genome_to_mutate]: #don't decreace into negative numbers!
                amount_to_decreace = X[i, genome_to_mutate]
            if X[i, genome_to_mutate] - amount_to_decreace < problem.Moq[genome_to_mutate]: #if we are lower than Moq we roll a dice for Moq or 0.0
                if np.random.random() > 0.5:
                    amount_to_decreace = X[i, genome_to_mutate]
                else:
                    amount_to_decreace = X[i, genome_to_mutate] - problem.Moq[genome_to_mutate]

            #actually mutate the gene:
            X[i, genome_to_mutate] -= amount_to_decreace

            #repair the block again to buy enough material:
            amount_to_increace = amount_to_decreace
            while amount_to_increace > 0:
                gene_to_increace = np.random.choice(other_genes_in_material_block)

                X[i, gene_to_increace] += amount_to_increace#always try to increace by the full amount!
                if X[i, gene_to_increace] > problem.Cap[gene_to_increace]: #don't buy more than the maximum
                    amount_to_increace -= ( X[i, gene_to_increace] - problem.Cap[gene_to_increace] )
                    X[i, gene_to_increace] = problem.Cap[gene_to_increace]
                elif X[i, gene_to_increace] < problem.Moq[gene_to_increace]: #set to at least Moq. Can only happen if the gene value previously was 0
                    amount_to_increace -= problem.Moq[gene_to_increace]
                    X[i, gene_to_increace] = problem.Moq[gene_to_increace]
                else:
                    amount_to_increace -= amount_to_increace

        return X

