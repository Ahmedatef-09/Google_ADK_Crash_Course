from ursina import *
import random
import math

# --- APP SETUP ---
app = Ursina()
window.title = "Dr. Quantum's Laboratory"
window.borderless = False
window.fullscreen = False

# --- CONFIGURATION ---
GUN_Z = -20
BARRIER_Z = 0
SCREEN_Z = 20
SLIT_WIDTH = 0.8
SLIT_DIST = 4.0

# --- SCENE SETUP ---
# Dark Lab Environment
Sky(color=color.rgb(10, 10, 20))
EditorCamera() # easy navigation

# 1. THE FLOOR
floor = Entity(model='plane', scale=(100, 1, 100), color=color.rgb(20, 20, 30), y=-2, texture='white_cube')

# 2. THE GUN
gun = Entity(model='cube', scale=(1, 1, 3), color=color.gray, position=(0, 0, GUN_Z))
gun_barrel = Entity(parent=gun, model='cylinder', rotation_x=90, scale=0.5, z=1, color=color.red)

# 3. THE BARRIER (We build it from parts so we can open/close gaps)
# We use 3 separate wall pieces: Left, Center, Right
barrier_left = Entity(model='cube', scale=(20, 5, 1), position=(-11, 0, BARRIER_Z), color=color.rgb(50, 50, 70))
barrier_right = Entity(model='cube', scale=(20, 5, 1), position=(11, 0, BARRIER_Z), color=color.rgb(50, 50, 70))
barrier_center = Entity(model='cube', scale=(3, 5, 1), position=(0, 0, BARRIER_Z), color=color.rgb(50, 50, 70))

# 4. THE DETECTOR SCREEN (The Histogram)
# Instead of infinite dots (laggy), we use 60 vertical bars to show accumulation
screen_wall = Entity(model='cube', scale=(40, 5, 0.5), position=(0, 0, SCREEN_Z), color=color.black)
bars = []
for i in range(60):
    # Create a bar for each "bin" on the screen
    x_pos = (i - 30) * 0.6
    bar = Entity(model='cube', position=(x_pos, -2, SCREEN_Z - 0.5), scale=(0.5, 0, 0.5), color=color.green)
    bars.append(bar)

# 5. THE OBSERVER EYE (Hidden by default)
observer_eye = Entity(model='sphere', color=color.yellow, scale=1.5, position=(5, 3, BARRIER_Z-2), visible=False)
Entity(parent=observer_eye, model='sphere', color=color.black, scale=0.4, z=0.4) # Pupil
observer_beam = Entity(model='cube', color=color.rgba(255, 255, 0, 50), scale=(0.1, 0.1, 10), position=(5, 3, BARRIER_Z), visible=False)

# --- GAME STATE ---
state = {
    'stage': 1,
    'firing': False,
    'particles': [],
    'hits': [0] * 60  # Data for the histogram
}

# --- TEXT UI ---
Text(text="CONTROLS: [1-5] Change Stage | [SPACE] Fire | [R] Reset | [Right Click+WASD] Fly", position=(-0.85, 0.45), scale=1)
stage_text = Text(text="STAGE 1: Marbles (Single Slit)", position=(-0.85, 0.4), scale=1.5, color=color.yellow)

# --- PHYSICS LOGIC ---
def get_impact_x(stage):
    # 1. Determine Physics Mode
    is_classical = (stage == 1 or stage == 2 or stage == 5)
    
    if is_classical:
        # Classical Gaussian (Two Piles)
        spread = 2.0
        if stage == 1: 
            return random.gauss(0, spread) # Center pile
        else:
            # Randomly pick Left or Right slit
            center = -SLIT_DIST/2 if random.random() < 0.5 else SLIT_DIST/2
            return random.gauss(center, spread)
    else:
        # Quantum Interference (Stripes)
        # Rejection Sampling for correct Wave Distribution
        while True:
            x = random.uniform(-15, 15)
            theta = math.atan(x / (SCREEN_Z - BARRIER_Z))
            
            # Physics Math
            lam = 2.0 # Wavelength
            alpha = (math.pi * SLIT_DIST * math.sin(theta)) / lam
            beta = (math.pi * SLIT_WIDTH * math.sin(theta)) / lam
            
            diff = 1.0 if beta == 0 else (math.sin(beta)/beta)**2
            inter = math.cos(alpha)**2
            
            prob = diff * inter # Double Slit Pattern
            
            if random.random() < prob:
                return x

