from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from datetime import datetime
from utils import search_train

app = Flask(__name__)
app.secret_key = "nagpurmetro123"

DATABASE = "metro.db"


def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def home():
    return render_template("index.html")
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        password = request.form["password"]

        conn = get_connection()

        try:

            conn.execute("""
            INSERT INTO passenger(name,email,phone,password)
            VALUES(?,?,?,?)
            """, (name, email, phone, password))

            conn.commit()

            flash("Registration Successful", "success")

            conn.close()

            return redirect(url_for("login"))

        except:

            flash("Email already exists", "danger")

            conn.close()

    return render_template("register.html")
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = get_connection()

        passenger = conn.execute("""
        SELECT *
        FROM passenger
        WHERE email=? AND password=?
        """, (email, password)).fetchone()

        conn.close()

        if passenger:

            session["passenger_id"] = passenger["passenger_id"]
            session["passenger_name"] = passenger["name"]

            return redirect(url_for("passenger_dashboard"))

        flash("Invalid Email or Password", "danger")

    return render_template("login.html")
@app.route("/passenger_dashboard")
def passenger_dashboard():

    if "passenger_id" not in session:
        return redirect(url_for("login"))

    conn = get_connection()

    stations = conn.execute("""
    SELECT station_name
    FROM station
    ORDER BY station_name
    """).fetchall()

    conn.close()

    return render_template(
        "passenger_dashboard.html",
        stations=stations,
        passenger=session["passenger_name"]
    )
# ----------------------------
# Search Metro
# ----------------------------

@app.route("/search", methods=["POST"])
def search():

    if "passenger_id" not in session:
        return redirect(url_for("login"))

    source = request.form["source"]
    destination = request.form["destination"]
    journey_date = request.form["journey_date"]

    if source == destination:

        flash("Source and Destination cannot be the same.", "danger")

        return redirect(url_for("passenger_dashboard"))

    results = search_train(source, destination)

    if not results:

        flash("No trains found.", "danger")

        return redirect(url_for("passenger_dashboard"))

    return render_template(
        "search_results.html",
        results=results,
        source=source,
        destination=destination,
        journey_date=journey_date
    )
# ----------------------------
# Book Ticket
# ----------------------------

from datetime import datetime

@app.route("/book_ticket", methods=["POST"])
def book_ticket():

    if "passenger_id" not in session:
        return redirect(url_for("login", next=request.url))

    passengers = request.form.get("passengers", "1")

    session["pending_booking"] = {
        "train": request.form["train"],
        "source": request.form["source"],
        "destination": request.form["destination"],
        "journey_date": request.form["journey_date"],
        "fare": request.form["fare"],
        "passengers": passengers
    }

    return redirect(url_for("payment_qr"))

@app.route("/payment_qr")
def payment_qr():

    if "passenger_id" not in session:
        return redirect(url_for("login"))

    if "pending_booking" not in session:
        flash("No booking found.", "warning")
        return redirect(url_for("passenger_dashboard"))

    booking = session["pending_booking"]

    return render_template(
        "payment_qr.html",
        booking=booking
    )

