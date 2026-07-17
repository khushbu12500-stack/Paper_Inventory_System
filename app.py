import re
from flask import flash
from flask import Flask, render_template, request, redirect, send_file, flash
from openpyxl import Workbook
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from database import conn, cursor
print("******** APP.PY LOADED ********")

app = Flask(__name__)
app.secret_key = "paper_inventory_secret_key"
@app.route('/', methods=['GET', 'POST'])
def home():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        cursor.execute(
            "SELECT * FROM users WHERE username=%s AND password=%s",
            (username, password)
        )

        user = cursor.fetchone()

        if user:
            return redirect('/dashboard')
        else:
            return "Invalid Username or Password"

    return render_template('login.html')



@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    cursor.execute("SELECT supplier_name FROM suppliers")
    suppliers = cursor.fetchall()
    print("SUPPLIERS =", suppliers)

    if request.method == 'POST':

        product_name = request.form['product_name']
        category = request.form['category']
        specification=request.form['specification']
        brand=request.form['brand']
        unit=request.form['unit']
        quantity = request.form['quantity']
        price_per_unit = request.form['price_per_unit']
        total_price=request.form['total_price']
        supplier = request.form['supplier']

        sql = """
        INSERT INTO products
        (product_name, category,specification, brand,unit, quantity ,price_per_unit ,total_price, supplier)
        VALUES (%s, %s, %s, %s, %s,  %s, %s,%s,%s)
        """

        values = (product_name, category, specification, brand,unit, quantity, price_per_unit, total_price,supplier)

        cursor.execute(sql, values)
        conn.commit()

        flash("✅ Product added successfully!", "success")

        return redirect('/view_products')

    return render_template('add_product.html',suppliers=suppliers, active_page="add_supplier")
@app.route('/view_products')
def view_products():

    cursor.execute("SELECT * FROM products ORDER BY id")
    products = cursor.fetchall()

    total_products = len(products)

    in_stock = 0
    low_stock = 0
    out_stock = 0

    for product in products:

        quantity = product[3]

        if quantity == 0:
            out_stock += 1

        elif quantity < 10:
            low_stock += 1

        else:
            in_stock += 1

    return render_template(
        'view_products.html',
        products=products,
        total_products=total_products,
        in_stock=in_stock,
        low_stock=low_stock,
        out_stock=out_stock
    )
@app.route('/edit_product/<int:id>', methods=['GET', 'POST'])
def edit_product(id):

    if request.method == 'POST':

        product_name = request.form['product_name']
        category = request.form['category']
        specification = request.form['specification']
        brand = request.form['brand']
        unit = request.form['unit']
        quantity = request.form['quantity']
        price_per_unit = request.form['price_per_unit']
        total_price = request.form['total_price']
        supplier = request.form['supplier']

        sql = """
        UPDATE products
        SET
            product_name=%s,
            category=%s,
            specification=%s,
            brand=%s,
            unit=%s,
            quantity=%s,
            price_per_unit=%s,
            total_price=%s,
            supplier=%s
        WHERE id=%s
        """

        values = (
            product_name,
            category,
            specification,
            brand,
            unit,
            quantity,
            price_per_unit,
            total_price,
            supplier,
            id
        )

        cursor.execute(sql, values)
        conn.commit()

        return redirect('/view_products')

    # GET request
    cursor.execute("SELECT * FROM products WHERE id=%s", (id,))
    product = cursor.fetchone()

    cursor.execute("SELECT * FROM suppliers")
    suppliers = cursor.fetchall()

    return render_template(
        "edit_product.html",
        product=product,
        suppliers=suppliers
    )
@app.route('/delete_product/<int:id>')
def delete_product(id):

    cursor.execute(
        "DELETE FROM products WHERE id=%s",
        (id,)
    )

    conn.commit()

    return redirect('/view_products')
