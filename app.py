from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap

import os
import db_manager
import forms

app = Flask(__name__)
app.config["SECRET_KEY"] = str(os.urandom(20).hex())
Bootstrap(app)



@app.route("/bar", methods=["GET", "POST"])
def bar():

	form = forms.BarOrderForm()

	products = db_manager.get_all_products()
	print(products)

	if form.validate_on_submit():
		print(f"RECIEVED POST")

	return render_template("bar.html", form = form)



@app.route("/", methods=["GET"])
def index():
	return redirect(url_for("bar"))





if __name__ == "__main__":
	db_manager.create_tables()
	print("DB created")
	db_manager.add_products()
	print("Added products")

	app.run(debug=True)
