import pygame
import sys

from config import *
from heart import Heart
from particle import ParticleEngine
from stars import StarField


def main():

    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)

    clock = pygame.time.Clock()

    # Create a transparent surface for trails
    trail_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    # Objects
    heart = Heart()
    particles = ParticleEngine(heart)
    stars = StarField()

    running = True

    while running:

        dt = clock.tick(FPS) / 1000.0

        # ---------------------------
        # Events
        # ---------------------------

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    running = False

        # ---------------------------
        # Update
        # ---------------------------

        heart.update(dt)

        particles.update(dt)

        stars.update(dt)

        # ---------------------------
        # Fade old frame
        # ---------------------------

        fade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

        fade.fill((0, 0, 0, TRAIL_ALPHA))

        trail_surface.blit(fade, (0, 0))

        # Draw stars
        stars.draw(trail_surface)

        # Draw particles
        particles.draw(trail_surface)

        # ---------------------------
        # Display
        # ---------------------------

        screen.fill(BLACK)

        screen.blit(trail_surface, (0, 0))

        fps = clock.get_fps()

        pygame.display.set_caption(
            f"{TITLE} | FPS: {fps:.0f}"
        )

        pygame.display.flip()

    pygame.quit()

    sys.exit()


if __name__ == "__main__":
    main()