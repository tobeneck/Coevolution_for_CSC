import numpy as np
from pymoo.core.problem import Problem

class MaterialSourcing_Problem(Problem):

    def set_production_plan(self, new_production_plan):
        '''
        Sets a new production plan, or a new problem instance for the material sourcing problem. 
        
        Parameters:
        -----------
        new_production_plan : np.array
            The new production plan as a new problem instance.
        '''
        #calculate profit for the production plan after the fixed cost
        income = new_production_plan * self.Sp
        self.profit = income.sum() - self.F

        #calculate the materials needed for the production plan
        self.materials_needed = (new_production_plan * self.Mc).sum(axis=1)

    def __init__(self, n_materials, n_suppliers, n_products, Moq, Cap, Mp, Source_Type, production_plan, Mc, Sp, F):
        '''
        Parameters:
        -----------
        n_materials : int
            The number of materials in this problem.
        n_suppliers : int
            The number of suppliers in this problem.
        n_products : int
            The number of products that can be produced.
        Moq : numpy.array (2D)
            The minimum order quantity for each material (row) at each supplier (column).
        Cap : numpy.array (2D)
            The the production capacity, or maximum order quantity, for each material (row) at each supplier (column).
        Mp : numpy.array (2D)
            The price for each material (row) at each supplier (column).
        Type : numpy.array (2D)
            The material type for each material (row) at each supplier (column). False if virgin material, True if recycled material.
        production_plan : numpy_array (2D)
            Vector containing for each product how much is be produced. This determines the profit and what materials need to be sourced.
        Mc : numpy.array (2D)
            The material (column) cost of each product (row).
        Sp : numpy.array
            The sale price of each product.
        F : number
            The fixed cost.

        '''

        self.n_suppliers = n_suppliers
        self.n_materials = n_materials
        self.n_products = n_products

        self.Cap = np.ravel( Cap )
        cap_zero_indices = np.where(self.Cap == 0) #the indices where we the production capacity is zero
        self.Cap = np.delete(self.Cap, cap_zero_indices) #this contains obly the suppliers where material can be sourced from
        self.Moq = np.delete(np.ravel( Moq ), cap_zero_indices)
        self.Mp = np.delete(np.ravel( Mp ), cap_zero_indices)
        self.Source_Type = np.delete(np.ravel( Source_Type ), cap_zero_indices)

        self.material_at_gene = np.array( [np.ones(n_suppliers)*(i+1) for i in range(n_materials)] ) #contains for each gene to which material it corresponds
        self.material_at_gene = np.delete( np.ravel( self.material_at_gene ), cap_zero_indices)
        
        self.supplier_at_gene = np.array( [np.arange(start=1, stop=n_suppliers+1) for i in range(n_materials)] ) #contains for each gene to which supplier it corresponds
        self.supplier_at_gene = np.delete( np.ravel( self.supplier_at_gene ), cap_zero_indices)
        
        self.Mc = Mc
        self.Sp = Sp
        self.F = F

        self.set_production_plan(production_plan)#sets the materials needed and the profit

        xl = np.zeros( len(self.Cap) )
        xu = self.Cap

        super().__init__(n_var=np.count_nonzero(Cap),
                n_obj=2,
                xl=xl,
                xu=xu
                )
    

    def f2(self, x):
        '''
        Calculates the second objective, which is the ratio of recycled material used in production.
        As this would be a maximization problem, the ratio is returned as a negative number.

        Parameters:
        -----------
        x : np.array()
            The population to be evaluated.

        Returns:
        --------
        inverted_recycled_material_ratio : np.array
            The ratio of recycled material used in production *-1 to make it a minimization problem.
        '''

        all_material_sourcing = x[:,:len(self.Mp)]

        virgin_material_sources = np.where(self.Source_Type == False)
        recycled_material_sourcing = np.delete(all_material_sourcing, virgin_material_sources, axis=1)

        all_material = all_material_sourcing.sum(axis=1)
        recycled_material = recycled_material_sourcing.sum(axis=1)

        #replace all zero values with ones to avoid dividing by zero. Not buying any material is considered to be maximally sustainable.
        nothing_bought = np.where(all_material == 0)
        all_material[nothing_bought] = 1
        recycled_material[nothing_bought] = 1

        recycled_material_ratio = recycled_material / all_material

        return recycled_material_ratio * -1

    def f1(self, x):
        '''
        Returns the first objective, the profit.

        Parameters:
        -----------
        x : np.array()
            The population to be evaluated.

        Returns:
        --------
        income : np.array
            The income generated from selling the product *-1 to make it a minimization problem.
        '''
        pop_size = len(x)

        #calculate cost
        material_sourcing = x[:,:len(self.Mp)]
        Mp = np.full( (pop_size, len(self.Mp)), self.Mp )
        cost = material_sourcing * Mp
        cost = cost.sum(axis=1)
        
        return (self.profit - cost) * -1
        


    def _evaluate(self, x, out, *args, **kwargs):
        f1 = self.f1(x)
        f2 = self.f2(x)
        out["F"] = np.column_stack([f1, f2])

