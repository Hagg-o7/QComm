import qiskit
import numpy as np
from qiskit_aer import AerSimulator
import random

def Alice(n):
    Alice_bits = np.array([])
    Alice_bases = np.array([])
    for i in range(0,n):
        Alice_bits = np.append(Alice_bits, random.randint(0,1))
        Alice_bases = np.append(Alice_bases, random.randint(0,1))
    return Alice_bits, Alice_bases
