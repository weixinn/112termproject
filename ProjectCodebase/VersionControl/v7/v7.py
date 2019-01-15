import pygame
import pygamegame #the framework
from helperFunctions import *
#from gameCharacter import *

# from last try, added dumb AI and user interface
# things to do:
#               - add in shield
#               - bg music
#               - basic AI
#               - clean up code
#               - settings
#               - num of AIs needed: 1. chaser AI, 2. running AI, 3. shooting AI
#               - customisable board

# what to do NOW: do running AI
#                 redo draw score

'''
what the chasing AI does:
    1. finds the closest player
    2. finds any route to it using backtracking
    3. moves according to the route using absolute x and y coordinates
    4. reaches that position
    5. finds a new route

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
    def __init__(self, x, y, image, speed):
        super().__init__(x, y, image, speed)
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
            
            targetQuadrant = oppQuadrant(getQuadrant(chaserPos, ketchUp.width, ketchUp.height))
            self.targetPos = getCornerPos(targetQuadrant, ketchUp.numRows-3, ketchUp.numCols-3)
            routeDir = aStarFindRoute(ketchUp.wallMap, self.pos, self.targetPos)
            x, y = getCoordFromPos(self.pos, ketchUp.wallSize)
            self.route = convertRoute(routeDir, x, y, ketchUp.wallSize)
            
    
    def move(self):
        nextX, nextY = self.route[0]
        diffX = nextX - self.x
        diffY = nextY - self.y
        
        if diffX > 0: # to the right
            if abs(diffX) >= self.speed:
                self.x += self.speed
            else:
                self.x += abs(diffX)
        elif diffX < 0: # to the left
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
    # DON'T CHANGE __INIT__ BECAUSE IT HAS ALREADY BEEN SET UP IN PYGAMEGAME
    # TO HANDLE STUFF LIKE WINDOW WIDTH AND HEIGHT. JUST USE A SECOND SELF DEFINED
    # INIT IT'S FINE :D
    
    def init(self):
        self.width = self.screenWidth
        self.height = self.width
        self.mode = 'start'
        
        self.boardSizes = ['small', 'medium', 'large']
        self.boardSize = self.boardSizes[2]
        
        # DON'T BE CONFUSED!! actual board rows and cols is self.numRows and
        # self.numCols - 2!!
        if self.boardSize == self.boardSizes[0]:
            self.numRows = 10
            self.numCols = 10
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
        self.powerUpsGroup = pygame.sprite.Group()
        
        # points right
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
        self.devilImage = pygame.transform.scale(pygame.image.load(
                            'images/emojiDevil.png').convert_alpha(), (self.wallSize,self.wallSize))
        self.devilImageH, self.devilImageW = self.devilImage.get_size()
        self.scaredImage = pygame.transform.scale(pygame.image.load(
                            'images/emojiScared.png').convert_alpha(), (self.wallSize,self.wallSize))
        self.scaredImageH, self.scaredImageW = self.scaredImage.get_size()
                            
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
        
        self.winScore = 5
        
        self.standardFont = pygame.font.SysFont(None,23)
        self.boldFont = pygame.font.SysFont(None,25,True)
        self.underlineFont = pygame.font.SysFont(None,23)
        self.italicFont = pygame.font.SysFont(None,23, False, True)
        self.underlineFont.set_underline(True)
        self.largeFont = pygame.font.SysFont(None,50)
        
        self.initEachRound()
    
    # only call this init to reset each round and not the whole game
    def initEachRound(self):
        
        # this chunk is only temporary just so the game can function for now
        self.time = 0
        self.count = 10
        self.characters = ('ketchup','mustard','mayo','bbq')
        self.chaser = self.characters[random.randint(0,3)]
        
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
        self.player3 = Computer(self.player3X, self.player3Y, self.player3Image, self.speed)
        self.characters.add(self.player3)
        self.player4 = Computer(self.player4X, self.player4Y, self.player4Image, self.speed)
        self.characters.add(self.player4)
        
        if self.chaser == 'mayo':
            print (1)
            self.player3.mode = 'chase'
            self.player4.mode = 'run'
        elif self.chaser == 'bbq':
            print (2)
            self.player3.mode = 'run'
            self.player4.mode = 'chase'
        else:
            print (3)
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
        def isLegalPosition(self, row, col):
            if row == None or col == None:
                return False
            elif row == 1 and col == 1:
                return False
            elif row == self.numRows-2 and col == self.numCols-2:
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
            powerUp = powerUpType(powerUpRow, powerUpCol, powerUpImage, powerUpWidth, powerUpHeight)
            self.powerUpsGroup.add(powerUp)
        
    def generateWalls(self):
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
        if keyCode == 114:
            self.init()
        
        if self.mode == 'start':
            if keyCode == 99:
                self.mode = 'chase'
                self.initEachRound()
            
            elif keyCode == 118:
                self.mode = 'shoot'
                self.initEachRound()
            
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
        
        elif self.mode == 'chase' or self.mode == 'shoot':
            if keyCode == 32:
                self.player1.useItem()
            
            elif keyCode == 305:
                self.player2.useItem()
    
    def timerFired(self, dt):
        
        print (self.chaser)
        
        if self.mode == 'chase' or self.mode == 'shoot':
            
            self.time += 1 #counts number of times timerFired is called
            
            # rotates the chaser between players
            if self.time%self.fps == 0:
                self.count -= 1 # counts the seconds
                if self.count < 1:
                    self.count = 10
                    if self.mode == 'chase':
                        self.generatePowerUps(self.powerUpsChase)
                    elif self.mode == 'shoot':
                        self.generatePowerUps(self.powerUpsShoot)
                        
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
                        self.chaser == 'bbq'
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
                    
            #controls for player 1
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
                        pass
        
        
        # !!!!!!!!!!!! rewrite this to include player 3 and 4 later !!!!!!!!!!!!
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
            
            
            bullet = pygame.sprite.spritecollideany(self.player1, self.bulletGroup)
            if bullet != None:
                if bullet.shooter != self.player1:
                    self.player1.kill()
                    self.player2Score += 1
                    if self.player2Score == self.winScore:
                        self.mode = 'p2Win'
                    bullet.kill()
                    self.initEachRound()
            
            bullet = pygame.sprite.spritecollideany(self.player2, self.bulletGroup)
            if bullet != None:
                if bullet.shooter != self.player2:
                    self.player2.kill()
                    self.player1Score += 1
                    if self.player1Score == self.winScore:
                        self.mode = 'p1Win'
                    bullet.kill()
                    self.initEachRound()
                    
            laserBeam = pygame.sprite.spritecollideany(self.player1, self.laserBeamGroup)
            if laserBeam != None:
                if laserBeam.shooter != self.player1:
                    self.player1.kill()
                    self.player2Score += 1
                    if self.player2Score == self.winScore:
                        self.mode = 'p2Win'
                    laserBeam.kill()
                    self.initEachRound()
            
            laserBeam = pygame.sprite.spritecollideany(self.player2, self.laserBeamGroup)
            if laserBeam != None:
                if laserBeam.shooter != self.player2:
                    self.player2.kill()
                    self.player1Score += 1
                    if self.player1Score == self.winScore:
                        self.mode = 'p1Win'
                    laserBeam.kill()
                    self.initEachRound()
            
            
        # collision controls for chase mode
        if self.mode == 'chase':
            
            if self.chaser == 'ketchup':
                playersCollide = pygame.sprite.spritecollide(self.player1,
                                 self.characters, False)
                if len(playersCollide) > 1:
                    for player in playersCollide:
                        if player != self.player1:
                            player.kill()
                            self.player1Score += 1
                            if self.player1Score == self.winScore:
                                self.mode = 'p1Win'
                    self.initEachRound()
            
            elif self.chaser == 'mustard':
                playersCollide = pygame.sprite.spritecollide(self.player2,
                                 self.characters, False)
                if len(playersCollide) > 1:
                    for player in playersCollide:
                        if player != self.player2:
                            player.kill()
                            self.player2Score += 1
                            if self.player2Score == self.winScore:
                                self.mode = 'p2Win'
                    self.initEachRound()
                
            elif self.chaser == 'mayo':
                playersCollide = pygame.sprite.spritecollide(self.player3,
                                 self.characters, False)
                if len(playersCollide) > 1:
                    for player in playersCollide:
                        if player != self.player3:
                            player.kill()
                            self.player3Score += 1
                            if self.player3Score == self.winScore:
                                self.mode = 'p3Win'
                    self.initEachRound()
            
            elif self.chaser == 'bbq':
                playersCollide = pygame.sprite.spritecollide(self.player4,
                                 self.characters, False)
                if len(playersCollide) > 1:
                    for player in playersCollide:
                        if player != self.player4:
                            player.kill()
                            self.player4Score += 1
                            if self.player4Score == self.winScore:
                                self.mode = 'p4Win'
                    self.initEachRound()

    def drawStart(self, screen):
        diffY = self.screenHeight/10
        
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
        
        title = self.largeFont.render('Help – Game Modes', True, (255,255,255))
        titleWidth, titleHeight = title.get_size()
        screen.blit(title, (self.screenWidth/2-titleWidth/2, 1*diffY))
        
        subtitle1 = self.boldFont.render('Chase Mode', True, (255,255,255))
        screen.blit(subtitle1, (margin, 3*diffY))
        
        text1 = self.standardFont.render(
        "If you are the 'chaser', catch your friends to earn a point! If not,",
                                            True, (255,255,255))
        screen.blit(text1, (margin, 4*diffY))
        
        text2 = self.standardFont.render(
        "then run the hell away! (The 'chaser' changes every 10 seconds)",
                                            True, (255,255,255))
        screen.blit(text2, (margin, 5*diffY))
        
        text3 = self.underlineFont.render(
        "Power ups included:",
                                            True, (255,255,255))
        screen.blit(text3, (margin, 6*diffY))
        
        text4 = self.standardFont.render(
        "                                        Boot – increases player speed",
                                            True, (255,255,255))
        screen.blit(text4, (margin, 6*diffY))
        
        text5 = self.standardFont.render(
        "                                        Snail – decreases player speed",
                                            True, (255,255,255))
        screen.blit(text5, (margin, 7*diffY))
        
        text6 = self.standardFont.render(
        "                                        Shield – gives immunity for 3 seconds",
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
        "                                        Gun – Fires a single bullet",
                                            True, (255,255,255))
        screen.blit(text8, (margin, 12*diffY))
        
        text9 = self.standardFont.render(
        "                                                    (cannot pass through walls)",
                                            True, (255,255,255))
        screen.blit(text9, (margin, 13*diffY))
        
        text10 = self.standardFont.render(
        "                                        Laser – Fires a single laser beam",
                                            True, (255,255,255))
        screen.blit(text10, (margin, 14*diffY))
        
        text11 = self.standardFont.render(
        "                                                      (able to pass through walls)",
                                            True, (255,255,255))
        screen.blit(text11, (margin, 15*diffY))
        
        text12 = self.standardFont.render(
        "                                        Shield – gives immunity for 3 seconds",
                                            True, (255,255,255))
        screen.blit(text12, (margin, 16*diffY))
        
        text13 = self.standardFont.render(
        "Press the ‘spacebar’ to go to the next page for controls",
                                            True, (255,255,255))
        text13Width, text13Height = text13.get_size()
        screen.blit(text13, (self.screenWidth/2-text13Width/2, 18*diffY))
        
    def drawHelpPage2(self, screen):
        diffY = self.screenHeight/20
        margin = 20
        
        title = self.largeFont.render('Help – Controls', True, (255,255,255))
        titleWidth, titleHeight = title.get_size()
        screen.blit(title, (self.screenWidth/2-titleWidth/2, 1*diffY))
        
        subtitle1 = self.boldFont.render('Player 1', True, (255,255,255))
        screen.blit(subtitle1, (margin, 4*diffY))
        
        text1 = self.standardFont.render("Press ‘w’ to move up", True, (255,255,255))
        screen.blit(text1, (margin, 5*diffY))
        
        text2 = self.standardFont.render("Press ‘a’ to move left", True, (255,255,255))
        screen.blit(text2, (margin, 6*diffY))
        
        text3 = self.standardFont.render("Press ‘s’ to move down", True, (255,255,255))
        screen.blit(text3, (margin, 7*diffY))
        
        text4 = self.standardFont.render("Press ‘d’ to move right", True, (255,255,255))
        screen.blit(text4, (margin, 8*diffY))
        
        text5 = self.standardFont.render("Press the ‘spacebar’ to shoot", True, (255,255,255))
        screen.blit(text5, (margin, 9*diffY))
        
        subtitle2 = self.boldFont.render('Player 2', True, (255,255,255))
        screen.blit(subtitle2, (margin, 11*diffY))
        
        text6 = self.standardFont.render(
                    "Press the ‘up’ arrow key to move up", True, (255,255,255))
        screen.blit(text6, (margin, 12*diffY))
        
        text7 = self.standardFont.render(
                    "Press the ‘left’ arrow key to move left", True, (255,255,255))
        screen.blit(text7, (margin, 13*diffY))
        
        text8 = self.standardFont.render(
                    "Press the ‘down’ arrow key to move down", True, (255,255,255))
        screen.blit(text8, (margin, 14*diffY))
        
        text9 = self.standardFont.render(
                    "Press the ‘right’ arrow key to move right", True, (255,255,255))
        screen.blit(text9, (margin, 15*diffY))
        
        
        text10 = self.standardFont.render(
                    "Press the ‘enter’ key to shoot", True, (255,255,255))
        screen.blit(text10, (margin, 16*diffY))
        
        text11 = self.standardFont.render(
        "Press ‘backspace’ to return to the main menu", True, (255,255,255))
        text11Width, text11Height = text11.get_size()
        screen.blit(text11, (self.screenWidth/2-text11Width/2, 18*diffY))
        
        
    def drawScore(self, screen):
        heightBox = self.screenHeight-self.height
        diffY = heightBox/5
        # pygame.draw.line(screen, (255,255,255), (self.screenWidth/2, 3+self.height+(heightBox/3)),
        #                  (self.screenWidth/2, self.screenHeight), 3)
        pygame.draw.rect(screen, (255,255,255), (1, 3+self.height, self.screenWidth-2,
                         heightBox-5), 5)
        # pygame.draw.line(screen, (255,255,255), (0,self.height+(heightBox/3)),
        #                  (self.screenWidth,self.height+(heightBox/3)), 3)
        
        timeLeft = self.boldFont.render("Time left: %d" %self.count, True, (255,255,255))
        timeLeftW, timeLeftH = timeLeft.get_size()
        timeLeftY = self.height + heightBox/7
        screen.blit(timeLeft, (self.screenWidth/2-timeLeftW/2, timeLeftY))
        
        name1 = self.boldFont.render("Ketchup", True, (255,255,255))
        name1W, name1H = name1.get_size()
        name1X = self.screenWidth/4 - name1W/2
        name1Y = self.height + diffY*2
        screen.blit(name1, (name1X, name1Y))
        
        name2 = self.boldFont.render("Mustard", True, (255,255,255))
        name2W, name2H = name2.get_size()
        name2X = self.screenWidth*(3/4) - name2W/2
        name2Y = self.height + diffY*2
        screen.blit(name2, (name2X, name2Y))
        
        player1ScoreSurface = self.standardFont.render(
                              "Score: %d" %(self.player1Score), 
                              True, (255,255,255))
        p1ScoreWidth = player1ScoreSurface.get_width()
        p1ScoreHeight = player1ScoreSurface.get_height()
        player2ScoreSurface = self.standardFont.render(
                              "Score: %d" %(self.player2Score), 
                              True, (255,255,255))
        p2ScoreWidth = player2ScoreSurface.get_width()
        p2ScoreHeight = player2ScoreSurface.get_height()
        p1ScoreX = self.screenWidth/4 - p1ScoreWidth/2
        p1ScoreY = self.height + diffY*3
        p2ScoreX = self.screenWidth*(3/4) - p2ScoreWidth/2
        p2ScoreY = self.height + diffY*3
        screen.blit(player1ScoreSurface, (p1ScoreX, p1ScoreY))
        screen.blit(player2ScoreSurface, (p2ScoreX, p2ScoreY))
        
        item1 = self.standardFont.render("Item: %s" %self.player1.item,
                                          True, (255,255,255))
        item1Width, item1Height = item1.get_size()
        screen.blit(item1, (self.screenWidth/4 - item1Width/2,
                    self.height + diffY*4))
                    
        item2 = self.standardFont.render("Item: %s" %self.player2.item,
                                          True, (255,255,255))
        item2Width, item2Height = item2.get_size()
        screen.blit(item2, (self.screenWidth*(3/4) - item2Width/2,
                    self.height + diffY*4))
        
        if self.chaser == 'ketchup':
            screen.blit(self.devilImage, (self.screenWidth/4 - self.devilImageW/2,
                        self.height + 15))
            screen.blit(self.scaredImage, (self.screenWidth*(3/4) - self.scaredImageW/2,
                        self.height + 15))
        elif self.chaser == 'mustard':
            screen.blit(self.devilImage, (self.screenWidth*(3/4) - self.devilImageW/2,
                        self.height + 15))
            screen.blit(self.scaredImage, (self.screenWidth/4 - self.scaredImageW/2,
                        self.height + 15))
        
    def drawP1Win(self, screen):
        message = self.standardFont.render("Ketchup Won!", True, (255,255,255))
        screen.blit(message, (self.width/2, self.screenHeight/2))
        
    def drawP2Win(self, screen):
        message = self.standardFont.render("Mustard Won!", True, (255,255,255))
        screen.blit(message, (self.width/2, self.screenHeight/2))
    
    def drawP3Win(self, screen):
        message = self.standardFont.render("Mayonnaise (computer) Won!", True, (255,255,255))
        screen.blit(message, (self.width/2, self.screenHeight/2))
        
    def redrawAll(self, screen):
        if self.mode == 'chase' or self.mode == 'shoot':
            self.wallGroup.draw(screen)
            self.bulletGroup.draw(screen)
            self.laserBeamGroup.draw(screen)
            self.powerUpsGroup.draw(screen)
            self.characters.draw(screen)
            self.drawScore(screen)
        
        elif self.mode == 'start':
            self.drawStart(screen)
            
        elif self.mode == 'helpP1':
            self.drawHelpPage1(screen)
            
        elif self.mode == 'helpP2':
            self.drawHelpPage2(screen)
            
        elif self.mode == 'p1Win':
            self.drawP1Win(screen)
            
        elif self.mode == 'p2Win':
            self.drawP2Win(screen)
        
        elif self.mode == 'p3Win':
            self.drawP3Win(screen)

#creating and running the game
ketchUp = myProject()
ketchUp.run()