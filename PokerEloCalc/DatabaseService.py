from distutils.util import execute
import re
from sqlalchemy import create_engine, text
from contextlib import contextmanager
from Player import Player
from PokerEloCalc import Game
from datetime import datetime
import os, uuid

noOne = Player("No One", 1000)
engine = "Uninitialised"

def InitialiseMySQL() -> engine:
    global engine
    if engine == "Uninitialised":
        # Fetch MySQL credentials from environment variables
        mySQLPassword = os.environ.get("CHATAPIADMINPASSWORD")
        mySQLUsername = os.environ.get("CHATAPIADMINUSERNAME")
        
        # Specify the new database name ('poker_game_db')
        engine = create_engine(f"mysql+pymysql://{mySQLUsername}:{mySQLPassword}@localhost:3306/poker_game_db", pool_size=20, max_overflow=10)
        
    return engine

engine = InitialiseMySQL()

@contextmanager
def get_db_connection():
    try:
        connection = engine.connect()
        yield connection
    finally:
        connection.close()

def execute_sql(query: str, params: dict, fetch: bool = False):
    with get_db_connection() as connection:
        result = connection.execute(text(query), params)
        connection.commit()
        return result if fetch else None


def test_connection():
    try:
        # Initialise the engine
        engine = InitialiseMySQL()
        
        # Establish connection
        with engine.connect() as connection:
            # Test with a simple query (selecting from an existing table or running a small SQL command)
            result = connection.execute(text("SELECT 1"))
            print("Connection successful:", result.scalar())
            
    except Exception as e:
        print("Error connecting to the database:", str(e))
        
def create_new_player(name: str, rating: int):
    execute_sql("INSERT INTO player (name, rating) VALUES (:name, :rating)", {"name": name, "rating": rating})
        
def update_player_rating(name: str, rating: int):
    execute_sql("UPDATE player SET rating = :rating WHERE name = :name", {"name": name, "rating": rating})
    
def create_player_poker_game_record(player: Player, game_id: str, placement: int, busted_by: Player, elo_before : float, elo_change: float):
    execute_sql("""
                INSERT INTO player_poker_game_info 
                (name, game_id, placement, busted_by, elo_before, elo_change) 
                VALUES (:name, :game_id, :placement, :busted_by, :elo_before, :elo_change)
                """,
               {"name": player.name,
                "game_id": game_id,
                "placement": placement,
                "busted_by": busted_by.name,
                "elo_before": elo_before,
                "elo_change": elo_change}
                )

def get_date_of_today() -> str:
    return datetime.now().strftime("%Y-%m-%d")
    
def create_new_game_record(game_id: str, date: str = None):
    if date == None:
        date = get_date_of_today()
    execute_sql("INSERT INTO poker_game (game_id, game_date) VALUES (:game_id, :game_date)", {"game_id": game_id, "game_date": date})

def player_exists_in_database(player: Player) -> bool:
    result = execute_sql("SELECT 1 FROM player WHERE name = :name", {"name": player.name}, fetch=True)
    return result.scalar() is not None

def get_player_rating(name: str) -> float:
    result = execute_sql("SELECT rating FROM player WHERE name = :name", {"name": name}, fetch=True)
    return result.scalar()

def reset_all_ratings():
    execute_sql("UPDATE player SET rating = 1000", {})

def clear_all_games_records():
    execute_sql("DELETE FROM poker_game", {})
    
def display_player_info(name : str):
    # Display elo, win rate, total number of games played, and total number of games won
    query = """
        SELECT name, rating,
        (SELECT COUNT(*) FROM player_poker_game_info WHERE name = :name) AS total_games,
        (SELECT COUNT(*) FROM player_poker_game_info WHERE name = :name AND placement = 1) AS total_wins
        FROM player WHERE name = :name
        """
    result = execute_sql(query, {"name": name}, fetch=True).fetchone()
    print(f"{result[0]} | elo: {result[1]} | Total Number of Games Played: {result[2]} | Total Number of wins: {result[3]}")

def display_leaderboard():
    query = """
        SELECT name, rating,
        (SELECT COUNT(*) FROM player_poker_game_info WHERE name = player.name) AS total_games,
        (SELECT COUNT(*) FROM player_poker_game_info WHERE name = player.name AND placement = 1) AS total_wins
        FROM player ORDER BY rating DESC
        """
    result = execute_sql(query, {}, fetch=True).fetchall()
    for row in result:
        print(f"{str(row[0]).center(20)} | elo: {str(int(row[1])).ljust(4)} | Total Number of Games Played: {str(row[2]).ljust(3)} | Total Number of wins: {row[3]}")
        

def record_poker_game(poker_game: Game, date : str = None):
    
    # Create a new game record
    game_id = str(uuid.uuid4())
    create_new_game_record(game_id, date)
    
    for player in poker_game.players:
        # Check if the player exists in the database
        # If not, create a new player record
        if not player_exists_in_database(player):
            create_new_player(player.name, player.rating)
        
        elo_before = player.rating
        elo_change = poker_game.calculate_elo_change(player)
        
        create_player_poker_game_record(player, game_id, poker_game.get_placement(player), poker_game.players_busted_by[player], elo_before, elo_change)
        update_player_rating(player.name, poker_game.calculate_new_elo(player))



def instantiate_poker_game(info: [[str]]):
    players = []
    players_busted = {}
    placements = {}
    for player_info in info:
        rating = get_player_rating(player_info[0])
        player = Player(player_info[0], rating)
        players.append(player)
        placements[player] = player_info[1]
        if player_info[2] != None:
            busted_by_elo = get_player_rating(player_info[2])
            busted_by = Player(player_info[2], busted_by_elo)
            players_busted[player] = busted_by
        else:
            players_busted[player] = noOne
    return Game(players, players_busted, placements)

def delete_game(game_id: str):
    execute_sql("DELETE FROM poker_game WHERE game_id = :game_id", {"game_id": game_id})

def revert_game(game_id: str):
    query = "SELECT name, elo_change FROM player_poker_game_info WHERE game_id = :game_id"
    result = execute_sql(query, {"game_id": game_id}, fetch=True).fetchall()
    # Delete the game from the database
    delete_game(game_id)
    for row in result:
        update_player_rating(row[0], get_player_rating(row[0]) - row[1])



