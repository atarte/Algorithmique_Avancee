import tsp_ant as tsp_ant

from pulp import *
from copy import *
import numpy as np
import progressbar as pb

def Convert_to_complete(matrix, city_to_pass):
    new_matrix = deepcopy(matrix)
    new_matrix = list(new_matrix)
    for i in range(len(matrix)-1, -1, -1):
        new_matrix[i] = list(new_matrix[i])

    for i in range(len(matrix)-1, -1, -1):
        if i not in city_to_pass:
            new_matrix.pop(i)
            for j in range(len(new_matrix)):
                new_matrix[j].pop(i)
    
    return new_matrix


def Borne(nb_vertex, tsp_matrix):
    StateMat = {}
    OrderList = {}
    for i in range(nb_vertex):
        for j in range(nb_vertex):  # create a binary variable
            StateMat[i, j] = LpVariable('x{},{}'.format(
                i, j), lowBound=0, upBound=1, cat=const.LpBinary)

    for i in range(nb_vertex):  # create a binary variable
        OrderList[i] = LpVariable('u{}'.format(
            i), lowBound=1, upBound=nb_vertex, cat=const.LpInteger)

    # probleme
    prob = LpProblem("Shortest_Delivery", LpMinimize)

    # fonction objective
    cost = lpSum([[tsp_matrix[n][m]*StateMat[n, m]
                 for m in range(nb_vertex)] for n in range(nb_vertex)])
    prob += cost

    # contrainte
    for n in range(nb_vertex):
        prob += lpSum([StateMat[n, m] for m in range(nb_vertex)]
                      ) == 1, "All entered constraint "+str(n)
        prob += lpSum([StateMat[m, n] for m in range(nb_vertex)]
                      ) == 1, "All exited constraint "+str(n)

    for i in range(nb_vertex):
        for j in range(nb_vertex):
            if i != j and (i != 0 and j != 0):
                prob += OrderList[i] - OrderList[j] <= nb_vertex * \
                    (1 - StateMat[i, j]) - 1

    cont2 = lpSum([StateMat[m, m]
                  for m in range(nb_vertex)]) == 0, "No loop constraint"
    prob += cont2

    prob.solve(PULP_CBC_CMD(msg=0, timeLimit=300))
    return prob.objective.value() if (LpStatus[prob.status] == "Optimal") else None


def Limit_Ant(graph, cities_to_pass, nb_test):
    '''
    ok
    '''
    widgets = [' ['
               , pb.Timer(),
            '] ',
            pb.Bar('*'),' (',
            pb.ETA(), ') ',
            ]
    
    nb_steps_bar = nb_test

    VarIteration = range(2, 100, 10)
    nb_steps_bar *= len(VarIteration)

    VarAnt = range(2, 100, 10)
    nb_steps_bar *= len(VarAnt)

    VarAlpha = range(5, 50, 10)
    nb_steps_bar *= len(VarAlpha)

    VarBeta = range(50, 5, -10)
    nb_steps_bar *= len(VarBeta)

    VarEvap = range(25, 55, 10)
    nb_steps_bar *= len(VarEvap)

    VarPheromone = range(90, 120, 10)
    nb_steps_bar *= len(VarPheromone)

    print(nb_steps_bar)

    Textbar = pb.ProgressBar(maxval=nb_steps_bar, widgets=widgets)
    Textbar.start()

    value = 0

    complete_matrix = Convert_to_complete(graph, cities_to_pass)
    limit = Borne(len(complete_matrix), complete_matrix)

    list_average = []

    for iteration in VarIteration:
        for ant in VarAnt:
            for alpha in VarAlpha:
                for beta in VarBeta:
                    for evaporation_factor in VarEvap:
                        for pheromone_spread in VarPheromone:
                            current_values = []

                            for _ in range(nb_test):
                                _, path_lenght = tsp_ant.Ant_Tsp(graph, cities_to_pass, nb_iteration=iteration, nb_ant=ant, alpha=alpha/10, 
                                            beta=beta/10, evaporation_factor=evaporation_factor/100, pheromone_spread=pheromone_spread/100)
                                
                                current_values.append((path_lenght / limit) * 100)
                                value += 1
                                Textbar.update(value)
                                
                            list_average.append(np.mean(current_values))

    Textbar.finish()
    
    total_average = np.mean(list_average)
    total_derivation = np.nanstd(list_average)


    print(total_average + total_derivation)
    print(total_average)
    print(total_average - total_derivation)


