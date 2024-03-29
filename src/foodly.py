from flask import Flask, render_template, redirect, url_for, make_response, request
from flask import flash
from flask_bootstrap import Bootstrap
from db_manager import Item, Product, Order

import argparse
import os
import db_manager
import forms
import secrets

app = Flask(__name__)


def configure_flask():       
    app.config.from_pyfile("secret.py")
    Bootstrap(app)


def sum_current_items(items: list[Item]) -> int:
    sum = 0
    for item in items:
        cost = item.product.cost
        sum += cost

    return sum

def get_current_items(order_id: int) -> list[Item]:
    current_items = []

    if order_id is not None:
        current_items = db_manager.get_items_from_order(order_id)
    
    return current_items


@app.route("/item/<int:item_id>", methods=["GET", "POST"])
def item(item_id: int):
    
    order_id = request.cookies.get('order_id')
    item = db_manager.get_item(item_id, order_id)

    if item is None:
        error_code = 404
        error_message = "Item not found"
        template = render_template("errors/404.html", 	error_code=error_code, 
                                                        error_message=error_message)
        return template

    # render item template
    form = forms.ItemDietForm()

    if form.validate_on_submit():
        diet = form.diet.data
        db_manager.set_diet(item_id, diet)
        return redirect(url_for("bar"))
        
    return render_template("item.html", form = form,
                                        item=item)
        


@app.route("/remove_order")
def remove_order():
    order_id = request.cookies.get("order_id")
    href = redirect(url_for("bar"))  
    resp = make_response(href)
    
    if order_id is not None:
        db_manager.remove_order(order_id)
        resp.delete_cookie("order_id")
    
    return resp
    

@app.route("/remove_item/<int:item_id>")
def remove_item(item_id: int):
    order_id = request.cookies.get("order_id")
    
    if not db_manager.item_in_order(order_id, item_id):
        code = 401
        message = "You don't have access to remove this order"
        return render_template("erros/404.html", error_code = code, error_message = message)

    if order_id is not None:
        db_manager.remove_item(item_id)

    return redirect(url_for("bar"))


@app.route("/add_to_cart/<int:product_id>", methods=["GET"])
def add_to_cart(product_id: int):
    order_id = request.cookies.get("order_id")
    
    if order_id is not None:
        db_manager.create_item(product_id, order_id)

    return redirect(url_for("bar"))





@app.route("/kitchen", methods=["GET", "POST"])
def kitchen():
    orders_ready, orders_begin_prepared = db_manager.get_active_orders() # tror inte att vi kommer att behöva denna

    orders_placed = db_manager.get_placed_orders()
    orders_cooking = db_manager.get_cooking_orders()
    orders_done = db_manager.get_done_orders()

    return render_template("kitchen.html", orders_begin_prepared = orders_begin_prepared,
                            orders_ready = orders_ready,
                            orders_placed=orders_placed,
                            orders_cooking=orders_cooking,
                            orders_done=orders_done)

@app.route("/status/<int:order_id>", methods=["GET","POST"])
def status(order_id: int):
    order = db_manager.get_any_order(order_id)

    if order is None:
        code = 404
        message = "Order not found" 
        return render_template("errors/404.html",
                                error_code = code,
                                error_message = message)

    return render_template("status.html", order = order)


@app.route("/statuscooking/<int:order_id>", methods=["GET"])
def statuscooking(order_id: int):
    order_status_cooking = db_manager.ORDER_STATUS_COOKING
    db_manager.update_status(order_id, order_status_cooking)
    return redirect(url_for("kitchen"))


@app.route("/statusdone/<int:order_id>", methods=["GET"])
def statusdone(order_id: int):
    order_status_done = db_manager.ORDER_STATUS_DONE
    db_manager.update_status(order_id, order_status_done)
    return redirect(url_for("kitchen"))









@app.route("/order/<int:order_id>", methods=["GET"])
def order(order_id: int):

    order = db_manager.get_order(order_id)

    if order is None:
        code = 404
        message = "Order not found" 
        return render_template("errors/404.html",
                                error_code = code,
                                error_message = message)

    return render_template("order.html", order = order)


@app.route("/bar", methods=["GET", "POST"])
def bar():

    form = forms.BarOrderForm()

    products = db_manager.get_all_products()
    order_id = request.cookies.get('order_id')
    current_items = get_current_items(order_id)
    item_sum = sum_current_items(current_items)

    template = render_template('bar.html', 	form = form, 
                                products = products, 
                                current_items = current_items,
                                item_sum = item_sum)
    resp = make_response(template)

    if order_id is None or not db_manager.order_exists(order_id):
        order_id = db_manager.create_order()
        resp.set_cookie('order_id', str(order_id))

    
    if form.validate_on_submit():
        
        # Zero items in cart
        if item_sum == 0:
            return redirect(url_for("bar"))
        
        handled_by = form.handled_by.data
        db_manager.place_order(order_id, handled_by)
        href = redirect(url_for("order", order_id = order_id))
        resp = make_response(href)
        resp.delete_cookie("order_id")
        
        return resp


    return resp


@app.route("/", methods=["GET"])
def index():
    
    orders_ready, orders_begin_prepared = db_manager.get_active_orders()
    return render_template("index.html", 
                            orders_begin_prepared = orders_begin_prepared,
                            orders_ready = orders_ready)


def start_development_server(port: int):
    app.run(port=port)


def start_production_server(port: int):
    pass
    # TODO

def generate_secret_key() -> str:
    key = secrets.token_urlsafe(40)
    return key    

def store_secret_key(key: str):
    file = open("secret.py", "wt")
    payload = f"SECRET_KEY = \"{key}\""
    file.write(payload)
    file.close()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="An easy order management system",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "-p", "--port",
        type=int, 
        nargs=1,
        default=5000,
        help="Port to listen on")

    parser.add_argument(
        "-k", "--generate-key",
        action="store_true",
        help="Generate a new secure token"
    )

    parser.add_argument(
            "--production", 
            action="store_true", 
            help="Use production environment")


    args = parser.parse_args()
    port = args.port

    if args.generate_key:
        print("Generating new key...")
        key = generate_secret_key()
        store_secret_key(key)
        print("Done!")
        exit(0)
        

    configure_flask()
    # db_manager.drop_all_tables()
    db_manager.create_tables()
    db_manager.add_products()

    if args.production:
        start_production_server(port)
    else:
        start_development_server(port)



