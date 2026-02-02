from flask import Flask, render_template, request, redirect, session, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# ==================== APP CONFIG ====================
app = Flask(__name__)
app.secret_key = "your_secret_key"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///grocery.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ==================== DATABASE MODELS ====================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    stock = db.Column(db.Integer, default=100)
    image = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship("Product")

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default="completed")
    order_date = db.Column(db.DateTime, default=datetime.utcnow)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    quantity = db.Column(db.Integer)
    price = db.Column(db.Float)

# ==================== ROUTES ====================
@app.route("/")
def index():
    return redirect(url_for("products")) if "user_id" in session else redirect(url_for("login"))

# -------- REGISTER --------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if request.form["password"] != request.form["confirm_password"]:
            return render_template("register.html", error="Passwords do not match")

        if User.query.filter_by(email=request.form["email"]).first():
            return render_template("register.html", error="Email already exists")

        user = User(
            name=request.form["name"],
            email=request.form["email"],
            password=generate_password_hash(request.form["password"])
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login"))

    return render_template("register.html")

# -------- LOGIN --------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(email=request.form["email"]).first()
        if user and check_password_hash(user.password, request.form["password"]):
            session["user_id"] = user.id
            session["user_name"] = user.name
            return redirect(url_for("products"))
        return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")

# -------- LOGOUT --------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# -------- PRODUCTS --------
@app.route("/products")
def products():
    if "user_id" not in session:
        return redirect(url_for("login"))

    products = Product.query.all()
    cart_count = Cart.query.filter_by(user_id=session["user_id"]).count()
    return render_template("products.html", products=products, cart_count=cart_count)

# -------- ADD TO CART --------
@app.route("/add-to-cart/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    if "user_id" not in session:
        return jsonify(success=False), 401

    item = Cart.query.filter_by(
        user_id=session["user_id"],
        product_id=product_id
    ).first()

    if item:
        item.quantity += 1
    else:
        db.session.add(Cart(
            user_id=session["user_id"],
            product_id=product_id,
            quantity=1
        ))

    db.session.commit()
    return jsonify(success=True)

# -------- CART --------
@app.route("/cart")
def cart():
    if "user_id" not in session:
        return redirect(url_for("login"))

    items = Cart.query.filter_by(user_id=session["user_id"]).all()
    total = sum(i.product.price * i.quantity for i in items)
    return render_template("cart.html", cart_items=items, total=total)

# -------- UPDATE QUANTITY --------
@app.route("/update_quantity/<int:cart_id>", methods=["POST"])
def update_quantity(cart_id):
    if 'user_id' not in session:
        return jsonify(success=False, message="Login required"), 401

    data = request.get_json()
    quantity = data.get("quantity")

    if not isinstance(quantity, int) or quantity < 1:
        return jsonify(success=False, message="Invalid quantity"), 400

    cart_item = Cart.query.filter_by(
        id=cart_id,
        user_id=session['user_id']
    ).first()

    if not cart_item:
        return jsonify(success=False, message="Item not found"), 404

    cart_item.quantity = quantity
    db.session.commit()

    return jsonify(success=True)

# -------- REMOVE ITEM --------
@app.route("/remove_from_cart/<int:cart_id>", methods=["POST"])
def remove_from_cart(cart_id):
    if 'user_id' not in session:
        return jsonify(success=False, message="Login required"), 401

    cart_item = Cart.query.filter_by(
        id=cart_id,
        user_id=session['user_id']
    ).first()

    if not cart_item:
        return jsonify(success=False, message="Item not found"), 404

    db.session.delete(cart_item)
    db.session.commit()

    return jsonify(success=True)


# -------- CHECKOUT --------
@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    if "user_id" not in session:
        return redirect(url_for("login"))

    items = Cart.query.filter_by(user_id=session["user_id"]).all()
    total = sum(i.product.price * i.quantity for i in items)

    if request.method == "POST" and items:
        order = Order(user_id=session["user_id"], total_amount=total)
        db.session.add(order)
        db.session.flush()

        for i in items:
            db.session.add(OrderItem(
                order_id=order.id,
                product_id=i.product_id,
                quantity=i.quantity,
                price=i.product.price
            ))

        Cart.query.filter_by(user_id=session["user_id"]).delete()
        db.session.commit()
        return render_template("success.html", order=order)

    return render_template("checkout.html", cart_items=items, total=total)

# -------- ORDERS --------
@app.route("/orders")
def orders():
    if "user_id" not in session:
        return redirect(url_for("login"))

    orders = Order.query.filter_by(user_id=session["user_id"]).all()
    return render_template("orders.html", orders=orders)

# ==================== RUN & SEED DATA ====================
if __name__ == "__main__":
    with app.app_context():
        # Create tables
        db.create_all()

        # Seed products only once
        if Product.query.count() == 0:
            products_data = [
                {
                    "name": "Fresh Carrots",
                    "description": "Organic fresh carrots, rich in Vitamin A",
                    "price": 45.00,
                    "category": "Vegetables",
                    "image": "https://images.unsplash.com/photo-1598170845058-78131a90f4bf?w=400&h=300&fit=crop",
                    "stock": 50
                },
                {
                    "name": "Red Onions",
                    "description": "Premium red onions, great for cooking",
                    "price": 60.00,
                    "category": "Vegetables",
                    "image": "https://images.unsplash.com/photo-1580201092675-a0a6a6cafbb1?w=400&h=300&fit=crop",
                    "stock": 40
                },
                {
                    "name": "Cucumber",
                    "description": "Fresh green cucumbers, perfect for salads",
                    "price": 25.00,
                    "category": "Vegetables",
                    "image": "https://images.unsplash.com/photo-1568639658-44f2a6e61f5c?w=400&h=300&fit=crop",
                    "stock": 60
                },
                {
                    "name": "Tomatoes",
                    "description": "Farm fresh tomatoes, juicy and ripe",
                    "price": 40.00,
                    "category": "Vegetables",
                    "image": "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=400&h=300&fit=crop",
                    "stock": 45
                },
                {
                    "name": "Broccoli",
                    "description": "Fresh broccoli, packed with nutrients",
                    "price": 80.00,
                    "category": "Vegetables",
                    "image": "https://images.unsplash.com/photo-1459411621453-7b03977f4c4e?w=400&h=300&fit=crop",
                    "stock": 30
                },
                {
                    "name": "Apples",
                    "description": "Red delicious apples, sweet and crisp",
                    "price": 120.00,
                    "category": "Fruits",
                    "image": "https://images.unsplash.com/photo-1568702846914-96b305d2aaeb?w=400&h=300&fit=crop",
                    "stock": 35
                },
                {
                    "name": "Bananas",
                    "description": "Ripe bananas, perfect for smoothies",
                    "price": 35.00,
                    "category": "Fruits",
                    "image": "https://images.unsplash.com/photo-1603833665858-e61d17a86224?w=400&h=300&fit=crop",
                    "stock": 55
                },
                {
                    "name": "Butter",
                    "description": "Amul butter 500g, creamy and fresh",
                    "price": 250.00,
                    "category": "Dairy",
                    "image": "https://images.unsplash.com/photo-1557838923-2985c318be48?w=400&h=300&fit=crop",
                    "stock": 25
                },
                {
                    "name": "Milk",
                    "description": "Fresh cow milk 1L, pasteurized",
                    "price": 60.00,
                    "category": "Dairy",
                    "image": "https://images.unsplash.com/photo-1563636619-e9143da7973b?w=400&h=300&fit=crop",
                    "stock": 40
                },
                {
                    "name": "Bread",
                    "description": "Whole wheat bread, fresh baked",
                    "price": 35.00,
                    "category": "Bakery",
                    "image": "https://images.unsplash.com/photo-1549931319-a545dcf3bc73?w=400&h=300&fit=crop",
                    "stock": 40
                }
            ]

            for prod in products_data:
                db.session.add(Product(**prod))

            db.session.commit()
            print("✅ Products seeded successfully")

    app.run(debug=True)
