from distutils.command import upload
from sqlite3 import DatabaseError
from Player import Player
from PokerEloCalc import Game
import DatabaseService, Uploader


def parse_result(results_string):
    lines = [[index + 1] + line.split(" - busted by ") for index, line in enumerate(results_string.split("\n")[::-1])]
    lines[0] += ["No One"]
    return lines

def upload_game(results_string):
    # Placeholder for player who was not busted by anyone
    noOne = Player("No One", 1000)


    poker_game = DatabaseService.instantiate_poker_game(parse_result(results_string))



    for player in poker_game.players:
        print(f"{player.name.center(20)} | rating: {str(player.rating).ljust(7)} -> {str(poker_game.calculate_new_elo(player)).ljust(7)} | placement: {poker_game.get_placement(player)} | busted by: {poker_game.players_busted_by[player].name}")

    DatabaseService.record_poker_game(poker_game)
    DatabaseService.display_leaderboard()
    

results = """Murad - busted by Kevin
Dima - busted by Henry
Kevin - busted by Henry
William - busted by Henry
Leo - busted by Joy
Noe - busted by Henry
Henry - busted by Joy
Joy"""

# upload_game(results)

# Uploader.export_to_excel()



