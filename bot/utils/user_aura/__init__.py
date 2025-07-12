import math
import random


def create_rand_aura_on_user_create() -> float:
    aura = random.uniform(100, 170)
    aura = round(aura, 2)
    return aura

def get_aura(all_reps, reps_finished) -> float:
    """returns aura (float) based on reps data"""
    # generate aura from reps
    aura = (((reps_finished * all_reps)) / (all_reps + 1 - reps_finished)) * random.uniform(5, 5.5)
    # floor number 1.3243 -> 1.32
    aura = round(aura, 2)
    return aura

def reduce_aura() -> float:
    """returns aura that should be redused"""

    aura = random.uniform(45, 55)
    aura = round(aura, 2)
    return aura