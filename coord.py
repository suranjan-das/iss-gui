import requests
import ephem
from ephem import degree
import datetime
# variable for storing satellite data
sat_data = list()
lons, lats = list(), list()

now = datetime.datetime.utcnow()
# fetch iss tle data
req_tle = requests.get('https://www.celestrak.com/NORAD/elements/stations.txt')
response = req_tle.text
line1, line2, line3 = response.split('\n')[0], response.split('\n')[
    1], response.split('\n')[2]
# read tle data
iss = ephem.readtle(line1, line2, line3)


def get_position(time):
    """returns iss position

    Keyword arguments:
    time in utc format

    returns list [longitude, latitude]"""
    iss.compute(time)
    lon = iss.sublong / degree
    lat = iss.sublat / degree
    position = [lon, lat]

    return position


def find_index(position, lons):

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


def get_path(resolution=0.5):
    """returns list of longitude and latitudes
    for the iss path to draw iss path
    this ranges from longitude -180 to 180 degree

    Keyword arguments:
    resolution = minute difference between two
    cosecutive point(default 0.5)

    returns [longitudes, latiudes] both list"""

    r = resolution
    t_range = int(100 / r)

    now_t = datetime.datetime.utcnow()
    iss.compute(now_t)
    pos_now = iss.sublong / degree

    longs1, longs2, latis1, latis2 = list(), list(), list(), list()
    for i in range(1, t_range):
        delta_t1 = datetime.timedelta(minutes=i * r)
        delta_t2 = datetime.timedelta(minutes=i * r + r)

        iss.compute(now_t - delta_t1)

        long1 = iss.sublong / degree
        lati1 = iss.sublat / degree

        iss.compute(now_t - delta_t2)

        long2 = iss.sublong / degree

        if long1 > long2 and pos_now > long1:
            longs1.append(long1)
            latis1.append(lati1)
        else:
            break

    for i in range(1, t_range):
        delta_t1 = datetime.timedelta(minutes=i * r)
        delta_t2 = datetime.timedelta(minutes=i * r + r)

        iss.compute(now_t + delta_t1)

        long1 = iss.sublong / degree
        lati1 = iss.sublat / degree

        iss.compute(now_t + delta_t2)

        long2 = iss.sublong / degree

        if long1 < long2 and pos_now < long1:
            longs2.append(long1)
            latis2.append(lati1)
        else:
            break

    longs1.reverse()
    longs = longs1 + longs2
    latis1.reverse()
    latis = latis1 + latis2

    return [longs, latis]


def get_iss_data():
    """this function calculate various iss data

    Returns:list
    [position, altitude, velocity]"""
    pass


