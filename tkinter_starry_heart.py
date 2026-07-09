"""Starry Sea Flowing Light heart animation in Tkinter.

Run:
    python tkinter_starry_heart.py

Record a 30 second MP4:
    python tkinter_starry_heart.py --record
"""

from __future__ import annotations

import argparse
import math
import os
import random
import sys
import tkinter as tk
from dataclasses import dataclass, field
from typing import List, Tuple

from PIL import Image, ImageDraw, ImageFilter, ImageTk
import numpy as np

try:
    import cv2
except ImportError:
    cv2 = None


WIDTH = 1280
HEIGHT = 720
FPS = 30
DURATION = 30.0
OUTPUT_PATH = os.path.join("output", "starry_heart.mp4")

BG = (4, 5, 10, 255)
WHITE = (255, 255, 255, 255)


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def ease_out_cubic(t: float) -> float:
    t = clamp(t, 0.0, 1.0)
    return 1.0 - (1.0 - t) ** 3


def heart_point(theta: float, scale: float, cx: float, cy: float, pulse: float) -> Tuple[float, float]:
    x = 16.0 * math.sin(theta) ** 3
    y = (
        13.0 * math.cos(theta)
        - 5.0 * math.cos(2.0 * theta)
        - 2.0 * math.cos(3.0 * theta)
        - math.cos(4.0 * theta)
    )

    x *= scale * pulse
    y *= scale * pulse
    y = -y

    return cx + x, cy + y


def heart_inside_point(scale: float, cx: float, cy: float, pulse: float) -> Tuple[float, float]:
    theta = random.random() * math.tau
    radius = math.sqrt(random.random())

    x = 16.0 * math.sin(theta) ** 3
    y = (
        13.0 * math.cos(theta)
        - 5.0 * math.cos(2.0 * theta)
        - 2.0 * math.cos(3.0 * theta)
        - math.cos(4.0 * theta)
    )

    x *= radius * scale * pulse
    y *= radius * scale * pulse
    y = -y

    return cx + x, cy + y


def cubic_bezier(p0, p1, p2, p3, t):
    u = 1.0 - t
    tt = t * t
    uu = u * u
    uuu = uu * u
    ttt = tt * t
    x = uuu * p0[0] + 3 * uu * t * p1[0] + 3 * u * tt * p2[0] + ttt * p3[0]
    y = uuu * p0[1] + 3 * uu * t * p1[1] + 3 * u * tt * p2[1] + ttt * p3[1]
    return x, y


