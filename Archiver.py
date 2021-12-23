from discord.ext import tasks, commands
from discord import Embed
import datetime
import bisect
from collections import defaultdict
from pickle import load, dump
from tabulate import tabulate
import re
from pytz import timezone, utc


def helper_double_zero_tuple():
    return 0, 0


async def last_human_msg_in_timelaps(timelaps, channel, limit=65):
    start_date = datetime.datetime.utcnow() - timelaps
    async_last_messages = channel.history(after=start_date, limit=limit).filter(lambda msg: not msg.author.bot)
    return await async_last_messages.flatten()


class MyClient(commands.Bot):
    ###########################################################################################
    # Start up
    ###########################################################################################
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Start the task to run in the background
        self.main_task.start()

        # Archive parameters
        self.archive_guild_watchlist = "Bot Playground"#, "PERF' Innovation"
        self.archive = {}  # Will be completed in before_archiver
        self.time_before_warning = datetime.timedelta(days=7)
        self.time_before_archive = datetime.timedelta(days=8)

        # Unarchive parameters
        self.unarchive_guild_watchlist = "Bot Playground"#, "PERF' Innovation"
        self.new_idea = {}  # Will be completed in before_archiver
        self.unarchive_timelaps = datetime.timedelta(days=3)
        self.unarchive_nb_users = 2

        # Activity tracker parameters
        self.activity_guild_watchlist = "Bot Playground"#, "PERF' Innovation"
        self.activity_timelaps = datetime.timedelta(days=3)
        self.activity_threshold = 3, 15, 45  # Based on Perf standard on 3 days

        # Report state of server
        self.report_guild_watchlist = "Bot Playground"#, "PERF' Innovation", "PERF' Historique"
        self.inventory_msg = {}

        # Highlight to channels
        self.highligh_new_watchlist = "Bot Playground"#, "PERF' Innovation"
        self.new_timelaps = datetime.timedelta(days=3)

        # Winrates loading
        try:
            with open('winrates.pkl', 'rb') as winrate_file:
                self.winrates = load(winrate_file)
        except FileNotFoundError:
            self.winrates = defaultdict(helper_double_zero_tuple)
            open('winrates.pkl', 'x').close()

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

        # Find Archive category
        print('Looking for the "Archives" and "Nouvelles idees" section')
        print('------')
        for guild in self.guilds:
            for channel in guild.channels:
                if 'archive' in channel.name.lower():
                    self.archive[guild] = channel
                    print(f'The archive section is {channel} in guild {guild}')
                elif 'nouvelles idees' in channel.name.lower() or 'labo' in channel.name.lower():
                    self.new_idea[guild] = channel
                    print(f'The new idea section is {channel} in guild {guild}')
        print('------')

    ###########################################################################################
    # Update colored channel list
    ###########################################################################################
    @tasks.loop(minutes=3)
    async def main_task(self):
        for guild in self.guilds:
            print(f'Start main task in {guild}')
            print('------')
            colored_channels = []
            for channel in guild.channels:
                if 'color' in str(channel.category).lower() or '2022' in str(channel.category).lower():
                    colored_channels.append(channel)
            colored_channels.sort(key=lambda channel: channel.name)
            print(f'The colored channels in {guild} are {[channel.name for channel in colored_channels]}')
            print('------')

            # Call the sub tasks
            if str(guild) in self.activity_guild_watchlist:
                await self.activity_tracker(colored_channels)
            if str(guild) in self.archive_guild_watchlist:
                await self.archiver(colored_channels, self.archive[guild])
            if str(guild) in self.unarchive_guild_watchlist:
                await self.unarchiver(self.archive[guild], self.new_idea[guild])
            if str(guild) in self.report_guild_watchlist:
                await self.deck_inventory(colored_channels)
            if str(guild) in self.highligh_new_watchlist:
                await self.highlight_new(colored_channels)

    @main_task.before_loop
    async def before_main_task(self):
        await self.wait_until_ready()  # wait until the bot logs in

    ###########################################################################################
    # Activity tracker
    ###########################################################################################
    async def activity_tracker(self, colored_channels):
        print('Start activity analysis')
        print('------')
        for channel in colored_channels:
            last_messages = await last_human_msg_in_timelaps(self.activity_timelaps, channel)
            activity_markers = '⚡' * bisect.bisect(self.activity_threshold, len(last_messages))
            print(f'Adding "{activity_markers}" to the channel {channel}')
            await channel.edit(name=channel.name.replace('⚡', '') + activity_markers)
        print('------')

    ###########################################################################################
    # Highlight new channels
    ###########################################################################################
    async def highlight_new(self, colored_channels):
        print('Start highlighting the new channels')
        print('------')
        for channel in colored_channels:
            async for first_message in channel.history(limit=1, oldest_first=True):
                if datetime.datetime.utcnow() - first_message.created_at < self.new_timelaps:
                    print(f'Adding the new flag "🆕" to the channel {channel}')
                    await channel.edit(name='🆕' + channel.name.replace('🆕', ''))
                elif '🆕' in channel.name:
                    print(f'Removing the new flag "🆕" to the channel {channel}')
                    await channel.edit(name=channel.name.replace('🆕', ''))

        print('------')

    ###########################################################################################
    # Archiver
    ###########################################################################################
    async def archiver(self, colored_channels, archive):
        print('Start archive analysis')
        print('------')
        for channel in colored_channels:
            # Find time since last message
            last_two_msg = await channel.history(limit=2).flatten()
            last_non_me_msg = last_two_msg[0] if last_two_msg[0].author != client.user else last_two_msg[1]
            time_since_last_message = datetime.datetime.utcnow() - last_non_me_msg.created_at
            print(f'Last mesage in {channel} was {time_since_last_message} ago.')

            # Archive
            if time_since_last_message > self.time_before_archive:
                await channel.move(category=archive, beginning=True)
                print(f'{channel} is archived.')

            # Warning
            elif time_since_last_message > self.time_before_warning and last_two_msg[0].author != client.user:
                time_remaining = self.time_before_archive - self.time_before_warning
                await channel.send(f"J'archiverai le canal dans {time_remaining.days} jour(s) sans nouvelle activité.")
                print(f'{channel} is warned.')
        print('------')

    ###########################################################################################
    # Unarchiver
    ###########################################################################################
    async def unarchiver(self, archive, new_idea):
        print('Start unarchive analysis')
        print('------')
        for channel in archive.channels:
            last_messages = await last_human_msg_in_timelaps(self.unarchive_timelaps, channel)
            if len({msg.author for msg in last_messages}) >= self.unarchive_nb_users and 'ARCHIVE' not in last_messages[-1].content:
                await channel.move(category=new_idea, beginning=True)
                await channel.send(f'Je désarchive le canal.')
                print(f'{channel} is unarchived.')
        print('------')

    ###########################################################################################
    # Report state of server
    ###########################################################################################
    async def deck_inventory(self, colored_channels):
        histo_colored_channel = [channel for channel in colored_channels
                                 if 'histo' in channel.category.name.lower() or 'histo' in channel.guild.name.lower()]
        std_colored_channel = [channel for channel in colored_channels
                                 if 'std' in channel.category.name.lower()]
        alchemy_colored_channel = [channel for channel in colored_channels
                                 if 'alchemy' in channel.category.name.lower()]
        std22_colored_channel = [channel for channel in colored_channels
                                 if '2022' in channel.category.name.lower()]
        for channels, str_format in ((std_colored_channel, '**Standard**'),
                                     (histo_colored_channel, '**Historique**'),
                                     (alchemy_colored_channel, '**Alchemy**'),
                                     (std22_colored_channel, '**Standard 2022**')):
            if channels:
                winrates = (f'{self.winrates[channel.id, channel.guild.id][0] / sum(self.winrates[channel.id, channel.guild.id]):.0%}'
                            if sum(self.winrates[channel.id, channel.guild.id]) != 0 else 'A tester !'
                            for channel in channels)
                content = ((channel.name.replace('⚡', ''),
                            re.sub('[^⚡]', '', channel.name),
                            self.winrates[channel.id, channel.guild.id],
                            winrate)
                        for channel, winrate in zip(channels, winrates))
                table = tabulate(content, ('Deck', 'Activité', '(Win, Lose)', 'Winrate'), 'github')
                to_print = str_format + " ("
                to_print += datetime.datetime.now(tz=utc).astimezone(timezone('Europe/Paris')).strftime('%d/%m/%y %H:%M')
                to_print += ")\n\n```\n" + table + "\n```"
                try:
                    await self.inventory_msg[colored_channels[0].guild, str_format].edit(content=to_print)
                except KeyError:
                    for channel in colored_channels[0].guild.channels:
                        if 'inventaire' in channel.name.lower():
                            self.inventory_msg[colored_channels[0].guild, str_format] = await channel.send(to_print)


