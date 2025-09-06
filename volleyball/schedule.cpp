#include <iostream>
#include <climits>
#include <vector>
#include <set>
#include <fstream>
#include <algorithm>

using namespace std;


struct Game {
    int team1;
    int team2;
};

struct GameWithReferee {
    Game game;
    int referee;
};

// Function to generate a round-robin schedule using the circle method
vector<Game> generateRoundRobinSchedule(int totalTeams) {
    vector<Game> games;
    int numTeams = totalTeams;

    // Create the round-robin schedule using the circle method
    for (int round = 0; round < numTeams - 1; ++round) {
        for (int i = 0; i < numTeams / 2; ++i) {
            int team1 = (round + i) % (numTeams - 1);
            int team2 = (numTeams - 1 - i + round) % (numTeams - 1);

            // Fix one team in place
            if (i == 0) {
                team2 = numTeams - 1;
            }

            games.push_back({team1 + 1, team2 + 1});
        }
    }

    return games;
}

// Function to assign referees after building the complete schedule
void assignReferees(vector<vector<pair<GameWithReferee, GameWithReferee>>>& schedule, vector<int>& refereeCounts) {
    for (size_t week = 0; week < schedule.size(); ++week) {
        for (size_t slot = 0; slot < schedule[week].size(); ++slot) {
            auto& gamePair = schedule[week][slot];

            // Collect teams playing in the current slot
            set<int> teamsPlayingThisSlot = {
                gamePair.first.game.team1, 
                gamePair.first.game.team2, 
                gamePair.second.game.team1, 
                gamePair.second.game.team2
            };

            // Function to find a referee for a game
            auto findRefereeForGame = [&](int& refereeCount) {
                set<int> potentialReferees;

                // Check teams in previous slot
                if (slot > 0) {
                    const auto& previousSlot = schedule[week][slot - 1];
                    potentialReferees.insert(previousSlot.first.game.team1);
                    potentialReferees.insert(previousSlot.first.game.team2);
                    potentialReferees.insert(previousSlot.second.game.team1);
                    potentialReferees.insert(previousSlot.second.game.team2);
                }

                // Check teams in next slot
                if (slot + 1 < schedule[week].size()) {
                    const auto& nextSlot = schedule[week][slot + 1];
                    potentialReferees.insert(nextSlot.first.game.team1);
                    potentialReferees.insert(nextSlot.first.game.team2);
                    potentialReferees.insert(nextSlot.second.game.team1);
                    potentialReferees.insert(nextSlot.second.game.team2);
                }

                // Remove teams that are playing in the current games
                for (int team : teamsPlayingThisSlot) {
                    potentialReferees.erase(team);
                }

                // Choose the referee with the least assignments
                int chosenReferee = -1;
                int minRefereeCount = INT_MAX;

                for (int team : potentialReferees) {
                    if (refereeCounts[team - 1] < minRefereeCount && (refereeCounts[team - 1] < 7)) {
                        chosenReferee = team;
                        minRefereeCount = refereeCounts[team - 1];
                    }
                }

                // Fallback to any eligible referee if no suitable option is found
                if (chosenReferee == -1) {
                    for (int team : potentialReferees) {
                        if (refereeCounts[team - 1] < 7) {
                            chosenReferee = team;
                            break;
                        }
                    }
                }

                // Assign referee if found
                if (chosenReferee != -1) {
                    refereeCounts[chosenReferee - 1]++;
                }

                return chosenReferee;
            };

            // Assign referees for both games in the slot
            gamePair.first.referee = findRefereeForGame(gamePair.first.referee);
            gamePair.second.referee = findRefereeForGame(gamePair.second.referee);
        }
    }
}

