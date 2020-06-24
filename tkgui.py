import matplotlib
matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import matplotlib.animation as Animation

import tkinter as tk
from tkinter import ttk

import datetime
import coord

# get iss path coordinates
x = coord.get_path(resolution=.3)
# save longitude and latitude in separate list variable
lons, lats = x[0], x[1]

fig = Figure()
ax = fig.add_subplot(111)
fig.subplots_adjust(left=.01, bottom=.01, right=.99,
                    top=.99, wspace=0, hspace=0)

map = Basemap(ax=ax)


def update_path():

    global lons, lats
    # get iss path coordinates
    x = coord.get_path(resolution=.3)
    # save longitude and latitude in separate list variable
    lons, lats = x[0], x[1]


def animate(i):

    path_updated = False
    ax.clear()
    time = datetime.datetime.utcnow()
    t = coord.get_position(time)
    index = coord.find_index(t, lons)
    draw_map(index, t, time)

    if t[0] < -175 and not path_updated:
        update_path()
        path_updated = True

    if t[0] > 170 and path_updated:
        path_updated = False


def plot_trajectory(index):

    if index == -1:
        lonA, latA = [], []
        lonB, latB = [], []
    else:
        lonA, latA = lons[:index + 1], lats[:index + 1]
        lonB, latB = lons[index:], lats[index:]

    x, y = map(lonA, latA)
    map.plot(x, y, marker=None, color='crimson')

    p, q = map(lonB, latB)
    map.plot(p, q, marker=None, color='navy')


def draw_map(index, position, time):

    map.drawcoastlines()
    map.drawmapboundary(fill_color='cadetblue')
    map.fillcontinents(color='tan')
    # current time for drawing nightshade
    map.nightshade(time, alpha=0.2)
    plot_trajectory(index)

    c, d = map(position[0], position[1])
    map.plot(c, d, marker='o', color='ivory', markersize=8)


class projIss(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.iconbitmap(self, default='iss_img.ico')
        tk.Tk.wm_title(self, "ISS Tracker")

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (StartPage, PageOne):

            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()


class StartPage(tk.Frame):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Home Page")
        label.pack()

        button1 = ttk.Button(self, text="ISS live",
                             command=lambda: controller.show_frame(PageOne))
        button1.pack()


class PageOne(tk.Frame):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="ISS path")
        label.pack()

        button1 = ttk.Button(self, text="Home",
                             command=lambda: controller.show_frame(StartPage))
        button1.pack()

        # a tk.DrawingArea
        canvas = FigureCanvasTkAgg(fig, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)


app = projIss()
ani = Animation.FuncAnimation(fig, animate, interval=10000)
app.mainloop()
