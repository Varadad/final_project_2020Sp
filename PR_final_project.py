# 1) Arrival rate of people who want to get tested
# 2) Rate at which people are being exposed despite social distinsing (Infectious rate)
# 3) Probability of these  people actually having COVID-19 (getting tested positive)
# 4) Recovery time distribution of patients (depends on age)
# 5) Service time distribution of testing kits (Median - 2 days range(1-7days)) (Chi-Squared distrbution)
# 6) Rate at which testing kits are supplied
# 7) Incubation period of people getting contracted
# 8) Recovery Rate of patients



from random import choice, randint, choices, seed, uniform, random
import numpy as np
from numba import jit

import matplotlib.pyplot as plt
from matplotlib import pylab
import time


def ran_pert_dist(minimum, most_likely, maximum, confidence, samples):
    """Produce random numbers according to the 'Modified PERT' distribution.

        :param minimum: The lowest value expected as possible.
        :param most_likely: The 'most likely' value, statistically, the mode.
        :param maximum: The highest value expected as possible.
        :param confidence: This is typically called 'lambda' in literature
                            about the Modified PERT distribution. The value
                            4 here matches the standard PERT curve. Higher
                            values indicate higher confidence in the mode.
                            Currently allows values 1-18
        :param samples: number of samples to create the distribution

        Formulas to convert beta to PERT are adapted from a whitepaper
        "Modified Pert Simulation" by Paulo Buchsbaum.
        """
    # Check for reasonable confidence levels to allow:
    if confidence < 1 or confidence > 18:
        raise ValueError('confidence value must be in range 1-18.')

    mean = (minimum + confidence * most_likely + maximum) / (confidence + 2)

    a = (mean - minimum) / (maximum - minimum) * (confidence + 2)
    b = ((confidence + 1) * maximum - minimum - confidence * most_likely) / (maximum - minimum)

    beta = np.random.beta(a, b, samples)
    beta = beta * (maximum - minimum) + minimum
    return beta

class Variables():

    def s_e():
        #
        infectious_rate = np.random.choice(1.0 / (ran_pert_dist(8, 10, 14, confidence=4, samples=1000000))) # beta
        return infectious_rate

    def e_i():
        incubation_rate = np.random.choice(1.0 / ran_pert_dist(2, 5, 14, confidence=4, samples=1000000)) # alpha
        arrival_rate = np.random.choice(ran_pert_dist(1.70, 1.92, 4.46, confidence=4, samples=1000000))
        prob_positive = np.random.choice(ran_pert_dist(0.10, 0.18, 0.22, confidence=3, samples=1000000))
        time_test_result = int(np.random.choice(ran_pert_dist(1, 2, 7, confidence=4, samples=1000000)))
        return incubation_rate, arrival_rate, prob_positive, time_test_result

    def i_r():
        time_to_outcome = int(np.random.choice(ran_pert_dist(8, 10, 14, confidence=4, samples=1000000)))
        outcome_rate = np.random.choice(1.0 / ran_pert_dist(8, 10, 14, confidence=4, samples=1000000))  # gamma
        return time_to_outcome, outcome_rate


def admitted_bed(number_of_days, new_days, lst_outcome, lst_day_out, lst_hospitalized, number_of_beds):
    admitted_beds = []
    for i in range(number_of_days):
        for j in range(new_days[i] + 1):
            if j == new_days[i]:
                number_of_beds = number_of_beds - lst_hospitalized[i]
                admitted_beds.append(number_of_beds)
    beds_available = available_bed(number_of_days, lst_outcome, lst_day_out, number_of_beds, admitted_beds)
    return beds_available

    # print("Admitted beds: ", admitted_beds)

def available_bed(number_of_days, lst_outcome, lst_day_out, number_of_beds, admitted_beds):
    X_num_days = []
    Y_available_beds = []
    available_beds = []
    simulation_df = pd.DataFrame()
    for i in range(number_of_days):
        X_num_days.append(i)
        # simulation_df['x'] = X_num_days
        for j in range(lst_day_out[i] + 1):
            if j == lst_day_out[i]:
                admitted_beds[i] = admitted_beds[i] + lst_outcome[i]
                available_beds.append(admitted_beds[i])
    Y_available_beds = available_beds
    # simulation_df['y'] = available_beds
    print('available beds: ', available_beds)
    pylab.plot(X_num_days, Y_available_beds)
    return available_beds

def test_result_days(lst_day, lst_time_to_outcome, number_of_days, new_days, lst_outcome, lst_day_out, lst_hospitalized, number_of_beds):
    new_days = []
    lst_day_out = []
    for k in range(len(lst_day)):
        day = k
        day = day + lst_day[k]
        day_out = day + lst_time_to_outcome[k]
        new_days.append(day)
        lst_day_out.append(day_out)
    avail_beds = admitted_bed(number_of_days, new_days, lst_outcome, lst_day_out, lst_hospitalized, number_of_beds)
    return avail_beds

def model(number_of_days, population, total_beds): #https://www.datahubbs.com/social-distancing-to-slow-the-coronavirus/
    number_of_beds = total_beds # beds in champaign
    total_population = population
    exposed = 1.0
    susceptible = total_population
    infected = 0.0
    day = 0
    hospitalized = 0

    lst_infected = []
    lst_outcome = []
    lst_time_to_outcome = []
    lst_day = []
    lst_day_out = []
    new_days = []
    lst_hospitalized = []

    for i in range(number_of_days):

        susceptible = susceptible - int(Variables.s_e())*infected*susceptible

        incub_rate, arr_rate, prob_pos, test_result_time = Variables.e_i()

        exposed = (Variables.s_e() * susceptible - incub_rate * exposed)*0.005 #people getting exposed after social distancing #https://github.com/covid19-bh-biostats/seir/blob/master/SEIR/model_configs/basic

        day = day + test_result_time

        infected = arr_rate * prob_pos * exposed

        lst_infected.append(infected)
        # Y_available_beds = lst_infected

        hospitalized = int(infected*(17/100)) # people who requires hospitalization: https://gis.cdc.gov/grasp/covidnet/COVID19_3.html ; https://en.as.com/en/2020/04/12/other_sports/1586725810_541498.html
        lst_hospitalized.append(hospitalized)
        # Y_available_beds = lst_hospitalized


        outcome_time, rate_outcome = Variables.i_r()

        outcome = rate_outcome * hospitalized

        lst_outcome.append(outcome)

        lst_day.append(test_result_time)
        lst_time_to_outcome.append(outcome_time)
    bed_count = test_result_days(lst_day, lst_time_to_outcome, number_of_days, new_days, lst_outcome, lst_day_out, lst_hospitalized, number_of_beds)
    return bed_count

def simulation(number_of_days, number_of_simulation, population, total_beds):
    i = 0
    count = 0
    beds = []
    while i < number_of_simulation:
        beds = model(number_of_days, population, total_beds)
        for j in range(len(beds)):
            if beds[j] < 0:
                index = j
                count += 1
                break
        i += 1
    probability = count/number_of_simulation
    print("The probability of hospitals overflowing: ", probability)