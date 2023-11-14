from flask import Flask, render_template, request, redirect, url_for
import pymysql
import requests

app = Flask(__name__)

# Connect to the database
db = pymysql.connect(host="localhost", user="root", password="42519h", database="book_store")


@app.route('/')
def index():
    # Get all products from the database
    cursor = db.cursor()
    cursor.execute("SELECT id,title,author,price FROM products")
    # Fetch the product data using cursor.fetchall()
    products = cursor.fetchall()
    return render_template("prod_admin.html", products=products)

@app.route('/products')
def main_products():
    key1 = 'bkg'                       # in case running in standalone mode
    # Get the data from the request
    data = request.args                 # comment this code when running in standalone mode
    key1 = data.get('c_name')           # comment this code when running in standalone mode

    print(f'Login Microservice has passed Username {key1} to Product Microservice after successful Login')
    
    # Get all products from the database
    cursor = db.cursor()
    cursor.execute("SELECT id,title,author,price FROM products")
    
    # Fetch the product data using cursor.fetchall()
    products = cursor.fetchall()
    
    return render_template('prod_main.html', products=products, key1=key1)

@app.route('/order/<user_name>/<title>/<author>/<price>')
def order(user_name,title,author,price):
    print(f'order_product Method: User: {user_name} Product Title: {title} Author: {author}')
    # Get all products from the database
    data_order = {'user_name': user_name, 'title': title, 'author': author, 'price':price}
    print(f'Order being processed with details Customer {user_name}, Book Title:{title} Book Author:{author} Price of Book: Rs{price}')
    # Send the JSON message to the Checkout microservice to add username, mobile no. and address to order_checkout table
    response = requests.get('http://localhost:5002/', params=data_order)
    print('Order successfully sent to process_order')
    #return 'Order successfully sent to process_order'
    return response.text    

# Route to add/edit products Delete Module if not working
@app.route('/manage_product/<int:product_id>', methods=['GET', 'POST'])
def manage_product(product_id):
    cursor = db.cursor()

    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        price = request.form['price']
        
        if product_id == 0:
            cursor.execute("INSERT INTO products (title, author, price) VALUES (%s, %s, %s)", (title, author, price))
        else:
            cursor.execute("UPDATE products SET title=%s, author=%s, price=%s WHERE id=%s", (title, author, price, product_id))
        
        pymysql.connection.commit()
        cursor.close()
        return redirect('/')
    
    if product_id == 0:
        return render_template('manage_product.html', product=None)
    else:
        cursor.execute('SELECT * FROM products WHERE id = %s', (product_id,))
        product = cursor.fetchone()
        cursor.close()
        return render_template('manage_product.html', product=product)


@app.route('/edit_product/<id>')
def edit_product(id):
    # Get the product with the specified ID
    cursor = db.cursor()
    cursor.execute("SELECT * FROM products WHERE id=%s", (id,))
    product = cursor.fetchone()

    return render_template("edit_product.html", product=product)

@app.route('/update_product', methods=["POST"])
def update_product():
    # Update the product with the specified ID
    id = request.form["id"]
    title = request.form["title"]
    author = request.form["author"]
    price = request.form["price"]

    cursor = db.cursor()
    cursor.execute("UPDATE products SET title=%s, author=%s, price=%s WHERE id=%s", (title, author, price, id))
    db.commit()

    return redirect("/")

@app.route('/delete_product/<id>')
def delete_product(id):
    # Delete the product with the specified ID
    cursor = db.cursor()
    cursor.execute("DELETE FROM products WHERE id=%s", (id,))
    db.commit()

    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)

