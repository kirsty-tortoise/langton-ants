"""
File containing all code for Langton's Ant app.
"""

import tkinter as tk

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
    def __init__(self, master, width, height):
        self.master = master
        self.width, self.height = width, height
        self.square_size = 10
        self.canvas = tk.Canvas(master,
                                height=self.height*self.square_size,
                                width=self.width*self.square_size)
        self.canvas.pack(side=tk.LEFT)
        self.running = False
        self.direction, self.coord, self.last_callback = None, None, None
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
        self.last_callback = self.master.after(10, self.update)

    def check_visible(self, coord):
        """
        Checks a coordinate is on the displayed grid
        """
        return 0 <= coord[0] < self.width and 0 <= coord[1] < self.height

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
        self.coord = (self.width//2, self.height//2)
        self.direction = NORTH
        self.blacks = set()
        self.redraw()

    def draw(self):
        """
        Sets up all rectangles displayed on screen
        """
        self.rectangles = dict()
        total_height = self.square_size*self.height
        for i in range(self.width):
            for j in range(self.height):
                id_ = self.canvas.create_rectangle(i*self.square_size,
                                                   total_height - (j+1)*self.square_size,
                                                   (i+1)*self.square_size,
                                                   total_height - j*self.square_size,
                                                   fill="white",
                                                   outline="")
                self.rectangles[(i, j)] = id_

    def redraw(self):
        """
        Redraws the whole grid.
        Used after major change to blacks.
        """
        for i in range(self.width):
            for j in range(self.height):
                self.canvas.itemconfig(self.rectangles[(i, j)], fill=self.check_colour((i, j)))
        self.canvas.itemconfig(self.rectangles[self.coord], fill="red")


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

root = tk.Tk()
app = Application(root, 50, 50)
root.mainloop()
