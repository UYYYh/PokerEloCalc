from distutils.command import upload
from sqlite3 import DatabaseError
from Player import Player
from PokerEloCalc import Game
import DatabaseService, Uploader


def upload_game():
    # Placeholder for player who was not busted by anyone
    noOne = Player("No One", 1000)


    poker_game = DatabaseService.instantiate_poker_game([
    ["Leo", 1, "No One"],
    ["Henry", 2, "Leo"],
    ["Andrew", 3, "Henry"],
    ["Joy", 4, "Henry"],
    ["Dima", 5, "Andrew"],
    ["Charis", 6, "Leo"],
    ["Vlad", 7, "Henry"],
    ["Kaka", 8, "Henry"],
    ["Kevin", 9, "Henry"],
    ["Nyron", 10, "Henry"],
    ["Blake", 11, "Andrew"]
])



    for player in poker_game.players:
        print(f"{player.name.center(20)} | rating: {str(player.rating).ljust(7)} -> {str(poker_game.calculate_new_elo(player)).ljust(7)} | placement: {poker_game.get_placement(player)} | busted by: {poker_game.players_busted_by[player].name}")

    DatabaseService.record_poker_game(poker_game)
    DatabaseService.display_leaderboard()
    
Uploader.export_to_excel()



