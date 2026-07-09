"""
Starry Sea Flowing Light (星海流光) - Exact Screen Replica with Ground Bed Waves
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
ANCHOR_Y = HEIGHT - 50

HEART_CX = WIDTH / 2
HEART_CY = HEIGHT * 0.40
HEART_SCALE = 16.5

N_LINES = 320 # Higher density to fill out the sea floor bed

def heart_xy(t):
    x = 16 * math.sin(t) ** 3
    y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
    return HEART_CX + x * HEART_SCALE, HEART_CY - y * HEART_SCALE

class FlowStrand:
    """Calculates individual strand trajectories, split into heart outlines, 

    sweeping side cascades, and low-lying ground waves beneath the heart."""
    def __init__(self, idx, total):
        self.idx = idx
        self.pct = idx / total
        
        self.target_t = -math.pi + self.pct * 2 * math.pi
        
        rnd = random.Random(idx * 999)
        self.speed = rnd.uniform(0.4, 0.7)
        self.phase = rnd.uniform(0, 2 * math.pi)
        self.wave_amp = rnd.uniform(8, 18)
        self.brightness = rnd.uniform(110, 230)
        self.thickness = rnd.choice([1, 1, 2])
        
        # Categorize into three behavioral groups based on index distribution
        if 0.28 <= self.pct <= 0.72:
            self.group = "heart_shell"
        elif (0.0 <= self.pct < 0.12) or (0.88 < self.pct <= 1.0):
            self.group = "side_cascade"
        else:
            self.group = "ground_waves"  # The curly waves crawling right beneath the heart

    def points(self, t_anim):
        pts = []
        steps = 60
        tx, ty = heart_xy(self.target_t)
        
        for i in range(steps + 1):
            prog = i / steps
            
            if self.group == "heart_shell":
                # --- HEART WALL TRAJECTORY ---
                bx = ANCHOR_X + (tx - ANCHOR_X) * prog
                by = ANCHOR_Y + (ty - ANCHOR_Y) * prog
                
                # Push outward to keep the center clean
                side_push = math.sin(prog * math.pi) * (tx - ANCHOR_X) * 0.22
                bx += side_push
                
                # Fast traveling vertical ripples
                wave = self.wave_amp * math.sin(prog * 3.5 - t_anim * 6.5 + self.phase) * math.sin(prog * math.pi)
                bx += wave
                
            elif self.group == "side_cascade":
                # --- WIDE SIDE CURTAIN WAVES ---
                side_sign = -1.0 if self.pct < 0.5 else 1.0
                mid_x = ANCHOR_X + side_sign * (WIDTH * 0.26)
                mid_y = HEART_CY + 50
                
                end_x = ANCHOR_X + side_sign * (WIDTH * 0.55) * (0.2 + 0.8 * prog)
                end_y = ANCHOR_Y - 50 + 40 * math.sin(prog * 2.0 + t_anim * 2.5 + self.phase)
                
                if prog < 0.35:
                    sub_p = prog / 0.35
                    bx = ANCHOR_X + (mid_x - ANCHOR_X) * sub_p
                    by = ANCHOR_Y + (mid_y - ANCHOR_Y) * sub_p
                else:
                    sub_p = (prog - 0.35) / 0.65
                    bx = mid_x + (end_x - mid_x) * sub_p
                    by = mid_y + (end_y - mid_y) * sub_p
                    
                by += 15 * math.sin(bx * 0.025 - t_anim * 4.5 + self.phase) * prog
                
            else:
                # --- GROUND BED WAVES (UNDERNEATH HEART) ---
                # These loop flatly along the floor, generating curly rolling waves underneath
                side_sign = -1.0 if self.pct < 0.5 else 1.0
                
                # Span horizontally across the baseline area directly below the tip
                bx = ANCHOR_X + side_sign * (WIDTH * 0.45) * prog
                
                # Keep it tightly restricted to the bottom sector
                base_y = ANCHOR_Y - 20
                
                # Intense harmonic frequency oscillation to create compressed 'curly' ripples
                curl_freq = 0.04
                rolling_wave = 22 * math.sin(bx * curl_freq - t_anim * 5.0 + self.phase)
                
                # Dampen near the center anchor so they emerge gracefully
                fade_in = math.sin(prog * math.pi * 0.5)
                by = base_y + rolling_wave * fade_in
                
            pts.append((bx, by))
            
        return pts

class HeartSparkle:
    def __init__(self):
        self.reset()

    def reset(self):
        self.t = random.uniform(-math.pi, math.pi)
        self.jitter_x = random.uniform(-12, 12)
        self.jitter_y = random.uniform(-12, 12)
        self.r = random.uniform(1.0, 3.2)
        self.phase = random.uniform(0, 2 * math.pi)
        self.speed = random.uniform(3.0, 6.0)
        self.life = random.randint(20, 65)
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
        self.heart_sparkles = [HeartSparkle() for _ in range(450)] 
        
        self.background_stars = [
            (random.uniform(0, WIDTH), random.uniform(0, HEIGHT * 0.85),
             random.uniform(0.4, 1.5), random.uniform(0, 2 * math.pi), random.uniform(0.4, 1.5))
            for _ in range(130)
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

        # 1. Background sky stars
        for (x, y, r, phase, speed) in self.background_stars:
            b = (math.sin(t * speed + phase) + 1) / 2
            c = int(80 + 135 * b)
            rr = r * (0.7 + b * 0.3)
            d_stars.ellipse([x - rr, y - rr, x + rr, y + rr], fill=c)

        # 2. Render smooth flowing strands
        for strand in self.strands:
            pts = strand.points(t)
            if len(pts) < 2: continue
            flicker = 0.85 + 0.15 * math.sin(t * 5.0 + strand.phase)
            c = int(strand.brightness * flicker)
            d_flow.line(pts, fill=c, width=strand.thickness, joint="curve")

        # 3. Dense boundary sparkles + cross lens flares
        for sp in self.heart_sparkles:
            sp.update()
            b = sp.brightness(t)
            if b <= 0: continue
            x, y = sp.position()
            c = int(255 * b)
            r = sp.r * (0.5 + b * 0.5)
            
            d_heart.ellipse([x - r, y - r, x + r, y + r], fill=c)
            
            if b > 0.75:
                d_heart.line([x - r * 4.5, y, x + r * 4.5, y], fill=int(c * 0.65))
                d_heart.line([x, y - r * 4.5, x, y + r * 4.5], fill=int(c * 0.65))

        # ---- Dynamic Glow Layering ----
        stars_glow = ImageChops.add(stars_l, stars_l.filter(ImageFilter.GaussianBlur(1)))

        flow_core = flow_l.filter(ImageFilter.GaussianBlur(0.4))
        flow_halo = flow_l.filter(ImageFilter.GaussianBlur(3.0)).point(lambda v: int(v * 0.6))
        flow_wide = flow_l.filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * 0.22))
        flow_glow = ImageChops.add(ImageChops.add(flow_core, flow_halo), flow_wide)

        heart_core = heart_l.filter(ImageFilter.GaussianBlur(0.6))
        heart_halo = heart_l.filter(ImageFilter.GaussianBlur(4.5)).point(lambda v: int(v * 0.8))
        heart_wide = heart_l.filter(ImageFilter.GaussianBlur(20)).point(lambda v: int(v * 0.4))
        heart_glow = ImageChops.add(ImageChops.add(heart_core, heart_halo), heart_wide)

        # ---- Additive Tint Blending ----
        def tint(layer, color):
            arr = np.asarray(layer, dtype=np.float32) / 255.0
            return np.stack([arr * color[0], arr * color[1], arr * color[2]], axis=-1)

        rgb = tint(stars_glow, (230, 230, 245))
        rgb += tint(flow_glow, (212, 226, 255)) # Balanced crisp white-silver glow matrix
        rgb += tint(heart_glow, (255, 252, 250)) 

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