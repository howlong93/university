#include <bits/stdc++.h>

using namespace std;

int main() {
	srand(time(NULL));
	
	vector<vector<int>> num = vector<vector<int>> (100, vector<int> (6, 0));
	vector<int> used(1500, 0);
	
	for (int i = 0; i < 100; i++) {
		int tmp = 0;
		do {
			tmp = rand() % 1500;
		} while (used[tmp] != 0);
		
		used[tmp] = 1;
		num[i][0] = tmp;
		
		for (int j = 1; j <= 5; j++) {
			num[i][j] = rand() % 256;
		}
	}
	
	sort (num.begin(), num.end(), [] (vector<int> &a, vector<int> &b) {
		return a[0] < b[0];
	});
	
	cout << "[\n";
	for (int i = 0; i < 100; i++) {
		cout << "\t{\"time\": " << num[i][0] << ", \"head\": " << num[i][1] << ", \"chest\": " << num[i][2]
			 << ", \"waist\": " << num[i][3] << ", \"arm\": " << num[i][4] << ", \"leg\": " << num[i][5] << "}";
		
		if (i != 99) cout << ',';
		cout << '\n';
	}
	cout << "]\n";
}
