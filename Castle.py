import time 

class Player():

    def __init__(self):
        self.inventory = []

    def go(self, direction):
        if direction in world.current_room.linked_rooms:
            door = world.doors[world.current_room.room_name+world.current_room.linked_rooms[direction].room_name]
            if door.typ in  ["open", "unlocked"]:
                world.current_room = world.rooms[world.current_room.linked_rooms[direction].room_name]
                print(world.current_room.short_description)
            elif door.typ ==  "locked":
                print(f'The door to the {door.room_to} is locked.')
            elif door.typ == "closed":  
                print(f'The door to the {door.room_to} is closed. Open it!')
        else:
            print("Are you sure you want to run into a wall?")

    def take(self, item):
        try:
            item = game.items[item]
            if item not in world.player.inventory and item in world.current_room.items and item.typ in ["USE", "MOVE"]:  
                world.player.inventory.append(item)
                world.current_room.items.remove(item)
                print(f'Ok, you took a {item.name}! {item.item_description}')
            elif item in world.player.inventory:  
                print("Look, you already have it!")
            elif item in world.current_room.items and item.typ == 'STATIONARY':   
                print(item.item_description)
                print("You wish you could have it, right?") 
            elif item not in world.current_room.items:   
                print("Are you blind? There is nothing like this here.") 
        except KeyError:
            print("Are you blind? There is nothing like this here.")

    def release(self, item):
        item = game.items[item]
        if item in world.player.inventory:
            world.player.inventory.remove(item) 
            world.current_room.items.append(item)
            print(f"Ok, you dropped {item.name}.")
        else:
            print("How can you drop something you don't have?")
    
    def show(self):
        print(f'You are in the {world.current_room.room_name}.')
        print(world.current_room.long_description)
        print('-> You can go in the following direction:')
        for w in world.current_room.linked_rooms.keys():
            print('* ' + w)
        if world.current_room.items: 
            print('-> You see the following items:')
            for i in world.current_room.items:
                i.describe()
        
    def commands(self):  
        commands =  {'go N': 'to go north',
                    'go S': 'to go south',
                    'go W': 'to go west',
                    'go E': 'to go east',
                    'help': 'to see commands',
                    'show':'to see the room',
                    'quit': 'quit the game',
                    'inventory': 'check what you have taken',
                    'take (item name)': 'take an item',
                    'release (item name)': 'drop an item',
                    'unlock (room you want to unlock)': 'unlock the door',
                    'open (room you want to unlock)': 'open the door',
                    'drink (item name)': 'drink liquid from a full item',
                    'fill (item name)': 'fill an empty item'}
        for command, description in commands.items():
            print('*', command, '->', description)

    def holding(self):
        if world.player.inventory:
            print("Inventory:")
            for item in world.player.inventory:
                print('* ' + item.name.title())
        else:
            print("It's empty here.")

    def quit(self):
        print("Ok, your choice. Bye!")
        exit()     

    def drink(self, item):
        try:
            item = game.items[item]
            if item.state == "full" and world.current_room.action == "win" and item in world.player.inventory:
                print('''You drink the smelly mixture and feel how your body starts to shrink.
                        You run fast through the canal to find yourself outside the castle.''')
                time.sleep(1)
                print("Congratulations, you're free! Now you need to steal")
                time.sleep(0.5)
                print('sorry...')
                time.sleep(0.5)
                print('find, some clothes to put on your, again, human-sized body!')
                exit()
            elif item.state != "full" and world.current_room.action == "win" and item in world.player.inventory:
                print("Ok, you're on the right track, but you need find something to drink first.")
            elif item.state == "full" and world.current_room.action != "win" and item in world.player.inventory:
                print("You sure? You just have once chance! Better try this somewhere else.")
            else:
                print("You need something to drink first, right?")
        except KeyError:
            print("You have nothing like that.") 

    def fill(self, item):
        try:
            item = game.items[item]
            if item.action.strip("\n") == "fill" and world.current_room.action == "fill" and item in world.player.inventory:
                print(f'You have filled {item.name}.')
                item.set_state("full")
                item.set_action("drink")
            elif item.action == "fill" and world.current_room.action != "fill" and item in world.player.inventory:
                print("You don't see anything that could be poured into the vial.")
            elif item.state == "full" and item in world.player.inventory:
                print("You have already filled the {item}.")
            else:
                print("What do you want to fill?")   
        except KeyError:
            print("You have nothing like that.")     

    def unlock(self, door):
        try:
            item = game.items["key"]
            door_to_unlock = world.doors[world.current_room.room_name+door]
            door_to_unlock_rev = world.doors[door+world.current_room.room_name]
            if door_to_unlock.typ == "locked" and item in world.player.inventory and door_to_unlock.room_from ==  world.current_room.room_name:
                door_to_unlock.set_typ("unlocked")
                door_to_unlock_rev.set_typ("unlocked")
                world.player.inventory.remove(item)
                print("You have unlocked the door.")
            else:
                print("You can't do this.")
        except KeyError:
            print("You can't really do it.")   
    
    def open(self, door):
        try:
            door_to_unlock = world.doors[world.current_room.room_name+door]
            door_to_unlock_rev = world.doors[door+world.current_room.room_name]
            if door_to_unlock.typ == "closed" and door_to_unlock.room_from ==  world.current_room.room_name:
                door_to_unlock.set_typ("open")
                door_to_unlock_rev.set_typ("unlocked")
                print("You have opened the door.")
            else:
                print("You can't do this.")
        except KeyError:
            print("You can't really do it.")


