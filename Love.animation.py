import pygame
import math
import random
import sys

pygame.init()
W, H = 800, 600
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("💖 Love Animation")
clock = pygame.time.Clock()

BG        = (10, 5, 15)
COLORS = [
    (255, 50, 100),
    (255, 100, 150),
    (255, 180, 200),
    (255, 80, 120),
    (220, 30, 80),
    (255, 220, 230),
    (255, 140, 170),
]

def heart_point(t, scale=1.0, cx=0, cy=0):
    x = 16 * (math.sin(t) ** 3)
    y = -(13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t))
    return cx + x * scale, cy + y * scale

def heart_points(scale=1.0, cx=0, cy=0, n=200):
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        pts.append(heart_point(t, scale, cx, cy))
    return pts

class Particle:
    def __init__(self, x=None, y=None, born_on_heart=False):
        if born_on_heart:
            t = random.uniform(0, 2 * math.pi)
            hx, hy = heart_point(t, scale=14, cx=W//2, cy=H//2)
            self.x = hx + random.uniform(-3, 3)
            self.y = hy + random.uniform(-3, 3)
        else:
            self.x = x or random.uniform(0, W)
            self.y = y or random.uniform(0, H)
        self.vx = random.uniform(-1.2, 1.2)
        self.vy = random.uniform(-2.5, -0.5)
        self.color = random.choice(COLORS)
        self.size  = random.uniform(2, 6)
        self.alpha = 255
        self.decay = random.uniform(2, 5)
        self.gravity = random.uniform(0.02, 0.06)

    def update(self):
        self.x  += self.vx
        self.vy += self.gravity
        self.y  += self.vy
        self.alpha -= self.decay
        self.size  *= 0.995

    @property
    def alive(self):
        return self.alpha > 0 and self.size > 0.5

    def draw(self, surface):
        if not self.alive:
            return
        a = max(0, min(255, int(self.alpha)))
        r, g, b = self.color
        # glow
        for s_off, a_off in [(6, 30), (4, 60), (2, 120)]:
            s = max(1, int(self.size + s_off))
            tmp = pygame.Surface((s*2, s*2), pygame.SRCALPHA)
            pygame.draw.circle(tmp, (r, g, b, min(a, a_off)), (s, s), s)
            surface.blit(tmp, (int(self.x)-s, int(self.y)-s))
        s = max(1, int(self.size))
        tmp = pygame.Surface((s*2, s*2), pygame.SRCALPHA)
        pygame.draw.circle(tmp, (r, g, b, a), (s, s), s)
        surface.blit(tmp, (int(self.x)-s, int(self.y)-s))


class FloatingHeart:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = random.uniform(50, W-50)
        self.y = H + 30
        self.scale = random.uniform(2, 6)
        self.speed = random.uniform(0.8, 2.2)
        self.color = random.choice(COLORS)
        self.alpha = random.randint(120, 220)
        self.wobble = random.uniform(0, 2*math.pi)
        self.wobble_speed = random.uniform(0.02, 0.06)
        self.wobble_amp   = random.uniform(0.5, 2.0)
        self.rot = random.uniform(-0.3, 0.3)

    def update(self):
        self.y -= self.speed
        self.wobble += self.wobble_speed
        self.x += math.sin(self.wobble) * self.wobble_amp
        self.alpha -= 0.4
        if self.y < -40 or self.alpha < 0:
            self.reset()

    def draw(self, surface):
        pts = heart_points(self.scale, self.x, self.y, n=80)
        if len(pts) < 3:
            return
        r, g, b = self.color
        a = max(0, min(255, int(self.alpha)))
        tmp = pygame.Surface((W, H), pygame.SRCALPHA)
        pygame.draw.polygon(tmp, (r, g, b, a), pts)
        surface.blit(tmp, (0, 0))


class BigHeart:
    def __init__(self):
        self.phase = 0
        self.trail = [] 

    def update(self):
        self.phase += 0.03

    def draw(self, surface):
        pulse = 1.0 + 0.08 * math.sin(self.phase * 2)
        
        pts = heart_points(scale=14*pulse, cx=W//2, cy=H//2, n=300)
        if len(pts) >= 3:
            r, g, b = 180, 20, 60
            tmp = pygame.Surface((W, H), pygame.SRCALPHA)
            pygame.draw.polygon(tmp, (r, g, b, 200), pts)
            surface.blit(tmp, (0, 0))

        for off, alpha in [(4, 30), (2, 60), (0, 180)]:
            scale_o = (14 + off) * pulse
            pts_o = heart_points(scale=scale_o, cx=W//2, cy=H//2, n=300)
            if len(pts_o) >= 3:
                tmp2 = pygame.Surface((W, H), pygame.SRCALPHA)
                pygame.draw.polygon(tmp2, (255, 80, 120, alpha), pts_o, width=2 if off==0 else 1)
                surface.blit(tmp2, (0, 0))


class Sparkle:
    def __init__(self):
        t = random.uniform(0, 2*math.pi)
        hx, hy = heart_point(t, scale=14, cx=W//2, cy=H//2)
        self.x = hx
        self.y = hy
        self.life = 1.0
        self.max_r = random.uniform(4, 10)
        self.color = random.choice(COLORS)

    def update(self):
        self.life -= 0.04

    @property
    def alive(self):
        return self.life > 0

    def draw(self, surface):
        a = int(self.life * 255)
        r_now = self.max_r * (1 - self.life)
        r, g, b = self.color
        for arm in range(4):
            angle = arm * math.pi / 2
            ex = self.x + math.cos(angle) * r_now * 2
            ey = self.y + math.sin(angle) * r_now * 2
            tmp = pygame.Surface((W, H), pygame.SRCALPHA)
            pygame.draw.line(tmp, (r, g, b, a), (int(self.x), int(self.y)), (int(ex), int(ey)), 2)
            surface.blit(tmp, (0, 0))

try:
    font_big   = pygame.font.SysFont("segoeuiemoji", 52, bold=True)
    font_small = pygame.font.SysFont("segoeuiemoji", 24)
except:
    font_big   = pygame.font.SysFont(None, 52, bold=True)
    font_small = pygame.font.SysFont(None, 24)


def draw_text_glow(surface, text, font, cx, cy, color, glow_color, alpha=255):
    for dx, dy, ga in [(-2,-2,40),( 2,-2,40),(-2, 2,40),( 2, 2,40),
                       (-4, 0,20),( 4, 0,20),( 0,-4,20),( 0, 4,20)]:
        s = font.render(text, True, glow_color)
        s.set_alpha(min(255, ga))
        rect = s.get_rect(center=(cx+dx, cy+dy))
        surface.blit(s, rect)
    s = font.render(text, True, color)
    s.set_alpha(alpha)
    rect = s.get_rect(center=(cx, cy))
    surface.blit(s, rect)

stars = [(random.randint(0,W), random.randint(0,H), random.uniform(0.5,2)) for _ in range(120)]

def draw_stars(surface, t):
    for sx, sy, sr in stars:
        a = int(128 + 80 * math.sin(t * 1.3 + sx * 0.05))
        tmp = pygame.Surface((int(sr)*2+2, int(sr)*2+2), pygame.SRCALPHA)
        pygame.draw.circle(tmp, (255, 200, 220, a), (int(sr)+1, int(sr)+1), int(sr))
        surface.blit(tmp, (sx-int(sr)-1, sy-int(sr)-1))

particles     = []
floating_hearts = [FloatingHeart() for _ in range(18)]
big_heart     = BigHeart()
sparkles      = []
tick          = 0


for i, fh in enumerate(floating_hearts):
    fh.y = random.uniform(-H, H)

print("💖  Love Animation running — press ESC or close to quit")

running = True
while running:
    dt = clock.tick(60)
    tick += 1

    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
    
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            for _ in range(30):
                particles.append(Particle(mx, my))


    if tick % 2 == 0:
        for _ in range(3):
            particles.append(Particle(born_on_heart=True))

    
    if tick % 8 == 0:
        sparkles.append(Sparkle())

    particles  = [p for p in particles if p.alive]
    sparkles   = [s for s in sparkles  if s.alive]
    for p in particles:   p.update()
    for fh in floating_hearts: fh.update()
    for s in sparkles:    s.update()
    big_heart.update()

    screen.fill(BG)
    draw_stars(screen, tick * 0.016)

    for fh in floating_hearts:
        fh.draw(screen)

    big_heart.draw(screen)

    for p in particles:
        p.draw(screen)

    for s in sparkles:
        s.draw(screen)

    text_alpha = int(200 + 55 * math.sin(tick * 0.05))
    draw_text_glow(screen, "I Love You ♥", font_big,
                   W//2, H//2,
                   (255, 220, 230), (255, 60, 100), alpha=text_alpha)
    draw_text_glow(screen, "click anywhere for more love ✨", font_small,
                   W//2, H - 30,
                   (255, 180, 200), (200, 40, 80), alpha=150)

    pygame.display.flip()

pygame.quit()
sys.exit()