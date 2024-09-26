import numpy as np

def kmeans_plusplus_initialization(X, n_clusters, random_state=None):

    if random_state is not None:
        np.random.seed(random_state)

    n_samples = X.shape[0]
    centroids = []

    # Choose the first centroid randomly
    first_centroid = X[np.random.randint(n_samples)]
    centroids.append(first_centroid)

    # Choose each next centroid
    for _ in range(1, n_clusters):
        # Compute distances from the nearest centroid for each point
        distances = np.min([np.linalg.norm(X - centroid, axis=1)**2 for centroid in centroids], axis=0)
        probabilities = distances / distances.sum()
        cumulative_probabilities = probabilities.cumsum()
        random_val = np.random.rand()
        next_centroid_idx = np.where(cumulative_probabilities >= random_val)[0][0]
        centroids.append(X[next_centroid_idx])

    return np.array(centroids)

def calculate_divergence(X, labels, centroids):

    # Calculate the distance of each point to its assigned centroid
    distances = np.linalg.norm(X - centroids[labels], axis=1)
    
    # Calculate the variance (mean squared distance)
    divergence = np.mean(distances ** 2)
    
    return divergence

# Example usage in clustering function
def clustering(X, n_clusters=10, n_iters=100, tol=1e-6, random_state=330):

    # Improved initialization with k-means++
    centroids = kmeans_plusplus_initialization(X, n_clusters, random_state=random_state)

    for iter_cnt in range(n_iters):
        # Step 1: Assign each data point to the nearest centroid
        distances = np.linalg.norm(X[:, np.newaxis] - centroids, axis=2)
        labels = np.argmin(distances, axis=1)

        # Check if any cluster is empty and reinitialize
        for cluster_idx in range(n_clusters):
            if len(X[labels == cluster_idx]) == 0:
                # Reinitialize the centroid for the empty cluster
                centroids[cluster_idx] = X[np.random.choice(X.shape[0])]

        # Step 2: Compute new centroids as the mean of assigned points
        new_centroids = np.array([X[labels == i].mean(axis=0) if len(X[labels == i]) > 0 else centroids[i] for i in range(n_clusters)])

        # Step 3: Calculate divergence (variance of distances)
        divergence = calculate_divergence(X, labels, centroids)
#       print(f"Iter {iter_cnt + 1}\tDivergence: {divergence:.4f}")

        # Step 4: Check for convergence (if centroids do not change much)
        if np.all(np.linalg.norm(new_centroids - centroids, axis=1) < tol):
            print(f"Converged in {iter_cnt + 1} iterations.")
            break

        centroids = new_centroids

    return labels

# Example usage (X should be your data):
# labels = clustering(X)


if __name__ == "__main__":
    # load data
    X = np.load("./data.npy") # size: [10000, 512]

    y = clustering(X)

    # save clustered labels
    np.save("predicted_result.npy", y) # output size should be [10000]
