import sqlite3
from datetime import datetime

DATABASE_NAME = "foodly.sqlite"

ORDER_STATUS_PENDING = 0
ORDER_STATUS_PLACED = 1
ORDER_STATUS_COOKING = 2
ORDER_STATUS_DONE = 3

class Product():
	
	def __init__(self, product_id: int, name: str, cost: float, category: str) -> None:
		self.product_id = product_id
		self.name = name
		self.cost = cost
		self.category = category

class Item():

	def __init__(self, item_id: int, product: Product, order_id: int, diet: str) -> None:
		self.item_id = item_id
		self.product = product
		self.order_id = order_id
		self.diet = diet

class ItemToDisplay():
	def __init__(self, name: str, cost: float, category: str, diet: str):
		self.name = name
		self.cost = cost
		self.category = category
		self.diet = diet

class Order():

	def __init__(self, order_id: int, last_modified: datetime, handled_by: str, 
				status: int, items: list[ItemToDisplay], placed_date: datetime) -> None:	

		self.order_id = order_id
		self.last_modified = last_modified
		self.placed_date = placed_date
		self.handled_by = handled_by
		self.status = status
		self.items = items



def create_tables():
	# drop_all_tables() # FOR SIENCE

	connection = get_connection()
	connection.execute("""CREATE TABLE IF NOT EXISTS orders (
						order_id INTEGER PRIMARY KEY AUTOINCREMENT,
						placed_date TIMESTAMP,
						last_modified TIMESTAMP DEFAULT (datetime('now', 'localtime')),
						handled_by TEXT DEFAULT NULL, 
						status INTEGER DEFAULT 0)  """)

	connection.execute("""CREATE TABLE IF NOT EXISTS products (
						product_id INTEGER PRIMARY KEY,
						name TEXT UNIQUE NOT NULL,
						cost REAL NOT NULL,
						category TEXT)  """)

	connection.execute("""CREATE TABLE IF NOT EXISTS items (
						item_id INTEGER PRIMARY KEY,
						product_id INTEGER NOT NULL,
						order_id INTEGER NOT NULL,
						diet TEXT,
						FOREIGN KEY(product_id) REFERENCES products(product_id),
						FOREIGN KEY(order_id) REFERENCES orders(order_id))  """)

	connection.execute("""CREATE TRIGGER IF NOT EXISTS auto_delete_items
							BEFORE DELETE ON orders
						BEGIN
							DELETE FROM items WHERE order_id = OLD.order_id;  
						END""")
	
	connection.execute("""CREATE TRIGGER IF NOT EXISTS auto_delete_orders
								BEFORE INSERT ON orders
							BEGIN 
								DELETE FROM orders WHERE last_modified < DATETIME('NOW', 'localtime', '-1 hour')
								AND status = 0;
							END""")
	
	connection.execute("""CREATE TRIGGER IF NOT EXISTS auto_refresh_order_timestamp
								AFTER INSERT ON items
							BEGIN
								UPDATE orders SET last_modified = DATETIME('NOW', 'localtime') WHERE order_id = NEW.order_id;
							END""")
	connection.close()

def remove_order(order_id: int):
	connection = get_connection()

	connection.execute("DELETE FROM orders WHERE order_id = ?", (order_id,))
	connection.commit()
	connection.close()

def get_connection():
	return sqlite3.connect(DATABASE_NAME)


def get_all_products() -> list[Product]:
	connection = get_connection()
	products = connection.execute("SELECT * FROM products ORDER BY category DESC").fetchall()

	list_of_products = []
	for product in products:
		product_obj = Product(product[0], product[1], product[2], product[3])
		list_of_products.append(product_obj)
	
	connection.close()
	return list_of_products


