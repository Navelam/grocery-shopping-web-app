from app import app, db
from app import User, Product
from werkzeug.security import generate_password_hash

def init_db():
    with app.app_context():
        db.create_all()

        # Clear old data
        User.query.delete()
        Product.query.delete()

        # Create user
        user1 = User(
            name='John Doe',
            email='john@example.com',
            password=generate_password_hash('password123')
        )

        # Add many products
        products = [
            Product(name='Carrot', price=45, category='Vegetables', stock=40),
            Product(name='Onions', price=40, category='Vegetables', stock=55),
           Product(name='Cucumber', price=35, category='Vegetables', stock=50),
            Product(name='Tomatoes', price=80, category='Vegetables', stock=40),
            Product(name='broccoli', price=50, category='Vegetables', stock=70),
            Product(name='Apples', price=80, category='Fruits', stock=40),
            Product(name='Bananas', price=50, category='Fruits', stock=70),
            Product(name='Cheese', price=150, category='Dairy', stock=20),
            Product(name='Milk', price=60, category='Dairy', stock=30),
            
        ]

        db.session.add(user1)
        db.session.add_all(products)
        db.session.commit()

        print("Database initialized successfully")

if __name__ == "__main__":
    init_db()
