import pygame
import random
import math
import numpy as np

# --- CONFIGURATION ---
WIDTH, HEIGHT = 1200, 600
BG_COLOR = (10, 10, 20)      # Dark Navy
LASER_COLOR = (50, 255, 100) # Bright Neon Green
WALL_COLOR = (50, 50, 70)
TEXT_COLOR = (200, 200, 200)

# Physics Constants
WAVELENGTH = 20
SLIT_DISTANCE = 120  # Distance between the two slits (Widened for visibility)
SLIT_WIDTH = 15      # Width of slit (Widened so it's easier to hit)
SCREEN_X = 1050      # Where the detector screen is
BARRIER_X = 300      # Where the slits are

# --- INIT ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Double Slit Interactive Lab (Fixed)")
font = pygame.font.SysFont("Arial", 20, bold=True)
header_font = pygame.font.SysFont("Arial", 28, bold=True)

# --- STATE ---
particles = [] 
hits = np.zeros(HEIGHT) 
mode = "double" 
is_firing = False
total_particles = 0

def get_wave_probability(y_pos_on_screen, mode):
    """ Calculates probability of landing at y_pos based on wave interference """
    y = y_pos_on_screen - (HEIGHT / 2)
    L = SCREEN_X - BARRIER_X
    if L == 0: return 0
    theta = math.atan(y / L)
    k = (2 * math.pi) / WAVELENGTH
    
    # 1. Diffraction (Envelope)
    beta = (k * SLIT_WIDTH * math.sin(theta)) / 2
    diffraction = 1.0 if beta == 0 else (math.sin(beta) / beta)**2
        
    if mode == "single":
        return diffraction
    
    # 2. Interference (Fringes)
    alpha = (k * SLIT_DISTANCE * math.sin(theta)) / 2
    interference = math.cos(alpha)**2
    
    return diffraction * interference

def spawn_particle():
    """ 
    FIXED: Fires particles in a CONE (spread) instead of a straight line.
    This ensures particles actually hit the top and bottom slits.
    """
    start_y = HEIGHT // 2
    
    # Random angle spread so the beam widens
    # We want the beam to be roughly 150px wide by the time it hits the barrier (x=300)
    # Gun is at x=50. Dist = 250.
    # We need spread of +/- 75. 
    # Slope ~ 75/250 = 0.3
    vy = random.uniform(-3.5, 3.5) # Vertical velocity spread
    
    particles.append({
        "x": 50,
        "y": start_y,
        "vx": 8,       # Horizontal speed
        "vy": vy,      # Vertical speed (The Spread)
        "state": "to_slit"
    })

def reset_simulation():
    global hits, particles, total_particles
    hits = np.zeros(HEIGHT)
    particles = []
    total_particles = 0

# --- MAIN LOOP ---
running = True
clock = pygame.time.Clock()

