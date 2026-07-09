"""
heart.py
Mathematical heart used by the particle system.
"""

import math
import random

from config import *


class Heart:
    def __init__(self):

        self.time = 0.0
        self.scale = HEART_SCALE

    # --------------------------------------------------
    # Update pulse
    # --------------------------------------------------

    def update(self, dt):

        self.time += dt

    # --------------------------------------------------
    # Breathing animation
    # --------------------------------------------------

    def pulse(self):

        return 1.0 + PULSE_AMOUNT * math.sin(
            self.time * PULSE_SPEED
        )

    # --------------------------------------------------
    # Heart equation
    # --------------------------------------------------

    def point(self, t):

        x = 16 * math.sin(t) ** 3

        y = (
            13 * math.cos(t)
            - 5 * math.cos(2 * t)
            - 2 * math.cos(3 * t)
            - math.cos(4 * t)
        )

        p = self.pulse()

        x *= self.scale * p
        y *= self.scale * p

        # Flip Y so heart points upward
        y = -y

        return (
            CENTER_X + x,
            CENTER_Y + y,
        )

    # --------------------------------------------------
    # Random point ON the heart
    # --------------------------------------------------

    def random_edge(self):

        t = random.random() * math.pi * 2

        return self.point(t)

    # --------------------------------------------------
    # Random point INSIDE the heart
    # --------------------------------------------------

    def random_inside(self):

        t = random.random() * math.pi * 2

        x = 16 * math.sin(t) ** 3

        y = (
            13 * math.cos(t)
            - 5 * math.cos(2 * t)
            - 2 * math.cos(3 * t)
            - math.cos(4 * t)
        )

        # Distance toward center
        r = math.sqrt(random.random())

        x *= r
        y *= r

        p = self.pulse()

        x *= self.scale * p
        y *= self.scale * p

        y = -y

        return (
            CENTER_X + x,
            CENTER_Y + y,
        )

    # --------------------------------------------------
    # Create many edge points
    # --------------------------------------------------

    def edge_points(self, count=HEART_POINTS):

        pts = []

        for i in range(count):

            t = i / count * math.pi * 2

            pts.append(self.point(t))

        return pts

    # --------------------------------------------------
    # Create cloud inside heart
    # --------------------------------------------------

    def cloud(self, count):

        return [self.random_inside() for _ in range(count)]