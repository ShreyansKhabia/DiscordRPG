# Git is working!!!
# hell yeah

import discord
import random
import asyncio
import json
from discord.ext import commands
import logging

toke_file = open("secret/bot_token.env")
BOT_TOKEN = toke_file.read()

# File path for storing user data
DATA_FILE = 'character_id.json'

logger = logging.getLogger('discord')
logger.setLevel(logging.ERROR)
handler = logging.FileHandler(filename='discord_errors.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


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


# Global error handler for commands
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("This command does not exist. Please use !help to see the list of available commands.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("You are missing required arguments for this command.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("One of your arguments is invalid.")
    elif isinstance(error, commands.CommandInvokeError):
        await ctx.send("There was an error while executing the command. Please try again later.")
        logger.error(f"Error in command '{ctx.command}': {error}")
    else:
        await ctx.send("An unexpected error occurred. Please try again later.")
        logger.error(f"Unexpected error: {error}")


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
                "tavern": {
                    "description": "You are at the tavern.",
                    "items": ["none"],
                    "npcs": ["Jimmy"],
                    "cords": [-1, 0],
                    "enter_cords": [142142253, 5132346]
                },
                "tavern inside": {
                    "description": "You are in the tavern bustling with life.",
                    "items": ["none"],
                    "npcs": ["Stormeye"],
                    "cords": [142142253, 5132346],
                    "leave_cords": [-1, 0],
                    "leave_name": "tavern"
                }
            },
            "Silverwood Forest": {
                "entrance": {
                    "description": "You are at the entrance of the Silverwood Forest.",
                    "items": ["none"],
                    "npcs": ["Eldrin"],
                    "cords": [10, 10]
                },
                "deep woods": {
                    "description": "You are deep within the Silverwood Forest.",
                    "items": ["Silverwood bark"],
                    "npcs": ["none"],
                    "cords": [15, 15]
                }
            },
            "The Dwarven Mines": {
                "entrance": {
                    "description": "You are at the entrance of the Dwarven Mines.",
                    "items": ["none"],
                    "npcs": ["Dorin"],
                    "cords": [20, -10]
                },
                "mine shaft": {
                    "description": "You are in the mine shaft of the Dwarven Mines.",
                    "items": ["Iron ore"],
                    "npcs": ["none"],
                    "cords": [25, -15]
                }
            },
            "Mystic Lake": {
                "shore": {
                    "description": "You are at the shore of the Mystic Lake.",
                    "items": ["none"],
                    "npcs": ["Mira"],
                    "cords": [5, 20]
                },
                "island": {
                    "description": "You are on a small island in the Mystic Lake.",
                    "items": ["Mystic pearl"],
                    "npcs": ["none"],
                    "cords": [10, 25]
                }
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
                "enemy_dexterity": 5,
                "xp": 32
            },
            "Feral cat": {
                "enemy_health": 12,
                "enemy_attack": 3,
                "enemy_dexterity": 6,
                "xp": 12
            }
        },
        "description": "You stroll through the luscious grassy plains.",
        "look_description": "You are in the grassy fields of the Central Dominance.",
        "freq": 1,
        "area": [-50, 100, -50, 50]
    },
    "Dark forest": {
        "enemies": {
            "Shadow wraith": {
                "enemy_health": 40,
                "enemy_attack": 15,
                "enemy_dexterity": 8,
                "xp": 50
            },
            "Gloom Spider": {
                "enemy_health": 20,
                "enemy_attack": 5,
                "enemy_dexterity": 4,
                "xp": 20
            }
        },
        "description": "You are in a dense, mist-covered forest where light barely breaks through the thick canopy.",
        "look_description": "The dark woods stretch endlessly, their trees towering high above.",
        "freq": 8,
        "area": [-100, 200, -200, 100]
    },
    "Craggy Mountains": {
        "enemies": {
            "Mountain Troll": {
                "enemy_health": 60,
                "enemy_attack": 20,
                "enemy_dexterity": 3,
                "xp": 75
            },
            "Gloom Spider": {
                "enemy_health": 100,
                "enemy_attack": 25,
                "enemy_dexterity": 2,
                "xp": 120
            }
        },
        "description": "You are in the rocky cliffs and steep peaks of the Craggy Mountains. The wind howls through "
                       "the craggy terrain.",
        "look_description": "Jagged mountain ranges rise sharply from the earth, the air growing thin and cold.",
        "freq": 5,
        "area": [50, 150, -200, 50]
    },
    "Sandy Desert": {
        "enemies": {
            "Sand Worm": {
                "enemy_health": 50,
                "enemy_attack": 20,
                "enemy_dexterity": 4,
                "xp": 70
            },
            "Scorpion": {
                "enemy_health": 25,
                "enemy_attack": 10,
                "enemy_dexterity": 8,
                "xp": 35
            }
        },
        "description": "You are walking through the vast, hot Sandy Desert.",
        "look_description": "The desert stretches endlessly, with sand dunes as far as the eye can see.",
        "freq": 6,
        "area": [100, 200, 50, 150]
    },
    "Frozen Tundra": {
        "enemies": {
            "Ice Golem": {
                "enemy_health": 70,
                "enemy_attack": 25,
                "enemy_dexterity": 3,
                "xp": 90
            },
            "Snow Leopard": {
                "enemy_health": 30,
                "enemy_attack": 15,
                "enemy_dexterity": 7,
                "xp": 40
            }
        },
        "description": "You are traversing the cold, icy expanse of the Frozen Tundra.",
        "look_description": "The tundra is covered in snow, with icy winds howling around you.",
        "freq": 4,
        "area": [-200, -100, -150, -50]
    },
    "The Iron Citadel": {
        "description": "You are in the bustling city of The Iron Citadel.",
        "look_description": "The city is filled with towering buildings and busy streets.",
        "freq": 7,
        "area": [0, 50, 0, 50]
    },
    "Elven Glade": {
        "description": "You are in the serene and magical Elven Glade.",
        "look_description": "The glade is filled with ancient trees and a sense of tranquility.",
        "freq": 5,
        "area": [-50, 0, -50, 0]
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
            "amount": 3,
            "xp_reward": 50
        },
        "Help": "You need help you say? Try typing !help to get a list of commands!"
    },
    "Jimmy": {
        "Talk": "Hey mate, this is the towns tavern!"
                "\nYou can find some friendly lads there."
    },
    "Stormeye": {
        "Talk": "Hey ma"
    },
    "Eldrin": {
        "Quest": {
            "description":
                "Greetings traveler, I have a task for you."
                "\nThe Shadow Wraiths have been causing trouble. Can you defeat 5 of them?",
            "clear": "Thank you for defeating the Shadow Wraiths!",
            "enemy": "Shadow wraith",
            "amount": 5,
            "xp_reward": 100
        },
        "Talk": "I am Eldrin the Wise. Seek knowledge and you shall find it."
    },
    "Captain Ironclad": {
        "Quest": {
            "description":
                "Soldier, we need your help!"
                "\nThe Mountain Trolls are attacking our fort. Defeat 3 of them.",
            "clear": "Well done! You've saved our fort!",
            "enemy": "Mountain Troll",
            "amount": 3,
            "xp_reward": 80
        },
        "Talk": "I am Captain Ironclad. Ready for battle!"
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
    try:
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
                "current_quest": None,
                "progress": 0,
                "xp": 0,
                "threshold": 50,
                "name": "Anonymous"
            }

            # Save the updated user data to the file only when new data is added
            save_data(user_data_RPG)

            await ctx.send("Bot initialized")
            await ctx.send("Please choose a name with !name <name>")
        else:
            await ctx.send("You are already initialized!")
    except Exception as e:
        await ctx.send("An error occurred during initialization. Please try again later.")
        logger.error(f"Error in initialize command: {e}")


