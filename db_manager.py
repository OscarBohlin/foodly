import sqlite3
from datetime import datetime

DATABASE_NAME = "foodly.sqlite"


class Order():

	def __init__(self, order_id: int, time_created: datetime, handled_by: str, status: int) -> None:			
		self.order_id = order_id
		self.time_created = time_created
		self.handled_by = handled_by
		self.status = status

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


def create_tables():
	drop_all_tables() # FOR SIENCE

	connection = get_connection()
	connection.execute("""CREATE TABLE IF NOT EXISTS orders (
						order_id INTEGER PRIMARY KEY AUTOINCREMENT,
						time_created TIMESTAMP DEFAULT (datetime('now', 'localtime')),
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
								DELETE FROM orders WHERE time_created < DATETIME('NOW', 'localtime', '-1 hour');
							END
						""")
	
	connection.execute("""CREATE TRIGGER IF NOT EXISTS auto_refresh_order_timestamp
								AFTER INSERT ON items
							BEGIN
								UPDATE orders SET time_created = DATETIME('NOW', 'localtime') WHERE order_id = NEW.order_id;
							END
						""")
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

	connection.execute("""	UPDATE items SET diet = ? WHERE item_id = ?""", (diet, item_id))

	connection.close()