import tkinter

from Field import Field
from CommandParser import Parser

from tkinter import *
import random


CYCLE='0123456789ABCDEF'

class Root(Tk):
    def __init__(self):
        super().__init__()
        self.state("zoomed")
        self.field = Field()
        self.canvas = Canvas(self, highlightbackground="black", highlightthickness=2)
        self.canvas.pack()
        canvas_size = min(self.winfo_height(), self.winfo_height())
        self.canvas.place_configure(x=0, y=0, width=canvas_size, height=canvas_size)
        self.min_tiles = 5
        self.max_tiles = len(self.field.field)
        self.map_size = 10
        self.delay = 20
        self.bind("<Configure>", self.update_map)
        self.bind('<+>', self.zoom_in)
        self.bind('<minus>', self.zoom_out)
        self.bind('<w>', self.handle_w)
        self.bind('<a>', self.handle_a)
        self.bind('<s>', self.handle_s)
        self.bind('<d>', self.handle_d)

        self.run_button = Button(self, text="Start", command=self.start)
        self.run_button.place_configure(x=canvas_size+50, y=50, height = 20, width = 50)
        self.stop_button = Button(self, text="Stop", command=self.stop)
        self.stop_button.place_configure(x=canvas_size + 50, y=100, height=20, width=50)
        self.step_button = Button(self, text="Step", command=self.step)
        self.step_button.place_configure(x=canvas_size + 50, y=150, height=20, width=50)

        self.reset_button = Button(self, text="Reset", command=self.reset)
        self.reset_button.place_configure(x=canvas_size + 50, y=200, height=20, width=50)

        self.export_button = Button(self, text="Export", command=self.export_file)
        self.export_button.place_configure(x=canvas_size + 30, y=canvas_size-50, height=20, width=70)

        self.export_field = Text(self,  height=20, width=50)
        self.export_field.place_configure(x=canvas_size + 120, y=canvas_size-50, height=20, width=200)

        self.import_button = Button(self, text="Import", command=self.import_file)
        self.import_button.place_configure(x=canvas_size + 30, y=canvas_size - 100, height=20, width=70)

        self.import_field = Text(self, height=20, width=50)
        self.import_field.place_configure(x=canvas_size + 120, y=canvas_size - 100, height=20, width=200)

        self.load_button = Button(self, text="Load", command=self.load_code)
        self.load_button.place_configure(x=canvas_size + 30, y=canvas_size - 150, height=20, width=70)

        self.load_field = Text(self, height=20, width=50)
        self.load_field.place_configure(x=canvas_size + 120, y=canvas_size - 150, height=20, width=200)

        self.error_field = Text(self, state='disabled')
        self.error_field.place_configure(x=canvas_size + 120, y=canvas_size - 300, height=100, width=200)

        self.is_running = False
        self.tiles = []
        self.center_x, self.center_y = self.field.bot.position

        self.current_backup = None


    def report_error(self, e):
        self.error_field.configure(state=NORMAL)
        self.error_field.delete('1.0', END)
        self.error_field.insert('1.0', e)
        self.error_field.configure(state=DISABLED)


    def copy(self):
        return (self.field.copy(), self.center_x, self.center_y, self.field.bot.position[0], self.field.bot.position[1])



    def tick(self):
        if self.current_backup == None:
            self.current_backup = self.copy()

        try:
            self.field.tick()
        except Exception as e:
            self.report_error(e)
            self.is_running = False
            return
        self.update_map()
        if self.is_running:
            self.after(self.delay, self.tick)


    def update_map(self, event=None):

        self.canvas.update_idletasks()
        if self.is_running:
            self.center_x = self.field.bot.position[0]
            self.center_y = self.field.bot.position[1]

        self.draw_tiles()

    def zoom_in(self, event=None):
        if (self.focus_get() in [self.load_field, self.export_field, self.import_field]):
            return

        self.map_size -= 2

        if self.map_size < self.min_tiles:
            self.map_size = self.min_tiles

        self.tiles = []

        self.update_map()

    def zoom_out(self, event=None):
        if (self.focus_get() in [self.load_field, self.export_field, self.import_field]):
            return
        self.map_size += 2

        if self.map_size > self.max_tiles:
            self.map_size = self.max_tiles

        self.tiles = []

        self.update_map()

    def start(self):
        self.is_running = True
        self.tick()

    def stop(self):
        self.is_running = False

    def step(self):
        self.tick()

    def reset(self):
        if self.current_backup:
            self.field = self.current_backup[0]
            self.center_x = self.current_backup[1]
            self.center_y = self.current_backup[2]
            self.field.bot.position[0] = self.current_backup[3]
            self.field.bot.position[1] = self.current_backup[4]
            self.update_map()
            self.current_backup = None

    def export_file(self):
        try:
            with open(self.export_field.get('1.0', 'end').strip(), 'w') as file:
                for i in range(len(self.field.field )):
                    l = self.field.field[i]
                    print(*[l[j] if (j != self.field.bot.position[1] or i != self.field.bot.position[0]) else 'P' for j in range(len(l))],
                        file=file, sep='')
                #print(self.field.bot.position[0], self.field.bot.position[1], file=file)
            self.export_button.focus_set()
        except Exception as e:
            self.report_error(e)

    def import_file(self):
        try:
            with open(self.import_field.get('1.0', 'end').strip(), 'r') as file:
                lines = file.readlines()
                for i in range(len(lines)):
                    line = lines[i]
                    for j in range(len(lines)):
                        if line[j] =='P':
                            self.field.bot.position[0] = j
                            self.field.bot.position[1] = i
                            self.field.field[i][j] = '1'
                        else:
                            self.field.field[i][j] = line[j]

            self.update_map()
            self.import_button.focus_set()
        except Exception as e:
            self.report_error(e)



    def load_code(self):
        try:
            with open(self.load_field.get('1.0', 'end').strip(), 'r') as file:
                self.field.parser = Parser(file.read())
            self.load_button.focus_set()
        except Exception as e:
            self.report_error(e)



    def draw_tiles(self):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        size = min(canvas_width, canvas_height)
        tile_width = size / self.map_size
        tile_height = size / self.map_size
        half = self.map_size//2

        self.canvas.delete("tile")
        self.canvas.delete('bot')

        for sy in range(self.map_size):

            for sx in range(self.map_size):
                tx = sx * tile_width
                ty = sy * tile_height
                wx = self.center_x - half + sx
                wy = self.center_y - half + sy
                color = ''
                if 0 <= wx < self.max_tiles and 0 <= wy < self.max_tiles:
                    match self.field.field[wy][wx]:
                        case '0':
                            color = 'black'
                        case '1':
                            color = 'white'

                        case '2':
                            color ='dark green'
                        case '3':
                            color='dark cyan'
                        case '4':
                            color='dark red'
                        case '5':
                            color='purple'
                        case '6':
                            color='gold'
                        case '7':
                            color='gray'
                        case '8':
                            color='dark gray'
                        case '9':
                            color='blue'
                        case 'A':
                            color='green'
                        case 'B':
                            color='cyan'
                        case 'C':
                            color ='red'
                        case 'D':
                            color ='pink'
                        case 'E':
                            color='yellow'
                        case 'F':
                            color='dark blue'

                else:
                    color = "gold"

                id = self.canvas.create_rectangle(
                    tx, ty,
                    tx + tile_width, ty + tile_height,
                    tags="tile",
                    fill=color,
                    outline=color
                )
                self.canvas.tag_bind(id, '<Button-1>', self.handle_left_click)
                self.canvas.tag_bind(id, '<Button-2>', self.handle_right_click)


        botx = (self.field.bot.position[0] + half - self.center_x)*tile_width
        boty = (self.field.bot.position[1] + half - self.center_y)*tile_height
        self.canvas.create_rectangle(botx+5, boty+5,botx+tile_width-5, boty+tile_height-5, fill='lime', tags='bot')


    def handle_left_click(self, event):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        size = min(canvas_width, canvas_height)
        tile_width = size / self.map_size
        tile_height = size / self.map_size
        half = self.map_size//2
        j, i = self.center_x - half + int(event.x//tile_width), self.center_y - half + int(event.y//tile_height)
        #print(event.x, event.y, tile_width, half, self.center_x, self.center_y, i, j)
        self.field.field[i][j] = CYCLE[(CYCLE.find(self.field.field[i][j])+1+16)%16]
        self.update_map()

    def handle_right_click(self, event):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        size = min(canvas_width, canvas_height)
        tile_width = size / self.map_size
        tile_height = size / self.map_size
        half = self.map_size // 2
        j, i = self.center_x - half + int(event.x // tile_width), self.center_y - half + int(event.y // tile_height)
        self.field.field[i][j] = CYCLE[(CYCLE.find(self.field.field[i][j]) - 1 + 16) % 16]
        self.update_map()

    def handle_w(self, event=None):
        if (self.focus_get() in [self.load_field, self.export_field, self.import_field]):
            return
        self.center_y-=1
        self.update_map()
    def handle_s(self, event=None):
        if (self.focus_get() in [self.load_field, self.export_field, self.import_field]):
            return
        self.center_y+=1
        self.update_map()
    def handle_a(self, event=None):
        if (self.focus_get() in [self.load_field, self.export_field, self.import_field]):
            return
        self.center_x-=1
        self.update_map()
    def handle_d(self, event=None):
        if (self.focus_get() in [self.load_field, self.export_field, self.import_field]):
            return
        self.center_x+=1
        self.update_map()





if __name__ == "__main__":
    root = Root()
    root.mainloop()