import discord
from multiprocessing import Process
from noapiframe import docDB
from elements import DiscordGuild, DiscordRole, DiscordMember, Setting

discord_process = None


def _discord_process():
    intents = discord.Intents.default()
    intents.message_content = True
    intents.guilds = True
    intents.members = True
    intents.presences = True

    client = discord.Client(intents=intents)

    def capture_member(player):
        if not player.bot:
            member = DiscordMember({'_id': str(player.id), 'name': player.name, 'guild_id': str(player.guild.id), 'role_ids': list()})

            playing = dict()
            for act in player.activities:
                if act.type.name == 'playing':
                    playing[act.timestamps.get('start', 0)] = act.name
            if len(playing) > 0:
                current_game = playing[sorted(playing.keys(), reverse=True)[0]]
                member['game'] = current_game
            else:
                member['game'] = None

            for role in player.roles:
                if str(role.id) not in member['role_ids']:
                    member['role_ids'].append(str(role.id))

            member.save()

    @client.event
    async def on_ready():
        print(f'We have logged in as {client.user}')
        docDB.clear('DiscordMember')
        docDB.clear('DiscordRole')
        docDB.clear('DiscordGuild')

        for guild in client.guilds:
            g = DiscordGuild({'_id': str(guild.id), 'name': guild.name})
            g.save()

            for role in guild.roles:
                r = DiscordRole({'_id': str(role.id), 'name': role.name, 'guild_id': str(guild.id)})
                r.save()

            for member in guild.members:
                capture_member(member)

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        if isinstance(message.channel, discord.DMChannel):
            if message.content.startswith('debug'):
                result = list()
                for member in DiscordMember.all():
                    playing = 'nothing'
                    if member['game'] is not None:
                        playing = member['game']
                    result.append(f"{member['_id']} is playing {playing}")
                await message.channel.send('\n'.join(result))
            else:
                await message.channel.send("Hi! I'm a bot collecting activities about played games, for displaying them on our Kiosk-projectors.")

    # on_presence_update is called when member status or member activity changes
    @client.event
    async def on_presence_update(before, after):
        capture_member(after)

    client.run(Setting.value('discord_bot_token'))


def start_worker():
    global discord_process
    if Setting.value('discord_bot_token') is None:
        return

    if discord_process is None:
        discord_process = Process(target=_discord_process, args=(), daemon=True)
        discord_process.start()
