import random

def random_walk(start, target):

    x, y = start
    tx, ty = target
    moves = [
        (1, 0),
        (-1, 0),
        (0, 1),
        (0, -1)
    ]
    steps = 0
    while (x, y) != (tx, ty):

        dx, dy = random.choice(moves)
        x += dx
        y += dy
        steps += 1
    return steps

start = (0, 0)
target = (5, 5)

arrival_time = random_walk(start, target)

print("Arrival time:", arrival_time)