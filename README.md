🛒 GroceryHub – Online Grocery Store Web Application

A full-stack online grocery shopping web application built using Python Flask, HTML, CSS, JavaScript, and SQLite.
This project allows users to browse grocery products, manage a shopping cart, and place orders with a clean, responsive UI.

📌 Features
👤 User Module

User Registration & Login

Secure authentication

View grocery products

Add products to cart

Increase / Decrease quantity

Remove items from cart

Checkout & order confirmation

View order history

🛍️ Product Module

Product listing (Fruits, Vegetables, Essentials, etc.)

Stock availability

Price display in INR (₹)

🖥️ UI Features

Fully responsive design (Mobile / Tablet / Desktop)

Clean card-based product layout

Interactive cart using JavaScript

Modern UI with green & white theme

🛠️ Technologies Used
Layer	Technology
Frontend	HTML, CSS, JavaScript
Backend	Python, Flask
Database	SQLite
ORM	Flask-SQLAlchemy
Authentication	Flask-Login
Version Control	Git & GitHub
📂 Project Structure
GROCERY_STORE/
│
├── app.py
├── config.py
├── database.py
├── requirements.txt
├── grocery.db
│
├── static/
│   └── css/
│       └── style.css
│
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── products.html
│   ├── cart.html
│   ├── orders.html
│   ├── payment.html
│   └── success.html

⚙️ Installation & Setup
1️⃣ Clone the repository
git clone https://github.com/your-username/groceryhub.git
cd groceryhub

2️⃣ Install dependencies
pip install -r requirements.txt

3️⃣ Initialize database
python database.py

4️⃣ Run the application
python app.py

5️⃣ Open in browser
http://127.0.0.1:5000

🧪 Sample Login (if seeded)
Email: john@example.com
Password: password123

🎥 Project Demo

This project is suitable for:

Final year project

Mini project

Portfolio project

YouTube tutorial demonstration

📱 Responsive Design

The application automatically adapts to:

Desktop

Tablet

Mobile devices

🔐 Security

Password hashing using Werkzeug

Session-based authentication

Protected routes

🚀 Future Enhancements

Online payment integration (UPI / Razorpay)

Admin dashboard

Product search & filters

Invoice PDF download

Email notifications

👩‍💻 Developed By

Elamathi
MCA Student | Python Developer


📜 License

This project is for educational purposes only.



