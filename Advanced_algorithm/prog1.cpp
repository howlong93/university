#include <bits/stdc++.h>

using namespace std;

vector<int> adjacent_pnt;
vector<vector<int>> mem;

int dp (int start, int end) {
    if (end <= start) return 0;
    if (mem[start][end] != -1) return mem[start][end];

    if (adjacent_pnt[start] == end) {
        return mem[start][end] = dp(start+1, end-1) + 1;
    }

    int start_adj, end_adj;
    int cut_start = -1, cut_end = -1;
    start_adj = adjacent_pnt[start], end_adj = adjacent_pnt[end];
    if (start_adj > start && start_adj < end)
        cut_start = dp(start, start_adj) + dp(start_adj+1, end);
    if (end_adj < end && end_adj > start)
        cut_end = dp(start, end_adj-1) + dp(end_adj, end);

    mem[start][end] = max({cut_start, cut_end, dp(start+1, end-1)});
    
    return mem[start][end];
}

void output() {
    for (size_t i = 0; i < adjacent_pnt.size(); i++) {
        for (size_t j = 0; j < adjacent_pnt.size(); j++) {
            printf("%4d", mem[i][j]);
        }
        cout << '\n';
    }
}

int main() {
	int pnt_amt;
	int coord1, coord2;
	
	cin >> pnt_amt;
    adjacent_pnt = vector<int> (pnt_amt, -1);
    mem = vector<vector<int>> (pnt_amt, vector<int> (pnt_amt, -1));

	while (cin >> coord1 >> coord2) {
		adjacent_pnt[coord1] = coord2;
        adjacent_pnt[coord2] = coord1;
	}
	
    int ans = dp (0, pnt_amt-1);
    cout << ans << '\n';

//    output();

	return 0;
}
