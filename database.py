import sqlite3

# Connect to the SQLite database (it will be created if it doesn't exist)
conn = sqlite3.connect('instance/bills.db')

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# SQL command to create the 'bills' table
# This table stores the main information for each bill
cursor.execute('''
CREATE TABLE IF NOT EXISTS bills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT NOT NULL,
    customer_address TEXT,
    bill_date DATE NOT NULL,
    subtotal REAL NOT NULL,
    tax_rate REAL NOT NULL,
    tax_amount REAL NOT NULL,
    grand_total REAL NOT NULL
)
''')

# SQL command to create the 'bill_items' table
# This table stores the line items for each bill, linked by bill_id
cursor.execute('''
CREATE TABLE IF NOT EXISTS bill_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bill_id INTEGER NOT NULL,
    description TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    total_price REAL NOT NULL,
    FOREIGN KEY (bill_id) REFERENCES bills (id)
)
''')

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database and tables created successfully in instance/bills.db")