// Function to distribute games across weeks with two games per time slot (no overlapping teams)
vector<vector<pair<GameWithReferee, GameWithReferee>>> distributeGamesAcrossWeeks(const vector<Game>& games, int totalWeeks) {
    vector<vector<pair<GameWithReferee, GameWithReferee>>> schedule(totalWeeks);
    size_t gameIndex = 0;

    for (int week = 0; week < totalWeeks; ++week) {
        int slotsThisWeek = (week == totalWeeks - 1) ? 2 : 3; // Last week has 2 slots (4 games)

        for (int slot = 0; slot < slotsThisWeek; ++slot) {
            if (gameIndex >= games.size()) break;

            // Attempt to create a pair of games that can be played simultaneously
            Game game1 = games[gameIndex++];
            Game game2;

            // Find a second game that does not overlap with the teams in the first game
            for (size_t i = gameIndex; i < games.size(); ++i) {
                if (games[i].team1 != game1.team1 && games[i].team1 != game1.team2 &&
                    games[i].team2 != game1.team1 && games[i].team2 != game1.team2) {
                    game2 = games[i];
                    gameIndex = i + 1; // Move the index to the next game after the selected one
                    break;
                }
            }

            // Schedule the pair of games without referees for now
            GameWithReferee gameWithReferee1 = {game1, -1}; // Initialize referee as -1
            GameWithReferee gameWithReferee2 = {game2, -1}; // Initialize referee as -1

            schedule[week].push_back({gameWithReferee1, gameWithReferee2});
        }
    }

    return schedule;
}

// Function to save the schedule with referees into a CSV file
void saveScheduleToCSV(const vector<vector<pair<GameWithReferee, GameWithReferee>>>& schedule, const string& filename) {
    ofstream file(filename);

    // Write the CSV header
    file << "Week,Slot,Game 1 Team 1,Game 1 Team 2,Game 1 Referee,Game 2 Team 1,Game 2 Team 2,Game 2 Referee\n";

    // Write the schedule data
    for (size_t week = 0; week < schedule.size(); ++week) {
        int slotNumber = 1;
        for (const auto& slot : schedule[week]) {
            file << (week + 1) << "," << slotNumber++ << ","
                 << slot.first.game.team1 << "," << slot.first.game.team2 << "," << slot.first.referee << ","
                 << slot.second.game.team1 << "," << slot.second.game.team2 << "," << slot.second.referee << "\n";
        }
    }

    file.close();
    cout << "Schedule saved to " << filename << endl;
}

// Function to display the schedule
void displaySchedule(const vector<vector<pair<GameWithReferee, GameWithReferee>>>& schedule) {
    for (size_t week = 0; week < schedule.size(); ++week) {
        cout << "Week " << week + 1 << " games:" << endl;
        int slotNumber = 1;
        for (const auto& slot : schedule[week]) {
            cout << "  Slot " << slotNumber++ << ":" << endl;
            cout << "    Game 1: Team " << slot.first.game.team1 << " vs Team " << slot.first.game.team2
                 << " (Referee: Team " << slot.first.referee << ")\n";
            cout << "    Game 2: Team " << slot.second.game.team1 << " vs Team " << slot.second.game.team2
                 << " (Referee: Team " << slot.second.referee << ")\n";
        }
        cout << endl;
    }
}

// Function to check referee balance
void checkRefereeBalance(const vector<int>& refereeCounts) {
    cout << "Referee balance check: " << endl;
    for (size_t i = 0; i < refereeCounts.size(); ++i) {
        cout << "Team " << i + 1 << ": Refereed " << refereeCounts[i] << " games." << endl;
    }
}

int main() {
	const int totalTeams = 14; // Adjust for your league
	const int totalWeeks = 16; // Number of weeks in the season

    // Generate round-robin schedule
    vector<Game> games = generateRoundRobinSchedule(totalTeams);

    // Distribute games across weeks
    vector<vector<pair<GameWithReferee, GameWithReferee>>> schedule = distributeGamesAcrossWeeks(games, totalWeeks);

    // Initialize referee counts
    vector<int> refereeCounts(totalTeams, 0);

    // Assign referees to each game
    assignReferees(schedule, refereeCounts);

    // Save the schedule to a CSV file
    saveScheduleToCSV(schedule, "game_schedule_with_referees.csv");

    // Display the schedule
    displaySchedule(schedule);

    // Check referee balance
    checkRefereeBalance(refereeCounts);

    return 0;
}
