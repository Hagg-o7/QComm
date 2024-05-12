import qiskit
import numpy as np
from qiskit_aer import AerSimulator
import random

def Bob(n):
    Bob_bases = np.array()
    for i in range(0,n):
        Bob_bases = np.append(random.randint(0,1))
    Bob_bits = np.array()
    return Bob_bits, Bob_bases
