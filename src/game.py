import random
from enum import Enum

class GameState(Enum):
    EXPLORATION = 1
    BATTLE = 2
    HUB = 3
    GAME_OVER = 4

class Player:
    def __init__(self, name="Hero"):
        self.name = name
        self.max_hp = 100
        self.hp = self.max_hp
        self.attack = 10
        self.defense = 5
        self.xp = 0
        self.level = 1
        self.gold = 0
        self.inventory = []

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0
        return self.hp == 0

    def heal(self, amount):
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def add_xp(self, amount):
        self.xp += amount
        # Simplified leveling up for now
        if self.xp >= self.level * 100:  # Example: 100 XP per level
            self.level_up()

    def level_up(self):
        self.level += 1
        self.max_hp += 10
        self.hp = self.max_hp
        self.attack += 2
        self.defense += 1
        print(f"{self.name} leveled up to Level {self.level}!")

    def add_gold(self, amount):
        self.gold += amount

    def add_item(self, item):
        self.inventory.append(item)

    def remove_item(self, item):
        if item in self.inventory:
            self.inventory.remove(item)
            return True
        return False

    def get_status(self):
        return (f"--- {self.name} Status ---\n"
                f"Level: {self.level}\n"
                f"HP: {self.hp}/{self.max_hp}\n"
                f"Attack: {self.attack}\n"
                f"Defense: {self.defense}\n"
                f"XP: {self.xp}\n"
                f"Gold: {self.gold}\n"
                f"Inventory: {', '.join(self.inventory) if self.inventory else 'Empty'}\n"
                f"--------------------------")

    def __str__(self):
        return self.name

class Enemy:
    def __init__(self, name, hp, attack, defense, xp_drop, gold_drop):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.xp_drop = xp_drop
        self.gold_drop = gold_drop

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0
        return self.hp == 0

    def __str__(self):
        return self.name

class Slime(Enemy):
    def __init__(self):
        super().__init__("Slime", hp=30, attack=5, defense=2, xp_drop=10, gold_drop=5)

class Skeleton(Enemy):
    def __init__(self):
        super().__init__("Skeleton", hp=50, attack=8, defense=4, xp_drop=20, gold_drop=10)

class Dragon(Enemy):
    def __init__(self):
        super().__init__("Dragon", hp=200, attack=20, defense=10, xp_drop=100, gold_drop=50)


class Room:
    def __init__(self, description, exits=None, enemies=None, items=None):
        self.description = description
        self.exits = exits if exits is not None else {}  # e.g., {"north": <RoomObject>}
        self.enemies = enemies if enemies is not None else []
        self.items = items if items is not None else []
        self.visited = False

    def add_exit(self, direction, room):
        self.exits[direction] = room

    def add_enemy(self, enemy):
        self.enemies.append(enemy)

    def remove_enemy(self, enemy):
        if enemy in self.enemies:
            self.enemies.remove(enemy)
            return True
        return False

    def add_item(self, item):
        self.items.append(item)


    def remove_item(self, item_name_to_remove):
        for item in self.items:
            if item.lower() == item_name_to_remove.lower():
                self.items.remove(item)
                return True
        return False

    def get_description(self):
        exit_descriptions = []
        for direction in self.exits:
            exit_descriptions.append(f"There is a door to the {direction.capitalize()}.")
        
        items_description = ""
        if self.items:
            items_description = "You see: " + ", ".join(self.items) + "."
        
        enemies_description = ""
        if self.enemies:
            enemy_names = [str(enemy) for enemy in self.enemies]
            enemies_description = "You encounter: " + ", ".join(enemy_names) + "."

        return (f"{self.description}\n"
                f"{' '.join(exit_descriptions)}\n"
                f"{items_description}\n"
                f"{enemies_description}").strip()