@app.route('/update_stock/<int:id>', methods=['GET', 'POST'])
def update_stock(id):

    print("UPDATE_STOCK FUNCTION CALLED")
    print("I AM INSIDE UPDATE_STOCK")
    cursor.execute(
        "SELECT * FROM products WHERE id=%s",
        (id,)
    )

    product = cursor.fetchone()

    if request.method == 'POST':

        stock_in = int(request.form['stock_in'])

        current_quantity = int(product[3])
        price_per_unit = float(product[4])

        new_quantity = current_quantity + stock_in
        new_total_price = new_quantity * price_per_unit

        # Update Product
        cursor.execute(
            """
            UPDATE products
            SET quantity=%s,
                total_price=%s
            WHERE id=%s
            """,
            (new_quantity, new_total_price, id)
        )

        print("Saving Stock In History...")

        try:
            cursor.execute(
                """
                INSERT INTO stock_history
                (product_name, action, quantity, date_time)
                VALUES (%s, %s, %s, NOW())
                """,
                (
                    product[1],
                    "Stock In",
                    stock_in
                )
            )

            print("Stock In History Saved Successfully")

        except Exception as e:
            print("ERROR:", e)

        conn.commit()

        return redirect('/view_products')

    return render_template(
        'update_stock.html',
        product=product
    )
@app.route('/stock_out/<int:id>', methods=['GET', 'POST'])
def stock_out(id):
   
    cursor.execute(
        "SELECT * FROM products WHERE id=%s",
        (id,)
    )

    product = cursor.fetchone()

    if request.method == 'POST':

        stock_out = int(request.form['stock_out'])

        current_quantity = int(product[3])

        if stock_out > current_quantity:
            return "Error: Not enough stock available!"

        price_per_unit = float(product[4])

        new_quantity = current_quantity - stock_out

        new_total_price = new_quantity * price_per_unit

        cursor.execute(
            """
            UPDATE products
            SET quantity=%s,
                total_price=%s
            WHERE id=%s
            """,
            (new_quantity, new_total_price, id)
        )
        print("Saving Stock Out History...")


        # Save Stock Out History
        cursor.execute(
            """
            INSERT INTO stock_history
            (product_name, action, quantity, date_time)
            VALUES (%s, %s, %s, NOW())
            """,
            (
                product[1],
                "Stock Out",
                stock_out
            )
        )

        conn.commit()

        return redirect('/view_products')

    return render_template(
        'stock_out.html',
        product=product
    )
@app.route('/search_product', methods=['GET', 'POST'])
def search_product():

    products = []

    if request.method == 'POST':

        keyword = request.form['keyword']

        sql = """
        SELECT * FROM products
        WHERE product_name LIKE %s
        OR category LIKE %s
        OR specification LIKE %s
        OR supplier LIKE %s
        """

        search = "%" + keyword + "%"

        cursor.execute(
            sql,
            (search, search, search, search)
        )

        products = cursor.fetchall()

    return render_template(
        'search_product.html',
        products=products
    )

@app.route('/stock_history')
def stock_history():

    cursor.execute("""
        SELECT * FROM stock_history
        ORDER BY date_time ASC
    """)
    histories = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM stock_history")
    total_transactions = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM stock_history WHERE action='Purchase'")
    total_purchase = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM stock_history WHERE action='Sale'")
    total_sale = cursor.fetchone()[0]

    
    return render_template(
        "stock_history.html",
        histories=histories,
        total_transactions=total_transactions,
        total_purchase=total_purchase,
        total_sale=total_sale
    )
@app.route('/dashboard')
def dashboard():

    # Total Products
    cursor.execute("SELECT COUNT(*) FROM products")
    total_products = cursor.fetchone()[0]

    # Total Suppliers
    cursor.execute("SELECT COUNT(*) FROM suppliers")
    total_suppliers = cursor.fetchone()[0]

    # Total Purchases
    cursor.execute("SELECT COUNT(*) FROM purchases")
    total_purchases = cursor.fetchone()[0]

    # Total Sales
    cursor.execute("SELECT COUNT(*) FROM sales")
    total_sales = cursor.fetchone()[0]

    # Low Stock (less than 10)
    cursor.execute("SELECT COUNT(*) FROM products WHERE quantity < 10")
    low_stock = cursor.fetchone()[0]

    # Out of Stock
    cursor.execute("SELECT COUNT(*) FROM products WHERE quantity = 0")
    out_of_stock = cursor.fetchone()[0]

    # Total Inventory Value
    cursor.execute("""
        SELECT SUM(quantity * price_per_unit)
        FROM products
    """)
    inventory_value = cursor.fetchone()[0]

    if inventory_value is None:
        inventory_value = 0
        # Total Stock Quantity
    cursor.execute("SELECT SUM(quantity) FROM products")
    total_stock = cursor.fetchone()[0]

    if total_stock is None:
     total_stock = 0

    return render_template(
        'dashboard.html',
         active_page="dashboard",
        total_products=total_products,
        total_suppliers=total_suppliers,
        total_purchases=total_purchases,
        total_sales=total_sales,
        low_stock=low_stock,
        out_of_stock=out_of_stock,
        inventory_value=inventory_value,
        total_stock=total_stock
    )


    
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        sql = """
        INSERT INTO users
        (username, email, password)
        VALUES (%s, %s, %s)
        """

        values = (username, email, password)

        cursor.execute(sql, values)
        conn.commit()

        return "Registration Successful!"

    return render_template('register.html')
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():

    if request.method == 'POST':

        email = request.form['email']

        cursor.execute(
            "SELECT * FROM users WHERE email=%s",
            (email,)
        )

        user = cursor.fetchone()

        if user:
         return redirect(f"/reset_password/{email}")
        else:
         return "Email Not Found!"

    return render_template('forgot_password.html')