def add_products():
	connection = get_connection()
	products = [
		("Kebabtallrik", 65,"Pubmeny"),
		("Hamburgaretallrik", 65,"Pubmeny"),
		("Pommestallrik", 50,"Pubmeny"),
		("Schnitzel", 70,"23 meny"),
		("Glass", 30,"23 meny"),
		("Kladdkaka", 35,"23 meny"),
		("Nacho tallrik", 55,"Pubmeny")
	]
	connection.executemany("INSERT OR IGNORE INTO products(name, cost, category) VALUES (?,?,?)", products)
	connection.commit()
	connection.close()


def drop_all_tables():
	connection = get_connection()

	connection.execute("DROP TABLE IF EXISTS orders")
	connection.execute("DROP TABLE IF EXISTS products")
	connection.execute("DROP TABLE IF EXISTS items")
	connection.commit()
	connection.close()


def create_order() -> int:
	connection = get_connection()
	cursor = connection.cursor()

	cursor.execute("INSERT INTO orders(handled_by, status) VALUES (NULL, 0)")
	order_id = cursor.lastrowid
	
	cursor.close()
	connection.commit()
	connection.close()

	return order_id


def get_items_from_order(order_id: int) -> list[Item]:
	connection = get_connection()
	items = connection.execute(	
		"""SELECT * 
			FROM items AS i 
			INNER JOIN products AS p ON i.product_id = p.product_id
			WHERE i.order_id = ?""", (order_id,)).fetchall()
	
	list_of_items = []
	for item in items:
		print(item)
		product_obj = Product(int(item[1]), item[5], float(item[6]), item[7])
		item_obj = Item(int(item[0]), product_obj, int(item[2]), item[3])
		list_of_items.append(item_obj)


	connection.close()
	return list_of_items


def create_item(product_id: int, order_id: int):
	connection = get_connection()
	connection.execute("INSERT INTO items(product_id, order_id) VALUES(?,?)", (product_id, order_id))
	connection.commit()
	connection.close()
	

def order_exists(order_id: int) -> bool:
	if order_id is None:
		return False
	
	connection = get_connection()
	
	order = connection.execute("""	SELECT order_id FROM orders 
							WHERE EXISTS (SELECT order_id FROM orders WHERE order_id = ?)
						""", (order_id,)).fetchone()
	connection.close()

	if order is None:
		return False
	
	return True

def get_item(item_id: int, order_id: int) -> Item:
	connection = get_connection()
	

	item = connection.execute("""SELECT * FROM items AS i
									INNER JOIN products AS p ON p.product_id = i.product_id
								WHERE item_id = ? AND order_id = ?
							""", (item_id, order_id)).fetchone()
	
	if item is None:
		return None

	product_obj = Product(int(item[1]), item[5], float(item[6]), item[7])
	item_obj = Item(int(item[0]), product_obj, int(item[2]), item[3])

	connection.close()
	return item_obj


def set_diet(item_id: int, diet: str):
	connection = get_connection()

	connection.execute("UPDATE items SET diet = ? WHERE item_id = ?", (diet, item_id))
	connection.commit()
	connection.close()

def place_order(order_id: int, handled_by: str):
	global ORDER_STATUS_PLACED
	connection = get_connection()

	connection.execute("""UPDATE orders SET status = ?, 
						handled_by = ?,
						last_modified = DATETIME('NOW', 'localtime'),
						placed_date = DATETIME('NOW', 'localtime')
						WHERE order_id = ?""", 
					(ORDER_STATUS_PLACED, handled_by, order_id))

	connection.commit()
	connection.close()

def parse_ItemToDisplay(item: tuple) -> Item:
	
	name = item[3]
	cost = item[4]
	category = item[5]
	diet = item[6]

	return ItemToDisplay(name, cost, category, diet)
	

