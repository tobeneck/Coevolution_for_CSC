import numpy as np

from pymoo.core.mutation import Mutation

from csc_problem.ProductionPlan_Problem import ProductionPlan_Problem

class ProductionPlan_Mutation(Mutation):
    def __init__(self, sigma = 0, scale=0.25):
        super().__init__()
        self.sigma = sigma
        self.scale = scale


    def random_mutation(self, X, ind_to_mutate, problem:ProductionPlan_Problem, market_avainalbe_material):
        '''
        Randomly mutates a gene of the selected individual from the population. Produces feasible individuals.

        Parameters:
        -----------
        X : np.array(2D)
            The population to be mutated.
        ind_to_mutate : int
            Index of the individual to be mutated.
        problem : ProductionPlan_Problem
            The current problem configuration.
        market_avainalbe_material : np.array
            An array containing for each material, how much is still available on the market.
        '''
        gene_id_to_mutate = np.random.randint(0, problem.n_var)

        #get the max increace and the max decreace
        max_decreace = X[ind_to_mutate, gene_id_to_mutate]
        max_increace = np.floor(market_avainalbe_material / problem.Mc[gene_id_to_mutate]).min()


        #calculate the amount to change the gene depending on the increace or decreace
        random_change = np.random.normal(self.sigma, self.scale)
        amount_to_change = 0
        if random_change < 0:
            amount_to_change = np.round(random_change * max_decreace)
        if random_change > 0:
            amount_to_change = np.round(random_change * max_increace)

        #Set new value and make shure it stays in the possible bounds
        if amount_to_change < -max_decreace: #don't build less than 0 products
            amount_to_change = -max_decreace
        if amount_to_change > max_increace: #don't build more products than possible
            amount_to_change = max_increace
        X[ind_to_mutate, gene_id_to_mutate] += amount_to_change

    def repair_mutation(self, X, ind_to_mutate, problem:ProductionPlan_Problem, material_market_cap, market_avainalbe_material):
        '''
        This mutation repairs an individual by decreacing the amount of products to be build until the individual stays in the bounds of the market avainable material.

        Parameters:
        -----------
        X : np.array(2D)
            The population to be mutated.
        ind_to_mutate : int
            Index of the individual to be mutated.
        problem : ProductionPlan_Problem
            The current problem configuration.
        material_market_cap : np.array
            An array containing for each material how much of it is overall available at the market.
        market_avainalbe_material : np.array
            An array containing for each material, how much is still available on the market.
        '''

        #which materials are overporchaced:
        indices_to_decreace = np.where(market_avainalbe_material < 0)[0]

        while indices_to_decreace.size != 0: #repair until no materials are overpurchaced
            #select the material that is overpurchaced the most for repair
            material_id_to_repair = np.argmin(market_avainalbe_material)

            #select a random product to be build less
            product_id_to_decreace = np.random.randint(0, problem.n_var)

            #calculate the min and max decreace
            max_decreace = X[ind_to_mutate, product_id_to_decreace] #the current genome value to not build less than 0 products
            min_decreace = np.ceil( -market_avainalbe_material[material_id_to_repair] / problem.Mc[product_id_to_decreace, material_id_to_repair] )#the decreace neccecary to repair the violation

            #catch if we can't repair the individual by decreacing just one product, or if min and max are the same
            if min_decreace >= max_decreace: #catch if min is bigger or equal to max to not build less than 0 products. In this case, we can't repair the individual by decreacing just one product.
                X[ind_to_mutate, product_id_to_decreace] = 0
            else: #If min is smaller tham max, we calculate a random amount to decreace the amount of products   
                #calculate the random change rate
                random_change = np.abs( np.random.normal(self.sigma, self.scale) )
                amount_to_decreace = np.round( random_change * (max_decreace - min_decreace) )
                
                #make shure the amount to change is in the bounds and change the gene
                if amount_to_decreace < min_decreace: amount_to_decreace = min_decreace
                if amount_to_decreace > max_decreace: amount_to_decreace = max_decreace
                X[ind_to_mutate, product_id_to_decreace] -= amount_to_decreace
            
            #re-calculate the material need and update the indices to decreace
            new_material_need = np.dot(X, problem.Mc)[ind_to_mutate]
            new_market_available_material = material_market_cap - new_material_need
            indices_to_decreace = np.where(new_market_available_material < 0)[0]


    def _do(self, problem:ProductionPlan_Problem, X, **kwargs):

        material_market_cap = problem.get_material_market_cap()

        #calculate the material need of the offspring to check feasability
        offspring_material_need = np.dot(X, problem.Mc)

        # for each individual
        for ind_id in range(len(X)):

            #calculate the material that is still available on the market
            market_avainalbe_material = material_market_cap - offspring_material_need[ind_id]

            #check if the individual exedes the market cap. If so, repair it!
            if market_avainalbe_material.min() < 0:
                self.repair_mutation(X=X, ind_to_mutate=ind_id, problem=problem, market_avainalbe_material=market_avainalbe_material, material_market_cap=material_market_cap)
            
            else: #Mutate randomly if repair is not needed
                self.random_mutation(X=X, ind_to_mutate=ind_id, problem=problem, market_avainalbe_material=market_avainalbe_material)

        return X

