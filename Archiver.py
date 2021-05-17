from discord.ext import tasks
import discord
import datetime
import bisect


class MyClient(discord.Client):
    ###########################################################################################
    # Start up
    ###########################################################################################
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Start the task to run in the background
        self.main_task.start()

        # Archive parameters
        self.archive = {}  # Will be completed in before_archiver
        self.time_before_warning = datetime.timedelta(days=7)
        self.time_before_archive = datetime.timedelta(days=8)
        self.channel_watch_list = 'Mono-color', 'Bi-color', 'Tri-color', '4+-color'

        # Activity tracker parameters
        self.activity_timelaps = datetime.timedelta(days=3)
        self.activity_threshold = 3, 15, 45  # Based on Perf standard on 3 days

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

        # Find Archive category
        print('Looking for the archive section')
        print('------')
        for guild in self.guilds:
            for channel in guild.channels:
                if channel.name == 'Archives':
                    self.archive[guild] = channel
        print('The archive section is', self.archive)
        print('------')

    ###########################################################################################
    # Update colored channel list
    ###########################################################################################
    @tasks.loop(hours=7)
    async def main_task(self):
        print('Looking for the colored channels')
        for guild in self.guilds:
            colored_channels = []
            for channel in guild.channels:
                if str(channel.category) in self.channel_watch_list:
                    colored_channels.append(channel)
                    print(f'The colored channels in {guild} are {(channel.names for channel in colored_channels)}')

                    # Call the sub tasks
                    await self.activity_tracker(colored_channels)
                    await self.archiver(colored_channels, self.archive[guild])

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
            start_date = datetime.datetime.utcnow() - self.activity_timelaps
            async_last_messages = channel.history(after=start_date, limit=65).filter(lambda msg: not msg.author.bot)
            last_messages = await async_last_messages.flatten()
            activity_markers = '⚡' * bisect.bisect(self.activity_threshold, len(last_messages))
            await channel.edit(name=channel.name.replace('⚡', '') + activity_markers)
            print(f'Adding "{activity_markers}" to the channel {channel}')

    ###########################################################################################
    # Archiver
    ###########################################################################################
    async def archiver(self, colored_channels, archive):
        print('Start archive analysis')
        print('------')
        for channel in colored_channels:
            # Find time since last message
            last_two_msg = await channel.history(limit=2).flatten()
            last_human_msg = last_two_msg[0] if last_two_msg[0].author != client.user else last_two_msg[1]
            time_since_last_message = datetime.datetime.utcnow() - last_human_msg.created_at
            print(f'Last mesage in {channel} was {time_since_last_message} ago.')

            # Archive
            if time_since_last_message > self.time_before_archive:
                await channel.move(category=archive, beginning=True)
                print(f'{channel} is archived.')

            # Warning
            elif time_since_last_message > self.time_before_warning and last_two_msg[0].author != client.user:
                time_remaining = self.time_before_archive - self.time_before_warning
                await channel.send(f'Ce canal sera archivé dans {time_remaining.days} jour(s) sans nouvelle activité.')
                print(f'{channel} is warned.')


client = MyClient()
client.run('ODM5MDU1MjAzOTExMDczODgz.YJEFDQ.BTZ0Et3FASxMteP0E6VEurHYzh4')
