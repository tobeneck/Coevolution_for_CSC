import numpy as np

from pymoo.core.sampling import Sampling

from csc_problem.ProductionPlan_Problem import ProductionPlan_Problem

class ProductionPlan_Sampling(Sampling):

    def _do(self, problem : ProductionPlan_Problem, n_samples, **kwargs):

        X = np.zeros((n_samples, problem.n_var), dtype=int)
    
        for ind_id in range(n_samples):#sample each individual separately

            #create a random order to fill the genome
            genome_id_in_random_order = np.arange(problem.n_products)
            np.random.shuffle(genome_id_in_random_order)

            #calculate the market cap (max amount for each material that can be purchaced) for the current individual
            material_market_cap = problem.get_material_market_cap()

            for product_id in genome_id_in_random_order: #sample for gene / ampunt of products separately
                
                #calculate the maximum amount of product that could be produced
                product_cost = problem.Mc[product_id]
                limits = material_market_cap / product_cost
                limits = np.floor(limits)
                max_amount_of_product = min(limits)

                #generate the amount of products to be produced
                new_value = np.random.randint(0, max_amount_of_product + 1)

                #calculate the mew market cap for the next genome
                material_market_cap = material_market_cap - (product_cost * new_value)

                #set the value
                X[ind_id, product_id] = new_value
        
        return X