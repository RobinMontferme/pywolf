
from random import randint

class Player:
    def __init__(self):
        self.name =""
        self.role = "role"
        self.votes = 0
        self.alive = True
        self.hasPower = False
        self.isCaptain = False
        self.memory = []
        self.lover = None

    def display(self):
        if self.alive:
            print(self.name)
        else:
            if self.lover:
                print(self.name +"("+self.role +") <3")
            else:
                print(self.name +"("+self.role +")")    
    def checkRoleIs(self,role):
        return (type(self.role) is role)

    def vote(self,list):
        chosenPlayer = self
        choice = list.index(self)
        if self.memory: #if the player now the roles of some other player we must review them first
            targets = []
            for player,role in self.memory:
                if role in werewolfRoles: #if any wolf is found they must be targetted
                    targets.append(player)
            if targets: #if wolves have been found the player will vote among them, if not the vote is normal
                list = targets
        while (chosenPlayer == self) or not chosenPlayer.alive:
            choice = randint(0,len(list)-1)
            chosenPlayer = list[choice]
        return choice
    def forgetDeadPlayers(self):
        self.memory[:] =[mem for mem in self.memory if mem[0].alive]


class Villager(Player):
    def __init__(self):
        super().__init__()
        self.role = "Villager"

        
class Werewolf(Player): 
    def __init__(self):
        super().__init__()
        self.role ="Werewolf"
        self.allies = []
    def vote(self,list):
        chosenPlayer = self
        choice = list.index(self)
        while ((chosenPlayer == self) or not chosenPlayer.alive) or (chosenPlayer in self.allies):
            choice = randint(0,len(list)-1)
            chosenPlayer = list[choice]
        return choice

class Ambiguous(Player):
    def __init__(self):
        super().__init__()
        self.name = "Ambiguous"
    def vote(self,list):
        pass
class Loner(Player):
    def __init__(self):
        super().__init__()
        self.name = "Loner"
    def vote(self,list):
        pass
#TODO finish  test FortuneTeller


class FortuneTeller(Villager):
    def __init__(self):
        super().__init__()
        self.role = "Fortune Teller"
        self.hasPower = True

    def tellFortune(self, list):
        chosenTarget = self
        while(chosenTarget == self or (chosenTarget, chosenTarget.role) in self.memory):
            chosenTarget = list[randint(0, len(list)-1)]
        print("The Fortune Teller saw that " +chosenTarget.name + " is a "+chosenTarget.role)

class Hunter(Villager):
    def __init__(self):
        super().__init__()
        self.role = "Hunter"
        self.hasPower = True

    def shootOnDeath(self,list):
        print("The Hunter shoot someone on is dying breath")
        return self.vote(list) 

class Cupid(Villager):
    def __init__(self):
        super().__init__()
        self.role = "Cupid"
        self.hasPower = True
    def chooseLovers(self,list):
        loverA = list[randint(0,len(list)-1)]
        loverB = loverA
        while loverB == loverA:
            loverB = list[randint(0,len(list)-1)]
        loverA.lover = loverB
        loverB.lover = loverA
        print(loverA.name +" and "+loverB.name+" are lovers")

class Witch(Villager):
    def __init__(self):
        super().__init__()
        self.role = "Witch"
        self.hasPower = True
        self.healthPotion = True
        self.healUseChange = 65
        self.poisonVial = True
        self.poisonUseChange = 30
    def heal(self,victim,victimsList,list):
        if list[victim] == self:
            self.healthPotion = False
            print("The witch healed herself")
            victimsList.remove(victim)
            return list.index(self)
        else:
            if victimsList and randint(0,101) >= self.healUseChange: #if there is a victim she can save it
                self.healthPotion = False
                print("The witch healed someone")
                victimsList.remove(victim)
                return victim
            else:
                print("The witch did not use her healing potion")
                return None

    def poison(self,saved,list):
        targets = []
        for player,role in self.memory: #the witch first targets are the wolves she is aware of
            if role in werewolfRoles:
                targets.append(player)

        if targets: # if she is aware of werewolves the then kill one
            self.poisonVial = False
            print("The witch use poison on a wolf")
            return targets[randint(0,len(targets)-1)]

        if randint(0,101)>=self.poisonUseChange: #if she doesn't know any wolf she still can decide to kill someone
            self.poisonVial = False
            print("The witch killed someone")
            choice = list.index(self)
            chosenTarget = self
            while (chosenTarget == self) or (choice == saved) or (not chosenTarget.alive):
                choice = randint(0,len(list)-1)
                chosenTarget = list[choice]
            return choice
        else:
            print("The witch didn't use her poison")
            return None
villagerRoles = {
    "Villager":Villager,
    "Villager-Villager":Player,
    "Fortune Teller":FortuneTeller,
    "Cupid":Cupid,
    "Witch":Witch,
    "Hunter":Hunter,
    "Little Girl":Player,
    "Guard":Player,
    "Ancient":Player,
    "Scapegoat":Player,
    "Idiot":Player,
    "Two Sisters":Player,
    "Three Brothers":Player, 
    "Fox":Player, 
    "Bear Tamer":Player,
    "Stuttering Judge":Player, 
    "Rusted Sword Knight":Player, 
    "Shaman":Player, 
    "Puppeteer":Player, 
    "Ankou":Player,
    "Night Owl":Player
    }


werewolfRoles = {
    "Werewolf":Werewolf,
    "Big Bad Wolf":Player,
    "Vile Father of Wolves":Player
    }
ambiguousRoles = {
    "Thief":Player,
    "Devoted Maid":Player,
    "Actor":Player,
    "Wild Child":Player,
    "Wolf-Dog":Player,
    "Abominable Sectarian":Player
    }
lonerRoles = {
    "White Wolf":Player,
    "Angel":Player,
    "Pied Pipper":Player,
    "White Rabbit":Player
    }
specialRoles = {
    "Pyromaniac":Player,
    "Raven":Player,
    "Gypsy":Player
    }