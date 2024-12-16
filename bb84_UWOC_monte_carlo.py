from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
import math
import numpy as np
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, amplitude_damping_error, phase_damping_error
import random
import Alice, Bob
from binary_error_correction import binary_error_correction
import sys
import io
from tqdm import tqdm
import matplotlib.pyplot as plt

# Channel parameters
w1 = 0.5117
lambda_c1 = 0.1602
a_u1 = 1.4175
b_u1 = 2.9963
c_u1 = 0.8444
iter = 100
x_u = np.linspace(0.0001, 100, iter)  # Distance range
f_egg1 = (w1 / lambda_c1 * np.exp(-x_u / lambda_c1)) + ((1 - w1) * c_u1 * (x_u ** (a_u1 * c_u1 - 1)) /
              (b_u1 ** (a_u1 * c_u1)) * np.exp(-(x_u / b_u1) ** c_u1) / math.gamma(a_u1))

# Function to simulate underwater channel attenuation
def apply_attenuation(distance, attenuation_coeff):
    return np.exp(-attenuation_coeff * distance)

# Function to simulate EGG turbulence as a noise factor
def apply_turbulence(distance):
    # Here, f_egg1 is a function that gives turbulence effect based on distance
    turbulence_factor = np.interp(distance, x_u, f_egg1) 
    return turbulence_factor

ampDamp_param = 0.0001  # Amplitude damping parameter
phaseDamp_param = 0.0001  # Phase damping parameter

# Apply attenuation and turbulence for the communication channel
epochs = 50
attenuation_factor = np.zeros(epochs)
turbulence_factor = np.zeros(epochs)
distance = np.linspace(0, 100, epochs)
for i in range(len(distance)):
    attenuation_factor[i] = apply_attenuation(distance[i], lambda_c1)  # Apply attenuation
    turbulence_factor[i] = apply_turbulence(distance[i])  # Apply turbulence (EGG noise)

error_rate_raw = np.zeros(epochs)
error_rate = np.zeros(epochs)


