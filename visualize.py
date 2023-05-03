import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib as mlp
import matplotlib.pyplot as plt


from pymoo.util.nds.non_dominated_sorting import NonDominatedSorting


fitness_data = pd.read_csv("test_20_plus_50.csv")
print(fitness_data)

only_last_gen = fitness_data[fitness_data.upper_gen == fitness_data.upper_gen.max()]
only_last_gen = only_last_gen[only_last_gen.lower_gen == only_last_gen.lower_gen.max()]


#calculate the ranks / the NDS
fitness = only_last_gen[["f_1", "f_2"]].to_numpy() * -1 #port back to minimization!
nds = NonDominatedSorting()
ranks = np.array(nds.do(F=fitness, return_rank=True)[1])
nds_indices = np.where(ranks == 0)[0]
ds_indices = np.where(ranks != 0)[0]
only_last_gen_nds = only_last_gen.iloc[nds_indices]
only_last_gen_ds = only_last_gen.iloc[ds_indices]
print(only_last_gen_nds)


#set up the styling:
plt.style.use('seaborn-darkgrid')
palette=sns.color_palette('tab20')#sns.color_palette('tab20c') + sns.color_palette('tab20b')
sns.set_palette(palette)
mlp.rcParams.update({'font.size': 12}) #for paper 12, for poster 24

#plot the plot
ax = sns.scatterplot(data=only_last_gen_nds, y="f_1", x="f_2", hue="upper_ind", palette=palette, s=60) #for paper s=60, for poster s=120
ax.set(xlabel="f2 - percentage of recycled material", ylabel="f1 - profit")
plt.legend(title="production plan")

plt.savefig("result.pdf")
plt.show()