'''
This file contains the main client for the game to run. By executing this code
you can play multiplayer on the same keyboard, against computer players as well
as multiplayer across computers.

References:
I created this file by modifying and merging framework code written by:
    - Rohan Varma, adapted by Kyle Chin for 15-112 Sockets Optional Lecture
    - Lukas Peraza for 15-112 F15 Pygame Optional Lecture, 11/11/15
'''

import pygame
import pygamegame #the framework
from helperFunctions import *
import socket
import threading
from queue import Queue

HOST = "192.168.0.178" # put server IP address here if playing on multiple computers
PORT = 50003

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.connect((HOST,PORT))
print("connected to server")

def handleServerMsg(server, serverMsg):
  server.setblocking(1)
  msg = ""
  command = ""
  while True:
    msg += server.recv(10).decode("UTF-8")
    command = msg.split("\n")
    while (len(command) > 1):
      readyMsg = command[0]
      msg = "\n".join(command[1:])
      serverMsg.put(readyMsg)
      command = msg.split("\n")

'''
CURRENT UPDATE ON AIs:

what the chasing AI does every second:
    1. finds the closest player
    2. finds a route to it using A*
    3. moves according to the route using absolute x and y coordinates
    
    
what the running AI does every second:
    1. finds the chaser
    2. sets target position to a space that is exactly the a certain num of steps away
    3. tries to find a route to that position that ensures it doesn't go more than
       a certain number of steps within range of the chaser
    4. if it cannot find a route then it will just find any shortest route to that position
'''


#GAME NAME IS KETCHUP. BECAUSE CATCH UP. GET IT?? :D

class GameCharacter(pygame.sprite.Sprite):
    
    def __init__(self, x, y, image, speed):
        super().__init__()
        
        # x,y is the center point of the character image
        self.x, self.y = x, y
        self.image = image
        self.width, self.height = image.get_size()
        self.speed = speed                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               
        self.item = None
        self.lastDir = None
        self.invincible = False
        
        self.updatePos()
        self.updateRect()
        
    # for collision detection
    def updateRect(self):
        w, h = self.width, self.height
        self.rect = pygame.Rect(self.x - w / 2, self.y - h / 2, w, h)
    
    def updatePos(self):
        self.pos = getPosition(self.x, self.y, ketchUp.wallSize)
        
    def update(self, keysDown):
        self.updateRect()
        self.updatePos()
        
    def useItem(self):
        if self.item == 'gun':
            bullet = Bullet(self.x, self.y, ketchUp.bulletImage, self.lastDir, 
                            ketchUp.bulletSpeed, self)
            ketchUp.bulletGroup.add(bullet)
            self.item = None
        elif self.item == 'laser':
            laserBeam = LaserBeam(self.x, self.y, ketchUp.laserBeamImage, self.lastDir,
                          ketchUp.laserBeamSpeed, self)
            ketchUp.laserBeamGroup.add(laserBeam)
            self.item = None

class Computer(GameCharacter):
    def __init__(self, x, y, image, speed, numRunSteps):
        super().__init__(x, y, image, speed)
        self.numRunSteps = numRunSteps
        self.mode = ''
        self.route = []
        
    def newRoute(self):
        if self.mode == 'chase':
            distance = []
            for player in ketchUp.characters:
                if player != self:
                    distance.append(getDistance(self.pos, player.pos))
            minDist = min(distance)
            for player in ketchUp.characters:
                if getDistance(self.pos, player.pos) == minDist:
                    self.targetPos = player.pos

            if ketchUp.computerDifficulty == 'easy':
                routeDir = findRoute(ketchUp.wallMap, self.pos, self.targetPos)
            elif ketchUp.computerDifficulty == 'hard':
                routeDir = aStarFindRoute(ketchUp.wallMap, self.pos, self.targetPos)

            x, y = getCoordFromPos(self.pos, ketchUp.wallSize)
            self.route = convertRoute(routeDir, x, y, ketchUp.wallSize)
            
        elif self.mode == 'run':
            if ketchUp.chaser == 'ketchup':
                chaserPos = ketchUp.player1.pos
            elif ketchUp.chaser == 'mustard':
                chaserPos = ketchUp.player2.pos
            elif ketchUp.chaser == 'mayo':
                chaserPos = ketchUp.player3.pos
            elif ketchUp.chaser == 'bbq':
                chaserPos = ketchUp.player4.pos
            
            self.targetPos = findPosNumStepsAway(ketchUp.wallMap, chaserPos, self.numRunSteps)
            
            if ketchUp.computerDifficulty == 'easy':
                routeDir = findRoute(ketchUp.wallMap, self.pos, self.targetPos)
            elif ketchUp.computerDifficulty == 'hard':
                routeDir = forRunAStarFindRoute(ketchUp.wallMap, self.pos, self.targetPos,
                                                chaserPos, int(0.3*ketchUp.numRows))
                                                
            if routeDir != None:
                x, y = getCoordFromPos(self.pos, ketchUp.wallSize)
                self.route = convertRoute(routeDir, x, y, ketchUp.wallSize)
            else:
                if ketchUp.computerDifficulty == 'easy':
                    routeDir = findRoute(ketchUp.wallMap, self.pos, self.targetPos)
                elif ketchUp.computerDifficulty == 'hard':
                    routeDir = aStarFindRoute(ketchUp.wallMap, self.pos, self.targetPos)
                x, y = getCoordFromPos(self.pos, ketchUp.wallSize)
                self.route = convertRoute(routeDir, x, y, ketchUp.wallSize)
    
    def move(self):
        nextX, nextY = self.route[0]
        diffX = nextX - self.x
        diffY = nextY - self.y
        
        if diffX > 0: # right
            if abs(diffX) >= self.speed:
                self.x += self.speed
            else:
                self.x += abs(diffX)
        elif diffX < 0: # left
            if abs(diffX) >= self.speed:
                self.x -= self.speed
            else:
                self.x -= abs(diffX)
        if diffY > 0: # downwards
            if abs(diffY) >= self.speed:
                self.y += self.speed
            else:
                self.y += abs(diffY)
        elif diffY < 0: # upwards
            if abs(diffY) >= self.speed:
                self.y -= self.speed
            else:
                self.y -= abs(diffY)

class GameObject(pygame.sprite.Sprite):
    def __init__(self, row, col, image, width, height):
        super().__init__()
        
        # row and col start at 0, x and y are the centre of the image
        self.width, self.height = width, height
        self.x = ((ketchUp.width/ketchUp.numCols)*col) + (self.width/2)
        self.y = ((ketchUp.height/ketchUp.numRows)*row) + (self.height/2)
        self.row, self.col = row, col
        self.image = image
        self.rect = pygame.Rect(self.x - self.width/2, self.y-self.height/2,
                                self.width, self.height)

class Boot(GameObject):
    pass
    
class Snail(GameObject):
    pass
    
class Gun(GameObject):
    pass
    
class Laser(GameObject):
    pass
    
class Shield(GameObject):
    pass

class Ammo(pygame.sprite.Sprite):
    def __init__(self, x, y, image, direction, speed, shooter):
        super().__init__()
        
        # x,y is the center point of the character image
        self.x, self.y = x, y
        self.dir = direction
        self.imageOriginal = image
        if self.dir == 'up':
            self.image = pygame.transform.rotate(self.imageOriginal, 90)
        elif self.dir == 'down':
            self.image = pygame.transform.rotate(self.imageOriginal, -90)
        elif self.dir == 'left':
            self.image = pygame.transform.rotate(self.imageOriginal, 180)
        elif self.dir == 'right':
            self.image = self.imageOriginal
        self.width, self.height = self.image.get_size()
        self.speed = speed
        self.shooter = shooter
    
        self.updateRect()
        
    # for collision detection
    def updateRect(self):
        w, h = self.width, self.height
        self.rect = pygame.Rect(self.x - w / 2, self.y - h / 2, w, h)
        
    def update(self, keysDown):
        if self.dir == 'up':
            self.y -= self.speed
        elif self.dir == 'down':
            self.y += self.speed
        elif self.dir == 'left':
            self.x -= self.speed
        elif self.dir == 'right':
            self.x += self.speed
        
        self.updateRect()
        
class Bullet(Ammo):
    pass

class LaserBeam(Ammo):
    pass
        
