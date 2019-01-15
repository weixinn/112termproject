import pygame

class GameCharacter(pygame.sprite.Sprite):
    
    def __init__(self, x, y, image, speed):
        super().__init__()
        
        # x,y is the center point of the character image
        self.x, self.y = x, y
        self.image = image
        self.width, self.height = image.get_size()
        self.speed = speed
        self.item = None
        
        self.updateRect()
        
    # for collision detection
    def updateRect(self):
        w, h = self.width, self.height
        self.rect = pygame.Rect(self.x - w / 2, self.y - h / 2, w, h)
        
    def update(self, keysDown):
        self.updateRect()
        
    def useItem(self):
        if self.item == 'gun':
            
        elif self.item == 'laser':
            pass