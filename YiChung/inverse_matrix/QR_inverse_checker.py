import numpy as np

def qr_inverse_checker(A):
    # Ensure the input is a 4x4 matrix
    if A.shape != (4, 4):
        raise ValueError("The input matrix must be 4x4.")

    # Perform QR decomposition
    Q, R = np.linalg.qr(A)

    # Calculate the inverse of R
    R_inv = np.linalg.inv(R)

    # Calculate the inverse of A
    A_inv = np.dot(R_inv, Q.T)

    # Print the results
    print("Matrix Q:")
    print(Q)
    print("\nMatrix R:")
    print(R)
    print("\nInverse of R:")
    print(R_inv)
    print("\nInverse of A:")
    print(A_inv)

    return Q, R, R_inv, A_inv

# Example usage:
print("Please enter a 4x4 matrix (row by row, space-separated):")
A = []
for i in range(4):
    row = list(map(float, input(f"Row {i + 1}: ").split()))
    if len(row) != 4:
        raise ValueError("Each row must contain exactly 4 elements.")
    A.append(row)
A = np.array(A)

Q, R, R_inv, A_inv = qr_inverse_checker(A)