class myProject(pygamegame.PygameGame):
    
    def init(self):
        self.height = self.screenHeight
        self.width = self.height
        self.mode = 'start'
        self.lastMode = ''
        self.chaser = None
        
        pygame.mixer.music.load('bgMusic.mp3')
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
        
        self.boardSizes = ['small', 'medium', 'large']
        self.boardSize = self.boardSizes[1]
        
        self.winScore = 3
        self.viewTimer = True
        self.computerDifficulty = 'hard'
        self.settingsRow = 0
        
        self.standardFont = pygame.font.SysFont(None,23)
        self.boldFont = pygame.font.SysFont(None,25,True)
        self.underlineFont = pygame.font.SysFont(None,23)
        self.italicFont = pygame.font.SysFont(None,23, False, True)
        self.underlineFont.set_underline(True)
        self.largeFont = pygame.font.SysFont(None,50)    
        
        self.player1ImageMed = pygame.transform.scale(pygame.image.load(
                            'images/ketchup.png').convert_alpha(), (42,57))
        self.player1ImageLarge = pygame.transform.scale(pygame.image.load(
                            'images/ketchup.png').convert_alpha(), (70,95))
        self.player2ImageMed = pygame.transform.scale(pygame.image.load(
                            'images/mustard.png').convert_alpha(), (42,57))
        self.player2ImageLarge = pygame.transform.scale(pygame.image.load(
                            'images/mustard.png').convert_alpha(), (70,95))
        self.player3ImageMed = pygame.transform.scale(pygame.image.load(
                            'images/mayo.png').convert_alpha(), (42,57))
        self.player3ImageLarge = pygame.transform.scale(pygame.image.load(
                            'images/mayo.png').convert_alpha(), (70,95))
        self.player4ImageMed = pygame.transform.scale(pygame.image.load(
                            'images/bbq.png').convert_alpha(), (42,57))
        self.player4ImageLarge = pygame.transform.scale(pygame.image.load(
                            'images/bbq.png').convert_alpha(), (70,95))
        self.startImage = pygame.transform.scale(pygame.image.load(
                            'images/ketchup.png').convert_alpha(),
                             (self.screenWidth//3, self.screenHeight))
        
        self.initNewGame()
    
    def initNewGame(self):
        
        # NOTE: actual board rows and cols is self.numRows-2 and self.numCols-2
        if self.boardSize == self.boardSizes[0]:
            self.numRows = 12
            self.numCols = 12
        elif self.boardSize == self.boardSizes[1]:
            self.numRows = 20
            self.numCols = 20
        elif self.boardSize == self.boardSizes[2]:
            self.numRows = 25
            self.numCols = 25
            
        self.wallSize = int(self.width/self.numCols)
        self.wallGroup = pygame.sprite.Group()
        self.wallMap = generateBoard(self.numRows-2, self.numCols-2)
        
        self.numSpace = countSpace(self.wallMap)
        self.numPowerUps = int(0.02*self.numSpace)
        self.maxNumPowerUps = 5*self.numPowerUps
        self.powerUpsGroup = pygame.sprite.Group()
        
        # bullet and laserBeam points right
        self.bulletImage = pygame.transform.scale(pygame.image.load(
                           'images/bullet.png').convert_alpha(), 
                           (self.wallSize//2,self.wallSize//2))
        self.laserBeamImage = pygame.transform.scale(pygame.image.load(
                              'images/laserBeam.png').convert_alpha(), 
                              (self.wallSize*2,self.wallSize//2))
        self.bootImage = pygame.transform.scale(pygame.image.load(
                            'images/boot.png').convert_alpha(), (self.wallSize,self.wallSize))
        self.snailImage = pygame.transform.scale(pygame.image.load(
                            'images/snail.png').convert_alpha(), (self.wallSize,self.wallSize))
        self.gunImage = pygame.transform.scale(pygame.image.load(
                            'images/gun.png').convert_alpha(), (self.wallSize,self.wallSize))
        self.laserImage = pygame.transform.scale(pygame.image.load(
                            'images/laser.png').convert_alpha(), (self.wallSize,self.wallSize))
        self.shieldImage = pygame.transform.scale(pygame.image.load(
                            'images/shield.png').convert_alpha(), (self.wallSize,self.wallSize))
                            
        self.powerUpsChase = [(Boot,self.bootImage), (Snail,self.snailImage), 
                              (Shield,self.shieldImage)]
        self.powerUpsShoot = [(Gun,self.gunImage), (Laser,self.laserImage)]
        
        self.generateWalls()
        
        self.speed = 0.2*self.wallSize
        self.maxSpeed = 0.5*self.wallSize
        self.minSpeed = 0.05*self.wallSize
        
        # initialises images, scaling them to the pixels you want,
        # and calculates their position based on the size
        self.playerWidth = int(0.6*self.wallSize)
        self.playerHeight = int(0.8*self.wallSize)
        self.player1Image = pygame.transform.scale(pygame.image.load(
                            'images/ketchup.png').convert_alpha(),
                            (self.playerWidth,self.playerHeight))
        self.player1W, self.player1H = self.playerWidth, self.playerHeight
        
        self.player2Image = pygame.transform.scale(pygame.image.load(
                            'images/mustard.png').convert_alpha(),
                            (self.playerWidth,self.playerHeight))
        self.player2W, self.player2H = self.playerWidth, self.playerHeight
        self.player1Score = 0
        self.player2Score = 0
        

        # players 3 and 4
        self.player3Image = pygame.transform.scale(pygame.image.load(
                            'images/mayo.png').convert_alpha(),
                            (self.playerWidth,self.playerHeight))
        self.player3W, self.player3H = self.playerWidth, self.playerHeight
        self.player3Score = 0
        
        self.player4Image = pygame.transform.scale(pygame.image.load(
                            'images/bbq.png').convert_alpha(),
                            (self.playerWidth,self.playerHeight))
        self.player4W, self.player4H = self.playerWidth, self.playerHeight
        self.player4Score = 0
        
        self.bulletGroup = pygame.sprite.Group()
        self.bulletSpeed = 0.5*self.wallSize
        self.laserBeamGroup = pygame.sprite.Group()
        self.laserBeamSpeed = 0.7*self.wallSize
        
        self.bubbleImage = pygame.transform.scale(pygame.image.load(
                            'images/bubble.png').convert_alpha(), 
                            (self.wallSize, self.wallSize))
        self.bubbleH, self.bubbleW = self.bubbleImage.get_size()

        self.initEachRound()
    
    # only call this init to reset each round and not the whole game
    def initEachRound(self):
        self.time = 0
        self.count = 10
        
        if self.chaser == None:
            self.chaser = 'bbq'
        elif self.chaser == 'ketchup':
            self.chaser = 'mustard'
        elif self.chaser == 'mustard':
            self.chaser = 'mayo'
        elif self.chaser == 'mayo':
            self.chaser = 'bbq'
        elif self.chaser == 'bbq':
            self.chaser = 'ketchup'
        
        # player1 starts in top left corner
        self.player1X = self.player1W/2 + self.wallWidth + 1
        self.player1Y = self.player1H/2 + self.wallHeight + 1
        
        # player2 starts in the bottom right corner
        self.player2X = self.width - self.player2W/2 - self.wallWidth - 1
        self.player2Y = self.height - self.player2H/2 - self.wallHeight - 1
        
        # player 3 starts in the bottom left corner
        self.player3X = self.player3W/2 + self.wallWidth + 1
        self.player3Y = self.height - self.player3H/2 - self.wallHeight - 1
        
        # player 4 starts in the top right corner
        self.player4X = self.width - self.player4W/2 - self.wallWidth - 1
        self.player4Y = self.player4H/2 + self.wallHeight + 1
        
        # initialises the characters
        self.characters = pygame.sprite.Group()
        self.player1 = GameCharacter(self.player1X, self.player1Y, self.player1Image, self.speed)
        self.characters.add(self.player1)
        self.player2 = GameCharacter(self.player2X, self.player2Y, self.player2Image, self.speed)
        self.characters.add(self.player2)
        
        
        if self.mode == 'shoot':
            self.player3 = GameCharacter(self.player3X, self.player3Y, self.player3Image, self.speed)
            self.player4 = GameCharacter(self.player4X, self.player4Y, self.player4Image, self.speed)
        else:
            # players 3 and 4 are computers
            self.player3 = Computer(self.player3X, self.player3Y, self.player3Image, 
                                self.speed, int(1.5*self.numRows))
            self.player4 = Computer(self.player4X, self.player4Y, self.player4Image, 
                                self.speed, int(1.9*self.numRows))
        
        self.characters.add(self.player3)
        self.characters.add(self.player4)
        
        if self.mode != 'shoot':
            if self.chaser == 'mayo':
                self.player3.mode = 'chase'
                self.player4.mode = 'run'
            elif self.chaser == 'bbq':
                self.player3.mode = 'run'
                self.player4.mode = 'chase'
            else:
                self.player3.mode = 'run'
                self.player4.mode = 'run'
            
            self.player3.newRoute()
            self.player4.newRoute()
        
        self.powerUpsGroup.empty()
        if self.mode == 'chase':
            self.generatePowerUps(self.powerUpsChase)
        elif self.mode == 'shoot':
            self.generatePowerUps(self.powerUpsShoot)
        
    def generatePowerUps(self, powerUpsList):
        
        if len(self.powerUpsGroup) < self.maxNumPowerUps:
            def isLegalPosition(self, row, col):
                if row == None or col == None:
                    return False
                elif row == 1 and col == 1:
                    return False
                elif row == self.numRows-2 and col == self.numCols-2:
                    return False
                elif row == self.numRows-2 and col == 1:
                    return False
                elif row == 1 and col == self.numCols-2:
                    return False
                elif self.wallMap[row-1][col-1] != 0:
                    return False
                for powerUp in self.powerUpsGroup:
                    if row ==  powerUp.row and col == powerUp.col:
                        return False
                return True
            
            for i in range (self.numPowerUps):
                index = random.randint(0,len(powerUpsList)-1)
                powerUpType = powerUpsList[index][0]
                powerUpImage = powerUpsList[index][1]
                powerUpRow = None
                powerUpCol = None
                while isLegalPosition(self, powerUpRow, powerUpCol) == False:
                    powerUpRow = random.randint(1,self.numRows-2)
                    powerUpCol = random.randint(1,self.numCols-2)
                powerUpWidth, powerUpHeight = self.wallSize, self.wallSize
                powerUp = powerUpType(powerUpRow, powerUpCol, powerUpImage,
                                      powerUpWidth, powerUpHeight)
                self.powerUpsGroup.add(powerUp)
        
    def generateWalls(self):
        self.wallGroup.empty()
        self.wallImage = pygame.transform.scale(pygame.image.load(
                            'images/burger.png').convert_alpha(), (self.wallSize,self.wallSize))
        self.wallWidth, self.wallHeight = self.wallSize, self.wallSize
        
        # generate border
        for i in range (0,self.numRows):
            borderBlock1 = GameObject(0, i, self.wallImage, self.wallWidth, self.wallHeight)
            borderBlock2 = GameObject(self.numRows-1, i, self.wallImage, 
                                      self.wallWidth, self.wallHeight)
            self.wallGroup.add(borderBlock1)
            self.wallGroup.add(borderBlock2)
        for j in range (1,self.numRows-1):
            borderBlock3 = GameObject(j, 0, self.wallImage, self.wallWidth, self.wallHeight)
            borderBlock4 = GameObject(j, self.numRows-1, self.wallImage, 
                                      self.wallWidth, self.wallHeight)
            self.wallGroup.add(borderBlock3)
            self.wallGroup.add(borderBlock4)
        
        for row in range (len(self.wallMap)):
            for col in range (len(self.wallMap[0])):
                if self.wallMap[row][col] != 0:
                    block = GameObject(row+1, col+1, self.wallImage, 
                                       self.wallWidth, self.wallHeight)
                    self.wallGroup.add(block)
        
    def keyPressed(self, keyCode, modifier):
        msgList = []
        
        if keyCode == 114:
            self.init()
        
        if self.mode == 'start':
            if keyCode == 99:
                self.mode = 'chase'
                self.lastMode = 'chase'
                self.initNewGame()
            
            elif keyCode == 118:
                self.mode = 'shoot'
                self.lastMode = 'shoot'
                self.initNewGame()
                map = removeSpacesForBoard(str(self.wallMap))
                rows = self.numRows
                cols = self.numCols
                winScore = self.winScore
                powerUpsStr = convertPowerUpSpritesToStr(self.powerUpsGroup)
                msg = ('newGame shoot %s %d %d %d\n' 
                        %(map, rows, cols, winScore))
                msg2 = ('powerUp %s False %d %d %d %d\n' %(powerUpsStr,
                     self.player1Score, self.player2Score, self.player3Score, self.player4Score))
                msgList.append(msg)
                msgList.append(msg2)
            
            elif keyCode == 115:
                self.mode = 'settings'
            
            elif keyCode == 104:
                self.mode = 'helpP1'
                
        elif self.mode == 'helpP1':
            if keyCode == 32:
                self.mode = 'helpP2'
        
        elif self.mode == 'helpP2':
            if keyCode == 8:
                self.mode = 'start'
        
        elif self.mode == 'shoot':
            if keyCode == 32:
                self.player1.useItem()
                msgList.append('fire nothing\n')
        
        elif self.mode == 'settings':
            if keyCode == 273:
                self.settingsRow -= 1
            if keyCode == 274:
                self.settingsRow += 1
            if self.settingsRow < 0:
                self.settingsRow = 3
            elif self.settingsRow > 3:
                self.settingsRow = 0
            
            if keyCode == 8:
                self.mode = 'start'
            
            # controls to select board size
            if self.settingsRow == 0:
                if keyCode == 276:
                    if self.boardSize == self.boardSizes[0]:
                        self.boardSize = self.boardSizes[2]
                    elif self.boardSize == self.boardSizes[1]:
                        self.boardSize = self.boardSizes[0]
                    elif self.boardSize == self.boardSizes[2]:
                        self.boardSize = self.boardSizes[1]
                if keyCode == 275:
                    if self.boardSize == self.boardSizes[0]:
                        self.boardSize = self.boardSizes[1]
                    elif self.boardSize == self.boardSizes[1]:
                        self.boardSize = self.boardSizes[2]
                    elif self.boardSize == self.boardSizes[2]:
                        self.boardSize = self.boardSizes[0]
            
            # controls to select number of points to win
            elif self.settingsRow == 1:
                if keyCode == 276:
                    if self.winScore == 3:
                        self.winScore = 7
                    elif self.winScore == 5:
                        self.winScore = 3
                    elif self.winScore == 7:
                        self.winScore = 5
                elif keyCode == 275:
                    if self.winScore == 3:
                        self.winScore = 5
                    elif self.winScore == 5:
                        self.winScore = 7
                    elif self.winScore == 7:
                        self.winScore = 3
            
            # controls to select whether to view the timer or not
            elif self.settingsRow == 2:
                if keyCode == 276 or keyCode == 275:
                    if self.viewTimer == True:
                        self.viewTimer = False
                    elif self.viewTimer == False:
                        self.viewTimer = True
            
            # controls to select difficulty of computer
            elif self.settingsRow == 3:
                if keyCode == 276 or keyCode == 275:
                    if self.computerDifficulty == 'easy':
                        self.computerDifficulty = 'hard'
                    elif self.computerDifficulty == 'hard':
                        self.computerDifficulty = 'easy'
            
        # sockets - handles sending messages
        if (msgList != []):
            for message in msgList:
                print ("sending: ", message,)
                self.server.send(message.encode())
    
    def timerFired(self, dt):
        msgList = []
        
        # sockets - handles received messages
        while (serverMsg.qsize() > 0):
            msg = serverMsg.get(False)
            
            try:
                print("received: ", msg, "\n")
                msg = msg.split()
                command = msg[0]
                player = msg[1]
                
                if command == 'move':
                    x = int(msg[2])
                    y = int(msg[3])
                    dir = msg[4]
                    
                    if player == 'Player1':
                        self.player1.x = x
                        self.player1.y = y
                        self.player1.lastDir = dir
                        self.player1.update(self.isKeyPressed)
                    
                    elif player == 'Player2':
                        self.player2.x = x
                        self.player2.y = y
                        self.player2.lastDir = dir
                        self.player2.update(self.isKeyPressed)
                        
                    elif player == 'Player3':
                        self.player3.x = x
                        self.player3.y = y
                        self.player3.lastDir = dir
                        self.player3.update(self.isKeyPressed)
                    
                    elif player == 'Player4':
                        self.player4.x = x
                        self.player4.y = y
                        self.player4.lastDir = dir
                        self.player4.update(self.isKeyPressed)
                
                elif command == 'fire':
                    if player == 'Player1':
                        self.player1.useItem()
                    elif player == 'Player2':
                        self.player2.useItem()
                    elif player == 'Player3':
                        self.player3.useItem()
                    elif player == 'Player4':
                        self.player4.useItem()
                    
            except:
                print("failed")
            serverMsg.task_done()
        
        if self.mode == 'chase' or self.mode == 'shoot':
            
            self.time += 1 #counts number of times timerFired is called
            
            # rotates the chaser between players during each round
            if self.time%self.fps == 0:
                self.count -= 1 # counts the seconds
                if self.count < 1:
                    self.count = 10
                    if self.mode == 'chase':
                        self.generatePowerUps(self.powerUpsChase)
                    elif self.mode == 'shoot':
                        self.generatePowerUps(self.powerUpsShoot)
                        powerUpsStr = convertPowerUpSpritesToStr(self.powerUpsGroup)
                        newMessage = ('powerUp %s False %d %d %d %d\n' %(powerUpsStr,
                     self.player1Score, self.player2Score, self.player3Score, self.player4Score))
                        msgList.append(newMessage)
                        
                    if self.mode != 'shoot':
                        if self.chaser == 'ketchup':
                            self.chaser = 'mustard'
                            self.player3.mode = 'run'
                            self.player4.mode = 'run'
                            self.player3.newRoute()
                            self.player4.newRoute()
                            
                        elif self.chaser == 'mustard':
                            self.chaser = 'mayo'
                            self.player3.mode = 'chase'
                            self.player4.mode = 'run'
                            self.player3.newRoute()
                            self.player4.newRoute()
                            
                        elif self.chaser == 'mayo':
                            self.chaser = 'bbq'
                            self.player3.mode = 'run'
                            self.player4.mode = 'chase'
                            self.player3.newRoute()
                            self.player4.newRoute()
                            
                        elif self.chaser == 'bbq':
                            self.chaser = 'ketchup'
                            self.player3.mode = 'run'
                            self.player4.mode = 'run'
                            self.player3.newRoute()
                            self.player4.newRoute()
                   
            # handles invincibility
            if self.time%self.fps == 0:
                for player in self.characters:
                    if player.invincible == True:
                        player.invincibleCount -= 1
                        if player.invincibleCount == 0:
                            player.invincible = False
                    
            # controls for player 1
            if self.isKeyPressed(pygame.K_a):
                self.player1.lastDir = 'left'
                self.player1.x -= self.player1.speed
                self.player1.update(self.isKeyPressed)
                wall = pygame.sprite.spritecollideany(self.player1, self.wallGroup)
                if wall != None:
                    playerLeftEdge = self.player1.x - self.player1.width/2
                    wallRightEdge = wall.x + wall.width/2
                    overlap = wallRightEdge - playerLeftEdge
                    self.player1.x += overlap
                    self.player1.update(self.isKeyPressed)
                if self.mode == 'shoot':
                    msgList.append('move %d %d %s\n' % 
                        (self.player1.x, self.player1.y, self.player1.lastDir))
                    
            if self.isKeyPressed(pygame.K_d):
                self.player1.lastDir = 'right'
                self.player1.x += self.player1.speed
                self.player1.update(self.isKeyPressed)
                wall = pygame.sprite.spritecollideany(self.player1, self.wallGroup)
                if wall != None:
                    playerRightEdge = self.player1.x + self.player1.width/2
                    wallLeftEdge = wall.x - wall.width/2
                    overlap = playerRightEdge - wallLeftEdge
                    self.player1.x -= overlap
                    self.player1.update(self.isKeyPressed)
                if self.mode == 'shoot':
                    msgList.append('move %d %d %s\n' % 
                        (self.player1.x, self.player1.y, self.player1.lastDir))
                
            if self.isKeyPressed(pygame.K_w):
                self.player1.lastDir = 'up'
                self.player1.y -= self.player1.speed
                self.player1.update(self.isKeyPressed)
                wall = pygame.sprite.spritecollideany(self.player1, self.wallGroup)
                if wall != None:
                    playerTopEdge = self.player1.y - self.player1.height/2
                    wallBotEdge = wall.y + wall.height/2
                    overlap = wallBotEdge - playerTopEdge
                    self.player1.y += overlap
                    self.player1.update(self.isKeyPressed)
                if self.mode == 'shoot':
                    msgList.append('move %d %d %s\n' % 
                        (self.player1.x, self.player1.y, self.player1.lastDir))
                    
            if self.isKeyPressed(pygame.K_s):
                self.player1.lastDir = 'down'
                self.player1.y += self.player1.speed
                self.player1.update(self.isKeyPressed)
                wall = pygame.sprite.spritecollideany(self.player1, self.wallGroup)
                if wall != None:
                    playerBotEdge = self.player1.y + self.player1.height/2
                    wallTopEdge = wall.y - wall.height/2
                    overlap = playerBotEdge - wallTopEdge
                    self.player1.y -= overlap
                    self.player1.update(self.isKeyPressed)
                if self.mode == 'shoot':
                    msgList.append('move %d %d %s\n' % 
                        (self.player1.x, self.player1.y, self.player1.lastDir))
                
            if self.mode != 'shoot':
                # controls for player 2
                if self.isKeyPressed(pygame.K_LEFT):
                    self.player2.lastDir = 'left'
                    self.player2.x -= self.player2.speed
                    self.player2.update(self.isKeyPressed)
                    wall = pygame.sprite.spritecollideany(self.player2, self.wallGroup)
                    if wall != None:
                        playerLeftEdge = self.player2.x - self.player2.width/2
                        wallRightEdge = wall.x + wall.width/2
                        overlap = wallRightEdge - playerLeftEdge
                        self.player2.x += overlap
                        self.player2.update(self.isKeyPressed)
                    
                if self.isKeyPressed(pygame.K_RIGHT):
                    self.player2.lastDir = 'right'
                    self.player2.x += self.player2.speed
                    self.player2.update(self.isKeyPressed)
                    wall = pygame.sprite.spritecollideany(self.player2, self.wallGroup)
                    if wall != None:
                        playerRightEdge = self.player2.x + self.player2.width/2
                        wallLeftEdge = wall.x - wall.width/2
                        overlap = playerRightEdge - wallLeftEdge
                        self.player2.x -= overlap
                        self.player2.update(self.isKeyPressed)
                    
                if self.isKeyPressed(pygame.K_UP):
                    self.player2.lastDir = 'up'
                    self.player2.y -= self.player2.speed
                    self.player2.update(self.isKeyPressed)
                    wall = pygame.sprite.spritecollideany(self.player2, self.wallGroup)
                    if wall != None:
                        playerTopEdge = self.player2.y - self.player2.height/2
                        wallBotEdge = wall.y + wall.height/2
                        overlap = wallBotEdge - playerTopEdge
                        self.player2.y += overlap
                        self.player2.update(self.isKeyPressed)
                    
                if self.isKeyPressed(pygame.K_DOWN):
                    self.player2.lastDir = 'down'
                    self.player2.y += self.player2.speed
                    self.player2.update(self.isKeyPressed)
                    wall = pygame.sprite.spritecollideany(self.player2, self.wallGroup)
                    if wall != None:
                        playerBotEdge = self.player2.y + self.player2.height/2
                        wallTopEdge = wall.y - wall.height/2
                        overlap = playerBotEdge - wallTopEdge
                        self.player2.y -= overlap
                        self.player2.update(self.isKeyPressed)
                        
                if self.computerDifficulty == 'hard':    
                    if self.boardSize == self.boardSizes[0]:
                        if self.time%2 == 0:
                            self.player3.newRoute()
                            self.player4.newRoute()
                    elif self.boardSize == self.boardSizes[1]:
                        if self.time%(self.fps//2) == 0:  
                            self.player3.newRoute()
                            self.player4.newRoute()
                    elif self.boardSize == self.boardSizes[2]:
                        if self.time%self.fps == 0:  
                            self.player3.newRoute()
                            self.player4.newRoute()
                        
                #controls for computer player 3
                if self.player3.route != []:
                    tempX = self.player3.x
                    tempY = self.player3.y
                    self.player3.move()
                    self.player3.update(self.isKeyPressed)
                    if self.player3.x == tempX and self.player3.y == tempY:
                        self.player3.route.pop(0)
                        if self.player3.route == []:
                            self.player3.newRoute()
                            
                #controls for computer player 4
                if self.player4.route != []:
                    tempX = self.player4.x
                    tempY = self.player4.y
                    self.player4.move()
                    self.player4.update(self.isKeyPressed)
                    if self.player4.x == tempX and self.player4.y == tempY:
                        self.player4.route.pop(0)
                        if self.player4.route == []:
                            self.player4.newRoute()
            
            # handles collisions with powerUps regardless of gamemodes
            collidePlayerPowerUp = pygame.sprite.groupcollide(
                                self.characters, self.powerUpsGroup, False, True)
            for player in collidePlayerPowerUp:
                powerUps = collidePlayerPowerUp[player]
                for powerUp in powerUps:
                    if isinstance(powerUp, Boot):
                        player.speed += 0.25*self.speed
                        if player.speed > self.maxSpeed:
                            player.speed = self.maxSpeed
                    elif isinstance(powerUp, Snail):
                        player.speed -= 0.25*self.speed
                        if player.speed < self.minSpeed:
                            player.speed = self.minSpeed
                    elif isinstance(powerUp, Gun):
                        player.item = 'gun'
                    elif isinstance(powerUp, Laser):
                        player.item = 'laser'
                    elif isinstance(powerUp, Shield):
                        player.invincible = True
                        player.invincibleCount = 3
        
        if self.mode == 'shoot':
            # ensures that bullets die after they go off screen
            for bullet in self.bulletGroup:
                bullet.update(self.isKeyPressed)
                if (bullet.x > self.width or bullet.x < 0 
                    or bullet.y > self.height or bullet.y < 0):
                    bullet.kill()
            
            # ensures that laser beams die after they go off screen
            for laserBeam in self.laserBeamGroup:
                laserBeam.update(self.isKeyPressed)
                if (laserBeam.x > self.width or laserBeam.x < 0 
                    or laserBeam.y > self.height or laserBeam.y < 0):
                    laserBeam.kill()
            
            # bullets can't go through walls but lasers can
            pygame.sprite.groupcollide(self.bulletGroup, self.wallGroup, True, False)
            # laserBeams can destroy bullets
            pygame.sprite.groupcollide(self.bulletGroup, self.laserBeamGroup, True, False)
            
            # collision detection between ammo and players
            bullet = pygame.sprite.spritecollideany(self.player1, self.bulletGroup)
            if bullet != None:
                if bullet.shooter != self.player1:
                    self.player1.kill()
                    if bullet.shooter == self.player2:
                        self.player2Score += 1
                        if self.player2Score == self.winScore:
                            self.mode = 'p2Win'
                    elif bullet.shooter == self.player3:
                        self.player3Score += 1
                        if self.player3Score == self.winScore:
                            self.mode = 'p3Win'
                    elif bullet.shooter == self.player4:
                        self.player4Score += 1
                        if self.player4Score == self.winScore:
                            self.mode = 'p4Win'
                    bullet.kill()
                    self.initEachRound()
                    powerUpsStr = convertPowerUpSpritesToStr(self.powerUpsGroup)
                    message = ('powerUp %s True %d %d %d %d\n' %(powerUpsStr,
                     self.player1Score, self.player2Score, self.player3Score, self.player4Score))
                    msgList.append(message)
            
            bullet = pygame.sprite.spritecollideany(self.player2, self.bulletGroup)
            if bullet != None:
                if bullet.shooter != self.player2:
                    self.player2.kill()
                    if bullet.shooter == self.player1:
                        self.player1Score += 1
                        if self.player1Score == self.winScore:
                            self.mode = 'p1Win'
                    elif bullet.shooter == self.player3:
                        self.player3Score += 1
                        if self.player3Score == self.winScore:
                            self.mode = 'p3Win'
                    elif bullet.shooter == self.player4:
                        self.player4Score += 1
                        if self.player4Score == self.winScore:
                            self.mode = 'p4Win'
                    bullet.kill()
                    self.initEachRound()
                    powerUpsStr = convertPowerUpSpritesToStr(self.powerUpsGroup)
                    message = ('powerUp %s True %d %d %d %d\n' %(powerUpsStr,
                     self.player1Score, self.player2Score, self.player3Score, self.player4Score))
                    msgList.append(message)
            
            bullet = pygame.sprite.spritecollideany(self.player3, self.bulletGroup)
            if bullet != None:
                if bullet.shooter != self.player3:
                    self.player3.kill()
                    if bullet.shooter == self.player2:
                        self.player2Score += 1
                        if self.player2Score == self.winScore:
                            self.mode = 'p2Win'
                    elif bullet.shooter == self.player1:
                        self.player1Score += 1
                        if self.player1Score == self.winScore:
                            self.mode = 'p1Win'
                    elif bullet.shooter == self.player4:
                        self.player4Score += 1
                        if self.player4Score == self.winScore:
                            self.mode = 'p4Win'
                    bullet.kill()
                    self.initEachRound()
                    powerUpsStr = convertPowerUpSpritesToStr(self.powerUpsGroup)
                    message = ('powerUp %s True %d %d %d %d\n' %(powerUpsStr,
                     self.player1Score, self.player2Score, self.player3Score, self.player4Score))
                    msgList.append(message)
                    
            bullet = pygame.sprite.spritecollideany(self.player4, self.bulletGroup)
            if bullet != None:
                if bullet.shooter != self.player4:
                    self.player4.kill()
                    if bullet.shooter == self.player2:
                        self.player2Score += 1
                        if self.player2Score == self.winScore:
                            self.mode = 'p2Win'
                    elif bullet.shooter == self.player3:
                        self.player3Score += 1
                        if self.player3Score == self.winScore:
                            self.mode = 'p3Win'
                    elif bullet.shooter == self.player1:
                        self.player1Score += 1
                        if self.player1Score == self.winScore:
                            self.mode = 'p1Win'
                    bullet.kill()
                    self.initEachRound()
                    powerUpsStr = convertPowerUpSpritesToStr(self.powerUpsGroup)
                    message = ('powerUp %s True %d %d %d %d\n' %(powerUpsStr,
                     self.player1Score, self.player2Score, self.player3Score, self.player4Score))
                    msgList.append(message)
                    
            laserBeam = pygame.sprite.spritecollideany(self.player1, self.laserBeamGroup)
            if laserBeam != None:
                if laserBeam.shooter != self.player1:
                    self.player1.kill()
                    if laserBeam.shooter == self.player2:
                        self.player2Score += 1
                        if self.player2Score == self.winScore:
                            self.mode = 'p2Win'
                    elif laserBeam.shooter == self.player3:
                        self.player3Score += 1
                        if self.player3Score == self.winScore:
                            self.mode = 'p3Win'
                    elif laserBeam.shooter == self.player4:
                        self.player4Score += 1
                        if self.player4Score == self.winScore:
                            self.mode = 'p4Win'
                    laserBeam.kill()
                    self.initEachRound()
                    powerUpsStr = convertPowerUpSpritesToStr(self.powerUpsGroup)
                    message = ('powerUp %s True %d %d %d %d\n' %(powerUpsStr,
                     self.player1Score, self.player2Score, self.player3Score, self.player4Score))
                    msgList.append(message)
            
            laserBeam = pygame.sprite.spritecollideany(self.player2, self.laserBeamGroup)
            if laserBeam != None:
                if laserBeam.shooter != self.player2:
                    self.player2.kill()
                    if laserBeam.shooter == self.player1:
                        self.player1Score += 1
                        if self.player1Score == self.winScore:
                            self.mode = 'p1Win'
                    elif laserBeam.shooter == self.player3:
                        self.player3Score += 1
                        if self.player3Score == self.winScore:
                            self.mode = 'p3Win'
                    elif laserBeam.shooter == self.player4:
                        self.player4Score += 1
                        if self.player4Score == self.winScore:
                            self.mode = 'p4Win'
                    laserBeam.kill()
                    self.initEachRound()
                    powerUpsStr = convertPowerUpSpritesToStr(self.powerUpsGroup)
                    message = ('powerUp %s True %d %d %d %d\n' %(powerUpsStr,
                     self.player1Score, self.player2Score, self.player3Score, self.player4Score))
                    msgList.append(message)
            
            laserBeam = pygame.sprite.spritecollideany(self.player3, self.laserBeamGroup)
            if laserBeam != None:
                if laserBeam.shooter != self.player3:
                    self.player3.kill()
                    if laserBeam.shooter == self.player2:
                        self.player2Score += 1
                        if self.player2Score == self.winScore:
                            self.mode = 'p2Win'
                    elif laserBeam.shooter == self.player1:
                        self.player1Score += 1
                        if self.player1Score == self.winScore:
                            self.mode = 'p1Win'
                    elif laserBeam.shooter == self.player4:
                        self.player4Score += 1
                        if self.player4Score == self.winScore:
                            self.mode = 'p4Win'
                    laserBeam.kill()
                    self.initEachRound()
                    powerUpsStr = convertPowerUpSpritesToStr(self.powerUpsGroup)
                    message = ('powerUp %s True %d %d %d %d\n' %(powerUpsStr,
                     self.player1Score, self.player2Score, self.player3Score, self.player4Score))
                    msgList.append(message)
            
            laserBeam = pygame.sprite.spritecollideany(self.player4, self.laserBeamGroup)
            if laserBeam != None:
                if laserBeam.shooter != self.player4:
                    self.player4.kill()
                    if laserBeam.shooter == self.player2:
                        self.player2Score += 1
                        if self.player2Score == self.winScore:
                            self.mode = 'p2Win'
                    elif laserBeam.shooter == self.player3:
                        self.player3Score += 1
                        if self.player3Score == self.winScore:
                            self.mode = 'p3Win'
                    elif laserBeam.shooter == self.player1:
                        self.player1Score += 1
                        if self.player1Score == self.winScore:
                            self.mode = 'p1Win'
                    laserBeam.kill()
                    self.initEachRound()
                    powerUpsStr = convertPowerUpSpritesToStr(self.powerUpsGroup)
                    message = ('powerUp %s True %d %d %d %d\n' %(powerUpsStr,
                     self.player1Score, self.player2Score, self.player3Score, self.player4Score))
                    msgList.append(message)
            
        # collision controls for chase mode
        if self.mode == 'chase':
            
            if self.chaser == 'ketchup':
                playersCollide = pygame.sprite.spritecollide(self.player1,
                                 self.characters, False)
                if len(playersCollide) > 1:
                    killed = False
                    for player in playersCollide:
                        if player != self.player1:
                            if player.invincible == False:
                                player.kill()
                                killed = True
                                self.player1Score += 1
                                if self.player1Score == self.winScore:
                                    self.mode = 'p1Win'
                    if killed == True:
                        self.initEachRound()
            
            elif self.chaser == 'mustard':
                playersCollide = pygame.sprite.spritecollide(self.player2,
                                 self.characters, False)
                if len(playersCollide) > 1:
                    killed = False
                    for player in playersCollide:
                        if player != self.player2:
                            if player.invincible == False:
                                player.kill()
                                killed = True
                                self.player2Score += 1
                                if self.player2Score == self.winScore:
                                    self.mode = 'p2Win'
                    if killed == True:
                        self.initEachRound()
                
            elif self.chaser == 'mayo':
                playersCollide = pygame.sprite.spritecollide(self.player3,
                                 self.characters, False)
                if len(playersCollide) > 1:
                    killed = False
                    for player in playersCollide:
                        if player != self.player3:
                            if player.invincible == False:
                                player.kill()
                                killed = True
                                self.player3Score += 1
                                if self.player3Score == self.winScore:
                                    self.mode = 'p3Win'
                    if killed == True:
                        self.initEachRound()
            
            elif self.chaser == 'bbq':
                playersCollide = pygame.sprite.spritecollide(self.player4,
                                 self.characters, False)
                if len(playersCollide) > 1:
                    killed = False
                    for player in playersCollide:
                        if player != self.player4:
                            if player.invincible == False:
                                player.kill()
                                killed = True
                                self.player4Score += 1
                                if self.player4Score == self.winScore:
                                    self.mode = 'p4Win'
                    if killed == True:
                        self.initEachRound()
                    
        # sockets - handle sending messages
        if (msgList != []):
            for message in msgList:
                print ("sending: ", message,)
                self.server.send(message.encode())

    def drawStart(self, screen):
        diffY = self.screenHeight/10
        
        bgImage = self.startImage
        bgW, bgH = bgImage.get_size()
        screen.blit(bgImage, (-75,0))
        screen.blit(bgImage, (self.screenWidth*(2/3) + 75, 0))
        
        gameName = self.largeFont.render("KetchUp!", True, (255,255,255))
        nameWidth, nameHeight = gameName.get_size()
        screen.blit(gameName, (self.screenWidth/2-nameWidth/2, 2*diffY))
        
        text1 = self.standardFont.render("Press 'c' to start Chase Mode", True, (255,255,255))
        text1Width, text1Height = text1.get_size()
        screen.blit(text1, (self.screenWidth/2-text1Width/2, 5*diffY))
        
        text2 = self.standardFont.render("Press 'v' to start Shoot Mode", True, (255,255,255))
        text2Width, text2Height = text2.get_size()
        screen.blit(text2, (self.screenWidth/2-text2Width/2, 6*diffY))
        
        text3 = self.standardFont.render("Press 's' for settings", True, (255,255,255))
        text3Width, text3Height = text3.get_size()
        screen.blit(text3, (self.screenWidth/2-text3Width/2, 7*diffY))
        
        text4 = self.standardFont.render("Press 'h' for help", True, (255,255,255))
        text4Width, text4Height = text4.get_size()
        screen.blit(text4, (self.screenWidth/2-text4Width/2, 8*diffY))
        
    def drawHelpPage1(self, screen):
        diffY = self.screenHeight/20
        margin = 20
        
        title = self.largeFont.render('Help - Game Modes', True, (255,255,255))
        titleWidth, titleHeight = title.get_size()
        screen.blit(title, (self.screenWidth/2-titleWidth/2, 1*diffY))
        
        subtitle1 = self.boldFont.render('Chase Mode', True, (255,255,255))
        screen.blit(subtitle1, (margin, 3*diffY))
        
        text1 = self.standardFont.render(
        "If you are the 'chaser', catch your friends to earn a point! If not,",
                                            True, (255,255,255))
        screen.blit(text1, (margin, 4*diffY))
        
        text2 = self.standardFont.render(
        "then run away! (The 'chaser' changes every 10 seconds)",
                                            True, (255,255,255))
        screen.blit(text2, (margin, 5*diffY))
        
        text3 = self.underlineFont.render(
        "Power ups included:",
                                            True, (255,255,255))
        screen.blit(text3, (margin, 6*diffY))
        
        text4 = self.standardFont.render(
        "                                        Boot - increases player speed",
                                            True, (255,255,255))
        screen.blit(text4, (margin, 6*diffY))
        
        text5 = self.standardFont.render(
        "                                        Snail - decreases player speed",
                                            True, (255,255,255))
        screen.blit(text5, (margin, 7*diffY))
        
        text6 = self.standardFont.render(
        "                                        Shield - gives immunity for 3 seconds",
                                            True, (255,255,255))
        screen.blit(text6, (margin, 8*diffY))
        
        subtitle2 = self.boldFont.render('Shoot Mode', True, (255,255,255))
        screen.blit(subtitle2, (margin, 10*diffY))
        
        text7 = self.standardFont.render(
        "Collect power ups to earn ammo and shoot your friends down!",
                                            True, (255,255,255))
        screen.blit(text7, (margin, 11*diffY))
        
        screen.blit(text3, (margin, 12*diffY))
        
        text8 = self.standardFont.render(
        "                                        Gun - Fires a single bullet",
                                            True, (255,255,255))
        screen.blit(text8, (margin, 12*diffY))
        
        text9 = self.standardFont.render(
        "                                                    (cannot pass through walls)",
                                            True, (255,255,255))
        screen.blit(text9, (margin, 13*diffY))
        
        text10 = self.standardFont.render(
        "                                        Laser - Fires a single laser beam",
                                            True, (255,255,255))
        screen.blit(text10, (margin, 14*diffY))
        
        text11 = self.standardFont.render(
        "                                                      (able to pass through walls)",
                                            True, (255,255,255))
        screen.blit(text11, (margin, 15*diffY))
        
        text13 = self.standardFont.render(
        "Press the spacebar to go to the next page for controls",
                                            True, (255,255,255))
        text13Width, text13Height = text13.get_size()
        screen.blit(text13, (self.screenWidth/2-text13Width/2, 18*diffY))
        
    def drawHelpPage2(self, screen):
        diffY = self.screenHeight/20
        margin = 20
        
        title = self.largeFont.render('Help - Controls', True, (255,255,255))
        titleWidth, titleHeight = title.get_size()
        screen.blit(title, (self.screenWidth/2-titleWidth/2, 1*diffY))
        
        subtitle1 = self.boldFont.render('Player 1', True, (255,255,255))
        screen.blit(subtitle1, (margin, 4*diffY))
        
        text1 = self.standardFont.render("Press w to move up", True, (255,255,255))
        screen.blit(text1, (margin, 5*diffY))
        
        text2 = self.standardFont.render("Press a to move left", True, (255,255,255))
        screen.blit(text2, (margin, 6*diffY))
        
        text3 = self.standardFont.render("Press s to move down", True, (255,255,255))
        screen.blit(text3, (margin, 7*diffY))
        
        text4 = self.standardFont.render("Press d to move right", True, (255,255,255))
        screen.blit(text4, (margin, 8*diffY))
        
        text5 = self.standardFont.render("Press the spacebar to shoot", True, (255,255,255))
        screen.blit(text5, (margin, 9*diffY))
        
        subtitle2 = self.boldFont.render('Player 2', True, (255,255,255))
        screen.blit(subtitle2, (margin, 11*diffY))
        
        text6 = self.standardFont.render(
                    "Press the up arrow key to move up", True, (255,255,255))
        screen.blit(text6, (margin, 12*diffY))
        
        text7 = self.standardFont.render(
                    "Press the left arrow key to move left", True, (255,255,255))
        screen.blit(text7, (margin, 13*diffY))
        
        text8 = self.standardFont.render(
                    "Press the down arrow key to move down", True, (255,255,255))
        screen.blit(text8, (margin, 14*diffY))
        
        text9 = self.standardFont.render(
                    "Press the right arrow key to move right", True, (255,255,255))
        screen.blit(text9, (margin, 15*diffY))
        
        
        text10 = self.standardFont.render(
                    "Press the right ctrl key to shoot", True, (255,255,255))
        screen.blit(text10, (margin, 16*diffY))
        
        text11 = self.standardFont.render(
        "Press backspace to return to the main menu", True, (255,255,255))
        text11Width, text11Height = text11.get_size()
        screen.blit(text11, (self.screenWidth/2-text11Width/2, 18*diffY))
        
    # in-game display
    def drawScoreChase(self, screen):
        boxX = self.width
        boxY = 0
        boxW = self.screenWidth - self.width
        boxH = self.height
        boxXMid = boxX + (boxW//2)
        diffY = boxH // 20
        smallDiffY = boxH//27
        
        chaserWord = self.boldFont.render('Current Chaser:', True, (255,255,255))
        chaserW, chaserH = chaserWord.get_size()
        screen.blit(chaserWord, (boxXMid-chaserW//2, 1*diffY))
        
        if self.chaser == 'ketchup':
            currChaserImage = self.player1ImageLarge
        elif self.chaser == 'mustard':
            currChaserImage = self.player2ImageLarge
        elif self.chaser == 'mayo':
            currChaserImage = self.player3ImageLarge
        elif self.chaser == 'bbq':
            currChaserImage = self.player4ImageLarge
        currChaserW, currChaserH = currChaserImage.get_size()
        screen.blit(currChaserImage, (boxXMid-currChaserW//2, 2*diffY))
        
        if self.viewTimer == True:
            timeLeft = self.boldFont.render("Time left: %d" %self.count, True, (255,255,255))
            timeLeftW, timeLeftH = timeLeft.get_size()
            screen.blit(timeLeft, (boxXMid-timeLeftW//2, 6*diffY))
        
        # player 1
        name1 = self.standardFont.render("Ketchup", True, (255,255,255))
        name1W, name1H = name1.get_size()
        name1X = boxXMid - 5
        name1Y = 11.5*smallDiffY
        screen.blit(name1, (name1X, name1Y))
        
        player1ScoreSurface = self.standardFont.render(
                              "Score: %d" %(self.player1Score), 
                              True, (255,255,255))
        p1ScoreX = boxXMid - 3
        p1ScoreY = 12.5*smallDiffY
        screen.blit(player1ScoreSurface, (p1ScoreX, p1ScoreY))
        
        p1Image = self.player1ImageMed
        p1X = boxX + 20
        p1Y = 11*smallDiffY
        screen.blit(p1Image, (p1X,p1Y))
        
        # player 2
        name2 = self.standardFont.render("Mustard", True, (255,255,255))
        name2W, name2H = name2.get_size()
        name2X = boxXMid - 5
        name2Y = 15.5*smallDiffY
        screen.blit(name2, (name2X, name2Y))
        
        player2ScoreSurface = self.standardFont.render(
                              "Score: %d" %(self.player2Score), 
                              True, (255,255,255))
        p2ScoreX = boxXMid - 3
        p2ScoreY = 16.5*smallDiffY
        screen.blit(player2ScoreSurface, (p2ScoreX, p2ScoreY))
        
        p2Image = self.player2ImageMed
        p2X = boxX + 20
        p2Y = 15*smallDiffY
        screen.blit(p2Image, (p2X,p2Y))
        
        # player 3
        name3 = self.standardFont.render("Mayonnaise", True, (255,255,255))
        name3W, name3H = name3.get_size()
        name3X = boxXMid - 5
        name3Y = 19.5*smallDiffY
        screen.blit(name3, (name3X, name3Y))
        
        player3ScoreSurface = self.standardFont.render(
                              "Score: %d" %(self.player3Score), 
                              True, (255,255,255))
        p3ScoreX = boxXMid - 3
        p3ScoreY = 20.5*smallDiffY
        screen.blit(player3ScoreSurface, (p3ScoreX, p3ScoreY))
        
        p3Image = self.player3ImageMed
        p3X = boxX + 20
        p3Y = 19*smallDiffY
        screen.blit(p3Image, (p3X,p3Y))
        
        # player 4
        name4 = self.standardFont.render("BBQ", True, (255,255,255))
        name4W, name4H = name4.get_size()
        name4X = boxXMid - 5
        name4Y = 23.5*smallDiffY
        screen.blit(name4, (name4X, name4Y))
        
        player4ScoreSurface = self.standardFont.render(
                              "Score: %d" %(self.player4Score), 
                              True, (255,255,255))
        p4ScoreX = boxXMid - 3
        p4ScoreY = 24.5*smallDiffY
        screen.blit(player4ScoreSurface, (p4ScoreX, p4ScoreY))
        
        p4Image = self.player4ImageMed
        p4X = boxX + 20
        p4Y = 23*smallDiffY
        screen.blit(p4Image, (p4X,p4Y))
        
    # in-game display
    def drawScoreShoot(self, screen):
        boxX = self.width
        boxY = 0
        boxW = self.screenWidth - self.width
        boxH = self.height
        boxXMid = boxX + (boxW//2)
        smallDiffY = boxH//5
        
        # player 1
        name1 = self.standardFont.render("Ketchup", True, (255,255,255))
        name1W, name1H = name1.get_size()
        name1X = boxXMid - 5
        name1Y = 1*smallDiffY- 20
        screen.blit(name1, (name1X, name1Y))
        
        player1ScoreSurface = self.standardFont.render(
                              "Score: %d" %(self.player1Score), 
                              True, (255,255,255))
        p1ScoreX = boxXMid - 3
        p1ScoreY = 1.2*smallDiffY- 20
        screen.blit(player1ScoreSurface, (p1ScoreX, p1ScoreY))
        
        item1 = self.standardFont.render("Item: %s" %self.player1.item,
                                          True, (255,255,255))
        item1Width, item1Height = item1.get_size()
        item1X = boxXMid - 12
        item1Y = 1.4*smallDiffY- 20
        screen.blit(item1, (item1X,item1Y))
        
        p1Image = self.player1ImageMed
        p1X = boxX + 20
        p1Y = 1*smallDiffY- 20
        screen.blit(p1Image, (p1X,p1Y))
        
        # player 2
        name2 = self.standardFont.render("Mustard", True, (255,255,255))
        name2W, name2H = name2.get_size()
        name2X = boxXMid - 5
        name2Y = 2*smallDiffY- 20
        screen.blit(name2, (name2X, name2Y))
        
        player2ScoreSurface = self.standardFont.render(
                              "Score: %d" %(self.player2Score), 
                              True, (255,255,255))
        p2ScoreX = boxXMid - 3
        p2ScoreY = 2.2*smallDiffY- 20
        screen.blit(player2ScoreSurface, (p2ScoreX, p2ScoreY))
        
        item2 = self.standardFont.render("Item: %s" %self.player2.item,
                                          True, (255,255,255))
        item2Width, item2Height = item2.get_size()
        item2X = boxXMid - 12
        item2Y = 2.4*smallDiffY- 20
        screen.blit(item2, (item2X,item2Y))
        
        p2Image = self.player2ImageMed
        p2X = boxX + 20
        p2Y = 2*smallDiffY- 20
        screen.blit(p2Image, (p2X,p2Y))
        
        # player 3
        name3 = self.standardFont.render("Mayonnaise", True, (255,255,255))
        name3W, name3H = name3.get_size()
        name3X = boxXMid - 5
        name3Y = 3*smallDiffY- 20
        screen.blit(name3, (name3X, name3Y))
        
        player3ScoreSurface = self.standardFont.render(
                              "Score: %d" %(self.player3Score), 
                              True, (255,255,255))
        p3ScoreX = boxXMid - 3
        p3ScoreY = 3.2*smallDiffY- 20
        screen.blit(player3ScoreSurface, (p3ScoreX, p3ScoreY))
        
        item3 = self.standardFont.render("Item: %s" %self.player3.item,
                                          True, (255,255,255))
        item3Width, item3Height = item3.get_size()
        item3X = boxXMid - 12
        item3Y = 3.4*smallDiffY- 20
        screen.blit(item3, (item3X,item3Y))
        
        p3Image = self.player3ImageMed
        p3X = boxX + 20
        p3Y = 3*smallDiffY- 20
        screen.blit(p3Image, (p3X,p3Y))
        
        # player 4
        name4 = self.standardFont.render("BBQ", True, (255,255,255))
        name4W, name4H = name4.get_size()
        name4X = boxXMid - 5
        name4Y = 4*smallDiffY- 20
        screen.blit(name4, (name4X, name4Y))
        
        player4ScoreSurface = self.standardFont.render(
                              "Score: %d" %(self.player4Score), 
                              True, (255,255,255))
        p4ScoreX = boxXMid - 3
        p4ScoreY = 4.2*smallDiffY- 20
        screen.blit(player4ScoreSurface, (p4ScoreX, p4ScoreY))
        
        item4 = self.standardFont.render("Item: %s" %self.player4.item,
                                          True, (255,255,255))
        item4Width, item4Height = item4.get_size()
        item4X = boxXMid - 12
        item4Y = 4.4*smallDiffY- 20
        screen.blit(item4, (item4X,item4Y))
        
        p4Image = self.player4ImageMed
        p4X = boxX + 20
        p4Y = 4*smallDiffY - 20
        screen.blit(p4Image, (p4X,p4Y))
        
    def drawWin(self, screen, winner, mode):
        midX = self.screenWidth//2
        diffY = self.screenHeight // 20
        smallDiffY = self.screenHeight // 27
        
        if mode == 'shoot':
            if winner == 'Ketchup':
                text1 = self.largeFont.render('You won!', True, (255,255,255))
                text1W, text1H = text1.get_size()
                screen.blit(text1, (midX-text1W//2, 1*diffY))
            else:
                text1 = self.largeFont.render('%s won! You lost...' %winner, True, (255,255,255))
                text1W, text1H = text1.get_size()
                screen.blit(text1, (midX-text1W//2, 1*diffY))
        
        elif mode == 'chase':
            text1 = self.largeFont.render('%s won!' %winner, True, (255,255,255))
            text1W, text1H = text1.get_size()
            screen.blit(text1, (midX-text1W//2, 1*diffY))
        
        if winner == 'Ketchup':
            currChaserImage = self.player1ImageLarge
        elif winner == 'Mustard':
            currChaserImage = self.player2ImageLarge
        elif winner == 'Mayonnaise':
            currChaserImage = self.player3ImageLarge
        elif winner == 'BBQ':
            currChaserImage = self.player4ImageLarge
        currChaserW, currChaserH = currChaserImage.get_size()
        screen.blit(currChaserImage, (midX-currChaserW//2, 3*diffY))
        
        text2 = self.boldFont.render('Final Scores', True, (255,255,255))
        text2W, text2H = text2.get_size()
        screen.blit(text2, (midX-text2W//2, 9*diffY))
        
        # player 1
        name1 = self.standardFont.render("Ketchup", True, (255,255,255))
        name1X = self.screenWidth//4 + 70
        name1Y = 12*diffY
        screen.blit(name1, (name1X, name1Y))
        
        player1ScoreSurface = self.standardFont.render(
                              "Score: %d" %(self.player1Score), 
                              True, (255,255,255))
        p1ScoreW, p1ScoreH = player1ScoreSurface.get_size()
        p1ScoreX = self.screenWidth//4 + 70
        p1ScoreY = name1Y + smallDiffY
        screen.blit(player1ScoreSurface, (p1ScoreX, p1ScoreY))
        
        p1Image = self.player1ImageMed
        p1X = self.screenWidth//4
        p1Y = name1Y - (0.5*smallDiffY)
        screen.blit(p1Image, (p1X,p1Y))
        
        # player 2
        name2 = self.standardFont.render("Mustard", True, (255,255,255))
        name2W, name2H = name2.get_size()
        name2X = self.screenWidth*(3/4) - name2W
        name2Y = 12*diffY
        screen.blit(name2, (name2X, name2Y))
        
        player2ScoreSurface = self.standardFont.render(
                              "Score: %d" %(self.player2Score), 
                              True, (255,255,255))
        p2ScoreX = self.screenWidth*(3/4) - name2W
        p2ScoreY = name2Y + smallDiffY
        screen.blit(player2ScoreSurface, (p2ScoreX, p2ScoreY))
        
        p2Image = self.player2ImageMed
        p2X = self.screenWidth*(3/4) - 131
        p2Y = name2Y - (0.5*smallDiffY)
        screen.blit(p2Image, (p2X,p2Y))
        
        # player 3
        name3 = self.standardFont.render("Mayonnaise", True, (255,255,255))
        name3W, name3H = name3.get_size()
        name3X = self.screenWidth//4 + 70
        name3Y = 16*diffY
        screen.blit(name3, (name3X, name3Y))
        
        player3ScoreSurface = self.standardFont.render(
                              "Score: %d" %(self.player3Score), 
                              True, (255,255,255))
        p3ScoreX = self.screenWidth//4 + 70
        p3ScoreY = name3Y + smallDiffY
        screen.blit(player3ScoreSurface, (p3ScoreX, p3ScoreY))
        
        p3Image = self.player3ImageMed
        p3X = self.screenWidth//4
        p3Y = name3Y - (0.5*smallDiffY)
        screen.blit(p3Image, (p3X,p3Y))
        
        # player 4
        name4 = self.standardFont.render("BBQ", True, (255,255,255))
        name4W, name4H = name4.get_size()
        name4X = self.screenWidth*(3/4) - name2W
        name4Y = 16*diffY
        screen.blit(name4, (name4X, name4Y))
        
        player4ScoreSurface = self.standardFont.render(
                              "Score: %d" %(self.player4Score), 
                              True, (255,255,255))
        p4ScoreX = self.screenWidth*(3/4) - name2W
        p4ScoreY = name4Y + smallDiffY
        screen.blit(player4ScoreSurface, (p4ScoreX, p4ScoreY))
        
        p4Image = self.player4ImageMed
        p4X = self.screenWidth*(3/4) - 131
        p4Y = name4Y - (0.5*smallDiffY)
        screen.blit(p4Image, (p4X,p4Y))
        
    def drawP1WinShoot(self, screen):
        winner = 'Ketchup'
        self.drawWin(screen, winner, 'shoot')
        
    def drawP2WinShoot(self, screen):
        winner = 'Mustard'
        self.drawWin(screen, winner, 'shoot')
    
    def drawP3WinShoot(self, screen):
        winner = 'Mayonnaise'
        self.drawWin(screen, winner, 'shoot')
    
    def drawP4WinShoot(self, screen):
        winner = 'BBQ'
        self.drawWin(screen, winner, 'shoot')
    
    def drawP1WinChase(self, screen):
        winner = 'Ketchup'
        self.drawWin(screen, winner, 'chase')
        
    def drawP2WinChase(self, screen):
        winner = 'Mustard'
        self.drawWin(screen, winner, 'chase')
    
    def drawP3WinChase(self, screen):
        winner = 'Mayonnaise'
        self.drawWin(screen, winner, 'chase')
    
    def drawP4WinChase(self, screen):
        winner = 'BBQ'
        self.drawWin(screen, winner, 'chase')
        
    def drawSettings(self, screen):
        midX = self.screenWidth//2
        diffY = self.screenHeight//20
        testWords = self.boldFont.render('test', True, (255,255,255))
        wordH = testWords.get_height()
        margin = 3
        boxH = wordH + margin*2
        
        title = self.largeFont.render('Settings', True, (255,255,255))
        titleW, titleH = title.get_size()
        titleX = midX - titleW//2
        titleY = 1*diffY
        screen.blit(title, (titleX, titleY))
        
        # Board Size
        boardL = self.boldFont.render('Size of Board:', True, (255,255,255))
        boardLX = self.screenWidth//4
        boardLY = 5*diffY
        
        boardR = self.boldFont.render('Small  /  Medium  /  Large', True, (255,255,255))
        boardRX = self.screenWidth//2
        boardRY = 5*diffY
        
        box1Y = boardRY - margin
        if self.boardSize == self.boardSizes[0]:
            box1W = 62
            box1X = int(self.screenWidth*(0.5)) - 5
        elif self.boardSize == self.boardSizes[1]:
            box1W = 75
            box1X = int(self.screenWidth*(0.6))
        elif self.boardSize == self.boardSizes[2]:
            box1W = 62
            box1X = int(self.screenWidth*(0.72)) + 1
            
        pygame.draw.rect(screen, (34,139,34), (box1X,box1Y,box1W,boxH))
        screen.blit(boardL, (boardLX, boardLY))
        screen.blit(boardR, (boardRX, boardRY))
        
        # No. of points to win
        pointsL = self.boldFont.render('Number of Points to Win:', True, (255,255,255))
        pointsLX = self.screenWidth//4
        pointsLY = 7*diffY
        
        pointsR = self.boldFont.render('3  /  5  /  7', True, (255,255,255))
        pointsRX = int(self.screenWidth*(5/8))
        pointsRY = 7*diffY
        
        box2Y = pointsRY - margin - 1
        if self.winScore == 3:
            box2W = 25
            box2X = int(self.screenWidth*(0.61)) + 5
        elif self.winScore == 5:
            box2W = 25
            box2X = int(self.screenWidth*(0.67)) - 4
        elif self.winScore == 7:
            box2W = 25
            box2X = int(self.screenWidth*(0.72)) - 3
            
        pygame.draw.rect(screen, (34,139,34), (box2X,box2Y,box2W,boxH))
        screen.blit(pointsL, (pointsLX, pointsLY))
        screen.blit(pointsR, (pointsRX, pointsRY))
        
        # Timer
        timerL = self.boldFont.render('Show timer for each turn:', True, (255,255,255))
        timerLX = self.screenWidth//4
        timerLY = 9*diffY
        
        timerR = self.boldFont.render('On  /  Off', True, (255,255,255))
        timerRX = int(self.screenWidth*(5/8))
        timerRY = 9*diffY
        
        box3Y = timerRY - margin - 1
        if self.viewTimer == True:
            box3W = 36
            box3X = int(self.screenWidth*(0.61)) + 7
        elif self.viewTimer == False:
            box3W = 38
            box3X = int(self.screenWidth*(0.69))
            
        pygame.draw.rect(screen, (34,139,34), (box3X,box3Y,box3W,boxH))
        screen.blit(timerL, (timerLX, timerLY))
        screen.blit(timerR, (timerRX, timerRY))
        
        # Computer Difficulty
        compDiffL = self.boldFont.render('Computer Difficulty Level:', True, (255,255,255))
        compDiffLX = self.screenWidth//4
        compDiffLY = 11*diffY
        
        compDiffR = self.boldFont.render('Easy  /  Hard', True, (255,255,255))
        compDiffRX = int(self.screenWidth*(5/8))
        compDiffRY = 11*diffY
        
        box4Y = compDiffRY - margin
        if self.computerDifficulty == 'easy':
            box4W = 52
            box4X = int(self.screenWidth*(0.61)) + 7
        elif self.computerDifficulty == 'hard':
            box4W = 52
            box4X = int(self.screenWidth*(0.71))
            
        pygame.draw.rect(screen, (34,139,34), (box4X,box4Y,box4W,boxH))
        screen.blit(compDiffL, (compDiffLX, compDiffLY))
        screen.blit(compDiffR, (compDiffRX, compDiffRY))
        
        # Selection Box
        box5H = int(diffY*1.2)
        box5W = self.screenWidth//1.6
        box5X = midX - box5W//2
        if self.settingsRow == 0:
            box5Y = 4*diffY + 21
        elif self.settingsRow == 1:
            box5Y = 6*diffY + 20
        elif self.settingsRow == 2:
            box5Y = 8*diffY + 20
        elif self.settingsRow == 3:
            box5Y = 10*diffY + 21
        pygame.draw.rect(screen, (255,255,255), (box5X,box5Y,box5W,box5H), 3)
        
        # Instructions
        text1 = self.standardFont.render(
        "Use the arrow keys to select your options", True, (255,255,255))
        text1Width, text1Height = text1.get_size()
        screen.blit(text1, (midX-text1Width//2, 16*diffY))
        
        text2 = self.standardFont.render(
        "Press backspace to return to the main menu", True, (255,255,255))
        text2Width, text2Height = text2.get_size()
        screen.blit(text2, (midX-text2Width//2, 17*diffY))
    
    # For invincibility
    def drawBubble(self,screen):
        for player in self.characters:
            if player.invincible == True:
                x = int(player.x - self.bubbleW/2)
                y = int(player.y - self.bubbleH/2)
                screen.blit(self.bubbleImage, (x,y))
        
    def redrawAll(self, screen):
        if self.mode == 'chase' or self.mode == 'shoot':
            self.wallGroup.draw(screen)
            self.bulletGroup.draw(screen)
            self.laserBeamGroup.draw(screen)
            self.powerUpsGroup.draw(screen)
            self.characters.draw(screen)
            self.drawBubble(screen)
        
        if self.mode == 'chase':
            self.drawScoreChase(screen)
        
        if self.mode == 'shoot':
            self.drawScoreShoot(screen)
        
        elif self.mode == 'start':
            self.drawStart(screen)
            
        elif self.mode == 'helpP1':
            self.drawHelpPage1(screen)
            
        elif self.mode == 'helpP2':
            self.drawHelpPage2(screen)
            
        elif self.mode == 'p1Win' and self.lastMode == 'shoot':
            self.drawP1WinShoot(screen)
            
        elif self.mode == 'p2Win' and self.lastMode == 'shoot':
            self.drawP2WinShoot(screen)
        
        elif self.mode == 'p3Win' and self.lastMode == 'shoot':
            self.drawP3WinShoot(screen)
        
        elif self.mode == 'p4Win' and self.lastMode == 'shoot':
            self.drawP4WinShoot(screen)
        
        elif self.mode == 'p1Win' and self.lastMode == 'chase':
            self.drawP1WinChase(screen)
            
        elif self.mode == 'p2Win' and self.lastMode == 'chase':
            self.drawP2WinChase(screen)
        
        elif self.mode == 'p3Win' and self.lastMode == 'chase':
            self.drawP3WinChase(screen)
        
        elif self.mode == 'p4Win' and self.lastMode == 'chase':
            self.drawP4WinChase(screen)
            
        elif self.mode == 'settings':
            self.drawSettings(screen)

#creating and running the game
ketchUp = myProject()
# sets up sockets handling
serverMsg = Queue(100)
threading.Thread(target = handleServerMsg, args = (server, serverMsg)).start()
ketchUp.run(serverMsg, server)