# --- UPDATE LOOP ---
def update():
    # 1. SPAWN PARTICLES
    if state['firing']:
        rate = 1 if state['stage'] <= 2 else 5 # Faster for electrons
        for _ in range(rate):
            spawn_particle()

    # 2. MOVE PARTICLES
    for p in state['particles']:
        p.z += 10 * time.dt # Move forward
        
        # Check if passed barrier
        if not p.passed_barrier and p.z > BARRIER_Z:
            p.passed_barrier = True
            
            # Visual: Snap to nearest slit to look realistic
            if state['stage'] == 1:
                p.x = 0 # Center slit
            else:
                # Snap to left or right slit based on current X
                if p.x < 0: p.x = -SLIT_DIST/2
                else: p.x = SLIT_DIST/2

            # OBSERVER EFFECT: Turn Red if observed
            if state['stage'] == 5:
                p.color = color.red
                
            # CALCULATE DESTINY
            # We calculate the final X now and interpolate towards it
            p.target_x = get_impact_x(state['stage'])
            
            # Set velocity vector to hit that target
            dist_z = SCREEN_Z - BARRIER_Z
            dist_x = p.target_x - p.x
            p.vx = dist_x / (dist_z / (10)) # delta_x / time_to_hit

        # Move X based on calculated velocity
        if p.passed_barrier:
            p.x += p.vx * time.dt
        
        # Check Screen Hit
        if p.z >= SCREEN_Z:
            register_hit(p.x)
            destroy(p)
            state['particles'].remove(p)

def spawn_particle():
    # Visuals based on stage
    if state['stage'] <= 2:
        col = color.red # Marbles
        scl = 0.5
    elif state['stage'] == 3:
        col = color.blue # Waves
        scl = 0.8 # Big blobs
    else:
        col = color.green # Electrons
        scl = 0.3

    # Initial X spread (aiming at slits)
    start_x = random.uniform(-3, 3) 
    
    p = Entity(model='sphere', color=col, scale=scl, position=(start_x, 0, GUN_Z))
    p.passed_barrier = False
    p.vx = 0
    state['particles'].append(p)

def register_hit(x):
    # Find which bar corresponds to this X
    # Range is -15 to 15 mapped to 0 to 59
    idx = int((x + 15) * 2)
    if 0 <= idx < 60:
        # Grow the bar
        bars[idx].scale_y += 0.5
        bars[idx].y += 0.25 # Shift up so it grows from bottom
        
        # Color the bar based on height (Heatmap style)
        if bars[idx].scale_y > 10: bars[idx].color = color.white
        
        # Optional: Spawn a temporary "Splat" mark
        s = Entity(model='quad', color=bars[idx].color, position=(x, random.uniform(-2, 2), SCREEN_Z-0.6), scale=0.3)
        destroy(s, delay=1) # Remove after 1 second

# --- INPUT HANDLING ---
def input(key):
    if key == 'space':
        state['firing'] = not state['firing']
    
    if key == 'r':
        reset_sim()

    # STAGE SWITCHING
    if key in ['1', '2', '3', '4', '5']:
        set_stage(int(key))

def set_stage(num):
    state['stage'] = num
    reset_sim()
    
    # Text Update
    names = [
        "1. MARBLES (Single Slit)",
        "2. MARBLES (Double Slit)",
        "3. WAVES (Interference)",
        "4. ELECTRONS (Quantum Mystery)",
        "5. OBSERVER (Wave Collapse)"
    ]
    stage_text.text = f"STAGE {names[num-1]}"
    
    # Visual Updates
    # Barrier Logic
    if num == 1:
        # Close the side gaps? No, Single slit usually means center is open.
        # Let's just adjust the center block to close side gaps?
        # Simpler: Just rely on physics snapping.
        barrier_center.visible = False # Open center
    else:
        barrier_center.visible = True # Close center (force left/right)

    # Observer Logic
    if num == 5:
        observer_eye.visible = True
        observer_beam.visible = True
        observer_eye.look_at(barrier_center)
    else:
        observer_eye.visible = False
        observer_beam.visible = False

def reset_sim():
    for p in state['particles']: destroy(p)
    state['particles'] = []
    
    for b in bars:
        b.scale_y = 0
        b.y = -2
        b.color = color.green

# --- RUN ---
app.run()