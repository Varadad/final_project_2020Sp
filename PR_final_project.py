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
        outcome_rate = np.random.choice(1.0 / ran_pert_dist(8, 10, 14, confidence=4, samples=1000000))  # gammad
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
    for i in range(number_of_days):
        X_num_days.append(i)
        for j in range(lst_day_out[i] + 1):
            if j == lst_day_out[i]:
                admitted_beds[i] = admitted_beds[i] + lst_outcome[i]
                available_beds.append(admitted_beds[i])
    Y_available_beds = available_beds
    print('available beds: ', available_beds)
    pylab.plot(X_num_days, Y_available_beds)
    return available_beds