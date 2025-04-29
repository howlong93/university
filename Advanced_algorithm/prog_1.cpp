#include <bits/stdc++.h>

using namespace std;

int main() {
	int pnt_amt, chord_amt;
	vector<pair<int, int>> chord;
	int coord1, coord2;
	
	cin >> pnt_amt;
	while (cin >> coord1 >> coord2) {
		pair<int, int> tmp;
		
		tmp.first = coord1, tmp.second = coord2;
		chord.push_back(tmp);
	}
    chord_amt = chord.size();
	
	sort (chord.begin(), chord.end(), [] (pair<int, int> &a, pair<int, int> &b) {
		return a.second < b.second;
	});
	
	vector<int> weight = vector<int> (chord_amt, 1);
	for (int i = 0; i < chord_amt; i++) {
		for (int j = i+1; j < chord_amt; j++) {
			if (chord[i].first > chord[j].first) {
				weight[j]++;
			}
		}
	}
	
//  cout << "start dp\n";
	vector<int> max_chords = vector<int> (chord_amt, 0);
	for (int i = 0; i < chord_amt; i++) {
		max_chords[i] = weight[i];
		for (int j = i-1; j >= 0; j--) {
			if (chord[i].first > chord[j].second) { //no overlap
				max_chords[i] = max (max_chords[i], max_chords[j] + weight[i]);
                break;
			}
		}
//      cerr << i << "th chord: " << max_chords[i] << '\n';
	}
	
//	for (auto k: chord) {
//		cout << k.first << ' ' << k.second << '\n';
//	}
	
	cout << max_chords[chord_amt-1] << '\n';
	
	return 0;
}
