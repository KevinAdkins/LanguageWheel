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

        self.draw_wheel() 
        self.draw_pointer() #pointer binds at 12 o'clock

        self.canvas.bind("<Button-1>", self.on_click)

        self.status_text_id = self.canvas.create_text(
            center[0], canvas_size - 30, text="Click the wheel to spin!",
            font=(font_name, 16, "bold")
        )

    def draw_wheel(self):
        self.canvas.delete("wheel") #delete previous wheel

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
            return
        
        step = max(min_step, self.spin_remaining * accel_decel_factor)
        step = min(step,self.spin_remaining)

        self.current_angle = (self.current_angle + step) % 360
        self.spin_remaining -= step
        self.draw_wheel()
        self.root.after(fps_ms, self.step_spin)

if __name__ == "__main__":
    root = tk.Tk()
    app = SpinWheelApp(root)
    root.mainloop() #this creates the tk app