def get_order(order_id: int) -> Order:
	global ORDER_STATUS_PLACED

	connection = get_connection()
	# "order_id, last_modified, product_name, product_cost, product_category, item_diet, handled_by"

	query = connection.execute("""SELECT o.order_id, o.last_modified, o.handled_by, 
										p.name, p.cost, p.category, i.diet, 
										o.status, o.placed_date 
						FROM orders AS o
						INNER JOIN items AS i ON i.order_id = o.order_id
						INNER JOIN products AS p ON p.product_id = i.product_id
						WHERE o.order_id = ? AND o.status = ?""", (order_id, ORDER_STATUS_PLACED)).fetchall()

	connection.commit()
	connection.close()

	if len(query) is 0:
		return None

	items = [parse_ItemToDisplay(item) for item in query]
	last_modified = query[0][1]
	handled_by 	= query[0][2]
	status 		= query[0][7]
	placed_date = query[0][8]

	return Order(order_id, last_modified, handled_by, status, items, placed_date)


def get_active_orders():
	connection = get_connection()

	active_statuses = (ORDER_STATUS_COOKING, ORDER_STATUS_PLACED)
	done_orders_tuple = connection.execute("""SELECT order_id FROM orders WHERE status = ?
										ORDER BY order_id ASC""", (ORDER_STATUS_DONE,)).fetchall()
	
	orders_prepared_tuple = connection.execute("""SELECT order_id FROM orders WHERE status IN (?, ?)
										ORDER BY order_id ASC""", active_statuses).fetchall()

	connection.commit()
	connection.close()

	done_orders = [order_id[0] for order_id in done_orders_tuple]
	orders_prepared = [order_id[0] for order_id in orders_prepared_tuple]
	return done_orders, orders_prepared


def item_in_order(order_id: int, item_id: int) -> bool:

	connection = get_connection()

	item = connection.execute("SELECT * FROM items WHERE item_id = ? AND order_id = ?",
						(item_id, order_id)).fetchone()

	connection.close()
	
	if item is None:
		return False
	
	return True

def remove_item(item_id):
	connection = get_connection()
	connection.execute("DELETE FROM items WHERE item_id = ?", (item_id,))
	connection.commit()
	connection.close()
	return

def get_placed_orders():
	connection = get_connection()

	placed_orders_tuple = connection.execute("""SELECT order_id FROM orders WHERE status = ?
										ORDER BY order_id ASC""", (ORDER_STATUS_PLACED,)).fetchall()

	connection.commit()
	connection.close()

	placed_orders = [order_id[0] for order_id in placed_orders_tuple]
	return placed_orders


def get_cooking_orders():
	connection = get_connection()

	cooking_orders_tuple = connection.execute("""SELECT order_id FROM orders WHERE status = ?
										ORDER BY order_id ASC""", (ORDER_STATUS_COOKING,)).fetchall()

	connection.commit()
	connection.close()

	cooking_orders = [order_id[0] for order_id in cooking_orders_tuple]
	return cooking_orders

def get_done_orders():
	connection = get_connection()

	done_orders_tuple = connection.execute("""SELECT order_id FROM orders WHERE status = ?
										ORDER BY order_id ASC""", (ORDER_STATUS_DONE,)).fetchall()

	connection.commit()
	connection.close()

	done_orders = [order_id[0] for order_id in done_orders_tuple]
	return done_orders

def update_status(order_id: int, status: int):
	connection = get_connection()

	connection.execute("""UPDATE orders SET status = ?
						WHERE order_id = ?""", (status, order_id))

	connection.commit()
	connection.close()

def get_any_order(order_id: int) -> Order:

	connection = get_connection()
	# "order_id, last_modified, product_name, product_cost, product_category, item_diet, handled_by"

	query = connection.execute("""SELECT o.order_id, o.last_modified, o.handled_by, 
										p.name, p.cost, p.category, i.diet, 
										o.status, o.placed_date 
						FROM orders AS o
						INNER JOIN items AS i ON i.order_id = o.order_id
						INNER JOIN products AS p ON p.product_id = i.product_id
						WHERE o.order_id = ?""", (order_id,)).fetchall()

	connection.commit()
	connection.close()

	if len(query) is 0:
		return None

	items = [parse_ItemToDisplay(item) for item in query]
	last_modified = query[0][1]
	handled_by 	= query[0][2]
	status 		= query[0][7]
	placed_date = query[0][8]

	return Order(order_id, last_modified, handled_by, status, items, placed_date)