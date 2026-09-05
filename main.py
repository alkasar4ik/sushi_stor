
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user
)

from database import Session, Users, Products, Orders
from sqlalchemy.orm import joinedload

from datetime import datetime, timedelta

import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_caching import Cache

app = Flask(__name__)

app.secret_key = "sakura_house_secret"

cache = Cache(
    app,
    config={
        "CACHE_TYPE": "SimpleCache",
        "CACHE_DEFAULT_TIMEOUT": 250
    }
)




login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):

    session = Session()

    user = session.get(Users, int(user_id))

    session.close()

    return user




def is_admin():

    return (
        current_user.is_authenticated
        and current_user.username == "Admin"
    )


@app.route("/admin")
@login_required
def admin():

    if not is_admin():
        flash("Доступ заборонено")
        return redirect(url_for("main"))

    with Session() as session:

        products = session.query(Products).all()

    return render_template(
        "admin.html",
        products=products
    )




@app.route("/")
def main():

    return render_template("main.html")




@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        password2 = request.form["password2"]

        if password != password2:

            flash("Паролі не співпадають!")

            return redirect(url_for("register"))

        session = Session()

        existing_user = session.query(Users).filter(
            (Users.username == username) |
            (Users.email == email)
        ).first()

        if existing_user:

            session.close()

            flash("Такий username або email вже існує!")

            return redirect(url_for("register"))

        user = Users(
            username=username,
            email=email,
            password=password
        )

        session.add(user)

        session.commit()

        session.close()

        return redirect(url_for("login"))

    return render_template("register.html")




@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        session = Session()

        user = session.query(Users).filter_by(
            username=username
        ).first()

        session.close()

        if user and user.password == password:

            login_user(user)

            return redirect(url_for("profile"))

        flash("Неправильний логін або пароль")

    return render_template("login.html")




@app.route("/profile")
@login_required
def profile():

    return render_template(
        "profile.html",
        user=current_user
    )




@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(url_for("main"))



@app.route("/menu")
@cache.cached(timeout=300)
def menu():

    with Session() as session:
        products = session.query(Products).all()

    return render_template(
        "menu.html",
        products=products
    )




@app.route("/admin/add-product", methods=["GET", "POST"])
@login_required
def add_product():

    if current_user.username != "Admin":
        return "Доступ заборонено", 403

    if request.method == "POST":

        name = request.form["name"]
        description = request.form["description"]
        price = request.form["price"]
        category = request.form["category"]

        image = request.files["image"]


        if image.filename == "":
            flash("Виберіть фото товару")
            return redirect(url_for("add_product"))


        upload_folder = os.path.join(
            app.static_folder,
            "images"
        )

        os.makedirs(upload_folder, exist_ok=True)


        filename = secure_filename(image.filename)


        image.save(
            os.path.join(
                upload_folder,
                filename
            )
        )


        new_product = Products(
            name=name,
            description=description,
            price=float(price),
            image=filename,
            category=category
        )


        with Session() as session:

            session.add(new_product)

            session.commit()

        flash("Товар успішно додано!")

        return redirect(url_for("admin"))

    return render_template("add_product.html")


@app.route("/admin/delete-product/<int:product_id>", methods=["POST"])
@login_required
def delete_product(product_id):

    if current_user.username != "Admin":
        return "Доступ заборонено", 403

    with Session() as session:

        product = session.get(Products, product_id)

        if product:
            session.delete(product)
            session.commit()

    flash("Товар видалено!")

    return redirect(url_for("admin"))




@app.route("/add_to_cart", methods=["POST"])
@login_required
def add_to_cart():

    product_id = int(request.form["product_id"])

    session = Session()

    order = Orders(
        user_id=current_user.id,
        product_id=product_id,
        quantity=1,
        status="В корзине",
        created_at=datetime.now()
    )

    session.add(order)

    session.commit()

    session.close()

    return redirect(url_for("cart"))




@app.route("/cart")
@login_required
def cart():

    session = Session()

    orders = session.query(Orders).options(
        joinedload(Orders.product)
    ).filter_by(
        user_id=current_user.id,
        status="В корзине"
    ).all()

    total = 0

    for order in orders:

        total += order.product.price * order.quantity

    session.close()

    return render_template(
        "cart.html",
        orders=orders,
        total=total
    )




@app.route(
    "/remove_from_cart/<int:order_id>",
    methods=["POST"]
)
@login_required
def remove_from_cart(order_id):

    session = Session()

    order = session.query(Orders).filter_by(
        id=order_id,
        user_id=current_user.id,
        status="В корзине"
    ).first()

    if order:

        session.delete(order)

        session.commit()

    session.close()

    return redirect(url_for("cart"))




@app.route("/payment")
@login_required
def payment():

    session = Session()

    orders = session.query(Orders).options(
        joinedload(Orders.product)
    ).filter_by(
        user_id=current_user.id,
        status="В корзине"
    ).all()

    total = 0

    for order in orders:

        total += order.product.price * order.quantity

    session.close()

    if not orders:

        flash("Корзина пуста")

        return redirect(url_for("cart"))

    return render_template(
        "payment.html",
        orders=orders,
        total=total
    )




@app.route("/confirm_order", methods=["POST"])
@login_required
def confirm_order():

    session = Session()

    orders = session.query(Orders).filter_by(
        user_id=current_user.id,
        status="В корзине"
    ).all()

    if not orders:

        session.close()

        flash("Корзина пуста")

        return redirect(url_for("cart"))


    for order in orders:

        order.status = "В обработке"
        order.created_at = datetime.now()

    session.commit()

    session.close()

    flash("Заказ успешно оформлен!")

    return redirect(url_for("order_history"))




@app.route("/orders")
@login_required
def order_history():

    session = Session()

    orders = session.query(Orders).options(
        joinedload(Orders.product)
    ).filter(
        Orders.user_id == current_user.id,
        Orders.status != "В корзине"
    ).order_by(
        Orders.created_at.desc()
    ).all()


    changed = False

    for order in orders:

        if order.status == "В обробці":

            time_passed = datetime.now() - order.created_at

            if time_passed >= timedelta(minutes=5):

                order.status = "Отправлено"

                changed = True

    if changed:

        session.commit()

    session.close()

    return render_template(
        "orders.html",
        orders=orders
    )




if __name__ == "__main__":
    app.run(debug=True)

