from sattrack import *
from numpy import pi, cos, sin
from skyfield.api import load, Topos, Star, EarthSatellite
from skyfield.units import Angle
import matplotlib.pyplot as plt

st = SatTrack()

t0=st.ts.now().tt
data_dt=[]
# data_ra=[]
# data_dec=[]
# data_alt=[]
# data_az=[]
# data_dist=[]
# for dt in range(0, 86400*10, 60):
#     tjd=t0 + dt/86400
#     ra,dec,dist=st.sat_pos(t=st.ts.tt(jd=tjd))
#     alt, az = st.radec2altaz(ra.radians, dec.radians, t=st.ts.tt(jd=tjd))
#     #print("{0} RA:{1} DE:{2} ALT:{3} AZ:{4} DIST:{5}km".format(st.ts.tt(jd=tjd).utc_iso(),ra,dec,Angle(radians=alt, preference="degrees"),Angle(radians=az, preference="degrees"),dist.km))
#     data_dt.append(dt)
#     data_ra.append(ra.hours)
#     data_dec.append(dec.degrees)
#     data_alt.append(alt*360/2/pi)
#     data_az.append(az*360/2/pi)
#     data_dist.append(dist.km)
# plt.plot(data_dt,data_alt)
# plt.show()

def alt_t(dt):
    tjd = t0 + dt / 86400
    ra, dec, dist = st.sat_pos(t=st.ts.tt(jd=tjd))
    alt, az = st.radec2altaz(ra.radians, dec.radians, t=st.ts.tt(jd=tjd))
    return alt*360/2/pi

def az_t(dt):
    tjd = t0 + dt / 86400
    ra, dec, dist = st.sat_pos(t=st.ts.tt(jd=tjd))
    alt, az = st.radec2altaz(ra.radians, dec.radians, t=st.ts.tt(jd=tjd))
    return az*360/2/pi

step=60*20 #less than 1/4 of orbit
small_step=30 #few deg
smaller_step=1 #time resolution
trajectory_segments=20
dt0=0
dt_rise = None
dt_set = None
dt_meridian = None
dt_culmination = None
az_rise = None
az_set_set = None
az_meridian = None
az_culmination = None
alt_rise = None
alt_set_set = None
alt_meridian = None
alt_culmination = None