@bot.command()
async def ping(ctx):
    await ctx.send("pong")


async def lvl_up(ctx):
    try:
        user_id = str(ctx.author.id)
        user_data_RPG = load_data()

        await ctx.send("You leveled up!")
        await ctx.send("Please choose an option!")

        view = discord.ui.View()

        strength_button = discord.ui.Button(label="Strength", style=discord.ButtonStyle.blurple)
        health_button = discord.ui.Button(label="Health", style=discord.ButtonStyle.red)
        dexterity_button = discord.ui.Button(label="Dexterity", style=discord.ButtonStyle.green)

        async def button_callback(interaction, attribute):
            if interaction.user == ctx.author:
                if attribute == "Strength":
                    await ctx.send("You have chosen Strength")
                    user_data_RPG[user_id]["player_attack"] += 5
                elif attribute == "Health":
                    await ctx.send("You have chosen Health")
                    user_data_RPG[user_id]["max_hp"] += 10
                elif attribute == "Dexterity":
                    await ctx.send("You have chosen Dexterity")
                    user_data_RPG[user_id]["player_dexterity"] += 5

                user_data_RPG[user_id]["xp"] = 0
                user_data_RPG[user_id]["threshold"] += 50
                save_data(user_data_RPG)

                # Clear or disable the buttons to prevent further clicks
                for item in view.children:
                    item.disabled = True
                await interaction.response.edit_message(view=view)
            else:
                await interaction.response.send_message("You cannot click this button!", ephemeral=True)

        strength_button.callback = lambda interaction: button_callback(interaction, "Strength")
        health_button.callback = lambda interaction: button_callback(interaction, "Health")
        dexterity_button.callback = lambda interaction: button_callback(interaction, "Dexterity")

        view.add_item(strength_button)
        view.add_item(health_button)
        view.add_item(dexterity_button)

        await ctx.send("Choose an attribute to improve:", view=view)
    except Exception as e:
        await ctx.send("An error occurred while leveling up. Please try again later.")
        logger.error(f"Error in lvl_up function: {e}")


