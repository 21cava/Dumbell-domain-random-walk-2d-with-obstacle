import random
import statistics
from collections import deque


# PARAMETERS

RADIUS = 20
DISTANCE = 30
NECK_WIDTH = 6

DENSITIES = [3, 6, 9, 12, 15]
N_SIMULATIONS = 100000

MAX_STEPS = 30000
TARGET_STEPS = 3

CLUSTER_SIZE = 5


# DUMBBELL DOMAIN

def create_dumbbell(radius, distance, neck_width):

    domain = set()

    for x in range(-distance - radius, distance + radius + 1):
        for y in range(-radius, radius + 1):

            left_lobe = (
                (x + distance) ** 2 + y ** 2 <= radius ** 2
            )

            right_lobe = (
                (x - distance) ** 2 + y ** 2 <= radius ** 2
            )

            neck = (
                -distance <= x <= distance
                and abs(y) <= neck_width // 2
            )

            if left_lobe or right_lobe or neck:
                domain.add((x, y))

    return domain


# LOBES

def create_lobes(domain, radius, distance):

    left_lobe = set()
    right_lobe = set()

    for x, y in domain:

        if (x + distance) ** 2 + y ** 2 <= radius ** 2:
            left_lobe.add((x, y))

        if (x - distance) ** 2 + y ** 2 <= radius ** 2:
            right_lobe.add((x, y))

    return left_lobe, right_lobe


# CLUSTER OBSTACLES

def create_obstacles(
    domain,
    left_lobe,
    right_lobe,
    density,
    cluster_size
):

    possible_positions = domain - right_lobe

    # Total number of obstacle cells
    total_obstacles = int(len(domain) * density / 100)

    if total_obstacles > len(possible_positions):
        raise ValueError(
            "Obstacle density is too high for this geometry."
        )

    obstacles = set()

    while len(obstacles) < total_obstacles:

        # Positions that are not occupied and are not adjacent
        # to existing clusters
        available = set()

        for position in possible_positions - obstacles:

            x, y = position

            # Check all 8 neighbouring cells
            neighbours = [
                (x + dx, y + dy)
                for dx in (-1, 0, 1)
                for dy in (-1, 0, 1)
                if not (dx == 0 and dy == 0)
            ]

            # Position can be used only if it is not
            # touching an existing obstacle
            if all(
                neighbour not in obstacles
                for neighbour in neighbours
            ):
                available.add(position)

        if not available:
            break

        # Random starting point for a new cluster
        start = random.choice(list(available))

        cluster = {start}
        frontier = [start]

        # Grow the cluster
        while len(cluster) < cluster_size:

            candidates = []

            for x, y in frontier:

                neighbours = [
                    (x + 1, y),
                    (x - 1, y),
                    (x, y + 1),
                    (x, y - 1)
                ]

                for position in neighbours:

                    if (
                        position in possible_positions
                        and position not in obstacles
                        and position not in cluster
                        and position not in candidates
                    ):
                        candidates.append(position)

            if not candidates:
                break

            position = random.choice(candidates)

            cluster.add(position)
            frontier.append(position)

        # Number of cells still needed
        remaining = total_obstacles - len(obstacles)

        # Do not exceed the requested density
        if len(cluster) > remaining:

            cluster = set(
                random.sample(
                    list(cluster),
                    remaining
                )
            )

        obstacles.update(cluster)

    # Check that the exact requested number of obstacles was created
    if len(obstacles) != total_obstacles:
        raise RuntimeError(
            "Could not generate enough separated obstacle clusters."
        )

    return obstacles


# RANDOM WALK

def random_walk(
    domain,
    obstacles,
    start,
    right_lobe,
    max_steps,
    target_steps
):

    x, y = start

    moves = [
        (1, 0),
        (-1, 0),
        (0, 1),
        (0, -1)
    ]

    consecutive_target = 0

    for step in range(1, max_steps + 1):

        valid_moves = []

        for dx, dy in moves:

            position = (x + dx, y + dy)

            if (
                position in domain
                and position not in obstacles
            ):
                valid_moves.append((dx, dy))

        if not valid_moves:
            return None

        dx, dy = random.choice(valid_moves)

        x += dx
        y += dy

        if (x, y) in right_lobe:
            consecutive_target += 1
        else:
            consecutive_target = 0

        if consecutive_target >= target_steps:
            return step

    return None


# SIMULATIONS

def run_simulation(
    domain,
    left_lobe,
    right_lobe,
    obstacles,
    n_simulations,
    max_steps,
    target_steps
):

    arrival_times = []
    failures = 0

    possible_starts = list(left_lobe - obstacles)

    for _ in range(n_simulations):

        start = random.choice(possible_starts)

        result = random_walk(
            domain,
            obstacles,
            start,
            right_lobe,
            max_steps,
            target_steps
        )

        if result is None:
            failures += 1
        else:
            arrival_times.append(result)

    successes = len(arrival_times)

    success_rate = (
        successes / n_simulations
    ) * 100

    if successes > 0:

        mean_time = statistics.mean(arrival_times)
        median_time = statistics.median(arrival_times)

        if successes > 1:
            variance = statistics.variance(arrival_times)
        else:
            variance = 0

    else:

        mean_time = None
        median_time = None
        variance = None

    return (
        successes,
        failures,
        success_rate,
        mean_time,
        median_time,
        variance
    )


# CREATE DOMAIN

domain = create_dumbbell(
    RADIUS,
    DISTANCE,
    NECK_WIDTH
)

left_lobe, right_lobe = create_lobes(
    domain,
    RADIUS,
    DISTANCE
)


# RUN

for density in DENSITIES:

    print()
    print("==========================================")
    print("Density:", density, "%")
    print("==========================================")

    obstacles = create_obstacles(
        domain,
        left_lobe,
        right_lobe,
        density,
        CLUSTER_SIZE
    )

    (
        successes,
        failures,
        success_rate,
        mean_time,
        median_time,
        variance
    ) = run_simulation(
        domain,
        left_lobe,
        right_lobe,
        obstacles,
        N_SIMULATIONS,
        MAX_STEPS,
        TARGET_STEPS
    )

    print("Simulations:", N_SIMULATIONS)
    print("Number of obstacles:", len(obstacles))
    print("Cluster size:", CLUSTER_SIZE)
    print("Maximum steps:", MAX_STEPS)
    print("Target consecutive steps:", TARGET_STEPS)

    print("------------------------------------------")

    print("Successful runs:", successes)
    print("Failed runs:", failures)
    print("Success rate:", round(success_rate, 2), "%")

    if mean_time is not None:

        print("Mean arrival time:", round(mean_time, 2))
        print("Median arrival time:", round(median_time, 2))
        print("Variance:", round(variance, 2))

    else:

        print("No successful runs.")