from heatmap import rogue
import unittest
from unittest.mock import patch, MagicMock
from gpxpy.gpx import GPXTrackPoint, GPXTrackSegment
from typing import Any, List


def fake_distance(p1, p2):
    return abs(p2.latitude - p1.latitude)


def generate_segment(lats):
    points = [GPXTrackPoint(latitude=x) for x in lats]
    return GPXTrackSegment(points=points)


# This is dumb
def equals(object1: Any, object2: Any, ignore: Any=None) -> bool:
    """ Testing purposes only """

    if not object1 and not object2:
        return True

    if not object1 or not object2:
        print('Not obj2')
        return False

    if not object1.__class__ == object2.__class__:
        print('Not obj1')
        return False

    if type(object1) == type(object2) == type([]):
        if len(object1) != len(object2):
            return False
        for i in range(len(object1)):
            if not equals(object1[i], object2[i]):
                return False
        return True

    attributes: List[str] = []
    for attr in dir(object1):
        if not ignore or attr not in ignore:
            if not hasattr(object1, '__call__') and not attr.startswith('_'):
                if attr not in attributes:
                    attributes.append(attr)

    for attr in attributes:
        attr1 = getattr(object1, attr)
        attr2 = getattr(object2, attr)

        if attr1 == attr2:
            return True

        if not attr1 and not attr2:
            return True
        if not attr1 or not attr2:
            print(f'Object differs in attribute {attr} ({attr1} - {attr2})')
            return False

        if not equals(attr1, attr2):
            print(f'Object differs in attribute {attr} ({attr1} - {attr2})')
            return False

    return True


class TestBreaks(unittest.TestCase):

    def test_break_segment_with_1_element(self):
        lats = [1]
        segment = generate_segment(lats)
        result = rogue.break_segment(segment, [])
        self.assertEqual(result, [segment])

    def test_break_segment_with_2_elements_no_breaks(self):
        lats = [1, 2]
        segment = generate_segment(lats)
        result = rogue.break_segment(segment, [])
        self.assertEqual(result, [segment])

    def test_break_segment_with_2_elements_1_break(self):
        lats = [1, 3]
        segment = generate_segment(lats)
        result = rogue.break_segment(segment, [0])
        correct = [generate_segment([1]), generate_segment([3])]
        self.assertTrue(equals(result, correct))

    @patch('heatmap.rogue.distance', MagicMock(side_effect=fake_distance))
    def test_find_breaks_with_1_span(self):
        lats = [1, 2, 3, 4, 5]
        segment = generate_segment(lats)
        result = rogue.find_breaks(segment, 1)
        self.assertEqual(result, [])

    @patch('heatmap.rogue.distance', MagicMock(side_effect=fake_distance))
    def test_find_breaks_with_2_spans(self):
        lats = [1, 2, 3, 5, 6, 7]
        segment = generate_segment(lats)
        result = rogue.find_breaks(segment, 1)
        self.assertEqual(result, [2])

    @patch('heatmap.rogue.distance', MagicMock(side_effect=fake_distance))
    def test_find_breaks_with_3_spans(self):
        lats = [1, 2, 3, 5, 6, 7, 9, 10, 11]
        segment = generate_segment(lats)
        result = rogue.find_breaks(segment, 1)
        self.assertEqual(result, [2, 5])

    @patch('heatmap.rogue.distance', MagicMock(side_effect=fake_distance))
    def test_fix_segments_with_1_span(self):
        lats = [1, 2, 3, 4, 5]
        segment = generate_segment(lats)
        result = rogue.fix_segments([segment], 1)
        self.assertTrue(equals(result, [segment]))

    @patch('heatmap.rogue.distance', MagicMock(side_effect=fake_distance))
    def test_fix_segments_with_2_spans(self):
        lats = [1, 2, 3, 5, 6, 7]
        segment = generate_segment(lats)
        result = rogue.fix_segments([segment], 1)
        correct = [generate_segment([1, 2, 3]), generate_segment([5, 6, 7])]
        self.assertTrue(equals(result, correct))

    @patch('heatmap.rogue.distance', MagicMock(side_effect=fake_distance))
    def test_fix_segments_with_3_spans(self):
        lats = [1, 2, 3, 5, 6, 7, 9, 10, 11]
        segment = generate_segment(lats)
        result = rogue.fix_segments([segment], 1)
        correct = [generate_segment([1, 2, 3]),
                   generate_segment([5, 6, 7]),
                   generate_segment([9, 10, 11])]
        self.assertTrue(equals(result, correct))


if __name__ == "__main__":
    unittest.main()
