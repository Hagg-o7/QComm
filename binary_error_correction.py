import numpy as np

def binary_error_correction(arr1, arr2):
    n = len(arr1)
    if n == 1:
        if arr1[0] != arr2[0]:
            arr2[0] = 1 - arr2[0]
        return arr1, arr2

    parity_arr1 = sum(arr1) % 2
    parity_arr2 = sum(arr2) % 2
    if parity_arr1 != parity_arr2:
        mid = n // 2
        arr11, arr12 = arr1[:mid], arr1[mid:]
        arr21, arr22 = arr2[:mid], arr2[mid:]
        _, arr21 = binary_error_correction(arr11, arr21)
        _, arr22 = binary_error_correction(arr12, arr22)
        arr2 = np.concatenate((arr21, arr22))

    return arr1, arr2

    