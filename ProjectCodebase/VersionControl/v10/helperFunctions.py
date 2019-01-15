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
    
    
def findNeighbours(pos):
    row, col = pos
    top = (row-1, col)
    bot = (row+1, col)
    left = (row, col-1)
    right = (row, col+1)
    return [top, bot, left, right]

def withinBoard(pos, maxRow, maxCol):
    row, col = pos
    if row<0 or row>maxRow:
        return False
    if col<0 or col>maxCol:
        return False
    return True

def isNeighbour(row1, col1, row2, col2):
    rowDiff = abs(row1-row2)
    colDiff = abs(col1-col2)
    if rowDiff == 0 and colDiff == 1:
        return True
    elif rowDiff == 1 and colDiff == 0:
        return True
    return False

def getDirection(row1, col1, row2, col2):
    rowDiff = row2 - row1
    colDiff = col2 - col1
    return (colDiff, rowDiff)

def convertRouteFromAStar(route):
    result = []
    lastItem = route.pop(0)
    for item in route:
        lastRow, lastCol, lastDepth = lastItem
        row, col, depth = item
        dir = getDirection(lastRow, lastCol, row, col)
        result.append(dir)
        lastItem = item
    return result

# https://en.wikipedia.org/wiki/Pathfinding
def aStarFindRoute(board, startPos, endPos):
    startRow, startCol = startPos
    endRow, endCol = endPos
    queue = [(startRow, startCol, 0)]
    queueNoWeight = [(startRow,startCol)]
    maxRow = len(board) - 1
    maxCol = len(board[0]) - 1
    
    for item in queue:
        row, col, depth = item
        
        if row == endRow and col == endCol:
            endDepth = depth
            break
        
        pos = (row, col)
        neighbours = findNeighbours(pos)
        for neighbour in neighbours:
            row, col = neighbour
            
            if withinBoard(neighbour, maxRow, maxCol) == False:
                continue
            
            elif board[row][col] == 1:
                continue
              
            else:
                found = False
                tempDepth = depth+1
                while tempDepth >= 0:
                    if (row, col, tempDepth) in queue:
                        found = True
                        tempDepth = -1
                    tempDepth -= 1
                if found == True:
                    continue
            
            queue.append((row,col,depth+1))
            
    index = queue.index((endRow, endCol, endDepth))
    queue = queue[:index+1]
    queue = queue[::-1]
    lastItem = queue.pop(0)
    routePositions = [lastItem]
    for item in queue:
        lastRow, lastCol, lastDepth = lastItem
        row, col, depth = item
        if depth == lastDepth-1 and isNeighbour(lastRow, lastCol, row, col):
            routePositions.append(item)
            lastItem = item
    
    routePositions = routePositions[::-1]
    
    result = convertRouteFromAStar(routePositions)
    
    return result


# same as a* find route but with an additional limitation such that the computer
# will not take a step that will bring it closer to the chaser
def forRunAStarFindRoute(board, startPos, endPos, chaserPos, minDist):
    startRow, startCol = startPos
    endRow, endCol = endPos
    queue = [(startRow, startCol, 0)]
    queueNoWeight = [(startRow,startCol)]
    maxRow = len(board) - 1
    maxCol = len(board[0]) - 1
    foundRoute = False
    
    for item in queue:
        row, col, depth = item
        
        if row == endRow and col == endCol:
            endDepth = depth
            foundRoute = True
            break
        
        pos = (row, col)
        neighbours = findNeighbours(pos)
        for neighbour in neighbours:
            row, col = neighbour
            
            if withinBoard(neighbour, maxRow, maxCol) == False:
                continue
            
            elif board[row][col] == 1:
                continue
              
            elif getDistance(chaserPos, neighbour) < minDist:
                continue
            
            else:
                found = False
                tempDepth = depth+1
                while tempDepth >= 0:
                    if (row, col, tempDepth) in queue:
                        found = True
                        tempDepth = -1
                    tempDepth -= 1
                if found == True:
                    continue
            
            queue.append((row,col,depth+1))
       
    if foundRoute == True:
        index = queue.index((endRow, endCol, endDepth))
        queue = queue[:index+1]
        queue = queue[::-1]
        lastItem = queue.pop(0)
        routePositions = [lastItem]
        
        for item in queue:
            lastRow, lastCol, lastDepth = lastItem
            row, col, depth = item
            if depth == lastDepth-1 and isNeighbour(lastRow, lastCol, row, col):
                routePositions.append(item)
                lastItem = item
        
        routePositions = routePositions[::-1]
        result = convertRouteFromAStar(routePositions)
        return result
    
    else:
        return None
                    
    
# converts route from directions to a set of x,y coords that the computer can move to
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

def getDistance(pos1,pos2):
    row1, col1 = pos1
    row2, col2 = pos2
    rowDiff = abs(row1 - row2)
    colDiff = abs(col1 - col2)
    return rowDiff + colDiff

# returns which quadrant the coord is in
def getQuadrant(pos, width, height):
    x, y = pos
    midX = width/2
    midY = height/2
    if x>midX and y<midY:
        return 1
    elif x<midX and y<midY:
        return 2
    elif x<midX and y>midY:
        return 3
    else:
        return 4

def oppQuadrant(quadrant):
    if quadrant == 1:
        return 3
    elif quadrant == 2:
        return 4
    elif quadrant == 3:
        return 1
    else:
        return 2

def getCornerPos(quadrant, maxRow, maxCol):
    if quadrant == 1:
        row = 0
        col = maxCol
        return (row,col)
    elif quadrant == 2:
        row = 0
        col = 0
        return (row,col)
    elif quadrant == 3:
        row = maxRow
        col = 0
        return (row,col)
    else:
        row = maxRow
        col = maxCol
        return (row,col)
    
# returns any random spot that is a certain number of steps away
def findPosNumStepsAway(board, pos, numSteps):
    startRow, startCol = pos
    seen = set()
    directions = [(0,-1),(0,1),(-1,0),(1,0)]
    maxRow, maxCol = len(board)-1, len(board[0])-1
    
    def solve(curRow = startRow, curCol = startCol, depth=0):
        curPos = (curRow, curCol)
        
        if curPos in seen:
            return None

        if depth == numSteps:
            return curPos
        
        else:
            seen.add(curPos)
            for move in directions:
                dCol, dRow = move
                newRow = curRow + dRow
                newCol = curCol + dCol
                
                if newRow > maxRow or newRow < 0:
                    continue
                if newCol > maxCol or newCol < 0:
                    continue
                
                if board[newRow][newCol] == 0:
                    solution = solve(newRow, newCol, depth+1)
                    if solution != None:
                        return solution
            
            return None
    
    return solve()