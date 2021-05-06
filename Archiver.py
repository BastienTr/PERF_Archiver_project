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
        self.archiver.start()
        self.activity_tracker.start()

        # Archive parameters
        self.time_before_warning = datetime.timedelta(minutes=1)
        self.time_before_archive = datetime.timedelta(minutes=3)
        self.channel_watch_list = 'Mono-color', 'Bi-color', 'Tri-color'

        # Activity tracker parameters
        self.activity_timelaps = datetime.timedelta(minutes=10)
        self.activity_threshold = 3, 15, 45  # Based on Perf standard on 3 days

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

        # Find colored channel
        self.colored_channels = []
        for guild in self.guilds:
            for channel in guild.channels:
                if str(channel.category) in self.channel_watch_list:
                    self.colored_channels.append(channel)

    ###########################################################################################
    # Activity tracker
    ###########################################################################################
    @tasks.loop(seconds=60)  # task runs every 60 seconds
    async def activity_tracker(self):
        for channel in self.colored_channels:
            start_date = datetime.datetime.utcnow() - self.activity_timelaps
            async_last_messages = channel.history(after=start_date, limit=65).filter(lambda msg: not msg.author.bot)
            last_messages = await async_last_messages.flatten()
            activity_markers = '⚡' * bisect.bisect(self.activity_threshold, len(last_messages))
            await channel.edit(name=activity_markers + channel.name.replace('⚡', ''))

    @activity_tracker.before_loop
    async def before_archiver(self):
        await self.wait_until_ready()  # wait until the bot logs in

    ###########################################################################################
    # Archiver
    ###########################################################################################
    @tasks.loop(seconds=60)  # task runs every 60 seconds
    async def archiver(self):
        for channel in self.colored_channels:
            # Find time since last message
            last_two_msg = await channel.history(limit=2).flatten()
            last_human_msg = last_two_msg[0] if last_two_msg[0].author != client.user else last_two_msg[1]
            time_since_last_message = datetime.datetime.utcnow() - last_human_msg.created_at

            # Archive
            if time_since_last_message > self.time_before_archive:
                await channel.move(category=self.archive, beginning=True)

            # Warning
            elif time_since_last_message > self.time_before_warning and last_two_msg[0].author != client.user:
                await channel.send(f'Ce canal sera archivé dans {self.time_before_archive - self.time_before_warning} sans nouvelle activité.')

    @archiver.before_loop
    async def before_archiver(self):
        await self.wait_until_ready()  # wait until the bot logs in

        # Find Archive category
        for guild in self.guilds:
            for channel in guild.channels:
                if channel.name == 'Archive':
                    self.archive = channel


client = MyClient()
client.run('ODM5MDU1MjAzOTExMDczODgz.YJEFDQ.BTZ0Et3FASxMteP0E6VEurHYzh4')
