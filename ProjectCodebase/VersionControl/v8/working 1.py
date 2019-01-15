def getDistance(pos1,pos2):
    row1, col1 = pos1
    row2, col2 = pos2
    rowDiff = abs(row1 - row2)
    colDiff = abs(col1 - col2)
    return rowDiff + colDiff

# returns any random spot that is a certain number of steps away
def findPosNumStepsAway(board, pos, numSteps):
    startRow, startCol = pos
    seen = set()
    directions = [(0,-1),(0,1),(-1,0),(1,0)]
    maxRow, maxCol = len(board)-1, len(board[0])-1
    
    def solve(curRow = startRow, curCol = startCol, depth=0):
        curPos = (curRow, curCol)
        
        if curRow > maxRow or curRow < 0:
            return None
        if curCol > maxCol or curCol < 0:
            return None
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
                
                if board[newRow][newCol] == 0:
                    solution = solve(newRow, newCol, depth+1)
                    if solution != None:
                        return solution
            
            return None
    
    return solve()
    
# same as a* find route but with an additional limitation such that the computer
# will not take a step that will bring it closer to the chaser
def forRunAStarFindRoute(board, startPos, endPos, chaserPos, minDist):
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

board = [[0, 0, 0, 0, 0, 0, 0, 0], 
         [0, 0, 0, 0, 0, 0, 1, 0], 
         [0, 0, 0, 0, 0, 1, 0, 0], 
         [0, 0, 0, 1, 1, 0, 0, 0], 
         [0, 1, 1, 0, 0, 0, 0, 0], 
         [0, 0, 1, 0, 1, 0, 1, 0], 
         [0, 0, 0, 0, 0, 0, 1, 0], 
         [0, 0, 0, 0, 0, 0, 0, 0]]
    
pos = (7,0)
numSteps = len(board)

print (findPosNumStepsAway(board,pos,numSteps))