import numpy as np
from sklearn.metrics import silhouette_score, adjusted_rand_score
import sys

import os ##

if __name__ == "__main__":
    """Usage: python eval.py {your predicted file path}"""
    file_name = sys.argv[1]

    cluster_label = np.load(file_name)
    true_label = np.load("label_test.npy")
    data = np.load("data.npy")

    silhouette_avg = silhouette_score(data, cluster_label)
    print(f'Silhouette Coefficient: {silhouette_avg:.3f}')

    # Final ARI score will calculated using whole 10000 data.
    test_num = true_label.size
    ari_score = adjusted_rand_score(true_label, cluster_label[:test_num])
    print(f'Adjusted Rand Index (ARI): {ari_score:.3f}')

    filename = "hw1_new_" + str(int(ari_score*1000))
    command_line = "cp -r ./ ../" + filename
    os.system(command_line)