@app.route('/reset_password/<email>', methods=['GET', 'POST'])
def reset_password(email):

    if request.method == 'POST':

        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            return "Passwords do not match!"

        cursor.execute(
            "UPDATE users SET password=%s WHERE email=%s",
            (password, email)
        )

        conn.commit()

        return redirect('/')

    return render_template('reset_password.html')
@app.route('/export_excel')
def export_excel():

    cursor.execute("""
        SELECT product_name,
               category,
               specification,
               brand,
               unit,
               quantity,
               price_per_unit,
               total_price,
               supplier
        FROM products
    """)

    products = cursor.fetchall()

    wb = Workbook()
    ws = wb.active
    ws.title = "Products"

    ws.append([
        "Product Name",
        "Category",
        "Specification",
        "Brand",
        "Unit",
        "Quantity",
        "Price Per Unit",
        "Total Price",
        "Supplier"
    ])

    for product in products:
        ws.append(product)

    filename = "products.xlsx"
    wb.save(filename)

    return send_file(filename, as_attachment=True)
@app.route('/export_stock_history_excel')
def export_stock_history_excel():


    # Get all products from database
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    # Create Excel workbook
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Products"

    # Column headings
    sheet.append([
        "ID",
        "Product Name",
        "Category",
        "Quantity",
        "Price Per Unit",
        "Specification",
        "Unit",
        "Total Price",
        "Supplier",
        "Brand"
    ])

    # Add product data
    for product in products:
        sheet.append(product)

    # Save Excel file
    filename = "products.xlsx"
    workbook.save(filename)

    # Download file
    return send_file(
        filename,
        as_attachment=True
    )
@app.route('/export_pdf')
def export_pdf():

    # Get all products
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    filename = "products.pdf"

    # Create PDF
    pdf = SimpleDocTemplate(filename)

    # Table headings
    data = [[
        "ID",
        "Product Name",
        "Category",
        "Quantity",
        "Price",
        "Specification",
        "Unit",
        "Total Price",
        "Supplier",
        "Brand"
    ]]

    # Add database records
    for product in products:
        data.append(list(product))

    # Create table
    table = Table(data)

    # Table Style
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),

        ('BACKGROUND', (0,1), (-1,-1), colors.beige),

        ('GRID', (0,0), (-1,-1), 1, colors.black),

        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),

        ('ALIGN', (0,0), (-1,-1), 'CENTER'),

        ('BOTTOMPADDING', (0,0), (-1,0), 10),
    ]))

    pdf.build([table])

    return send_file(
        filename,
        as_attachment=True
    )