@app.route("/confirm_payment")
def confirm_payment():

    if "passenger_id" not in session:
        return redirect(url_for("login"))

    if "pending_booking" not in session:
        flash("No booking found.", "warning")
        return redirect(url_for("passenger_dashboard"))

    booking = session["pending_booking"]

    conn = get_connection()

    train = conn.execute("""
        SELECT train_id
        FROM train
        WHERE train_number=?
    """, (booking["train"],)).fetchone()

    booking_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO booking(
            passenger_id,
            train_id,
            source_station,
            destination_station,
            journey_date,
            booking_date,
            fare,
            passenger_count,
            booking_status
        )
        VALUES(?,?,?,?,?,?,?,?,?)
    """, (

        session["passenger_id"],
        train["train_id"],
        booking["source"],
        booking["destination"],
        booking["journey_date"],
        booking_date,
        booking["fare"],
        booking["passengers"],
        "Confirmed"

    ))

    conn.commit()

    booking_id = cursor.lastrowid

    conn.close()

    session.pop("pending_booking", None)

    flash("Payment Successful!", "success")

    return redirect(url_for("view_ticket", booking_id=booking_id))

@app.route("/booking_history")
def booking_history():

    if "passenger_id" not in session:
        return redirect(url_for("login"))

    conn = get_connection()

    bookings = conn.execute("""

    SELECT

    booking.*,

    train.train_number

    FROM booking

    JOIN train

    ON booking.train_id=train.train_id

    WHERE passenger_id=?

    ORDER BY booking_id DESC

    """,(session["passenger_id"],)).fetchall()

    conn.close()

    return render_template(

        "booking_history.html",

        bookings=bookings

    )
# ----------------------------
# View Ticket
# ----------------------------

@app.route("/ticket/<int:booking_id>")
def view_ticket(booking_id):

    if "passenger_id" not in session:
        return redirect(url_for("login"))

    conn = get_connection()

    booking = conn.execute("""
        SELECT
            booking.booking_id,
            booking.source_station,
            booking.destination_station,
            booking.journey_date,
            booking.booking_date,
            booking.fare,
            booking.booking_status,
            booking.passenger_count,
            train.train_number,
            passenger.name AS passenger_name
        FROM booking
        JOIN train
            ON booking.train_id = train.train_id
        JOIN passenger
            ON booking.passenger_id = passenger.passenger_id
        WHERE booking.booking_id = ?
    """, (booking_id,)).fetchone()

    conn.close()

    if booking is None:
        flash("Ticket not found.", "danger")
        return redirect(url_for("booking_history"))

    return render_template(
        "ticket.html",
        booking=booking
    )
@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_connection()

        admin = conn.execute("""
        SELECT *
        FROM admin
        WHERE username=? AND password=?
        """, (username, password)).fetchone()

        conn.close()

        if admin:

            session["admin_id"] = admin["admin_id"]
            session["admin_username"] = admin["username"]

            return redirect(url_for("admin_dashboard"))

        flash("Invalid Username or Password", "danger")

    return render_template("admin_login.html")
@app.route("/admin_dashboard")
def admin_dashboard():

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    conn = get_connection()

    total_passengers = conn.execute(
        "SELECT COUNT(*) FROM passenger"
    ).fetchone()[0]

    total_stations = conn.execute(
        "SELECT COUNT(*) FROM station"
    ).fetchone()[0]

    total_trains = conn.execute(
        "SELECT COUNT(*) FROM train"
    ).fetchone()[0]

    total_bookings = conn.execute(
        "SELECT COUNT(*) FROM booking"
    ).fetchone()[0]

    conn.close()

    return render_template(
        "admin_dashboard.html",
        total_passengers=total_passengers,
        total_stations=total_stations,
        total_trains=total_trains,
        total_bookings=total_bookings
    )

@app.route("/route_map")
def route_map():
    return render_template("route_map.html")

@app.route("/fare_calculator", methods=["GET", "POST"])
def fare_calculator():

    conn = get_connection()

    stations = conn.execute("""
        SELECT station_name
        FROM station
        ORDER BY station_name
    """).fetchall()

    result = None

    if request.method == "POST":

        source = request.form["source"]
        destination = request.form["destination"]

        journey = search_train(source, destination)

        if journey:

            result = journey[0]

    conn.close()

    return render_template(
        "fare_calculator.html",
        stations=stations,
        result=result
    )

@app.route("/offers")
def offers():
    return render_template("offers.html")

@app.route("/payment/<plan>")
def payment(plan):

    plans = {
        "student": {
            "name": "Student Smart Card",
            "amount": 200
        },
        "monthly": {
            "name": "Monthly Pass",
            "amount": 800
        },
        "tourist": {
            "name": "Tourist Pass",
            "amount": 100
        }
    }

    if plan not in plans:
        return redirect(url_for("offers"))

    return render_template(
        "payment.html",
        plan=plans[plan]
    )

from datetime import datetime
import random

@app.route("/payment_success")
def payment_success():

    transaction_id = "NM" + str(random.randint(100000000,999999999))

    payment_date = datetime.now().strftime("%d %B %Y")

    payment_time = datetime.now().strftime("%I:%M %p")

    return render_template(

        "payment_success.html",

        transaction_id=transaction_id,

        payment_date=payment_date,

        payment_time=payment_time

    )

@app.route("/logout")
def logout():

    session.clear()

    flash("Logged out successfully", "success")

    return redirect(url_for("home"))

@app.route("/stations")
def stations():

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    conn = get_connection()

    stations = conn.execute("""
    SELECT
        station.station_id,
        station.station_name,
        metro_line.line_name
    FROM station
    JOIN metro_line
    ON station.line_id = metro_line.line_id
    ORDER BY metro_line.line_name, station.station_order
    """).fetchall()

    conn.close()

    return render_template(
        "stations.html",
        stations=stations
    )
@app.route("/add_station", methods=["GET", "POST"])
def add_station():

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    conn = get_connection()

    if request.method == "POST":

        station_name = request.form["station_name"]
        line_id = request.form["line_id"]
        station_order = request.form["station_order"]

        conn.execute("""
        INSERT INTO station
        (station_name,line_id,station_order)
        VALUES(?,?,?)
        """, (station_name, line_id, station_order))

        conn.commit()

        conn.close()

        flash("Station Added Successfully", "success")

        return redirect(url_for("stations"))

    lines = conn.execute("SELECT * FROM metro_line").fetchall()

    conn.close()

    return render_template(
        "add_station.html",
        lines=lines
    )
@app.route("/delete_station/<int:station_id>")
def delete_station(station_id):

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    conn = get_connection()

    conn.execute(
        "DELETE FROM station WHERE station_id=?",
        (station_id,)
    )

    conn.commit()

    conn.close()

    flash("Station Deleted Successfully", "success")

    return redirect(url_for("stations"))
@app.route("/trains")
def trains():

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    conn = get_connection()

    trains = conn.execute("""
    SELECT
        train.train_id,
        train.train_number,
        train.train_name,
        metro_line.line_name
    FROM train
    JOIN metro_line
    ON train.line_id = metro_line.line_id
    ORDER BY train.train_number
    """).fetchall()

    conn.close()

    return render_template(
        "trains.html",
        trains=trains
    )
@app.route("/add_train", methods=["GET", "POST"])
def add_train():

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    conn = get_connection()

    if request.method == "POST":

        train_number = request.form["train_number"]
        train_name = request.form["train_name"]
        line_id = request.form["line_id"]

        conn.execute("""
        INSERT INTO train(train_number,train_name,line_id)
        VALUES(?,?,?)
        """,(train_number,train_name,line_id))

        conn.commit()

        flash("Train Added Successfully","success")

        conn.close()

        return redirect(url_for("trains"))

    lines = conn.execute("SELECT * FROM metro_line").fetchall()

    conn.close()

    return render_template(
        "add_train.html",
        lines=lines
    )
@app.route("/delete_train/<int:train_id>")
def delete_train(train_id):

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    conn = get_connection()

    conn.execute(
        "DELETE FROM train WHERE train_id=?",
        (train_id,)
    )

    conn.commit()

    conn.close()

    flash("Train Deleted Successfully","success")

    return redirect(url_for("trains"))
@app.route("/schedules")
def schedules():

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    conn = get_connection()

    schedules = conn.execute("""

    SELECT

    schedule.schedule_id,

    train.train_number,

    station.station_name,

    schedule.arrival_time,

    schedule.departure_time

    FROM schedule

    JOIN train

    ON schedule.train_id=train.train_id

    JOIN station

    ON schedule.station_id=station.station_id

    ORDER BY train.train_number

    """).fetchall()

    conn.close()

    return render_template(
        "schedules.html",
        schedules=schedules
    )
@app.route("/add_schedule", methods=["GET","POST"])
def add_schedule():

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    conn = get_connection()

    if request.method=="POST":

        train_id=request.form["train_id"]
        station_id=request.form["station_id"]
        arrival=request.form["arrival_time"]
        departure=request.form["departure_time"]

        conn.execute("""

        INSERT INTO schedule
        (train_id,station_id,arrival_time,departure_time)

        VALUES(?,?,?,?)

        """,(train_id,station_id,arrival,departure))

        conn.commit()

        flash("Schedule Added Successfully","success")

        conn.close()

        return redirect(url_for("schedules"))

    trains=conn.execute(
        "SELECT * FROM train"
    ).fetchall()

    stations=conn.execute(
        "SELECT * FROM station"
    ).fetchall()

    conn.close()

    return render_template(
        "add_schedule.html",
        trains=trains,
        stations=stations
    )
@app.route("/delete_schedule/<int:schedule_id>")
def delete_schedule(schedule_id):

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    conn=get_connection()

    conn.execute(
        "DELETE FROM schedule WHERE schedule_id=?",
        (schedule_id,)
    )

    conn.commit()

    conn.close()

    flash("Schedule Deleted Successfully","success")

    return redirect(url_for("schedules"))
if __name__ == "__main__":
    app.run(debug=True)