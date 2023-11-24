 
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
db = SQLAlchemy(app)

class Laptop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return '<Laptop %r>' % self.name

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    laptop_id = db.Column(db.Integer, db.ForeignKey('laptop.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return '<CartItem %r>' % self.id

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

@app.route('/')
def index():
    laptops = Laptop.query.all()
    return render_template('index.html', laptops=laptops)

@app.route('/product/<int:product_id>')
def product(product_id):
    laptop = Laptop.query.get_or_404(product_id)
    return render_template('product.html', laptop=laptop)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    laptop = Laptop.query.get_or_404(product_id)
    current_user = get_current_user()
    cart_item = CartItem(laptop_id=laptop.id, quantity=1, user_id=current_user.id)
    db.session.add(cart_item)
    db.session.commit()
    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    laptop = Laptop.query.get_or_404(product_id)
    current_user = get_current_user()
    cart_item = CartItem.query.filter_by(laptop_id=laptop.id, user_id=current_user.id).first_or_404()
    db.session.delete(cart_item)
    db.session.commit()
    return redirect(url_for('cart'))

@app.route('/update_cart_quantity/<int:product_id>/<int:quantity>')
def update_cart_quantity(product_id, quantity):
    laptop = Laptop.query.get_or_404(product_id)
    current_user = get_current_user()
    cart_item = CartItem.query.filter_by(laptop_id=laptop.id, user_id=current_user.id).first_or_404()
    cart_item.quantity = quantity
    db.session.commit()
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    current_user = get_current_user()
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total_price = 0
    for cart_item in cart_items:
        laptop = Laptop.query.get(cart_item.laptop_id)
        total_price += laptop.price * cart_item.quantity
    return render_template('cart.html', cart_items=cart_items, total_price=total_price)

@app.route('/checkout')
def checkout():
    current_user = get_current_user()
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total_price = 0
    for cart_item in cart_items:
        laptop = Laptop.query.get(cart_item.laptop_id)
        total_price += laptop.price * cart_item.quantity
    return render_template('checkout.html', cart_items=cart_items, total_price=total_price)

@app.route('/confirmation')
def confirmation():
    current_user = get_current_user()
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    for cart_item in cart_items:
        db.session.delete(cart_item)
    db.session.commit()
    return render_template('confirmation.html')

def get_current_user():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return user
    return None

if __name__ == '__main__':
    app.run(debug=True)
