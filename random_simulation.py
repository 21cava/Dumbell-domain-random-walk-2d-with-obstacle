import random
import statistics


# ============================================================
# PARAMETRI DELLA SIMULAZIONE
# ============================================================

RADIUS = 20
DISTANCE = 30
NECK_WIDTH = 6

# Percentuale del dominio occupata dagli ostacoli
DENSITIES = [3, 6, 9, 12, 15]

# Numero di random walk per ogni densità
N_SIMULATIONS = 100

# Numero massimo di passi per ogni random walk
MAX_STEPS = 30000

# Numero di passi consecutivi nel lobo destro
# necessari per considerare raggiunto il target
TARGET_STEPS = 3


# ============================================================
# CREAZIONE DEL DOMINIO A MANUBRIO
# ============================================================

def create_dumbbell(radius, distance, neck_width):

    domain = set()

    for x in range(-distance - radius, distance + radius + 1):
        for y in range(-radius, radius + 1):

            # Lobo sinistro
            left_lobe = (
                (x + distance) ** 2 + y ** 2 <= radius ** 2
            )

            # Lobo destro
            right_lobe = (
                (x - distance) ** 2 + y ** 2 <= radius ** 2
            )

            # Collo centrale
            neck = (
                -distance <= x <= distance
                and abs(y) <= neck_width // 2
            )

            if left_lobe or right_lobe or neck:
                domain.add((x, y))

    return domain


# ============================================================
# IDENTIFICAZIONE DEI DUE LOBI
# ============================================================

def create_lobes(domain, radius, distance):

    left_lobe = set()
    right_lobe = set()

    for x, y in domain:

        if (x + distance) ** 2 + y ** 2 <= radius ** 2:
            left_lobe.add((x, y))

        if (x - distance) ** 2 + y ** 2 <= radius ** 2:
            right_lobe.add((x, y))

    return left_lobe, right_lobe


# ============================================================
# CREAZIONE DEGLI OSTACOLI RANDOM
# ============================================================

def create_obstacles(
    domain,
    right_lobe,
    density
):

    # Gli ostacoli possono essere collocati in tutto il dominio
    # tranne che nel lobo destro.
    possible_positions = domain - right_lobe

    # Numero totale di celle che devono diventare ostacoli.
    total_obstacles = int(len(domain) * density / 100)

    if total_obstacles > len(possible_positions):
        raise ValueError(
            "Obstacle density is too high for this geometry."
        )

    # Estrazione casuale senza ripetizioni.
    # Non esistono cluster: ogni cella viene scelta casualmente.
    obstacles = set(
        random.sample(
            list(possible_positions),
            total_obstacles
        )
    )

    return obstacles


# ============================================================
# RANDOM WALK
# ============================================================

def random_walk(
    domain,
    obstacles,
    start,
    right_lobe,
    max_steps,
    target_steps
):

    x, y = start

    # Movimento sulla griglia: destra, sinistra, sopra, sotto.
    moves = [
        (1, 0),
        (-1, 0),
        (0, 1),
        (0, -1)
    ]

    consecutive_target = 0

    for step in range(1, max_steps + 1):

        # Determina le mosse possibili:
        # - dentro il dominio
        # - non dentro un ostacolo
        valid_moves = []

        for dx, dy in moves:

            position = (x + dx, y + dy)

            if (
                position in domain
                and position not in obstacles
            ):
                valid_moves.append((dx, dy))

        # Il walker è completamente bloccato.
        if not valid_moves:
            return None

        # Scelta casuale di una delle mosse valide.
        dx, dy = random.choice(valid_moves)

        x += dx
        y += dy

        # Controlla se il walker si trova nel lobo destro.
        if (x, y) in right_lobe:
            consecutive_target += 1
        else:
            consecutive_target = 0

        # Successo se rimane nel lobo destro
        # per TARGET_STEPS passi consecutivi.
        if consecutive_target >= target_steps:
            return step

    # Nessun raggiungimento del target entro MAX_STEPS.
    return None


# ============================================================
# ESECUZIONE DELLE SIMULAZIONI
# ============================================================

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

    # Possibili punti di partenza:
    # tutte le celle libere del lobo sinistro.
    possible_starts = list(left_lobe - obstacles)

    if not possible_starts:
        raise RuntimeError(
            "There are no available starting positions in the left lobe."
        )

    for _ in range(n_simulations):

        # Punto di partenza casuale.
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

    # Percentuale di simulazioni riuscite.
    success_rate = (
        successes / n_simulations
    ) * 100

    # Le statistiche dei tempi vengono calcolate
    # solamente sulle simulazioni riuscite.
    if successes > 0:

        mean_time = statistics.mean(arrival_times)

        median_time = statistics.median(
            arrival_times
        )

        if successes > 1:
            variance = statistics.variance(
                arrival_times
            )
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


# ============================================================
# PROGRAMMA PRINCIPALE
# ============================================================

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


print("==========================================")
print("2D RANDOM WALK - RANDOM OBSTACLES")
print("==========================================")

print("Domain cells:", len(domain))
print("Left lobe cells:", len(left_lobe))
print("Right lobe cells:", len(right_lobe))

print("Densities:", DENSITIES)
print("Simulations per density:", N_SIMULATIONS)
print("Maximum steps:", MAX_STEPS)
print("Target consecutive steps:", TARGET_STEPS)

print()


# ============================================================
# SIMULAZIONE PER OGNI DENSITÀ
# ============================================================

for density in DENSITIES:

    print("==========================================")
    print(f"Density: {density} %")
    print("==========================================")

    # Genera una nuova disposizione casuale
    # degli ostacoli per questa densità.
    obstacles = create_obstacles(
        domain,
        right_lobe,
        density
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
    print("Maximum steps:", MAX_STEPS)
    print("Target consecutive steps:", TARGET_STEPS)

    print("------------------------------------------")

    print("Successful runs:", successes)
    print("Failed runs:", failures)
    print("Success rate:", round(success_rate, 2), "%")

    if mean_time is not None:

        print(
            "Mean arrival time:",
            round(mean_time, 2)
        )

        print(
            "Median arrival time:",
            round(median_time, 2)
        )

        print(
            "Variance:",
            round(variance, 2)
        )

    else:

        print("No successful runs.")

    print()