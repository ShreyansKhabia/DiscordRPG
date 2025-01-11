# Git is working!!!
# hell yeah

import discord
import random
import asyncio
import json
from discord.ext import commands
from discord.ui import View, Button

toke_file = open("secret/bot_token.env")
BOT_TOKEN = toke_file.read()

# File path for storing user data
DATA_FILE = 'character_id.json'


# Use a dictionary to store user-specific health and score


# Helper function to load user data
# Helper function to load user data
def load_data():
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        print("No existing data found or JSON decode error.")  # Debug statement
        return {}


# Helper function to save user data
def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)


intent = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intent, help_command=None)

places = {
    "kingdoms": {
        "The Central Dominance": {
            "Dominous": {
                "town square": {
                    "description": "You stand at in the middle of town square.",
                    "items": ["none"],
                    "npcs": ["Agrand"],
                    "cords": [0, 0]
                },
            }
        }
    }
}

biomes = {
    "grassy plains": {
        "enemies": {
            "Swamp lurch": {
                "enemy_health": 30,
                "enemy_attack": 13,
                "enemy_dexterity": 5
            },
            #            "Feral cats": {
            #                "enemy_health": 6,
            #                "enemy_attack": 6
            #            }
        },
        "description": "You stroll through the lucious grassy plains.",
        "look_description": "You are in the grassy fields of the Central Dominance.",
        "freq": 1,
        "area": [-50, 100, -50, 50],
        "xp": 5
    }
}

dialouges = {
    "Agrand": {
        "Quest": {
            "description":
                "Yes mate, go kill some swamp lurches."
                "\nThose bastards have been chewing on my grain for weeks!",
            "clear": "Thank you for killing those bastards!",
            "enemy": "Swamp lurch",
            "amount": 3
        },
        "Help": "You need help you say? Try typing !help to get a list of commands!"
    }
}


# startup
@bot.event
async def on_ready():
    global user_data_RPG
    print(f'Logged in as {bot.user}')
    user_data_RPG = load_data()  # Load user data once at startup
    print(f'User data loaded: {user_data_RPG}')


@bot.command()
async def initialize(ctx):
    user_id = str(ctx.author.id)

    # Load the user data from the file
    user_data_RPG = load_data()

    # Initialize user data if not already done
    if user_id not in user_data_RPG:
        user_data_RPG[user_id] = {
            'x': 0, 'y': 0,
            "max_hp": 100,
            "player_health": 100,
            "player_attack": 20,
            "player_dexterity": 10,
            "player_energy": 10,
            "max_energy": 10,
            "current_quest": None,  # Use None instead of an empty list
            "progress": 0,
            "xp": 0,
            "threshold": 50
        }

        # Save the updated user data to the file only when new data is added
        save_data(user_data_RPG)

        await ctx.send("Bot initialized")
    else:
        await ctx.send("You are already initialized!")


@bot.command()
async def ping(ctx):
    await ctx.send("pong")


async def lvl_up(ctx):
    user_id = str(ctx.author.id)

    user_data_RPG = load_data()

    await ctx.send("You leveled up!")
    await ctx.send("Please choose an option!")

    # Create buttons for accepting or declining the quest
    view = discord.ui.View()

    strenght_button = discord.ui.Button(label="Strenght", style=discord.ButtonStyle.blurple)
    health_button = discord.ui.Button(label="Health", style=discord.ButtonStyle.red)
    dexterity_button = discord.ui.Button(label="Dexterity", style=discord.ButtonStyle.green)

    async def strenght_button_callback(interaction):
        if interaction.user == ctx.author:
            await ctx.send("You have choosen Strenght")
            user_data_RPG[user_id]["max_hp"] += 10
        else:
            await interaction.response.send_message("You cannot click this button!", ephemeral=True)

    async def health_button_callback(interaction):
        if interaction.user == ctx.author:
            await ctx.send("You have choosen Health")
            user_data_RPG[user_id]["player_attack"] += 5
        else:
            await interaction.response.send_message("You cannot click this button!", ephemeral=True)

    async def dexterity_button_callback(interaction):
        if interaction.user == ctx.author:
            await ctx.send("You have choosen Dexterity")
            user_data_RPG[user_id]["player_dexterity"] += 5
        else:
            await interaction.response.send_message("You cannot click this button!", ephemeral=True)

    strenght_button.callback = strenght_button_callback
    health_button.callback = health_button_callback
    dexterity_button.callback = dexterity_button_callback

    view.add_item(strenght_button)
    view.add_item(health_button)
    view.add_item(dexterity_button)