###########################################################################################
# Add the bot winrate-related commands
###########################################################################################
client = MyClient('%', case_insensitive=True)


def result_message(ctx):
    actual_wins, actual_loses = client.winrates[ctx.channel.id, ctx.guild.id]
    total_matchs = actual_wins + actual_loses
    print(f'Notifying {ctx.channel} that the recorded score is {client.winrates[ctx.channel.id, ctx.guild.id]}')
    if total_matchs == 0:
        return "Je ne connais aucun résultat pour ce deck."
    else:
        return f"""Il y a eu {total_matchs} partie(s) jouée(s) avec ce deck. Le score total est de {actual_wins}-{actual_loses} soit un winrate de {actual_wins / total_matchs:.0%}."""


async def set_winrates(ctx, modif_type, new_wins, new_loses):
    # Update the winrates
    client.winrates[ctx.channel.id, ctx.guild.id] = new_wins, new_loses

    # Send the answer and delete the user message
    async for message in ctx.history(limit=1):
        await message.delete()
    await ctx.send(f"La {modif_type} a bien été enregistrée. Merci :)", delete_after=10.0)
    await ctx.send(result_message(ctx), delete_after=10.0)
    await ctx.send("Ce message s'auto-détruira dans 10s pour éviter de remplir le salon.", delete_after=10.0)

    # Update the backup file
    with open('winrates.pkl', 'wb') as winrate_file:
        dump(client.winrates, winrate_file)


