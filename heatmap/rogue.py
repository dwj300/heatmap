#!/usr/bin/env python3
from gpxpy import parse
from gpxpy.gpx import GPXTrackSegment
from math import atan2, cos, radians, sin, sqrt
from glob import glob
import os
import multiprocessing


def break_segment(segment, break_points): 
    new = [segment]
    if len(break_points) != 0:
        i = 0
        for b in break_points:
            old = new.pop()
            new1, new2 = old.split(b-i)
            if len(new1.points) != 0:
                new.append(new1)
            if len(new2.points) == 0:
                return new
            new.append(new2)
            i += b
    return new


def find_breaks(segment, max_dist):
    breaks = []
    for i in range(len(segment.points)-1):
        if distance(segment.points[i+1], segment.points[i]) > max_dist:
            breaks.append(i)
    return breaks


def fix_segments(segments, max_dist):
    s = []
    for segment in segments:
        s.extend(break_segment(segment, find_breaks(segment, max_dist)))
    return s


def distance(origin, destination):
    lat1, lon1 = origin.latitude, origin.longitude
    lat2, lon2 = destination.latitude, destination.longitude
    radius = 6371  # km
    dlat = radians(lat2-lat1)
    dlon = radians(lon2-lon1)
    a = sin(dlat/2) * sin(dlat/2) + cos(radians(lat1)) \
        * cos(radians(lat2)) * sin(dlon/2) * sin(dlon/2)
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    d = radius * c
    return d


def disjointed(filename):
    with open(filename, 'r') as f:
        gpx = parse(f)
    old_segments = gpx.tracks[0].segments
    new_segments = fix_segments(old_segments, 0.1)
    if len(old_segments) == len(new_segments):
        return None
    gpx.tracks[0].segments = new_segments
    with open(filename, 'w') as f:
        f.write(gpx.to_xml())
    return filename


def main():
    files = glob("strava/*.gpx")
    p = multiprocessing.Pool(multiprocessing.cpu_count())
    results = p.map(disjointed, files)
    bad = [r for r in results if r]
    if len(bad) > 0:
        if os.path.isfile("strava/cache.pkl"):
            os.remove("strava/cache.pkl")
        print(bad)


if __name__ == '__main__':
    main()
