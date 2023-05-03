import numpy as np

from pymoo.operators.crossover.ux import UniformCrossover
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize

from csc_problem.ProductionPlan_Problem import ProductionPlan_Problem
from operators.ProductionPlan_Sampling import ProductionPlan_Sampling
from operators.ProductionPlan_Mutation import ProductionPlan_Mutation

from operators.MaterialSourcing_Crosover import MaterialSourcing_Crossover
from operators.MaterialSourcing_Mutation import MaterialSourcing_Mutation

from callback import CSC_Coevolution_Callback

#EA parameters
upper_stopping_gen = 20
upper_pop_size = 20

lower_pop_size = 20
lower_stopping_gen = 20
lower_finalization_stopping_gen = 50

#problem instance
F = 50
n_materials = 2
n_products = 2
n_suppliers = 3

Moq = [[15, 2, 1],
        [10, 3, 2]]
Cap = [[100, 20, 30],
        [70, 30, 50]]
Mp  = [[2, 2.5, 3],
        [2, 2.5, 2.5]]
Type  = [[False, False, True],
            [False, False, True]]
Mc = [[3, 1],
        [1, 3]]
Sp = [15, 15]

Moq = np.ravel( np.array(Moq) )
Cap = np.array(Cap)
Mp = np.array(Mp)
Mc = np.array(Mc)
Sp = np.array(Sp)

production_plan_problem = ProductionPlan_Problem(n_materials,
                n_suppliers,
                n_products,
                Moq,
                Cap,
                Mp,
                Type,
                Mc,
                Sp,
                F,
                stopping_gen=upper_stopping_gen,
                subpop_size=lower_pop_size,
                subpop_crossover=MaterialSourcing_Crossover,
                subpop_mutation=MaterialSourcing_Mutation,
                subpop_callback=CSC_Coevolution_Callback,
                subpop_stopping_gen=lower_stopping_gen,
                subpop_finalization_gen=lower_finalization_stopping_gen
                )

#run the test
upper_algorithm = NSGA2(pop_size=upper_pop_size,
                  sampling=ProductionPlan_Sampling(),
                  crossover=UniformCrossover(),
                  mutation=ProductionPlan_Mutation(),
                )

res = minimize(production_plan_problem,
               upper_algorithm,
               ('n_gen', upper_stopping_gen),
               seed=1,
               verbose=False)

#save the fitness data
fitness_data = production_plan_problem.lower_pop_callback.fitness_data
fitness_data.to_csv("test_20_plus_50.csv")