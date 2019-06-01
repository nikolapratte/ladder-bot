import re
import pickle
from collections import defaultdict

import discord

import ladder_manager_base as base
from ladder_manager_base import DirectedMessage
from ladder_manager_base import Team

class InvalidUserInput(Exception):
    """Called when the user input is invalid."""
    pass


class Challenge():
    """Truth value shared between the two global challenge dictionaries."""
    def __init__(self, team1 : Team, team2 : Team):
        self._challenger = team1
        self._challenged = team2
        self._teams = (self._challenger, self._challenged)
        self.accepted = False
    
    def get_challenger_team(self):
        return self._challenger
    
    def get_challenged_team(self):
        return self._challenged
    
    def get_challenged_players(self) -> [int]:
        return self._challenged.get_players()
    
    def get_challenged_players_names(self) -> [str]:
        return self._challenged.get_players_names()
    
    def get_challenger_players(self) -> [int]:
        return self._challenger.get_players()
    
    def get_challenger_players_names(self) -> [str]:
        return self._challenger.get_players_names()
    
    def get_all_players(self) -> [int]:
        return self.get_challenger_players() + self.get_challenged_players()
    
    def get_is_1v1(self) -> bool:
        return len(self.get_all_players()) == 2
    
    def get_acceptance(self) -> bool:
        return self.accepted
    
    def get_teams(self, p_id : int) -> (Team, Team):
        """Returns the teams involved in the challenge, the first team representing the team the p_id is in."""
        return (self._challenger, self._challenged) if p_id in self._challenger else (self._challenged, self._challenger)


