import random

import discord

import ladder_manager_base as base
from ladder_manager_base import Team
from dynamic_options import DYNAMIC_OPTIONS


        
def create_line() -> str:
    return 30*'~'


class InformationCommands():
    """Inherited by LadderManager. Supplies information-related commands."""
    """Help text provided when help_option function is called."""
    
    
    #NOTE: create_team option was removed from help since its pretty much the same as invite but worse. But create_team still exists.
    _help_text = (('General Options', create_line()),
                ('{}help'.format(DYNAMIC_OPTIONS['command_symbol']), 'How to use this bot'),
                  ('{}about'.format(DYNAMIC_OPTIONS['command_symbol']), 'About this bot'),
                  ('{}rules'.format(DYNAMIC_OPTIONS['command_symbol']), 'Rules of this ladder system'),
                  ('{}leaderboard'.format(DYNAMIC_OPTIONS['command_symbol']), 'Top players leaderboard'),
                  ('{}full_leaderboard'.format(DYNAMIC_OPTIONS['command_symbol']), 'All players leaderboard'),
                  ('{}stats'.format(DYNAMIC_OPTIONS['command_symbol']), 'Your stats'),
                  ('{}stats @username'.format(DYNAMIC_OPTIONS['command_symbol']), '@username\'s stats'),
                  ('{}record'.format(DYNAMIC_OPTIONS['command_symbol']), 'Your record vs other players'),
                  ('{}record @username'.format(DYNAMIC_OPTIONS['command_symbol']), '@username\'s record vs other players'),
                  
                  ('Challenge Options', create_line()),
                  ('{}play @username'.format(DYNAMIC_OPTIONS['command_symbol']), 'challenge @username to a set'),
                  ('{}accept'.format(DYNAMIC_OPTIONS['command_symbol']), 'accept a received challenge'),
                  ('{}decline'.format(DYNAMIC_OPTIONS['command_symbol']), 'decline a received challenge'),
                  ('{}ongoing'.format(DYNAMIC_OPTIONS['command_symbol']), 'see ongoing challenges (accepted and not accepted)'),
                  ('{command_symbol}report'.format(command_symbol = DYNAMIC_OPTIONS['command_symbol']), '''reports wins and losses for a challenge and concludes the challenge.
                        Order matters!! Example commands:
                        "{command_symbol}report win 2, loss 1"
                        "{command_symbol}report loss 3"
                        "{command_symbol}report win 1, loss 1, win 1"'''.format(command_symbol = DYNAMIC_OPTIONS['command_symbol'])),
                  
                  ('Team Options', create_line()),
                  ('Note', 'All members on a team must have accepted the team invite before they can challenge another team.'),
                  ('{}invite @users'.format(DYNAMIC_OPTIONS['command_symbol']), 'invite mentioned people to your team (can be used to create a team)'),
                  ('{}accept team'.format(DYNAMIC_OPTIONS['command_symbol']), 'accepts a team request (don\'t confuse with "{}accept"'.format(DYNAMIC_OPTIONS['command_symbol'])),
                  ('{}leave team'.format(DYNAMIC_OPTIONS['command_symbol']), 'leaves your current team'),
                  ('{}status'.format(DYNAMIC_OPTIONS['command_symbol']), 'see your team\'s current status')
                  )
    def help_option(self, message: discord.Message) -> base.DirectedMessage:
        """Provides assistance on how to use the bot."""
        author = message.author
        string = """Hi {name}. I am Ladder Manager, version {version}.\n\n""".format(name = author.name,
                                                                        version = self.version)
        string += '\n'.join(f'{op_name:<20} : {op_desc}' for op_name, op_desc in self._help_text)
        
        return base.DirectedMessage('```' + string + '```', author)


    def _get_about_text(self) -> str:
        """Relies on dynamic option: 'about text'."""
        return self.dynamic_options['about_text']

    _default_text = '''LadderManager is a bot made by discord user Antis#4219 to facilitate an honor-based ladder
system for discord servers. If you find issues or have ideas for additional feature, please let me know.
Thank you for using LadderManager.\n\n'''
    def about_option(self, message: discord.Message) -> base.DirectedMessage:
        """Discusses what the bot is about."""
        return base.DirectedMessage(self._default_text + self._get_about_text(), message.author)


    def _get_rules_text(self) -> str:
        """Relies on dynamic option: 'rules text'."""
        return self.dynamic_options['rules_text']
    
    def rules_option(self, message: discord.Message) -> (base.DirectedMessage):
        """Returns rules of use for the ladder."""
        return base.DirectedMessage('Rules:\n' + self._get_rules_text(), message.author)

    
    def _filter_player_stats(self, player_stats : dict, archived_player_stats : dict) -> None:
        """Eliminates players who are no longer on the server from player_stats so generate leaderboard
        works properly."""
        for player in dict(player_stats):
            if self._find_user(player) == None:
                archived_player_stats[player] = player_stats[player]
                del player_stats[player]
                print(f'Deleted player (id: {player}) since system cannot find them in any server.')
            
    
    def _return_player_stats(self, player_stats : dict, archived_player_stats : dict) -> None:
        """Returns archived players back into player stats if they can be detected again."""
        for player in dict(archived_player_stats):
            if self._find_user(player):
                player_stats[player] = archived_player_stats[player]
                del archived_player_stats[player]
                print(f'Returned player (id: {player}) to the player stats system since they can be found (previously they were missing).')
        
        
    def _str_leaderboard(self, entries : int, player_stats : dict, description : str) -> str:
        message_str = '```{:^30}\n'.format('~~~~~ {} LEADERBOARD ~~~~~'.format(description))
        place = 1
        for player in sorted(player_stats.items(), 
                                    key = lambda player: player[1]['rating'], 
                                    reverse=True):
            if place >= entries + 1: break
            if (place - 1) % 10 == 0: message_str += '\n'
            try:
                message_str += '{:<4}{:<30} {}\n'.format(place, self._find_user(player[0]).name, player[1]['rating'])
            except UnicodeEncodeError:
                continue
            
            place += 1
            
        message_str += '```'
        
        return message_str
    
    
    def _generate_leaderboard(self, entries: int) -> str:
        """Generates the leaderboard as a string, entries input determines
           how many players are shown on the leaderboard."""
        self._return_player_stats(self.player_stats, self._archived_player_stats)
        self._filter_player_stats(self.player_stats, self._archived_player_stats)
    
        if self.dynamic_options['separate_1v1_mmr']:
            self._return_player_stats(self.player_stats_1v1, self._archived_player_stats_1v1)
            self._filter_player_stats(self.player_stats_1v1, self._archived_player_stats_1v1)
            return self._str_leaderboard(entries, self.player_stats, 'General') + '\n' + self._str_leaderboard(entries, self.player_stats_1v1, '1v1')
        else:
            return self._str_leaderboard(entries, self.player_stats, '')
        
        
    def get_num_top_leaderboard(self) -> int:
        return self.dynamic_options['num_top_leaderboard']
    
    
    def leaderboard_option(self, message: discord.Message) -> base.DirectedMessage:
        """Default leaderboard command, displays the top self._num_top_leaderboard players (dynamic option)."""
        entries = len(self.player_stats.keys()) if len(self.player_stats.keys()) < self.get_num_top_leaderboard() else self.get_num_top_leaderboard()
        return base.DirectedMessage(self._generate_leaderboard(entries), message.channel)

    
    def full_leaderboard_option(self, message: discord.Message) -> base.DirectedMessage:
        """Displays all players in the ladder system."""
        return base.DirectedMessage(self._generate_leaderboard(len(self.player_stats.keys())), message.author)

    
    def _str_stats(self, user_id : int, player_stats : dict, description : str) -> str:
        if self._has_account(user_id):
            list_of_ratings = sorted([player['rating'] for player in player_stats.values()])
            
            place_on_leaderboard = len(list_of_ratings) - list_of_ratings.index(player_stats[user_id]['rating'])
                
            string = '''```{name}\'s {description} stats\nRating: {rating}\nWins: {wins}\nLosses: {losses}\nPlace on leaderboard: {place} out of {total}```'''.format(
                                        name = self._find_user(user_id).name,
                                        description = description,
                                        rating = player_stats[user_id]['rating'],
                                        wins = player_stats[user_id]['wins'],
                                        losses = player_stats[user_id]['losses'],
                                        place = place_on_leaderboard,
                                        total = len(list_of_ratings))
            return string
        else:
            return 'Player {} not found.'.format(self._find_user(
                                                user_id).name)
    
    
    def _generate_stats(self, user_id: int) -> str:
        """Returns a string describing a player's stats,
           includes rating, wins, and losses."""
        if self.dynamic_options['separate_1v1_mmr']:
            return self._str_stats(user_id, self.player_stats, 'general') + self._str_stats(user_id, self.player_stats_1v1, '1v1')
        else:
            return self._str_stats(user_id, self.player_stats, 'general')
    

    def stats_self_option(self, message: discord.Message) -> base.DirectedMessage:
        """Returns the stats of the player who requested his or her stats."""
        return base.DirectedMessage(self._generate_stats(message.author.id),
                                message.channel)


    def stats_other_option(self, message:discord.Message) -> base.DirectedMessage:
        """Returns the stats of the player mentioned."""
        return base.DirectedMessage(self._generate_stats(self._mention_strip(message.content)),
                                message.channel)

    def _str_record(self, user_id : int, player_stats : dict, description : str) -> str:
        if not self._has_account(user_id):
            return 'Player {} does not have an account.'.format(self._find_user(user_id).name)
        if 'records' not in player_stats[user_id]:
            return 'The specified player does not have a record with other players.'
        
        string = '{}\'s {} record against other players:\n\n'.format(self._find_user(user_id).name, description)
        
        for opponent in player_stats[user_id]['records']:
            opponent = self._find_user(opponent)
            if opponent:
                string += 'Against {op_name}\n\tWins: {wins}\n\tLosses: {losses}\n\n'.format(
                    op_name = opponent.name,
                    wins = player_stats[user_id]['records'][opponent.id]['wins'],
                    losses = player_stats[user_id]['records'][opponent.id]['losses'])
            
        return string
    
    
    def _generate_record(self, user_id: int) -> str:
        """Generates the record of a player against other players."""
        if self.dynamic_options['separate_1v1_mmr']:
            return self._str_record(user_id, self.player_stats, 'general') + self._str_record(user_id, self.player_stats_1v1, '1v1')
        else:
            return self._str_record(user_id, self.player_stats, 'general')
        
        
    def record_self_option(self, message: discord.Message) -> base.DirectedMessage:
        """Returns the record of the user who asked for it."""
        return base.DirectedMessage(self._generate_record(message.author.id), message.author)


    def record_other_option(self, message: discord.Message) -> base.DirectedMessage:
        """Returns the record of the pinged player"""
        return base.DirectedMessage(self._generate_record(self._mention_strip(message.content)), message.author)
    
    
    def _player_on_team(self, p_id : int) -> bool:
        return p_id in self.teams and self.teams[p_id]
    
    
    def _input_team_system(self, team : Team) -> None:
        for player in team.get_players():
            self.teams[player] = team
            
            
    def _team_remove(self, p_id : int) -> None:
        team = self.teams[p_id]
        team.remove(p_id)
        del self.teams[p_id]
    
    #inefficient call? (self._find_user)
    def create_team_option(self, message: discord.Message) -> base.DirectedMessage:
        if self._player_on_team(message.author.id):
            return base.DirectedMessage('Error: You are already on a team or have been invited to one.', message.channel)
            
        members = (p_id for p_id in self._mention_strip_mass(message.content.strip().lower()))
        members = ((member, self._find_user(member).name) for member in members if self._find_user(member) is not None)
        
        if members:
            team = Team((message.author.id, self._find_user(message.author.id).name), *members)
            self._input_team_system(team)
            
            return base.DirectedMessage('Successfully created team.', message.channel)
        else:
            return base.DirectedMessage('Syntax error: Mention your desired teammates.', message.channel)
    
    
    def invite_team_option(self, message : discord.Message) -> base.DirectedMessage:
        desired_members = self._mention_strip_mass(message.content)
        team = self.teams[message.author.id] if message.author.id in self.teams else Team((message.author.id, self._find_user(message.author.id).name))
        if desired_members:
            invited = set()
            for user in desired_members:
                if self._player_on_team(user):
                    continue
                
                user_name = self._find_user(user).display_name
                invited.add(user_name)
                team.invite(user, user_name)
            self._input_team_system(team)
            
            return base.DirectedMessage('Successfully invited the following players: {}. Any players not invited are already on a team.'.format(
                                        ', '.join(user for user in invited)), message.channel)
        else:
            return base.DirectedMessage('Syntax error: Mention at least 1 person to invite.', message.channel)
    
    
    def status_team_option(self, message : discord.Message) -> base.DirectedMessage:
        if self._player_on_team(message.author.id):
            return base.DirectedMessage(str(self.teams[message.author.id]), message.channel)
        else:
            return base.DirectedMessage('You are currently not on a team.', message.channel)
    
    
    def accept_team_option(self, message : discord.Message) -> base.DirectedMessage:
        if self._player_on_team(message.author.id):
            team = self.teams[message.author.id]
            team.update(message.author.id)
            
            if team.get_acceptance():
                return base.DirectedMessage('Team is fully ready to play!', message.channel)
            else:
                return base.DirectedMessage('Successfully updated team.', message.channel)
        else:
            return base.DirectedMessage('You have not been invited to a team.')
    
    
    def leave_team_option(self, message : discord.Message) -> base.DirectedMessage:
        if self._player_on_team(message.author.id):
            team = self.teams[message.author.id]
            self._team_remove(message.author.id)
            return base.DirectedMessage('Successfully removed you from team. Current team is now...' + str(team), message.channel)
        else:
            return base.DirectedMessage('You are not in a team nor have you been invited to one.', message.channel)

    
    def ongoing_option(self, message : discord.Message) -> base.DirectedMessage:
        shown = set()
        string = '`CHALLENGES`\n'
        count = 1
        for player in self.challenges:
            challenge = self.challenges[player]
            if challenge not in shown:
                shown.add(challenge)
                string += \
'''Challenge #{count}:
        Challengers - {challengers}
        Challenged - {challenged}
        Accepted - {bool_val}\n'''.format(count = count,
                                              challengers = ', '.join(challenge.get_challenger_players_names()),
                                              challenged = ', '.join(challenge.get_challenged_players_names()),
                                              bool_val = challenge.accepted)
                count += 1
                
        return base.DirectedMessage(string, message.channel)
    
    
    _possible_messages = ('Yeah I don\'t like Antis either...',
                          'Hey no talking about Antis behind his back!',
                          'Antis hears all.')
    def antis_option(self, message : discord.Message) -> base.DirectedMessage:
        return base.DirectedMessage(random.choice(self._possible_messages), message.channel)