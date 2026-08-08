# 🚇 Nagpur Metro Management System

A web-based Nagpur Metro Management System developed using **Python Flask, SQLite, HTML, CSS, JavaScript, and Bootstrap**.

The system provides passengers with an easy-to-use interface for searching metro routes, checking fares, booking tickets, making simulated QR payments, and viewing booking history.

---

## 📌 Project Overview

The Nagpur Metro Management System is designed to simplify metro ticket booking and passenger services through a web application.

The application provides:

- Metro route search
- Direct and interchange route handling
- Fare calculation
- Passenger ticket booking
- Number of passenger selection
- QR-based payment simulation
- Digital metro ticket
- Booking history
- Passenger dashboard
- Route map
- Recharge and offers section
- Login and registration
- Admin management features

---

## ✨ Features

### 👤 Passenger Features

- Passenger registration
- Secure login and logout
- Passenger dashboard
- Search metro trains
- Select source and destination
- Select journey date
- Search direct metro routes
- Search interchange routes
- Select number of passengers
- Automatic fare calculation
- Book metro tickets
- QR-based payment simulation
- Generate digital ticket
- View booking history
- Print ticket

---

### 🚇 Metro Features

- Orange Line
- Aqua Line
- Station information
- Train information
- Train schedules
- Interchange support at Sitabuldi
- Route search
- Fare calculation

---

### 💳 Payment Features

The application provides a simple simulated payment process.

Booking flow:

Search Train

↓

Book Ticket

↓

Payment QR

↓

I Have Paid

↓

Payment Successful

↓

Ticket Generated

The payment system is designed for demonstration purposes and does not process real financial transactions.

---

### 🎫 Digital Ticket

After successful payment, the system generates a digital metro ticket containing:

- Booking ID
- Passenger name
- Number of passengers
- Train number
- Source station
- Destination station
- Journey date
- Booking date
- Total fare
- Booking status
- Ticket QR code

---

### 🗺 Route Map

The application provides a route map interface showing the Nagpur Metro network and its major stations.

Users can access the route map directly from the navigation bar.

---

### 💰 Fare Calculator

Passengers can calculate the estimated metro fare based on their journey.

The system also automatically calculates the total fare according to the selected number of passengers.

Example:

```text
Fare per passenger = ₹30
Passengers = 3

Total Fare = ₹90
