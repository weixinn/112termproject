import pygame
import pygamegame #the framework

#GAME NAME IS KETCHUP. BECAUSE CATCH UP. GET IT?? :D
#Things to include only if have time:
#   1. masks ==> pixel perfect collisions
#   2. running animation *alrdy have images
#   3. Online multiplayer, four characters *alrdy have images

class GameCharacter(pygame.sprite.Sprite):
    
    def __init__(self, x, y, image, border):
        super().__init__()
        
        # x,y is the center point of the character image
        self.x, self.y = x, y
        self.speed = 10
        self.border = border
        self.image = image
        self.width, self.height = image.get_size()
        
        self.updateRect()
        
    # for collision detection (can try putting in masks later)
    def updateRect(self):
        w, h = self.width, self.height
        self.rect = pygame.Rect(self.x - w / 2, self.y - h / 2, w, h)
        
    def update(self, keysDown):
        
        #!!!need to put in collision with walls
        
        #never allow it to go offscreen no wraparound because difficult to get rect right
        if self.x >= (ketchUp.width - self.width/2 - self.border):
            self.x = ketchUp.width - self.width/2 - self.border
        elif self.x <= self.width/2 + self.border:
            self.x = self.width/2 + self.border
        if self.y >= (ketchUp.height - self.height/2 - self.border):
            self.y = ketchUp.height - self.height/2 - self.border
        elif self.y <= self.height/2 + self.border:
            self.y = self.height/2 + self.border
        
        self.updateRect()
        
class Player1Character(GameCharacter):
    def update(self, keysDown):
        
        if keysDown(pygame.K_a):
            self.x -= self.speed
        if keysDown(pygame.K_d):
            self.x += self.speed
        if keysDown(pygame.K_w):
            self.y -= self.speed
        if keysDown(pygame.K_s):
            self.y += self.speed
        
        super().update(keysDown)

class Player2Character(GameCharacter):
    def update(self, keysDown):
            
        if keysDown(pygame.K_LEFT):
            self.x -= self.speed
        if keysDown(pygame.K_RIGHT):
            self.x += self.speed
        if keysDown(pygame.K_UP):
            self.y -= self.speed
        if keysDown(pygame.K_DOWN):
            self.y += self.speed
        
        super().update(keysDown)
        
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
        
        self.numRows = 12
        self.numCols = 12
        
        # initialises images, scaling them to the pixels you want,
        # and calculates their position based on the size
        self.player1Image = pygame.transform.scale(pygame.image.load(
                            'images/ketchup.png').convert_alpha(), (24,48))
        self.player1W, self.player1H = self.player1Image.get_size()
        self.player2Image = pygame.transform.scale(pygame.image.load(
                            'images/mustard.png').convert_alpha(), (24,48))
        self.player2W, self.player2H = self.player2Image.get_size()
        self.border = 10
        
        #player1 starts in top left corner
        self.player1X = self.player1W/2 + self.border
        self.player1Y = self.player1H/2 + self.border
        
        # player2 starts in the bottom right corner
        self.player2X = self.width - self.player2W/2 - self.border
        self.player2Y = self.height - self.player2H/2 - self.border
        
        self.characters = pygame.sprite.Group()
        self.player1Group = pygame.sprite.Group()
        self.player2Group = pygame.sprite.Group()
        # initialises the two characters
        self.player1 = Player1Character(self.player1X, self.player1Y, self.player1Image,
                                        self.border)
        self.characters.add(self.player1)
        self.player1Group.add(self.player1)
        self.player2 = Player2Character(self.player2X, self.player2Y, self.player2Image,
                                        self.border)
        self.characters.add(self.player2)
        self.player2Group.add(self.player2)
        
        self.wallGroup = pygame.sprite.Group()
        self.wallMap = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                        [0, 1, 0, 1, 1, 0, 1, 0, 1, 0], 
                        [0, 1, 0, 1, 1, 0, 1, 0, 0, 0], 
                        [0, 1, 0, 0, 0, 0, 0, 0, 1, 0], 
                        [0, 1, 0, 0, 1, 0, 1, 0, 0, 0], 
                        [0, 1, 1, 0, 1, 0, 0, 1, 1, 0], 
                        [0, 1, 1, 0, 1, 1, 0, 0, 0, 0], 
                        [0, 0, 0, 0, 1, 0, 0, 1, 0, 0], 
                        [1, 1, 1, 0, 1, 0, 0, 1, 0, 0], 
                        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
        
        self.generateWalls()
        
    def generateWalls(self):
        self.wallImage = pygame.transform.scale(pygame.image.load(
                            'images/burger.png').convert_alpha(), (50,50))
        self.wallWidth, self.wallHeight = self.wallImage.get_size()
        
        # generate border
        for i in range (0,12):
            borderBlock1 = Wall(0, i, self.wallImage, self.wallWidth, self.wallHeight)
            borderBlock2 = Wall(11, i, self.wallImage, self.wallWidth, self.wallHeight)
            print (borderBlock1.x, borderBlock1.y)
            print (borderBlock2.x, borderBlock2.y)
            self.wallGroup.add(borderBlock1)
            self.wallGroup.add(borderBlock2)
        for j in range (1,11):
            borderBlock3 = Wall(j, 0, self.wallImage, self.wallWidth, self.wallHeight)
            borderBlock4 = Wall(j, 11, self.wallImage, self.wallWidth, self.wallHeight)
            print (borderBlock3.x, borderBlock3.y)
            print (borderBlock4.x, borderBlock4.y)
            self.wallGroup.add(borderBlock3)
            self.wallGroup.add(borderBlock4)
        
        for row in range (len(self.wallMap)):
            for col in range (len(self.wallMap[0])):
                if self.wallMap[row][col] != 0:
                    block = Wall(row+1, col+1, self.wallImage, self.wallWidth, self.wallHeight)
                    self.wallGroup.add(block)
        
    def drawBorder(self, screen):
        pygame.draw.rect(screen, (255,0,0), (0,0,self.width,self.border))
        pygame.draw.rect(screen, (255,0,0), (0,0,self.border,self.height))
        pygame.draw.rect(screen, (255,0,0), (self.width-self.border,0,
                                                 self.border, self.height))
        pygame.draw.rect(screen, (255,0,0), (0,self.height-self.border,
                                                 self.width, self.border))
    
    def drawBoardBG(self, screen):
        pass
    
    def timerFired(self, dt):
        self.characters.update(self.isKeyPressed)
        
        # this is to check between two groups. it is destructive but also returns a dict
        pygame.sprite.groupcollide(self.player1Group, self.player2Group, False, True)
        
        # this is to check between two sprites
        # if pygame.sprite.collide_rect(self.player1, self.player2):
        #     print ('Collided!!')
        
    def redrawAll(self, screen):
        self.characters.draw(screen)
        self.wallGroup.draw(screen)
        # self.drawBorder(screen)

#creating and running the game
ketchUp = myProject()
ketchUp.run()