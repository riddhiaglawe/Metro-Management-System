import sqlite3

# -----------------------------
# Create / Connect Database
# -----------------------------
conn = sqlite3.connect("metro.db")
cursor = conn.cursor()

# -----------------------------
# Drop Existing Tables
# -----------------------------
cursor.execute("DROP TABLE IF EXISTS booking")
cursor.execute("DROP TABLE IF EXISTS schedule")
cursor.execute("DROP TABLE IF EXISTS train")
cursor.execute("DROP TABLE IF EXISTS station")
cursor.execute("DROP TABLE IF EXISTS metro_line")
cursor.execute("DROP TABLE IF EXISTS passenger")
cursor.execute("DROP TABLE IF EXISTS admin")

# -----------------------------
# ADMIN TABLE
# -----------------------------
cursor.execute("""
CREATE TABLE admin(
    admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")

cursor.execute("""
INSERT INTO admin(username,password)
VALUES('admin','admin123')
""")

# -----------------------------
# PASSENGER TABLE
# -----------------------------
cursor.execute("""
CREATE TABLE passenger(
    passenger_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT NOT NULL,
    password TEXT NOT NULL
)
""")

# -----------------------------
# METRO LINE TABLE
# -----------------------------
cursor.execute("""
CREATE TABLE metro_line(
    line_id INTEGER PRIMARY KEY AUTOINCREMENT,
    line_name TEXT NOT NULL,
    line_color TEXT NOT NULL
)
""")

cursor.execute("""
INSERT INTO metro_line(line_name,line_color)
VALUES
('Orange Line','Orange'),
('Aqua Line','Blue')
""")

# -----------------------------
# STATION TABLE
# -----------------------------
cursor.execute("""
CREATE TABLE station(
    station_id INTEGER PRIMARY KEY AUTOINCREMENT,
    station_name TEXT NOT NULL,
    line_id INTEGER NOT NULL,
    station_order INTEGER NOT NULL,
    FOREIGN KEY(line_id) REFERENCES metro_line(line_id)
)
""")

# Orange Line
orange_stations = [
"Automotive Square",
"Nari Road",
"Indora Square",
"Kadbi Square",
"Gaddigodam Square",
"Kasturchand Park",
"Zero Mile Freedom Park",
"Sitabuldi",
"Congress Nagar",
"Rahate Colony",
"Ajni Square",
"Chhatrapati Square",
"Jaiprakash Nagar",
"Ujjwal Nagar",
"Airport",
"Airport South",
"New Airport",
"Khapri"
]

for i, station in enumerate(orange_stations, start=1):
    cursor.execute("""
    INSERT INTO station(station_name,line_id,station_order)
    VALUES(?,?,?)
    """, (station, 1, i))

# Aqua Line
aqua_stations = [
"Prajapati Nagar",
"Vaishno Devi Square",
"Ambedkar Square",
"Telephone Exchange",
"Chitar Oli Square",
"Agrasen Square",
"Dosar Vaishya Square",
"Nagpur Railway Station",
"Cotton Market",
"Sitabuldi",
"Jhansi Rani Square",
"Institute of Engineers",
"Shankar Nagar Square",
"LAD Square",
"Dharampeth College",
"Subhash Nagar",
"Rachana Ring Road Junction",
"Vasudev Nagar",
"Bansi Nagar",
"Lokmanya Nagar"
]

for i, station in enumerate(aqua_stations, start=1):
    cursor.execute("""
    INSERT INTO station(station_name,line_id,station_order)
    VALUES(?,?,?)
    """, (station, 2, i))

# -----------------------------
# TRAIN TABLE
# -----------------------------

cursor.execute("""
CREATE TABLE train(
    train_id INTEGER PRIMARY KEY AUTOINCREMENT,
    train_number TEXT UNIQUE NOT NULL,
    train_name TEXT NOT NULL,
    line_id INTEGER NOT NULL,
    FOREIGN KEY(line_id) REFERENCES metro_line(line_id)
)
""")

trains = [
("OR101","Orange Express",1),
("OR102","Orange Express",1),
("OR103","Orange Express",1),
("OR104","Orange Express",1),

("AQ201","Aqua Express",2),
("AQ202","Aqua Express",2),
("AQ203","Aqua Express",2),
("AQ204","Aqua Express",2)
]

cursor.executemany("""
INSERT INTO train(train_number,train_name,line_id)
VALUES(?,?,?)
""", trains)

# -----------------------------
# SCHEDULE TABLE
# -----------------------------
cursor.execute("""
CREATE TABLE schedule(
    schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,
    train_id INTEGER NOT NULL,
    station_id INTEGER NOT NULL,
    arrival_time TEXT,
    departure_time TEXT,
    FOREIGN KEY(train_id) REFERENCES train(train_id),
    FOREIGN KEY(station_id) REFERENCES station(station_id)
)
""")

from datetime import datetime, timedelta

def generate_schedule(train_id, line_id, start_time):

    stations = cursor.execute("""
        SELECT station_id
        FROM station
        WHERE line_id=?
        ORDER BY station_order
    """, (line_id,)).fetchall()

    current = datetime.strptime(start_time, "%H:%M")

    for station in stations:

        arrival = current.strftime("%H:%M")
        departure = (current + timedelta(minutes=1)).strftime("%H:%M")

        cursor.execute("""
            INSERT INTO schedule
            (train_id, station_id, arrival_time, departure_time)
            VALUES (?,?,?,?)
        """, (
            train_id,
            station[0],
            arrival,
            departure
        ))

        current += timedelta(minutes=2)

# ----------------------------------
# CALL THE FUNCTION HERE (OUTSIDE)
# ----------------------------------

# Orange Line
generate_schedule(1, 1, "08:00")
generate_schedule(2, 1, "08:20")
generate_schedule(3, 1, "08:40")
generate_schedule(4, 1, "09:00")

# Aqua Line
generate_schedule(5, 2, "08:05")
generate_schedule(6, 2, "08:25")
generate_schedule(7, 2, "08:45")
generate_schedule(8, 2, "09:05")

# ----------------------------
# BOOKING TABLE
# ----------------------------

cursor.execute("""
CREATE TABLE booking (

    booking_id INTEGER PRIMARY KEY AUTOINCREMENT,

    passenger_id INTEGER NOT NULL,

    train_id INTEGER NOT NULL,

    source_station TEXT NOT NULL,

    destination_station TEXT NOT NULL,

    journey_date TEXT NOT NULL,

    booking_date TEXT NOT NULL,

    fare REAL NOT NULL,

    passenger_count INTEGER DEFAULT 1,

    booking_status TEXT DEFAULT 'Confirmed',

    FOREIGN KEY(passenger_id) REFERENCES passenger(passenger_id),

    FOREIGN KEY(train_id) REFERENCES train(train_id)

)
""")

conn.commit()
conn.close()

print("====================================")
print("Nagpur Metro Database Created Successfully!")
print("Default Admin Credentials")
print("Username : admin")
print("Password : admin123")
print("====================================")