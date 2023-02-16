from flask import Flask, render_template, redirect, url_for, make_response, request
from flask_bootstrap import Bootstrap
from db_manager import Item, Product, Order

import os
import db_manager
import forms

app = Flask(__name__)
app.config["SECRET_KEY"] = str(os.urandom(20).hex())
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


@app.route("/item/<int:item_id>")
def item(item_id: int):
	
	order_id = request.cookies.get('order_id')
	item = db_manager.get_item(item_id, order_id)

	if item is None:
		error_code = 404
		error_message = f"Item (id={item.item_id}) not found"
		template = render_template("errors/404.html", error_code=error_code, error_message=error_message)
		return template

	# render item template
	form = forms.ItemDietForm()

	if form.validate_on_submit():
		diet = form.diet.data
		db_manager.set_diet(item.item_id, diet)
	
	template = render_template("item.html", item=item)
		


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

	if order_id is None or not db_manager.order_exists(order_id):
		order_id = db_manager.create_order()
		resp.set_cookie('order_id', str(order_id))

	
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
