"""
File containing all code for Langton's Ant app.
"""

import tkinter as tk
from tkinter import ttk

# Most colours from clrs.cc
RED = "#FF4136"
BLUE = "#0074D9"
PURPLE = "#B10DC9"
GREEN = "#2ECC40"
YELLOW = "#FFDC00"
BLACK = "#111111"
WHITE = "#FFFFFF"
GREENACTIVE = "#228B22"
REDACTIVE = "#8B0000"
BLUEACTIVE = "#27408B"

NORTH = 0
EAST = 1
SOUTH = 2
WEST = 3

def turn_clockwise(direction):
    """
    Given a direction, returns the next direction around clockwise.
    """
    return (direction + 1) % 4

def turn_anticlockwise(direction):
    """
    Given a direction, returns the next direction around anticlockwise.
    """
    return (direction - 1) % 4

class Application:
    """
    Class that runs the app - includes ant area and control area.
    """
    def __init__(self, master, width, height):
        self.ant_control = AntControl(master, width, height)
        self.controls = Controls(master, self.ant_control)

class AntControl:
    """
    Class to control the ant and draws the board.
    """
    def __init__(self, master, max_x, max_y):
        self.master = master
        self.max_x, self.max_y = max_x, max_y
        self.width, self.height = 2*self.max_x + 1, 2*self.max_y + 1
        self.square_size = 10
        self.canvas = tk.Canvas(master,
                                height=self.height*self.square_size,
                                width=self.width*self.square_size,
                                background="white")
        self.canvas.bind("<Configure>", self.configure)
        self.canvas.pack(side=tk.LEFT, expand=1, fill=tk.BOTH)
        self.running = False
        self.direction, self.coord, self.last_callback = None, None, None
        self.delay = 100
        self.draw()
        self.reset()

    def move(self, direction, coords):
        """
        Moves the ant one step forward given a direction and coordinates.
        """
        x, y = coords
        if direction is NORTH:
            return (x, y+1)
        elif direction is EAST:
            return (x+1, y)
        elif direction is SOUTH:
            return (x, y-1)
        else:
            return (x-1, y)

    def step(self, blacks, direction, coord):
        """
        Carries out one step of the ant.
        """
        if coord in blacks:
            blacks.remove(coord)
            new_direction = turn_anticlockwise(direction)
        else:
            blacks.add(coord)
            new_direction = turn_clockwise(direction)
        new_coord = self.move(new_direction, coord)
        return new_direction, new_coord

    def check_colour(self, coord):
        """
        Given a coordinate, returns colour of that square.
        """
        if coord in self.blacks:
            return "black"
        else:
            return "white"

    def update(self):
        """
        Updates the ant and grid by one step.
        """
        self.direction, new_coord = self.step(self.blacks, self.direction, self.coord)
        if self.check_visible(self.coord):
            self.canvas.itemconfig(self.rectangles[self.coord], fill=self.check_colour(self.coord))
        if self.check_visible(new_coord):
            self.canvas.itemconfig(self.rectangles[new_coord], fill="red")
        self.coord = new_coord
        self.last_callback = self.master.after(self.delay, self.update)

    def check_visible(self, coord):
        """
        Checks a coordinate is on the displayed grid
        """
        return coord in self.rectangles

    def stop(self):
        """
        Pauses the ant.
        """
        if self.running:
            self.master.after_cancel(self.last_callback)
            self.running = False

    def start(self):
        """
        Restarts the ant when paused.
        """
        if not self.running:
            self.running = True
            self.update()

    def reset(self):
        """
        Returns the ant to the starting position and makes the grid all white.
        Doesn't change whether the ant is running.
        """
        self.coord = (0, 0)
        self.direction = NORTH
        self.blacks = set()
        self.redraw()

    def draw(self):
        """
        Sets up all rectangles displayed on screen
        """
        self.canvas.delete("all")
        self.rectangles = dict()
        total_height = self.square_size*self.height
        for i in range(-self.max_x, self.max_x+1):
            for j in range(-self.max_y, self.max_x+1):
                i_ = i + self.max_x
                j_ = j + self.max_y
                id_ = self.canvas.create_rectangle(i_*self.square_size,
                                                   total_height - (j_+1)*self.square_size,
                                                   (i_+1)*self.square_size,
                                                   total_height - j_*self.square_size,
                                                   fill="white",
                                                   outline="")
                self.rectangles[(i, j)] = id_

    def redraw(self):
        """
        Redraws the whole grid.
        Used after major change to blacks.
        """
        for i, j in self.rectangles:
            self.canvas.itemconfig(self.rectangles[(i, j)], fill=self.check_colour((i, j)))
        if self.check_visible(self.coord):
            self.canvas.itemconfig(self.rectangles[self.coord], fill="red")

    def configure(self, event):
        """
        Expand square sizes when window is enlarged.
        """
        new_size = min(event.width/self.width, event.height/self.height)
        ratio = new_size / self.square_size
        self.square_size = new_size
        for i, j in self.rectangles:
            self.canvas.scale(self.rectangles[(i, j)], 0, 0, ratio, ratio)

    def update_speed(self, value):
        """
        Update speed of animation (when slider moved)
        """
        self.delay = int(1000/float(value))

    def update_zoom(self, value):
        """
        Change zoom of canvas
        """
        self.max_x, self.max_y = int(value), int(value)
        self.width, self.height = 2*self.max_x + 1, 2*self.max_y + 1
        self.square_size = int(min(float(self.canvas.winfo_width())/self.width, 
                                   float(self.canvas.winfo_height())/self.height))
        self.draw()
        self.redraw()