class ChallengeCommands():
    """Inherited by LadderManager. Supplies challenge-related commands."""
    def challenge_option(self, message: discord.Message) -> base.DirectedMessage:
        """Allows a player to challenge another player."""
        team1 = self._get_player_team(message.author.id)
        
        try:
            player2 = self._mention_strip(message.content)
        except ValueError:
            return DirectedMessage('Cannot locate user', message.channel)
        
        team2 = self._get_player_team(player2)
        if not(team1.get_acceptance() and team2.get_acceptance()):
            return DirectedMessage('Error: One of the teams is not fully ready:\n' + 'Team 1 - ' + str(team1) + '\nTeam 2 - ' + str(team2), message.channel)
        if self.dynamic_options['enforce_equal_size_teams'] and len(team1) != len(team2):
            return DirectedMessage('Error: Server owner enforces that teams are equal size.', message.channel)
        
        challenge_value = Challenge(team1, team2)
        
        if not self._valid_challenge_input(challenge_value):
            return DirectedMessage(
'''One of the players involved is engaged in a challenge already.
Or for some reason you are challenging yourself...''', message.channel)
            
        for player in challenge_value.get_all_players():
            self.challenges[player] = challenge_value
        
        return DirectedMessage('Challenged: {team2}\nChallenger(s): {team1}'.format(
            team2 = ', '.join(challenge_value.get_challenged_players_names()),
            team1 = ', '.join(challenge_value.get_challenger_players_names())), message.channel)


    def _player_in_chal_system(self, player : int) -> bool:
        """Returns whether or not a player is in the challenge system."""
        return player in self.challenges
    
    
    def _valid_challenge_input(self, challenge : Challenge) -> bool:
        """Raises an Error if the user input is invalid."""
        for player in challenge.get_all_players():
            if (self._player_in_chal_system(player)):
                return False
        return True and challenge.get_challenger_team() != challenge.get_challenged_team()
        
        
    def cancel_challenge_option(self, message : discord.Message) -> base.DirectedMessage:
        if message.author.id in self.challenges:
            for player in self.challenges[message.author.id].get_all_players():
                del self.challenges[player]
            return DirectedMessage('Challenge successfully declined', message.channel)
        return DirectedMessage('You have no challenge to decline.', message.channel)
    
    
    def accept_challenge_option(self, message : discord.Message) -> base.DirectedMessage:
        if message.author.id not in self.challenges:
            return DirectedMessage('You have no challenge to accept.', message.channel)
        elif message.author.id not in self.challenges[message.author.id].get_challenged_players():
            return DirectedMessage('You cannot accept your own challenge.', message.channel)
        elif self.challenges[message.author.id].get_acceptance():
            return DirectedMessage('Challenge has already been accepted.', message.channel)
        else:
            self.challenges[message.author.id].accepted = True
            return DirectedMessage('Challenge successfully accepted', message.channel)
        
    
    #same command as cancel_challenge
    def decline_challenge_option(self, message : discord.Message) -> base.DirectedMessage:
        if message.author.id in self.challenges:
            for player in self.challenges[message.author.id].get_all_players():
                del self.challenges[player]
            return DirectedMessage('Challenge successfully declined', message.channel)
        return DirectedMessage('You have no challenge to decline.', message.channel)
    
    
    def _find_challenge(self, player : int) -> Challenge:
        if player in self.challenges:
            return self.challenges[player]
    
    
    def report_challenge_option(self, message : discord.Message) -> base.DirectedMessage:
        if not self._player_in_chal_system(message.author.id): #ensure player is in a challenge
            return DirectedMessage('You need to be engaged in a challenge to report scores', message.channel)
        
        challenge = self.challenges[message.author.id]
        if not challenge.get_acceptance():
            return DirectedMessage('Challenged team needs to have accepted the challenge to report scores', message.channel)
        t1, t2 = challenge.get_teams(message.author.id)
        
        message_cont = message.content.strip().lower()
        descriptions = {'win': r'win|won|wins|wons',
                        'loss': r'loss|lose|lost',
                        'match': r'(#win#|#loss#) ?([1-9])?'}
        
        def name_re(re_dict : {str: str}) -> None:
            """Mutates a given dictionary to implement named regex."""
            for key in re_dict:
                pattern = re.compile(f'#{key}#')
                for other_key in re_dict:
                    re_dict[other_key] = pattern.sub(f'(?:{re_dict[key]})', re_dict[other_key])
        name_re(descriptions)
        
        if not re.search(descriptions['match'], message_cont):
            return DirectedMessage('Error: report syntax is wrong (should be "!report (win or loss) #, (win or loss) #").', message.channel)
        
        sets = ((base.WIN if re.match(descriptions['win'], outcome) else base.LOSS, int(amt))\
                 for outcome, amt in re.findall(descriptions['match'], message_cont))
        
        if self.dynamic_options['separate_1v1_mmr'] and challenge.get_is_1v1():
            player_stats = self.player_stats_1v1
        else:
            player_stats = self.player_stats
            
        for player in challenge.get_all_players():
            self._create_player_account(player_stats, player)
        
        
        t1mmr = sum((player_stats[player]['rating'] for player in t1.get_players()))//len(t1.get_players())
        t2mmr = sum((player_stats[player]['rating'] for player in t2.get_players()))//len(t2.get_players())
        
        new_t1mmr, new_t2_mmr, t1wins, t2wins = base.mmr_calculator(
                                                            self.dynamic_options['base_rating_change'],
                                                           self.dynamic_options['prediction_difference'],
                                                           t1mmr,
                                                           t2mmr,
                                                           sets)
        
        t1mmr_delta = new_t1mmr - t1mmr
        t2mmr_delta = new_t2_mmr - t2mmr 
        
        self._set_stats_mass(t1.get_players(), t1mmr_delta, t1wins, t2wins, player_stats)
        self._set_stats_mass(t2.get_players(), t2mmr_delta, t2wins, t1wins, player_stats)
        
        self._update_record_mass(t1.get_players(), t2.get_players(),
                                 t1wins, t2wins, player_stats)
        self._update_record_mass(t2.get_players(), t1.get_players(),
                                 t2wins, t1wins, player_stats)
        
        self._save_player_stats()
        self._delete_from_challenges(challenge.get_all_players())
        string = self._inform_match(t1.get_players_names(), t2.get_players_names(),
                                    t1wins, t2wins, t1mmr_delta, t2mmr_delta)
        
        return DirectedMessage(string, message.channel)
    
    
    def _delete_from_challenges(self, players : [int]) -> None:
        for player in players:
            del self.challenges[player]
            
    
    def _set_stats_mass(self, players : [int], mmr_delta : int, wins : int, losses : int, player_stats : dict) -> None:
        for player in players:
            self._set_stats(player, mmr_delta, wins, losses, player_stats)
    
    
    def _set_stats(self, p1_id : int, mmr_delta : int, p1wins : int, p1losses : int, player_stats : dict):
        player_stats[p1_id]['rating'] += mmr_delta
        player_stats[p1_id]['wins'] += p1wins
        player_stats[p1_id]['losses'] += p1losses
    
    
    def _add_record(self, user_id : int, player_stats : dict) -> None:
        if user_id not in player_stats:
            return False
        if 'records' not in player_stats[user_id]:
            player_stats[user_id]['records'] = {}
        return True
    
    
    def _update_record_mass(self, players : [int], opponents : [int], wins : int, losses : int, player_stats : dict) -> None:
        for player in players:
            self._update_record(player, opponents, wins, losses, player_stats)
    
    
    def _update_record(self, user_id : int, opponents : [int], wins : int, losses : int, player_stats : dict) -> None:
        """Updates the record of a player vs any amount of opponents. Must be run separately for all involved players."""
        user_worked = self._add_record(user_id, player_stats)
        
        if user_worked:
            for opponent in opponents:
                opponent_worked = self._add_record(opponent, player_stats)
                if opponent_worked and not opponent in player_stats[user_id]['records']:
                    player_stats[user_id]['records'][opponent] = defaultdict(int)
                    player_stats[user_id]['records'][opponent]['wins'] += wins
                    player_stats[user_id]['records'][opponent]['losses'] += losses
                else:
                    pass
    

    def _inform_match(self, challengers : [str], challenged : [str],
                      t1wins : int, t2wins : int, t1mmr_delta : int, t2mmr_delta : int):
        challengers = ', '.join(player for player in challengers)
        challenged = ', '.join(player for player in challenged)
        
        if t1wins > t2wins:
            string = 'Reporting team: ({t1}) beat team ({t2}) {wins} to {losses}.'.format(
                t1 = challengers, t2 = challenged, wins = t1wins, losses = t2wins)
        elif t1wins < t2wins:
            string = 'Reporting team: ({t2}) beat team ({t1}) {wins} to {losses}.'.format(
                t1 = challengers, t2 = challenged, wins = t2wins, losses = t1wins)
        else:
            string = 'Reporting team: ({t1}) tied team ({t2}) {wins} to {losses}.'.format(
                t1 = challengers, t2 = challenged, wins = t1wins, losses = t2wins)
            
        string += \
f'''\nEach member of the reporting team gained {t1mmr_delta} mmr.
Each member of the other team gained {t2mmr_delta}mmr.'''
    
        return string


    def _create_player_account(self,player_stats : dict, *id_list) -> None:
        """Creates an 'account' for a player in player_stats global variable if
        the player doesn't already have an account (accounts are associated with
        discord user ID."""
        
        for user_id in id_list:
            if user_id not in player_stats:
                player_stats[user_id] = {'rating': self.dynamic_options['starting_rating'],
                                             'wins': 0,
                                             'losses': 0,
                                             'records': {}}
    
    
    def _save_player_stats(self):
        player_stats = self.player_stats
        archived_player_stats = self._archived_player_stats
        player_stats_1v1 = self.player_stats_1v1
        archived_player_stats_1v1 = self._archived_player_stats_1v1
        with open('laddermanager.pkl', 'wb') as saveFile:
                pickle.dump([player_stats, archived_player_stats, player_stats_1v1, archived_player_stats_1v1], saveFile)
        