def Optimal_parameters(graph, cities_to_pass, nb_test):
    widgets = [' [', pb.Timer(),
               '] ',
               pb.Bar('*'), ' (',
               pb.ETA(), ') ',
               ]

    nb_steps_bar = nb_test

    VarIteration = range(5, 100, 10)
    nb_steps_bar *= len(VarIteration)

    VarAnt = range(10, 100, 10)
    nb_steps_bar *= len(VarAnt)

    VarAlpha = range(5, 50, 10)
    nb_steps_bar *= len(VarAlpha)

    VarBeta = range(50, 5, -10)
    nb_steps_bar *= len(VarBeta)

    VarEvap = range(25, 55, 10)
    nb_steps_bar *= len(VarEvap)

    VarPheromone = range(90, 120, 10)
    nb_steps_bar *= len(VarPheromone)

    print(nb_steps_bar)

    Textbar = pb.ProgressBar(maxval=nb_steps_bar, widgets=widgets)
    Textbar.start()

    value = 0

    complete_matrix = Convert_to_complete(graph, cities_to_pass)
    limit = Borne(len(complete_matrix), complete_matrix)

    list_average = []
    list_compo = []

    limit_attempt = False
    limit_acceptation = 104

    for alpha in VarAlpha:
        for beta in VarBeta:
            for evaporation_factor in VarEvap:
                for pheromone_spread in VarPheromone:
                    for iteration in VarIteration:
                        for ant in VarAnt:
                            current_values = []

                            for _ in range(nb_test):
                                if not limit_attempt :
                                    _, path_lenght = tsp_ant.Ant_Tsp(graph, cities_to_pass, nb_iteration=iteration, nb_ant=ant, alpha=alpha/10,
                                                                    beta=beta/10, evaporation_factor=evaporation_factor/100, pheromone_spread=pheromone_spread/100)

                                    current_values.append(
                                        (path_lenght / limit) * 100)

                                value += 1
                                Textbar.update(value)

                            if not limit_attempt: 
                                value_calculate = np.mean(current_values)
                                list_average.append(value_calculate)
                                list_compo.append((alpha, beta, evaporation_factor, pheromone_spread, iteration, ant))

                                print(value_calculate)
                                print("iteration : ", iteration, " ant : ", ant, " alpha : ", alpha/10, " beta : ", beta/10, " evap : ", evaporation_factor/100, " pheromone : ", pheromone_spread/100)
                                if value_calculate <= limit_acceptation:
                                    limit_attempt = True

    Textbar.finish()

def Test(graph, cities_to_pass, nb_test):
    '''
    ok
    '''
    widgets = [' [', pb.Timer(),
                '] ',
                pb.Bar('*'), ' (',
                pb.ETA(), ') ',
                ]

    nb_steps_bar = nb_test

    VarIteration = 50

    VarAnt = 100

    VarAlpha = 5

    VarBeta = 50

    VarEvap = 25

    VarPheromone = 90

    Textbar = pb.ProgressBar(maxval=nb_steps_bar, widgets=widgets)
    Textbar.start()

    value = 0

    current_values = []

    for _ in range(nb_test):
        _, path_lenght = tsp_ant.Ant_Tsp(graph, cities_to_pass, nb_iteration=VarIteration, nb_ant=VarAnt, alpha=VarAlpha/10,
                                            beta=VarBeta/10, evaporation_factor=VarEvap/100, pheromone_spread=VarPheromone/100)

        current_values.append(
            (path_lenght / 1019) * 100)
        value += 1
        Textbar.update(value)

    Textbar.finish()

    total_average = np.mean(current_values)
    total_derivation = np.nanstd(current_values)

    print(total_average + total_derivation)
    print(total_average)
    print(total_average - total_derivation)
