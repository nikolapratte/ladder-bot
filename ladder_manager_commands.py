import re

import discord

from dynamic_options import DYNAMIC_OPTIONS

class Command():
    def __init__(self, command_name, match):
        self.match = match
        self.command_name = command_name


def match_command(message: discord.Message) -> Command:
    """Matches the person's message to a specific command and returns that
    command.
    Returns None if a command could not be found."""
    message = message.content.strip().lower()
    COMMANDS = (
        Command('help',
                lambda message: \
                message == '{}help'.format(DYNAMIC_OPTIONS['command_symbol']) \
                or message == '{}h'.format(DYNAMIC_OPTIONS['command_symbol']) \
                or message == '{}commands'.format(DYNAMIC_OPTIONS['command_symbol']) \
                or message == '{}commandslist'.format(DYNAMIC_OPTIONS['command_symbol'])),
        
        Command('about',
                lambda message: message == '{}about'.format(DYNAMIC_OPTIONS['command_symbol'])),
        
        Command('rules',
                lambda message: message == '{}rules'.format(DYNAMIC_OPTIONS['command_symbol'])),

        Command('leaderboard',
                lambda message: message == '{}leaderboard'.format(DYNAMIC_OPTIONS['command_symbol'])),

        Command('full_leaderboard',
                lambda message: \
                re.match(r'{}full.leaderboard'.format(DYNAMIC_OPTIONS['command_symbol']), message) \
                or message == '{}full'.format(DYNAMIC_OPTIONS['command_symbol'])),
        
        Command('status_team',
                lambda m : m.startswith('{}status team'.format(DYNAMIC_OPTIONS['command_symbol'])) or\
                m.startswith('{}team status'.format(DYNAMIC_OPTIONS['command_symbol'])) or\
                m.startswith('{}status'.format(DYNAMIC_OPTIONS['command_symbol']))),

        Command('stats_self',
                lambda message: re.match(r'{}stats$'.format(DYNAMIC_OPTIONS['command_symbol']), message) \
                or re.match(r'{}rank$'.format(DYNAMIC_OPTIONS['command_symbol']), message) \
                or re.match(r'{}rating$'.format(DYNAMIC_OPTIONS['command_symbol']), message) \
                or re.match(r'{}status$'.format(DYNAMIC_OPTIONS['command_symbol']), message)),

        Command('stats_other',
                lambda message: message.startswith('{}stats '.format(DYNAMIC_OPTIONS['command_symbol'])) \
                or message.startswith('{}rank '.format(DYNAMIC_OPTIONS['command_symbol'])) \
                or message.startswith('{}rating '.format(DYNAMIC_OPTIONS['command_symbol'])) \
                or message.startswith('{}status '.format(DYNAMIC_OPTIONS['command_symbol']))),

        Command('record_self',
                lambda message: re.match(r'{}record$'.format(DYNAMIC_OPTIONS['command_symbol']), message)),

        Command('record_other',
                lambda message: message.startswith('{}record '.format(DYNAMIC_OPTIONS['command_symbol']))),
        
        Command('ongoing',
                lambda m : m.startswith('{}ongoing'.format(DYNAMIC_OPTIONS['command_symbol']))),
        
        Command('challenge',
                lambda message: message.startswith('{}challenge '.format(DYNAMIC_OPTIONS['command_symbol'])) \
                or message.startswith('{}play'.format(DYNAMIC_OPTIONS['command_symbol']))),
        
        Command('accept_team',
                lambda m : re.match(r'{}accept[\W_]team'.format(DYNAMIC_OPTIONS['command_symbol']), m)),
        
        Command('accept_challenge',
                lambda message: message == '{}accept'.format(DYNAMIC_OPTIONS['command_symbol'])),
        
        Command('decline_challenge',
                lambda message: message == '{}decline'.format(DYNAMIC_OPTIONS['command_symbol'])),
        
        Command('cancel_challenge',
                lambda m : m.startswith('{}cancel'.format(DYNAMIC_OPTIONS['command_symbol']))),
        
        Command('report_challenge',
                lambda message: message.startswith('{}report '.format(DYNAMIC_OPTIONS['command_symbol']))),
        
        Command('create_team',
                lambda m : m.startswith('{}create '.format(DYNAMIC_OPTIONS['command_symbol'])) or\
                m.startswith('{}create_team'.format(DYNAMIC_OPTIONS['command_symbol'])) or
                re.match(r'{}create[\W_]team'.format(DYNAMIC_OPTIONS['command_symbol']), m)),
        
        Command('invite_team',
                lambda m : m.startswith('{}invite'.format(DYNAMIC_OPTIONS['command_symbol']))),
        
        Command('leave_team',
                lambda m : m.startswith('{}leave'.format(DYNAMIC_OPTIONS['command_symbol'])) or\
                re.match(r'{}leave[\W_]team'.format(DYNAMIC_OPTIONS['command_symbol']), m)),
        
        Command('antis',
                lambda m : m.startswith(DYNAMIC_OPTIONS['command_symbol']) and 'antis' in m)
        )

    for command in COMMANDS:
        if command.match(message):
            return command
