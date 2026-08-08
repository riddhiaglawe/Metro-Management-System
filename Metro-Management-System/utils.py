import sqlite3

DATABASE = "metro.db"


# ----------------------------
# Database Connection
# ----------------------------
def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ----------------------------
# Get Station Details
# ----------------------------
def get_station(station_name):

    conn = get_connection()

    station = conn.execute("""
        SELECT *
        FROM station
        WHERE station_name=?
    """, (station_name,)).fetchone()

    conn.close()

    return station


# ----------------------------
# Calculate Fare
# ----------------------------
def calculate_fare(total_stations):

    if total_stations <= 5:
        return 10

    elif total_stations <= 10:
        return 20

    elif total_stations <= 15:
        return 30

    elif total_stations <= 20:
        return 40

    else:
        return 50


# ----------------------------
# Travel Time
# ----------------------------
def calculate_time(total_stations):

    return total_stations * 2


# ----------------------------
# Same Line Distance
# ----------------------------
def same_line_distance(source, destination):

    return abs(
        source["station_order"] -
        destination["station_order"]
    )


# ----------------------------
# Interchange Distance
# ----------------------------
def interchange_distance(source, destination):

    conn = get_connection()

    orange = conn.execute("""
        SELECT *
        FROM station
        WHERE station_name='Sitabuldi'
        AND line_id=1
    """).fetchone()

    aqua = conn.execute("""
        SELECT *
        FROM station
        WHERE station_name='Sitabuldi'
        AND line_id=2
    """).fetchone()

    conn.close()

    if source["line_id"] == 1:

        first = abs(
            source["station_order"] -
            orange["station_order"]
        )

        second = abs(
            destination["station_order"] -
            aqua["station_order"]
        )

    else:

        first = abs(
            source["station_order"] -
            aqua["station_order"]
        )

        second = abs(
            destination["station_order"] -
            orange["station_order"]
        )

    return first + second


# ----------------------------
# Total Stations
# ----------------------------
def total_stations(source_name, destination_name):

    source = get_station(source_name)
    destination = get_station(destination_name)

    if source is None or destination is None:
        return None

    if source["line_id"] == destination["line_id"]:

        return same_line_distance(
            source,
            destination
        )

    return interchange_distance(
        source,
        destination
    )


def search_train(source_name, destination_name):

    source = get_station(source_name)
    destination = get_station(destination_name)

    if source is None or destination is None:
        return []

    conn = get_connection()

    results = []

    # -------------------------
    # SAME LINE
    # -------------------------

    if source["line_id"] == destination["line_id"]:

        trains = conn.execute("""
            SELECT *
            FROM train
            WHERE line_id=?
            ORDER BY train_number
        """, (source["line_id"],)).fetchall()

        for train in trains:

            source_schedule = conn.execute("""
                SELECT departure_time
                FROM schedule
                WHERE train_id=? AND station_id=?
            """, (train["train_id"], source["station_id"])).fetchone()

            destination_schedule = conn.execute("""
                SELECT arrival_time
                FROM schedule
                WHERE train_id=? AND station_id=?
            """, (train["train_id"], destination["station_id"])).fetchone()

            if source_schedule and destination_schedule:

                stations = abs(
                    destination["station_order"] -
                    source["station_order"]
                )

                results.append({

                    "type": "Direct",

                    "train": train["train_number"],

                    "train_name": train["train_name"],

                    "departure": source_schedule["departure_time"],

                    "arrival": destination_schedule["arrival_time"],

                    "stations": stations,

                    "travel_time": calculate_time(stations),

                    "fare": calculate_fare(stations)

                })

        conn.close()

        return results

    # -------------------------
    # INTERCHANGE
    # -------------------------

    orange_train = conn.execute("""
        SELECT *
        FROM train
        WHERE line_id=1
        ORDER BY train_number
        LIMIT 1
    """).fetchone()

    aqua_train = conn.execute("""
        SELECT *
        FROM train
        WHERE line_id=2
        ORDER BY train_number
        LIMIT 1
    """).fetchone()

    conn.close()

    total = total_stations(
        source_name,
        destination_name
    )

    if source["line_id"] == 1:

        first_train = orange_train

        second_train = aqua_train

    else:

        first_train = aqua_train

        second_train = orange_train

    results.append({

        "type": "Interchange",

        "first_train": first_train["train_number"],

        "second_train": second_train["train_number"],

        "interchange": "Sitabuldi",

        "travel_time": calculate_time(total),

        "fare": calculate_fare(total),

        "stations": total

    })

    conn.close()

    print("Results:", results)
    return results