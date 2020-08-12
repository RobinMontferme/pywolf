import math
from player import *
from random import shuffle
from enum import Enum
from time import sleep
import os

class Phase(Enum):
    """Defines an enum for the game differents phases
    """
    SETUP = 0
    NIGHT = 1
    DAY = 2


class Game:
    """Defines a Game
    Data:

    - __playerAmount(int) : total amount of player in the game
    - __villagerAmount(int) : total amount of villager player in the game
    - __werewolfAmount(int) : total amount of werewolf player in the game
    - __ambiguousAmount(int) : total amount of ambiguous player in the game
    - __lonerAmount(int) : total amount of loner player in the game
    - __specialAmount(int) : total amount of special player in the game
    - __turns(int) : counter for turn in the game
    - __maxFailedVotes(int) : max failed votes allowed
    - __playerList(list) : list of Player present in the game
    - __presenRole(list) : list of str representing roles in the game
    - __victimsList(list) : list of Player representing the victim for current turn
    - __phase(Phase) : current Phase of the turn
    - __running(bool) : running status of the game

    """
    def __init__(self,verbose=True):
        """Constructor.
        """
        self.__playerAmount = 0
        self.__villagerAmount = 0
        self.__werewolfAmount = 0
        self.__ambiguousAmount = 0
        self.__lonerAmount = 0
        self.__specialAmount = 0
        self.__turns = 0
        self.__maxFailedVotes = 20

        self.__playerList = []
        self.__presentRoles = []
        self.__victimsList = []

        self.__phase = Phase.SETUP

        self.__running = False
        self.__verbose = verbose

    def setup(self, roleList):
        """Set the games up
        """
        if self.__verbose:
            os.system('cls' if os.name =='nt' else 'clear')
            print("Game Informations")
        self.__playerList.clear()
        for role, amount in roleList:
            if role in villagerRoles:
                self.__villagerAmount += amount
                for i in range(0, amount):
                    self.addPlayer(villagerRoles[role]())
            elif role in werewolfRoles:
                self.__werewolfAmount += amount
                for i in range(0, amount):
                    self.addPlayer(werewolfRoles[role]())
            elif role in ambiguousRoles:
                self.__ambiguousAmount += amount
                for i in range(0, amount):
                    self.addPlayer(ambiguousRoles[role]())
            elif role in lonerRoles:
                self.__lonerAmount += amount
                for i in range(0, amount):
                    self.addPlayer(lonerRoles[role]())
            elif role in specialRoles:
                self.__specialAmount += amount
                for i in range(0, amount):
                    self.addPlayer(specialRoles[role]())
            else:
                raise ValueError("Unknown role", role)
            if self.__verbose:
                print(str(amount) + " * " + role)
        shuffle(self.__playerList)
        i = 0
        for player in self.__playerList:
            player.name = str(i) + "p"
            i += 1

    def play(self):
        """Main Game Loop
        """
        self.__running = True
        while self.__running:
            if self.__verbose:
                print("#=================================================================================#")
            if self.__phase == Phase.SETUP:
                if self.__verbose:
                    print("Setup - Turn " + str(self.__turns))
                self.playerUsePower("Villager-Villager")
                if self.__verbose:
                    print("-----------------------------------")
                self.__phase = Phase.NIGHT
            elif self.__phase == Phase.NIGHT:
                if self.__turns == 0:
                    if self.__verbose: 
                        print("First Night - Turn " + str(self.__turns))
                else:
                    if self.__verbose:
                        print("Night - Turn " + str(self.__turns))
                if self.__verbose:
                    print("-----------------------------------")
                self.night()
                self.__phase = Phase.DAY
            elif self.__phase == Phase.DAY:
                if self.__verbose:
                    print("Day - Turn " + str(self.__turns))
                    print("-----------------------------------")
                self.day()
                self.__turns += 1
                self.__phase = Phase.NIGHT
            self.killVictims()

            self.updatePlayers()

            self.__victimsList.clear()
            if self.__victimsList:
                raise ValueError("List should be clear", self.__victimsList)
            
            self.checkGameEndConditions()
            if self.__verbose:
                print("#===================================Game===Status=================================#")
                self.displayGameStatus()
                print("#=================================================================================#")
                input("Press any key to continue...")
                os.system('cls' if os.name =='nt' else 'clear')
        if self.__verbose:                
            self.gameEnd()

    def day(self):
        """Process day actions. Mainly call for villagers to vote for a victim to eliminate.
        """
        victim = self.dayVote()
        self.__victimsList.append(victim)

    def night(self):
        """Process night actions. Calls roles in the order stated in the original game rulebook.
        """
        firstNight = self.__turns == 0
        if firstNight:
            self.playerUsePower("Cupid")

        self.playerUsePower("Fortune Teller")

        if firstNight:
            self.wolfSetup()
        victim = self.nightVote()
        self.__victimsList.append(victim)

        self.playerUsePower("Witch")

    def wolfSetup(self):
        """Called during the first night. Allows Werewolves to know each others.
        """
        for p in self.__playerList:
            if p.camp == Camp.WEREWOLVES:
                p.registerAllies(self.__playerList)

    def dayVote(self):
        """Handles the vote during day.
        """
        if self.__verbose:
            print("The village is deciding who it will eliminate")
        voteDone = False
        failedVotes = 0
        while not voteDone:
            equality = False
            result = None
            highestVote = 0
            if failedVotes != 0:
                for player in self.__playerList:
                    player.votes = 0
            if failedVotes == self.__maxFailedVotes:
                raise ValueError("Vote Failed")
            for player in self.__playerList:
                if player.alive:
                    votedPlayer = player.vote(self.getPlayerList())
                    if not votedPlayer:
                        continue
                    if player.isCaptain:
                        votedPlayer.votes += 2
                    else:
                        votedPlayer.votes += 1
            for player in self.__playerList:
                if player.votes > highestVote:
                    equality = False
                    highestVote = player.votes
                    result = player
            for player in self.__playerList:
                if player.votes == result.votes and player != result:
                    equality = True

            if equality:
                # print("An equality occured! Vote restarts!!")
                # print("\tPlayer " + result.name + " was the chosen player")
                failedVotes += 1
            elif not result.alive:
                if self.__verbose:
                    print("Victim chosen among the deads! Vote Restarts!!")
                    print("\tThe chosen victim: " + result.name + " is already dead!")
                failedVotes += 1
            else:
                voteDone = True
        if self.__verbose:
            print("Chosen villager: " + result.name + " with " + str(result.votes) + " votes")
        return result

    def nightVote(self):
        """Handles the werewolves votes during night
        """
        if self.__verbose:
            print("The Werewolves are choosing their victim!")
        voteDone = False
        failedVotes = 0
        while not voteDone:
            equality = False
            result = None
            highestVote = 0
            if failedVotes != 0:
                for player in self.__playerList:
                    player.votes = 0
            if failedVotes == self.__maxFailedVotes:
                if self.__verbose:
                    print("The werewolf finally decided")
            for player in self.__playerList:
                if player.camp == Camp.WEREWOLVES and player.alive:
                    votedPlayer = player.vote(self.getPlayerList(),True)
                    if not votedPlayer:
                        continue
                    votedPlayer.votes += 1
            for player in self.__playerList:
                if player.camp == Camp.VILLAGERS:
                    if player.votes > highestVote:
                        equality = False
                        highestVote = player.votes
                        result = player
            
            for player in self.__playerList:
                if player.votes == result.votes and player != result and failedVotes!=self.__maxFailedVotes:
                    equality = True
            if equality:
                # print("An equality occured. Vote restarts!")
                # print("\tPlayer " + result.name + " was the chosen player")
                failedVotes += 1
            if not result:
                if self.__verbose:
                    print("No Victim was chosen. Vote Restarts!!")
                failedVotes+=1
            elif not result.alive:
                if self.__verbose:
                    print("Victim chosen among the deads! Vote Restarts!!")
                    print("\tThe chosen victim: " + result.name + " is already dead!")
                failedVotes += 1
            else:
                voteDone = True
        if self.__verbose:
            print("Wolfs victim: " + result.name)
        return result

    def killVictims(self,addVictims = []):
        """ This function sets all victims present in "self.__victimsList" to be dead. 
        
            It also process certain players role power or status that can create additionnal victims.
            Thus this function can be recursively called.

            Parameters:

            - addVictims (list) : (default value : []) list of Player that were added after the first call during this turn produced additionnal victims. 
        """
        victimList  = self.__victimsList[:]
        potentialVictims  = self.__playerList[:]
        for p in potentialVictims:
            if p in victimList:
                potentialVictims.remove(p)

        for v in addVictims:
            victimList.append(v)

        if not victimList:
            if self.__verbose:
                print("Nobody died !!!!")

        additionalVictims = []
        for victim in victimList:
            victim.alive = False
            if self.__verbose:
                print("Player " + victim.name + " is now dead and was a " + victim.role)
            if victim.lover:
                if victim.lover.alive:
                    if self.__verbose:
                        print(victim.name + " lover: " + victim.lover.name + ", followed his love in death")
                    additionalVictims.append(victim.lover)
            if victim.role == "Hunter":
                hunterVictim = victim.vote(potentialVictims)
                if self.__verbose:
                    print("On his dying breath, the Hunter killed " + hunterVictim.name)
                additionalVictims.append(hunterVictim)
        self.__victimsList.clear()
        addVictims.clear()
        if additionalVictims:
            self.killVictims(additionalVictims)
    def gameEnd(self):
        """Called when game ends. Displays which camp won;
        """
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Game ended")
        print("Villager alive " + str(self.__villagerAmount))
        print("Werewolves alive " + str(self.__werewolfAmount))

        if (self.__villagerAmount == 0) or (self.__villagerAmount == 1 and self.__werewolfAmount==1):
            print("The wolves have won!!")
        elif self.__werewolfAmount == 0:
            print("The villagers have won!!")

    def updatePlayers(self):
        """Updates the currents stats about player in game and Players themselves;
        """
        villagers = 0
        wolves = 0
        ambiguous = 0
        loner = 0
        special = 0
        for p in self.__playerList:
            if p.alive:
                if p.role in villagerRoles:
                    villagers += 1
                elif p.role in werewolfRoles:
                    wolves += 1
                elif p.role in ambiguousRoles:
                    ambiguous += 1
                elif p.role in lonerRoles:
                    loner += 1
                elif p.role in specialRoles:
                    special += 1
        self.__villagerAmount = villagers
        self.__werewolfAmount = wolves
        self.__ambiguousAmount = ambiguous
        self.__lonerAmount = loner
        self.__specialAmount = special
        for p in self.__playerList:
            p.forgetDeadPlayers()

    def playerUsePower(self, role):
        """Search if a player of specific role is present and alive.
        If so, that player power is called through it's "usePower" method.

        Parameters:

        role(str) : string of the Role to be searched
        """
        player = None
        if role in self.__presentRoles:
            for p in self.__playerList:
                if p.role == role and p.alive:
                    player = p
        if player:
            player.usePower(self)
    def revealRole(self,player):
        """Update player memory with specified player role.

        Parameters:

        - player(Player): player that gets it's role revealed to the other
        """
        for p in self.__playerList:
            if p != player:
                p.memories.append(Memory(player,player.role))
    def getPlayerList(self):
        return self.__playerList[:]
    def addPlayer(self,player):
        self.__playerList.append(player)
        if player.role not in self.__presentRoles:
            self.__presentRoles.append(player.role)
    def getVictimsList(self):
        return self.__victimsList
    def getVillagersAmount(self):
        return self.__villagerAmount
    def getWereWolvesAmount(self):
        return self.__werewolfAmount
    def getLonersAmount(self):
        return self.__lonerAmount
    def displayGameStatus(self):
        """Displays current  game informations:

            - Amount of players from each camp

            - Each player status, role, name and memory
        """
        print("-----------------------------------")
        print("Remaining players: ", end="")
        print("\tvillagers:" + str(self.__villagerAmount), end="")
        print("\twolves:" + str(self.__werewolfAmount), end="")
        print("\tloners:" + str(self.__lonerAmount), end="")
        print("\tambiguous:" + str(self.__ambiguousAmount), end="")
        print("\tspecials:" + str(self.__specialAmount))
        print("-----------------------------------")
        for p in self.__playerList:
            p.display()
            p.votes = 0
        
    def checkGameEndConditions(self):
        """Checks whether or not the game can be ended or not.
        """
        if self.__villagerAmount == 0 or self.__werewolfAmount == 0 or (self.__villagerAmount == 1 and self.__werewolfAmount==1):
                self.__running = False
