import random
from time import time
from evalFuncs import *

from deap import base
from deap import creator
from deap import tools

start_time = time()

#------Modifiable values (notable ones)----------------
n_inds = 6 # Number of genes in each chromosome
n_pop  = 8 # Number of chromosomes in each genome
#------------------------------------------------------

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()
# Attribute generators
toolbox.register("attr_bool", random.randint, 0, 1)
toolbox.register("attr_255", random.randint, 0, 255)

# Structure initializers

toolbox.register("individual", tools.initRepeat, creator.Individual, 
    toolbox.attr_bool, n_inds)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

#-------Evaluation Functions---------------------------
# imported evalFuncs.py
#-------------------------------------------------------   

# Operator registering
toolbox.register("evaluate", evalhalf01)
toolbox.register("mate", tools.cxTwoPoints)
toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
toolbox.register("select", tools.selTournament, tournsize=3)

def main():
    #random.seed(64)
    
    pop = toolbox.population(n=n_pop)
    for i in pop:
      print pop.index(i), i


    CXPB, MUTPB, NGEN = 0.5, 0.2, 5000
    
    print("Start of evolution")
    
    # Evaluate the entire population
    fitnesses = list(map(toolbox.evaluate, pop))
    print fitnesses
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit
    
    print("  Evaluated %i individuals" % len(pop))
    
    # Begin the evolution
    for g in range(NGEN):
        k = g+1
        print("-- Generation %i --" % k)
        
        # Select the next generation individuals
        offspring = toolbox.select(pop, len(pop))
        # Clone the selected individuals
        offspring = list(map(toolbox.clone, offspring))
    
        # Apply crossover and mutation on the offspring
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < CXPB:
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values

        for mutant in offspring:
            if random.random() < MUTPB:
                toolbox.mutate(mutant)
                del mutant.fitness.values
    
        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit
        
        print("  Evaluated %i individuals" % len(invalid_ind))
        
        # The population is entirely replaced by the offspring
        pop[:] = offspring
        
        # Gather all the fitnesses in one list and print the stats
        fits = [ind.fitness.values[0] for ind in pop]
        
        length = len(pop)
        mean = sum(fits) / length
        sum2 = sum(x*x for x in fits)
        std = abs(sum2 / length - mean**2)**0.5
        mx = float(max(fits))
        mxp = (mx*100) / n_inds

        print("  genes %s" % n_inds)
        print("  chromosomes %s" % n_pop)
        print("  Min %s" % min(fits))
        print("  Max %s" % max(fits))
        print("  mxp %.3f %%" % mxp)
        print("  Avg %s" % mean)
        print("  Std %s" % std)

        for i in pop:
          print pop.index(i), i, i.fitness.values

        if max(fits) == n_inds:
            break
    
    print("-- End of (as NGEN set) evolution --")
    
    best_ind = tools.selBest(pop, 1)[0]
    print("Best individual is %s, %s" % (best_ind, best_ind.fitness.values))

if __name__ == "__main__":
    main()

print "Took: ", time()-start_time, " seconds"