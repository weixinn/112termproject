import pygame
import pygamegame #the framework


'''

This version treats walls as a sprite. but because the collision is not working
properly so I'm gonna change walls to just be plain bounds and objects.

things to add:

variable board size (add into the generate board function)
random board generator (use islegal board, set number of walls e.g.30% of total
                        board size)
customisable board
E
power ups:
1. increase speed
2. long range weapons, guns, which destruct when crash into walls, and lasers
        that can go through walls
3. turn you invincible

gamemode:
1. pure chasing
2. using weapons, so basic weapon is a knife OR maybe a slingshot the bullet
    does not travel far
    
settings:
1. how many points to win e.g. 3,5,7

'''

#GAME NAME IS KETCHUP. BECAUSE CATCH UP. GET IT?? :D
#Things to include only if have time:
#   1. masks ==> pixel perfect collisions
#   2. running animation *alrdy have images
#   3. Online multiplayer, four characters *alrdy have images

class GameCharacter(pygame.sprite.Sprite):
    
    def __init__(self, x, y, image):
        super().__init__()
        
        # x,y is the center point of the character image
        self.x, self.y = x, y
        self.image = image
        self.width, self.height = image.get_size()
        
        self.updateRect()
        
    # for collision detection (can try putting in masks later)
    def updateRect(self):
        w, h = self.width, self.height
        self.rect = pygame.Rect(self.x - w / 2, self.y - h / 2, w, h)
        
    def update(self, keysDown):
        
        #never allow it to go offscreen no wraparound because difficult to get rect right
        # if self.x >= (ketchUp.width - self.width/2):
        #     self.x = ketchUp.width - self.width/2
        # elif self.x <= self.width/2:
        #     self.x = self.width/2
        # if self.y >= (ketchUp.height - self.height/2):
        #     self.y = ketchUp.height - self.height/2
        # elif self.y <= self.height/2:
        #     self.y = self.height/2
        
        self.updateRect()
        
class Wall(pygame.sprite.Sprite):
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