for j in tqdm(range(epochs), desc="Simulating BB84 over UWOC", unit="epochs", file=sys.stdout):
    n = 2048  # Length of initial raw key
    Alice_bits, Alice_bases = Alice.Alice(n)
    Bob_bits, Bob_bases = Bob.Bob(n)

    old_stderr = sys.stderr
    sys.stderr = io.StringIO()

    try:
        for i in range(n):
            qr = QuantumRegister(1)
            cr = ClassicalRegister(1)
            qc = QuantumCircuit(qr, cr)  # Defining the quantum communication circuit

            # Alice (sender) qubit preparation stage
            if Alice_bits[i] == 1:
                qc.x(0)
            if Alice_bases[i] == 1:
                qc.h(0)

            # Modify the noise model based on channel effects
            noise_model = NoiseModel()
            ampDamp_error = amplitude_damping_error(ampDamp_param * attenuation_factor[j])
            phaseDamp_error = phase_damping_error(phaseDamp_param * turbulence_factor[j])
            noise_model.add_all_qubit_quantum_error(ampDamp_error, "id")
            noise_model.add_all_qubit_quantum_error(phaseDamp_error, "id")

            # Add a measurement operation to the circuit
            qc.measure(qr, cr)

            # Simulating the quantum communication circuit
            backend = AerSimulator(noise_model=noise_model)

            # Run the circuit directly
            result = backend.run(qc).result()

            # Ensure results contain counts
            counts = result.get_counts(qc)
            if counts:
                measured = int(list(counts.keys())[0], 2)  # Convert binary string to integer
                Bob_bits = np.append(Bob_bits, measured)

    finally:
        sys.stderr = old_stderr

    #Now, all the communication throughh the Quantum Communication Channel is complete, all communication will happen through a public authenticated channel now
    #Now Alice and bob will compare the bases they used to prepare/measure the qubits
    #And then they will delete the bits where they used different bases

    mismatched_bases = []
    for i in range(0, n):
        if Alice_bases[i] != Bob_bases[i]:
            mismatched_bases.append(i)

    Alice_bits = np.delete(Alice_bits, mismatched_bases)
    Bob_bits = np.delete(Bob_bits, mismatched_bases)

    #Error Rate Calculation
    n = min(len(Alice_bits), len(Bob_bits))
    Subset_length = len(Alice_bits)//4
    erroneus_bits = 0
    Subset_indices = np.array(random.sample(range(n), Subset_length))
    for i in Subset_indices:
        if Alice_bits[i] != Bob_bits[i]:
            erroneus_bits += 1
    Alice_bits = np.delete(Alice_bits, Subset_indices)
    Bob_bits = np.delete(Bob_bits, Subset_indices)
        
    error_rate_raw[j] = erroneus_bits / Subset_length

    #Information Reconciliation
    n = min(len(Alice_bits), len(Bob_bits))
    Block_length = 1/(error_rate_raw[j])
    number_Blocks = int(n // Block_length)
    Alice_blocks = np.array_split(Alice_bits, number_Blocks)
    Bob_blocks = np.array_split(Bob_bits, number_Blocks)

    for i in range(0, number_Blocks):
        parity_Alice = sum(Alice_blocks[i]) % 2
        parity_Bob = sum(Bob_blocks[i]) % 2

        if parity_Alice != parity_Bob:
            _, Bob_blocks[i] = binary_error_correction(Alice_blocks[i], Bob_blocks[i])
            Alice_blocks[i] = np.delete(Alice_blocks[i], len(Alice_blocks[i])-1)
            Bob_blocks[i] = np.delete(Bob_blocks[i], len(Bob_blocks[i])-1)

    Alice_bits = np.concatenate(Alice_blocks)
    Bob_bits = np.concatenate(Bob_blocks)

    #Privacy Amplification
    #Error Rate Calculation
    n = min(len(Alice_bits), len(Bob_bits))
    Subset_length = len(Alice_bits)//4
    erroneus_bits = 0
    Subset_indices = np.array(random.sample(range(n), Subset_length))
    for i in Subset_indices:
        if Alice_bits[i] != Bob_bits[i]:
            erroneus_bits += 1
    Alice_bits = np.delete(Alice_bits, Subset_indices)
    Bob_bits = np.delete(Bob_bits, Subset_indices)
        
    error_rate[j] = erroneus_bits / Subset_length

    n = min(len(Alice_bits), len(Bob_bits))
    k = error_rate[j]*n
    s = 2*n//5
    num_subsets = n - k - s
    sub_length = int(n//num_subsets)
    final_key_Alice = np.array([])
    final_key_Bob = np.array([])
    for i in range(0, s):
        n = min(len(Alice_bits), len(Bob_bits))
        sub_indices = np.array(random.sample(range(n), sub_length))
        parity_Alice = sum(Alice_bits[sub_indices]) % 2
        parity_Bob = sum(Bob_bits[sub_indices]) % 2
        Alice_bits = np.delete(Alice_bits, sub_indices)
        Bob_bits = np.delete(Bob_bits, sub_indices)
        final_key_Alice = np.append(final_key_Alice, parity_Alice)
        final_key_Bob = np.append(final_key_Bob, parity_Bob)

    erroneus_bits = 0
    for i in range(len(final_key_Alice)):
        if final_key_Alice[i] != final_key_Bob[i]:
            erroneus_bits += 1
    error_rate[j] = erroneus_bits/len(final_key_Alice)


plt.figure(1)
plt.scatter(distance, error_rate)  # Plot error rate
plt.xlabel("Distance (km)")
plt.ylabel("Error Rate")
plt.title("Error Rate After Information Reconcilation and Privacy Amplification vs Distance")

plt.figure(2)
plt.scatter(distance, error_rate_raw)  # Plot raw error rate
plt.xlabel("Distance (km)")
plt.ylabel("Raw Error Rate")
plt.title("Raw Error Rate vs Distance")

plt.figure(3)
plt.plot(distance, attenuation_factor)  # Plot attenuation factor
plt.xlabel("Distance (km)")
plt.ylabel("Attenuation Factor")
plt.title("Attenuation Factor vs Distance")

plt.figure(4)
plt.plot(distance, turbulence_factor)  # Plot turbulence factor
plt.xlabel("Distance (km)")
plt.ylabel("Turbulence Factor")
plt.title("Turbulence Factor vs Distance")

plt.show()

