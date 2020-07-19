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

        def ask_confirm():
            msgbx = tk.messagebox.askquestion(
                'Exit', 'Exit Application?', icon=None)
            if msgbx == 'yes':
                self.destroy()
            else:
                pass
            # MessageWindow('Quit', 'Exit Application')

        menubar = tk.Menu(container)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="ISS live graph",
                             command=lambda: self.show_frame(StartPage))
        filemenu.add_command(label="ISS pass info",
                             command=lambda: self.show_frame(PageOne))
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=ask_confirm)
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

        style = ttk.Style(parent)
        style.configure("Placeholder.TEntry",
                        foreground="grey")

        frame1 = tk.Frame(self, parent)
        frame1.grid(row=0, column=0, sticky="nsew")

        frame1.columnconfigure((0, 2, 3, 5), weight=1, uniform='y')
        frame1.columnconfigure((1, 4), weight=2, uniform='y')

        frame1.rowconfigure(8, weight=1)

        lbl_loc = ttk.Label(frame1, text='Enter location')
        lbl_loc.grid(row=0, columnspan=4)

        lbl_lat = ttk.Label(frame1, text='Lat: ')
        lbl_lat.grid(row=1, column=0, padx=5, sticky='w')

        entry_lat = PlaceholderEntry(
            frame1, "0.000", style="TEntry", placeholder_style="Placeholder.TEntry")
        entry_lat.grid(row=1, column=1, padx=10, pady=5)

        lbl_degN = ttk.Label(frame1, text='\u00B0E')
        lbl_degN.grid(row=1, column=2, padx=5, sticky='w')

        lbl_lon = ttk.Label(frame1, text='Long: ')
        lbl_lon.grid(row=1, column=3, sticky='w')

        entry_lon = PlaceholderEntry(
            frame1, "0.000", style="TEntry", placeholder_style="Placeholder.TEntry")
        entry_lon.grid(row=1, column=4, padx=10, pady=5)

        lbl_degE = ttk.Label(frame1, text='\u00B0N')
        lbl_degE.grid(row=1, column=5, sticky='w')

        lbl_hzn = ttk.Label(frame1, text='Set Horizon: ')
        lbl_hzn.grid(row=2, column=0, columnspan=2,
                     padx=5, pady=10, sticky='w')

        entry_hzn = ttk.Entry(frame1)
        entry_hzn.grid(row=2, column=2, sticky='e')
        entry_hzn.insert("0", 10)

        lbl_hzn_deg = ttk.Label(frame1, text='\u00B0')
        lbl_hzn_deg.grid(row=2, column=3, sticky='w')

        lbl_type = ttk.Label(frame1, text='Pass type: ')
        lbl_type.grid(row=3, column=0, columnspan=2,
                      padx=5, pady=10, sticky='w')

        pass_choice = ttk.Combobox(frame1, width=10, state="readonly")
        pass_choice['values'] = ['Visible', 'Daylight', 'Both']
        pass_choice.grid(row=3, column=2, columnspan=2)
        pass_choice.current(0)

        lbl_dur = ttk.Label(frame1, text='Duration: ')
        lbl_dur.grid(row=4, column=0, padx=5, pady=10,
                     columnspan=2, sticky='w')

        entry_dur = ttk.Entry(frame1)
        entry_dur.grid(row=4, column=2)
        entry_dur.insert("0", 15)

        lbl_days = ttk.Label(frame1, text='days')
        lbl_days.grid(row=4, column=3, columnspan=2, padx=5, sticky='w')

        def grab_date():
            def cal_date():
                # print('last_date="{}"'.format(cal.selection_get()))
                dateStr = cal.get_date()
                entry_date.change_date(dateStr)
                self.cal_open = False
                cal_frame.destroy()

            def cal_exit():
                print("exit pressed")
                self.cal_open = False
                cal_frame.destroy()

            if not self.cal_open:
                cal_frame = tk.Toplevel(bg="grey")
                cal_frame.resizable(False, False)
                mindate = datetime.datetime.today() - datetime.timedelta(days=30)
                maxdate = datetime.datetime.today() + datetime.timedelta(days=30)
                cal = Calendar(cal_frame, selectmode='day', mindate=mindate,
                               maxdate=maxdate, date_pattern="yyyy/mm/dd")
                cal.pack()

                self.cal_open = True

                ttk.Button(cal_frame, text="ok", command=cal_date).pack(
                    side=tk.LEFT, expand=True, pady=2)
                ttk.Button(cal_frame, text="exit", command=cal_exit).pack(
                    side=tk.LEFT, expand=True, pady=2)
                cal_frame.grab_set()

        lbl_strt_date = ttk.Label(frame1, text='Select start date: ')
        lbl_strt_date.grid(row=5, column=0, columnspan=2, padx=5, sticky='w')

        entry_date = PlaceholderEntry(
            frame1,
            datetime.date.today().strftime("%Y/%m/%d"),
            style="TEntry",
            placeholder_style="Placeholder.TEntry"
        )
        entry_date.grid(row=5, column=2, columnspan=2)

        date_button = ttk.Button(
            frame1, text='date', command=grab_date)
        date_button.grid(row=5, column=4, padx=5, sticky='w')

        def validate_input():

            valid = True

            latitude = entry_lat.get().strip()
            longitude = entry_lon.get().strip()
            horizon = entry_hzn.get().strip()
            pass_type = pass_choice.get()
            duration = entry_dur.get().strip()
            date = entry_date.get().strip()

            msg = []
            if latitude:
                if latitude.replace("-", "", 1).replace(".", "", 1).isnumeric():
                    if float(latitude) > 180 or float(latitude) < -180:
                        valid = False
                        msg.append("*not a valid latitude value")
                        entry_lat.delete(0, 'end')
                else:
                    valid = False
                    msg.append("*latitude must be a number")
                    entry_lat.delete(0, 'end')
            else:
                msg.append("*latitude field can not be left blank")
                valid = False

            if longitude:
                if longitude.replace("-", "", 1).replace(".", "", 1).isnumeric():
                    if float(longitude) > 90 or float(longitude) < -90:
                        valid = False
                        msg.append("*not a valid longitude value")
                        entry_lon.delete(0, 'end')
                else:
                    valid = False
                    msg.append("*longitude must be a number")
                    entry_lon.delete(0, 'end')
            else:
                msg.append("*longitude field can not be left blank")
                valid = False

            if horizon:
                if horizon.replace("-", "", 1).replace(".", "", 1).isnumeric():
                    if float(horizon) > 90 or float(horizon) < 0:
                        valid = False
                        msg.append("*invalid horizon value")
                        entry_hzn.delete(0, 'end')
                else:
                    valid = False
                    msg.append("*horizon not a valid number")
                    entry_hzn.delete(0, 'end')
            else:
                msg.append("*horizon field can not be left blank")
                valid = False

            if duration:
                if duration.isnumeric():
                    if int(duration) < 0 or int(duration) > 30:
                        valid = False
                        msg.append("*provide duration less than 30 days")
                        entry_dur.delete(0, 'end')
                else:
                    valid = False
                    msg.append("*duration not a valid integer")
                    entry_dur.delete(0, 'end')
            else:
                msg.append("*duration field can not be left blank")
                valid = False

            if date:
                try:
                    setDate = (datetime.datetime.strptime(
                        date, '%Y/%m/%d')).date()
                    daysdiff = (datetime.date.today() - setDate).days
                    if abs(daysdiff) > 30:
                        msg.append('*provide date withind 15 days from today')
                        entry_date.delete(0, 'end')
                        valid = False
                except ValueError:
                    msg.append("*incorrect data format")
                    entry_date.delete(0, 'end')
                    valid = False
            else:
                msg.append("*date field can not be left blank")
                valid = False

            if not valid:
                show_error = '\n'.join(msg)
                labelvar.set(show_error)
            else:
                labelvar.set('')
                coord.get_observer_data(date, longitude, latitude, duration=int(
                    duration), horizon=int(horizon))

        labelvar = tk.StringVar()
        labelvar.set("")
        lbl_error = ttk.Label(
            frame1, textvariable=labelvar, foreground='red')
        lbl_error.grid(row=7, column=0, columnspan=6,
                       padx=5, pady=10, sticky='w')

        submit_button = ttk.Button(
            frame1, text='Submit', command=validate_input)
        submit_button.grid(row=8, column=2, columnspan=2,
                           rowspan=5, padx=5, pady=5, sticky='s')

        frame2 = tk.Frame(self, parent)
        frame2.grid(row=0, column=1, sticky="nsew")

        passvar = tk.StringVar()
        passvar.set("")
        lbl_passes = ttk.Label(
            frame2, textvariable=passvar, foreground='blue')
        lbl_passes.pack()


