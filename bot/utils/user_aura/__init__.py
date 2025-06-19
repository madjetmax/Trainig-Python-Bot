import math
import random

def get_aura(all_reps, reps_finished):
    # generate aura from reps
    aura = (((reps_finished * all_reps)) / (all_reps + 1 - reps_finished)) * random.uniform(5, 5.5)
    # floor number 1.3243 -> 1.32
    aura = round(aura, 2)
    return aura
