from bid import Bid, Bids
from functools import reduce
from hasher import Hasher, Hashers
from itertools import islice
from pytest import fixture
from random import choice
from timeSlot import TimeSlot, TimeSlots
from trail import Trail, Trails
import csv


@fixture
def bid(hasher, trail, score):
    bid = Bid(hasher, trail, score)
    return bid


@fixture
def bids(bid_file, hashers, trails):
    return Bids('.', hashers=hashers, trails=trails)


@fixture
def bid_allowance():
    return 1000


@fixture
def bid_file(fs, hasher_list, trail_list):
    loop_max = max([len(hasher_list), len(trail_list)])
    content = [['hasher', 'trail', 'value']]
    for i in range(loop_max):
        hasher_idx = i % len(hasher_list)
        trail_idx = i % len(trail_list)
        content.append([hasher_list[hasher_idx].id, trail_list[trail_idx].id, 100])
    with open('bids.txt', 'w+') as csv_file:
        writer = csv.writer(csv_file)
        for row in content:
            writer.writerow(row)


@fixture
def hasher(hasher_id, name, sequence):
    return Hasher(hasher_id, sequence, name)


@fixture
def hashers(hasher_file):
    return Hashers('.')


@fixture
def hasher_file(fs, hasher_list):
    content = [['hasher_id', 'sequence', 'name']]
    content.extend([[hasher.id, hasher.sequence, hasher.name] for hasher in hasher_list])
    with open('hashers.txt', 'w+') as csv_file:
        writer = csv.writer(csv_file)
        for row in content:
            writer.writerow(row)

@fixture
def hasher_ids():
    return (n for n in range(10000))


@fixture
def hasher_list(hasher_ids, hasher_names, sequence):
    def reducer(acc, value):
        acc.append(Hasher(next(hasher_ids), 0, hasher_names[value]))
        return acc
    return reduce(reducer, range(500), [])


@fixture
def hasher_names(faker):
    return [faker.name() for _ in range(500)]


@fixture
def hasher_id():
    return 101


@fixture
def name():
    return "Stupid McNamey"


@fixture
def score():
    return 500


@fixture
def sequence():
    return 0


@fixture
def time_slot(timeslot_id, timeslot_name):
    return TimeSlot(timeslot_id, 0, timeslot_name)


@fixture
def time_slots(time_slot_file):
    return TimeSlots('.')


@fixture
def time_slot_file(fs, timeslot_list):
    content = [['time_slot_id', 'sequence', 'name']]
    content.extend([[timeslot.id, timeslot.sequence, timeslot.name] for timeslot in timeslot_list])
    with open('timeSlots.txt', 'w+') as csv_file:
        writer = csv.writer(csv_file)
        for row in content:
            writer.writerow(row)


@fixture
def timeslot_list(timeslot_ids, timeslot_names):
    def reducer(acc, value):
        timeslot = TimeSlot(next(timeslot_ids), 0, next(timeslot_names))
        acc.append(timeslot)
        return acc
    return reduce(reducer, range(50), [])


@fixture
def timeslot_id():
    return '331232'


@fixture
def timeslot_ids():
    return (num for num in range(500))


@fixture
def timeslot_name():
    return 'test time slot'


@fixture
def timeslot_names(faker):
    return (' '.join(faker.words()) for _ in range(10000))


@fixture
def trail(time_slot, trail_capacity, trail_id, trail_name):
    trail = Trail(trail_id, 0, trail_name, trail_capacity)
    trail.timeSlot = time_slot
    return trail


@fixture
def trails(trail_file, time_slots):
    trails = Trails('.')
    for idx, trail in enumerate(trails.list):
        time_slot = time_slots.list[idx % len(time_slots.list)]
        trail.setTimeSlot(time_slot)
    return trails


@fixture
def trail_file(fs, trail_list):
    content = [['trail_id', 'sequence', 'name', 'capacity']]
    content.extend([[trail.id, trail.sequence, trail.name, trail.capacity] for trail in trail_list])
    with open('trails.txt', 'w+') as csv_file:
        writer = csv.writer(csv_file)
        for row in content:
            writer.writerow(row)


@fixture
def trail_list(timeslot_list, trail_capacity, trail_ids, trail_names):
    def reducer(acc, value):
        trail = Trail(next(trail_ids), 0, next(trail_names), 100)
        acc.append(trail)
        return acc
    slots = list(islice(timeslot_list, 4))
    a = reduce(reducer, range(100), [])
    map(lambda trail: trail.setTimeSlot(choice(slots)), a)
    return list(a)


@fixture
def trail_capacity():
    return 200


@fixture
def trail_id():
    return 201


@fixture
def trail_ids():
    return (n for n in range(10000))


@fixture
def trail_name():
    return 'test trail'


@fixture
def trail_names(faker):
    return (' '.join(faker.words()) for _ in range(10000))