while True:
    # Ascending / descending orbit coarse detection
    alt0 = alt_t(dt0)
    alt1 = alt_t(dt0+step)
    while alt1 < alt0 and dt0<86400:
        print("Phase 1: Decreasing at dt0={0}, alt0={1}, alt1={2}".format(dt0,alt0, alt1))
        alt0=alt1
        dt0=dt0+step
        alt1=alt_t(dt0+step)

    while alt1 >= alt0 and dt0<86400:
        print("Phase 1: Increasing at dt0={0}, alt0={1}, alt1={2}".format(dt0, alt0, alt1))
        alt0 = alt1
        dt0 = dt0 + step
        alt1 = alt_t(dt0 + step)

    if dt0 > 86400:
        print("no other pass for today")
        break

    print("Phase 1: Maximum between dt0={0} and {1}".format(dt0-step, dt0+step))
    dt0 = dt0 - step
    alt0 = alt_t(dt0)
    alt1 = alt_t(dt0 + small_step)

    # Refining the maximum altitude
    while alt1 >= alt0 and alt1<10 and dt0<86400:
        print("Phase 2: Increasing at dt0={0}, alt0={1}, alt1={2}".format(dt0, alt0, alt1))
        alt0 = alt1
        dt0 = dt0 + small_step
        alt1 = alt_t(dt0 + small_step)


    if(alt1<0):
        if dt0<86400:
            continue # restart the search for the following orbit
        else:
            print("no pass found")
            break
    else:
        # Refining a 2nd time the maximum altitude to get the date
        alt1 = alt_t(dt0 + smaller_step)
        while alt1 >= alt0:
            if dt0>86400:
                print("no culmination today")
                break
            print("Phase 3: Increasing at dt0={0}, alt0={1}, alt1={2}".format(dt0, alt0, alt1))
            alt0 = alt1
            dt0 = dt0 + smaller_step
            alt1 = alt_t(dt0 + smaller_step)
        dt_culmination=dt0
        alt_culmination=alt0
        az_culmination = az_t(dt_culmination)

        # refining rise and set date by dichotomy
        # set
        dt0 = dt_culmination
        alt0 = alt_t(dt_culmination)
        alt1 = alt_t(dt_culmination+step)
        while alt1 >= 0 and dt0 < 86400:
            print("Phase 4 set: Increasing at dt0={0}, alt0={1}, alt1={2}".format(dt0, alt0, alt1))
            alt0 = alt1
            dt0 = dt0 + step
            alt1 = alt_t(dt0 + step)
        if dt0 > 86400:
            print("no set today")
        else:
            dt1 = dt0+step
            while dt1-dt0>smaller_step:
                dt2 = (dt0 + dt1)/2
                alt2 = alt_t(dt2)

                if alt2 > 0:
                    dt0 = dt2
                    alt0 = alt2
                else:
                    dt1 = dt2
                    alt1 =alt2
                print("Phase 4 set: Restrict set date to dt={0} alt={1} to dt={2} alt={3}".format(dt0, alt0, dt1, alt1))
            dt_set = dt0
            az_set = az_t(dt_set)
        # rise
        dt0 = dt_culmination
        alt0 = alt_t(dt_culmination)
        alt1 = alt_t(dt_culmination-step)
        while alt1 >= 0 and dt0 > -86400:
            print("Phase 4 rise: Increasing at dt0={0}, alt0={1}, alt1={2}".format(dt0, alt0, alt1))
            alt0 = alt1
            dt0 = dt0 - step
            alt1 = alt_t(dt0 - step)
        if dt0 < -86400:
            print("no rise today")
        else:
            dt1 = dt0-step
            while dt0-dt1>smaller_step:
                dt2 = (dt0 + dt1)/2
                alt2 = alt_t(dt2)
                if alt2 > 0:
                    dt0 = dt2
                    alt0 = alt2
                else:
                    dt1 = dt2
                    alt1 =alt2
                print("Phase 4 rise: Restrict set date to dt={0} alt={1} to dt={2} alt={3}".format(dt0, alt0, dt1, alt1))
            dt_rise = dt0
            az_rise = az_t(dt_rise)

        #meridian
        if(dt_rise is not None) and (dt_set is not None):
            dt0=dt_rise
            dt1=dt0+(dt_set-dt_rise)/trajectory_segments
            az0=az_t(dt0)
            az1 = az_t(dt1)
            while dt1 < dt_set and az0*az1 > 0:  # equivalent to sign(az0)==sign(az1)
                dt0=dt1
                dt1 = dt0 + (dt_set - dt_rise) / trajectory_segments
                az0 = az1
                az1 = az_t(dt1)
                print(
                    "Phase 5a: Segment dt={0} az={1} to dt={2} az={3}".format(dt0, az0, dt1, az1))
        if dt1 >= dt_set:
            print("no meridian crossing")
        else:
            while dt1-dt0>smaller_step:
                dt2 = (dt0 + dt1)/2
                az2 = az_t(dt2)
                if az2*az0 > 0:
                    dt0 = dt2
                    az0 = az2
                else:
                    dt1 = dt2
                    az1 =az2
                print("Phase 5b: Restrict meridian crossing date to dt={0} az={1} to dt={2} az={3}".format(dt0, az0, dt1, az1))
            dt_meridian = dt0
            az_meridian = az_t(dt_meridian)
            alt_meridian = alt_t(dt_meridian)

        print("pass found:\n rise: dt={0} az={1}\n meridian:  dt={2} az={3} alt={4}\n culmination:  dt={5} az={6} alt={7}\n set: dt={8} az={9}".format(dt_rise, az_rise, dt_meridian, az_meridian, alt_meridian, dt_culmination, az_culmination, alt_culmination, dt_set,az_set))
        input()
        #break



