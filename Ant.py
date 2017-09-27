import tkinter as tk

NORTH = 0
EAST = 1
SOUTH = 2
WEST = 3

def turn_clockwise(direction):
    return (direction + 1) % 4

def turn_anticlockwise(direction):
    return (direction - 1) % 4

class Application:
    def __init__(self, master, width, height):
        self.ant_control = AntControl(master, width, height)

class AntControl:
    def __init__(self, master, width, height):
        self.master = master
        self.width, self.height = width, height
        self.square_size = 10
        self.canvas = tk.Canvas(master,
                                height=self.height*self.square_size,
                                width=self.width*self.square_size)
        self.canvas.pack(side=tk.LEFT)
        rectangles = dict()
        total_height = self.square_size*height
        for i in range(width):
            for j in range(height):
                id_ = self.canvas.create_rectangle(i*self.square_size,
                                                   total_height - (j+1)*self.square_size,
                                                   (i+1)*self.square_size,
                                                   total_height - j*self.square_size,
                                                   fill="white",
                                                   outline="")
                rectangles[(i, j)] = id_
        self.rectangles = rectangles
        self.coord = (width//2, height//2)
        self.direction = NORTH
        self.blacks = set()
        self.update()

    def move(self, direction, coords):
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
        if coord in blacks:
            blacks.remove(coord)
            new_direction = turn_anticlockwise(direction)
        else:
            blacks.add(coord)
            new_direction = turn_clockwise(direction)
        new_coord = self.move(new_direction, coord)
        return new_direction, new_coord

    def check_colour(self, coord):
        if coord in self.blacks:
            return "black"
        else:
            return "white"

    def update(self):
        self.direction, new_coord = self.step(self.blacks, self.direction, self.coord)
        if self.check_visible(self.coord):
            self.canvas.itemconfig(self.rectangles[self.coord], fill=self.check_colour(self.coord))
        if self.check_visible(new_coord):
            self.canvas.itemconfig(self.rectangles[new_coord], fill="red")
        self.coord = new_coord
        self.master.after(10, self.update)

    def check_visible(self, coord):
        return 0 <= coord[0] < self.width and 0 <= coord[1] < self.height

class Controls:
    pass

root = tk.Tk()
app = Application(root, 50, 50)
root.mainloop()
