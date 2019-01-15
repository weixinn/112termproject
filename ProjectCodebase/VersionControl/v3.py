import pygame
import pygamegame #the framework
import random, copy

# from last try, added variable board sizes
'''
things to add:
customisable board

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
def isLegalBoard(board):
    if board == []:
        return False
        
    maxRow, maxCol = len(board)-1, len(board[0])-1
    directions = [(0,-1),(0,1),(-1,0),(1,0)] # up, down, left, right
    # dictionary of each position on the board and whether or not it has a valid way out
    visited = {}
    
    # for a given board and row & col, check that there is always a way out
    # of any blank spots so there are no isolated "pockets" that cannot be accessed
    def pathExists(board, row, col):
        seen = set()
    
        def solve(board, row, col, depth = 0):
            if (row,col) in visited:
                solution = visited[(row,col)]
                return solution
                
            elif (row,col) in seen:
                return False
            
            elif row == 0 or col == 0 or row==maxRow or col == maxCol:
                return True
                
            else:
                seen.add((row,col))
                for move in directions:
                    dCol, dRow = move
                    newRow = row + dRow
                    newCol = col + dCol
                    
                    if board[newRow][newCol] == 0:
                        solution = solve(board, newRow, newCol, depth +1)
                        if solution == True:
                            return solution
                return False
        
        result = solve(board, row, col)
        visited[(row,col)] = result
        return result
        
    for row in range (len(board)):
        for col in range (len(board[0])):
            if board[row][col] == 0:
                if pathExists(board, row, col) != True:
                    return False
    return True

def generateBoard(largeRow, largeCol):
    # row and col refer to the space within the '0' border
    row = largeRow - 2
    col = largeCol - 2
    percentageWalls = 0.35
    totalSpace = row*col
    totalWalls = int(percentageWalls*totalSpace)
    totalEmpty = totalSpace - totalWalls
    
    totalBlocks = []
    for i in range (totalEmpty):
        totalBlocks.append(0)
    for j in range (totalWalls):
        totalBlocks.append(1)
            
    board = []
    
    def generate(numRow,numCol):
        newBoard = [[None for i in range (numCol)] for i in range (numRow)]
        buildFrom = copy.deepcopy(totalBlocks)
        for row in range (numRow):
            for col in range (numCol):
                index = random.randint(0, len(buildFrom)-1)
                newBoard[row][col] = buildFrom[index]
        return newBoard
    
    # generates a legal "inner" board
    while isLegalBoard(board) != True:
        board = generate(row,col)
        
    # adds the '0' border
    for row in board:
        row.insert(0, 0)
        row.append(0)
    newRow = [0 for i in range (len(board[0]))]
    board.insert(0, newRow)
    board.append(newRow)
    
    return board
    
print (generateBoard(10,10))

#GAME NAME IS KETCHUP. BECAUSE CATCH UP. GET IT?? :D

class GameCharacter(pygame.sprite.Sprite):
    
    def __init__(self, x, y, image):
        super().__init__()
        
        # x,y is the center point of the character image
        self.x, self.y = x, y
        self.image = image
        self.width, self.height = image.get_size()
        
        self.updateRect()
        
    # for collision detection
    def updateRect(self):
        w, h = self.width, self.height
        self.rect = pygame.Rect(self.x - w / 2, self.y - h / 2, w, h)
        
    def update(self, keysDown):
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
        
        # this chunk is only temporary just so the game can function for now
        self.time = 0
        self.count = 0
        self.mode = 'ketchup'
        print (self.mode)
        
        self.time = 0
        self.count = 0
        self.mode = 'ketchup'
        self.boardSizes = ['small', 'medium', 'large']
        self.boardSize = self.boardSizes[0]
        
        # DON'T BE CONFUSED!! actual board rows and cols is self.numRows and
        # self.numCols - 2!!
        if self.boardSize == self.boardSizes[0]:
            self.numRows = 12
            self.numCols = 12
        elif self.boardSize == self.boardSizes[1]:
            self.numRows = 17
            self.numCols = 17
        elif self.boardSize == self.boardSizes[2]:
            self.numRows = 22
            self.numCols = 22
        
        self.wallSize = int(self.width/self.numCols)
        self.wallGroup = pygame.sprite.Group()
        self.wallMap = generateBoard(self.numRows-2, self.numCols-2)
        
        # self.wallMap = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
        #                 [0, 1, 0, 1, 1, 0, 1, 0, 1, 0], 
        #                 [0, 1, 0, 1, 1, 0, 1, 0, 0, 0], 
        #                 [0, 1, 0, 0, 0, 0, 0, 0, 1, 0], 
        #                 [0, 1, 1, 0, 1, 0, 1, 0, 0, 0], 
        #                 [0, 1, 1, 0, 1, 0, 0, 1, 1, 0], 
        #                 [0, 1, 1, 0, 1, 1, 0, 0, 0, 0], 
        #                 [0, 0, 0, 0, 1, 0, 0, 1, 0, 0], 
        #                 [0, 1, 1, 0, 1, 0, 1, 1, 1, 0], 
        #                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
        
        self.generateWalls()
        
        self.speed = 0.2*self.wallSize
        
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
        
        # player1 starts in top left corner
        self.player1X = self.player1W/2 + self.wallWidth + 1
        self.player1Y = self.player1H/2 + self.wallHeight + 1
        
        # player2 starts in the bottom right corner
        self.player2X = self.width - self.player2W/2 - self.wallWidth - 1
        self.player2Y = self.height - self.player2H/2 - self.wallHeight - 1
        
        # initialises the two characters
        self.characters = pygame.sprite.Group()
        self.player1 = GameCharacter(self.player1X, self.player1Y, self.player1Image)
        self.characters.add(self.player1)
        self.player2 = GameCharacter(self.player2X, self.player2Y, self.player2Image)
        self.characters.add(self.player2)
    
    
        
    def generateWalls(self):
        self.wallSize
        self.wallImage = pygame.transform.scale(pygame.image.load(
                            'images/burger.png').convert_alpha(), (self.wallSize,self.wallSize))
        self.wallWidth, self.wallHeight = self.wallSize, self.wallSize
        
        # generate border
        for i in range (0,self.numRows):
            borderBlock1 = Wall(0, i, self.wallImage, self.wallWidth, self.wallHeight)
            borderBlock2 = Wall(self.numRows-1, i, self.wallImage, self.wallWidth, self.wallHeight)
            self.wallGroup.add(borderBlock1)
            self.wallGroup.add(borderBlock2)
        for j in range (1,self.numRows-1):
            borderBlock3 = Wall(j, 0, self.wallImage, self.wallWidth, self.wallHeight)
            borderBlock4 = Wall(j, self.numRows-1, self.wallImage, self.wallWidth, self.wallHeight)
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