#!/usr/bin/env python3
from gpxpy import parse
from math import atan2, cos, radians, sin, sqrt
from glob import glob


def distance(origin, destination):
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371  # km
    dlat = radians(lat2-lat1)
    dlon = radians(lon2-lon1)
    a = sin(dlat/2) * sin(dlat/2) + cos(radians(lat1)) \
        * cos(radians(lat2)) * sin(dlon/2) * sin(dlon/2)
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    d = radius * c
    return d


def disjointed(filename, max_jump=1):
    gpx_file = open(filename, 'r')
    gpx = parse(gpx_file)
    distances = []
    for i in range(len(gpx.tracks[0].segments[0].points)-1):
        p1 = gpx.tracks[0].segments[0].points[i]
        p2 = gpx.tracks[0].segments[0].points[i+1]
        d = distance((p1.latitude, p1.longitude), (p2.latitude, p2.longitude))
        distances.append(d)
    return max(distances) > max_jump


def main():
    files = glob("strava/*.gpx")
    for filename in files:
        if disjointed(filename):
            print(filename)


if __name__ == '__main__':
    main()
