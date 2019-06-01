import re
import discord

WIN = 1
LOSS = -1 #important for these to stay the same, see mmr_calculator function


class DirectedMessage():
    """Used to create a message-channel combination.
        If want to send to a user's DM channel, make channel
        equal to the user's user object."""
    def __init__(self, message, channel):
        self.message = message
        self.channel = channel


class Team():
    """Represents a team."""
    def __init__(self, first : [int, str],*args : (int, str)):
        self._members = {p_id:[False, name] for p_id, name in args}
        self._members[first[0]] = [True, first[1]]

    def __bool__(self):
        return len(self._members) >= 2
    
    def __str__(self):
        if self.get_acceptance():
            return 'Team is fully ready to play! Players are:' + '\n' + '\n'.join(name for _, name in self._members.values())
        
        string = 'Status:\n' 
        for bool_val, name in sorted(self._members.values(), key = lambda x: x[1].lower()):
            string += f'{name} is ready.' if bool_val else f'{name} has not accepted the team invitation.'
            string += '\n'
        
        return string
    
    def __contains__(self, item):
        return item in self._members
    
    def __eq__(self, other):
        return set(self._members.keys()) == set(other._members.keys())
    
    def __len__(self):
        return len(self._members)
    
    def get_players(self) -> [int]:
        return list(self._members)
    
    def get_players_names(self) -> [str]:
        return [member[1] for member in sorted(self._members.values(), key = lambda x: x[1].lower())]
    
    def get_acceptance(self) -> bool:
        return all(bool_val for bool_val, _ in self._members.values())
    
    def get_members_dict(self) -> dict:
        return self._members
    
    def invite(self, p_id : int, name : str) -> None:
        self._members[p_id] = [False, name]
    
    def update(self, p_id : int) -> None:
        self._members[p_id][0] = True
        
    def remove(self, p_id : int) -> None:
        del self._members[p_id]
        

def other_player(players : (int, int), player : int):
    return players[1 - players.index(player)]


def mmr_calculator(base_rating_change : int, prediction_difference : int,
                   player1mmr : int, player2mmr : int, match_sets : (WIN or LOSS, int)):
    p1wins = p2wins = 0
    for outcome, amount in match_sets:
        if outcome == WIN:
            p1wins += amount
        else:
            p2wins += amount
        
        for _ in range(amount):
            
            rating_difference = abs(player1mmr - player2mmr)//prediction_difference
            
            if rating_difference > base_rating_change: rating_difference = base_rating_change #make sure there isn't negative mmr change
            
            player_favored = 1 if player1mmr >= player2mmr else -1
            
            mmr_change = (base_rating_change + rating_difference * player_favored * -outcome) + 1
        
            player1mmr += mmr_change * outcome
            player2mmr += mmr_change * -outcome
    
    return (player1mmr, player2mmr, p1wins, p2wins)
            

class BaseCommands():
    """Contains base commands that are useful in general."""
    def _find_user(self, identity):
        """Input: id of user.
        Output: user's model."""
        if identity:
            for user in self.client.users:
                if user.id == int(identity):
                    return user


    def find_user_with_name(self, name):
        #need name of user as input, tries to find them
        for user in self.client.users:
            try:
                if user.name.lower() == name.lower():
                    return user
            except UnicodeEncodeError:
                continue

            
    def find_channel(self, identity):
        #need id of channel as input, outputs the channel model
        for guild in self.client.guilds:
            for channel in guild.channels:
                if channel.id == identity:
                    return channel

                
    def _mention_strip(self, mention):
        mention = mention.strip()
        match = re.search('[0-9]+', mention)
        if match:
            return int(mention[match.start():match.end()])
        raise ValueError('Message contained no mentions.')
    
    
    def _mention_strip_mass(self, message : str) -> [int]:
        return [int(num) for num in re.findall('[0-9]+', message)]


    def _has_account(self, user_id: int) -> bool:
        """Returns whether or not a player has an account in player_stats."""
        if user_id in self.player_stats:
            return True
        return False


    def _invalid_user_input(self,
                            error_message: str,
                            message: discord.Message) -> (DirectedMessage):
        """Gives the user feedback on what they did wrong."""
        return (DirectedMessage(error_message, message.channel),)
    
    
    def _get_player_team(self, p_id : int) -> Team:
        return self.teams[p_id] if p_id in self.teams else\
             Team((p_id, self._find_user(p_id).name))
    
