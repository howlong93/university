import numpy as np

# Define the target function
def target_function(x):
    return 1 - 1 / (2 * x)

# Define the ranges
# ranges = [(1, 1.125), (1.125, 1.25), (1.25, 1.5), (1.5, 1.75), (1.75, 2), (2, 2.5), (2.5, 3), (3, 4), (4, 5), (5, 6), (6, 8), (8, 10), (10, 12), (12, 16), (16, 20), (20, 32), (32, 48), (48, 64), (64, 128), (128, 256)]
ranges = [(48, 64), (64, 96), (96, 128), (128, 160), (160,256)]
coefficients = {}

max_errors = []
max_error_coords = []
tmp_max = 0.0
tmp_coord = 0.0
thresh = 1/(2**16)
print(f'clipping threshold: {thresh}')
# Compute the coefficients for each range
for start, end in ranges:
    x_values = np.linspace(start, end, 10000)  # Generate 100 points within the range
    y_values = target_function(x_values)    # Compute the target values
    coeff = np.polyfit(x_values, y_values, 1)  # Fit a 2nd-degree polynomial
    for i in range(coeff.size):
        if abs(coeff[i]) < thresh:
            coeff[i] = 0
    
    coefficients[(start, end)] = coeff
    
    tmp_max = 0.0
    for i in range(x_values.size):
        result_calc = coeff[0] * x_values[i] + coeff[1]
        # result_calc = coeff[0] * x_values[i] * x_values[i] + coeff[1] * x_values[i] + coeff[2]
        tmp_error = y_values[i] - result_calc

        if tmp_error < 0:
            tmp_error = -tmp_error

        if tmp_max < tmp_error:
            tmp_max = tmp_error
            tmp_coord = x_values[i]

    max_errors.append(tmp_max)
    max_error_coords.append(tmp_coord)

# Display the coefficients
for range_, coeff in coefficients.items():
    print(f"Range {range_}: Coefficients {coeff}")

for i in range(len(max_errors)):
    print(f"maximum_errors: {max_errors[i]} , at {max_error_coords[i]}")