class Castle(Player):
    
    current_room = None
    
    def __init__(self, data):
        self.data = data
        self.rooms = {}
        self.doors = {}
        self.load_room(data)
        self.first_room(data)
        self.player = Player()

    def load_room(self, filename):
        file = open(filename, "r")
        for line in file:
            if line[:4] == "room":
                room = line.strip("room ").strip("\n").split(" ")
                try:
                    action = room[1]
                except IndexError:
                    action = None
            if "short_description" in line:
                description = line.strip("short_description: ").strip("\n")
            if "long_description" in line:
                long_description = line.strip("long_description: ").strip("\n")
                self.rooms[room[0]] = Room(room[0], description, action, long_description)
        file.close()


    def first_room(self, filename):
        file = open(filename, "r")
        for line in file:
            if "start" in line:
                first_room = line.strip("start ").strip("\n").split(" ")
                room = (first_room[0])
                self.current_room = self.rooms[room]
        file.close()


class Game(Castle):
    def __init__(self):
        self.load_door(world.data)
        self.items = {}
        self.load_items(world.data)

    def load_door(self, filename):
        file = open(filename, "r")
        for line in file:
            if "door" in line:
                d = line.strip("door ").split(" ")
                direction = d[0]
                typ = d[1]
                room_from = d[2]
                room_to = d[3]
                passage = Door(direction, typ, room_from, room_to)
                if passage.typ == "closed" or "locked":
                    world.doors[passage.room_from+passage.room_to] = passage
                    world.doors[passage.room_to+passage.room_from] = passage
        file.close()

    def load_items(self, filename):
        file = open(filename, "r")
        for line in file:
            if "item" in line:
                d = line.strip("item ").split(" ")
                name = d[0]
                room = d[1]
                typ = d[2]
                try:
                    if d[3] and d[4]:
                        action = d[3]
                        state = d[4]
                except IndexError:
                    action = None
                    state = None
            if "i_description" in line:
                item_description = line.strip("i_description: ").strip("\n")
                item = Item(name, room, typ, action, state, item_description)
                item.item_description
                self.items[item.name] = item               
        file.close()
        
    def start_action(self): 
        print("Welcome to the Castle!")
        time.sleep(1)
        print(''' 
                                  o                    
                       _---|         _ _ _ _ _ 
                    o   ---|     o   ]-I-I-I-[ 
   _ _ _ _ _ _  _---|      | _---|    \ ` ' / 
   ]-I-I-I-I-[   ---|      |  ---|    |.   | 
    \ `   '_/       |     / \    |    | /^\| 
     [*]  __|       ^    / ^ \   ^    | |*|| 
     |__   ,|      / \  /    `\ / \   | ===| 
  ___| ___ ,|__   /    /=_=_=_=\   \  |,  _|
  I_I__I_I__I_I  (====(_________)___|_|____|____
  \-\--|-|--/-/  |     I  [ ]__I I_I__|____I_I_| 
   |[]      '|   | []  |`__  . [  \-\--|-|--/-/  
   |.   | |' |___|_____I___|___I___|---------| 
  / \| []   .|_|-|_|-|-|_|-|_|-|_|-| []   [] | 
 <===>  |   .|-=-=-=-=-=-=-=-=-=-=-|   |    / \  
 ] []|`   [] ||.|.|.|.|.|.|.|.|.|.||-      <===> 
 ] []| ` |   |/////////\\\\\\\\\\.||__.  | |[] [ 
 <===>     ' ||||| |   |   | ||||.||  []   <===>
  \T/  | |-- ||||| | O | O | ||||.|| . |'   \T/ 
   |      . _||||| |   |   | ||||.|| |     | |
../|' v . | .|||||/____|____\|||| /|. . | . ./
.|//\............/...........\........../../\\\      
        ''')
        time.sleep(2)
        print( '''The room is dark and you have no idea how have you ended up here.
        The last thing you can remember is a weirdly pale guy,
        who approached you at the bar. ''')
        time.sleep(2)
        print( '''It seems that you are locked behind the bars. Oh no...You're locked in the Cell!
        You need to figure out how to escape. You can see something shiny on the floor. What is that? ''')
        time.sleep(3)
        print("What do you do?")
        time.sleep(1)
        print("Here are your choices:")
        time.sleep(1)
        self.commands()
        time.sleep(1.5)
        print("So what is your choice? Maybe try to see the room!")

    def play(self, command_status=True):
        self.start_action()
        command = '  '
        while command_status:
            command = input('--> ')
            if command == '':
                print('You have to say what it is you want to do!')
                command = '#'
            command = command.split()
            user_command = command[0].lower()
            if len(command) == 1:
                if user_command == 'show':
                    self.show()
                elif user_command == 'help':
                    self.commands()
                elif user_command == 'inventory':
                    world.player.holding()
                elif user_command == 'quit':
                    self.quit()
                elif user_command == 'take':
                    print('What do you want to take?')   
                elif user_command == 'go':
                    print('Where do you want to go?')  
                elif user_command == 'unlock':
                    print('Which room do you want to unlock?')
                elif user_command == 'open':
                    print("Which room do you want to open?")
                elif user_command == 'fill':
                    print("What item do you want to fill?")
                elif user_command == 'drink':
                    print("What do you want to drink?")
                elif user_command == 'release':
                    print("What item do you want to drop?") 
                else:
                    print('Invalid command. You can type help to see available commands.')
            if len(command) == 2:
                if user_command in 'go':
                    if command[1] in ["E","W", "S", "N"]:
                        self.go(command[1])
                    else:
                        print("It's not possible.")
                elif user_command == 'take':
                    self.take(command[1])     
                elif user_command == 'unlock':
                    self.unlock(command[1].title())
                elif user_command == 'open':
                    self.open(command[1].title())
                elif user_command == 'fill':
                    self.fill(command[1])
                elif user_command == 'drink':
                    self.drink(command[1])
                elif user_command == 'release':
                    self.release(command[1])
                else:
                    print('Invalid command. You can type help to see available commands.')


