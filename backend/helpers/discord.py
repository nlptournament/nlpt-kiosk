import discord
from multiprocessing import Process

discord_process = None


def _discord_process():
    intents = discord.Intents.default()
    intents.message_content = True
    intents.guilds = True
    intents.members = True
    intents.presences = True

    client = discord.Client(intents=intents)

    def capture_game(player):
        if not player.bot and player.guild.id == 544405246810783744:  # TODO: insert guild from settings
            # if role_filter is active, only scan players having this role
            role_filter = None  # TODO: insert role_filter from settings
            if role_filter is not None:
                for role in player.roles:
                    if role.id == role_filter:
                        break
                else:
                    return

            playing = dict()
            for act in player.activities:
                if act.type.name == 'playing':
                    playing[act.timestamps.get('start', 0)] = act.name
            if len(playing) > 0:
                current_game = playing[sorted(playing.keys(), reverse=True)[0]]
                print(f'Player {player.id} ({player.name}) is playing {current_game}')  # TODO: save to db
            else:
                print(f'Player {player.id} ({player.name}) is playing nothing')  # TODO: save to db

    @client.event
    async def on_ready():
        print(f'We have logged in as {client.user}')
        print('available guilds:')
        for g in client.guilds:  # TODO: save guilds somewhere the frontend can read them
            print(f'  {g.name}: {g.id}')
        # TODO: initial fetch of all member activities (including dump of DB data???)
        for g in client.guilds:
            if g.id == 544405246810783744:  # TODO: insert guild from settings
                print('\naavailable roles:')
                for r in g.roles:  # TODO: save roles somewhere the frontend can read them
                    print(f'  {r.name}: {r.id}')
                for m in g.members:
                    capture_game(m)
        print('\n')

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        """ TODO: make this happen only on DMs
        if message.content.startswith('/hello'):
            await message.channel.send('Hello!')
        else:
            await message.channel.send("Hi! I'm a bot collecting activities about played games, for displaying them on our Kiosk-projectors.")
        """

    # on_presence_update is called when member status or member activity changes
    @client.event
    async def on_presence_update(before, after):
        capture_game(after)

    client.run('token')  # TODO: insert token from settings


def start_worker():
    global discord_process
    if discord_process is None:  # also check if token is configured
        discord_process = Process(target=_discord_process, args=(), daemon=True)
        discord_process.start()
