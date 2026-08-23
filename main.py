from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user
)

from database import Session, Users, Products, Orders
from sqlalchemy.orm import joinedload
import os
from werkzeug.utils import secure_filename
app = Flask(__name__)

app.secret_key = "sakura_house_secret"




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

    return render_template("admin.html")

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
def menu():

    return render_template("menu.html")


@app.route("/admin/add-product", methods=["GET", "POST"])
@login_required
def add_product():

    if current_user.username != "Admin":
        return "Доступ заборонено", 403

    if request.method == "POST":

        name = request.form["name"]
        description = request.form["description"]
        price = request.form["price"]

        new_product = Products(
            name=name,
            description=description,
            price=float(price)
        )

        with Session() as session:
            session.add(new_product)
            session.commit()

        return redirect(url_for("admin"))

    return render_template("add_product.html")




@app.route("/add_to_cart", methods=["POST"])
@login_required
def add_to_cart():

    product_id = int(request.form["product_id"])


    session = Session()


    order = Orders(
        user_id=current_user.id,
        product_id=product_id,
        quantity=1
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
        user_id=current_user.id
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
@app.route("/payment")
@login_required
def payment():
    return render_template("payment.html")

if __name__ == "__main__":
    app.run(debug=True)