class MessageWindow(tk.Toplevel):

    def __init__(self, title, message):
        super().__init__()
        self.details_expanded = False
        self.title(title)
        x = self.master.winfo_x()
        y = self.master.winfo_y()
        w = 200
        h = 100
        dx, dy = self.master.winfo_width(), self.master.winfo_height()
        self.geometry("%dx%d+%d+%d" %
                      (w, h, x + 0.5 * dx - 0.5 * w, y + 0.5 * dy - 0.5 * h))
        self.resizable(False, False)
        tk.Label(self, text=message).pack(expand=True)
        tk.Button(self, text="OK", command=self.master.destroy).pack(
            side=tk.RIGHT, padx=5, pady=5)
        tk.Button(self, text="Cancel", command=self.destroy).pack(
            side=tk.RIGHT, padx=5, pady=5)
        self.grab_set()


class PlaceholderEntry(ttk.Entry):

    def __init__(self, container, placeholder, style, placeholder_style, *args, **kwargs):
        super().__init__(container, *args, **kwargs)

        self.placeholder = placeholder
        self.style = style
        self.placeholder_style = placeholder_style

        self["style"] = self.placeholder_style

        self.insert("0", self.placeholder)
        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._add_placeholder)

    def _clear_placeholder(self, e):
        if self["style"] == self.placeholder_style:
            self.delete("0", "end")
            self["style"] = self.style

    def _add_placeholder(self, e):
        if not self.get():
            self.insert("0", self.placeholder)
            self["style"] = self.placeholder_style

    def change_date(self, date):
        self.delete("0", "end")
        self.insert('0', date)
        self["style"] = self.style


app = projIss()
app.geometry("800x440")
ani = Animation.FuncAnimation(fig, animate, interval=10000)
app.mainloop()
