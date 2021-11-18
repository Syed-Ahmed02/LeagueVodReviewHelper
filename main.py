import os
import time
import webbrowser
import json
from lcu_driver import Connector

connector = Connector()


def get_data_from_json(data_type):

    with open("config.json") as json_data_file:
        data = json.load(json_data_file)

        data_returned = data[data_type]

    return data_returned


def execute_script():

    league_path = get_data_from_json("league_path")

    chrome_path = get_data_from_json("chrome_path")

    websites = get_data_from_json("websites")

    wait_time = get_data_from_json("wait_time")

    try:
        os.system('TASKKILL /F /IM LeagueClient.exe') #closes league

    except:
        print("Failed to close league") #incase league didn't close

    if chrome_path != "" and len(websites) != 0:

        try:

            for i in range(len(websites)):
                webbrowser.register('chrome',
                                    None,
                                    webbrowser.BackgroundBrowser(
                                        chrome_path))
                webbrowser.get('chrome').open(websites[i])
        except:
            pass

    i = 0

    while i < wait_time:

        if i % 60 == 0:

            print(f"{(wait_time - i)} seconds remaining till league automatically launches")

        time.sleep(1)

        i += 1

    try:

        os.startfile(league_path)

    except:

        pass


@connector.ready
async def connect(connector):

    print("Script started")

    closedisc = get_data_from_json("close_discord")

    if (closedisc is True):
        try:
            os.system('TASKKILL /F /IM Discord.exe')
        except:
            print("Failed to close discord")


@connector.ws.register('/lol-honor-v2/v1/ballot', event_types=('UPDATE', 'CREATE', 'DELETE'))
async def voted(connection, event):
    # check if the client just launches
    # all code in the league client executes when the client launches, however requesting summoner data during this time returns
    # error 404 which is different from when honoring finishes
    summoner = await connection.request('get',
                                        '/lol-summoner/v1/current-summoner')  # get summoner info, being used to
    if event.data is None and summoner.status != 404:
        response = await connection.request('post', '/lol-end-of-game/v1/state/dismiss-stats')  # skips the end of game
        execute_script()  # executes main script


@connector.ws.register('/lol-ranked/v1/notifications')
async def ranked_notification(connection, event):  # this function only works when you rank up a division
    if event.data is not None:
        if isinstance(event.data, list) and len(event.data) > 0:
            await connection.request('post', f'/lol-ranked/v1/notifications/{event.data[0]}/acknowledge')
            execute_script()


connector.start()
