import discord
import logging
from multiprocessing import Process
from noapiframe import docDB
from elements import DiscordGuild, DiscordRole, DiscordMember, DiscordChannel, DiscordPoll, Setting

discord_process = None
_LOGGER = logging.getLogger(__name__)


def _discord_process():
    intents = discord.Intents.default()
    intents.message_content = True
    intents.guilds = True
    intents.members = True
    intents.presences = True

    client = discord.Client(intents=intents)

    def capture_member(player):
        if not player.bot:
            member = DiscordMember({'_id': f'{player.guild.id}_{player.id}', 'name': player.name, 'guild_id': str(player.guild.id), 'role_ids': list()})

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
            _LOGGER.info(f'Captured member: {member}')

    def capture_poll(poll):
        p = DiscordPoll({
            '_id': str(poll.message.id),
            'channel_id': str(poll.message.channel.id),
            'question': poll.question,
            'options': list([a.text for a in poll.answers]),
            'active': not poll.is_finalized()})
        if poll.expires_at:
            p['till_ts'] = int(poll.expires_at.timestamp())
        p.save()
        _LOGGER.info(f'Captured poll: {p}')

    async def capture_channel_polls(channel):
        async for message in channel.history(limit=100):
            if message.poll:
                capture_poll(message.poll)

    @client.event
    async def on_ready():
        _LOGGER.info(f'We have logged in as {client.user}')
        docDB.clear('DiscordMember')
        docDB.clear('DiscordRole')
        docDB.clear('DiscordGuild')
        docDB.clear('DiscordChannel')
        docDB.clear('DiscordPoll')

        for guild in client.guilds:
            g = DiscordGuild({'_id': str(guild.id), 'name': guild.name})
            g.save()

            for role in guild.roles:
                r = DiscordRole({'_id': str(role.id), 'name': role.name, 'guild_id': str(guild.id)})
                r.save()

            for member in guild.members:
                capture_member(member)

            for channel in guild.channels:
                if isinstance(channel, discord.channel.TextChannel):
                    c = DiscordChannel({'_id': str(channel.id), 'name': channel.name, 'guild_id': str(guild.id)})
                    c.save()
                    await capture_channel_polls(channel)
        _LOGGER.info('initial loading completed')

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

        elif message.poll:
            capture_poll(message.poll)

        elif str(message.type) == 'MessageType.poll_result':
            await capture_channel_polls(message.channel)

    # on_presence_update is called when member status or member activity changes
    @client.event
    async def on_presence_update(before, after):
        capture_member(after)

    # gets called when a new channel is created
    @client.event
    async def on_guild_channel_create(channel):
        if isinstance(channel, discord.channel.TextChannel):
            c = DiscordChannel({'_id': str(channel.id), 'name': channel.name, 'guild_id': str(channel.guild.id)})
            c.save()
            _LOGGER.info(f'Channel created: {c}')

    # gets called when a channel is deleted
    @client.event
    async def on_guild_channel_delete(channel):
        c = DiscordChannel.get(str(channel.id))
        if c['_id'] is not None:
            c.delete()
            _LOGGER.info(f'Channel deleted: {channel.id}')

    client.run(Setting.value('discord_bot_token'))


def start_worker():
    global discord_process
    if Setting.value('discord_bot_token') is None:
        return

    if discord_process is None:
        discord_process = Process(target=_discord_process, args=(), daemon=True)
        discord_process.start()


