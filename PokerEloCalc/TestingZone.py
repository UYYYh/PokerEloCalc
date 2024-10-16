from sqlite3 import DatabaseError
from Player import Player
from PokerEloCalc import Game
import DatabaseService

# Placeholder for player who was not busted by anyone
noOne = Player("No One", 1000)

# info = [[name, placement, busted_by]]
# DatabaseService.reset_all_ratings()
# DatabaseService.clear_all_games_records()

poker_game = DatabaseService.instantiate_poker_game([["Kevin Wang", 1, "No One"], 
                                                     ["Noe Teyssier", 2, "Kevin Wang"], 
                                                     ["Andrew Chen", 3, "Noe Teyssier"],
                                                     ["Krrish Shah", 4, "Andrew Chen"],
                                                     ["Yuquan Zhou", 5, "Krrish Shah"],
                                                     ])



for player in poker_game.players:
    print(f"{player.name} | rating: {player.rating} -> {poker_game.calculate_new_elo(player)} | placement: {poker_game.get_placement(player)} ")



DatabaseService.test_connection()
DatabaseService.record_poker_game(poker_game)

DatabaseService.display_leaderboard()


