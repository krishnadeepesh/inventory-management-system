# Inventory Management System (Django + MySQL)

A web-based Inventory Management System built using **Django Framework** with **MySQL database integration**.  
The system helps manage products, stock, and purchase requests efficiently using role-based access control.

---

## Project Overview

This system is designed to simplify inventory handling in an organization by providing a centralized platform for managing products and purchase requests.

It supports three types of users:

- **Admin**
- **Manager**
- **User**

All users access the system through a **common login page** and are redirected to their respective dashboards based on their role.

---

## Key Features

### Admin
- View all products and categories
- Add/Delete Managers
- Monitor user purchase requests
- View overall system activity and statistics

---

### Manager
- Add/Delete categories
- Add/Delete products
- Manage stock availability
- Accept or Reject purchase requests from users
- Communicate with users regarding orders

---

### User
- View product details and stock availability
- Send purchase requests for products
- Track request status (Pending / Approved / Rejected)
- Communicate with assigned manager

---

## Tech Stack

- **Backend:** Python (Django)
- **Database:** MySQL
- **Frontend:** HTML, CSS, JavaScript
- **Version Control:** Git & GitHub



