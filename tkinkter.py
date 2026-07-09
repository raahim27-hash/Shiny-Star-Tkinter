"""
Starry Sea Flowing Light (星海流光) - Complete 3-Layer Wave & Fountain Replica
"""

import tkinter as tk
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageTk
import numpy as np
import math
import random

# ---------- Config ----------
WIDTH, HEIGHT = 1000, 640
FPS = 30
DURATION_SECONDS = 30
TOTAL_FRAMES = FPS * DURATION_SECONDS

ANCHOR_X = WIDTH / 2
ANCHOR_Y = HEIGHT - 80

HEART_CX = WIDTH / 2
HEART_CY = HEIGHT * 0.38
HEART_SCALE = 16.0

N_LINES = 360      # Increased density to handle all 3 structural groups
N_SPARKLES = 600   # Keeps the heart shape outline extremely clear and sharp

def heart_xy(t):
    """Mathematical definition of the reference heart profile."""
    x = 16 * math.sin(t) ** 3
    y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
    return HEART_CX + x * HEART_SCALE, HEART_CY - y * HEART_SCALE

class FlowStrand:
    """Generates the three foundational motion behaviors seen in the original reference video."""
    def __init__(self, idx, total):
        self.idx = idx
        self.pct = idx / total
        self.target_t = -math.pi + self.pct * 2 * math.pi
        
        rnd = random.Random(idx * 777)
        self.speed = rnd.uniform(0.5, 0.9)
        self.phase = rnd.uniform(0, 2 * math.pi)
        self.wave_amp = rnd.uniform(12, 24)
        self.brightness = rnd.uniform(140, 245)
        self.thickness = rnd.choice([1, 1, 2])
        
        # Split strands cleanly into three specialized functional layers
        if 0.25 <= self.pct <= 0.75:
            self.group = "core_fountain"
        elif (self.pct < 0.12) or (self.pct > 0.88):
            self.group = "side_cascade"
        else:
            self.group = "ground_bed_curls"

    def points(self, t_anim):
        pts = []
        steps = 55
        tx, ty = heart_xy(self.target_t)
        side_sign = -1.0 if self.pct < 0.5 else 1.0
        
        for i in range(steps + 1):
            prog = i / steps
            
            if self.group == "core_fountain":
                # --- LAYER 1: FOUNTAIN FILL & SHELL ---
                # Ascends from bottom anchor point to the outer heart target coordinates
                bx = ANCHOR_X + (tx - ANCHOR_X) * prog
                by = ANCHOR_Y + (ty - ANCHOR_Y) * prog
                
                # Sinuous high-frequency shimmer that creates the glowing fluid texture
                shimmer = self.wave_amp * math.sin(prog * 3.5 - t_anim * 6.0 + self.phase) * math.sin(prog * math.pi)
                bx += shimmer
                
            elif self.group == "side_cascade":
                # --- LAYER 2: WIDE SIDE CASCADES (LEFT & RIGHT WINGS) ---
                # Emigrates from center anchor, climbs up near heart edge, then drops outward
                mid_x = ANCHOR_X + side_sign * (WIDTH * 0.24)
                mid_y = HEART_CY + 60
                
                # Outward termination paths across left and right frame borders
                end_x = ANCHOR_X + side_sign * (WIDTH * 0.52) * (0.3 + 0.7 * prog)
                end_y = ANCHOR_Y - 30
                
                if prog < 0.35:
                    sub_p = prog / 0.35
                    bx = ANCHOR_X + (mid_x - ANCHOR_X) * sub_p
                    by = ANCHOR_Y + (mid_y - ANCHOR_Y) * sub_p
                else:
                    sub_p = (prog - 0.35) / 0.65
                    bx = mid_x + (end_x - mid_x) * sub_p
                    by = mid_y + (end_y - mid_y) * sub_p
                
                # Smooth organic fluid rolling wave action
                by += 22 * math.sin(bx * 0.022 - t_anim * 4.0 + self.phase) * math.sin(prog * math.pi)
                
            else:
                # --- LAYER 3: CURLY GROUND BED WAVES (UNDERNEATH THE HEART) ---
                # Sits flatly along the ground line right under the bottom tip of the heart
                bx = ANCHOR_X + side_sign * (WIDTH * 0.46) * prog
                base_y = ANCHOR_Y + 15
                
                # Highly compressed overlapping curly waveforms rolling across the ground plane
                c_freq1 = 0.045
                c_freq2 = 0.08
                curl = (16 * math.sin(bx * c_freq1 - t_anim * 5.5 + self.phase) + 
                        7 * math.cos(bx * c_freq2 + t_anim * 3.5))
                
                by = base_y + curl * math.sin(prog * math.pi * 0.5)
                
            pts.append((bx, by))
            
        return pts

