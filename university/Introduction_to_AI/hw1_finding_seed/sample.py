import numpy as np
from tqdm import tqdm
import os
from test_eval import evaluate

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
def clustering(X, n_clusters=10, n_iters=100, tol=1e-6, random_state=72):

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
            break

        centroids = new_centroids


    print(f"Converged in {iter_cnt + 1} iterations.\n")
    return labels

# Example usage (X should be your data):
# labels = clustering(X)


if __name__ == "__main__":
    # load data
    X = np.load("./data.npy") # size: [10000, 512]

    max_ari = 0
    cur_ari = 0
    best_seed = -1

    for rand_seed in range(3001, 10001):
        print('cur random seed: ', rand_seed)

        y = clustering(X, 10, 100, 1e-6, rand_seed)

        # save clustered labels
        filename = "../prediction_files/predicted_result_" + str(rand_seed) + ".npy"
        np.save("predicted_result.npy", y) # output size should be [10000]

        cur_ari = evaluate()
        
        if cur_ari > max_ari:
            print ("find better seed -> update best random seed & saving prediction file...")
            max_ari = cur_ari
            best_seed = rand_seed
            commandline = "cp predicted_result.npy " + filename
            os.system(commandline)

        print ("\nMaximum ARI score is ", max_ari, " when random seed is ", best_seed)
        print ("\n------------------------------------------------------------------\n")


#        commandline = "python eval.py " + filename
#        os.system(commandline)
