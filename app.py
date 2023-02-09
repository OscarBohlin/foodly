import db_manager


if __name__ == "__main__":
    db_manager.create_tables()
    print("DB created")
    db_manager.add_products()
    print("Added products")