class HeartSparkle:
    """Creates dense, sharp glitter clusters detailing the structural perimeter of the heart shape."""
    def __init__(self, idx):
        self.idx = idx
        self.reset()

    def reset(self):
        self.t = random.uniform(-math.pi, math.pi)
        # Tight padding to make sure the core heart shape is perfectly clear and sharp
        self.jitter_x = random.uniform(-7, 7)
        self.jitter_y = random.uniform(-7, 7)
        self.r = random.uniform(1.2, 3.4)
        self.phase = random.uniform(0, 2 * math.pi)
        self.speed = random.uniform(4.0, 7.5)
        self.life = random.randint(25, 65)
        self.age = random.randint(0, self.life)

    def update(self):
        self.age += 1
        if self.age > self.life:
            self.reset()

    def position(self):
        x, y = heart_xy(self.t)
        return x + self.jitter_x, y + self.jitter_y

    def brightness(self, t_anim):
        twinkle = (math.sin(t_anim * self.speed + self.phase) + 1) / 2
        fade = math.sin((self.age / self.life) * math.pi)
        return max(0.0, twinkle * fade)

class HeartApp:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.strands = [FlowStrand(i, N_LINES) for i in range(N_LINES)]
        self.heart_sparkles = [HeartSparkle(i) for i in range(N_SPARKLES)]
        
        self.background_stars = [
            (random.uniform(0, WIDTH), random.uniform(0, HEIGHT * 0.85),
             random.uniform(0.5, 1.4), random.uniform(0, 2 * math.pi), random.uniform(0.4, 1.3))
            for _ in range(120)
        ]

        self.frame_count = 0
        self.photo = None

        self.status = tk.Label(root, text="", fg="white", bg="black", font=("Segoe UI", 10))
        self.status.place(x=10, y=10)

        self.animate()

    def draw_frame(self):
        t = self.frame_count / FPS

        stars_l = Image.new("L", (WIDTH, HEIGHT), 0)
        flow_l = Image.new("L", (WIDTH, HEIGHT), 0)
        heart_l = Image.new("L", (WIDTH, HEIGHT), 0)

        d_stars = ImageDraw.Draw(stars_l)
        d_flow = ImageDraw.Draw(flow_l)
        d_heart = ImageDraw.Draw(heart_l)

        # 1. Background Environmental Stardust
        for (x, y, r, phase, speed) in self.background_stars:
            b = (math.sin(t * speed + phase) + 1) / 2
            c = int(75 + 125 * b)
            rr = r * (0.7 + b * 0.3)
            d_stars.ellipse([x - rr, y - rr, x + rr, y + rr], fill=c)

        # 2. Render Integrated Light Strands (Fountain + Wings + Ground Curls)
        for strand in self.strands:
            pts = strand.points(t)
            if len(pts) < 2: continue
            flicker = 0.86 + 0.14 * math.sin(t * 5.5 + strand.phase)
            c = int(strand.brightness * flicker)
            d_flow.line(pts, fill=c, width=strand.thickness, joint="curve")

        # 3. Brilliant Boundary Profile Sparkles
        for sp in self.heart_sparkles:
            sp.update()
            b = sp.brightness(t)
            if b <= 0: continue
            x, y = sp.position()
            c = int(255 * b)
            r = sp.r * (0.5 + b * 0.5)
            
            d_heart.ellipse([x - r, y - r, x + r, y + r], fill=c)
            
            # Anamorphic Cross Lens Flare Accents
            if b > 0.74:
                d_heart.line([x - r * 4.5, y, x + r * 4.5, y], fill=int(c * 0.65))
                d_heart.line([x, y - r * 4.5, x, y + r * 4.5], fill=int(c * 0.65))

        # ---- Dynamic Glow Layering ----
        stars_glow = ImageChops.add(stars_l, stars_l.filter(ImageFilter.GaussianBlur(1)))

        flow_core = flow_l.filter(ImageFilter.GaussianBlur(0.4))
        flow_halo = flow_l.filter(ImageFilter.GaussianBlur(2.5)).point(lambda v: int(v * 0.55))
        flow_glow = ImageChops.add(flow_core, flow_halo)

        heart_core = heart_l.filter(ImageFilter.GaussianBlur(0.5))
        heart_halo = heart_l.filter(ImageFilter.GaussianBlur(3.5)).point(lambda v: int(v * 0.85))
        heart_wide = heart_l.filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * 0.35))
        heart_glow = ImageChops.add(ImageChops.add(heart_core, heart_halo), heart_wide)

        # ---- Matrix Color Blending ----
        def tint(layer, color):
            arr = np.asarray(layer, dtype=np.float32) / 255.0
            return np.stack([arr * color[0], arr * color[1], arr * color[2]], axis=-1)

        rgb = tint(stars_glow, (225, 225, 240))
        rgb += tint(flow_glow, (210, 224, 255))  # Smooth, glowing white-silver light waves
        rgb += tint(heart_glow, (255, 254, 253)) # Crisp, intensely bright white heart structure

        rgb = np.clip(rgb, 0, 255).astype(np.uint8)
        return Image.fromarray(rgb, mode="RGB")

    def animate(self):
        if self.frame_count >= TOTAL_FRAMES:
            self.frame_count = 0

        frame = self.draw_frame()
        self.photo = ImageTk.PhotoImage(frame)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo)

        seconds_left = max(0, DURATION_SECONDS - self.frame_count // FPS)
        self.status.config(text=f"Starry Sea Flowing Light  |  {seconds_left}s")

        self.frame_count += 1
        self.root.after(int(1000 / FPS), self.animate)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Starry Sea Flowing Light - 星海流光")
    root.configure(bg="black")
    app = HeartApp(root)
    root.mainloop()