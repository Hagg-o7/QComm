from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
import numpy as np
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, amplitude_damping_error, phase_damping_error
import random
import Alice, Bob
from binary_error_correction import binary_error_correction


n=2048 #length of initial raw key
ampDamp_param = 0.05
phaseDamp_param = 0.05

Alice_bits, Alice_bases = Alice(n)
Bob_bits, Bob_bases = Bob(n)

initiate_QKD = 1

while initiate_QKD == 1:
    for i in range(0, n):
        qr = QuantumRegister(1)
        cr = ClassicalRegister(1)
        qc = QuantumCircuit(qr, cr) #Defining the quantum communication circuit

        #Alice(sender) qubit preparation stage
        if Alice_bits[i] == 1:
            qr.x(0)
        if Alice_bases[i] == 1:
            qc.h(0)

        qc.id(0) #Noisy Quantum Communication Channel

        #Bob(reciever) qubit measurement stage
        if Bob_bases == 1:
            qc.h(0)
        qc.measure(0, 0)

        #Quantum Communication Channel Noise Model
        noise_model = NoiseModel()
        ampDamp_error = amplitude_damping_error(ampDamp_param)
        phaseDamp_error = phase_damping_error(phaseDamp_param)
        noise_model.add_all_qubit_quantum_error(ampDamp_error, "id")
        noise_model.add_all_qubit_quantum_error(phaseDamp_error, "id")

        #Simulating the quantum communication circuit
        backend = AerSimulator(noise_model=noise_model)
        RunCircuit = transpile(qc, backend)

        result = backend.run(qc).result()

        #Appending the measured qubit to Bob's bits
        measured = int(list(result.get_counts(qc).keys())[0])
        Bob_bits.append(measured)

    #Now, all the communication throughh the Quantum Communication Channel is complete, all communication will happen through a public authenticated channel now
    #Now Alice and bob will compare the bases they used to prepare/measure the qubits
    #And then they will delete the bits where they used different bases

    for i in range(0, n):
        if Alice_bases[i] != Bob_bases[i]:
            Alice_bits = np.delete(Alice_bits, i)
            Bob_bits = np.delete(Bob_bits, i)

    rawKey_length = len(Alice_bits)

    #Error Rate Calculation
    Subset_length = len(Alice_bits)//4
    erroneus_bits = 0
    Subset_indices = np.array(random.sample(range(rawKey_length+1), Subset_length))
    for i in Subset_indices:
        if Alice_bits[i] != Bob_bits[i]:
            erroneus_bits += 1
        Alice_bits = np.delete(Alice_bits, i)
        Bob_bits = np.delete(Bob_bits, i)
        
    error_rate = erroneus_bits / Subset_length



    print("Error Rate: ", error_rate)
    if error_rate < 0.11:
        print("The Quantum Key Distribution was successful")
        initiate_QKD = 0
    else:
        print("The Quantum Key Distribution was unsuccessful")

#Now, Alice and bob will perform Information Reconciliation and Privacy Amplification

#Information Reconciliation

Block_length = 1/(error_rate)
number_Blocks = rawKey_length // Block_length
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
Subset_length = len(Alice_bits)//4
erroneus_bits = 0
Subset_indices = np.array(random.sample(range(rawKey_length+1), Subset_length))
for i in Subset_indices:
    if Alice_bits[i] != Bob_bits[i]:
        erroneus_bits += 1
    Alice_bits = np.delete(Alice_bits, i)
    Bob_bits = np.delete(Bob_bits, i)
    
error_rate = erroneus_bits / Subset_length

k = error_rate*len(Alice_bits)
s = 2*len(Alice_bits)//5
num_subsets = len(Alice_bits) - k - s
sub_length = len(Alice_bits)//num_subsets
final_key_Alice = np.array()
final_key_Bob = np.array()
for i in range(0, s):
    sub_indices = np.array(random.sample(range(len(Alice_bits)+1), sub_length))
    parity_Alice = sum(Alice_bits[sub_indices]) % 2
    parity_Bob = sum(Bob_bits[sub_indices]) % 2
    Alice_bits = np.delete(Alice_bits, sub_indices)
    Bob_bits = np.delete(Bob_bits, sub_indices)
    final_key_Alice = np.append(final_key_Alice, parity_Alice)
    final_key_Bob = np.append(final_key_Bob, parity_Bob)

final_key_Alice = final_key_Alice[0: 128]
final_key_Bob = final_key_Bob[0: 128]

#Quantum Key Distribution is complete
print("Quantum Key Distribution is complete")    
print("Final Key Length: ", len(final_key_Alice))
print("Final Key Alice: ", final_key_Alice)
print("Final Key Bob: ", final_key_Bob)

