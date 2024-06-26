import pyodbc
import random
import string
from flask import jsonify

class Database:

    def __init__(self):
        self.server = ""
        self.database = ""
        self.username = ""
        self.password = ""
        self.conn = self._create_connection()
        print("Database Connected")

    def _create_connection(self):
        conn_str = f'DRIVER={{SQL Server}};SERVER={self.server};DATABASE={self.database};UID={self.username};PWD={self.password}'
        try:
            conn = pyodbc.connect(conn_str)
            return conn
        except pyodbc.Error as e:
            print(f"Error connecting to the database: {e}")
            return None

    def insert_data(self, category, item_category, item, price, description, link):
        print("Inserting data:")
        print(f"Category: {category}")
        print(f"Item Category: {item_category}")
        print(f"Item: {item}")
        print(f"Price: {price}")
        print(f"Description: {description}")
        print(f"Link: {link}")

        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO " + category + " (itemcategory, item, price, description, link) VALUES (?, ?, ?, ?, ?)",
                           (item_category, item, price, description, link))
            self.conn.commit()
            print("Data inserted successfully.")
        except pyodbc.Error as e:
            print(f"Error inserting data: {e}")

    # -------------------------------------Getting Data---------------------------------------------------------

    # return false if Mail already Exists
    def insert_user(self, email, password):
        if self.email_exists(email):
            return None

        identifier = self._generate_identifier()
        query = f"INSERT INTO users (password, email, identifier) VALUES (?, ?, ?)"
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, (password, email, identifier))
            self.conn.commit()
            print("User inserted successfully.")
            return identifier
        except pyodbc.Error as e:
            print(f"Error inserting user into the database: {e}")
            return None

    def email_exists(self, email):
        query = "SELECT COUNT(*) FROM Users WHERE Email = ?"
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, (email,))
            row = cursor.fetchone()
            if row and row[0] > 0:
                return True
            else:
                return False
        except pyodbc.Error as e:
            print(f"Error checking if email exists in the database: {e}")
            return False

    def _generate_identifier(self):
        # Generate a random integer identifier
        return random.randint(10000000, 99999999)


    def check_login(self, email, password):
        query = "SELECT identifier FROM users WHERE email = ? AND password = ?"
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, (email, password))
            row = cursor.fetchone()
            if row:
                return row.identifier
            else:
                print("User not found.")
                return None
        except pyodbc.Error as e:
            print(f"Error retrieving user from the database: {e}")


    def get_all_data(self, table_name):
        try:
            # SQL query to retrieve data
            cursor = self.conn.cursor()
            cursor.execute(f"""
                SELECT *
                FROM (
                    SELECT *,
                           ROW_NUMBER() OVER (PARTITION BY itemcategory ORDER BY (SELECT NULL)) AS rn
                    FROM {table_name}
                ) AS subquery
                WHERE rn = 1
            """)
            # Fetch all rows
            rows = cursor.fetchall()

            # Get column names
            columns = [column[0] for column in cursor.description]

            # Create a list of dictionaries where each dictionary represents a row
            data = []
            for row in rows:
                data.append(dict(zip(columns, row)))

            # Close cursor and return data as JSON
            cursor.close()
            return jsonify(data)
        except Exception as e:
            return jsonify({"error": str(e)})

    def get_item_category(self, table_name, itemid):
        try:
            # SQL query to retrieve item category for the given itemid
            cursor = self.conn.cursor()
            cursor.execute(f"""
                SELECT itemcategory
                FROM {table_name}
                WHERE id = ?
            """, (itemid,))

            # Fetch the first result
            row = cursor.fetchone()
            if row:
                itemcategory = row[0]
            else:
                return jsonify({"error": "Item not found."}), 404

            # Now, fetch all items with the same category
            cursor.execute(f"""
                SELECT *
                FROM {table_name}
                WHERE itemcategory = ?
            """, (itemcategory,))

            # Fetch all rows
            rows = cursor.fetchall()

            # Get column names
            columns = [column[0] for column in cursor.description]

            # Create a list of dictionaries where each dictionary represents a row
            data = []
            for row in rows:
                data.append(dict(zip(columns, row)))

            # Close cursor and return data as JSON
            cursor.close()
            return jsonify(data)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
