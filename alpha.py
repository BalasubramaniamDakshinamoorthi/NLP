import os
import datetime
import time
import re
from slackclient import SlackClient
from DataBase import DataBase
import sys
import platform
import os.path
import json

file_dict = {}
bot_name = ''

if os.path.isfile('data_slack.json'):
    with open('data_slack.json', 'r') as f:
        file_dict  = json.load(f)
else:
    print ('Required file data_slack.json not found.')
    exit()
 
bot_name = file_dict['slackbotname']

print('botname = ' + bot_name)

'''
At start up, grab an arbitrary number of .tsv files from the command line,
and create a DataBase object from each one.  (See DataBase.py).  Then
create a Python dictionary with the bare filenames as keys and the
DataBase objects as values.
'''

db_dict = {}
cmdargs = sys.argv
cmdargs.pop(0) # Get rid of the script name, leaving only the actual arguments.
print(str(cmdargs))
for arg in cmdargs:
    if arg.endswith('.tsv'):
       bare_filename = arg[:-4]
    elif arg.endswith('.csv'):
       bare_filename = arg[:-4]
    elif arg.endswith('.xlsx'):
       bare_filename = arg[:-5]
    else:
       print('Invalid filetype.')
       exit()
    bare_filename = re.sub('.*/', '', bare_filename)
    print('barefile = ' + bare_filename)
    db = DataBase(arg)
    db_dict[bare_filename] = db 
    print('arg = ' + arg)

print('db_dict = ' + str(db_dict))

# instantiate Slack client
slack_client = SlackClient(os.environ.get('ALPHA_TOKEN'))
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

for key in db_dict.keys():  # Diagnostic code
    print('key = ' + key)

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "do"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"]
    return None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    print("message text = " + message_text, flush=True)
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "Not sure what you mean. Try *{}*.".format(EXAMPLE_COMMAND)

    # Finds and executes the given command, filling in response
    response = None
    # This is where you start to implement more commands!
    # if command.startswith(EXAMPLE_COMMAND):
    # response = "Sure...write some more code then I can do that!"
    # response = db.lookup(command)

    '''
    Check if one of the keys (bare filenames) appears in the command.
    If it does, call the lookup method of the DataBase associated with
    that command.
    '''

    if command.startswith(bot_name):

        command.replace(bot_name + ' ', '')

    else:

        return

    found = False
    random_key = ""
    for key in db_dict.keys():
        random_key = key
        if key in command:
            response = db_dict[key].lookup(command)
            found = True
            break
    '''
    The keyword "sh" has special handling.  It's not associated with
    a DataBase.  Instead it just means run a particular shell script.
    '''

    if not found:
        if 'sh' in command:
            response = db_dict[random_key].lookup(command)
        else:
            response = "Query must contain a valid keyword."

    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )
    print(response, flush=True)

'''
Code to start up the server.  Mainly boilerplate code from the
api.slack.com website.
'''

if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Python " + platform.python_version(), flush=True)
        print("Establishing secure connection to Slack Web API...", flush=True)
        print("HTH Bot connected and running!", flush=True)

        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        print(str(starterbot_id), flush=True)
        while True:
            try:
                print(str(datetime.datetime.now()))
                sys.stderr.flush()
                sys.stdout.flush()
                sr = slack_client.rtm_read()
                sys.stderr.flush()
                sys.stdout.flush()
                print(str(sr))
                command, channel = parse_bot_commands(sr)
            except:
                print("Attempting to re-start server...", flush=True)
                sys.stderr.flush()
                sys.stdout.flush()
                slack_client.rtm_connect(with_team_state=False)
                starterbot_id = slack_client.api_call("auth.test")["user_id"]
                command, channel = parse_bot_commands(slack_client.rtm_read())

            if command != None:
                print(command, flush=True)
            if channel != None:
                print(channel, flush=True)
            if command:
                handle_command(command, channel)

            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.", flush=True)

