import math
import random
import tkinter as tk

items = [
    "Java", "Python", "C++", "JavaScript",
    "HTML", "CSS", "React", "Typescript"
]

canvas_size = 600
radius = 240
center = (canvas_size // 2, canvas_size // 2) #center wheel
pointer_size = 18
font_name = "Helvetica" 
label_radius = int(radius * 0.62) # distance labels sit from center

slice_colors = [
    "#FF6B6B", "#4D96FF", "#6BCB77", "#FFD93D",
    "#FF8E3C", "#845EC2", "#EF5DA8", "#00C2A8"
]

min_step = 2.0 #minimum degrees per frame when almost stopped
accel_decel_factor = 0.25 #fraction of remaining spin used per frame
fps_ms = 16 #frames per second thats pretty self explanatory
full_rotations = (3, 6) #randomly do between 3 and 6 full rotations before landing

#confetti
CONFETTI_COUNT = 120
CONFETTI_COLORS = [
     "#ff595e", "#ffca3a", "#8ac926", "#1982c4", "#6a4c93", "#ff7f50", "#00c2a8"
]
CONFETTI_MIN_SPEED = 4
CONFETTI_MAX_SPEED = 10
CONFETTI_GRAVITY = 0.35
CONFETTI_DRAG = 0.995 #air resistance, 1.0 = gentle
CONFETTI_SPIN = 0.3
CONFETTI_LIFETIME = 90
CONFETTI_SIZE = (4,9)
class SpinWheelApp:
    def __init__(self, root): #__init__ sets up the self attributes
        self.root = root
        self.root.title("Spin the wheel to choose a programming language!")

        self.canvas = tk.Canvas(root, width=canvas_size, height=canvas_size, bg="white", highlightthickness=0)
        self.canvas.pack()

        self.items = items[:]
        self.n = len(self.items)
        self.seg_angle = 360.0 / self.n
        self.current_angle = 0.0
        self.spinning = False
        self.spin_remaining = 0.0
        self.target_label = None

        self.confetti = []
        self.draw_wheel() 
        self.draw_pointer() #pointer binds at 12 o'clock

        self.canvas.bind("<Button-1>", self.on_click)

        self.status_text_id = self.canvas.create_text(
            center[0], canvas_size - 30, text="Click the wheel to spin!",
            font=(font_name, 16, "bold")
        )

    def draw_wheel(self):
        self.canvas.delete("wheel") #delete previous wheel and keeps confetti and UI

        x0 = center[0] - radius
        y0 = center[1] - radius
        x1 = center[0] + radius
        y1 = center[1] + radius

        for i, label in enumerate(self.items):
            start_angle = (self.current_angle + i * self.seg_angle) % 360

            fill = slice_colors[i % len(slice_colors)]

            self.canvas.create_arc(
                x0, y0, x1, y1,
                start=start_angle, #where we start drawing
                extent=self.seg_angle, #width
                fill=fill, 
                outline="white",
                width=2,
                style=tk.PIESLICE #pie wedge
            )

            label_angle_deg = start_angle + self.seg_angle / 2.0 

            theta = math.radians(label_angle_deg) #convert to radians

            lx = center[0] + label_radius * math.cos(theta)
            ly = center[1] - label_radius * math.sin(theta) #y axis inverted

            self.canvas.create_text(
                lx, ly, text=label, font=(font_name, 12, "bold"), fill="black"
            )

            self.canvas.create_oval(
                center[0] - 10, center[1] - 10, center[0] + 10, center[1] + 10,
                fill="black", outline=""
            )

            self.draw_pointer()
            if hasattr(self, "status_text_id") and self.status_text_id:
                pass

    def draw_pointer(self):
        cx, cy = center

        #tip of the triangle
        tip_x = cx
        tip_y = cy - (radius + 10)

        #triangle base
        base_y = tip_y - pointer_size
        left_x = cx - pointer_size
        right_x = cx + pointer_size

        #draw it pointing down
        self.canvas.create_polygon(
            left_x, base_y,  # left base corner
            right_x, base_y, # right base corner
            tip_x, tip_y,    # tip of the triangle (points down)
            fill="black", outline="white", width=2
        )

    def on_click(self, event):
        if self.spinning:
            return  #ignore clicks while spinning
        
        self.spinning = True

        target_index = random.randrange(self.n) #random target segment
        self.target_label = self.items[target_index] #label to land on
        target_center_angle = (target_index * self.seg_angle + self.seg_angle / 2.0) % 360 #center angle of target segment
        desired_final_angle_mod = (90 - target_center_angle) % 360 #angle to align target with pointer
        delta_to_target = (desired_final_angle_mod - self.current_angle) % 360 #angle difference
        extra_full_turns = random.randint(full_rotations[0], full_rotations[1]) #random full rotations
        self.spin_remaining = extra_full_turns + delta_to_target #total spin angle

        self.canvas.itemconfigure(self.status_text_id, text="Spinning...")

        self.step_spin() #start spinning

    def step_spin(self):
        if self.spin_remaining <= 0:
            self.spinning = False
            self.current_angle = (self.current_angle) % 360
            self.draw_wheel()
            self.canvas.itemconfigure(self.status_text_id, text=f"Landed on: {self.target_label}, go make a project")
            self.start_confetti() #launches confetti when result appears           
            return
        
        step = max(min_step, self.spin_remaining * accel_decel_factor)
        step = min(step,self.spin_remaining)

        self.current_angle = (self.current_angle + step) % 360
        self.spin_remaining -= step
        self.draw_wheel()
        self.root.after(fps_ms, self.step_spin)

    def clear_confetti(self):
        self.canvas.delete("confetti")
        self.confetti = []

    def start_confetti(self):
        #confetti spawn from the pointer
        px = center[0]
        py = center[1]  - (radius + 10) + 8

        for _ in range(CONFETTI_COUNT):
            #random size and color
            size = random.randint(CONFETTI_SIZE[0], CONFETTI_SIZE[1])
            color = random.choice(CONFETTI_COLORS)

            #random direction and speed (downward)
            angle = random.uniform(-math.pi/2 - 0.8, -math.pi/2 + 0.8) #fan down
            speed = random.uniform(CONFETTI_MIN_SPEED, CONFETTI_MAX_SPEED)

            vx = speed * math.cos(angle)
            vy = speed * math.sin(angle) + 2  #a little extra downward kick

            #each piece is a rotated square
            omega = random.uniform(-CONFETTI_SPIN, CONFETTI_SPIN)  #angular velocity

            #create the square (we’ll keep it simple as a rectangle; rotation is visualized by wobble)
            pid = self.canvas.create_rectangle(
                px, py, px + size, py + size,
                fill=color, outline="", tags=("confetti",)
            )

            #store particle data
            self.confetti.append({
                "id": pid,
                "x": px, "y": py,
                "vx": vx, "vy": vy,
                "ay": CONFETTI_GRAVITY,
                "life": CONFETTI_LIFETIME,
                "angle": 0.0,
                "omega": omega,
                "size": size,
            })

        #kick off the animation loop
        self.animate_confetti()

    def animate_confetti(self):
        alive = []
        for p in self.confetti:
            #update velocity with gravity and drag
            p["vy"] += p["ay"]
            p["vx"] *= CONFETTI_DRAG
            p["vy"] *= CONFETTI_DRAG

            #update position
            p["x"] += p["vx"]
            p["y"] += p["vy"]

            #spin (we’ll fake rotation by nudging the rect corners based on angle)
            p["angle"] += p["omega"]

            #compute wobble offsets for a fun effect
            wobble = math.sin(p["angle"]) * 0.5 * p["size"]

            #move rectangle to new position
            x, y, s = p["x"], p["y"], p["size"]
            #apply a small horizontal wobble by shifting left/right corners
            self.canvas.coords(p["id"], x - wobble, y, x + s + wobble, y + s)

            #fade out near end of life, could change fill to lighter
            p["life"] -= 1
            if p["life"] > 0 and (0 <= x <= canvas_size) and (y <= canvas_size + 50):
                alive.append(p)
            else:
                #delete dead/out-of-bounds particles
                self.canvas.delete(p["id"])

        #keep only particles still alive
        self.confetti = alive

        #keep animating while any particles remain
        if self.confetti:
            self.root.after(fps_ms, self.animate_confetti)

if __name__ == "__main__":
    root = tk.Tk()
    app = SpinWheelApp(root)
    root.mainloop() #this creates the tk app