class Dungeon:
    def __init__(self, size=5, stage_level=1, is_boss_stage=False):
        self.size = size
        self.stage_level = stage_level
        self.is_boss_stage = is_boss_stage
        self.rooms = {}  # {(x, y): RoomObject}
        self.start_room_coords = (0, 0)
        self._generate_dungeon()

    def _generate_dungeon(self):
        # Create a grid of rooms
        for x in range(self.size):
            for y in range(self.size):
                description = f"You are in a dimly lit room at ({x},{y})."
                self.rooms[(x, y)] = Room(description)

        # Connect rooms randomly
        for x in range(self.size):
            for y in range(self.size):
                current_room = self.rooms[(x, y)]

                # Connect North-South
                if y < self.size - 1:
                    north_room = self.rooms[(x, y + 1)]
                    current_room.add_exit("north", north_room)
                    north_room.add_exit("south", current_room)

                # Connect East-West
                if x < self.size - 1:
                    east_room = self.rooms[(x + 1, y)]
                    current_room.add_exit("east", east_room)
                    east_room.add_exit("west", current_room)

        # Add enemies and items
        if self.is_boss_stage:
            # Place boss in the exit room
            boss_room_coords = (self.size - 1, self.size - 1)
            boss_room = self.rooms[boss_room_coords]
            
            boss = Dragon() # Use Dragon as a boss for now
            boss.max_hp = int(boss.max_hp * (1 + (self.stage_level - 1) * 0.5)) # Boss HP scales more
            boss.hp = boss.max_hp
            boss.attack = int(boss.attack * (1 + (self.stage_level - 1) * 0.2))
            boss.defense = int(boss.defense * (1 + (self.stage_level - 1) * 0.1))
            boss.xp_drop = int(boss.xp_drop * (1 + (self.stage_level - 1) * 0.2))
            boss.gold_drop = int(boss.gold_drop * (1 + (self.stage_level - 1) * 0.2))
            boss_room.add_enemy(boss)
            boss_room.description += f" A fearsome {boss.name} guards the portal to the next stage!"
        else:
            # Add some random enemies and items to rooms (excluding the starting room)
            for coords, room in self.rooms.items():
                if coords != self.start_room_coords:
                    if random.random() < 0.3 + (self.stage_level * 0.05):  # Increased chance for enemies per stage
                        enemy_type = random.choice([Slime, Skeleton])
                        # Scale enemy stats based on stage_level
                        scaled_enemy = enemy_type()
                        scaled_enemy.max_hp = int(scaled_enemy.max_hp * (1 + (self.stage_level - 1) * 0.2))
                        scaled_enemy.hp = scaled_enemy.max_hp
                        scaled_enemy.attack = int(scaled_enemy.attack * (1 + (self.stage_level - 1) * 0.1))
                        scaled_enemy.defense = int(scaled_enemy.defense * (1 + (self.stage_level - 1) * 0.05))
                        scaled_enemy.xp_drop = int(scaled_enemy.xp_drop * (1 + (self.stage_level - 1) * 0.1))
                        scaled_enemy.gold_drop = int(scaled_enemy.gold_drop * (1 + (self.stage_level - 1) * 0.1))
                        room.add_enemy(scaled_enemy)
                    if random.random() < 0.2:  # 20% chance for an item
                        room.add_item(random.choice(["Health Potion", "Rusty Sword", "Small Shield"]))

        # Designate an exit room for stage progression (e.g., bottom-right corner)
        exit_coords = (self.size - 1, self.size - 1)
        if exit_coords != self.start_room_coords and not self.is_boss_stage: # Ensure exit is not start and not boss stage
            exit_room = self.rooms[exit_coords]
            exit_room.description += " A glowing portal shimmers in the corner, leading to the next stage."

    def get_room(self, coords):
        return self.rooms.get(coords)

    def get_start_room(self):
        return self.rooms[self.start_room_coords]

