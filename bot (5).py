  
############# IMPORT MODULES ###############


import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, has_any_role
import random
from datetime import datetime
import asyncio

############ BOT SETTINGS ##############


client = commands.Bot(command_prefix='+')
client.remove_command('help')

############## VARIABLES, CLASSES AND FUNCTIONS################

def RandomColour(): return random.randint(1048576, 0xFFFFFF)


class TextCommand:
    def __init__(self, cmdName, cmdOutput):
        self.CommandPrefix = cmdName
        self.CommandOutput = cmdOutput


##################### ROOT SECTION ########################

async def get_muted_role(guild):
    muted_role = discord.utils.get(guild.roles, name='Muted')
    if muted_role is None:
        muted_permissions = discord.Permissions()
        muted_permissions.send_messages = False
        muted_permissions.add_reactions = False
        muted_role = await guild.create_role(
            name='Muted',
            permissions=muted_permissions,
            color=discord.Color.dark_red()
        )

    return muted_role


async def log(

        ctx,
        desc,
        title='**Moderation**',
        color=0xff0000,
        **kwargs
):
    guild = ctx.guild
    log_embed = discord.Embed(
        title=title,
        description=desc,
        color=color
    )
    for key, value in kwargs.items():
        if key == 'fields':
            for field in value:
                if len(field) == 2:
                    log_embed.add_field(
                        name=field[0],
                        value=field[1]
                    )
                else:
                    log_embed.add_field(
                        name=field[0],
                        value=field[1],
                        inline=field[2]
                    )
        if key == 'showauth':
            if value:
                author = ctx.author
                disp_name = author.display_name
                icon_url = author.avatar_url
                log_embed.set_author(
                    name=disp_name,
                    icon_url=icon_url
                )
                log_embed.set_thumbnail(
                    url=icon_url
                )
    now = datetime.now()
    log_embed.timestamp = now
    log_channel = discord.utils.get(guild.text_channels, name="mod-logs")
    await log_channel.send(embed=log_embed)


############################## EVENTS ###################################


@client.event
async def on_ready():
    print("Ready to go!")
    await client.change_presence(activity=discord.Game(name="Yotopihis Mod"))


############################ ALL COMMANDS #############################


################# BOT MODULE #####################

@client.command(brief=client.command_prefix + 'change_pres {g/l/s/w/n} {name here}',
                description=client.command_prefix + 'change_pres {g(Playing)/l(Listening)/s(Streaming)/w(Watching)/n(Nothing)} {name here}\n\nFor "Streaming" there has to be a link behind the name\n\n' + f'{client.command_prefix}change_pres g "Terraria"\n{client.command_prefix}change_pres l "Virtual (Blue Balenciagas)"\n{client.command_prefix}change_pres s "ASTRONEER" https://www.twitch.idk\n{client.command_prefix}change_pres w "Steel Ball Run (if only)"\n{client.command_prefix}change_pres n')
async def change_pres(ctx, *args):
    # i know this is bad code ; i wrote this at like 5am  topi || LOL - billy
    acts = ['g', 'l', 's', 'w', 'n']
    wanted_act = args[0]
    if wanted_act != acts[4]:
        wanted_subject = args[1]
    else:
        wanted_subject = ''
    if wanted_act == acts[2]:
        if len(args) >= 3:
            wanted_link = args[2]
        else:
            wanted_link = ''
    else:
        wanted_link = ''
    if wanted_act in acts:
        if wanted_act == acts[0]:
            await client.change_presence(activity=discord.Game(name=wanted_subject))
        elif wanted_act == acts[1]:
            await client.change_presence(
                activity=discord.Activity(type=discord.ActivityType.listening, name=wanted_subject))
        elif wanted_act == acts[2]:
            await client.change_presence(activity=discord.Streaming(name=wanted_subject, url=wanted_link))
        elif wanted_act == acts[3]:
            await client.change_presence(
                activity=discord.Activity(type=discord.ActivityType.watching, name=wanted_subject))
        elif wanted_act == acts[4]:
            await client.change_presence()


@client.command()
async def ping(ctx):
    """check latency"""
    result = client.latency
    embed = discord.Embed(
        title='**Pong!**',
        description=f'Current Latency is {result}',
        color=0xff0000
    )
    await ctx.send(embed=embed)


