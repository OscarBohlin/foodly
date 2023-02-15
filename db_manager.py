import sqlite3

DATABASE_NAME = "foodly.sqlite"


def create_tables():
	drop_all_tables() # FOR SIENCE

	connection = get_connection()
	connection.execute("""CREATE TABLE IF NOT EXISTS orders (
						order_id INTEGER PRIMARY KEY AUTOINCREMENT,
						time_created TIMESTAMP DEFAULT NULL,
						handled_by TEXT DEFAULT NULL, 
						status INTEGER DEFAULT 0)  """)

	connection.execute("""CREATE TABLE IF NOT EXISTS products(
						product_id INTEGER PRIMARY KEY,
						name TEXT UNIQUE NOT NULL,
						cost REAL NOT NULL,
						category TEXT)  """)

	connection.execute("""CREATE TABLE IF NOT EXISTS items(
						item_id INTEGER PRIMARY KEY,
						product_id INTEGER NOT NULL,
						order_id INTEGER NOT NULL,
						diet TEXT,
						FOREIGN KEY(product_id) REFERENCES products(product_id),
						FOREIGN KEY(order_id) REFERENCES orders(order_id))  """)
	connection.close()



def get_connection():
	return sqlite3.connect(DATABASE_NAME)


def get_all_products():
	connection = get_connection()
	products = connection.execute("SELECT * FROM products").fetchall()
	connection.close()
	return products

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

	cursor.execute("INSERT INTO orders(time_created, handled_by, status) VALUES (NULL, NULL, 0)")
	order_id = cursor.lastrowid
	
	cursor.close()
	connection.commit()
	connection.close()

	return order_id

def get_items_from_order(order_id: int) -> list[tuple]:
	connection = get_connection()
	items = connection.execute(	
		"""SELECT i.item_id, p.product_id, p.name, p.cost, p.category 
			FROM items AS i 
			INNER JOIN products AS p ON i.product_id = p.product_id
			WHERE i.order_id = ?""", (order_id,)).fetchall()
	connection.close()
	return items

def create_item(product_id: int, order_id: int):
	connection = get_connection()
	connection.execute("INSERT INTO items(product_id, order_id) VALUES(?,?)", (product_id, order_id))
	connection.commit()
	connection.close()
	