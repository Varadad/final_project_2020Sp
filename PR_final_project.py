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

