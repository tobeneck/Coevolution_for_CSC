import numpy as np

from pymoo.core.sampling import Sampling

from csc_problem.MaterialSourcing_Problem import MaterialSourcing_Problem

class MaterialSourcing_Sampling(Sampling):
            

    def _do(self, problem : MaterialSourcing_Problem, n_samples, **kwargs):

        X = np.zeros((n_samples, problem.n_var), dtype=int)

        Cap = problem.Cap
        Moq = problem.Moq
        n_materials = problem.n_materials
        material_at_gene = problem.material_at_gene

        materials_needed = np.array( [problem.materials_needed for i in range(n_samples)] )


    
        for ind_id in range(n_samples):#sample each individual separately
            for material_id in range(0, n_materials): #sample for each material block separately
                current_block = np.where(material_at_gene == material_id+1)[0]
                if current_block.size != 0: #don`t sample anythink if the block is not needed
                    while materials_needed[ind_id, material_id] > 0: #sample one block until the material need is met
                        
                        #choose a random supplier:
                        supplier_index_to_buy_from = np.random.choice(current_block)

                        #get what is still needed
                        current_need = materials_needed[ind_id, material_id]                        


                        #calc maximum to buy
                        max_to_buy = min([ current_need, Cap[supplier_index_to_buy_from] - X[ind_id, supplier_index_to_buy_from]])
                        if max_to_buy <= 0: #start again if the maximum is already bought
                            continue
                        
                        
                        #calc the min to buy
                        min_to_buy = 1
                        if X[ind_id, supplier_index_to_buy_from] < Moq[supplier_index_to_buy_from]: #is we don't already order the Moq thats the new min
                            min_to_buy = Moq[supplier_index_to_buy_from]
                            
                        
                        #if we need less then the min, we have to purchace the min. Otherwise we randomly sample.
                        amount_to_buy = min_to_buy
                        if min_to_buy < max_to_buy:
                            amount_to_buy = np.random.randint(min_to_buy, max_to_buy + 1)
                        
                        X[ind_id, supplier_index_to_buy_from] += amount_to_buy
                        materials_needed[ind_id, material_id] = current_need - amount_to_buy


        #print(X)
        #maybe future improvement: repair to lower the amount of material purchaced, it it is not going to be less than Moq then. This should probably also be done randomly to avoid bias. DANGER: there can be cases where every Moq is purchaced and nothing can be lowered!
        #for ind_id in range(n_samples):
        #    for material_id in range(0, n_materials): #sample for each material block separately
        #        current_block = np.where(material_at_gene == material_id+1)[0]
        #        print(ind_id, material_id+1, np.sum(X[ind_id, current_block]))
        
        return X