@client.command(hidden=True)
async def credits(ctx):
    description = 'Thanks to asian_nerd#1090 & billy for creating the bot'
    embed = discord.Embed(
        title='**Credits!**',
        description=f'{description}',
        color=0xff0000
    )
    await ctx.send(embed=embed)


############## MOD MODULE ##############


@client.command(name='kick', aliases=['k'])
@has_permissions(kick_members=True)
async def kick(ctx, user: discord.Member, *_):
    """Kick a user.
    Example Usage:
    <prefix>kick <user> [reason] // Kicks <user> reason```"""
    msg = ctx.message
    author = ctx.author
    try:
        reason = msg.content.split(None, 1)[1]
        found_reason = True
    except IndexError:
        found_reason = False
    if found_reason:
        await log(
            ctx,
            f'<@{author.id} kicked <@{user.id}>',
            fields=[
                ('**Reason:**', reason)
            ]
        )
        await user.kick(reason=reason)
    else:
        await client.log(
            ctx,
            f'<@{author.id}> kicked <@{user.id}>'
        )
        await user.kick()


@client.command(name='ban')
@has_permissions(ban_members=True)
async def ban(ctx, user: discord.Member, time=None, *argv):
    """Ban a user.
    Example Usage:
    <prefix>ban <user> [reason]]// Bans <user> from the guild for the reason [reason]"""
    fields = []
    guild = ctx.guild
    argv = list(argv)
    argv.insert(0, time)

    author = ctx.author
    if len(argv) > 1:  # ------------------------------------------------------------------------------------------------  Its 1 instead of 0 ; see if the ban command works without an argument now || ok :)
        reason = ' '.join(argv)
        fields.append(('**Reason:**', reason, True))

    await log(
        ctx,
        f'<@{author.id}> banned <@{user.id}>',
        fields=fields,
        showauth=True
    )
    embed = discord.Embed(
        title='**Ban**',
        description=f'<@{user.id}> has been banned.',
        color=0xff0000
    )
    await user.ban()
    await ctx.send(embed=embed)


@client.command(name='mute', aliases=['silence'])
@has_permissions(kick_members=True)
async def mute(ctx, user: discord.Member, time=None, *argv):
    """Mute a user so that they cannot send messages anymore.
    Example Usage:
    <prefix>mute <user> [reason] // Mutes <user> permanately for reason [reason]"""

    fields = []
    guild = ctx.guild
    argv = list(argv)
    argv.insert(0, time)

    author = ctx.author
    if len(argv) > 0:
        reason = ' '.join(argv)
        fields.append(
            ('**Reason:**', reason, True)
        )
    else:
        fields.append(
            ('**Reason:**', "for some reason", True)
        )

    await log(
        ctx,
        f'<@{author.id}> muted <@{user.id}>',
        fields=fields,
        showauth=True
    )
    muted_role = await get_muted_role(guild)
    await user.add_roles(muted_role)
    embed = discord.Embed(
        title='**Mute**',
        description=f'<@{user.id}> has been muted.',
        color=0xff0000
    )
    await ctx.send(embed=embed)


@client.command(name='unmute')
@has_permissions(kick_members=True)
async def unmute(ctx, user: discord.Member, *argv):
    """Unmute a user.
    Example usage:
    <prefix>unmute <user> oops wrong person // Unbans <user> for the reason oops wrong person."""
    fields = []
    guild = ctx.guild

    author = ctx.author
    try:
        reason = ' '.join(argv)
        fields.append(
            ('**Reason:**', reason, True)
        )
    except IndexError:
        pass

    await log(
        ctx,
        f'<@{author.id}> unmuted <@{user.id}>',
        fields=fields,
        showauth=True
    )
    muted_role = await get_muted_role(guild)
    await user.remove_roles(muted_role)