class GameEngine:
    def __init__(self):
        self.player = Player()
        self.current_stage = 1
        self.dungeon = Dungeon(stage_level=self.current_stage)
        self.current_room = self.dungeon.get_start_room()
        self.game_state = GameState.EXPLORATION
        self.current_enemy = None # For battle state

    def start_game(self):
        print("Welcome to the Python Dungeon Crawler!")
        self.game_loop()

    def game_loop(self):
        while self.game_state != GameState.GAME_OVER:
            if self.game_state == GameState.EXPLORATION:
                self._exploration_state()
            elif self.game_state == GameState.BATTLE:
                self._battle_state()
            elif self.game_state == GameState.HUB:
                self._hub_state()
            
            # Simple check for game over (player defeated)
            if self.player.hp <= 0:
                self.game_state = GameState.GAME_OVER
                print("\n" + "="*30)
                print(r"""
  _   _   _   _     _   _   _   _   _  
 / \ / \ / \ / \   / \ / \ / \ / \ / \ 
( G | A | M | E ) ( O | V | E | R | ! )
 \_/ \_/ \_/ \_/   \_/ \_/ \_/ \_/ \_/
""")
                print("="*30)
                print("You have been defeated!")

    def next_stage(self):
        print("\nYou have cleared the current stage!")
        self.game_state = GameState.HUB # Transition to hub state

    def _hub_state(self):
        print("\n" + "="*30)
        print("WELCOME TO THE HUB")
        print("="*30)
        print("Here you can rest, upgrade your stats, or buy items.")
        
        while True:
            choice = input("What would you like to do? [Upgrade, Shop (not implemented), Continue] ").lower().strip()
            if choice == "upgrade":
                self._handle_upgrades()
            elif choice == "shop":
                print("The shopkeeper is currently away. Come back later!")
            elif choice == "continue":
                self.current_stage += 1
                print(f"\n--- Entering Stage {self.current_stage}! ---\n")
                
                is_boss_stage = (self.current_stage % 5 == 0)
                self.dungeon = Dungeon(stage_level=self.current_stage, is_boss_stage=is_boss_stage)
                self.current_room = self.dungeon.get_start_room()
                self.game_state = GameState.EXPLORATION
                break
            else:
                print("Invalid choice.")

    def _handle_upgrades(self):
        print("\n--- UPGRADE STATS ---")
        print(f"Current Gold: {self.player.gold}")
        print(f"Current XP: {self.player.xp}")
        print(f"1. Upgrade Attack (+5 Attack, Cost: 20 Gold, 50 XP)")
        print(f"2. Upgrade Max HP (+20 Max HP, Cost: 15 Gold, 40 XP)")
        print(f"3. Back")

        while True:
            upgrade_choice = input("Choose an upgrade: ").lower().strip()
            if upgrade_choice == "1":
                if self.player.gold >= 20 and self.player.xp >= 50:
                    self.player.attack += 5
                    self.player.gold -= 20
                    self.player.xp -= 50
                    print(f"Attack upgraded! New Attack: {self.player.attack}")
                else:
                    print("Not enough gold or XP.")
                break
            elif upgrade_choice == "2":
                if self.player.gold >= 15 and self.player.xp >= 40:
                    self.player.max_hp += 20
                    self.player.hp += 20 # Heal player to new max hp
                    self.player.gold -= 15
                    self.player.xp -= 40
                    print(f"Max HP upgraded! New Max HP: {self.player.max_hp}, Current HP: {self.player.hp}")
                else:
                    print("Not enough gold or XP.")
                break
            elif upgrade_choice == "3":
                break
            else:
                print("Invalid choice.")

    def _exploration_state(self):
        print("\n" + "="*30)
        print(f"EXPLORATION (Stage {self.current_stage})")
        print("="*30)
        print(self.current_room.get_description())

        # Check if player is in the exit room
        exit_coords = (self.dungeon.size - 1, self.dungeon.size - 1)
        if (self.current_room == self.dungeon.rooms.get(exit_coords) and
            all(not room.enemies for room in self.dungeon.rooms.values())): # Check if all enemies in dungeon are defeated
            print("\nYou found the exit to the next stage!")
            self.next_stage()
            return # Skip command parsing for this turn to display new room description
        
        # Random encounter chance if no enemies in current room
        if not self.current_room.enemies and random.random() < 0.2: 
            enemy_type = random.choice([Slime, Skeleton])
            scaled_enemy = enemy_type()
            scaled_enemy.max_hp = int(scaled_enemy.max_hp * (1 + (self.current_stage - 1) * 0.2))
            scaled_enemy.hp = scaled_enemy.max_hp
            scaled_enemy.attack = int(scaled_enemy.attack * (1 + (self.current_stage - 1) * 0.1))
            scaled_enemy.defense = int(scaled_enemy.defense * (1 + (self.current_stage - 1) * 0.05))
            scaled_enemy.xp_drop = int(scaled_enemy.xp_drop * (1 + (self.current_stage - 1) * 0.1))
            scaled_enemy.gold_drop = int(scaled_enemy.gold_drop * (1 + (self.current_stage - 1) * 0.1))
            self.current_enemy = scaled_enemy

            print(f"A wild {self.current_enemy.name} appears!")
            self.game_state = GameState.BATTLE
            return
            
        command = input("What do you want to do? ").lower().strip()
        self._parse_exploration_command(command)


    def _battle_state(self):
        print("\n" + "#"*30)
        print(r"""
██████╗  █████╗ ████████╗████████╗██╗     ███████╗
██╔══██╗██╔══██╗╚══██╔══╝╚══██╔══╝██║     ██╔════╝
██████╔╝███████║   ██║      ██║   ██║     █████╗  
██╔══██╗██╔══██║   ██║      ██║   ██║     ██╔══╝  
██████╔╝██║  ██║   ██║      ██║   ███████╗███████╗
╚═════╝ ╚═╝  ╚═╝   ╚═╝      ╚═╝   ╚══════╝╚══════╝
""")
        print("#"*30)

        # Display stats
        print(f"{self.player.name} HP: {self.player.hp}/{self.player.max_hp} | Attack: {self.player.attack} | Defense: {self.player.defense}")
        print(f"{self.current_enemy.name} HP: {self.current_enemy.hp}/{self.current_enemy.max_hp} | Attack: {self.current_enemy.attack} | Defense: {self.current_enemy.defense}")
        print("-"*30)

        action = input("Choose an action: [Attack, Magic, Item, Flee] ").lower().strip()
        
        player_turn_over = False

        if action == "attack":
            player_damage = max(0, self.player.attack - self.current_enemy.defense)
            enemy_dead = self.current_enemy.take_damage(player_damage)
            print(f"You attack the {self.current_enemy.name} for {player_damage} damage.")
            player_turn_over = True
            
            if enemy_dead:
                print(f"The {self.current_enemy.name} is defeated!")
                self.player.add_xp(self.current_enemy.xp_drop)
                self.player.add_gold(self.current_enemy.gold_drop)
                print(f"You gained {self.current_enemy.xp_drop} XP and {self.current_enemy.gold_drop} gold.")
                self.current_room.remove_enemy(self.current_enemy) # Remove enemy from the room
                self.game_state = GameState.EXPLORATION
                self.current_enemy = None
                return # Battle ends here
        elif action == "magic":
            print("You wave your hands, but nothing happens. (Magic not implemented yet)")
            player_turn_over = True
        elif action == "item":
            print("You fumble in your bag. (Items not implemented yet)")
            player_turn_over = True
        elif action == "flee":
            if random.random() > 0.5: # 50% chance to flee
                print("You successfully fled the battle!")
                self.game_state = GameState.EXPLORATION
                self.current_enemy = None
                return # Battle ends here
            else:
                print("You failed to flee!")
                player_turn_over = True
        else:
            print("Invalid battle action. You lose your turn.")
            player_turn_over = True

        # Enemy's turn if player's turn is over and battle is still ongoing
        if player_turn_over and self.game_state == GameState.BATTLE:
            enemy_damage = max(0, self.current_enemy.attack - self.player.defense)
            player_dead = self.player.take_damage(enemy_damage)
            print(f"The {self.current_enemy.name} attacks you for {enemy_damage} damage.")
            if player_dead:
                print("You have been defeated!")
                self.game_state = GameState.GAME_OVER


    def _parse_exploration_command(self, command):
        if command.startswith("move"):
            # Split only once to handle multi-word directions like "move north" or "move portal"
            parts = command.split(" ", 1) 
            if len(parts) > 1:
                direction = parts[1]
                if direction == "portal":
                    exit_coords = (self.dungeon.size - 1, self.dungeon.size - 1)
                    if (self.current_room == self.dungeon.rooms.get(exit_coords) and
                        all(not room.enemies for room in self.dungeon.rooms.values())):
                        print("You step into the shimmering portal...")
                        self.next_stage()
                    else:
                        print("There is no active portal here, or the current stage is not yet cleared.")
                else:
                    self._move_player(direction)
            else:
                print("Move where? Specify a direction (e.g., 'move north') or 'move portal'.")
        elif command == "status":
            print(self.player.get_status())
        elif command == "inventory":
            print(f"Inventory: {', '.join(self.player.inventory) if self.player.inventory else 'Empty'}")
        elif command.startswith("take"):
            item_name = " ".join(command.split(" ")[1:])
            if self.current_room.remove_item(item_name):
                self.player.add_item(item_name)
                print(f"You took the {item_name}.")
            else:
                print(f"Could not find '{item_name}' in this room.")
        elif command.startswith("attack"):
            if self.current_room.enemies:
                print(f"You prepare to fight the {self.current_room.enemies[0].name}!")
                self.current_enemy = self.current_room.enemies[0] # Target the first enemy
                self.game_state = GameState.BATTLE
            else:
                print("There are no enemies to attack in this room.")
        elif command == "help":
            print("\n--- Available Commands ---")
            print("  move <direction> (e.g., 'move north', 'move east')")
            print("  move portal (to advance to the next stage if cleared)")
            print("  status (display player stats)")
            print("  inventory (display player inventory)")
            print("  take <item name> (pick up an item from the room)")
            print("  attack (initiate battle with an enemy in the room)")
            print("  help (display this list)")
            print("--------------------------")
        else:
            print("Unknown command. Type 'help' for available commands.")


    def _move_player(self, direction):
        new_room = self.current_room.exits.get(direction)
        if new_room:
            self.current_room = new_room
            print(f"You moved {direction}.")
        else:
            print("You can't go that way.")

if __name__ == "__main__":
    game = GameEngine()
    game.start_game()