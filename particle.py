# """
# particle.py
# Particle engine for the Starry Sea Flowing Light animation.
# """

# import random
# import math
# import pygame

# from config import *


# class Particle:

#     def __init__(self, heart):

#         self.heart = heart
#         self.reset()

#     # ----------------------------------------------------
#     # Respawn particle
#     # ----------------------------------------------------

#     def reset(self):

#         self.x, self.y = self.heart.random_inside()

#         self.target_x, self.target_y = self.heart.random_edge()

#         self.life = random.uniform(1.5, 4.0)

#         self.age = random.uniform(0, self.life)

#         self.size = random.uniform(
#             PARTICLE_MIN_SIZE,
#             PARTICLE_MAX_SIZE,
#         )

#         self.speed = random.uniform(
#             0.8,
#             1.6,
#         )

#         self.alpha = random.randint(
#             150,
#             PARTICLE_ALPHA,
#         )

#     # ----------------------------------------------------
#     # Update particle
#     # ----------------------------------------------------

#     def update(self, dt):

#         self.age += dt

#         if self.age >= self.life:
#             self.reset()
#             return

#         dx = self.target_x - self.x
#         dy = self.target_y - self.y

#         dist = math.hypot(dx, dy)

#         if dist > 1:

#             self.x += dx * PARTICLE_SPEED * self.speed * 60
#             self.y += dy * PARTICLE_SPEED * self.speed * 60

#         else:

#             self.target_x, self.target_y = (
#                 self.heart.random_edge()
#             )

#         # Tiny floating movement
#         self.x += random.uniform(-0.15, 0.15)
#         self.y += random.uniform(-0.15, 0.15)

#     # ----------------------------------------------------
#     # Draw particle
#     # ----------------------------------------------------

#     def draw(self, screen):

#         # Outer glow
#         glow_radius = int(self.size * 6)

#         glow = pygame.Surface(
#             (glow_radius * 2, glow_radius * 2),
#             pygame.SRCALPHA,
#         )

#         pygame.draw.circle(
#             glow,
#             (255, 255, 255, 20),
#             (glow_radius, glow_radius),
#             glow_radius,
#         )

#         screen.blit(
#             glow,
#             (
#                 self.x - glow_radius,
#                 self.y - glow_radius,
#             ),
#         )

#         # Middle glow
#         glow2 = pygame.Surface(
#             (12, 12),
#             pygame.SRCALPHA,
#         )

#         pygame.draw.circle(
#             glow2,
#             (255, 255, 255, 70),
#             (6, 6),
#             4,
#         )

#         screen.blit(
#             glow2,
#             (
#                 self.x - 6,
#                 self.y - 6,
#             ),
#         )

#         # Bright center
#         pygame.draw.circle(
#             screen,
#             WHITE,
#             (int(self.x), int(self.y)),
#             max(1, int(self.size)),
#         )


# # ============================================================
# # Particle Manager
# # ============================================================

# class ParticleSystem:

#     def __init__(self, heart):

#         self.heart = heart

#         self.particles = [

#             Particle(heart)

#             for _ in range(PARTICLE_COUNT)

#         ]

#     def update(self, dt):

#         for p in self.particles:
#             p.update(dt)

#     def draw(self, screen):

#         for p in self.particles:
#             p.draw(screen)


"""
particle.py
Professional particle engine
Part 1
"""

import math
import random
from collections import deque

import pygame

from config import *


# -------------------------------------------------------
# Small vector helpers
# -------------------------------------------------------

def clamp(value, low, high):
    return max(low, min(high, value))


def lerp(a, b, t):
    return a + (b - a) * t


# -------------------------------------------------------
# Flow Field
# -------------------------------------------------------

class FlowField:
    """
    Creates a smooth vector field.
    Particles follow this instead of moving
    directly toward a point.
    """

    def __init__(self):

        self.time = 0.0

    def update(self, dt):

        self.time += dt

    def angle(self, x, y):

        nx = x * 0.0025
        ny = y * 0.0025

        a = math.sin(nx * 3 + self.time)

        b = math.cos(ny * 2 - self.time * 0.7)

        c = math.sin((nx + ny) * 2)

        return (a + b + c) * math.pi

    def vector(self, x, y):

        ang = self.angle(x, y)

        return (
            math.cos(ang),
            math.sin(ang)
        )


# -------------------------------------------------------
# Trail
# -------------------------------------------------------

class Trail:

    def __init__(self):

        self.points = deque(maxlen=25)

    def add(self, x, y):

        self.points.append((x, y))

    def clear(self):

        self.points.clear()


# -------------------------------------------------------
# Particle
# -------------------------------------------------------

