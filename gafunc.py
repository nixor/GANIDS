import random           #for most of the things done here
import fileinput        #for reading an audit dataset
import bisect           #for mapping different weights for members in a list
import itertools        #for eliminating duplicate lists in a list
import re               #for multiple delimiters in dataset files
import copy             #for making an unshared copy
from time import time   #for counting the amount of time GANIDS runs


from deap import base
from deap import creator
from deap import tools

from gaconfig import *

start_time = time()

# I ------Read DARPA audit files---*done*try put this in individuals--
auditData = []
#nosplit = []
for line in fileinput.input([fileName]):
    line = line.rstrip('\r\n') # strip off the newline of each record
    #nosplit.append(line)
    if len(line) > 0:
        line = re.sub(' +', ' ', line)
        array = line.split(" ")
# Now array looks like this
#['1', '01/23/1998', '16:56:48', '00:01:26', 'telnet', '1754', '23',
# '192.168.1.30', '192.168.0.20', '0', '-']

# Below we reconstruct the audit data to have chromosome-like structure.
        line = []
        #---Duration
        line.append(int(array[3][0:2])) #append hour as gene into chromosome
        line.append(int(array[3][3:5])) #append minute
        line.append(int(array[3][6:8])) #append second
        #---Protocal
        line.append(array[4])
        #---Source Port
        if array[5] != '-':
            line.append(int(array[5]))
        else:
            line.append(-1)
        #---Destination Port
        if array[6] != '-':
            line.append(int(array[6]))
        else:
            line.append(-1)
        #---Source IP
        ip = array[7].split(".")
        line.append(int(ip[0])) #1st octet
        line.append(int(ip[1])) #2nd octet
        line.append(int(ip[2])) #3rd octet
        line.append(int(ip[3])) #4th octet
        #---Destination IP
        ip = array[8].split(".")
        line.append(int(ip[0])) #1st octet
        line.append(int(ip[1])) #2nd octet
        line.append(int(ip[2])) #3rd octet
        line.append(int(ip[3])) #4th octet
        #---Attack type
        line.append(array[10])


    auditData.append(line)

# return auditData #when put in a function

#END I--------------------------------------------------------------

# II -------find unique values in each field from audit data----
uniq_hour = set()
uniq_minute = set()
uniq_second = set()
uniq_protocol = set()
uniq_srcport = set()
uniq_desport = set()

uniq_srcip_1stoct = set()
uniq_srcip_2ndoct = set()
uniq_srcip_3rdoct = set()
uniq_srcip_4thoct = set()

uniq_desip_1stoct = set()
uniq_desip_2ndoct = set()
uniq_desip_3rdoct = set()
uniq_desip_4thoct = set()

uniq_attack = set()

for i in auditData:
    uniq_hour.add(i[0])
    uniq_minute.add(i[1])
    uniq_second.add(i[2])
    uniq_protocol.add(i[3])
    uniq_srcport.add(i[4])
    uniq_desport.add(i[5])
    uniq_srcip_1stoct.add(i[6])
    uniq_srcip_2ndoct.add(i[7])
    uniq_srcip_3rdoct.add(i[8])
    uniq_srcip_4thoct.add(i[9])
    uniq_desip_1stoct.add(i[10])
    uniq_desip_2ndoct.add(i[11])
    uniq_desip_3rdoct.add(i[12])
    uniq_desip_4thoct.add(i[13])
    #uniq_attack.add(i[14])
    if i[14] != '-':
        uniq_attack.add(i[14])

print uniq_attack

uniq_hour = list(uniq_hour)
uniq_minute = list(uniq_minute)
uniq_second = list(uniq_second)
uniq_protocol = list(uniq_protocol)
uniq_srcport = list(uniq_srcport)
uniq_desport = list(uniq_desport)
uniq_srcip_1stoct = list(uniq_srcip_1stoct)
uniq_srcip_2ndoct = list(uniq_srcip_2ndoct)
uniq_srcip_3rdoct = list(uniq_srcip_3rdoct)
uniq_srcip_4thoct = list(uniq_srcip_4thoct)
uniq_desip_1stoct = list(uniq_desip_1stoct)
uniq_desip_2ndoct = list(uniq_desip_2ndoct)
uniq_desip_3rdoct = list(uniq_desip_3rdoct)
uniq_desip_4thoct = list(uniq_desip_4thoct)
uniq_attack = list(uniq_attack)

uniq_all = [] # List containing all uniqe_values in all fields

