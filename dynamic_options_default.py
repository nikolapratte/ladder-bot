################################################################################
'''All essential options must be filled out properly for the bot to work.'''
ESSENTIAL_OPTIONS  = {
    'token': ''
}
################################################################################
################################################################################
################################################################################
'''Dynamic Options change how the bot functions (numbers or description wise).'''
'''Notes:
        - if python breaks after changing an option, you may want to look into
        python data types (strings, lists, integers, dictionaries [which is what DYNAMIC_OPTIONS is])
        to debug your code
        - command_symbol is sometimes used in regex match strings.
            Therefore, don't use $, ^, or other significant regex symbols.
        - Ask Antis if you have any questions.
'''
DYNAMIC_OPTIONS = {
    'version': '2.2.2',
    
    'num_top_leaderboard': 10,
    
    'about_text': \
'''Server specific about text has not been filled out.''',

    'rules_text': \
'''1. Be respectful.''',

    'base_rating_change': 25,
    
    'prediction_difference': 25,
    
    'starting_rating': 2000,
    
    'separate_1v1_mmr': False,
    
    'enforce_equal_size_teams': False,
    
    'command_symbol': '!'
}