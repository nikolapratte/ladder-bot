import pickle

import discord

from  ladder_manager_commands import match_command
import ladder_manager_base as base
from ladder_manager_information import InformationCommands
from ladder_manager_challenges import ChallengeCommands
from dynamic_options import DYNAMIC_OPTIONS, ESSENTIAL_OPTIONS

client = discord.Client()
################################################################################
################################################################################
################################################################################
'''
Player_stats dictionary description:
self.player_stats = {user_id: {'rating': int,
                            'wins': int,
                            'losses': int,
                            'records': {user_id: {'wins': int,
                                                  'losses': int}
                                        ...}
                        }
                ...
            }
'''

class LadderManager(InformationCommands,
                    base.BaseCommands,
                    ChallengeCommands):
    """Inherits all ladder commands and functions, holds several key
       global variables."""
    def __init__(self, client : 'discord.Client()'):
        """Loads client and player stats."""
        self.client = client
        self.player_stats = {} #used if first time
        self._archived_player_stats = {} #used if first time
        self.player_stats_1v1 = {} #used if first time
        self._archived_player_stats_1v1 = {} #used if first time
        
        self.teams = {}
        self.challenges = {}
        
        self.dynamic_options = DYNAMIC_OPTIONS
        self.version = self.dynamic_options['version']
        try:
            with open('laddermanager.pkl', 'rb') as saveFile:
                    self.player_stats, self._archived_player_stats, self.player_stats_1v1, self._archived_player_stats_1v1 = pickle.load(saveFile)
        except Exception as e:
            print(
f'''Player stats could not be loaded, exception: {e}.
This should happen first time you run the bot.
If this is not your first run, try rebooting the bot.
If the problem persists contact Antis.''')
        
        try:
            with open('laddermanager_tmp.pkl', 'rb') as saveFile_tmp:
                self.teams, self.challenges = pickle.load(saveFile_tmp)
        except Exception as e:
            print(f'''Temporary data could not be loaded, exception : {e}.''')


async def send_message(message : base.DirectedMessage) -> None:
        """Sends a message to a channel.
            If channel is none, sends a message to the DM channel of the author."""
        if type(message.channel) == discord.User:
            if message.channel.dm_channel == None: await message.channel.create_dm()
            await message.channel.dm_channel.send(message.message)
        else:
            await message.channel.send(message.message)


ladder = LadderManager(client)

@ladder.client.event
async def on_ready():
    print(f"Logged in as {ladder.client.user}")
    

POSSIBLE_COMMANDS = {'help': ladder.help_option,
                         'about': ladder.about_option,
                         'leaderboard': ladder.leaderboard_option,
                         'full_leaderboard': ladder.full_leaderboard_option,
                         'stats_self': ladder.stats_self_option,
                         'stats_other': ladder.stats_other_option,
                         'record_self': ladder.record_self_option,
                         'record_other': ladder.record_other_option,
                         'rules': ladder.rules_option,
                         'ongoing': ladder.ongoing_option,
                         
                         'challenge': ladder.challenge_option,
                         'accept_challenge': ladder.accept_challenge_option,
                         'report_challenge': ladder.report_challenge_option,
                         'decline_challenge': ladder.decline_challenge_option,
                         'cancel_challenge': ladder.cancel_challenge_option,
                         
                         'create_team': ladder.create_team_option,
                         'accept_team': ladder.accept_team_option,
                         'leave_team': ladder.leave_team_option,
                         'invite_team': ladder.invite_team_option,
                         'status_team': ladder.status_team_option,
                         
                         'antis': ladder.antis_option}


#unnecessary
def _save_temporary_data(ladder : LadderManager) -> None:
    """This is kinda inefficient to do every time a command is called 
    but just trying to do a quick fix to my own issue of walking around."""
    teams = ladder.teams
    challenges = ladder.challenges
    with open('laddermanager_tmp.pkl', 'wb') as saveFile:
                pickle.dump([teams, challenges], saveFile)


@ladder.client.event
async def on_message(message):
    command = match_command(message)
    if command:
        await send_message(POSSIBLE_COMMANDS[command.command_name](message))
        _save_temporary_data(ladder)


ladder.client.run(ESSENTIAL_OPTIONS['token'])
