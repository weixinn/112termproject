import random, copy

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
    
        def solve(board, row, col):
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
                        solution = solve(board, newRow, newCol)
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

def countSpace(board):
    count = 0
    for row in range (len(board)):
        for col in range (len(board[0])):
            if board[row][col] == 0:
                count +=1
    return count
    
# finds any random route from the current position to a target position
# returns a set of directions in terms of tuples
def findRoute(board, pos, targetPos):
    row, col = pos
    targetRow, targetCol = targetPos
    seen = set()
    stepsTaken = []
    directions = [(0,-1),(0,1),(-1,0),(1,0)]
    maxRow = len(board)
    maxCol = len(board[0])
    
    def solve(board, row, col, targetRow, targetCol):
        if (row,col) in seen:
            return None
        
        elif row == targetRow and col == targetCol:
            return stepsTaken
            
        else:
            seen.add((row,col))
            for move in directions:
                dCol, dRow = move
                newRow = row + dRow
                newCol = col + dCol
                
                if newRow == maxRow or newCol == maxCol or newRow<0 or newCol<0:
                    continue
                
                if board[newRow][newCol] == 0:
                    stepsTaken.append(move)
                    solution = solve(board, newRow, newCol, targetRow, targetCol)
                    if solution != None:
                        return solution
                    stepsTaken.pop()
            return None
    
    result = solve(board, row, col, targetRow, targetCol)
    return result
    
def convertRoute(route, x, y, wallSize):
    result = []
    for move in route:
        dCol, dRow = move
        dx = dCol*wallSize
        dy = dRow*wallSize
        x += dx
        y += dy
        result.append((x,y))
    return result

# gets position on board based on x and y
def getPosition(x,y,wallSize):
    x -= wallSize
    y -= wallSize
    row = int(y//wallSize)
    col = int(x//wallSize)
    return (row,col)

# for me to read more easily
def printRoute(route):
    newRoute = []
    for move in route:
        if move == (0,-1):
            newRoute.append('up')
        elif move == (0,1):
            newRoute.append('down')
        elif move == (-1,0):
            newRoute.append('left')
        elif move == (1,0):
            newRoute.append('right')
    print (newRoute)

def getRectForPos(pos, wallSize):
    row, col = pos
    x = wallSize*(col+1)
    y = wallSize*(row+1)
    width, height = wallSize, wallSize
    return (x,y,width,height)
    
def getCoordFromPos(pos, wallSize):
    row, col = pos
    x = (col+1.5)*wallSize
    y = (row+1.5)*wallSize
    return (x,y)
    
def convertRoute(route, x, y, wallSize):
    result = []
    for move in route:
        pos = getPosition(x,y,wallSize)
        x, y = getCoordFromPos(pos, wallSize)
        dCol, dRow = move
        dx = dCol*wallSize
        dy = dRow*wallSize
        x += dx
        y += dy
        result.append((x,y))
    return result

# # centre of the player must be within the innerRect of the pos
# # midX and midY are the centre of the pos
# def isWithinPos(curX, curY, pos, wallSize, playerH, playerW):
#     rect = getRectForPos(pos, wallSize)
#     x, y, w, h = rect
#     midX = x + w/2
#     midY = y + h/2
#     maxHeightDiff = (0.5*wallSize) - (0.5*playerH)
#     maxWidthDiff = (0.5*wallSize) - (0.5*playerW)
#     if curX >= midX+maxWidthDiff or curX <= midX-maxWidthDiff:
#         return False
#     if curY >= midY+maxHeightDiff or curY <= midY-maxHeightDiff:
#         return False
#     return True