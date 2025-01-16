import numpy as np

num_of_testcases = 500
cnt = 0

import numpy as np

N = 4  # Matrix size

# Print a matrix
def print_matrix(mat, name):
    print(f"{name} Matrix:")
    for row in mat:
        print(" ".join(f"{val:10.6f}" for val in row))
    print()

# Compute Givens rotation (cosine and sine)
def compute_givens(a, b):
    r = np.sqrt(a**2 + b**2)
    c = a / r
    s = -b / r
    return c, s

# Apply Givens rotation to a matrix
def apply_givens(mat, row1, row2, col, c, s):
    for j in range(col, N):
        temp1 = c * mat[row1][j] - s * mat[row2][j]
        temp2 = s * mat[row1][j] + c * mat[row2][j]
        mat[row1][j] = temp1
        mat[row2][j] = temp2

# QR decomposition using Givens rotations
def qr_decomposition(A):
    R = A.copy()
    Q = np.eye(N)

    for j in range(N - 1):  # Column
        for i in range(j + 1, N):  # Row
            c, s = compute_givens(R[j][j], R[i][j])
            apply_givens(R, j, i, j, c, s)  # Modify R
            for k in range(N):  # Modify Q
                temp1 = c * Q[k][j] - s * Q[k][i]
                temp2 = s * Q[k][j] + c * Q[k][i]
                Q[k][j] = temp1
                Q[k][i] = temp2
    return Q, R

# Compute the inverse of R
def invert_upper_triangular(R):
    invR = np.zeros_like(R)
    for i in range(N):
        invR[i][i] = 1.0 / R[i][i]
        for j in range(i - 1, -1, -1):
            sum_ = 0.0
            for k in range(j + 1, i + 1):
                sum_ += R[j][k] * invR[k][i]
            invR[j][i] = -sum_ / R[j][j]
    return invR

# Compute the inverse of A using Q and inv(R)
def compute_inverse(Q, R):
    invR = invert_upper_triangular(R)
    invA = np.dot(invR, Q.T)
    return invA, invR

def qr_inverse_checker(A):
    # Ensure the input is a 4x4 matrix
    if A.shape != (4, 4):
        raise ValueError("The input matrix must be 4x4.")

    # Perform QR decomposition
    Q, R = qr_decomposition(A)

    # Compute inverses
    A_inv, R_inv = compute_inverse(Q, R)

    # Print the results
    print("Matrix Q:")
    print(Q)
    print("\nMatrix R:")
    print(R)
    print("\nInverse of R:")
    print(R_inv)
    print("\nInverse of A:")
    print(A_inv)

    # Save the matrices to individual files
    with open(f'testcases/A_matrix.txt', 'a') as a_file:
        a_file.write(f'case {cnt}\n')
        for row in A:
            a_file.write(' '.join(f'{val:.12f}' for val in row) + '\n')
        a_file.write('\n')

    with open(f'testcases/Q_matrix.txt', 'a') as q_file:
        q_file.write(f'case {cnt}\n')
        for row in Q:
            q_file.write(' '.join(f'{val:.12f}' for val in row) + '\n')
        q_file.write('\n')

    with open(f'testcases/R_matrix.txt', 'a') as r_file:
        r_file.write(f'case {cnt}\n')
        for row in R:
            r_file.write(' '.join(f'{val:.12f}' for val in row) + '\n')
        r_file.write('\n')

    with open(f'testcases/R_inverse.txt', 'a') as r_inv_file:
        r_inv_file.write(f'case {cnt}\n')
        for row in R_inv:
            r_inv_file.write(' '.join(f'{val:.12f}' for val in row) + '\n')
        r_inv_file.write('\n')

    with open(f'testcases/A_inverse.txt', 'a') as a_inv_file:
        a_inv_file.write(f'case {cnt}\n')
        for row in A_inv:
            a_inv_file.write(' '.join(f'{val:.12f}' for val in row) + '\n')
        a_inv_file.write('\n')

    return Q, R, R_inv, A_inv

for cnt in range(num_of_testcases):
    # Generate a random 4x4 matrix with elements between -1 and 1
    A = np.random.uniform(-1, 1, (4, 4))

    # Print the matrix in decimal format
    print("\nRandomly generated matrix A (decimal format):")
    print(A)

    # Convert the matrix to Q3.12 binary fixed-point format
    # Q3.12 format: 1 sign bit, 3 integer bits, 12 fractional bits
    A_q3_12 = np.round(A * (2 ** 12)).astype(int)

    print("\nRandomly generated matrix A (Q3.12 binary fixed-point format, 2's complement):")
    with open('testcases/A_matrix_binary.txt', 'a') as file:
        for row in A_q3_12:
            formatted_row = []
            for val in row:
                # Scale and convert to Q3.12 format
                
                # Ensure the value is within the range of Q3.12 (-2^15 to 2^15 - 1)
                if val < -32768 or val > 32767:
                    raise ValueError(f"Value {orig_val} out of Q3.12 range!")
                
                # Convert to 16-bit two's complement
                if val < 0:
                    val = (1 << 15) + val  # Two's complement for negative numbers
                
                # Binary representation with underscore for Q3.12
                binary_repr = format(val, '015b')  # 16-bit binary
                formatted_val = binary_repr[:3] + '_' + binary_repr[3:]  # Add underscore between integer and fractional part
                formatted_row.append(formatted_val)
            
            # Write to file and print
            print(formatted_row)
            file.write(' '.join(formatted_row) + '\n')
        file.write('\n')
    print('\n')
    Q, R, R_inv, A_inv = qr_inverse_checker(A)
