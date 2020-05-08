
"""
IS 590 PR - Final Project

Monte Carlo Simulation on Hospital Capacity During COVID-19

Team members:
                        Varad Deshpande
                        Rohit Sanvaliya
                        Tanya Gupta
Note:
    The ranges of all randomised variables have been taken from real data from various
    sourses that are cited withing the code as well as in the README document of github
    repository of github's project repository

"""



from random import choice, randint, choices, seed, uniform, random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import pylab


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
        R = Result
        """
    # concept of transition between compartments - https://www.datahubbs.com/social-distancing-to-slow-the-coronavirus/

    def s_e(): # s = Suceptibility    ;   e= Exposed
        """
        Infectious Rate (Beta= = R1 * Gamma) based on the pert distribution
        :return: Infectious Rate
        """
        # infectious rate - https://www.inverse.com/mind-body/how-long-are-you-infectious-when-you-have-coronavirus
        infectious_rate = np.random.choice(1.0 / (ran_pert_dist(8, 10, 14, confidence=4, samples=1000))) # beta
        return infectious_rate

    def e_i(): # e= Exposed;    i = Infectious
        """
        Alpha           =   Incubation Rate = time in which infection is showing symptoms
        Arrival Rate =  Arrival Rate of patients at the hospitals
        Test Results  =  Time for test results to arrive
        :return: Incubation Rate, Arrival Rate, Probability of being COVID-19 positive, Test Results
        """
        #incubation rate - https: // www.inverse.com / mind - body / how - long - are - you - infectious - when - you - have - coronavirus, https://www.medscape.com/answers/2500114-197431/what-is-the-incubation-period-for-coronavirus-disease-2019-covid-19
        incubation_rate = np.random.choice(1.0 / ran_pert_dist(2, 5, 14, confidence=4, samples=1000)) # alpha
        #arrival rate - https://www.cdc.gov/coronavirus/2019-ncov/covid-data/covidview/05012020/covid-like-illness.html
        arrival_rate = np.random.choice(ran_pert_dist(1.70, 1.92, 4.46, confidence=4, samples=1000))
        #probability of people testing positive for COVID-19 - https://www.cdc.gov/coronavirus/2019-ncov/covid-data/covidview/index.html?CDC_AA_refVal=https%3A%2F%2Fwww.cdc.gov%2Fcoronavirus%2F2019-ncov%2Fcovid-data%2Fcovidview.html
        prob_positive = np.random.choice(ran_pert_dist(0.10, 0.18, 0.22, confidence=3, samples=1000))
        time_test_result = int(np.random.choice(ran_pert_dist(1, 2, 7, confidence=4, samples=1000)))
        return incubation_rate, arrival_rate, prob_positive, time_test_result

    def i_r(): # i= Infectious;    r = Result
        """
        Time to Outcome = Number of days patient will leave the hospital (Dead / Recovered)
        Outcome Rate      =  Rate at which people are leaving hospital bed (Dead / Recovered)
        :return: Time to Outcome, Outcome Rate
        """
        # time_to_outcome, outcome_rate - https://www.inverse.com/mind-body/how-long-are-you-infectious-when-you-have-coronavirus
        time_to_outcome = int(np.random.choice(ran_pert_dist(8, 10, 14, confidence=4, samples=1000)))
        outcome_rate = np.random.choice(1.0 / ran_pert_dist(8, 10, 14, confidence=4, samples=1000))  # gamma
        return time_to_outcome, outcome_rate


def admitted_bed(number_of_days, new_days, lst_outcome, lst_day_out, lst_hospitalized, number_of_beds):
    """
        beds_available = Number of available beds
        :param number_of_days:  Number days of the pendemic we want to test on
        :param new_days: this list contains the number of days after which the test result are coming out
        :param lst_outcome:list of number of patients with some outcome. Either recovered or dead
        :param lst_day_out:this is the list of number of days for each day in simulation, after which the outcome is recieved
        :param lst_hospitalized: This is the list of patients wo are hospitalized after being tested
        :param number_of_beds: This is the available number of hospital beds in the given city
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
        available_beds : This function gives the number of available beds after admitting the patients. It keeps on updating the
        number of available beds based on the admitted patients and  outcome patients.
        :param number_of_days: Number of days simulation has to run
        :param lst_outcome:  list of number of patients with some outcome. Either recovered or dead
        :param lst_day_out:  this is the list of number of days for each day in simulation, after which the outcome is recieved
        :param number_of_beds:  This is the available number of hospital beds in the given city
        :param admitted_beds: List of beds after admitting the patients
        :return:  available_beds: list of available beds for given day
        """
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

def test_result_days(lst_day, lst_time_to_outcome, number_of_days, new_days, lst_outcome, lst_day_out, lst_hospitalized, number_of_beds):
    """
        avail_beds =
        :param lst_day: list of nth days when test result are coming out
        :param lst_time_to_outcome: the nth day when outcome have come with respect to the admitted day
        :param number_of_days: number of days to test the simulation
        :param new_days: this is the list of number of days for each day in simulation, after which the test result are arriving
        :param lst_outcome: list of number of patients with some outcome. Either recovered or dead
        :param lst_day_out: this is the list of number of days for each day in simulation, after which the outcome is received
        :param lst_hospitalized: number of patients hospitalized
        :param number_of_beds: number of hospital beds available in simulation
        :return: avail_beds: list of available beds for given day
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

def model(number_of_days, population, total_beds):
    """
        bed_count =
        :param number_of_days: number of days simulation has to run for
        :param population: general population of the region
        :param total_beds: total number of hospital beds available in the region
        :return: bed_count: list of available beds
        """
    #concept of compartments - https://www.datahubbs.com/social-distancing-to-slow-the-coronavirus/
    number_of_beds = total_beds # beds in champaign
    total_population = population
    exposed = 1.0
    susceptible = total_population
    infected = 0.0
    day = 0


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


        hospitalized = int(infected*(17/100)) # people who require hospitalization: https://gis.cdc.gov/grasp/covidnet/COVID19_3.html ; https://en.as.com/en/2020/04/12/other_sports/1586725810_541498.html
        lst_hospitalized.append(hospitalized)



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
    prob_vacant_beds = []

    while i < number_of_simulation:

        beds = model(number_of_days, population, total_beds)

        if beds[-1] < 0:
            prob_vacant = 0
        else:
            prob_vacant = (beds[-1] / total_beds)

        print(prob_vacant)
        prob_vacant_beds.append(prob_vacant)
        for j in range(len(beds)):
            if beds[j] < 0:
                index = j
                count += 1
                break
        i += 1
    probability = count / number_of_simulation
    percent_vacant_bed = sum(prob_vacant_beds) / len(prob_vacant_beds)
    print('The Probability of vacant beds is:', probability)

if __name__ == '__main__':

    population = int(input("Enter the total population to be considered: "))
    total_beds = int(input("Enter the number of beds to be considered: "))
    simulations = int(input("Enter the number of simulations to be considered: "))
    number_of_days = int(input("Enter the number of days to be considered: "))

    simulation(number_of_days, simulations, population, total_beds)

    pylab.ylabel('Available Beds')
    pylab.xlabel('Number of Days')
    pylab.show()