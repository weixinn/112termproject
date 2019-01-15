'''
This file is the client file for player 2. By executing this file you can play
'shoot' mode multiplayer across computers.

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
        
        pygame.mixer.music.load('bgMusic.mp3')
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
        
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
        
        self.numRows = 1
        self.numCols = 1
        self.winScore = 5
        self.wallGroup = pygame.sprite.Group()
        self.wallMap = [[]]
        self.powerUpsGroup = pygame.sprite.Group()
    
    def initNewGame(self):
        
        if self.mode == 'shoot':
            self.wallSize = int(self.width/self.numCols)
            
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
            
            # player 3 and 4 are computers
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
        
        if self.mode == 'shoot':
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
            self.player3 = GameCharacter(self.player3X, self.player3Y, self.player3Image, self.speed)
            self.characters.add(self.player3)
            self.player4 = GameCharacter(self.player4X, self.player4Y, self.player4Image, self.speed)
            self.characters.add(self.player4)
        
        
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
        
        if self.mode == 'shoot':
            if keyCode == 32:
                self.player2.useItem()
                msgList.append('fire nothing\n')
         
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
        
                if (command == "newGame"):
                    self.mode = msg[2]
                    self.wallMap = createMapFromStr(msg[3])
                    self.numRows = int(msg[4])
                    self.numCols = int(msg[5])
                    self.winScore = int(msg[6])
                    self.initNewGame()
                
                elif (command == 'move'):
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
                
                elif command == 'powerUp':
                    
                    def addSpriteFromStr(str, group):
                        powerUps = str.split('&')
                        for i in range (len(powerUps)-1):
                            powerUp = powerUps[i]
                            attributes = powerUp.split('#')
                            row = int(attributes[0])
                            col = int(attributes[1])
                            powerUpType = attributes[2]
                            width = int(attributes[3])
                            height = int(attributes[4])
                            if powerUpType == '<class\'__main__.Gun\'>':
                                img = self.gunImage
                                single = Gun(row, col, img, width, height)
                            elif powerUpType == '<class\'__main__.Laser\'>':
                                img = self.laserImage
                                single = Laser(row, col, img, width, height)
                            group.add(single)
        
                    powerUpStr = ''
                    for i in range (2, len(msg) - 5):
                        powerUpStr += str(msg[i])
                    self.powerUpsGroup.empty()
                    addSpriteFromStr(powerUpStr, self.powerUpsGroup)
                    
                    newRound = msg[-5]
                    if newRound == 'True':
                        self.initEachRound()
                    
                    self.player1Score = int(msg[-4])
                    self.player2Score = int(msg[-3])
                    self.player3Score = int(msg[-2])
                    self.player4Score = int(msg[-1])
                    
                    if self.player1Score == self.winScore:
                        self.mode = 'p1Win'
                    elif self.player2Score == self.winScore:
                        self.mode = 'p2Win'
                    elif self.player3Score == self.winScore:
                        self.mode = 'p3Win'
                    elif self.player4Score == self.winScore:
                        self.mode = 'p4Win'
                
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
        
        if self.mode == 'shoot':
            
            self.time += 1 #counts number of times timerFired is called
            
            # rotates the chaser between players during each round
            if self.time%self.fps == 0:
                self.count -= 1 # counts the seconds
                if self.count < 1:
                    self.count = 10
                    
            # controls for player 2
            if self.isKeyPressed(pygame.K_a):
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
                msgList.append('move %d %d %s\n' % 
                    (self.player2.x, self.player2.y, self.player2.lastDir))
                    
            if self.isKeyPressed(pygame.K_d):
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
                if self.mode == 'shoot':
                    msgList.append('move %d %d %s\n' % 
                        (self.player2.x, self.player2.y, self.player2.lastDir))
                
            if self.isKeyPressed(pygame.K_w):
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
                if self.mode == 'shoot':
                    msgList.append('move %d %d %s\n' % 
                        (self.player2.x, self.player2.y, self.player2.lastDir))
                    
            if self.isKeyPressed(pygame.K_s):
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
                if self.mode == 'shoot':
                    msgList.append('move %d %d %s\n' % 
                        (self.player2.x, self.player2.y, self.player2.lastDir))
                    
                    
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
            pygame.sprite.groupcollide(self.bulletGroup, self.laserBeamGroup, True, False)
            
            # collision detection between ammo and players
            bullet = pygame.sprite.spritecollideany(self.player1, self.bulletGroup)
            if bullet != None:
                if bullet.shooter != self.player1:
                    self.player1.kill()
                    bullet.kill()
                    self.initEachRound()
            
            bullet = pygame.sprite.spritecollideany(self.player2, self.bulletGroup)
            if bullet != None:
                if bullet.shooter != self.player2:
                    self.player2.kill()
                    bullet.kill()
                    self.initEachRound()
            
            bullet = pygame.sprite.spritecollideany(self.player3, self.bulletGroup)
            if bullet != None:
                if bullet.shooter != self.player3:
                    self.player3.kill()
                    bullet.kill()
                    self.initEachRound()
                    
            bullet = pygame.sprite.spritecollideany(self.player4, self.bulletGroup)
            if bullet != None:
                if bullet.shooter != self.player4:
                    self.player4.kill()
                    bullet.kill()
                    self.initEachRound()
                    
            laserBeam = pygame.sprite.spritecollideany(self.player1, self.laserBeamGroup)
            if laserBeam != None:
                if laserBeam.shooter != self.player1:
                    self.player1.kill()
                    laserBeam.kill()
                    self.initEachRound()
            
            laserBeam = pygame.sprite.spritecollideany(self.player2, self.laserBeamGroup)
            if laserBeam != None:
                if laserBeam.shooter != self.player2:
                    self.player2.kill()
                    laserBeam.kill()
                    self.initEachRound()
            
            laserBeam = pygame.sprite.spritecollideany(self.player3, self.laserBeamGroup)
            if laserBeam != None:
                if laserBeam.shooter != self.player3:
                    self.player3.kill()
                    laserBeam.kill()
                    self.initEachRound()
            
            laserBeam = pygame.sprite.spritecollideany(self.player4, self.laserBeamGroup)
            if laserBeam != None:
                if laserBeam.shooter != self.player4:
                    self.player4.kill()
                    laserBeam.kill()
                    self.initEachRound()
        
        # sockets - handles sending messages
        if (msgList != []):
            for message in msgList:
                print ("sending: ", message,)
                self.server.send(message.encode())
            

    def drawStart(self, screen):
        diffY = self.screenHeight/10
        
        gameName = self.largeFont.render("Waiting for Player 1 to start the game...",
                                          True, (255,255,255))
        nameWidth, nameHeight = gameName.get_size()
        screen.blit(gameName, (self.screenWidth/2-nameWidth/2, 2*diffY))
    
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
        
    def drawWin(self, screen, winner):
        midX = self.screenWidth//2
        diffY = self.screenHeight // 20
        smallDiffY = self.screenHeight // 27
        
        if winner == 'Mustard':
            text1 = self.largeFont.render('You won!', True, (255,255,255))
            text1W, text1H = text1.get_size()
            screen.blit(text1, (midX-text1W//2, 1*diffY))
        else:
            text1 = self.largeFont.render('%s won! You lost...' %winner, True, (255,255,255))
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
        
    def drawP1Win(self, screen):
        winner = 'Ketchup'
        self.drawWin(screen, winner)
        
    def drawP2Win(self, screen):
        winner = 'Mustard'
        self.drawWin(screen, winner)
    
    def drawP3Win(self, screen):
        winner = 'Mayonnaise'
        self.drawWin(screen, winner)
    
    def drawP4Win(self, screen):
        winner = 'BBQ'
        self.drawWin(screen, winner)
        
    def redrawAll(self, screen):
        if self.mode == 'shoot':
            self.wallGroup.draw(screen)
            self.bulletGroup.draw(screen)
            self.laserBeamGroup.draw(screen)
            self.powerUpsGroup.draw(screen)
            self.characters.draw(screen)
            self.drawScoreShoot(screen)
        
        elif self.mode == 'start':
            self.drawStart(screen)
            
        elif self.mode == 'p1Win':
            self.drawP1Win(screen)
            
        elif self.mode == 'p2Win':
            self.drawP2Win(screen)
        
        elif self.mode == 'p3Win':
            self.drawP3Win(screen)
        
        elif self.mode == 'p4Win':
            self.drawP4Win(screen)

#creating and running the game
ketchUp = myProject()
# sets up sockets handling
serverMsg = Queue(100)
threading.Thread(target = handleServerMsg, args = (server, serverMsg)).start()
ketchUp.run(serverMsg, server)