def get_observer_data(start_date, lon, lat, duration=10, horizon=10):
    """calculates iss visible and daylight pass details

    Keyword arguments:
    start_date(string) : date in 'YYYY/MM/DD' format from which search to be made
    lon(float) : observer longitude
    lat(float) : observer latitude
    duration(int) : search period in days
    horizon(int) : observer minimum horizon in degrees

    returns (pass type, rise time, rise azimuth, rise altitude, max altitude time, max altitude, set time, set azimuht, set altitude)"""

    passes = []
    # initiate a observer
    obs = ephem.Observer()
    # set up observer details
    strt_date = start_date + ' 00:00:00'
    end_date = ephem.date(strt_date) + duration * 24 * ephem.hour

    obs.lon = str(lon)
    obs.lat = str(lat)
    obs.horizon = str(horizon)
    # compute data in give time period
    while ephem.date(end_date) > ephem.date(strt_date):

        eclipse = []  # holds timestamps of different condition
        obs.date = strt_date
        info = obs.next_pass(iss)  # calculate next pass for the observer

        # philosophy for determining pass type : for a pass to be visible
        # the iss must cross the twilight zone that is iss.eclipse parameter
        # must change value between True and False
        # it will be visible when iss.eclipse is False, one minute margin
        # added to ensure iss.eclipse state change

        # store all the pass information
        strt_time = info[0] - ephem.minute
        end_time = info[4] + ephem.minute
        max_time = info[2]

        rise_az = get_azimuth(info[1])
        set_az = get_azimuth(info[5])
        max_alt = info[3]

        rise_alt = horizon
        set_alt = horizon

        obs.date = strt_time
        iss.compute(obs)
        ecl1 = iss.eclipsed

        obs.date = end_time
        iss.compute(obs)
        ecl2 = iss.eclipsed

        pass_type = ''

        if ecl1 != ecl2:
            pass_type = 'visible'
            while ephem.date(end_time) >= ephem.date(strt_time):
                obs.date = strt_time
                iss.compute(obs)
                if not iss.eclipsed:
                    eclipse.append(strt_time)
                strt_time = ephem.date(strt_time) + 5 * ephem.second
            # get rid of the one minute margin added previously
            while eclipse[0] < (info[0]) and len(eclipse) > 1:
                del eclipse[0]
            while eclipse[-1] > (info[4]) and len(eclipse) > 1:
                del eclipse[-1]
        else:
            pass_type = 'daylight'
            eclipse.append(info[0])
            eclipse.append(info[4])
        # adjust pass data according to new calculated time for
        # visible pass
        if eclipse:
            if pass_type == 'visible':
                if max_time > eclipse[-1]:
                    max_time = eclipse[-1]
                elif max_time < eclipse[0]:
                    max_time = eclipse[0]

                obs.date = eclipse[0]
                iss.compute(obs)
                rise_az = get_azimuth(
                    (int((str(iss.az)).split(':')[0])) / 57.295)
                rise_alt = iss.alt

                obs.date = eclipse[-1]
                iss.compute(obs)
                set_az = get_azimuth(
                    (int((str(iss.az)).split(':')[0])) / 57.295)
                set_alt = iss.alt

                obs.date = max_time
                iss.compute(obs)
                max_alt = iss.alt

            passes.append(format_pass_data(pass_type, eclipse[
                          0], rise_az, rise_alt, max_time, max_alt, eclipse[-1], set_az, set_alt))
        # look for next pass from the end of this pass
        strt_date = info[4]

    [print(x) for x in passes if x[0] == 'visible']


def get_azimuth(az):
    """this returns the azimuth direction
    from an angle(radian) value"""

    dir_name = ['N', 'NNE', 'NE', 'NEE', 'E', 'SEE', 'SE', 'SSE',
                'S', 'SSW', 'SW', 'SWW', 'W', 'NWW', 'NW', 'NNW', 'N']
    dir_angle = []
    angle = 0
    for i in range(0, 17):
        angle = i * 22.5
        dir_angle.append(angle)

    az = 57.295 * az
    a = [abs(x - az) for x in dir_angle]
    index = a.index(min(a))

    return dir_name[index]


def format_pass_data(ptype, rise_t, rise_az, rise_alt, max_t, max_alt, set_t, set_az, set_alt):
    """this function format all pass data"""
    degree_sign = u"\N{DEGREE SIGN}"

    pass_type = ptype
    date = (str(ephem.localtime(rise_t))).split(' ')[0]
    rise_time = (str(ephem.localtime(rise_t))).split(' ')[1][:8]
    rise_azimuth = rise_az
    rise_altitude = str(int(57.295 * rise_alt)) + degree_sign
    max_time = (str(ephem.localtime(max_t))).split(' ')[1][:8]
    max_altitude = str(int(57.295 * max_alt)) + degree_sign
    set_time = (str(ephem.localtime(set_t))).split(' ')[1][:8]
    set_azimuth = set_az
    set_altitude = str(int(57.295 * set_alt)) + degree_sign

    return (ptype, date, rise_time, rise_azimuth, rise_altitude, max_time, max_altitude, set_time, set_azimuth, set_altitude)
