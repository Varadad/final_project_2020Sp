# 	Variables:
#   1) Arrival rate of people who want to get tested
#   2) Rate at which people are being exposed despite social distinsing (Infectious rate)
#   3) Probability of these  people actually having COVID-19 (getting tested positive)
#   4) Recovery time distribution of patients (depends on age)
#   5) Service time distribution of testing kits (Median - 2 days range(1-7days)) (Chi-Squared distrbution)
#   6) Rate at which testing kits are supplied
#   7) Incubation period of people getting contracted
#   8) Recovery Rate of patients

# 	Starting State:
#    1.	Number of beds in the hospital
#    2.	Number of testing kits available in the hospital
#    3.	Number of COVID-19 patients already being treated at the hospital

# 	Hypotheses:
#   •	Hypothesis 1: By doubling the number of beds for COVID-19 patients, the hospital will not overflow.
#   •	Hypothesis 2: By increasing the sanitization by 50%, we can reduce the number of people coming for testing getting infected by 30%

from random import choice, randint, choices, seed, uniform, random
import numpy as np
from numba import jit
from pandas import pd

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
    """
    This class contains all the variables which are resposible for the COVID-19 spread
    According to SEIR model:
    S = Suceptibility
    E= Exposed
    I = Infectious
    R = Recovered
    """

    def s_e():  # s = Suceptibility    ;   e= Exposed
        """
        Infectious Rate (Beta= = R1 * Gamma) based on the pert distribution
        :return: Infectious Rate
        """
        # infectious rate - https://www.inverse.com/mind-body/how-long-are-you-infectious-when-you-have-coronavirus
        infectious_rate = np.random.choice(1.0 / (ran_pert_dist(8, 10, 14, confidence=4, samples=1000000)))  # beta
        return infectious_rate

    def e_i():  # e= Exposed;    i = Infectious
        """
        Alpha           =   Incubation Rate = time in which infection is showing symptoms
        Arrival Rate =  Arrival Rate of patients at the hospitals
        Test Results  =  Time for test results to arrive
        :return: Incubation Rate, Arrival Rate, Probability of being COVID-19 positive, Test Results
        """
        # incubation rate - https: // www.inverse.com / mind - body / how - long - are - you - infectious - when - you - have - coronavirus, https://www.medscape.com/answers/2500114-197431/what-is-the-incubation-period-for-coronavirus-disease-2019-covid-19
        incubation_rate = np.random.choice(1.0 / ran_pert_dist(2, 5, 14, confidence=4, samples=1000000))  # alpha
        # arrival rate - https://www.cdc.gov/coronavirus/2019-ncov/covid-data/covidview/05012020/covid-like-illness.html
        arrival_rate = np.random.choice(ran_pert_dist(1.70, 1.92, 4.46, confidence=4, samples=1000000))
        # probability of people testing positive for COVID-19 - https://www.cdc.gov/coronavirus/2019-ncov/covid-data/covidview/index.html?CDC_AA_refVal=https%3A%2F%2Fwww.cdc.gov%2Fcoronavirus%2F2019-ncov%2Fcovid-data%2Fcovidview.html
        prob_positive = np.random.choice(ran_pert_dist(0.10, 0.18, 0.22, confidence=3, samples=1000000))
        # time for test results to arrive -
        time_test_result = int(np.random.choice(ran_pert_dist(1, 2, 7, confidence=4, samples=1000000)))
        return incubation_rate, arrival_rate, prob_positive, time_test_result

    def i_r():  # i= Infectious;    r = Recovered
        """
        Time to Outcome = Number of days patient will leave the hospital (Dead / Recovered)
        Outcome Rate      =  Rate at which people are leaving hospital bed (Dead / Recovered)
        :return: Time to Outcome, Outcome Rate
        """
        time_to_outcome = int(np.random.choice(ran_pert_dist(8, 10, 14, confidence=4, samples=1000000)))
        outcome_rate = np.random.choice(1.0 / ran_pert_dist(8, 10, 14, confidence=4, samples=1000000))  # gamma
        return time_to_outcome, outcome_rate

def admitted_bed(number_of_days, new_days, lst_outcome, lst_day_out, lst_hospitalized, number_of_beds):
    """
    beds_available = Number of available beds
    :param number_of_days:  Number days of the pendemic
    :param new_days:
    :param lst_outcome:
    :param lst_day_out:
    :param lst_hospitalized:
    :param number_of_beds:
    :return:  beds_available
    """
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
    """
    available_beds =
    :param number_of_days:
    :param lst_outcome:
    :param lst_day_out:
    :param number_of_beds:
    :param admitted_beds:
    :return:  available_beds
    """
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

def test_result_days(lst_day, lst_time_to_outcome, number_of_days, new_days, lst_outcome, lst_day_out,
                     lst_hospitalized, number_of_beds):
    """
    avail_beds =
    :param lst_day:
    :param lst_time_to_outcome:
    :param number_of_days:
    :param new_days:
    :param lst_outcome:
    :param lst_day_out:
    :param lst_hospitalized:
    :param number_of_beds:
    :return: avail_beds
    """
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

def model(number_of_days, population,
          total_beds):  # https://www.datahubbs.com/social-distancing-to-slow-the-coronavirus/
    """
    bed_count =
    :param number_of_days:
    :param population:
    :param total_beds:
    :return: bed_count
    """
    number_of_beds = total_beds  # beds in champaign
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
        susceptible = susceptible - int(Variables.s_e()) * infected * susceptible
        incub_rate, arr_rate, prob_pos, test_result_time = Variables.e_i()
        exposed = (Variables.s_e() * susceptible - incub_rate * exposed) * 0.005  # people getting exposed after social distancing #https://github.com/covid19-bh-biostats/seir/blob/master/SEIR/model_configs/basic

        day = day + test_result_time
        infected = arr_rate * prob_pos * exposed
        lst_infected.append(infected)
        # Y_available_beds = lst_infected

        hospitalized = int(infected * (17 / 100))  # people who requires hospitalization: https://gis.cdc.gov/grasp/covidnet/COVID19_3.html ; https://en.as.com/en/2020/04/12/other_sports/1586725810_541498.html
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
    """

    :param number_of_days:
    :param number_of_simulation:
    :param population:
    :param total_beds:
    :return:
    """
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
    probability = count / number_of_simulation

    print("The probability of hospitals overflowing: ", probability)
    population = int(input("Enter the total population to be considered: "))
    total_beds = int(input("Enter the number of beds to be considered: "))
    simulations = int(input("Enter the number of simulations to be considered: "))
    number_of_days = int(input("Enter the number of days to be considered: "))
    simulation(number_of_days, simulations, population, total_beds)

    pylab.ylabel('Available Beds')
    pylab.xlabel('Number of Days')
    pylab.show()