class Particle:

    def __init__(self, heart, flow):

        self.heart = heart
        self.flow = flow

        self.reset()

    # --------------------------------------------

    def reset(self):

        self.x, self.y = self.heart.random_inside()

        self.vx = random.uniform(-0.4, 0.4)
        self.vy = random.uniform(-0.4, 0.4)

        self.ax = 0.0
        self.ay = 0.0

        self.size = random.uniform(1.0, 3.5)

        self.life = random.uniform(4.0, 8.0)
        self.age = random.random() * self.life

        self.alpha = random.randint(170, 255)

        self.speed = random.uniform(0.6, 1.6)

        self.trail = Trail()

        self.twinkle = random.random() * math.pi * 2

    # --------------------------------------------

    def update(self, dt):

        self.age += dt

        if self.age >= self.life:

            self.reset()
            return

        fx, fy = self.flow.vector(self.x, self.y)

        self.ax = fx * 0.15
        self.ay = fy * 0.15

        self.vx += self.ax
        self.vy += self.ay

        speed = math.sqrt(self.vx*self.vx + self.vy*self.vy)

        max_speed = 2.2 * self.speed

        if speed > max_speed:

            self.vx *= max_speed / speed
            self.vy *= max_speed / speed

        self.x += self.vx
        self.y += self.vy

        # breathing attraction
        hx, hy = self.heart.random_inside()

        self.x = lerp(self.x, hx, 0.002)
        self.y = lerp(self.y, hy, 0.002)

        self.trail.add(self.x, self.y)

        self.twinkle += dt * 4

                # --------------------------------------------
        # Friction (keeps particles stable)
        # --------------------------------------------

        self.vx *= 0.985
        self.vy *= 0.985

        # --------------------------------------------
        # Keep particles inside the heart region
        # --------------------------------------------

        cx = CENTER_X
        cy = CENTER_Y

        dx = self.x - cx
        dy = self.y - cy

        dist = math.sqrt(dx * dx + dy * dy)

        max_radius = HEART_SCALE * 18

        if dist > max_radius:

            angle = math.atan2(dy, dx)

            self.x = cx + math.cos(angle) * max_radius
            self.y = cy + math.sin(angle) * max_radius

            self.vx *= -0.3
            self.vy *= -0.3

    # -------------------------------------------------------
    # Glow Drawing
    # -------------------------------------------------------

    def draw_glow(self, surface):

        glow_radius = int(self.size * 8)

        glow = pygame.Surface(
            (glow_radius * 2, glow_radius * 2),
            pygame.SRCALPHA
        )

        pygame.draw.circle(
            glow,
            (255, 255, 255, 12),
            (glow_radius, glow_radius),
            glow_radius
        )

        pygame.draw.circle(
            glow,
            (255, 255, 255, 28),
            (glow_radius, glow_radius),
            int(glow_radius * 0.65)
        )

        pygame.draw.circle(
            glow,
            (255, 255, 255, 70),
            (glow_radius, glow_radius),
            int(glow_radius * 0.35)
        )

        surface.blit(
            glow,
            (
                self.x - glow_radius,
                self.y - glow_radius
            ),
            special_flags=pygame.BLEND_PREMULTIPLIED
        )

    # -------------------------------------------------------
    # Trail Drawing
    # -------------------------------------------------------

    def draw_trail(self, surface):

        pts = list(self.trail.points)

        if len(pts) < 2:
            return

        for i in range(1, len(pts)):

            p1 = pts[i - 1]
            p2 = pts[i]

            alpha = int(255 * (i / len(pts)) * 0.35)

            color = (
                255,
                255,
                255,
                alpha
            )

            line_surface = pygame.Surface(
                (WIDTH, HEIGHT),
                pygame.SRCALPHA
            )

            pygame.draw.line(
                line_surface,
                color,
                p1,
                p2,
                max(1, int(self.size))
            )

            surface.blit(
                line_surface,
                (0, 0),
                special_flags=pygame.BLEND_PREMULTIPLIED
            )

    # -------------------------------------------------------
    # Core Particle Drawing
    # -------------------------------------------------------

    def draw(self, surface):

        self.draw_trail(surface)

        self.draw_glow(surface)

        pulse = 0.8 + 0.2 * math.sin(self.twinkle)

        radius = max(
            1,
            int(self.size * pulse)
        )

        pygame.draw.circle(
            surface,
            WHITE,
            (
                int(self.x),
                int(self.y)
            ),
            radius
        )

        # ==========================================================
# Particle Engine
# ==========================================================

