import sqlite3

DATABASE_NAME = "foodly.sqlite"
connection = sqlite3.connect(DATABASE_NAME)


def create_tables():
    drop_all_tables() # FOR SIENCE

    cursor = get_cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS orders(
                        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        placed TEXT,
                        handled_by TEXT NOT NULL, 
                        status INTEGER NOT NULL)  """)

    cursor.execute("""CREATE TABLE IF NOT EXISTS products(
                        product_id INTEGER PRIMARY KEY,
                        name TEXT UNIQUE NOT NULL,
                        cost REAL NOT NULL,
                        category TEXT)  """)

    cursor.execute("""CREATE TABLE IF NOT EXISTS items(
                        item_id INTEGER PRIMARY KEY,
                        product_id INTEGER NOT NULL,
                        order_id INTEGER NOT NULL,
                        diet TEXT,
                        FOREIGN KEY(product_id) REFERENCES products(product_id),
                        FOREIGN KEY(order_id) REFERENCES orders(order_id))  """)
    cursor.close()


def get_cursor():
    global connection
    return connection.cursor()


def add_products():
    global connection
    products = [
        ("Kebabtallrik", 65,"Pubmeny"),
        ("Hamburgaretallrik", 65,"Pubmeny"),
        ("Pommestallrik", 50,"Pubmeny"),
        ("Schnitzel", 70,"23 meny"),
        ("Glass", 30,"23 meny"),
        ("Kladdkaka", 35,"23 meny"),
        ("Nacho tallrik", 55,"Pubmeny")
    ]
    cursor = get_cursor()
    cursor.executemany("INSERT OR IGNORE INTO products(name, cost, category) VALUES (?,?,?)", products)
    connection.commit()
    cursor.close()


def drop_all_tables():
    global connection
    cursor = get_cursor()
    cursor.execute("DROP TABLE IF EXISTS orders")
    cursor.execute("DROP TABLE IF EXISTS products")
    cursor.execute("DROP TABLE IF EXISTS items")
    connection.commit()
    cursor.close()