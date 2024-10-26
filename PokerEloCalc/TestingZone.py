from sqlite3 import DatabaseError
from Player import Player
from PokerEloCalc import Game
import DatabaseService


def m():
    # Placeholder for player who was not busted by anyone
    noOne = Player("No One", 1000)

    # info = [[name, placement, busted_by]]
    # DatabaseService.reset_all_ratings()
    # DatabaseService.clear_all_games_records()

    poker_game = DatabaseService.instantiate_poker_game([
        ["Henry", 1, "No One"],
    ["Kevin", 2, "Henry"],
    ["Rory", 3, "Henry"],
    ["Noe", 4, "Kevin"]
    ])



    for player in poker_game.players:
        print(f"{player.name.center(20)} | rating: {str(player.rating).ljust(7)} -> {str(poker_game.calculate_new_elo(player)).ljust(7)} | placement: {poker_game.get_placement(player)} | busted by: {poker_game.players_busted_by[player].name}")

    DatabaseService.record_poker_game(poker_game)
    DatabaseService.display_leaderboard()

m()

