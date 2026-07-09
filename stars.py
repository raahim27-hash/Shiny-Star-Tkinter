"""
stars.py
Twinkling star field for the Starry Heart animation.
"""

import random
import pygame

from config import *


class Star:
    def __init__(self):
        self.reset()

    def reset(self):

        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)

        self.radius = random.randint(
            STAR_MIN_SIZE,
            STAR_MAX_SIZE
        )

        self.alpha = random.randint(30, 255)

        self.direction = random.choice([-1, 1])

        self.speed = random.uniform(
            50,
            180
        )

    def update(self, dt):

        self.alpha += self.direction * self.speed * dt

        if self.alpha >= 255:
            self.alpha = 255
            self.direction = -1

        elif self.alpha <= 20:

            self.reset()

    def draw(self, screen):

        size = self.radius * 6

        surf = pygame.Surface(
            (size, size),
            pygame.SRCALPHA
        )

        # Outer glow
        pygame.draw.circle(
            surf,
            (255, 255, 255, int(self.alpha * 0.15)),
            (size // 2, size // 2),
            self.radius * 3
        )

        # Middle glow
        pygame.draw.circle(
            surf,
            (255, 255, 255, int(self.alpha * 0.45)),
            (size // 2, size // 2),
            self.radius * 2
        )

        # Bright center
        pygame.draw.circle(
            surf,
            (255, 255, 255, int(self.alpha)),
            (size // 2, size // 2),
            self.radius
        )

        screen.blit(
            surf,
            (
                self.x - size // 2,
                self.y - size // 2
            )
        )


class StarField:

    def __init__(self):

        self.stars = [
            Star()
            for _ in range(STAR_COUNT)
        ]

    def update(self, dt):

        for star in self.stars:
            star.update(dt)

    def draw(self, screen):

        for star in self.stars:
            star.draw(screen)