async def get_biome(ctx):
    user_id = str(ctx.author.id)
    user_data = load_data()

    x = user_data[user_id]["x"]
    y = user_data[user_id]["y"]

    # Corrected biome check logic
    # Return biome if coordinates fall within its area
    for biome_name, biome_data in biomes.items():
        biome_area = biome_data["area"]
        if biome_area[0] <= x <= biome_area[1] and biome_area[2] <= y <= biome_area[3]:
            return biome_data

    # Return None if the coordinates don't match any biome
    return None


async def get_rand_encounter(ctx):
    biome = await get_biome(ctx)

    # If a biome is returned, choose a random enemy
    if biome:
        # Get a random enemy from the biome (choose a random key)
        enemy_name = random.choice(list(biome["enemies"].keys()))

        # Retrieve the enemy stats (attack and health)
        enemy_stats = biome["enemies"][enemy_name]

        freq = random.randint(1, biome["freq"])

        # Return the enemy name and its stats
        if freq == 1:
            return enemy_name, enemy_stats, freq
        else:
            return None


async def get_place(ctx):
    user_id = str(ctx.author.id)
    user_data = load_data()

    x = user_data[user_id]['x']
    y = user_data[user_id]['y']

    # Iterate through each kingdom, city, and region to find the correct place based on coordinates
    for kingdom_name, kingdom_data in places.items():
        for city_name, city_data in kingdom_data.items():
            for region_name, region_data in city_data.items():
                for region_key, region_info in region_data.items():
                    # Safeguard for missing "cords" key
                    if "cords" not in region_info:
                        continue  # Skip this region if it doesn't have "cords"

                    cords = region_info["cords"]

                    # Check if the coordinates match the current region
                    if cords == [x, y]:
                        # Return the region details if coordinates match
                        return region_info

    # If no region with matching coordinates is found, return None (or handle as needed)
    return None


async def accept_quest(ctx, user_id, enemy, amount):
    user_data_RPG = load_data()
    user_data_RPG[user_id]["current_quest"] = {"enemy": enemy, "amount": amount, "progress": 0}
    save_data(user_data_RPG)
    await ctx.send(f"You have accepted the quest to kill {amount} {enemy}")


# Function to handle declining a quest
async def decline_quest(ctx):
    await ctx.send("You have declined the quest.")


@bot.command()
async def quest(ctx, enemy, amount, quest_info):
    user_id = str(ctx.author.id)

    user_data_RPG = load_data()

    if user_data_RPG[user_id]["current_quest"]:
        await ctx.send("You are already doing a quest!")
    else:
        # Create buttons for accepting or declining the quest
        view = discord.ui.View()

        accept_button = discord.ui.Button(label="Yes", style=discord.ButtonStyle.green)
        decline_button = discord.ui.Button(label="No", style=discord.ButtonStyle.red)

        async def accept_button_callback(interaction):
            if interaction.user == ctx.author:
                await accept_quest(ctx, user_id, enemy, amount)
            else:
                await interaction.response.send_message("You cannot click this button!", ephemeral=True)

        async def decline_button_callback(interaction):
            if interaction.user == ctx.author:
                await decline_quest(ctx)
            else:
                await interaction.response.send_message("You cannot click this button!", ephemeral=True)

        accept_button.callback = accept_button_callback
        decline_button.callback = decline_button_callback

        view.add_item(accept_button)
        view.add_item(decline_button)

        await ctx.send(quest_info["description"], ephemeral=True)
        await ctx.send(f"Do you want to accept the quest to kill {amount} {enemy}?", view=view)