class myProject(pygamegame.PygameGame):
    # DON'T CHANGE __INIT__ BECAUSE IT HAS ALREADY BEEN SET UP IN PYGAMEGAME
    # TO HANDLE STUFF LIKE WINDOW WIDTH AND HEIGHT. JUST USE A SECOND SELF
    # DEFINED INIT
    
    def init(self):
        
        self.time = 0
        self.count = 0
        self.mode = 'ketchup'
        print (self.mode)
        
        self.numRows = 12
        self.numCols = 12
        self.speed = 10
        
        self.wallGroup = pygame.sprite.Group()
        self.wallMap = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                        [0, 1, 0, 1, 1, 0, 1, 0, 1, 0], 
                        [0, 1, 0, 1, 1, 0, 1, 0, 0, 0], 
                        [0, 1, 0, 0, 0, 0, 0, 0, 1, 0], 
                        [0, 1, 1, 0, 1, 0, 1, 0, 0, 0], 
                        [0, 1, 1, 0, 1, 0, 0, 1, 1, 0], 
                        [0, 1, 1, 0, 1, 1, 0, 0, 0, 0], 
                        [0, 0, 0, 0, 1, 0, 0, 1, 0, 0], 
                        [0, 1, 1, 0, 1, 0, 1, 1, 1, 0], 
                        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
        
        self.generateWalls()
        
        # initialises images, scaling them to the pixels you want,
        # and calculates their position based on the size
        self.player1Image = pygame.transform.scale(pygame.image.load(
                            'images/ketchup.png').convert_alpha(), (30,40))
        self.player1W, self.player1H = self.player1Image.get_size()
        self.player2Image = pygame.transform.scale(pygame.image.load(
                            'images/mustard.png').convert_alpha(), (30,40))
        self.player2W, self.player2H = self.player2Image.get_size()
        
        # player1 starts in top left corner
        self.player1X = self.player1W/2 + self.wallWidth
        self.player1Y = self.player1H/2 + self.wallHeight
        
        # player2 starts in the bottom right corner
        self.player2X = self.width - self.player2W/2 - self.wallWidth
        self.player2Y = self.height - self.player2H/2 - self.wallHeight
        
        # initialises the two characters
        self.characters = pygame.sprite.Group()
        self.player1 = GameCharacter(self.player1X, self.player1Y, self.player1Image)
        self.characters.add(self.player1)
        self.player2 = GameCharacter(self.player2X, self.player2Y, self.player2Image)
        self.characters.add(self.player2)
        
    def generateWalls(self):
        self.wallImage = pygame.transform.scale(pygame.image.load(
                            'images/burger.png').convert_alpha(), (50,50))
        self.wallWidth, self.wallHeight = self.wallImage.get_size()
        
        # generate border
        for i in range (0,12):
            borderBlock1 = Wall(0, i, self.wallImage, self.wallWidth, self.wallHeight)
            borderBlock2 = Wall(11, i, self.wallImage, self.wallWidth, self.wallHeight)
            self.wallGroup.add(borderBlock1)
            self.wallGroup.add(borderBlock2)
        for j in range (1,11):
            borderBlock3 = Wall(j, 0, self.wallImage, self.wallWidth, self.wallHeight)
            borderBlock4 = Wall(j, 11, self.wallImage, self.wallWidth, self.wallHeight)
            self.wallGroup.add(borderBlock3)
            self.wallGroup.add(borderBlock4)
        
        for row in range (len(self.wallMap)):
            for col in range (len(self.wallMap[0])):
                if self.wallMap[row][col] != 0:
                    block = Wall(row+1, col+1, self.wallImage, self.wallWidth, self.wallHeight)
                    self.wallGroup.add(block)
    
    def keyPressed(self, keyCode, modifier):
        if keyCode == 114:
            self.init()
    
    def timerFired(self, dt):
        self.time += 1
        
        if self.time%50 == 0:
            self.count += 1
            if self.count > 10:
                self.count = 0
                if self.mode == 'ketchup':
                    self.mode = 'mustard'
                else: 
                    self.mode = 'ketchup'
                print (self.mode)
        
        
        #controls for player 1
        if self.isKeyPressed(pygame.K_a):
            self.player1.x -= self.speed
            self.player1.update(self.isKeyPressed)
            wall = pygame.sprite.spritecollideany(self.player1, self.wallGroup)
            if wall != None:
                playerLeftEdge = self.player1.x - self.player1.width/2
                wallRightEdge = wall.x + wall.width/2
                overlap = wallRightEdge - playerLeftEdge
                self.player1.x += overlap
                self.player1.update(self.isKeyPressed)
                
        if self.isKeyPressed(pygame.K_d):
            self.player1.x += self.speed
            self.player1.update(self.isKeyPressed)
            wall = pygame.sprite.spritecollideany(self.player1, self.wallGroup)
            if wall != None:
                playerRightEdge = self.player1.x + self.player1.width/2
                wallLeftEdge = wall.x - wall.width/2
                overlap = playerRightEdge - wallLeftEdge
                self.player1.x -= overlap
                self.player1.update(self.isKeyPressed)
            
        if self.isKeyPressed(pygame.K_w):
            self.player1.y -= self.speed
            self.player1.update(self.isKeyPressed)
            wall = pygame.sprite.spritecollideany(self.player1, self.wallGroup)
            if wall != None:
                playerTopEdge = self.player1.y - self.player1.height/2
                wallBotEdge = wall.y + wall.height/2
                overlap = wallBotEdge - playerTopEdge
                self.player1.y += overlap
                self.player1.update(self.isKeyPressed)
                
        if self.isKeyPressed(pygame.K_s):
            self.player1.y += self.speed
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
            self.player2.x -= self.speed
            self.player2.update(self.isKeyPressed)
            wall = pygame.sprite.spritecollideany(self.player2, self.wallGroup)
            if wall != None:
                playerLeftEdge = self.player2.x - self.player2.width/2
                wallRightEdge = wall.x + wall.width/2
                overlap = wallRightEdge - playerLeftEdge
                self.player2.x += overlap
                self.player2.update(self.isKeyPressed)
            
        if self.isKeyPressed(pygame.K_RIGHT):
            self.player2.x += self.speed
            self.player2.update(self.isKeyPressed)
            wall = pygame.sprite.spritecollideany(self.player2, self.wallGroup)
            if wall != None:
                playerRightEdge = self.player2.x + self.player2.width/2
                wallLeftEdge = wall.x - wall.width/2
                overlap = playerRightEdge - wallLeftEdge
                self.player2.x -= overlap
                self.player2.update(self.isKeyPressed)
            
        if self.isKeyPressed(pygame.K_UP):
            self.player2.y -= self.speed
            self.player2.update(self.isKeyPressed)
            wall = pygame.sprite.spritecollideany(self.player2, self.wallGroup)
            if wall != None:
                playerTopEdge = self.player2.y - self.player2.height/2
                wallBotEdge = wall.y + wall.height/2
                overlap = wallBotEdge - playerTopEdge
                self.player2.y += overlap
                self.player2.update(self.isKeyPressed)
            
        if self.isKeyPressed(pygame.K_DOWN):
            self.player2.y += self.speed
            self.player2.update(self.isKeyPressed)
            wall = pygame.sprite.spritecollideany(self.player2, self.wallGroup)
            if wall != None:
                playerBotEdge = self.player2.y + self.player2.height/2
                wallTopEdge = wall.y - wall.height/2
                overlap = playerBotEdge - wallTopEdge
                self.player2.y -= overlap
                self.player2.update(self.isKeyPressed)
        
        # this is to check between two sprites
        if pygame.sprite.collide_rect(self.player1, self.player2):
            if self.mode == 'ketchup':
                self.player2.kill()
            else: self.player1.kill()
        
    def redrawAll(self, screen):
        self.characters.draw(screen)
        self.wallGroup.draw(screen)

#creating and running the game
ketchUp = myProject()
ketchUp.run()