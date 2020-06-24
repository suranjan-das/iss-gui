from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import matplotlib.animation as Animation
import datetime
import coord

# get iss path coordinates
x = coord.get_path(resolution=.3)
# save longitude and latitude in separate list variable
lons, lats = x[0], x[1]


def update_path():

    global lons, lats
    # get iss path coordinates
    x = coord.get_path(resolution=.3)
    # save longitude and latitude in separate list variable
    lons, lats = x[0], x[1]


def find_index(position):

    index = 0
    pos = position
    found = False
    for i in range(len(lons) - 1):
        if lons[i] <= pos[0] and lons[i + 1] > pos[0] and (not found):
            index = i
            found = True

    if not found:
        if pos[0] > lons[-1]:
            index = len(lons)
        else:
            index = -1

    return index


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


# define figure size of basemap
fig = plt.figure(figsize=(10, 6))
ax = fig.add_subplot(1, 1, 1)
map = Basemap()

def animate(i):

    path_updated = False
    ax.clear()
    time = datetime.datetime.utcnow()
    t = coord.get_position(time)
    index = find_index(t)
    draw_map(index, t, time)

    if t[0] < -175 and not path_updated:
        update_path()
        path_updated = True

    if t[0] > 170 and path_updated:
        path_updated = False


ani = Animation.FuncAnimation(fig, animate, interval=10000)

plt.show()
