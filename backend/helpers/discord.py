import discord
from multiprocessing import Process

discord_process = None


def _discord_process():
    intents = discord.Intents.default()
    intents.message_content = True

    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f'We have logged in as {client.user}')
        print('available guilds:')
        for g in client.guilds:
            print(f'  {g.name}: {g.id}')
        # TODO: initial fetch of all member activities (including dump of DB data???)

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        if message.content.startswith('$hello'):
            await message.channel.send('Hello!')

    # on_presence_update is called when member status or member activity changes
    @client.event
    async def on_presence_update(before, after):
        if not after.bot and after.guild.id == 'selected guild':  # TODO: insert guild from settings
            # TODO: optional check for member.role
            playing = dict()
            for act in after.activities:
                if act.type == 'playing':
                    playing[act.timestamps.get('start', 0)] = act.name
            if len(playing) > 0:
                current_game = playing[sorted(playing.keys(), reverse=True)[0]]
                print(f'Player {after.id} is playing {current_game}')  # TODO: save to db
            else:
                print(f'Player {after.id} is playing nothing')  # TODO: save to db

    client.run('your token here')  # TODO: insert token from settings


def start_worker():
    global discord_process
    if discord_process is None:  # also check if token is configured
        discord_process = Process(target=_discord_process, args=(), daemon=True)
        discord_process.start()