@app.route('/add_supplier', methods=['GET', 'POST'])
def add_supplier():

    if request.method == 'POST':

        supplier_name = request.form['supplier_name'].strip()
        company_name = request.form['company_name'].strip()
        phone = request.form['phone'].strip()
        email = request.form['email'].strip()
        address = request.form['address'].strip()
        gst_number = request.form['gst_number'].strip()

        # Required Field Validation
        if not supplier_name:
            flash("❌ Supplier Name is required.", "danger")
            return redirect('/add_supplier')

        if not company_name:
            flash("❌ Company Name is required.", "danger")
            return redirect('/add_supplier')

        if not phone:
            flash("❌ Phone Number is required.", "danger")
            return redirect('/add_supplier')

        if not email:
            flash("❌ Email is required.", "danger")
            return redirect('/add_supplier')

        if not address:
            flash("❌ Address is required.", "danger")
            return redirect('/add_supplier')

        if not gst_number:
            flash("❌ GST Number is required.", "danger")
            return redirect('/add_supplier')

        # Phone Validation
        if not re.fullmatch(r"[6-9]\d{9}", phone):
            flash("❌ Please enter a valid 10-digit phone number.", "danger")
            return redirect('/add_supplier')

        # Email Validation
        email_pattern = r'^[A-Za-z0-9._%+-]+@(gmail|yahoo|outlook|hotmail|icloud)\.(com|in|org)$'

        if not re.fullmatch(email_pattern, email):
            flash("❌ Please enter a valid email address.", "danger")
            return redirect('/add_supplier')

        # GST Validation
        gst_pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'

        if not re.fullmatch(gst_pattern, gst_number):
            flash("❌ Please enter a valid GST number.", "danger")
            return redirect('/add_supplier')

        # Duplicate Check
        cursor.execute("""
            SELECT * FROM suppliers
            WHERE supplier_name=%s
               OR phone=%s
               OR email=%s
               OR gst_number=%s
        """, (supplier_name, phone, email, gst_number))

        existing_supplier = cursor.fetchone()

        if existing_supplier:
            flash("❌ Supplier already exists.", "danger")
            return redirect('/add_supplier')
        print(supplier_name)
        print(phone, email, gst_number)

        # Insert Supplier
        cursor.execute("""
            INSERT INTO suppliers
            (supplier_name, company_name, phone, email, address, gst_number)
            VALUES (%s,%s,%s,%s,%s,%s)
        """,
        (
            supplier_name,
            company_name,
            phone,
            email,
            address,
            gst_number
        ))

        conn.commit()

        flash("✅ Supplier added successfully!", "success")
        return redirect('/view_suppliers')

    return render_template('add_supplier.html')
@app.route('/view_suppliers')
def view_suppliers():

    search = request.args.get('search', '').strip()

    if search:
        sql = """
        SELECT * FROM suppliers
        WHERE supplier_name LIKE %s
           OR company_name LIKE %s
        """
        value = ("%" + search + "%", "%" + search + "%")
        cursor.execute(sql, value)
    else:
        cursor.execute("SELECT * FROM suppliers")

    suppliers = cursor.fetchall()

    return render_template(
        'view_suppliers.html',
        suppliers=suppliers,
        search=search
    )
    
@app.route('/edit_supplier/<int:id>', methods=['GET', 'POST'])
def edit_supplier(id):

    cursor.execute(
        "SELECT * FROM suppliers WHERE id=%s",
        (id,)
    )

    supplier = cursor.fetchone()

    if request.method == 'POST':

        supplier_name = request.form['supplier_name']
        company_name = request.form['company_name']
        phone = request.form['phone']
        email = request.form['email']
        address = request.form['address']
        gst_number = request.form['gst_number']

        cursor.execute("""
            UPDATE suppliers
            SET supplier_name=%s,
                company_name=%s,
                phone=%s,
                email=%s,
                address=%s,
                gst_number=%s
            WHERE id=%s
        """,
        (
            supplier_name,
            company_name,
            phone,
            email,
            address,
            gst_number,
            id
        ))

        conn.commit()

        return redirect('/view_suppliers')

    return render_template(
        'edit_supplier.html',
        supplier=supplier
    )
@app.route('/delete_supplier/<int:id>')
def delete_supplier(id):

    cursor.execute(
        "DELETE FROM suppliers WHERE id=%s",
        (id,)
    )

    conn.commit()

    return redirect('/view_suppliers')

@app.route('/add_purchase', methods=['GET', 'POST'])
def add_purchase():

    cursor.execute("SELECT * FROM suppliers")
    suppliers = cursor.fetchall()

    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    if request.method == 'POST':

        supplier_name = request.form['supplier_name']
        product_name = request.form['product_name']
        quantity = int(request.form['quantity'])
        price_per_unit = float(request.form['price_per_unit'])

        total_price = quantity * price_per_unit

        # Save purchase
        cursor.execute("""
            INSERT INTO purchases
            (supplier_name, product_name, quantity, price_per_unit, total_price)
            VALUES (%s, %s, %s, %s, %s)
        """,
        (
            supplier_name,
            product_name,
            quantity,
            price_per_unit,
            total_price
        ))

        # Update product stock
        cursor.execute("""
            UPDATE products
            SET quantity = quantity + %s
            WHERE product_name = %s
        """,
        (
            quantity,
            product_name
        ))
        # Save Stock History
        cursor.execute("""
            INSERT INTO stock_history
            (product_name, action, quantity, date_time)
            VALUES (%s, %s, %s, NOW())
        """,

         (
            product_name,
            "Purchase",
             quantity
))
        

        conn.commit()

        return redirect('/view_purchases')

    return render_template(
        'add_purchase.html',
        suppliers=suppliers,
        products=products
    )