@client.command()
async def score(ctx, wins, loses):
    """*%score NbrVictoires NbrDéfaites* Pour soumettre des résultats de Bo3."""
    actual_wins, actual_loses = client.winrates[ctx.channel.id, ctx.guild.id]
    await set_winrates(ctx, 'session', actual_wins + int(wins), actual_loses + int(loses))
    print(f'Updating the record for {ctx.channel}. New record is {client.winrates[ctx.channel.id, ctx.guild.id]}')


@client.command()
@commands.has_role('Planeswalkers')
async def correct(ctx, wins, loses):
    """*%correct NbrVictoires NbrDéfaites* Pour corriger les résultats (Planeswalkers seulement)."""
    await set_winrates(ctx, 'correction', int(wins), int(loses))
    print(f'Correcting the record for {ctx.channel}. New record is {client.winrates[ctx.channel.id, ctx.guild.id]}')


@client.command()
async def winrate(ctx):
    """Résume les winrates pour ce salon."""
    await ctx.send(result_message(ctx))
    print(f'Providing the winrate {client.winrates[ctx.channel.id, ctx.guild.id]} to {ctx.channel}')



@client.command()
@commands.has_role('Planeswalkers')
async def move(ctx, channel_id):
    """Déplace les messages du salon spécifié en argument là ou la commande est appellée."""
    channel = client.get_channel(int(channel_id))
    print(f'Moving the messages from {channel.name} in {channel.guild.name} to {ctx.channel.name} in {ctx.guild.name}')
    async for msg_to_move in channel.history(limit=None, oldest_first=True):
        message_date = msg_to_move.created_at.astimezone(timezone('Europe/Paris')).strftime('%d/%m/%y %H:%M')
        embed = Embed(description=msg_to_move.content)
        embed.set_author(name=msg_to_move.author.display_name,
                         icon_url=msg_to_move.author.avatar_url)
        embed.add_field(name='Provenance',
                        value=f'Message du {message_date} déplacé depuis {channel.guild.name}')
        await ctx.send(embed=embed)


###########################################################################################
# Launch the bot
###########################################################################################
client.run('ODM5MDU1MjAzOTExMDczODgz.YJEFDQ.7Sto2HkesOuhZ50rgCSC7K8puTY')
