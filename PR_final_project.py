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

