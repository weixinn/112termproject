class ComputerChase(GameCharacter):
    def __init__(self, x, y, image, speed):
        super().__init__(x, y, image, speed)
        
        self.targetPos = (0,9)
        self.newRoute()
        self.updateNextPos()
    
    def updateNextPos(self):
        move = self.route[0]
        dCol, dRow = move
        curRow, curCol = self.pos
        newRow = curRow + dRow
        newCol = curCol + dCol
        self.nextPos = (newRow, newCol)
    
    def newRoute(self):
        self.route = findRoute(ketchUp.wallMap, self.pos, self.targetPos)
    
    def move(self, speed):
        move = self.route[0]
        dCol, dRow = move
        dX = dCol*speed
        dY = dRow*speed
        self.x += dX
        self.y += dY
        self.updatePos()
        self.updateRect()
        # self.updateNextPos()
        
        wall = pygame.sprite.spritecollideany(self, ketchUp.wallGroup)
        if wall != None:
            if move == (0,-1): #up
                playerTopEdge = self.y - self.height/2
                wallBotEdge = wall.y + wall.height/2
                overlap = wallBotEdge - playerTopEdge
                self.y += overlap
                
            elif move == (0,1): #down
                playerBotEdge = self.y + self.height/2
                wallTopEdge = wall.y - wall.height/2
                overlap = playerBotEdge - wallTopEdge
                self.y -= overlap
                
            elif move == (-1,0): #left
                playerLeftEdge = self.x - self.width/2
                wallRightEdge = wall.x + wall.width/2
                overlap = wallRightEdge - playerLeftEdge
                self.x += overlap
                
            elif move == (1,0): #right
                playerRightEdge = self.x + self.width/2
                wallLeftEdge = wall.x - wall.width/2
                overlap = playerRightEdge - wallLeftEdge
                self.x -= overlap
            
            self.updatePos()
            self.updateRect()
            # self.updateNextPos()