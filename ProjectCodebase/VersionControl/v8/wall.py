import pygame

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