def phase_style(time_value: float) -> dict:
    phase = int(time_value // 7.5) % 4

    styles = [
        {"ribbon_count": 72, "spark_count": 760, "glow_strength": 1.05, "wave": 0.95, "side_boost": 1.10},
        {"ribbon_count": 86, "spark_count": 920, "glow_strength": 1.18, "wave": 1.18, "side_boost": 1.18},
        {"ribbon_count": 98, "spark_count": 1080, "glow_strength": 1.28, "wave": 1.42, "side_boost": 1.28},
        {"ribbon_count": 82, "spark_count": 900, "glow_strength": 1.12, "wave": 1.00, "side_boost": 1.16},
    ]
    return styles[phase]


def flow_vector(x: float, y: float, time_value: float, wave_strength: float) -> Tuple[float, float]:
    nx = x / WIDTH
    ny = y / HEIGHT

    angle = (
        math.sin(nx * 6.0 + time_value * 0.95) 
        + math.cos(ny * 5.0 - time_value * 0.70)
        + math.sin((nx + ny) * 8.0 + time_value * 0.35)
    ) * math.pi * wave_strength

    return math.cos(angle), math.sin(angle)


@dataclass
class Ribbon:
    cx: float
    cy: float
    scale: float
    pulse_speed: float
    phase_offset: float = field(default_factory=lambda: random.random() * math.tau)
    speed: float = field(default_factory=lambda: random.uniform(0.18, 0.52))
    drift: float = field(default_factory=lambda: random.uniform(-0.7, 0.7))
    thickness: float = field(default_factory=lambda: random.uniform(1.0, 2.6))
    progress: float = field(default_factory=random.random)

    def reset(self) -> None:
        self.phase_offset = random.random() * math.tau
        self.speed = random.uniform(0.18, 0.52)
        self.drift = random.uniform(-0.7, 0.7)
        self.thickness = random.uniform(1.0, 2.6)
        self.progress = random.random() * 0.12

    def points(self, time_value: float, pulse: float, wave_strength: float):
        theta = self.phase_offset + time_value * 0.18

        start = heart_point(theta, self.scale, self.cx, self.cy, pulse)

        bottom = (self.cx + self.drift * 160.0, self.cy + self.scale * 20.5 * pulse)

        top_bump = heart_point(theta * 0.4 + 0.7, self.scale * 0.92, self.cx, self.cy - 12.0, pulse)

        control1 = (
            lerp(start[0], self.cx, 0.35) + math.sin(time_value * 1.8 + self.phase_offset) * 18.0 * wave_strength,
            lerp(start[1], self.cy - self.scale * 9.0, 0.45) + math.cos(time_value * 1.35 + self.phase_offset) * 12.0,
        )

        control2 = (
            lerp(bottom[0], self.cx, 0.72) + math.sin(time_value * 1.2 + self.phase_offset * 2.0) * 32.0 * wave_strength,
            lerp(bottom[1], self.cy + self.scale * 3.0, 0.42) - self.scale * 10.5 * pulse,
        )

        if math.sin(theta * 1.5 + time_value * 0.9) > 0.2:
            control1 = (
                lerp(control1[0], top_bump[0], 0.28),
                lerp(control1[1], top_bump[1], 0.22),
            )

        return start, control1, control2, bottom


@dataclass
class Spark:
    cx: float
    cy: float
    scale: float
    life: float = field(default_factory=lambda: random.uniform(0.7, 2.7))
    age: float = field(default_factory=lambda: random.random())
    theta: float = field(default_factory=lambda: random.random() * math.tau)
    radius: float = field(default_factory=lambda: random.uniform(0.4, 1.8))
    brightness: float = field(default_factory=lambda: random.uniform(0.25, 1.0))
    drift_x: float = field(default_factory=lambda: random.uniform(-0.5, 0.5))
    drift_y: float = field(default_factory=lambda: random.uniform(-0.3, 0.3))
    side_bias: float = field(default_factory=lambda: random.uniform(0.0, 1.0))
    x: float = 0.0
    y: float = 0.0

    def __post_init__(self) -> None:
        self.x, self.y = self._spawn_point(1.0)

    def _spawn_point(self, pulse: float) -> Tuple[float, float]:
        if self.side_bias > 0.62:
            side = -1.0 if random.random() < 0.5 else 1.0
            x = self.cx + side * random.uniform(self.scale * 7.2, self.scale * 15.4)
            y = self.cy - random.uniform(self.scale * 8.8, self.scale * 1.8)
            x += random.uniform(-self.scale * 1.0, self.scale * 1.0)
            y += random.uniform(-self.scale * 0.9, self.scale * 1.8)
            return x, y

        return heart_inside_point(self.scale, self.cx, self.cy, pulse)

    def reset(self) -> None:
        self.life = random.uniform(0.7, 2.7)
        self.age = 0.0
        self.theta = random.random() * math.tau
        self.radius = random.uniform(0.4, 1.8)
        self.brightness = random.uniform(0.25, 1.0)
        self.drift_x = random.uniform(-0.5, 0.5)
        self.drift_y = random.uniform(-0.3, 0.3)
        self.side_bias = random.uniform(0.0, 1.0)
        self.x, self.y = self._spawn_point(1.0)

    def update(self, dt: float, time_value: float, pulse: float, wave_strength: float) -> None:
        self.age += dt

        if self.age >= self.life:
            self.reset()
            return

        fx, fy = flow_vector(self.x, self.y, time_value, wave_strength)

        self.x += (fx * 0.9 + self.drift_x) * 28.0 * dt
        self.y += (fy * 0.9 + self.drift_y) * 28.0 * dt

        if self.side_bias > 0.62:
            edge_theta = random.random() * math.tau
            target_x, target_y = heart_point(edge_theta, self.scale * 1.03, self.cx, self.cy - 10.0, pulse)
            target_x += math.sin(time_value * 1.4 + self.theta) * self.scale * 0.25
            target_y += math.cos(time_value * 1.1 + self.theta) * self.scale * 0.18
        else:
            target_x, target_y = heart_inside_point(self.scale, self.cx, self.cy, pulse)

        mix = 0.008 if self.side_bias > 0.62 else 0.011
        self.x = lerp(self.x, target_x, mix)
        self.y = lerp(self.y, target_y, mix)

        self.theta += dt * (1.1 + wave_strength * 0.45)

    def draw(self, draw: ImageDraw.ImageDraw, time_value: float) -> None:
        age_ratio = self.age / self.life
        alpha = int(255 * (1.0 - age_ratio) * self.brightness)
        if alpha <= 0:
            return

        pulse = 0.75 + 0.25 * math.sin(time_value * 6.0 + self.theta)
        radius = max(1, int(self.radius * pulse))

        glow_radius = radius * 6
        x0 = int(self.x - glow_radius)
        y0 = int(self.y - glow_radius)
        x1 = int(self.x + glow_radius)
        y1 = int(self.y + glow_radius)

        draw.ellipse((x0, y0, x1, y1), fill=(255, 255, 255, max(0, int(alpha * 0.14))))
        draw.ellipse((int(self.x - radius * 3), int(self.y - radius * 3), int(self.x + radius * 3), int(self.y + radius * 3)), fill=(255, 255, 255, max(0, int(alpha * 0.34))))
        draw.ellipse((int(self.x - radius), int(self.y - radius), int(self.x + radius), int(self.y + radius)), fill=(255, 255, 255, alpha))


class Star:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.radius = random.randint(1, 3)
        self.phase = random.random() * math.tau
        self.speed = random.uniform(1.8, 4.8)
        self.depth = random.uniform(0.2, 1.0)

    def update(self, dt: float) -> None:
        self.phase += dt * self.speed
        self.y += math.sin(self.phase * 0.6) * 2.0 * dt * self.depth
        self.x += math.cos(self.phase * 0.35) * 1.2 * dt * self.depth

        if self.x < -20 or self.x > WIDTH + 20 or self.y < -20 or self.y > HEIGHT + 20:
            self.reset()

    def draw(self, draw: ImageDraw.ImageDraw, time_value: float) -> None:
        twinkle = 0.35 + 0.65 * (0.5 + 0.5 * math.sin(time_value * self.speed + self.phase))
        alpha = int(210 * twinkle)
        r = self.radius
        draw.ellipse((self.x - r * 4, self.y - r * 4, self.x + r * 4, self.y + r * 4), fill=(255, 255, 255, int(alpha * 0.10)))
        draw.ellipse((self.x - r * 2, self.y - r * 2, self.x + r * 2, self.y + r * 2), fill=(255, 255, 255, int(alpha * 0.35)))
        draw.ellipse((self.x - r, self.y - r, self.x + r, self.y + r), fill=(255, 255, 255, alpha))


class StarryHeartApp:
    def __init__(self, record: bool = False):
        self.record = record
        self.running = True
        self.frame_index = 0

        self.root = tk.Tk()
        self.root.title("Starry Sea Flowing Light")
        self.root.geometry(f"{WIDTH}x{HEIGHT}")
        self.root.configure(bg="#04050a")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.bind("<Escape>", lambda _event: self.close())

        self.canvas = tk.Canvas(self.root, width=WIDTH, height=HEIGHT, highlightthickness=0, bg="#04050a")
        self.canvas.pack(fill="both", expand=True)
        self.image_item = self.canvas.create_image(0, 0, anchor="nw")
        self.photo = None

        self.cx = WIDTH * 0.5
        self.cy = HEIGHT * 0.50
        self.scale = min(WIDTH, HEIGHT) / 54.0

        self.ribbons: List[Ribbon] = [Ribbon(self.cx, self.cy, self.scale, 2.0) for _ in range(116)]
        self.sparks: List[Spark] = [Spark(self.cx, self.cy, self.scale) for _ in range(1280)]
        self.stars: List[Star] = [Star() for _ in range(220)]

        self.video_writer = None
        if self.record:
            if cv2 is None:
                raise RuntimeError("OpenCV is required for --record. Install with: pip install opencv-python")
            os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
            self.video_writer = cv2.VideoWriter(
                OUTPUT_PATH,
                cv2.VideoWriter_fourcc(*"mp4v"),
                FPS,
                (WIDTH, HEIGHT),
            )

        self.root.after(0, self._tick)

    def close(self) -> None:
        self.running = False
        if self.video_writer is not None:
            self.video_writer.release()
            self.video_writer = None
        self.root.destroy()

    def _background(self, image: Image.Image, time_value: float) -> None:
        draw = ImageDraw.Draw(image, "RGBA")

        # Side blooms help reproduce the bright glowy lights in the reference.
        side_offset_y = self.scale * 2.8
        for offset_x, radius, alpha in ((-self.scale * 10.5, 160, 48), (self.scale * 10.5, 160, 48)):
            draw.ellipse(
                (
                    self.cx + offset_x - radius,
                    self.cy - side_offset_y - radius,
                    self.cx + offset_x + radius,
                    self.cy - side_offset_y + radius,
                ),
                fill=(255, 255, 255, alpha),
            )

        # Broad backlight behind the whole composition.
        for radius, alpha in ((400, 20), (320, 28), (240, 38)):
            draw.ellipse(
                (
                    self.cx - radius,
                    self.cy - radius * 0.75,
                    self.cx + radius,
                    self.cy + radius * 0.95,
                ),
                fill=(255, 255, 255, alpha),
            )

        # Lower flowing band like the reference video's base light curtain.
        for idx in range(6):
            y = int(self.cy + self.scale * 10.0 + idx * 16)
            amp = 12 + idx * 2
            points = []
            for x in range(0, WIDTH + 40, 18):
                yy = y + math.sin(x * 0.010 + time_value * (0.55 + idx * 0.07)) * amp
                points.append((x, yy))
            draw.line(points, fill=(255, 255, 255, 30 - idx * 3), width=2)

        # Tiny side sparkles around the heart to mimic the scattered edge lights.
        for side in (-1, 1):
            for idx in range(24):
                x = self.cx + side * (self.scale * 7.5 + idx * 10.5)
                y = self.cy - self.scale * 2.0 + math.sin(time_value * 0.9 + idx * 0.22) * (self.scale * 0.9)
                radius = 1 + (idx % 3)
                draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(255, 255, 255, 30 + (idx % 4) * 14))

    def _heart_outline(self, image: Image.Image, time_value: float, pulse: float) -> None:
        draw = ImageDraw.Draw(image, "RGBA")
        pts = []
        for index in range(260):
            theta = math.tau * index / 260.0
            pts.append(heart_point(theta, self.scale * 1.04, self.cx, self.cy - 12.0, pulse))

        # Draw the outline in two passes to mimic the bright rim from the reference.
        draw.line(pts, fill=(255, 255, 255, 14), width=12, joint="curve")
        draw.line(pts, fill=(255, 255, 255, 66), width=5, joint="curve")

        top_glow = []
        for index in range(90):
            theta = math.pi * (0.12 + index / 120.0)
            top_glow.append(heart_point(theta, self.scale * 0.98, self.cx, self.cy - 16.0, pulse))
        draw.line(top_glow, fill=(255, 255, 255, 42), width=3, joint="curve")

    def _draw_ribbons(self, image: Image.Image, time_value: float, pulse: float, style: dict) -> None:
        glow_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        core_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow_layer, "RGBA")
        core_draw = ImageDraw.Draw(core_layer, "RGBA")

        active_ribbons = max(20, min(len(self.ribbons), style["ribbon_count"]))

        for ribbon in self.ribbons[:active_ribbons]:
            if ribbon.progress >= 1.0:
                ribbon.reset()

            start, control1, control2, bottom = ribbon.points(time_value, pulse, style["wave"])

            ribbon.progress += ribbon.speed * (0.012 + style["wave"] * 0.003)
            local_progress = ease_out_cubic(ribbon.progress)

            samples = []
            sample_count = 28
            for idx in range(sample_count + 1):
                t = (idx / sample_count) * local_progress
                x, y = cubic_bezier(start, control1, control2, bottom, t)

                # Small motion across the ribbons to create the living flow.
                x += math.sin(time_value * 2.1 + ribbon.phase_offset + t * 9.0) * 7.5 * style["wave"]
                y += math.cos(time_value * 1.5 + ribbon.phase_offset + t * 7.0) * 2.5
                samples.append((x, y))

            if len(samples) >= 2:
                alpha = int(76 * style["glow_strength"])
                glow_draw.line(samples, fill=(255, 255, 255, alpha), width=max(2, int(ribbon.thickness * 5)))
                glow_draw.line(samples, fill=(255, 255, 255, int(alpha * 0.50)), width=max(1, int(ribbon.thickness * 8)))
                core_draw.line(samples, fill=(255, 255, 255, 165), width=max(1, int(ribbon.thickness)))

                end_x, end_y = samples[-1]
                glow_draw.ellipse((end_x - 6, end_y - 6, end_x + 6, end_y + 6), fill=(255, 255, 255, 135))
                core_draw.ellipse((end_x - 2, end_y - 2, end_x + 2, end_y + 2), fill=(255, 255, 255, 255))

        blur = glow_layer.filter(ImageFilter.GaussianBlur(radius=3.2))
        image.alpha_composite(blur)
        image.alpha_composite(core_layer)

    def _draw_sparks(self, image: Image.Image, time_value: float, pulse: float, style: dict) -> None:
        draw = ImageDraw.Draw(image, "RGBA")
        active_sparks = max(120, min(len(self.sparks), style["spark_count"]))

        for spark in self.sparks[:active_sparks]:
            spark.update(1.0 / FPS, time_value, pulse, style["wave"])
            spark.draw(draw, time_value)

    def _draw_stars(self, image: Image.Image, time_value: float) -> None:
        draw = ImageDraw.Draw(image, "RGBA")
        for star in self.stars:
            star.update(1.0 / FPS)
            star.draw(draw, time_value)

    def generate_frame(self, time_value: float) -> Image.Image:
        style = phase_style(time_value)
        pulse = 1.0 + 0.055 * math.sin(time_value * 2.15)

        frame = Image.new("RGBA", (WIDTH, HEIGHT), BG)
        self._background(frame, time_value)
        self._draw_stars(frame, time_value)
        self._heart_outline(frame, time_value, pulse)
        self._draw_ribbons(frame, time_value, pulse, style)
        self._draw_sparks(frame, time_value, pulse, style)

        flare_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        flare_draw = ImageDraw.Draw(flare_layer, "RGBA")
        for side in (-1, 1):
            for idx, y_ratio in enumerate((0.22, 0.32, 0.45, 0.58)):
                x = self.cx + side * self.scale * (11.0 + idx * 1.4)
                y = self.cy - self.scale * (8.3 - y_ratio * 9.0)
                flare_draw.ellipse((x - 8, y - 8, x + 8, y + 8), fill=(255, 255, 255, 110))
                flare_draw.ellipse((x - 18, y - 18, x + 18, y + 18), fill=(255, 255, 255, 40))
        frame.alpha_composite(flare_layer.filter(ImageFilter.GaussianBlur(radius=5.0)))

        # Center bloom to push the heart toward the bright reference look.
        bloom = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        bloom_draw = ImageDraw.Draw(bloom, "RGBA")
        bloom_draw.ellipse(
            (
                self.cx - self.scale * 13,
                self.cy - self.scale * 11,
                self.cx + self.scale * 13,
                self.cy + self.scale * 11,
            ),
            fill=(255, 255, 255, int(42 * style["glow_strength"])),
        )
        frame.alpha_composite(bloom.filter(ImageFilter.GaussianBlur(radius=22)))

        return frame

    def _tick(self) -> None:
        if not self.running:
            return

        elapsed = self.frame_index / FPS
        if elapsed >= DURATION:
            self.close()
            return

        frame = self.generate_frame(elapsed)

        if self.video_writer is not None:
            rgb = np.array(frame.convert("RGB"))
            bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
            self.video_writer.write(bgr)

        self.photo = ImageTk.PhotoImage(frame)
        self.canvas.itemconfig(self.image_item, image=self.photo)

        self.frame_index += 1
        self.root.after(int(1000 / FPS), self._tick)

    def run(self) -> None:
        self.root.mainloop()


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Starry Sea Flowing Light heart animation")
    parser.add_argument("--record", action="store_true", help="Export a 30 second MP4 to output/starry_heart.mp4")
    return parser.parse_args(argv)


def main(argv: List[str]) -> int:
    args = parse_args(argv)
    app = StarryHeartApp(record=args.record)
    app.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))