async def fight(ctx, enemy_health, enemy_attack, enemy_dexterity, enemy_name, xp):
    user_id = str(ctx.author.id)

    # Load user data at the start of the fight
    user_data_RPG = load_data()

    # Get the player's initial health and attack values
    player_health = user_data_RPG[user_id]['player_health']
    player_attack = user_data_RPG[user_id]['player_attack']
    player_dexterity = user_data_RPG[user_id]['player_dexterity']

    while player_health > 0 and enemy_health > 0:
        round_message = []

        # Player's turn (weighted attack roll)
        player_roll = random.randint(1, player_dexterity + enemy_dexterity)
        if player_roll <= player_attack:
            enemy_health -= player_attack
            round_message.append(f"You hit the {enemy_name} for {player_attack} damage.")
        else:
            round_message.append("You missed.")

        # Enemy's turn (weighted attack roll)
        enemy_roll = random.randint(1, player_dexterity + enemy_dexterity)
        if enemy_roll <= enemy_dexterity:
            player_health -= enemy_attack
            round_message.append(f"The {enemy_name} hits you for {enemy_attack} damage.")
        else:
            round_message.append(f"The {enemy_name} missed.")

        # Display health
        round_message.append(f"Your health: {player_health}")
        round_message.append(f"{enemy_name}'s health: {enemy_health}")

        # Send round message to the user
        await ctx.send("\n".join(round_message))

        # Save the updated player health after each round
        user_data_RPG[user_id]['player_health'] = player_health
        save_data(user_data_RPG)

        # Check for defeat
        if player_health <= 0 or enemy_health <= 0:
            break

        # Wait before next round
        await asyncio.sleep(0.5)

    # Final outcome message
    if player_health <= 0:
        await ctx.send("You have been defeated!")
        user_data_RPG[user_id]['player_health'] = 0  # Ensure health is set to 0 on defeat
    elif enemy_health <= 0:
        await asyncio.sleep(0.5)
        await ctx.send(f"The {enemy_name} has been defeated!")
        user_data_RPG[user_id]["xp"] += xp

        # Handle quest progress
        current_quest = user_data_RPG[user_id].get("current_quest", None)
        if current_quest:
            enemy = current_quest["enemy"]
            amount = current_quest["amount"]
            progress = current_quest["progress"]

            if enemy_name == enemy:
                progress += 1
                current_quest["progress"] = progress
                user_data_RPG[user_id]["current_quest"] = current_quest  # Update quest progress

                if progress == amount:
                    await ctx.send("You have completed your quest!")
                else:
                    await ctx.send(f"{progress} / {amount}")

    # Save user data after the battle ends (this will save both health and quest progress)
    user_data_RPG[user_id]['player_health'] = player_health  # Ensure health is updated
    save_data(user_data_RPG)


@bot.command()
async def move(ctx, direction, amount):
    user_id = str(ctx.author.id)

    # Load user data at the start of the move
    user_data_RPG = load_data()

    # Check if the user exists in the data
    if user_id not in user_data_RPG:
        await ctx.send("You need to initialize first with !initialize.")
        return

    x = user_data_RPG[user_id]['x']
    player_energy = user_data_RPG[user_id]['player_energy']
    y = user_data_RPG[user_id]['y']

    # Validate direction
    valid_directions = ["w", "west", "n", "north", "e", "east", "s", "south"]
    direction = direction.lower()  # Make it case-insensitive
    if direction not in valid_directions:
        await ctx.send("Please choose a valid direction (w/west, n/north, e/east, s/south).")
        return

    # Validate amount
    try:
        amount = int(amount)
    except ValueError:
        await ctx.send("Please provide a valid integer for the amount.")
        return

    # Move based on the direction and available energy
    if player_energy > 0:
        for i in range(amount):
            if player_energy <= 0:
                await ctx.send("You are out of energy, try resting!")
                break

            if direction in ["w", "west"]:
                x -= 1
            elif direction in ["e", "east"]:
                x += 1
            elif direction in ["n", "north"]:
                y += 1
            elif direction in ["s", "south"]:
                y -= 1

            player_energy -= 1
            await ctx.send(f"Your coordinates are now {x}, {y}. Remaining energy: {player_energy}")
            await asyncio.sleep(0.5)

            biome = await get_biome(ctx)
            place = await get_place(ctx)

            # Call get_rand_encounter() and check if it returned a valid result
            encounter = await get_rand_encounter(ctx)
            if place:
                await ctx.send(place["description"])

                # Update user data and save it to the file
                user_data_RPG[user_id]['x'] = x
                user_data_RPG[user_id]['y'] = y
                user_data_RPG[user_id]['player_energy'] = player_energy
                save_data(user_data_RPG)
            else:
                await ctx.send(biome["description"])
                if encounter:
                    enemy_name, enemy_stats, freq = encounter
                    await ctx.send(f"You encounter a {enemy_name}")
                    await fight(ctx, enemy_stats["enemy_health"], enemy_stats["enemy_attack"], enemy_stats["enemy_dexterity"], enemy_name, enemy_stats["xp"])

                    # Load updated data after the fight
                    user_data_RPG = load_data()

                    user_data_RPG[user_id]['x'] = x
                    user_data_RPG[user_id]['y'] = y
                    user_data_RPG[user_id]['player_energy'] = player_energy
                    save_data(user_data_RPG)
                else:
                    # Update user data and save it to the file
                    user_data_RPG[user_id]['x'] = x
                    user_data_RPG[user_id]['y'] = y
                    user_data_RPG[user_id]['player_energy'] = player_energy
                    save_data(user_data_RPG)
    else:
        await ctx.send("You are out of energy, try resting!")


