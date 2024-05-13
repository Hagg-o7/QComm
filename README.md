Quantum Key Distribution(QKD) using bb84 algorithm.
I have simulated bb84 quantum communication channels using Qiskit's Aer simulator models using low noise parameters for the Quantum Communication Channel.
After that the raw key generated is refined through information reconcilation through the cascade algorithm,
and then privacy amplification is done by taking parities of subsets of the raw key after information reconcilation.
