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

        # Wall-aware movement
        new_rect = self.rect.move(dx, 0)
        if not self._hits_wall(new_rect, walls, rows, cols):
            self.rect = new_rect

        new_rect = self.rect.move(0, dy)
        if not self._hits_wall(new_rect, walls, rows, cols):
            self.rect = new_rect

    def _hits_wall(self, rect, walls, rows, cols):
        # Prevent the player from leaving the maze.
        if rect.left < 0 or rect.top < 0:
            return True
        if rect.right > cols * CELL or rect.bottom > rows * CELL:
            return True

        # Only check cells touched by the player's rectangle.
        left = rect.left // CELL
        right = (rect.right - 1) // CELL
        top = rect.top // CELL
        bottom = (rect.bottom - 1) // CELL

        for r in range(top, bottom + 1):
            for c in range(left, right + 1):
                x = c * CELL
                y = r * CELL

                # North wall
                if walls[r][c][0]:
                    wall = pygame.Rect(x, y, CELL, 3)
                    if rect.colliderect(wall):
                        return True

                # South wall
                if walls[r][c][1]:
                    wall = pygame.Rect(x, y + CELL - 3, CELL, 3)
                    if rect.colliderect(wall):
                        return True

                # East wall
                if walls[r][c][2]:
                    wall = pygame.Rect(x + CELL - 3, y, 3, CELL)
                    if rect.colliderect(wall):
                        return True

                # West wall
                if walls[r][c][3]:
                    wall = pygame.Rect(x, y, 3, CELL)
                    if rect.colliderect(wall):
                        return True

        return False

    def draw(self, screen):
        pygame.draw.ellipse(screen, self.color, self.rect)