def generate_mock_data():
    from datetime import datetime
    from elements import DiscordGuild, DiscordRole, DiscordMember, DiscordChannel, DiscordPoll

    guilds = [
        {'_id': '1', 'name': 'Guild1'},
        {'_id': '2', 'name': 'Guild2'},
        {'_id': '3', 'name': 'Guild3'},
    ]
    for guild in guilds:
        g = DiscordGuild(guild)
        g.save()

    roles = [
        {'_id': '1', 'guild_id': '1', 'name': 'g1role1'},
        {'_id': '2', 'guild_id': '1', 'name': 'g1role2'},
        {'_id': '3', 'guild_id': '1', 'name': 'g1role3'},
        {'_id': '4', 'guild_id': '2', 'name': 'g2role1'},
        {'_id': '5', 'guild_id': '2', 'name': 'g2role2'},
        {'_id': '6', 'guild_id': '3', 'name': 'g3role1'},
    ]
    for role in roles:
        r = DiscordRole(role)
        r.save()

    members = [
        {'_id': '1', 'guild_id': '1', 'role_ids': ['1'], 'game': 'Game1'},
        {'_id': '2', 'guild_id': '1', 'role_ids': ['1'], 'game': 'Game2'},
        {'_id': '3', 'guild_id': '1', 'role_ids': ['1'], 'game': 'Game3'},
        {'_id': '4', 'guild_id': '1', 'role_ids': ['1', '2'], 'game': 'Game2'},
        {'_id': '5', 'guild_id': '1', 'role_ids': ['1', '2'], 'game': 'Game2'},
        {'_id': '6', 'guild_id': '1', 'role_ids': ['1', '2'], 'game': 'Game3'},
        {'_id': '7', 'guild_id': '1', 'role_ids': ['1', '3'], 'game': 'Game1'},
        {'_id': '8', 'guild_id': '1', 'role_ids': ['1', '3'], 'game': 'Game2'},
        {'_id': '9', 'guild_id': '1', 'role_ids': ['1', '3'], 'game': 'Game2'},
        {'_id': '10', 'guild_id': '1', 'role_ids': ['1', '2', '3'], 'game': 'Game1'},
        {'_id': '11', 'guild_id': '2', 'role_ids': [], 'game': 'Game4'},
        {'_id': '12', 'guild_id': '2', 'role_ids': ['4'], 'game': 'Game4'},
        {'_id': '13', 'guild_id': '2', 'role_ids': ['4'], 'game': 'Game4'},
        {'_id': '14', 'guild_id': '2', 'role_ids': ['4'], 'game': 'Game5'},
        {'_id': '15', 'guild_id': '2', 'role_ids': ['4'], 'game': None},
        {'_id': '16', 'guild_id': '2', 'role_ids': ['5'], 'game': None},
        {'_id': '17', 'guild_id': '2', 'role_ids': ['5'], 'game': None},
        {'_id': '18', 'guild_id': '2', 'role_ids': ['5'], 'game': 'Game4'},
        {'_id': '19', 'guild_id': '2', 'role_ids': ['5'], 'game': 'Game5'},
        {'_id': '20', 'guild_id': '2', 'role_ids': ['4', '5'], 'game': 'Game5'},
        {'_id': '21', 'guild_id': '3', 'role_ids': [], 'game': 'Game6'},
        {'_id': '22', 'guild_id': '3', 'role_ids': [], 'game': 'Game6'},
        {'_id': '23', 'guild_id': '3', 'role_ids': [], 'game': 'Game7'},
        {'_id': '24', 'guild_id': '3', 'role_ids': [], 'game': 'Game3'},
        {'_id': '25', 'guild_id': '3', 'role_ids': [], 'game': 'Game3'},
        {'_id': '26', 'guild_id': '3', 'role_ids': ['6'], 'game': 'Game6'},
        {'_id': '27', 'guild_id': '3', 'role_ids': ['6'], 'game': 'Game7'},
        {'_id': '28', 'guild_id': '3', 'role_ids': ['6'], 'game': 'Game7'},
        {'_id': '29', 'guild_id': '3', 'role_ids': ['6'], 'game': 'Game7'},
        {'_id': '30', 'guild_id': '3', 'role_ids': ['6'], 'game': 'Game3'},
    ]
    for member in members:
        m = DiscordMember(member)
        m.save()

    channels = [
        {'_id': '1', 'guild_id': '1', 'name': 'g1c1'},
        {'_id': '2', 'guild_id': '1', 'name': 'g1c2 1poll'},
        {'_id': '3', 'guild_id': '1', 'name': 'g1c3 1poll'},
        {'_id': '4', 'guild_id': '2', 'name': 'g2c1'},
        {'_id': '5', 'guild_id': '2', 'name': 'g2c2 2polls'},
        {'_id': '6', 'guild_id': '2', 'name': 'g2c3 1inactive'},
        {'_id': '7', 'guild_id': '3', 'name': 'g3c1'},
        {'_id': '8', 'guild_id': '3', 'name': 'g3c2'},
        {'_id': '9', 'guild_id': '3', 'name': 'g3c3'},
    ]
    for channel in channels:
        c = DiscordChannel(channel)
        c.save()

    till = int(datetime.now().timestamp()) + (60 * 60)
    polls = [
        {'_id': '1', 'channel_id': '2', 'question': 'R u there?', 'options': ['yes', 'no'], 'active': True, 'till_ts': till},
        {'_id': '2', 'channel_id': '3', 'question': 'Welches Game als nächstes?',
         'options': ['UT2k4', 'CoD2', 'Battlefield 2', 'RV there yet?'], 'active': True, 'till_ts': till - 2},
        {'_id': '3', 'channel_id': '5', 'question': 'Etwas mit noch mehr Optionen',
         'options': ['Option1', 'Option2', 'Option3', 'Option4', 'Option5', 'Option6', 'Option7', 'Option8'], 'active': True, 'till_ts': None},
        {'_id': '4', 'channel_id': '5', 'question': 'Etwas mit vielen Optionen',
         'options': ['Option1', 'Option2', 'Option3', 'Option4', 'Option5', 'Option6'], 'active': True, 'till_ts': till - 4},
        {'_id': '5', 'channel_id': '6', 'question': 'Sollte nie gezeigt werden', 'options': ['ist', 'egal'], 'active': False, 'till_ts': till - (60 * 60)},
    ]
    for poll in polls:
        p = DiscordPoll(poll)
        p.save()