class Controls:
    """
    Class for title, description and controls
    """
    def __init__(self, master, ant_control):
        self.master = master
        self.ant_control = ant_control
        self.frame = tk.Frame(self.master, background=PURPLE)
        self.frame.pack(side=tk.LEFT, fill=tk.BOTH)

        # Add title
        self.title = tk.Label(self.frame, text="Langton's Ant", font=("Courier", 30), bg=PURPLE)
        self.title.pack()

        # Add description
        description_file = open("description.txt", "r")
        self.description_frame = tk.Frame(self.frame, padx=10, pady=5, bg=BLACK)
        self.description_frame.pack(padx=10, pady=5)
        self.description_text = tk.Label(self.description_frame, text=description_file.read(),
                                         bg=BLACK, fg=WHITE, wraplength=500, justify=tk.LEFT,
                                         font=("Courier", 10))
        self.description_text.pack()
        description_file.close()

        # Make stop, start, reset control buttons
        self.control_frame = tk.Frame(self.frame, padx=10, pady=5, bg=BLACK)
        self.control_frame.pack(padx=10, pady=5)
        self.control_label = tk.Label(self.control_frame, text="Controls",
                                      bg=BLACK, fg=WHITE, font=("Courier", 12))
        self.control_label.pack()
        buttons = [("START", self.ant_control.start, GREEN, GREENACTIVE),
                   ("STOP", self.ant_control.stop, RED, REDACTIVE),
                   ("RESET", self.ant_control.reset, BLUE, BLUEACTIVE),
                  ]
        for text, command, colour, acolour in buttons:
            button = tk.Button(self.control_frame, width=5, font=("Courier", 10), text=text,
                               command=command, background=colour, activebackground=acolour)
            button.pack(side=tk.LEFT, padx=1)

        # Make option buttons including speed
        self.option_frame = tk.Frame(self.frame, padx=10, pady=5, bg=BLACK)
        self.option_frame.pack(padx=10, pady=5)
        self.option_label = tk.Label(self.option_frame, text="Options",
                                     bg=BLACK, fg=WHITE, font=("Courier", 12))
        self.option_label.pack()

        options = [("Speed", BLUE, BLUEACTIVE, self.ant_control.update_speed, 1, 500, 250),
                   ("Zoom", RED, REDACTIVE, self.ant_control.update_zoom, 1, 50, 25)]
        for label, colour, acolour, callback, from_, to, initial  in options:
            option_scale = tk.Scale(self.option_frame, bg=colour, orient=tk.HORIZONTAL,
                                    bd=1, label=label, fg=WHITE, font=("Courier", 10),
                                    showvalue=0, length=200, activebackground=acolour,
                                    from_=from_, to=to, command=callback, highlightthickness=0)
            option_scale.set(initial)
            option_scale.pack(pady=2)


root = tk.Tk()
app = Application(root, 25, 25)
root.mainloop()
