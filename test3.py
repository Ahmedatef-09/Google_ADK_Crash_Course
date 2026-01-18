import pygame
import random
import math
import numpy as np

# --- CONFIGURATION ---
WIDTH, HEIGHT = 1200, 600
BG_COLOR = (20, 20, 30)       
TEXT_COLOR = (200, 200, 200)

# Colors
TENNIS_COLOR = (220, 255, 0)  
WAVE_COLOR = (0, 200, 255)    
ELECTRON_COLOR = (100, 255, 100) 
OBSERVER_COLOR = (255, 50, 50) 
GUN_COLOR = (100, 100, 100)

# Physics Constants
WAVELENGTH = 25
SLIT_DISTANCE = 120   # Distance between top and bottom slits
SLIT_WIDTH = 15
SCREEN_X = 1050
BARRIER_X = 300       # Barrier position
GUN_X = 50

# --- INIT ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Physics Minute: Ultimate Slit Simulator")
font = pygame.font.SysFont("Arial", 16, bold=True)
header_font = pygame.font.SysFont("Arial", 22, bold=True)
big_font = pygame.font.SysFont("Arial", 28, bold=True)

# --- STATE ---
screen_intensity = np.zeros(HEIGHT)
particles = []
particle_mode = "quantum" # 'classical', 'wave', 'quantum'
slit_mode = "double"      # 'single', 'double'
observer_on = False
is_firing = False

def get_probability(y_pos):
    """
    Calculates impact probability based on Slit Mode + Particle Mode.
    """
    y = y_pos - (HEIGHT / 2)
    
    # --- 1. CLASSICAL / OBSERVED QUANTUM (Gaussian Piles) ---
    if particle_mode == "classical" or (particle_mode == "quantum" and observer_on):
        spread_factor = 2000
        if slit_mode == "single":
            # One pile in center
            return math.exp(-(y**2) / (2 * spread_factor))
        else:
            # Two piles (Top and Bottom)
            top_y = -(SLIT_DISTANCE / 2)
            bot_y = (SLIT_DISTANCE / 2)
            prob_top = math.exp(-((y - top_y)**2) / (2 * spread_factor))
            prob_bot = math.exp(-((y - bot_y)**2) / (2 * spread_factor))
            return prob_top + prob_bot

    # --- 2. WAVE / UN-OBSERVED QUANTUM (Interference Math) ---
    else:
        L = SCREEN_X - BARRIER_X
        if L == 0: return 0
        theta = math.atan(y / L)
        k = (2 * math.pi) / WAVELENGTH
        
        # Diffraction (Single Slit Envelope)
        beta = (k * SLIT_WIDTH * math.sin(theta)) / 2
        diffraction = 1.0 if beta == 0 else (math.sin(beta) / beta)**2
        
        if slit_mode == "single":
            return diffraction
        else:
            # Interference (Double Slit Stripes)
            alpha = (k * SLIT_DISTANCE * math.sin(theta)) / 2
            interference = math.cos(alpha)**2
            return diffraction * interference

def spawn_particle():
    # Visual Source Logic
    start_y = HEIGHT // 2
    
    # 1. Classical (Tennis Ball Cannon - Messy)
    if particle_mode == "classical":
        vy = random.uniform(-6, 6)
        col, rad = TENNIS_COLOR, 5
        
    # 2. Quantum (Electron Gun - Precise)
    elif particle_mode == "quantum":
        vy = random.uniform(-4, 4)
        col, rad = ELECTRON_COLOR, 3
        
    particles.append({
        "x": GUN_X + 40, "y": start_y, # Start at tip of gun
        "vx": 10, "vy": vy,
        "state": "to_slit",
        "color": col, "radius": rad
    })

def reset_simulation():
    global screen_intensity, particles
    screen_intensity = np.zeros(HEIGHT)
    particles = []

# --- MAIN LOOP ---
running = True
clock = pygame.time.Clock()