class ParticleEngine:
    """
    High-performance particle manager.
    Handles thousands of particles efficiently.
    """

    def __init__(self, heart):

        self.heart = heart
        self.flow = FlowField()

        # Create particle pool
        self.particles = [
            Particle(self.heart, self.flow)
            for _ in range(PARTICLE_COUNT)
        ]

        # Reusable glow surface (avoids reallocating every frame)
        self.glow_surface = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )

    # ------------------------------------------------------
    # Update
    # ------------------------------------------------------

    def update(self, dt):

        self.flow.update(dt)

        for particle in self.particles:
            particle.update(dt)

    # ------------------------------------------------------
    # Draw all trails
    # ------------------------------------------------------

    def draw_trails(self, surface):

        for particle in self.particles:
            particle.draw_trail(surface)

    # ------------------------------------------------------
    # Draw all glows
    # ------------------------------------------------------

    def draw_glows(self):

        self.glow_surface.fill((0, 0, 0, 0))

        for particle in self.particles:
            particle.draw_glow(self.glow_surface)

    # ------------------------------------------------------
    # Draw particle cores
    # ------------------------------------------------------

    def draw_particles(self, surface):

        for particle in self.particles:

            pulse = 0.8 + 0.2 * math.sin(
                particle.twinkle
            )

            radius = max(
                1,
                int(particle.size * pulse)
            )

            pygame.draw.circle(
                surface,
                WHITE,
                (
                    int(particle.x),
                    int(particle.y)
                ),
                radius
            )

    # ------------------------------------------------------
    # Complete renderer
    # ------------------------------------------------------

    def draw(self, surface):

        # 1. trails
        self.draw_trails(surface)

        # 2. glows
        self.draw_glows()

        surface.blit(
            self.glow_surface,
            (0, 0),
            special_flags=pygame.BLEND_ADD
        )

        # 3. particle cores
        self.draw_particles(surface)

    # ------------------------------------------------------
    # Reset
    # ------------------------------------------------------

    def reset(self):

        for particle in self.particles:
            particle.reset()

    # ------------------------------------------------------
    # Change particle count dynamically
    # ------------------------------------------------------

    def set_particle_count(self, count):

        self.particles = [
            Particle(self.heart, self.flow)
            for _ in range(count)
        ]

    # ------------------------------------------------------
    # FPS Optimizer
    # ------------------------------------------------------

    def optimize(self, fps):

        # Optional adaptive quality

        if fps < 40 and len(self.particles) > 2500:

            remove = int(len(self.particles) * 0.05)

            self.particles = self.particles[:-remove]

        elif fps > 70 and len(self.particles) < PARTICLE_COUNT:

            add = int(PARTICLE_COUNT * 0.03)

            for _ in range(add):

                self.particles.append(
                    Particle(self.heart, self.flow)
                )

                # ==========================================================
# Utility Methods
# ==========================================================

    def add_particles(self, amount):

        for _ in range(amount):

            self.particles.append(
                Particle(self.heart, self.flow)
            )

    def remove_particles(self, amount):

        if amount <= 0:
            return

        self.particles = self.particles[:-amount]

    def particle_count(self):

        return len(self.particles)

    def clear(self):

        self.particles.clear()


# ==========================================================
# Bloom Effect
# ==========================================================

    def bloom(self, screen):

        bloom = pygame.transform.smoothscale(
            self.glow_surface,
            (WIDTH // 2, HEIGHT // 2)
        )

        bloom = pygame.transform.smoothscale(
            bloom,
            (WIDTH, HEIGHT)
        )

        screen.blit(
            bloom,
            (0, 0),
            special_flags=pygame.BLEND_ADD
        )


# ==========================================================
# Motion Blur
# ==========================================================

    def motion_blur(self, screen):

        blur = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )

        blur.fill((0, 0, 0, 12))

        screen.blit(
            blur,
            (0, 0)
        )


# ==========================================================
# Full Renderer
# ==========================================================

    def render(self, screen):

        self.motion_blur(screen)

        self.draw(screen)

        self.bloom(screen)


# ==========================================================
# Statistics
# ==========================================================

    def stats(self):

        return {

            "particles": len(self.particles),

            "average_size":

                sum(
                    p.size
                    for p in self.particles
                ) / len(self.particles),

            "average_speed":

                sum(
                    math.sqrt(
                        p.vx*p.vx +
                        p.vy*p.vy
                    )
                    for p in self.particles
                ) / len(self.particles)
        }


# ==========================================================
# Debug Draw
# ==========================================================

    def debug(self, screen, font):

        fps = int(pygame.time.Clock().get_fps())

        text = [

            f"Particles : {len(self.particles)}",

            f"FPS : {fps}",

            f"Heart Scale : {HEART_SCALE}",

        ]

        y = 10

        for line in text:

            img = font.render(
                line,
                True,
                (255,255,255)
            )

            screen.blit(
                img,
                (10,y)
            )

            y += 22


# ==========================================================
# End of particle.py
# ==========================================================