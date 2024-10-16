from Player import Player


class Game(object):
    
    players : [Player]
    players_busted_by : {Player: Player}
    placements : {Player: int}
    K_constant = 48
    bust_bonus = 0.15
    
    def __init__(self, players = [], players_busted_by = {}, placements = {}):
        self.players = players
        self.players_busted_by = players_busted_by
        self.placements = placements
        
    def calculate_new_elo(self):
        for player in self.players:
            player.rating = player.rating + self.calculate_elo_change(player)
     
    def calculate_elo_change(self, player) -> float:
        mean_elo = self.get_mean_elo()
        score = self.get_score(player)
        probability = self.get_probability_of_winning(player)
        bust_bonus_mult = 1 + self.get_total_number_of_players_busted(player) * self.bust_bonus
        return (self.K_constant * (score - probability)) * bust_bonus_mult if score - probability > 0 else (self.K_constant * (score - probability) / bust_bonus_mult)

    def calculate_new_elo(self, player) -> float:
        return player.rating + self.calculate_elo_change(player)
        
    def get_total_number_of_players_busted(self, player) -> int:
        return sum([1 for key in self.players_busted_by if self.players_busted_by[key] == player])
        
    
    def get_mean_elo(self) -> float: 
        return sum([player.rating for player in self.players]) / len(self.players)
    
    def get_placement(self, player) -> int:
        return self.placements[player]

    def get_score(self, player) -> float:
        return 1 - (self.get_placement(player) - 1)  * (1 / len(self.players))
    
    def get_probability_of_winning(self, player) -> float:
        return 1 / (1 + 10 ** ((self.get_mean_elo() - player.rating) / 400))
        