while running:
    # 1. EVENT HANDLING
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            
            # MODE BUTTONS (Top Row)
            if 30 < mx < 160 and 50 < my < 90:
                particle_mode = "classical"; observer_on = False; reset_simulation()
            if 170 < mx < 300 and 50 < my < 90:
                particle_mode = "wave"; observer_on = False; reset_simulation()
            if 310 < mx < 440 and 50 < my < 90:
                particle_mode = "quantum"; reset_simulation()
            
            # SLIT BUTTONS (Second Row)
            if 30 < mx < 160 and 110 < my < 150:
                slit_mode = "single"; reset_simulation()
            if 170 < mx < 300 and 110 < my < 150:
                slit_mode = "double"; reset_simulation()

            # OBSERVER (Only Quantum)
            if particle_mode == "quantum" and 310 < mx < 440 and 110 < my < 150:
                observer_on = not observer_on; reset_simulation()

            # FIRE CONTROLS (Bottom)
            if 50 < mx < 200 and 500 < my < 550: is_firing = not is_firing
            if 220 < mx < 370 and 500 < my < 550: reset_simulation()

    # 2. PHYSICS ENGINE
    
    # Spawn Particles
    if is_firing and particle_mode != "wave":
        rate = 2 if particle_mode == "classical" else 10
        for _ in range(rate): spawn_particle()

    # Move Particles
    for p in particles[:]:
        p["x"] += p["vx"]
        p["y"] += p["vy"]
        
        # A. Hit Barrier
        if p["state"] == "to_slit" and p["x"] >= BARRIER_X:
            mid = HEIGHT // 2
            passed = False
            
            # Define Slit Geometry
            if slit_mode == "single":
                # One center hole
                if (mid - SLIT_WIDTH) < p["y"] < (mid + SLIT_WIDTH): 
                    passed = True; p["y"] = mid # Snap to center
            else:
                # Two holes
                top = mid - (SLIT_DISTANCE // 2)
                bot = mid + (SLIT_DISTANCE // 2)
                if (top - SLIT_WIDTH) < p["y"] < (top + SLIT_WIDTH): 
                    passed = True; p["y"] = top
                elif (bot - SLIT_WIDTH) < p["y"] < (bot + SLIT_WIDTH): 
                    passed = True; p["y"] = bot
            
            if passed:
                p["state"] = "to_screen"
                
                # Check for Observer Effect
                if particle_mode == "quantum" and observer_on:
                    # Measured! Behave classically (random spread)
                    p["color"] = OBSERVER_COLOR
                    # Simple angle spread logic
                    dx = SCREEN_X - BARRIER_X
                    spread = random.gauss(0, 20)
                    target_y = p["y"] + spread * 5
                    p["vy"] = (target_y - p["y"]) / (dx / p["vx"])
                
                else:
                    # Not Measured (or Classical) -> Use Probability Function
                    # Classical uses the 'get_probability' which returns Gaussian
                    # Quantum uses 'get_probability' which returns Wave Interference
                    while True:
                        ry = random.randint(0, HEIGHT-1)
                        if random.random() < get_probability(ry):
                            target_y = ry
                            break
                    dx = SCREEN_X - BARRIER_X
                    p["vy"] = (target_y - p["y"]) / (dx / p["vx"])
            else:
                particles.remove(p) # Hit wall

        # B. Hit Screen
        elif p["state"] == "to_screen" and p["x"] >= SCREEN_X:
            y_idx = int(np.clip(p["y"], 0, HEIGHT-1))
            val = 80 if particle_mode == "classical" else 30
            screen_intensity[y_idx] = min(255, screen_intensity[y_idx] + val)
            if y_idx > 0: screen_intensity[y_idx-1] = min(255, screen_intensity[y_idx-1] + val/2)
            if y_idx < HEIGHT-1: screen_intensity[y_idx+1] = min(255, screen_intensity[y_idx+1] + val/2)
            if p in particles: particles.remove(p)

    # Wave Mode Logic (Instant Math)
    if particle_mode == "wave" and is_firing:
        for y in range(HEIGHT):
            intensity = get_probability(y)
            target = intensity * 255
            current = screen_intensity[y]
            screen_intensity[y] = current + (target - current) * 0.1

    # 3. DRAWING
    screen.fill(BG_COLOR)

    # --- DRAW SOURCE (THE GUN) ---
    mid = HEIGHT // 2
    if particle_mode == "classical":
        # Tennis Cannon
        pygame.draw.circle(screen, (50, 50, 50), (GUN_X, mid + 10), 15) # Wheel
        pygame.draw.rect(screen, (80, 80, 80), (GUN_X-10, mid-15, 60, 30)) # Barrel
        pygame.draw.rect(screen, (40, 40, 40), (GUN_X+40, mid-18, 10, 36)) # Muzzle
    
    elif particle_mode == "wave":
        # Laser Pointer
        pygame.draw.rect(screen, (30, 30, 30), (GUN_X, mid-10, 50, 20)) 
        pygame.draw.line(screen, WAVE_COLOR, (GUN_X+50, mid), (GUN_X+55, mid), 3) # Emitter
        # Draw Beam Fan
        if is_firing:
            s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.polygon(s, (0, 200, 255, 30), [(GUN_X+50, mid), (BARRIER_X, mid-60), (BARRIER_X, mid+60)])
            # Fan after slits
            if slit_mode == "single":
                 pygame.draw.polygon(s, (0, 200, 255, 20), [(BARRIER_X, mid-SLIT_WIDTH), (BARRIER_X, mid+SLIT_WIDTH), (SCREEN_X, HEIGHT), (SCREEN_X, 0)])
            else:
                 top, bot = mid - (SLIT_DISTANCE//2), mid + (SLIT_DISTANCE//2)
                 pygame.draw.polygon(s, (0, 200, 255, 15), [(BARRIER_X, top), (BARRIER_X, top), (SCREEN_X, HEIGHT), (SCREEN_X, 0)])
                 pygame.draw.polygon(s, (0, 200, 255, 15), [(BARRIER_X, bot), (BARRIER_X, bot), (SCREEN_X, HEIGHT), (SCREEN_X, 0)])
            screen.blit(s, (0,0))

    elif particle_mode == "quantum":
        # Electron Gun (Sci-Fi)
        pygame.draw.polygon(screen, (60, 60, 70), [(GUN_X, mid-20), (GUN_X, mid+20), (GUN_X+50, mid)])
        pygame.draw.circle(screen, ELECTRON_COLOR, (GUN_X+20, mid), 5) # Core

    # --- DRAW BARRIER ---
    pygame.draw.line(screen, (70, 70, 80), (BARRIER_X, 0), (BARRIER_X, HEIGHT), 8)
    if slit_mode == "single":
        pygame.draw.line(screen, BG_COLOR, (BARRIER_X, mid - SLIT_WIDTH), (BARRIER_X, mid + SLIT_WIDTH), 10)
    else:
        top, bot = mid - (SLIT_DISTANCE//2), mid + (SLIT_DISTANCE//2)
        pygame.draw.line(screen, BG_COLOR, (BARRIER_X, top - SLIT_WIDTH), (BARRIER_X, top + SLIT_WIDTH), 10)
        pygame.draw.line(screen, BG_COLOR, (BARRIER_X, bot - SLIT_WIDTH), (BARRIER_X, bot + SLIT_WIDTH), 10)

    # Observer Eye
    if particle_mode == "quantum" and observer_on:
        eye_y = mid - 100
        pygame.draw.ellipse(screen, OBSERVER_COLOR, (BARRIER_X+20, eye_y, 40, 20), 2)
        pygame.draw.circle(screen, OBSERVER_COLOR, (BARRIER_X+40, eye_y+10), 5)
        screen.blit(font.render("OBSERVING", True, OBSERVER_COLOR), (BARRIER_X+10, eye_y-20))

    # --- DRAW PARTICLES ---
    if particle_mode != "wave":
        for p in particles:
            pygame.draw.circle(screen, p["color"], (int(p["x"]), int(p["y"])), p["radius"])

    # --- DRAW SCREEN (RESULT) ---
    pygame.draw.line(screen, (150, 150, 150), (SCREEN_X, 0), (SCREEN_X, HEIGHT), 2)
    for y in range(0, HEIGHT, 2):
        bright = screen_intensity[y]
        if bright > 5:
            if particle_mode == "classical": col = (bright, bright, 0)
            elif particle_mode == "wave": col = (0, bright, bright)
            else: col = (0, bright, 0) # Green for electron
            pygame.draw.line(screen, col, (SCREEN_X, y), (SCREEN_X + 100, y), 2)

    # --- UI ---
    def draw_btn(rect, text, active):
        bg = (80, 80, 100) if active else (40, 40, 50)
        border = (255, 255, 255) if active else (100, 100, 100)
        pygame.draw.rect(screen, bg, rect, border_radius=5)
        pygame.draw.rect(screen, border, rect, 2, border_radius=5)
        screen.blit(font.render(text, True, (255,255,255)), (rect[0]+10, rect[1]+10))

    # Row 1: Source
    draw_btn((30, 50, 130, 40), "Tennis Cannon", particle_mode=="classical")
    draw_btn((170, 50, 130, 40), "Laser Beam", particle_mode=="wave")
    draw_btn((310, 50, 130, 40), "Electron Gun", particle_mode=="quantum")
    
    # Row 2: Slits
    draw_btn((30, 110, 130, 40), "Single Slit", slit_mode=="single")
    draw_btn((170, 110, 130, 40), "Double Slit", slit_mode=="double")
    
    # Observer
    if particle_mode == "quantum":
        draw_btn((310, 110, 130, 40), "Eye: " + ("ON" if observer_on else "OFF"), observer_on)

    # Fire
    fire_col = (200, 50, 50) if is_firing else (0, 150, 100)
    pygame.draw.rect(screen, fire_col, (50, 500, 150, 50), border_radius=10)
    screen.blit(big_font.render("STOP" if is_firing else "FIRE", True, (255,255,255)), (90, 510))
    pygame.draw.rect(screen, (80, 80, 80), (220, 500, 150, 50), border_radius=10)
    screen.blit(big_font.render("CLEAR", True, (255,255,255)), (255, 510))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()