class Room():
    def __init__(self, room_name, short_description, action, long_description): 
        self.room_name = room_name
        self.action  = action
        self.short_description = short_description 
        self.linked_rooms = {}
        self.items = []
        self.long_description = long_description
        
    def add_item(self, item):
        self.items.append(item)

        
class Door():
    def __init__(self, direction, typ, room_from, room_to):
        self.direction = direction
        self.typ = typ
        self.room_from = room_from.strip("\n")
        self.room_to = room_to.strip("\n")
        self.passages()

    def passages(self):
        if self.room_from in world.rooms:
                world.rooms[self.room_from].linked_rooms[self.direction[2]] = world.rooms[self.room_to]
        if self.room_to in world.rooms:
                world.rooms[self.room_to].linked_rooms[self.direction[0]] = world.rooms[self.room_from]
            
    def set_typ(self, typ):
        self.typ = typ


class Item():
    def __init__(self, name, room, typ, action, state, item_description):
        self.name = name
        self.room = room
        self.state = state
        self.typ = typ.strip('\n')
        self.action = action
        self.item_description = item_description
        self.add_to_room()

    def add_to_room(self):
        if self.room in world.rooms:
                world.rooms[self.room].items.append(self)  
    
    def describe(self):
        print("The " + self.name + " is here." )
    
    def set_state(self, state):
        self.state = state

    def set_action(self, action):
        self.action = action


if __name__ == '__main__':
    import sys
    from sys import stdin, stderr
    configuration_file = sys.argv[1]
    world = Castle(configuration_file)
    game = Game()
    game.play()






