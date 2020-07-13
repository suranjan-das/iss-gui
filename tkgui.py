import matplotlib
matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import matplotlib.animation as Animation

import tkinter as tk
from tkinter import ttk
from tkcalendar import *

import datetime
import coord

# get iss path coordinates
x = coord.get_path(resolution=.3)
# save longitude and latitude in separate list variable
lons, lats = x[0], x[1]

fig = Figure()
ax = fig.add_subplot(111)
fig.subplots_adjust(left=.01, bottom=0, right=.99,
                    top=.93, wspace=0, hspace=0)

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
    ax.set_title("ISS live position")
    time = datetime.datetime.utcnow()
    t = coord.get_position(time)
    index = coord.find_index(t, lons)
    draw_map(index, t, time)
    ax.legend(bbox_to_anchor=(0, 1.02, 1, .102), loc=3,
              ncol=2, borderaxespad=0)

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
    map.plot(x, y, marker=None, color='crimson', label="past")

    p, q = map(lonB, latB)
    map.plot(p, q, marker=None, color='navy', label="future")


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

        menubar = tk.Menu(container)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="ISS live graph",
                             command=lambda: self.show_frame(StartPage))
        filemenu.add_command(label="ISS pass info",
                             command=lambda: self.show_frame(PageOne))
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=quit)
        menubar.add_cascade(label="Options", menu=filemenu)

        tk.Tk.config(self, menu=menubar)

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
        # label = tk.Label(self, text="Home Page")
        # label.pack()

        # button1 = ttk.Button(self, text="ISS live",
        #                      command=lambda: controller.show_frame(PageOne))
        # button1.pack()

        # a tk.DrawingArea
        canvas = FigureCanvasTkAgg(fig, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)


class PageOne(tk.Frame):

    cal_open = False

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)

        self.columnconfigure(0, weight=1, uniform='x')
        self.columnconfigure(1, weight=2, uniform='x')

        self.rowconfigure(0, weight=1)

        frame1 = tk.Frame(self, parent)
        frame1.grid(row=0, column=0, sticky="nsew")

        frame1.columnconfigure((0, 2, 3, 5), weight=1, uniform='y')
        frame1.columnconfigure((1, 4), weight=2, uniform='y')

        lbl_loc = ttk.Label(frame1, text='Enter location')
        lbl_loc.grid(row=0, columnspan=4, pady=10)

        lbl_lat = ttk.Label(frame1, text='Lat: ')
        lbl_lat.grid(row=1, column=0, padx=5, sticky='w')

        entry_lat = ttk.Entry(frame1)
        entry_lat.grid(row=1, column=1, padx=10, pady=5)

        lbl_degN = ttk.Label(frame1, text='\u00B0N')
        lbl_degN.grid(row=1, column=2, padx=5, sticky='w')

        lbl_lon = ttk.Label(frame1, text='Long: ')
        lbl_lon.grid(row=1, column=3, sticky='w')

        entry_lon = ttk.Entry(frame1)
        entry_lon.grid(row=1, column=4, padx=10, pady=5)

        lbl_degE = ttk.Label(frame1, text='\u00B0E')
        lbl_degE.grid(row=1, column=5, sticky='w')

        lbl_hzn = ttk.Label(frame1, text='Set Horizon: ')
        lbl_hzn.grid(row=2, column=0, columnspan=2,
                     padx=5, pady=10, sticky='w')

        entry_hzn = ttk.Entry(frame1)
        entry_hzn.grid(row=2, column=2, sticky='e')

        lbl_hzn_deg = ttk.Label(frame1, text='\u00B0')
        lbl_hzn_deg.grid(row=2, column=3, sticky='w')

        lbl_type = ttk.Label(frame1, text='Pass type: ')
        lbl_type.grid(row=3, column=0, columnspan=2,
                      padx=5, pady=10, sticky='w')

        def create_type_dropdown():
            pass_choice = ttk.Combobox(frame1, width=10)
            pass_choice['values'] = ['Visible', 'Daylight', 'Both']
            pass_choice.grid(row=3, column=2, columnspan=2)
            pass_choice.current(0)

        create_type_dropdown()

        lbl_dur = ttk.Label(frame1, text='Duration: ')
        lbl_dur.grid(row=4, column=0, padx=5, pady=10,
                     columnspan=2, sticky='w')

        entry_dur = ttk.Entry(frame1)
        entry_dur.grid(row=4, column=2)

        lbl_days = ttk.Label(frame1, text='days')
        lbl_days.grid(row=4, column=3, padx=5, sticky='e')

        def grab_date():
            def cal_date():
                print('last_date="{}"'.format(cal.selection_get()))
                self.cal_open = False
                cal_frame.destroy()

            def cal_exit():
                print("exit pressed")
                self.cal_open = False
                cal_frame.destroy()

            if not self.cal_open:
                cal_frame = tk.Frame(frame1, bg="grey")
                cal_frame.grid(row=6, column=1, columnspan=4)

                cal = Calendar(cal_frame, selectmode='day',
                               year=2020, month=7, day=10)
                cal.pack()

                self.cal_open = True

                ttk.Button(cal_frame, text="ok", command=cal_date).pack(
                    side=tk.LEFT, expand=True, pady=2)
                ttk.Button(cal_frame, text="exit", command=cal_exit).pack(
                    side=tk.LEFT, expand=True, pady=2)

        lbl_strt_date = ttk.Label(frame1, text='Select start date: ')
        lbl_strt_date.grid(row=5, column=0, columnspan=2, padx=5, sticky='w')

        entry_date = ttk.Entry(frame1)
        entry_date.grid(row=5, column=2, columnspan=2)

        date_button = ttk.Button(
            frame1, text='date', command=grab_date)
        date_button.grid(row=5, column=4, padx=5, sticky='w')

        frame2 = tk.Frame(self, parent, bg='green')
        frame2.grid(row=0, column=1, sticky="nsew")


app = projIss()
app.geometry("800x440")
ani = Animation.FuncAnimation(fig, animate, interval=10000)
app.mainloop()
