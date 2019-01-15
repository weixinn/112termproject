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

def getCoordFromPos(pos, wallSize):
    row, col = pos
    x = (col+1.5)*wallSize
    y = (row+1.5)*wallSize
    return (x,y)

board =        [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                [0, 1, 0, 1, 1, 0, 1, 0, 1, 0], 
                [0, 1, 0, 1, 1, 0, 1, 0, 0, 0], 
                [0, 1, 0, 0, 0, 0, 0, 0, 1, 0], 
                [0, 1, 1, 0, 1, 0, 1, 0, 0, 0], 
                [0, 1, 1, 0, 1, 0, 0, 1, 1, 0], 
                [0, 1, 1, 0, 1, 1, 0, 0, 0, 0], 
                [0, 0, 0, 0, 1, 0, 0, 1, 0, 0], 
                [0, 1, 1, 0, 1, 0, 1, 1, 1, 0], 
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
              
route = findRoute(board,(9,0),(0,9))
printRoute(route)
startingPos = (9,0)
endingPos = (0,9)
wallSize = 41
# get pos of player ==> get x and y of mid of that pos ==> do math
x, y = getCoordFromPos(startingPos, wallSize)
print(convertRoute(route, x, y, wallSize))
