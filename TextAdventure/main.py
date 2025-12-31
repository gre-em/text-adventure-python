import json
import os


class Scene:
    def __init__(self, atts):
        self.interactables = {}
        for att in atts:
            if att == "interactables":
                for intr in atts[att]:
                    self.interactables[intr] = self.Interactable(atts[att][intr])
            else:
                setattr(self, att, atts[att])

    class Interactable:
        def __init__(self, atts):
            for att in atts:
                setattr(self, att, atts[att])


# load scene from scenes folder (locations your havent seen in your playthrough
def load_scene(_name):
    scene_data = load_data("Scenes/" + _name)
    for scene in scene_data:
        scnDict[scene] = Scene(scene_data[scene])


# load save game
def load_save_scenes():
    scenes_data = load_data("SaveFiles/" + saveFolder + "/scenes")
    for scene in scenes_data:
        scnDict[scene] = Scene(scenes_data[scene])


# load player stats, when resuming a save game
def load_player():
    player = load_data("SaveFiles/" + saveFolder + "/player")
    global inventory
    inventory = player["inventory"]
    func_match = find_match(player["location"], scnDict)
    global scnName
    scnName = func_match
    return scnDict[func_match]


# when changing location / either take from cache, or read data if doesnt exist
def switch_scene(scene_name):
    if cScn != 0:
        scnDict[scnName] = cScn
    try:
        return scnDict[scene_name]
    except KeyError:
        load_scene(scene_name)
        return scnDict[scene_name]


# save game on quitting
def save_game():
    # create directory if doesn't exist
    if not os.path.exists("SaveFiles/" + saveFolder):
        os.mkdir("SaveFiles/" + saveFolder)
    # save inventory / location in player.json
    _data = {"inventory": inventory, "location": scnName}
    with open("SaveFiles/" + saveFolder + "/player.json", "w") as sfile:
        json.dump(_data, sfile, indent=3)
    # save scenes + interactables in scenes.json
    _data = {}
    for scene in scnDict:
        scene_data = scnDict[scene].__dict__
        for inter in scene_data["interactables"]:
            scene_data["interactables"][inter] = scnDict[scene].interactables[inter].__dict__
        _data[scene] = scene_data
    with open("SaveFiles/" + saveFolder + "/scenes.json", "w") as sfile:
        json.dump(_data, sfile, indent=3)


# read any data file, used in different functions
def load_data(file_path):
    with open(file_path + ".json", "r") as lfile:
        data = json.load(lfile)
    return data


# find match between input and e.g. inventory/scenes/etc...
def find_match(lock, keys):
    matched = ""
    for key in keys:
        if key in lock:
            matched = key
            break
    return matched


# just a way of giving the player time to read before the next block appears
def eat_input():
    print("[ENTER]")
    sad_unused_variable = input()


# print out information about the player
def print_info():
    print("Location: " + scnName)
    print("Objects: " + ", ".join(x for x in cScn.interactables))
    if inventory:
        print("Inventory: " + ", ".join(x for x in inventory))
    print("Locations: " + ", ".join(x for x in cScn.connections))


# print help. it prints the help sheet. if you need help.
def print_help():
    print("HELPGUIDE:\n" +
          "> Action commands:\n" +
          "'examine' to examine an object in the scene\n" +
          "'use' to use an item in your inventory on an object\n" +
          "'move to' to enter target connected scene\n" +
          "\n" +
          "> Menu options\n" +
          "'help' if you're lost\n" +
          "'quit' to save and quit the game\n" +
          "\n" +
          "TIP: You can combine keywords with an item/object/scene (respectively),\n" +
          "for example: 'examine car' or 'use keys door'." +
          "\n")


# i am not sure what that is actually about?? maybe i will come back to it, when i remember
def initiate_game():
    pass


