import tkinter as tk
import math
import random

class QuantumSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Young's Double Slit Experiment Simulator")
        self.root.configure(bg="#222222")

        # --- Physics Constants ---
        self.WAVELENGTH = 15      # Wavelength of the "light"
        self.SLIT_WIDTH = 20      # Width of a single slit (a)
        self.SLIT_DISTANCE = 80   # Distance between slits (d)
        self.SCREEN_DIST = 400    # Distance from slit to screen (L)
        
        # Simulation State
        self.particles = []       # List of active particle objects
        self.hits = []           # List of where particles landed (y-coords)
        self.is_firing = False
        self.mode = "double"      # "single" or "double"

        # --- GUI Layout ---
        self.create_controls()
        self.create_canvas()

        # Start the animation loop
        self.animate()

    def create_controls(self):
        control_frame = tk.Frame(self.root, bg="#333333", padx=10, pady=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Title
        tk.Label(control_frame, text="Quantum Lab", font=("Arial", 16, "bold"), 
                 bg="#333333", fg="white").pack(pady=(0, 20))

        # Slit Selection
        tk.Label(control_frame, text="Select Barrier:", bg="#333333", fg="#AAAAAA").pack(anchor="w")
        self.mode_var = tk.StringVar(value="double")
        
        rb1 = tk.Radiobutton(control_frame, text="Single Slit", variable=self.mode_var, 
                             value="single", command=self.reset_screen, 
                             bg="#333333", fg="white", selectcolor="#555555", activebackground="#333333")
        rb1.pack(anchor="w", pady=2)
        
        rb2 = tk.Radiobutton(control_frame, text="Double Slit", variable=self.mode_var, 
                             value="double", command=self.reset_screen,
                             bg="#333333", fg="white", selectcolor="#555555", activebackground="#333333")
        rb2.pack(anchor="w", pady=2)

        # Fire Button
        self.btn_fire = tk.Button(control_frame, text="FIRE PARTICLES", font=("Arial", 12, "bold"),
                                  bg="#00AA00", fg="white", command=self.toggle_fire)
        self.btn_fire.pack(pady=30, fill=tk.X)

        # Clear Button
        tk.Button(control_frame, text="Clear Screen", command=self.reset_screen,
                  bg="#555555", fg="white").pack(fill=tk.X)

        # Explanation Label
        self.lbl_stats = tk.Label(control_frame, text="Particles: 0", bg="#333333", fg="#00FF00")
        self.lbl_stats.pack(pady=20)

    def create_canvas(self):
        # Main simulation area
        self.width = 800
        self.height = 500
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height, bg="black")
        self.canvas.pack(side=tk.RIGHT)

        # Draw static elements
        self.draw_scene_setup()

    def draw_scene_setup(self):
        self.canvas.delete("static")
        mid_y = self.height / 2
        
        # 1. The Gun (Left)
        self.gun_x = 50
        self.canvas.create_rectangle(20, mid_y-10, 60, mid_y+10, fill="#444444", tags="static")
        self.canvas.create_rectangle(60, mid_y-3, 70, mid_y+3, fill="#FF0000", tags="static") # Barrel

        # 2. The Slit Barrier (Middle)
        self.barrier_x = 250
        barrier_color = "#4444FF"
        
        self.mode = self.mode_var.get()
        
        if self.mode == "single":
            # Draw top and bottom parts leaving one gap
            gap_size = self.SLIT_WIDTH
            self.canvas.create_line(self.barrier_x, 0, self.barrier_x, mid_y - gap_size, width=5, fill=barrier_color, tags="static")
            self.canvas.create_line(self.barrier_x, mid_y + gap_size, self.barrier_x, self.height, width=5, fill=barrier_color, tags="static")
        else:
            # Draw parts leaving two gaps
            gap_size = self.SLIT_WIDTH
            dist = self.SLIT_DISTANCE / 2
            # Top Wall
            self.canvas.create_line(self.barrier_x, 0, self.barrier_x, mid_y - dist - gap_size, width=5, fill=barrier_color, tags="static")
            # Middle Wall
            self.canvas.create_line(self.barrier_x, mid_y - dist + gap_size, self.barrier_x, mid_y + dist - gap_size, width=5, fill=barrier_color, tags="static")
            # Bottom Wall
            self.canvas.create_line(self.barrier_x, mid_y + dist + gap_size, self.barrier_x, self.height, width=5, fill=barrier_color, tags="static")

        # 3. The Screen (Right)
        self.screen_x = 750
        self.canvas.create_line(self.screen_x, 0, self.screen_x, self.height, width=2, fill="#888888", tags="static")

    def toggle_fire(self):
        self.is_firing = not self.is_firing
        if self.is_firing:
            self.btn_fire.config(text="STOP FIRING", bg="#AA0000")
        else:
            self.btn_fire.config(text="FIRE PARTICLES", bg="#00AA00")

    def reset_screen(self):
        self.hits = []
        self.particles = []
        self.canvas.delete("particle")
        self.canvas.delete("hit_marker")
        self.draw_scene_setup()
        self.lbl_stats.config(text="Particles: 0")

    # --- THE PHYSICS ENGINE ---
    def get_wave_intensity(self, y_offset):
        # Map screen position to angle theta
        # y_offset is distance from center of screen
        theta = math.atan(y_offset / self.SCREEN_DIST)
        
        # Constants for equations
        k = (2 * math.pi) / self.WAVELENGTH
        
        # 1. Diffraction (Single Slit Envelope)
        # Beta = (pi * a * sin(theta)) / lambda
        beta = (k * self.SLIT_WIDTH * math.sin(theta)) / 2
        
        if beta == 0:
            diffraction = 1.0
        else:
            diffraction = (math.sin(beta) / beta) ** 2

        if self.mode == "single":
            return diffraction

        # 2. Interference (Double Slit)
        # Alpha = (pi * d * sin(theta)) / lambda
        alpha = (k * self.SLIT_DISTANCE * math.sin(theta)) / 2
        interference = math.cos(alpha) ** 2
        
        return diffraction * interference

    def determine_landing_y(self):
        # Uses Rejection Sampling to find a random Y coordinate 
        # that fits the probability distribution of the wave function.
        while True:
            # 1. Pick a random spot on the screen (between -200 and +200 pixels from center)
            rand_y = random.uniform(-200, 200)
            
            # 2. Calculate how likely a particle is to hit there (Intensity 0.0 to 1.0)
            probability = self.get_wave_intensity(rand_y)
            
            # 3. Roll the dice
            if random.random() < probability:
                return rand_y + (self.height / 2)

    def spawn_particle(self):
        mid_y = self.height / 2
        # Start at gun
        particle = {
            "id": self.canvas.create_oval(self.gun_x, mid_y-3, self.gun_x+6, mid_y+3, fill="#00FF00", outline="", tags="particle"),
            "x": self.gun_x,
            "y": mid_y,
            "state": "traveling_to_slit",
            "target_y": 0 # Will be calculated after slit
        }
        self.particles.append(particle)

    def animate(self):
        # Spawn new particle if firing
        if self.is_firing:
            # Fire rate limiter (spawn every few frames)
            if random.random() < 0.2: 
                self.spawn_particle()

        # Update all particles
        for p in self.particles[:]:
            speed = 15 # Pixels per frame
            
            if p["state"] == "traveling_to_slit":
                self.canvas.move(p["id"], speed, 0)
                p["x"] += speed
                
                # Check if hit barrier
                if p["x"] >= self.barrier_x:
                    # Visual trick: Determine its final destiny now using Quantum Mechanics
                    p["state"] = "traveling_to_screen"
                    final_y = self.determine_landing_y()
                    p["target_y"] = final_y
                    
                    # Calculate trajectory to that final Y
                    dx = self.screen_x - self.barrier_x
                    dy = final_y - p["y"]
                    p["vx"] = speed
                    p["vy"] = speed * (dy / dx)

            elif p["state"] == "traveling_to_screen":
                self.canvas.move(p["id"], p["vx"], p["vy"])
                p["x"] += p["vx"]
                p["y"] += p["vy"]

                # Check if hit screen
                if p["x"] >= self.screen_x:
                    # Add to hits
                    self.hits.append(p["target_y"])
                    self.particles.remove(p)
                    self.canvas.delete(p["id"])
                    
                    # Draw visual marker on screen
                    # Use a translucent rectangle to build up intensity visually
                    self.canvas.create_line(self.screen_x, p["target_y"]-2, self.screen_x+10, p["target_y"]+2, 
                                          fill="#00FF00", width=1, tags="hit_marker")
                    
                    self.lbl_stats.config(text=f"Particles: {len(self.hits)}")

        # Loop
        self.root.after(20, self.animate)

# --- RUNNER ---
if __name__ == "__main__":
    root = tk.Tk()
    app = QuantumSimulator(root)
    root.mainloop()