uniq_all.append(uniq_hour)
uniq_all.append(uniq_minute)
uniq_all.append(uniq_second)
uniq_all.append(uniq_protocol)
uniq_all.append(uniq_srcport)
uniq_all.append(uniq_desport)
uniq_all.append(uniq_srcip_1stoct)
uniq_all.append(uniq_srcip_2ndoct)
uniq_all.append(uniq_srcip_3rdoct)
uniq_all.append(uniq_srcip_4thoct)
uniq_all.append(uniq_desip_1stoct)
uniq_all.append(uniq_desip_2ndoct)
uniq_all.append(uniq_desip_3rdoct)
uniq_all.append(uniq_desip_4thoct)
uniq_all.append(uniq_attack)

#return uniq_all #when put in a function

#END II----------------------------------------------------------------

#-III -----Generator, Generate population: Build randomizor
#-for each field in a chromosome---------------------------------------

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()
# Attribute generator
toolbox.register("attr_bool", random.randint, 0, 1)

#---randomizor and chromosomizor

def randomizor(breakpoints,items):
    score = random.random() * breakpoints[-1]
    i = bisect.bisect(breakpoints, score)
    return items[i]

def chromosomizor(): #A function for building a chromosome.
    wcw = wildcardWeight
    an_individual = []
    for i, j in enumerate(uniq_all): # Using unique values from each field
        if i == (len(uniq_all)-1):
            wcw = 0.0 #we don't generate wildcard at attack field
        
        weight = {-1:wcw} #wcw
        for u in uniq_all[i]:
            #print len(uniq_all[i])
            # len()-1 because we don't need to count '-1' member
            if i == 14:
                weight[u] = (1 - wcw)/(len(uniq_all[i]))
            else:    
                weight[u] = (1 - wcw)/(len(uniq_all[i]))
        weight[-1] = wcw
        
        items = weight.keys()
        mysum = 0
        breakpoints = []
        for i in items:
            mysum += weight[i]
            breakpoints.append(mysum)

        #print weight
        an_individual.append(randomizor(breakpoints,items))

    return an_individual

def empty_chromosome():
    an_individual = []
    return an_individual

# Structure initializers
toolbox.register("attr_chromosomizor", chromosomizor)
toolbox.register("attr_empty_chromosome", empty_chromosome)
toolbox.register("individual", tools.initIterate,
                creator.Individual, toolbox.attr_chromosomizor)
toolbox.register("empty_individual", tools.initIterate,
                creator.Individual, toolbox.attr_empty_chromosome)

toolbox.register("population", tools.initRepeat,
                    list, toolbox.individual)

#END III -----------------------------------------------------------------

#-IV ------Evaluation Functions---------------------------
# imported evalFuncs.py

def evalSupCon(individual):
    Nconnect = float(len(auditData))
    matched_lines = 0.0
    wildcard = 0
    A = 0.0
    AnB = 0.0
    w1 = weightSupport #default 0.2
    w2 = weightConfidence #default 0.8
    for record in auditData:
        matched_fields = 0.0

        for index, field in enumerate(record, start=0):
            if (individual[index] == field) or (individual[index] == -1):
                matched_fields = matched_fields + 1.0
            if (individual[index] == -1):
                wildcard += 1
            if index == 13 and matched_fields == 14.0: 
                A += 1
            if index == 14 and matched_fields == 15.0:
                AnB += 1
                            #Wei Li's paper says that each field should have different
                            #Matching weight, I think it's true, this could be improved.
    #print 'A:', A,
    #print 'AnB:', AnB
    support = AnB / Nconnect
    if A > 0:
        confidence = AnB / A
    else:
        confidence = 0.0
    
    #print support
    #print confidence

    wildcard_deduct = wildcard * wildcardPenaltyWeight
    fitness = w1 * support + w2 * confidence

    if (wildcardPenalty == True) and (wildcard >= wildcard_allowance):
        if fitness > 0:
            fitness = fitness - wildcard_deduct

    if wildcard == 0 and fitness > 0:
        fitness = fitness - 0.001
    return fitness,
    #return [(fitness,), A, AnB]

#END IV -------------------------------------------------------

#-- V --- Selector (for elites) -------------------------------------
#Select 2 best individuals for each type of attack in generated old pop
#(So it select elites)
#len(uniq_attack) no. of attack types
#def selElites(pop):

attkUniqs = uniq_attack
#attkUniqs.remove('-')

