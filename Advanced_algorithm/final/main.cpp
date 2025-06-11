#include <bits/stdc++.h>

using namespace std;

#define OBSTACLE    -1
#define SPARE       0

class Connection {
  public:
    int idx;
    bool connected;
    int init_x, init_y;
    int term_x, term_y;

    int dist_sqr;
    int lnth, bend;
    vector<pair<int, int>> path;
    int shortest_route_length;

    Connection () {
        idx = 0;
        connected = 0;
        init_x = init_y = term_x = term_y = 0;
        dist_sqr = 0;
        lnth = bend = 0;
        shortest_route_length = 0;
    }

    Connection (int _idx, int _init_x, int _init_y, int _term_x, int _term_y) {
        idx = _idx;
        connected = 0;
        init_x = _init_x;
        init_y = _init_y;
        term_x = _term_x;
        term_y = _term_y;
        dist_sqr = (term_y-init_y)*(term_y-init_y) + (term_x-init_x)*(term_x-init_x);
        lnth = bend = 0;
        shortest_route_length = 0;
    }

    bool operator< (const Connection &a) {
        // return dist_sqr < a.dist_sqr;
        return shortest_route_length < a.shortest_route_length;
    }
};

void print_grid (const vector<vector<int>> &grid, const int cur_idx) {
    cout << '\n';

    cout << "| ";
    for (size_t j = 1; j < grid[0].size(); j++) cout << j%10 << ' ';
    cout << "| \n";

    for (int i = grid.size()-1; i >= 1; i--) {
        cout << i%10 << " ";
        for (size_t j = 1; j < grid[0].size(); j++) {
            if (grid[i][j] == -1) cout << '#';
            else if (grid[i][j] == cur_idx) cout << 'o';
            else if (grid[i][j] > 0) cout << '*';
            else cout << ' ';
            cout << ' ';
        }
        cout << i%10 << " \n";
    }

    cout << "| ";
    for (size_t j = 1; j < grid[0].size(); j++) cout << j%10 << ' ';
    cout << "| \n";

    cout << '\n' << string(50, '=') << '\n';
    return;
}

void BFS(Connection &c, const vector<vector<int>> &grid) {
    int h = grid.size();
    int w = grid[0].size();

    const vector<pair<int, int>> dirs = {{-1, 0}, {1, 0}, {0, -1}, {0, 1}}; // up, down, left, right

    struct State {
        int x, y, dir, dist, bends;
        vector<pair<int, int>> path;
    };

    vector<vector<vector<int>>> visited(h, vector<vector<int>>(w, vector<int>(4, INT_MAX)));
    queue<State> q;

    // Try starting in all directions
    for (int d = 0; d < 4; ++d) {
        int nx = c.init_x + dirs[d].first;
        int ny = c.init_y + dirs[d].second;
        if (nx >= 1 && nx < w && ny >= 1 && ny < h && grid[ny][nx] == SPARE) {
            q.push({nx, ny, d, 1, 0, {{c.init_x, c.init_y}, {nx, ny}}});
            visited[ny][nx][d] = 0;
        }
    }

    int shortest = INT_MAX;
    int min_bends = INT_MAX;
    vector<pair<int, int>> best_path;

    while (!q.empty()) {
        State cur = q.front();
        q.pop();

        if (cur.x == c.term_x && cur.y == c.term_y) {
            if (cur.dist < shortest || (cur.dist == shortest && cur.bends < min_bends)) {
                shortest = cur.dist;
                min_bends = cur.bends;
                best_path = cur.path;
            }
            continue;
        }

        for (int d = 0; d < 4; ++d) {
            int nx = cur.x + dirs[d].first;
            int ny = cur.y + dirs[d].second;

            if (nx < 1 || nx >= w || ny < 1 || ny >= h || grid[ny][nx] != SPARE)
                continue;

            int new_bends = cur.bends + (d != cur.dir);
            if (new_bends < visited[ny][nx][d]) {
                visited[ny][nx][d] = new_bends;
                vector<pair<int, int>> new_path = cur.path;
                new_path.emplace_back(nx, ny);
                q.push({nx, ny, d, cur.dist + 1, new_bends, new_path});
            }
        }
    }

    if (shortest < INT_MAX) {
        c.connected = true;
        c.lnth = shortest;
        c.bend = min_bends;
        c.path = best_path;
    } else {
        c.connected = false;
    }
}