async def get_biome(ctx):
    try:
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
    except Exception as e:
        await ctx.send("An error occurred while moving. Please try again later.")
        logger.error(f"Error in move command: {e}")


async def get_rand_encounter(ctx):
    try:
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
    except Exception as e:
        await ctx.send("An error occurred while moving. Please try again later.")
        logger.error(f"Error in move command: {e}")


async def get_place(ctx):
    try:
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
                            return region_info, region_key
        # If no region with matching coordinates is found, return None (or handle as needed)
        return None, None
    except Exception as e:
        await ctx.send("An error occurred while moving. Please try again later.")
        logger.error(f"Error in move command: {e}")
        return None, None


async def quest(ctx, enemy, amount, quest_info):
    try:
        user_id = str(ctx.author.id)
        user_data_RPG = load_data()

        current_quest = user_data_RPG[user_id]["current_quest"]

        if current_quest:
            if current_quest["enemy"] != enemy and current_quest["amount"] != amount:
                await ctx.send("Come back when you have completed the quest.")
            else:
                await ctx.send("You are already doing a quest!")
        else:
            # Create buttons for accepting or declining the quest
            view = discord.ui.View()

            accept_button = discord.ui.Button(label="Yes", style=discord.ButtonStyle.green)
            decline_button = discord.ui.Button(label="No", style=discord.ButtonStyle.red)

            async def accept_button_callback(interaction):
                if interaction.user == ctx.author:
                    await accept_quest(ctx, user_id, enemy, amount, quest_info["xp_reward"])
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
    except Exception as e:
        await ctx.send("An error occurred while processing the quest. Please try again later.")
        logger.error(f"Error in quest function: {e}")


# Function to handle accepting a quest
async def accept_quest(ctx, user_id, enemy, amount, xp_reward):
    try:
        user_data_RPG = load_data()
        user_data_RPG[user_id]["current_quest"] = {
            "enemy": enemy,
            "amount": amount,
            "progress": 0,
            "xp_reward": xp_reward
        }
        save_data(user_data_RPG)
        await ctx.send(f"You have accepted the quest to kill {amount} {enemy}.")
    except Exception as e:
        await ctx.send("An error occurred while accepting the quest. Please try again later.")
        logger.error(f"Error in accept_quest function: {e}")


# Function to handle declining a quest
async def decline_quest(ctx):
    try:
        await ctx.send("You have declined the quest.")
    except Exception as e:
        await ctx.send("An error occurred while declining the quest. Please try again later.")
        logger.error(f"Error in decline_quest function: {e}")


# Function to handle completing a quest
async def complete_quest(ctx, user_id, xp_reward):
    try:
        user_data_RPG = load_data()
        xp = user_data_RPG[user_id]["xp"]
        threshold = user_data_RPG[user_id]["threshold"]

        xp += xp_reward
        user_data_RPG[user_id]["xp"] = xp

        if xp >= threshold:
            await lvl_up(ctx)

        user_data_RPG[user_id]["current_quest"] = None  # Clear current quest
        save_data(user_data_RPG)

        await ctx.send(f"You have completed your quest and earned {xp_reward} XP!")
    except Exception as e:
        await ctx.send("An error occurred while completing the quest. Please try again later.")
        logger.error(f"Error in complete_quest function: {e}")