@app.route('/view_purchases')
def view_purchases():

    cursor.execute("""
        SELECT * FROM purchases
        ORDER BY purchase_date ASC
    """)
    purchases = cursor.fetchall()

    # Summary calculations
    total_purchases = len(purchases)

    total_quantity = 0
    total_amount = 0

    for purchase in purchases:
        total_quantity += purchase[3]      # Quantity
        total_amount += purchase[5]        # Total Price

    return render_template(
        'view_purchases.html',
        purchases=purchases,
        total_purchases=total_purchases,
        total_quantity=total_quantity,
        total_amount=total_amount
    )
@app.route('/add_sale', methods=['GET', 'POST'])
def add_sale():

    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    if request.method == 'POST':

        product_name = request.form['product_name']
        customer_name = request.form['customer_name'].strip()
        quantity = int(request.form['quantity'])
        price_per_unit = float(request.form['price_per_unit'])

        # Customer Name Validation
        if not customer_name:
            flash("❌ Customer Name is required.", "danger")
            return redirect('/add_sale')

        if not re.fullmatch(r"[A-Za-z ]+", customer_name):
            flash("❌ Customer Name should contain only letters and spaces.", "danger")
            return redirect('/add_sale')

        # Quantity Validation
        if quantity <= 0:
            flash("❌ Quantity must be greater than 0.", "danger")
            return redirect('/add_sale')

        # Price Validation
        if price_per_unit <= 0:
            flash("❌ Price must be greater than 0.", "danger")
            return redirect('/add_sale')

        total_price = quantity * price_per_unit

        # Check current stock
        cursor.execute(
            "SELECT quantity FROM products WHERE product_name=%s",
            (product_name,)
        )

        stock = cursor.fetchone()

        if stock is None:
            flash("❌ Product not found!", "danger")
            return redirect('/add_sale')

        current_stock = stock[0]

        # Prevent overselling
        if quantity > current_stock:
            flash(f"❌ Not enough stock! Only {current_stock} item(s) available.", "danger")
            return redirect('/add_sale')

        # Save sale
        cursor.execute("""
            INSERT INTO sales
            (product_name, customer_name, quantity, price_per_unit, total_price)
            VALUES (%s,%s,%s,%s,%s)
        """,
        (
            product_name,
            customer_name,
            quantity,
            price_per_unit,
            total_price
        ))

        # Reduce stock
        cursor.execute("""
            UPDATE products
            SET quantity = quantity - %s
            WHERE product_name = %s
        """,
        (
            quantity,
            product_name
        ))

        # Save Stock History
        cursor.execute("""
            INSERT INTO stock_history
            (product_name, action, quantity, date_time)
            VALUES (%s, %s, %s, NOW())
        """,
        (
            product_name,
            "Sale",
            quantity
        ))

        conn.commit()

        flash("✅ Sale added successfully!", "success")
        return redirect('/view_sales')

    return render_template(
        'add_sale.html',
        products=products
    )
@app.route('/view_sales')
def view_sales():

    cursor.execute("""
        SELECT *
        FROM sales
        ORDER BY sale_date ASC
    """)

    sales = cursor.fetchall()

    total_sales = len(sales)

    total_quantity = 0
    total_revenue = 0

    for sale in sales:
        total_quantity += sale[3]
        total_revenue += sale[5]

    return render_template(
        'view_sales.html',
        sales=sales,
        total_sales=total_sales,
        total_quantity=total_quantity,
        total_revenue=total_revenue
    )

@app.route('/export_stock_excel')
def export_stock_excel():

    # Get stock history from database
    cursor.execute("""
        SELECT product_name, action, quantity, date_time
        FROM stock_history
        ORDER BY date_time DESC
    """)

    stock = cursor.fetchall()

    # Create Excel workbook
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Stock History"

    # Column headings
    sheet.append([
        "Product Name",
        "Action",
        "Quantity",
        "Date & Time"
    ])

    # Add stock history data
    for row in stock:
        sheet.append(row)

    # Save Excel file
    filename = "Stock_History.xlsx"
    workbook.save(filename)

    # Download file
    return send_file(
        filename,
        as_attachment=True
    )


   
      

   

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)