while running:
    # 1. Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            # Buttons
            if 50 < mx < 200 and 50 < my < 90:
                mode = "single"
                reset_simulation()
            if 220 < mx < 370 and 50 < my < 90:
                mode = "double"
                reset_simulation()
            if 50 < mx < 200 and 500 < my < 550:
                is_firing = not is_firing
            if 220 < mx < 370 and 500 < my < 550:
                reset_simulation()

    # 2. Physics Update
    if is_firing:
        # Fire MORE particles for a fuller beam look
        for _ in range(5):
            spawn_particle()
            
    for p in particles[:]:
        p["x"] += p["vx"]
        p["y"] += p["vy"]
        
        # A. Hit Barrier Logic
        if p["state"] == "to_slit" and p["x"] >= BARRIER_X:
            
            # Where are the holes?
            mid = HEIGHT // 2
            passed = False
            
            # Define slit boundaries
            if mode == "single":
                # One hole in center
                if (mid - SLIT_WIDTH) < p["y"] < (mid + SLIT_WIDTH):
                    passed = True
            else:
                # Two holes (Top and Bottom)
                top_slit_y = mid - (SLIT_DISTANCE // 2)
                bot_slit_y = mid + (SLIT_DISTANCE // 2)
                
                # Check if particle hits Top Slit OR Bottom Slit
                if (top_slit_y - SLIT_WIDTH) < p["y"] < (top_slit_y + SLIT_WIDTH):
                    passed = True
                elif (bot_slit_y - SLIT_WIDTH) < p["y"] < (bot_slit_y + SLIT_WIDTH):
                    passed = True
            
            if passed:
                p["state"] = "to_screen"
                
                # VISUAL TRICK: Snap particle to exact slit center for cleaner animation
                # (Optional, but makes the diffraction look clearer)
                if mode == "double":
                     if p["y"] < mid: p["y"] = mid - (SLIT_DISTANCE // 2)
                     else: p["y"] = mid + (SLIT_DISTANCE // 2)
                else:
                    p["y"] = mid

                # QUANTUM COLLAPSE: Pick a random destination based on wave math
                while True:
                    rand_y = random.randint(0, HEIGHT-1)
                    prob = get_wave_probability(rand_y, mode)
                    if random.random() < prob:
                        target_y = rand_y
                        break
                
                # Recalculate velocity to hit that specific target
                dx = SCREEN_X - BARRIER_X
                dy = target_y - p["y"]
                frames_needed = dx / p["vx"]
                p["vy"] = dy / frames_needed
                
            else:
                # Hit the solid wall
                particles.remove(p)
                
        # B. Hit Screen Logic
        elif p["state"] == "to_screen" and p["x"] >= SCREEN_X:
            y_idx = int(p["y"])
            if 0 <= y_idx < HEIGHT:
                hits[y_idx] += 1
                total_particles += 1
            if p in particles:
                particles.remove(p)

    # 3. Drawing
    screen.fill(BG_COLOR)

    # Draw Beam Source (Gun)
    pygame.draw.polygon(screen, (80, 80, 80), [(20, HEIGHT//2-10), (20, HEIGHT//2+10), (60, HEIGHT//2)])
    
    # Draw Barrier
    mid = HEIGHT // 2
    pygame.draw.line(screen, WALL_COLOR, (BARRIER_X, 0), (BARRIER_X, HEIGHT), 8)
    
    # Cut holes in the barrier (by drawing background color over it)
    if mode == "single":
        pygame.draw.line(screen, BG_COLOR, (BARRIER_X, mid - SLIT_WIDTH), (BARRIER_X, mid + SLIT_WIDTH), 10)
    else:
        top = mid - (SLIT_DISTANCE // 2)
        bot = mid + (SLIT_DISTANCE // 2)
        pygame.draw.line(screen, BG_COLOR, (BARRIER_X, top - SLIT_WIDTH), (BARRIER_X, top + SLIT_WIDTH), 10)
        pygame.draw.line(screen, BG_COLOR, (BARRIER_X, bot - SLIT_WIDTH), (BARRIER_X, bot + SLIT_WIDTH), 10)

    # Draw Particles
    for p in particles:
        # If past barrier, make them brighter/white to show they are "interfering"
        col = (200, 255, 200) if p["state"] == "to_screen" else LASER_COLOR
        pygame.draw.circle(screen, col, (int(p["x"]), int(p["y"])), 2)

    # Draw Detector Screen
    pygame.draw.line(screen, (100, 100, 100), (SCREEN_X, 0), (SCREEN_X, HEIGHT), 2)
    
    # Draw Accumulation Graph (The Result)
    max_val = np.max(hits)
    if max_val == 0: max_val = 1
    
    for y in range(0, HEIGHT, 2):
        if hits[y] > 0:
            bar_len = (hits[y] / max_val) * 120
            # Color gradient: Green -> White
            green = min(255, 100 + hits[y]*5)
            pygame.draw.line(screen, (0, green, 0), (SCREEN_X, y), (SCREEN_X + bar_len, y), 2)

    # UI Overlay
    screen.blit(header_font.render(f"MODE: {mode.upper()}", True, (255, 255, 255)), (WIDTH//2 - 80, 20))
    screen.blit(font.render(f"Photons: {total_particles}", True, LASER_COLOR), (WIDTH//2 - 50, 60))

    # Button Graphics
    btn_s_col = (0, 150, 0) if mode == "single" else (50, 50, 50)
    btn_d_col = (0, 150, 0) if mode == "double" else (50, 50, 50)
    
    pygame.draw.rect(screen, btn_s_col, (50, 50, 120, 40), border_radius=5)
    screen.blit(font.render("Single Slit", True, (255,255,255)), (60, 60))
    
    pygame.draw.rect(screen, btn_d_col, (200, 50, 120, 40), border_radius=5)
    screen.blit(font.render("Double Slit", True, (255,255,255)), (210, 60))

    # Controls
    fire_col = (200, 50, 50) if is_firing else (0, 150, 100)
    pygame.draw.rect(screen, fire_col, (50, 500, 150, 50), border_radius=10)
    screen.blit(header_font.render("STOP" if is_firing else "FIRE", True, (255,255,255)), (90, 510))
    
    pygame.draw.rect(screen, (80, 80, 80), (220, 500, 150, 50), border_radius=10)
    screen.blit(header_font.render("CLEAR", True, (255,255,255)), (255, 510))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()