async def fight(ctx, enemy_health, enemy_attack, enemy_dexterity, enemy_name, enemy_xp):
    try:
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
    except Exception as e:
        await ctx.send("An error occurred while moving. Please try again later.")
        logger.error(f"Error in move command: {e}")

    # Final outcome message
    if player_health <= 0:
        await ctx.send("You have been defeated!")
        user_data_RPG[user_id]['player_health'] = 0  # Ensure health is set to 0 on defeat
    elif enemy_health <= 0:
        await ctx.send(f"The {enemy_name} has been defeated!")
        xp = user_data_RPG[user_id]["xp"]
        threshold = user_data_RPG[user_id]["threshold"]

        xp += enemy_xp

        user_data_RPG[user_id]["xp"] = xp

        if xp >= threshold:
            await lvl_up(ctx)
        else:
            pass

        # Handle quest progress
        current_quest = user_data_RPG[user_id].get("current_quest", None)
        if current_quest:
            enemy = current_quest["enemy"]
            amount = current_quest["amount"]
            progress = current_quest["progress"]

            if enemy_name == enemy and progress < amount:
                progress += 1
                current_quest["progress"] = progress
                user_data_RPG[user_id]["current_quest"] = current_quest  # Update quest progress

                if progress == amount:
                    await complete_quest(ctx, user_id, current_quest["xp_reward"])
                else:
                    await ctx.send(f"{progress} / {amount}")

    # Save user data after the battle ends (this will save both health and quest progress)
    user_data_RPG[user_id]['player_health'] = player_health  # Ensure health is updated
    save_data(user_data_RPG)


@bot.command()
async def move(ctx, direction, amount):
    try:
        user_id = str(ctx.author.id)
        user_data_RPG = load_data()

        if user_id not in user_data_RPG:
            await ctx.send("You need to initialize first with !initialize.")
            return

        x = user_data_RPG[user_id]['x']
        y = user_data_RPG[user_id]['y']
        player_energy = user_data_RPG[user_id]['player_energy']

        valid_directions = ["w", "west", "n", "north", "e", "east", "s", "south"]
        direction = direction.lower()
        if direction not in valid_directions:
            await ctx.send("Please choose a valid direction (w/west, n/north, e/east, s/south).")
            return

        try:
            amount = int(amount)
        except ValueError:
            await ctx.send("Please provide a valid integer for the amount.")
            return

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

                place, place_key = await get_place(ctx)
                if place:
                    await ctx.send(place["description"])
                else:
                    biome = await get_biome(ctx)
                    if biome:
                        await ctx.send(biome["description"])
                        encounter = await get_rand_encounter(ctx)
                        if encounter:
                            enemy_name, enemy_stats, freq = encounter
                            await ctx.send(f"You encounter a {enemy_name}")
                            await fight(ctx, enemy_stats["enemy_health"], enemy_stats["enemy_attack"],
                                        enemy_stats["enemy_dexterity"], enemy_name, enemy_stats["xp"])

                user_data_RPG[user_id]['x'] = x
                user_data_RPG[user_id]['y'] = y
                user_data_RPG[user_id]['player_energy'] = player_energy
                save_data(user_data_RPG)
        else:
            await ctx.send("You are out of energy, try resting!")
    except Exception as e:
        await ctx.send("An error occurred while moving. Please try again later.")
        logger.error(f"Error in move command: {e}")


@bot.command()
async def rest(ctx, amount):
    try:
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
    except Exception as e:
        await ctx.send("An error occurred while moving. Please try again later.")
        logger.error(f"Error in move command: {e}")


async def get_user_name(user_id):
    user = await bot.fetch_user(user_id)
    return user.name


@bot.command()
async def look(ctx):
    try:
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
        place, place_key = await get_place(ctx)

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

        other_players = [user for user in user_data_RPG if
                         user != user_id and user_data_RPG[user]['x'] == x and user_data_RPG[user]['y'] == y]
        if other_players:
            player_names = await asyncio.gather(*[get_user_name(user) for user in other_players])
            await ctx.send(f"Players here: {', '.join(player_names)}")
        else:
            await ctx.send("There are no other players here.")
    except Exception as e:
        await ctx.send("An error occurred while moving. Please try again later.")
        logger.error(f"Error in move command: {e}")


@bot.command()
async def talk(ctx, npc):
    try:
        user_id = str(ctx.author.id)
        user_data_RPG = load_data()

        if npc in dialouges:
            npc_dialogue = dialouges[npc]
            view = discord.ui.View()

            for option in npc_dialogue.keys():
                button = discord.ui.Button(label=option, style=discord.ButtonStyle.blurple)

                async def button_callback(interaction, option=option):
                    if interaction.user == ctx.author:
                        if option == "Quest":
                            current_quest = user_data_RPG[user_id].get("current_quest", None)
                            if current_quest and current_quest["progress"] == current_quest["amount"]:
                                await interaction.response.send_message(npc_dialogue[option]["clear"], ephemeral=True)
                            else:
                                quest_info = npc_dialogue[option]
                                await quest(ctx, quest_info["enemy"], quest_info["amount"], quest_info)
                        else:
                            await interaction.response.send_message(npc_dialogue[option], ephemeral=True)
                    else:
                        await interaction.response.send_message("You cannot click this button!", ephemeral=True)

                button.callback = button_callback
                view.add_item(button)

            await ctx.send(f"Talking to {npc}. Please choose an option:", view=view)
        else:
            await ctx.send("That isn't a valid NPC.")
    except Exception as e:
        await ctx.send("An error occurred while moving. Please try again later.")
        logger.error(f"Error in move command: {e}")


