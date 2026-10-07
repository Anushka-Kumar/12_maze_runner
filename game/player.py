import pygame
from game.maze import CELL

SPEED = 3

class Player:
    def __init__(self, r, c):
        self.r = r
        self.c = c
        x = c*CELL + CELL//2
        y = r*CELL + CELL//2
        self.rect = pygame.Rect(x-10, y-10, 20, 20)
        self.color = (60,120,220)

    def move(self, keys, walls, rows, cols):
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx = -SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx = SPEED
        if keys[pygame.K_UP] or keys[pygame.K_w]: dy = -SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy = SPEED

        # Wall-aware movement (check cell boundaries)
        new_rect = self.rect.move(dx, 0)
        if not self._hits_wall(new_rect, walls, rows, cols):
            self.rect = new_rect
        new_rect = self.rect.move(0, dy)
        if not self._hits_wall(new_rect, walls, rows, cols):
            self.rect = new_rect

    def _hits_wall(self, rect, walls, rows, cols):
        # Check the player's occupied cells and the maze walls between them
        left = rect.left // CELL
        right = (rect.right - 1) // CELL
        top = rect.top // CELL
        bottom = (rect.bottom - 1) // CELL

        if top < 0 or bottom >= rows or left < 0 or right >= cols:
            return True

        for r in range(top, bottom + 1):
            for c in range(left, right + 1):
                if c < right and walls[r][c][2]:  # East wall
                    return True
                if c > left and walls[r][c][3]:   # West wall
                    return True
                if r < bottom and walls[r][c][1]: # South wall
                    return True
                if r > top and walls[r][c][0]:    # North wall
                    return True

        return False

    def draw(self, screen):
        pygame.draw.ellipse(screen, self.color, self.rect)
