import discord
from discord.ext import commands

class Game:
    def __init__(self, host, name):
        self.host = host
        self.name = name
        self.players = [host]
        self.alive = []
        self.dead = []
        self.active = False

    def add(self, player):
        self.players.append(player)


class AmongUs(commands.Cog):
    alive_id = 756213706379100310
    dead_id = 756213764877058241
    guild_id = 756213043771342928

    def __init__(self, bot):
        self.bot = bot
        self.current_game = None

    @commands.Cog.listener()
    async def on_ready(self):
        print("Connected!")

    @commands.guild_only()
    @commands.command()
    async def create(self, ctx, *name):
        """
        Creates a game
        """
        if self.current_game:
            await ctx.send("A game is already in progress")

        elif not name:
            await ctx.send("Game code must be provided")

        else:
            game_name = '_'.join(name)
            self.current_game = Game(ctx.author, game_name)

            await ctx.send(f"Created new game: {game_name}\nType \".join\" to join.")

    @commands.guild_only()
    @commands.command()
    async def join(self, ctx):
        """
        Joins the current game
        """
        if not self.current_game:
            await ctx.send("No game active. You can start a game with \".create game_name\"")

        elif ctx.author in self.current_game.players:
            await ctx.send("You are already in this game")

        elif self.current_game.active:
            await ctx.send("This game is already in progress!")

        else:
            self.current_game.add(ctx.author)
            await ctx.send(f"You have joined game {self.current_game.name}")

    @commands.guild_only()
    @commands.command()
    async def start(self, ctx):
        """
        Starts the current game if sender is host
        """
        if not self.current_game:
            await ctx.send("No game active. You can start a game with \".create game_name\"")

        elif ctx.author != self.current_game.host:
            await ctx.send("You are not the host")

        else:
            self.current_game.active = True
            await ctx.send("Game has started")

            for user in self.current_game.players:
                self.current_game.alive = self.current_game.players.copy()
                await user.add_roles(ctx.guild.get_role(AmongUs.alive_id))
            return

    @commands.command()
    async def dead(self, ctx):
        """
        DM me this when you die
        """
        if not self.current_game:
            await ctx.send("No game active. You can start a game with \".create game_name\"")

        elif ctx.author not in self.current_game.players:
            await ctx.send("You are not in this game")

        elif ctx.author in self.current_game.dead:
            await ctx.send("You are already dead")

        elif not self.current_game.active:
            await ctx.send("This game hasn't started yet")

        else:
            if ctx.guild:
                await ctx.message.delete()

            guild = self.bot.get_guild(AmongUs.guild_id)
            for user in self.current_game.players:
                if user.id == ctx.author.id:
                    author = user

            await author.remove_roles(guild.get_role(AmongUs.alive_id))
            self.current_game.alive.remove(author)

            await author.add_roles(guild.get_role(AmongUs.dead_id))
            self.current_game.dead.append(author)


    @commands.guild_only()
    @commands.command()
    async def leave(self, ctx):
        """
        Sender leaves the game
        """
        if not self.current_game:
            await ctx.send("No game active. You can start a game with \".create game_name\"")

        elif ctx.author not in self.current_game.players:
            await ctx.send("You are not in this game")

        elif ctx.author == self.current_game.host:
            await ctx.send("The host can't leave the game")

        else:
            if self.current_game.active:
                if ctx.author in self.current_game.alive:
                    self.current_game.alive.remove(ctx.author)
                    await ctx.author.remove_roles(ctx.guild.get_role(AmongUs.alive_id))

                else:
                    await ctx.author.remove_roles(ctx.guild.get_role(AmongUs.dead_id))
                    self.current_game.dead.remove(ctx.author)

            self.current_game.players.remove(ctx.author)

    @commands.guild_only()
    @commands.command()
    async def end(self, ctx):
        """
        Ends the current game if sender is host
        """
        if not self.current_game:
            await ctx.send("No game active. You can start a game with \".create game_name\"")

        elif ctx.author != self.current_game.host:
            await ctx.send("Only the host can end the game")

        else:
            for user in self.current_game.players:
                await user.remove_roles(ctx.guild.get_role(AmongUs.alive_id))
                await user.remove_roles(ctx.guild.get_role(AmongUs.dead_id))

            self.current_game = None
            await ctx.send("Game has been ended")

    @commands.guild_only()
    @commands.command()
    async def round(self, ctx):
        """
        Moves the game onto the next round if sender is host
        """
        if not self.current_game:
            await ctx.send("No game active. You can start a game with \".create game_name\"")

        elif ctx.author != self.current_game.host:
            await ctx.send("Only the host can start a new round")

        elif not self.current_game.active:
            await ctx.send("This command can only be used when the game is in progress")

        else:
            self.current_game.active = False
            for user in self.current_game.players:
                await user.remove_roles(ctx.guild.get_role(AmongUs.alive_id))
                await user.remove_roles(ctx.guild.get_role(AmongUs.dead_id))

            self.current_game.dead = []
            self.current_game.alive = []

    @commands.command()
    async def game(self, ctx):
        """
        Lists details about the current game
        """
        if not self.current_game:
            await ctx.send("No game active. You can start a game with \".create GAME_CODE\"")

        else:
            info = f"**Game Code:** {self.current_game.name}\n**Host:** {self.current_game.host.name}\n**Players:**\n"
            for player in self.current_game.players:
                info += player.name + '\n'

            if self.current_game.active:
                info += "Currently active"
            else:
                info += "Currently inactive"

            await ctx.send(info)

    @commands.command()
    async def code(self, ctx):
        """
        Provides only the game code
        """
        if not self.current_game:
            await ctx.send("No game active. You can start a game with \".create GAME_CODE\"")

        else:
            await ctx.send(self.current_game.name)



    @commands.command()
    async def roles(self, ctx):
        """
        Utility command only for me
        """
        print(ctx.guild.roles)

bot = commands.Bot(command_prefix='.')
bot.add_cog(AmongUs(bot))



with open("token.txt") as token_file:
    token = token_file.read()
bot.run(token)