@bot.command()
async def help(ctx):
    await ctx.send("\nHere is a list of all the commands:"
                   "\n- help - provides a list of all the commands."
                   "\n- initialize - initializes the bot."
                   "\n- ping - returns pong."
                   "\n- move <direction> <amount> - lets you move through the map."
                   "\n- rest <amount> - lets you recharge your energy."
                   "\n- look - describes your surroundings including npcs and items."
                   "\n- talk <npc> - lets you talk to npcs."
                   "\n- name <name> - lets you name your character."
                   "\n- leave <place> - leave buildings."
                   "\n- enter <place> - enter buildings.")


@bot.command()
async def stats(ctx):
    try:
        user_id = str(ctx.author.id)
        user_data_RPG = load_data()

        if user_id not in user_data_RPG:
            await ctx.send("You need to initialize first with !initialize.")
            return

        user_info = user_data_RPG[user_id]
        current_quest = user_info.get("current_quest", None)
        name = user_info.get("name", "Anonymous")  # Default to "Anonymous" if name is not set

        if current_quest:
            await ctx.send(f"""
                Position: {user_info['x']}, {user_info['y']}
                Health: {user_info['player_health']} / {user_info['max_hp']}
                Attack: {user_info['player_attack']}
                Dexterity: {user_info['player_dexterity']}
                Energy: {user_info['player_energy']} / {user_info['max_energy']}
                Quest: {current_quest['enemy']} {current_quest['progress']} / {current_quest['amount']}
                Xp: {user_info['threshold']} / {user_info['xp']}
                Name: {name}
            """)
        else:
            await ctx.send(f"""
                Position: {user_info['x']}, {user_info['y']}
                Health: {user_info['player_health']} / {user_info['max_hp']}
                Attack: {user_info['player_attack']}
                Dexterity: {user_info['player_dexterity']}
                Energy: {user_info['player_energy']} / {user_info['max_energy']}
                Quest: You don't have any quests.
                Xp: {user_info['threshold']} / {user_info['xp']}
                Name: {name}
            """)
    except Exception as e:
        await ctx.send("An error occurred while fetching stats. Please try again later.")
        logger.error(f"Error in the stats command: {e}")


@bot.command()
async def enter(ctx, place):
    user_data_RPG = load_data()
    user_id = str(ctx.author.id)

    place = place.lower()
    current_place, place_name = await get_place(ctx)

    if current_place and place == place_name:
        user_data_RPG[user_id]["x"] = current_place["enter_cords"][0]
        user_data_RPG[user_id]["y"] = current_place["enter_cords"][1]

        save_data(user_data_RPG)

        await ctx.send(f"You enter the {place_name}")
    else:
        await ctx.send(f"You cannot enter {place}.")


@bot.command()
async def leave(ctx, place):
    try:
        user_data_RPG = load_data()
        user_id = str(ctx.author.id)

        place = place.lower()
        current_place, place_name = await get_place(ctx)

        if current_place and place in current_place.get('description', '').lower():
            if "leave_cords" in current_place:
                user_data_RPG[user_id]["x"] = current_place["leave_cords"][0]
                user_data_RPG[user_id]["y"] = current_place["leave_cords"][1]

                save_data(user_data_RPG)
                await ctx.send(f"You leave the {place_name}")
            else:
                await ctx.send(f"The place {place_name} does not have leave coordinates.")
        else:
            await ctx.send(f"You are not in the specified place: {place}.")
    except Exception as e:
        await ctx.send("An error occurred. Please try again later.")
        logger.error(f"Error in leave command: {e}")


@bot.command()
async def name(ctx, name):
    user_data_RPG = load_data()
    user_id = str(ctx.author.id)

    user_data_RPG[user_id]["name"] = name
    save_data(user_data_RPG)
    await ctx.send(f"Your name has been set to {name}")


@bot.event
async def on_disconnect():
    save_data(user_data_RPG)


# Run the bot
bot.run(BOT_TOKEN)
