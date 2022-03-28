"""
Contains miscellaneous commands to be used for fun.
"""

import datetime
import random

import discord
import humanize
from discord import app_commands
from discord.ext import commands
from utils.models import TwitchBroadcast


class SlashMiscCog(commands.Cog):
    """
    🎲 Contains miscellaneous commands.
    """

    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(description="Shows information about a Twitch streamer.")
    @app_commands.describe(name="Twitch Streamer's name")
    async def twitch(self, interaction: discord.Interaction, *, name: str):
        """
        🎲 Shows information about a Twitch stream.

        Usage:
        ```
        /twitch <streamer name>
        ```
        """
        await interaction.response.defer()
        client = self.client.twitch
        name = name.lower()
        broadcaster_data = await client.connect("helix/users", login=name)
        broad_list = broadcaster_data['data']

        if broad_list:
            broadcaster_id = broad_list[0]['id']

            broadcaster_name = broad_list[0]['display_name']
            json = await client.connect('helix/streams', user_id=str(broadcaster_id))

            if not json['data']:
                return await interaction.followup.send(f"{broadcaster_name} isn't live")

            stream: TwitchBroadcast = await client.return_information(json)
            stream.thumbnail.seek(0)
            file = discord.File(fp=stream.thumbnail, filename="stream.png")

            game_cover = stream.game_image
            game_name = stream.game_name
            view_count = stream.viewer_count
            username = stream.username
            stream_title = stream.stream_title
            started_at = stream.started_at

            on_going_for = humanize.precisedelta(datetime.datetime.utcnow() - started_at, format="%0.0f")

            embed = discord.Embed(title=stream_title, timestamp=datetime.datetime.utcnow(), url=stream.stream_url)

            embed.set_image(url="attachment://stream.png")
            embed.set_thumbnail(url=game_cover)
            embed.add_field(name="Stream Time", value=on_going_for)
            embed.add_field(name="Username", value=username)
            embed.add_field(name="Viewer Count", value=view_count)
            embed.add_field(name="Category", value=game_name)

            return await interaction.followup.send(embed=embed, file=file)

        return await interaction.followup.send(f":x: {interaction.message.author}: {name} isn't a valid streamer's name")

    @app_commands.command()
    @app_commands.describe(choices="Your choices separated by spaces")
    async def choose(self, interaction: discord.Interaction, *, choices: str):
        """
        🎲 Chooses a random option from a list of choices.

        Usage:
        ```
        /choose <...choices>
        ```
        """
        await interaction.response.defer()
        choices = choices.split(' ')
        # Display some error messages if the user's input is invalid.
        # This is because it's kinda awkward to do this in the on_command_error event.
        if len(choices) < 1:
            return await interaction.followup.send(f':x: {interaction.user.mention}: You need to give me choices to choose from.')
        if len(choices) == 1:
            return await interaction.followup.send(f':x: {interaction.user.mention}: I need more than one choice!')

        embed = discord.Embed(title=f'🎲 I choose {random.choice(choices)}')
        await interaction.followup.send(embed=embed)

    @app_commands.command()
    async def meme(self, interaction: discord.Interaction):
        """
        🎲 Sends a random meme from Reddit.

        Usage:
        ```
        /meme
        ```
        """
        await interaction.response.defer()
        response = await self.client.session.get("https://meme-api.herokuapp.com/gimme")
        data = await response.json()
        meme = discord.Embed(title=str(data["title"]))
        meme.set_image(url=str(data["url"]))

        await interaction.followup.send(embed=meme)

    @app_commands.command()
    @app_commands.describe(question="The question you want to open the poll for")
    async def poll(self, interaction: discord.Interaction, *, question: str):
        """
        🎲 Creates a simple yes or no poll.

        Usage:
        ```
        /poll <question>
        ```
        """
        await interaction.response.defer()
        if not question:
            return await interaction.followup.send(f':x: {interaction.user.mention}: You need to specify a question.')

        embed = discord.Embed(
            title=f"Poll by **{interaction.user.name}**:",
            description=question
        )

        message = await interaction.followup.send(embed=embed)

        await message.add_reaction("✔️")
        await message.add_reaction("❌")


async def setup(client: commands.Bot):
    """
    Registers the cog with the client.
    """
    await client.add_cog(SlashMiscCog(client))


async def teardown(client: commands.Bot):
    """
    Un-registers the cog with the client.
    """
    await client.remove_cog(SlashMiscCog(client))