# you can tell...
if __name__ == "__main__":
    ending = 0
    scnDict = {}
    scnName = ""
    cScn = 0
    inventory = []

    # initiate(load savefiles, or create a new ones)
    print("How do you want your savefile to be named?", end="")
    if os.listdir("SaveFiles"):
        print(" (or load existing one: " + ", ".join(os.listdir("SaveFiles")), end="): ")
    else:
        print(": ", end="")
    saveFolder = input()
    if saveFolder in os.listdir("SaveFiles"):
        print("")
        load_save_scenes()
        cScn = load_player()
    else:
        with open("Scenes/start.json", "r") as file:
            start = json.load(file)
            scnName = start["startlocation"]
            cScn = switch_scene(scnName)
            print("\n" + start["introduction"])
            eat_input()

    print_help()
    eat_input()

    # game loop
    while ending == 0:
        # print information about the player and his location
        print(cScn.description)
        eat_input()
        print_info()

        # take player input, try matching with possible commands
        plInput = input("Your action: ")
        match = find_match(plInput, ["examine", "use", "move to", "help", "quit"])
        # scene loop (for as long the player stays in that area)
        while not any(x == match for x in ["quit", "move to"]):
            while match == "":
                plInput = input("That is no viable move! Try again: ")
                match = find_match(plInput, ["examine", "use", "move to", "help", "quit"])
            # if examine in player input
            if match == "examine":
                match = find_match(plInput, [inter for inter in cScn.interactables])
                while match == "":
                    plInput = input(
                        "What do you want to examine? ({}): ".format(", ".join([inter for inter in cScn.interactables]))
                    )
                    match = find_match(plInput, [inter for inter in cScn.interactables])
                print("\n" + cScn.interactables[match].description)
                if cScn.interactables[match].item and cScn.interactables[match].item not in inventory:
                    print("You've found: " + cScn.interactables[match].item)
                    inventory.append(cScn.interactables[match].item)
                    eat_input()
                    print_info()
                plInput = input("Your action: ")
                match = find_match(plInput, ["examine", "use", "move to", "help", "quit"])
            elif match == "use":
                if inventory:
                    match = find_match(plInput, [item for item in inventory])
                    while match == "":
                        plInput = input(
                            "What item do you want to use? ({}): ".format(", ".join([item for item in inventory]))
                        )
                        match = find_match(plInput, [item for item in inventory])
                    itemMatch = match
                    match = find_match(plInput, [inter for inter in cScn.interactables])
                    while match == "":
                        plInput = input(
                            "What do you want to use {} on? ({}): ".format(
                                itemMatch, ", ".join([inter for inter in cScn.interactables])
                            )
                        )
                        match = find_match(plInput, [inter for inter in cScn.interactables])
                    if hasattr(cScn.interactables[match], "returnItem") \
                            and cScn.interactables[match].returnItem == itemMatch:
                        print("\n" + cScn.interactables[match].returnMessage)
                        inventory.remove(itemMatch)
                        print("Something happening. But the coder was too lazy to implement it yet...")
                        eat_input()
                        print_info()
                    else:
                        print("\nThat really won't work!")
                        eat_input()
                        print_info()
                else:
                    print("\nNo items to use!")
                    eat_input()
                    print_info()
                plInput = input("Your action: ")
                match = find_match(plInput, ["examine", "use", "move to", "help", "quit"])
            elif match == "help":
                print_help()
                eat_input()
                print_info()
                plInput = input("Your move: ")
                match = find_match(plInput, ["examine", "use", "move to", "help", "quit"])
        if match == "quit":
            save_game()
            ending = 1
        elif match == "move to":
            match = find_match(plInput, [x for x in cScn.connections])
            while match == "":
                plInput = input("Where do you want to move to? ({}): ".format(", ".join([x for x in cScn.connections])))
                match = find_match(plInput, [x for x in cScn.connections])
            cScn = switch_scene(match)
            scnName = match
            print("")
    # if end is reached (out of "while true loop")
    if ending == 1:
        print("Game quit. Savefile created!"
              "")
    elif ending == 2:
        print("game is over. this is a placeholder. maybe put this text in a file instead...")
