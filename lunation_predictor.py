import juliandate as jd
import numpy as np
import re


def analyze(fname='data/babylonian_chronology_pd_1971.dat', center=0):
    with open(fname, 'r') as file:
        data = file.readlines()

    data = [tuple(map(int, re.findall('-?\d+', d)[2:5])) for d in data]
    data = [int(round(jd.from_julian(*d) + .5)) for d in data]

    month = np.arange(-center, len(data) - center)
    X = np.column_stack((month, np.ones_like(data)))
    k, b = np.linalg.lstsq(X, data, rcond=None)[0]
    return lambda x: int(round(k * x + b))


if __name__ == '__main__':
    analyze()
