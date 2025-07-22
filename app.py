from flask import Flask, render_template, request, redirect, url_for, g
import sqlite3
from datetime import datetime

app = Flask(__name__)
DATABASE = 'instance/bills.db'

# --- Database Helper Functions (Unchanged) ---
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# --- Routes ---

@app.route('/')
def index():
    """Renders the simple bill creation form."""
    return render_template('index.html')

@app.route('/generate_bill', methods=['POST'])
def generate_bill():
    """Processes the static form, calculates totals, saves to DB."""
    # --- 1. Get Data from Form ---
    customer_name = request.form['customer_name']
    customer_address = request.form['customer_address']
    bill_date = datetime.now().strftime("%Y-%m-%d")
    tax_rate = float(request.form.get('tax_rate', 0))

    descriptions = request.form.getlist('item_description[]')
    quantities = request.form.getlist('item_quantity[]')
    unit_prices = request.form.getlist('item_price[]')
    
    # --- 2. Calculate Totals (and filter out empty rows) ---
    subtotal = 0
    items_data = []
    for i in range(len(descriptions)):
        # Only process rows where all fields are filled
        if descriptions[i] and quantities[i] and unit_prices[i]:
            try:
                quantity = int(quantities[i])
                unit_price = float(unit_prices[i])
                total_price = quantity * unit_price
                subtotal += total_price
                items_data.append({
                    "description": descriptions[i],
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "total_price": total_price
                })
            except (ValueError, TypeError):
                # Handle case where data is not a valid number, just skip it
                continue
    
    tax_amount = subtotal * (tax_rate / 100)
    grand_total = subtotal + tax_amount

    # --- 3. Save to Database ---
    db = get_db()
    cursor = db.cursor()

    cursor.execute('''
        INSERT INTO bills (customer_name, customer_address, bill_date, subtotal, tax_rate, tax_amount, grand_total)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (customer_name, customer_address, bill_date, subtotal, tax_rate, tax_amount, grand_total))
    
    bill_id = cursor.lastrowid

    for item in items_data:
        cursor.execute('''
            INSERT INTO bill_items (bill_id, description, quantity, unit_price, total_price)
            VALUES (?, ?, ?, ?, ?)
        ''', (bill_id, item['description'], item['quantity'], item['unit_price'], item['total_price']))
    
    db.commit()

    # --- 4. Redirect to View the Bill ---
    return redirect(url_for('view_bill', bill_id=bill_id))


@app.route('/bill/<int:bill_id>')
def view_bill(bill_id):
    db = get_db()
    bill = db.execute('SELECT * FROM bills WHERE id = ?', (bill_id,)).fetchone()
    items = db.execute('SELECT * FROM bill_items WHERE bill_id = ?', (bill_id,)).fetchall()
    
    if bill is None:
        return "Bill not found!", 404

    return render_template('bill_view.html', bill=bill, items=items)

@app.route('/bills')
def list_bills():
    db = get_db()
    all_bills = db.execute('SELECT id, customer_name, bill_date, grand_total FROM bills ORDER BY bill_date DESC').fetchall()
    return render_template('bills_list.html', bills=all_bills)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