def selElites(pop): #Selector function

    attkTypes = len(attkUniqs) # 4, Numbers of attacks in integer
    attkPop = []
    elitesSub = []
    elitesAll = []

    for i in xrange(attkTypes): #create lists within the attkPop list
        attkPop.append([]) #equals to the number of attkTypes

    for i in xrange(attkTypes):
        for j, k in enumerate(pop):
            if k[-1] == attkUniqs[i]: #if last field is the same attack
                attkPop[i].append(k) #type then add to the attkPop

    for i in attkPop:
        elitesSub.append(tools.selBest(i, elitesNo))


    for i in elitesSub: #appending all elites to elitesAll list
        i = list(i for i,_ in itertools.groupby(i)) #eliminate duplicate elites by attk type
        for j in i:
            elitesAll.append(j)

    #for i in elitesAll:
    #    i = list(i for i,_ in itertools.groupby(i))

    return elitesAll #This will be returned to create part of new
                     #population

###For main selector we uses deap default tools.selRandom

#END V ---------------------------------------------------------

#-- VI Crossover operator---------------------------------------
# Uses deap default tools.cxTwoPoints
#END VI---------------------------------------------------------

#-- VII Mutation operator---------------------------------------
unique_all_app = copy.deepcopy(uniq_all)
for i, field in enumerate(unique_all_app):
    if i != 14:
        field.append(-1)

def mutator(individaul):
    mutant = toolbox.empty_individual()
    for i, field in enumerate(individaul):
        unique_types = unique_all_app
        if random.random() < MUTPB:
            #print field, unique_types[i], "\n",
            #remove original value from pool
            #unique_types[i].remove(field)  
            field = random.choice(unique_types[i])
            #print field, unique_types[i],
        mutant.append(field)
    return mutant

def mutateWcardGene(individaul): #use to mutate wildcard genes of elites
    mutant = toolbox.clone(individaul)
    for i, field in enumerate(mutant):
        unique_types = uniq_all
        #print unique_types
        if (field == -1) and (random.random() < mutateElitesWildcards_PB):# and i != 3 and i != 4:
            mutant[i] = random.choice(unique_types[i])
            del mutant.fitness.values
            break
        del mutant.fitness.values
    return mutant

def mutateWcardGene_rand(individaul):
    mutant = toolbox.clone(individaul)
    wcard_field = [] # get the positions of the wildcard genes
    for i, field in enumerate(mutant):
        unique_types = uniq_all
        if (field == -1):
            wcard_field.append(i)
    #print wcard_field
    if random.random() < mutateElitesWildcards_PB and len(wcard_field) != 0:
        idx = random.choice(wcard_field)
        mutant[idx] = random.choice(unique_types[idx])
        del mutant.fitness.values
    #print mutant
    return mutant

def matchEliminate(ace, indi): 

    matched_fields = 0
    for index, field in enumerate(indi, start=0):
        if (ace[index] == field):
            matched_fields = matched_fields + 1

    return (matched_fields >= matchEliminate_AllowFields)

def aceComparison(elites):
    supremes = []

    for i in uniq_attack:
        space = []
        jail = []
        for j in elites:
            if j[-1] == i:
                space.append(j)
        global ace
        ace = tools.selBest(space, 1)
        ace = ace[0]

        if fitnessDiff_opt == True:
            for idx, ind in enumerate(space):
                if (((ace.fitness.values[0] - ind.fitness.values[0]) <= fitnessDiff_value) and (idx > 0)):
                    jail.append(ind)
            for ind in jail:
                space.remove(ind)

        if matchEliminate_opt == True:
            jail = []
            for idx, ind in enumerate(space):
                if matchEliminate(ace, ind) and ind != ace:
                    jail.append(ind)
            for ind in jail:
                space.remove(ind)

        for i in space:
            supremes.append(i)

    return supremes


#---------------------------------------------------------------

# Operator registering
toolbox.register("evaluate", evalSupCon) #Support-Confidence
toolbox.register("mate", tools.cxTwoPoints) #cxTwoPoints should work
toolbox.register("mutate", mutator)
toolbox.register("selectE", selElites) #this is not main selection
                                      #it is only elites selection

#toolbox.register("select", SOMENAME) #main selector needed
toolbox.register("select", tools.selRandom)

#del later
popza = toolbox.population(n=200)
indy = popza[0]

#---del later, this was simulated to gain understanding
# more of map(), zip()
#ass = selElites(popza)
fitneys = list(map(toolbox.evaluate, popza))
print fitneys[0]
print i
#for i, (k, j) in enumerate(zip(popza, (fitneys[i][0],))):
for k, j in zip(popza, fitneys):
    k.fitness.values = j