@client.command(name='purge')
@has_permissions(manage_messages=True)
async def purge(ctx, ammount: int, user: discord.Member = None):
    """
    Bulk delete messages in a channel.
    Example Usage:
    <prefix>purge 20 // Purges the last 20 messages in the channel
    <prefix>purge 20 @baduser#1234 // Purge the last 20 messages by @baduser#1234 in the channel."""
    channel = ctx.channel
    if ammount > 200:
        await ctx.send("You can't delete more than 200 messages at at time.")
    else:
        def check_user(message):
            return message.author == user

        msg = await ctx.send('Purging messages.')
        if user is not None:
            class count_num:
                def __init__(client):
                    client.value = 0

                def __ge__(other: int):
                    return client.value >= other

                def add(client):
                    client.value += 1
                    return client.value

            msg_number = count_num()

            def msg_check(x):

                if msg_number >= ammount:
                    return False
                if x.id != msg.id and x.author == user:
                    msg_number.add()
                    return True
                return False

            msgs = await channel.purge(
                limit=100,
                check=msg_check,
                bulk=True
            )
            await log(
                ctx,
                f"{len(msgs)} of <@{user.id}>'s messages were "
                f"deleted by <@{ctx.author.id}>",
                '**Message Purge**',
                showauth=True
            )
            # print(msg in msgs, len(msgs))
        else:

            msgs = await channel.purge(
                limit=ammount + 2,
                check=lambda x: x.id != msg.id,
                bulk=True
            )
            await log(
                ctx,
                f'{len(msgs)} messages were deleted by <@{ctx.author.id}>',
                '**Message Purge**',
                showauth=True
            )
            # print(msg in msgs)

        await msg.edit(content='Deleted messages.')
        await asyncio.sleep(2)
        await msg.delete()


@client.command(brief='Out of sight',
                description='Out of sight. Use this to erase the weird f**king jotaro h**tai you just searched up')
@has_any_role('Helper', 'Mod', 'Staff', 'Admin')
async def oos(ctx):
    await ctx.send(
        '‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎'
        '‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n'
        '‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n'
        '‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎‎\n‎\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')


@client.event
async def on_message(message):
    if not message.author.bot:
        if message.content[0] == client.command_prefix:
            wanted_command_name = message.content[1::]
            if wanted_command_name in [z.CommandPrefix for z in GlobalCommandList]:
                embed = discord.Embed(description=[a.CommandOutput for a in GlobalCommandList][
                    [b.CommandPrefix for b in GlobalCommandList].index(wanted_command_name)], color=RandomColour())
                await message.channel.send(embed=embed)
    await client.process_commands(message)


@has_permissions(manage_messages=True)
@client.command(name='command_add', aliases=['ccadd'])
async def command_add(ctx, *args):
    wanted_command_name = args[0]
    if wanted_command_name not in [command.CommandPrefix for command in GlobalCommandList]:
        # this is a bad way to do it but eh
        wanted_command_output = ''
        for x in ' '.join(args[1::]):
            if x == '\\':
                wanted_command_output += '\n'
            else:
                wanted_command_output += x
        GlobalCommandList.append(TextCommand(wanted_command_name, wanted_command_output))
        await ctx.send(
            f'Your command,`{wanted_command_name}`,with the output,`{wanted_command_output}`,has been recorded.')
    else:
        await ctx.send(
            f'Your command,`{wanted_command_name}`,already exists and has the output `{[a.CommandOutput for a in GlobalCommandList][[b.CommandPrefix for b in GlobalCommandList].index(wanted_command_name)]}`')


@has_permissions(manage_messages=True)
@client.command(name='command_get', aliases=['ccget', 'cc'])
async def command_get(ctx):
    embed = discord.Embed(title='***`Commands`***', description='\n'.join(
        [f"{x.CommandPrefix}  ::  {x.CommandOutput}" for x in GlobalCommandList]), color=RandomColour())
    await ctx.send(embed=embed)


@has_permissions(manage_messages=True)
@client.command(name='command_remove', aliases=['ccremove'])
async def command_remove(ctx, *args):
    wanted_command_name = args[0]
    if wanted_command_name in [x.CommandPrefix for x in GlobalCommandList][
        [y.CommandPrefix for y in GlobalCommandList].index(wanted_command_name)]:
        await ctx.send(
            f'Command with prefix : {[x.CommandPrefix for x in GlobalCommandList][[y.CommandPrefix for y in GlobalCommandList].index(wanted_command_name)]} and output : {[x.CommandOutput for x in GlobalCommandList][[y.CommandPrefix for y in GlobalCommandList].index(wanted_command_name)]}')
        GlobalCommandList.pop([y.CommandPrefix for y in GlobalCommandList].index(wanted_command_name))
    else:
        await ctx.send("Command not found.")