int main() {
    int h, w;

    int in_amt;
    string tmp_string;

    vector<vector<int>> grid;
    vector<Connection> connects;

    //input stage
    cin >> w >> h;
    grid = vector<vector<int>> (h+1, vector<int> (w+1, 0));

    cin >> tmp_string >> in_amt;
    for (int i = 0; i < in_amt; i++) {
        int l, r, t, b;
        cin >> l >> b >> r >> t;
        
        for (int cur_y = b; cur_y <= t; cur_y++)
            for (int cur_x = l; cur_x <= r; cur_x++)
                grid[cur_y][cur_x] = OBSTACLE;
            
    }

    cin >> tmp_string >> in_amt;
    for (int i = 0; i < in_amt; i++) {
        int in[4];
        cin >> in[0] >> in[1] >> in[2] >> in[3];

        Connection tmp_connect (i+1, in[0], in[1], in[2], in[3]);

        BFS (tmp_connect, grid);
        tmp_connect.shortest_route_length = tmp_connect.lnth;
        tmp_connect.lnth = tmp_connect.bend = 0;
        tmp_connect.path.clear();

        connects.push_back(tmp_connect);
    }

    sort (connects.begin(), connects.end());
    
    bool valid = true;
    for (Connection &k : connects) {
        if (grid[k.init_y][k.init_x] != SPARE || grid[k.term_y][k.term_x] != SPARE)
            k.connected = false;
        else BFS (k, grid);

        if (k.connected) {
//            cout << "connecting " << k.idx << '\n';
            for (auto p : k.path) {
                if (grid[p.second][p.first] != 0) {
                    cout << "connection on obstacle!! >> " << p.first << ' ' << p.second;
                    valid = false;
                }
                grid[p.second][p.first] = k.idx;
            }
        }
//        else
//            cout << "connecting " << k.idx << " failed!\n";
//
//        print_grid(grid, k.idx);
        
        if (!valid) return -1;  //check routing on obstacles
    }

    sort (connects.begin(), connects.end(), [] (Connection &a, Connection &b) {
            return a.idx < b.idx;
         });

    //Analyze each connection
    int route_cnt = 0;
    int total_lnth = 0, total_bend = 0;
    int max_lnth = 0, max_lnth_idx = 0;
    for (const Connection &c : connects) {
        if (!c.connected) {
            continue;
        }

        route_cnt++;
        total_lnth += c.lnth, total_bend += c.bend;
        if (c.lnth > max_lnth) max_lnth = c.lnth, max_lnth_idx = c.idx;
    }

    // Output
    cout << "#interconnections routed = " << route_cnt << '\n';
    cout << "Total interconnection length = " << total_lnth << '\n';
    cout << "The longest interconnection = " << max_lnth_idx;
    cout << "; length = " << max_lnth << '\n';
    cout << "Total number of bends = " << total_bend << '\n';

    for (const Connection &c : connects) {
        cout << "Interconnection " << c.idx << ": ";

        // not routed
        if (!c.connected) {
            cout << "fails.\n";
            continue;
        }

        // routed
        cout << "length = " << c.lnth << ", #bends = " << c.bend << '\n';
        for (size_t i = 0; i < c.path.size(); i++) {
            cout << '(' << c.path[i].first << ", " << c.path[i].second << ")";

            if (i != c.path.size()-1) cout << ", ";
            else cout << '\n';
        }
    }

    return 0;
}