@bot.command()
async def rest(ctx, amount):
    user_id = str(ctx.author.id)

    # Load user data
    user_data_RPG = load_data()

    player_energy = user_data_RPG[user_id]['player_energy']
    max_energy = user_data_RPG[user_id]["max_energy"]

    player_health = user_data_RPG[user_id]['player_health']
    max_hp = user_data_RPG[user_id]["max_hp"]

    try:
        amount = int(amount)
    except ValueError:
        await ctx.send(f"Please give an integer that is between 0 and {max_energy}")
        return

    if amount <= 0:
        await ctx.send(f"You need to rest for a positive number of seconds.")
        return

    # If both health and energy are full, notify the user
    if player_energy == max_energy and player_health == max_hp:
        await ctx.send(f"Your energy and health are already full.")
        return

    await ctx.send(f"You sit down to rest for {amount} seconds.")

    # Send the initial message
    message = await ctx.send(f"{amount} seconds remaining")
    await asyncio.sleep(1)

    # Countdown and update message
    for i in range(amount):
        # Update remaining time
        remaining_time = amount - (i + 1)
        await message.edit(content=f"{remaining_time} seconds remaining.")

        # Simulate resting by increasing energy and health
        if player_energy < max_energy:
            player_energy = min(player_energy + 1, max_energy)
        if player_health < max_hp:
            player_health = min(player_health + 10, max_hp)

        # Save updated energy and health after each increase
        user_data_RPG[user_id]['player_energy'] = player_energy
        user_data_RPG[user_id]['player_health'] = player_health
        save_data(user_data_RPG)

        # If both energy and health are full, break the loop
        if player_energy == max_energy and player_health == max_hp:
            await ctx.send(f"Your energy and health are now full.")
            break

        # Delay 1 second before the next loop iteration
        await asyncio.sleep(1)

    # Final energy and health status
    await ctx.send(f"Rest is complete! You now have {player_energy} energy and {player_health} HP.")


@bot.command()
async def look(ctx):
    user_id = str(ctx.author.id)  # Ensure user_id is a string

    # Load user data
    user_data_RPG = load_data()

    # Check if user data exists
    if user_id not in user_data_RPG:
        await ctx.send("You need to initialize first with !initialize.")
        return

    x = user_data_RPG[user_id]['x']
    y = user_data_RPG[user_id]['y']

    # Get the current place using get_place function
    place = await get_place(ctx)

    if place:
        # If a place is found, display the place information
        await ctx.send(f"\n{place['description']}")

        # Show items if available
        items = place.get('items', ['none'])
        if "none" not in items:
            await ctx.send(f"Items: {', '.join(items)}")
        else:
            await ctx.send("There are no items here.")

        # Show NPCs if available
        npcs = place.get('npcs', ['none'])
        if "none" not in npcs:
            for npc in npcs:
                await ctx.send(f"{npc} is here")
        else:
            await ctx.send("There are no NPCs here.")
    else:
        # If no specific place is found, fallback to the biome
        biome = await get_biome(ctx)
        if biome:
            await ctx.send(biome["look_description"])
            items = biome.get('items', ['none'])
            if "none" not in items:
                await ctx.send(f"Items: {', '.join(items)}")
            else:
                await ctx.send("There are no items here.")

            npcs = biome.get('npcs', ['none'])
            if "none" not in npcs:
                for npc in npcs:
                    await ctx.send(f"{npc} is here")
            else:
                await ctx.send("There are no NPCs here.")
        else:
            await ctx.send("You are in an unknown area, and there is no information available.")


