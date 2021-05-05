from discord.ext import tasks
import discord
import datetime


class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # start the task to run in the background
        self.archiver.start()

        # archive parameters
        self.time_before_warning = datetime.timedelta(minutes=1)
        self.time_before_archive = datetime.timedelta(minutes=3)
        self.channel_watch_list = 'Mono', 'Bi', 'Tri'

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    @tasks.loop(seconds=60)  # task runs every 60 seconds
    async def archiver(self):
        for guild in self.guilds:
            for channel in guild.channels:
                if str(channel.category) in self.channel_watch_list:
                    # Find time since last message
                    last_two_msg = await channel.history(limit=2).flatten()
                    last_human_msg = last_two_msg[0] if not last_two_msg[0].author.bot else last_two_msg[1]
                    time_since_last_message = datetime.datetime.utcnow() - last_human_msg.created_at

                    # Archive
                    if time_since_last_message > self.time_before_archive:
                        await channel.move(category=self.archive, beginning=True)

                    # Warning
                    elif time_since_last_message > self.time_before_warning and not last_two_msg[0].author.bot:
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