###### HELP MODULE ######


@client.command()
async def help(ctx, arg):
    author = ctx.message.author

    embed = discord.Embed(
        color=discord.Color.orange()
    )
    embed.set_author(name='Help')
    arg = str(arg)
    if arg == 'mod':
        # do stuff
        embed.add_field(name='kick', value='Kick a member from server', inline=False)
        embed.add_field(name='ban', value='ban a member from server', inline=False)
        embed.add_field(name='mute', value='mute a member', inline=False)
        embed.add_field(name='unmute', value='unmute a muted Member', inline=False)
        embed.add_field(name='purge', value='bulk delete message', inline=False)
        embed.add_field(name='oos', value='out of sight! ', inline=False)
    elif arg == 'user':
        # do other stuff
        embed.add_field(name='shuffle', value='Matrix', inline=False)
        embed.add_field(name='pick', value='need help on deciding?', inline=False)
        embed.add_field(name='rand', value='Sends a random number from the range given', inline=False)
        embed.add_field(name='retardify', value='retardify input', inline=False)

    elif arg == 'bot':
        # do another stuff
        embed.add_field(name='ping', value='get my latency', inline=False)
        embed.add_field(name='credits', value='creators of the bot', inline=False)
        embed.add_field(name='change_pres', value="change bot's activity", inline=False)
        embed.add_field(name='help',
                        value="what you are lookin' at.\nuse without arguments for seeing available modules",
                        inline=False)
    elif arg == 'game':
        # do game stuff
        embed.add_field(name='yt', value='visit youtube channel', inline=False)
    elif arg == 'customcommands' or arg == 'cc':
    	embed.add_field(name='command_add', value='add custom command', inline=False)
    	embed.add_field(name='command_get', value='list custom commands', inline=False)
    	embed.add_field(name='command_remove', value='remove custom command', inline=False)
    else:
        # lol
        embed.add_field(name='Module not Found', value='Use +help to see available modules', inline=False)

    # embed.add_field(name='command', value='description', inline=False)
    mhelp = await ctx.send(embed=embed)
    emoji = '✅'
    # get(ctx.guild.emojis, name='767364910367113226')]
    await mhelp.add_reaction(emoji)


@help.error
async def help_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            color=discord.Color.orange()
        )
        embed.set_author(name='Help')
        embed.add_field(name='How To Use', value='help modules', inline=False)
        embed.add_field(name='Mod', value='Moderation commands', inline=False)
        embed.add_field(name='User', value='commands available for all members', inline=False)
        embed.add_field(name='Game', value='All game related commands', inline=False)
        embed.add_field(name='Bot', value='Bot related commands', inline=False)
        embed.add_field(name='customcommands', value='Custom Commands module', inline=False)

        # embed.add_field(name='command', value='description', inline=False)
        mhelp = await ctx.send(embed=embed)
        emoji = '✅'
        # get(ctx.guild.emojis, name='767364910367113226')]
        await mhelp.add_reaction(emoji)


######## USER MODULE ##########


@client.command(pass_context=True, brief='Randomizes order of input',
                description='Randomizes the order of the input. {object},{object},...')
async def shuffle(ctx, args):
    elements = args.split(',')
    random.shuffle(elements)
    description = '\n'.join(elements)
    embed = discord.Embed(
        title='**Matrix!**',
        description=f'{description}',
        color=0xff0000
    )
    await ctx.send(embed=embed)


@client.command(pass_context=True, brief='Picks one out of the arguments',
                description='Picks one out of the arguments.\nFormat:{object},{object}')
async def pick(ctx, *args):
    description = random.choice(args)
    embed = discord.Embed(
        title="**Here's my pick!**",
        description=f'{description}',
        color=0xff0000
    )
    await ctx.send(embed=embed)


@client.command(pass_context=True, brief='Sends a random number from the range given',
                description='Sends a random number from the range given.\nFormat:\n.rand {minimum} {maximum}')
async def rand(ctx, *args):
    randmin = args[0]
    randmax = args[1]
    try:
        int(randmin)
    except ValueError:
        description = 'The first argument is not an integer.'
    try:
        int(randmax)
    except ValueError:
        description = 'The second argument is not an integer.'
    description = str(random.randint(int(randmin), int(randmax)))
    embed = discord.Embed(
        title="**Here's a random number!**",
        description=f'{description}',
        color=0xff0000
    )
    await ctx.send(embed=embed)


