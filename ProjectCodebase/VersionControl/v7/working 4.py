def getRectForPos(pos, wallSize):
    row, col = pos
    x = wallSize*(col+1)
    y = wallSize*(row+1)
    width, height = wallSize, wallSize
    return (x,y,width,height)

# centre of the player must be within the innerRect of the pos
# midX and midY are the centre of the pos
def isWithinPos(curX, curY, pos, wallSize, playerH, playerW):
    rect = getRectForPos(pos, wallSize)
    x, y, w, h = rect
    midX = x + w/2
    midY = y + h/2
    maxHeightDiff = (0.5*wallSize) - (0.5*playerH)
    maxWidthDiff = (0.5*wallSize) - (0.5*playerW)
    print (midX-maxWidthDiff, midY-maxHeightDiff)
    print (midX+maxWidthDiff, midY+maxHeightDiff)
    if curX >= midX+maxWidthDiff or curX <= midX-maxWidthDiff:
        return False
    if curY >= midY+maxHeightDiff or curY <= midY-maxHeightDiff:
        return False
    return True
    
print (isWithinPos(5,4,(3,3),41,32,24))