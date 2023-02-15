from flask import Flask, render_template, redirect, url_for, make_response, request
from flask_bootstrap import Bootstrap

import os
import db_manager
import forms

app = Flask(__name__)
app.config["SECRET_KEY"] = str(os.urandom(20).hex())
Bootstrap(app)


def sum_current_items(items: list[tuple]) -> int:
	sum = 0
	for item in items:
		cost = item[3]
		sum += cost

	return sum

def get_current_items(order_id: int) -> list[tuple]:
	current_items = []

	if order_id is not None:
		current_items = db_manager.get_items_from_order(order_id)
	
	return current_items

@app.route("/remove_order")
def remove_order():
	order_id = request.cookies.get("order_id")
	href = redirect(url_for("bar"))  
	resp = make_response(href)
	
	if order_id is not None:
		db_manager.remove_order(order_id)
		resp.delete_cookie("order_id")
	
	return resp
	

@app.route("/add_to_cart/<int:product_id>", methods=["GET"])
def add_to_cart(product_id: int):
	order_id = request.cookies.get('order_id')
	
	if order_id is not None:
		db_manager.create_item(product_id, order_id)

	return redirect(url_for("bar"))


@app.route("/kitchen", methods=["GET", "POST"])
def kitchen():
	return "<h1>KITCHEN </h1>"


@app.route("/bar", methods=["GET", "POST"])
def bar():

	form = forms.BarOrderForm()

	products = db_manager.get_all_products()
	order_id = request.cookies.get('order_id')
	current_items = get_current_items(order_id)
	item_sum = sum_current_items(current_items)

	template = render_template('bar.html', 	form = form, products = products, 
											current_items = current_items,
											item_sum = item_sum)
	resp = make_response(template)

	if order_id is None:
		print("CREATING ORDER")
		order_id = db_manager.create_order()
		resp.set_cookie('order_id', str(order_id))
		print(f"order id {order_id}")


	print(current_items)
	# debugging
	if form.validate_on_submit():
		print(f"RECIEVED POST")

	return resp


@app.route("/", methods=["GET"])
def index():
	return redirect(url_for("bar"))





if __name__ == "__main__":
	db_manager.create_tables()
	print("DB created")
	db_manager.add_products()
	print("Added products")

	app.run(debug=True)
