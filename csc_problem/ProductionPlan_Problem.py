import numpy as np

from pymoo.optimize import minimize
from pymoo.core.problem import Problem
from pymoo.algorithms.moo.nsga2 import NSGA2

from csc_problem.MaterialSourcing_Problem import MaterialSourcing_Problem

from operators.MaterialSourcing_Crosover import MaterialSourcing_Crossover
from operators.MaterialSourcing_Mutation import MaterialSourcing_Mutation
from operators.MaterialSourcing_Sampling import MaterialSourcing_Sampling

import time

class ProductionPlan_Problem(Problem):

    def get_material_market_cap(self):
        '''
        Returns for each material how much of it can be purchaced on the whole market (all suppliers).

        Parameters:
        -----------
        n_products : int
            The number of products that can be produced.
        Cap : np.array (2D)
            The the production capacity, or maximum order quantity, for each material (row) at each supplier (column).
        material_at_gene : numpy_array (2D)
            Array containing for each possible purchace in Cap to which material it belongs.

        Returns:
        --------
        material_market_cap : np.array
            Array containining for each material how much can be porchaced at the market.
        '''

        material_market_cap = np.zeros(self.n_products)

        for product_index in range(self.n_products):
            current_product_indices = np.where(self.material_at_gene == product_index + 1)[0]
            material_market_cap[product_index] = self.Cap[current_product_indices].sum()

        return material_market_cap

    def xu_of_products(self, Cap, Mc):
        '''
        Returns per product the theoretical maximum that could be produced (if no other product would be pdoruced).
        Needs tp be called after self.n_products and self.n_materials are defined.

        Parameters:
        -----------
        Cap : numpy.array (2D)
            The the production capacity, or maximum order quantity, for each material (row) at each supplier (column).
        Mc : numpy.array (2D)
            The material (column) cost of each product (row).
        
        Returns:
        --------
        xu_products : numpy.array
            The theoretical maximum amount of each product that could be produced with all resources on the market.
        '''
        xu_products = []

        market_cap = np.ravel( np.sum(Cap, axis=1) )
        for p_index in range(self.n_products):
            curr_p_m_cost = Mc[p_index]
            current_upper_limit = np.iinfo(np.int64).max
            for m_index in range(self.n_materials): #the cost for each material
                curr_m_cost = curr_p_m_cost[m_index]
                production_limit_p_m = np.floor( curr_m_cost / market_cap[m_index] )#the production limit only concerning the current material
                if curr_m_cost != 0 and production_limit_p_m < current_upper_limit:
                    current_upper_limit = production_limit_p_m
            xu_products.append(current_upper_limit)
        
        return xu_products

    def __init__(self, 
                 n_materials, n_suppliers, n_products, Moq, Cap, Mp, Type, Mc, Sp, F,
                 stopping_gen,
                 subpop_size, subpop_crossover, subpop_mutation, subpop_callback, subpop_stopping_gen=20, subpop_finalization_gen=50):
        '''
        Parameters:
        n_materials : int
            The number of materials in this problem.
        n_suppliers : int
            The number of suppliers in this problem.
        n_products : int
            The number of products in this problem
        Moq : numpy.array (2D)
            The minimum order quantity for each material (row) at each supplier (column).
        Cap : numpy.array (2D)
            The the production capacity, or maximum order quantity, for each material (row) at each supplier (column).
        Mp : numpy.array (2D)
            The price for each material (row) at each supplier (column).
        Type : numpy.array (2D)
            The material type for each material (row) at each supplier (column). False if virgin material, True if recycled material.
        Mc : numpy.array (2D)
            The material (column) cost of each product (row).
        Sp : numpy.array
            The sale price of each product.
        F : number
            The fixed cost.
        stopping_gen : number
            The final generation of the problem. This triggers the finalization step, evaluating the sub-populations over more generations.
        
        subpop_size : int
            The size of the lower population
        subpop_callback : Callback
            The (not initialized) callback to be used by the lower population.
        subpop_stopping_gen=20 : int
            The stopping cryterion of the lower population.
        subpop_finalization_gen=50 : int
            The stopping cryterion of the lower population in the final generation of the upper population (finalization step).
        '''

        self.F = F
        self.n_suppliers = n_suppliers
        self.n_materials = n_materials
        self.n_products = n_products

        self.Cap = np.ravel( Cap )
        cap_zero_indices = np.where(self.Cap == 0) #the indices where we the production capacity is zero
        self.Cap = np.delete(self.Cap, cap_zero_indices) #this contains obly the suppliers where material can be sourced from
        self.Moq = np.delete(np.ravel( Moq ), cap_zero_indices)
        self.Mp = np.delete(np.ravel( Mp ), cap_zero_indices)
        self.Type = np.delete(np.ravel( Type ), cap_zero_indices)

        self.material_at_gene = np.array( [np.ones(n_suppliers)*(i+1) for i in range(n_materials)] ) #contains for each gene to which material it corresponds
        self.material_at_gene = np.delete( np.ravel( self.material_at_gene ), cap_zero_indices)

        self.supplier_at_gene = np.array( [np.arange(start=1, stop=n_suppliers+1) for i in range(n_materials)] ) #contains for each gene to which supplier it corresponds
        self.supplier_at_gene = np.delete( np.ravel( self.supplier_at_gene ), cap_zero_indices)

        self.Sp = Sp
        self.Mc = Mc
        

        #initialize the callback
        self.lower_pop_callback = subpop_callback()
        xl = np.zeros( n_products )
        xu = self.xu_of_products(Cap, Mc)

        self.gen = 0
        self.stopping_gen = stopping_gen

        #initialize the sub-problem:
        self.material_sourcing_problem = MaterialSourcing_Problem(
            n_materials = self.n_materials,
            n_suppliers = self.n_suppliers,
            n_products = self.n_products,
            Moq = self.Moq,
            Cap = self.Cap,
            Mp = self.Mp,
            Source_Type=self.Type,
            production_plan=np.zeros(n_products), #this is why we need to initialize every time
            Mc=self.Mc,
            Sp=self.Sp,
            F=self.F
            )
        self.subpop_stopping_gen = subpop_stopping_gen
        self.subpop_finalization_gen = subpop_finalization_gen
        self.subpop_mutation = subpop_mutation
        self.subpop_vrossover = subpop_crossover
        self.subpop_size = subpop_size

        
        self.start_time = time.time()

        super().__init__(n_var=n_products,
                n_obj=2,
                xl=xl,
                xu=xu
                )

    def _evaluate(self, x, out, *args, **kwargs):

        #initialize the fitness:
        f1 = np.zeros(len(x))
        f2 = np.zeros(len(x))

        sub_problem_stopping_gen = self.subpop_stopping_gen
        if self.gen == self.stopping_gen - 1:
            sub_problem_stopping_gen = self.subpop_finalization_gen 

        for ind_id, ind in enumerate(x):#evaluate each individual separately
            #set the production plan for the problem:
            self.material_sourcing_problem.set_production_plan(new_production_plan = ind)
            
            #create the algorithm:
            algorithm = NSGA2(pop_size=self.subpop_size,
                  sampling=MaterialSourcing_Sampling(),
                  crossover=MaterialSourcing_Crossover(material_blocks = self.material_sourcing_problem.material_at_gene),
                  mutation=MaterialSourcing_Mutation(material_blocks = self.material_sourcing_problem.material_at_gene),
                )
            
            #run the sub-population:
            self.lower_pop_callback.set_upper_generation_and_individual(self.gen, ind_id)
            res = minimize(self.material_sourcing_problem,
                            algorithm,
                            ('n_gen', sub_problem_stopping_gen),
                            #seed=1,
                            callback=self.lower_pop_callback,
                            verbose=False)
            


            #extract the fitness values:
            f1[ind_id] = res.opt.get("F")[:,0].min()
            f2[ind_id] = res.opt.get("F")[:,1].min()


        out["F"] = np.column_stack([f1, f2])
        self.gen += 1

        s = time.time() - self.start_time
        m = s / 60
        h = m / 60
        print("evaluated generation", self.gen, ", running for", s, "seconds, or",m,"minutes, or", h,"hours" )

