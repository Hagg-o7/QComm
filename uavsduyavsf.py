from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
import numpy as np
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
import random
import Alice, Bob

AerSimulator.available_devices()