@client.command(pass_context=True)
async def retardify(ctx, *args):
    retarded = ''
    retard_words = ' '.join(args)
    i = True  # capitalize
    for char in retard_words:
        if i:
            retarded += char.upper()
        else:
            retarded += char.lower()
        if char != ' ':
            i = not i
    embed = discord.Embed(
        title='**Retardified!**',
        description=f'{retarded}',
        color=0xff0000
    )
    await ctx.send(embed=embed)


################# GAME MODULE ################

@client.command()
async def faq(ctx):
    description = f'Have this,\n{FAQText}'
    embed = discord.Embed(
        title='**FAQ!**',
        description=f'{description}',
        color=0xff0000
    )
    await ctx.message.author.send(embed=embed)


@client.command()
async def tutorial(ctx):
    description = "A  & D are the controls < >, 'Space' is for jumping. If you’d like to Pause the game or quit or go back to the main menu, Use the key 'Esc'"
    embed = discord.Embed(
        title='**Tutorial**',
        description=f'{description}',
        color=0xff0000
    )
    await ctx.send(embed=embed)


@client.command()
async def installguide(ctx, args):
    if args == 'windows' or args == 'win':
        description = "Download the zip file \nExtract the zip file, then look for 'Slime _Mayhem.exe', And if it says 'windows protected your PC', just click on 'more info', then click on 'run anyway'"
    elif args == 'mac':
        description = "Download the zip file \nExtract the zip file, then look for 'Slime Mayhem Beta (Mac)' - Mac Slime mayhem.app"
    elif args == 'linux':
        description = "Download the zip file \nExtract the zip file, open slime mayhem folder, then look for 'slime mayhem 86x64' \nsimply run the file"
    else:
        description = "available platforms are: windows, linux, mac"
    embed = discord.Embed(
        title='**InstallGuide**',
        description=f'{description}',
        color=0xff0000
    )
    await ctx.send(embed=embed)


@installguide.error
async def guide_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            color=discord.Color.orange()
        )
        embed.set_author(name='Help')
        embed.add_field(name='How To Use', value="provide the platform name! \ne.g: ?installguide windows",
                        inline=False)

        # embed.add_field(name='command', value='description', inline=False)
        mhelp = await ctx.send(embed=embed)


@client.command()
async def download(ctx):
    description = 'https://yotopihigames.itch.io/'
    embed = discord.Embed(
        title='**Downloads!**',
        description=f'Visit : {description} \nmake sure you look for the latest one!',
        color=0xff0000
    )
    await ctx.send(embed=embed)


@client.command()
async def yt(ctx):
    description = 'https://www.youtube.com/channel/UCqK2VZRKf4brItm73G0er1w'
    embed = discord.Embed(
        title='**YouTube**',
        description=f'visit : {description}',
        color=0xff0000
    )
    await ctx.send(embed=embed)


# template
@client.command()
async def command(ctx):
    description = 'this is description!'
    embed = discord.Embed(
        title='**Template**',
        description=f'description {description}',
        color=0xff0000
    )
    await ctx.send(embed=embed)


client.run('Nzk2NTk4MjMxODAyMTgzNzUw.X_aP6g.AMfQYG-IXW6_SFQv_2gXJx8Lb4c')












###### trash #######

# Tut = A  & D are the controls < >, 'Space' is for jumping. If you’d like to Pause the game or quit or go back to the main menu, Use the key ‘Esc’
# InstallGuide
# { WINDOWS }, DISCLAIMER: Download doesnt work without all its files with it, So extract the zip file, then look for ["Slime _Mayhem.exe"], And if it says "windows protected your PC", just click on 'more info', then click on 'run anyway'
# { MAC }, extract the file, Go find: Slime Mayhem Beta (Mac) - Mac Slime mayhem.app - Contents - MacOS - Slime_Mayhem
# { LINUX }, Extract the file, Click on slime mayhem, after clicking on the folder Find an app for it, or something called “slime mayhem 86x64

# Download = https://yotopihigames.itch.io/, make sure you look for the latest one!

# YT = https://www.youtube.com/channel/UCqK2VZRKf4brItm73G0er1w?view_as=subscriber