@bot.command()
async def talk(ctx, npc):
    user_id = str(ctx.author.id)
    user_data_RPG = load_data()

    # Check if the NPC exists in the dialogues dictionary
    if npc in dialouges:
        # Retrieve the dialogue options for the NPC
        npc_dialogue = dialouges[npc]

        # Create a view to hold the buttons for Quest and Help options
        view = discord.ui.View()

        # Create buttons for Quest and Help
        quest_button = discord.ui.Button(label="Quest", style=discord.ButtonStyle.blurple)
        help_button = discord.ui.Button(label="Help", style=discord.ButtonStyle.blurple)

        async def quest_button_callback(interaction):
            if interaction.user == ctx.author:
                current_quest = user_data_RPG[user_id].get("current_quest", None)
                if current_quest and current_quest["progress"] == current_quest["amount"]:
                    await interaction.response.send_message(npc_dialogue["Quest"]["clear"], ephemeral=True)
                else:
                    quest_info = npc_dialogue["Quest"]
                    await quest(ctx, quest_info["enemy"], quest_info["amount"], quest_info)
            else:
                await interaction.response.send_message("You cannot click this button!", ephemeral=True)

        async def help_button_callback(interaction):
            if interaction.user == ctx.author:
                await interaction.response.send_message(npc_dialogue["Help"], ephemeral=True)
            else:
                await interaction.response.send_message("You cannot click this button!", ephemeral=True)

        # Assign callbacks to buttons
        quest_button.callback = quest_button_callback
        help_button.callback = help_button_callback

        # Add buttons to the view
        view.add_item(quest_button)
        view.add_item(help_button)

        await ctx.send(f"Talking to {npc}. Please choose an option:", view=view)
    else:
        await ctx.send("That isn't a valid NPC.")


@bot.command()
async def help(ctx):
    await ctx.send("\nHere is a list of all the commands:"
                   "\n- help - provides a list of all the commands."
                   "\n- initialize - initializes the bot."
                   "\n- ping - returns pong."
                   "\n- move <direction> <amount> - lets you move through the map."
                   "\n- rest <amount> - lets you recharge your energy."
                   "\n- look - describes your surroundings including npcs and items."
                   "\n- talk <npc> - lets you talk to npcs")


@bot.command()
async def stats(ctx):
    user_id = str(ctx.author.id)
    user_data_RPG = load_data()

    # Check if user data exists
    if user_id not in user_data_RPG:
        await ctx.send("You need to initialize first with !initialize.")
        return

    # Retrieve quest information from user data
    current_quest = user_data_RPG[user_id].get("current_quest", None)
    if current_quest:
        enemy = current_quest["enemy"]
        amount = current_quest["amount"]
        progress = current_quest["progress"]
        await ctx.send(f"\nPosition: {user_data_RPG[user_id]['x']}, {user_data_RPG[user_id]['y']}"
                       f"\nHealth: {user_data_RPG[user_id]['player_health']}"
                       f"\nAttack: {user_data_RPG[user_id]['player_attack']}"
                       f"\nEnergy: {user_data_RPG[user_id]['player_energy']} / {user_data_RPG[user_id]['max_energy']}"
                       f"\nQuest: {enemy} {progress} / {amount}")
    else:
        await ctx.send(f"\nPosition: {user_data_RPG[user_id]['x']}, {user_data_RPG[user_id]['y']}"
                       f"\nHealth: {user_data_RPG[user_id]['player_health']}"
                       f"\nAttack: {user_data_RPG[user_id]['player_attack']}"
                       f"\nEnergy: {user_data_RPG[user_id]['player_energy']} / {user_data_RPG[user_id]['max_energy']}"
                       f"\nQuest: You don't have any quests.")


@bot.event
async def on_disconnect():
    save_data(user_data_RPG)


# Run the bot
bot.run(BOT_TOKEN)
