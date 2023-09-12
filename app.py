from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
from DBConnections import add_text

app = Flask(__name__)

# Change this to your secret key (it can be anything, it's for extra protection)
app.secret_key = 'your secret key'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '5a*YMFEP'
app.config['MYSQL_DB'] = 'bg_boarding_house'

# Intialize MySQL
mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/pythonlogin/', methods=['GET', 'POST'])
def login():
    # Output a message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM admin WHERE Admin_UserName = %s AND Admin_Password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['AdminId'] = account['AdminId']
            session['Admin_UserName'] = account['Admin_UserName']
            # Redirect to home page
            return test()
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('login.html', msg=msg)
    

@app.route('/test')
def test():
    return render_template('Test.html')

@app.route('/add_boarder', methods=["GET", "POST"])
def add_boarder():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        firstName = request.form['firstName']
        middleName = request.form['middleName']
        lastName = request.form['lastName']
        address = request.form['address']
        email = request.form['email']
        mobile = request.form['mobile']
        school = request.form['school']
        course = request.form['course']
        schoolYear = request.form['schoolYear']
        emergencyName = request.form['emergencyName']
        emergencyNumber = request.form['emergencyNumber']
        emergencyRelationship = request.form['emergencyRelationship']
        add_new = add_text(username, password, firstName, middleName, lastName, address, email, mobile, school, course, schoolYear, emergencyName, emergencyNumber, emergencyRelationship)
        return redirect(url_for('test'))
    return render_template('Addboarder.html')

@app.route('/view_boarder')
def view_boarder():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        cursor.execute('SELECT Customer_UserName, Customer_FirstName, Customer_MiddleName, Customer_LastName FROM customer')
        customers = cursor.fetchall()
        
        cursor.close()
        
        return render_template('ViewBoarder.html', customers=customers)
    return redirect(url_for('index'))

@app.route('/account_student', methods=['GET'])
def account_student():
    username = request.args.get('username')

    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute('SELECT * FROM customer WHERE Customer_UserName = %s', (username,))
        customer = cursor.fetchone()

        if customer:
            cursor.execute('''
                SELECT c.*, p.AmountPaid, p.DatePaid, p.Status, p.Remarks
                FROM customer AS c
                LEFT JOIN contract AS p ON c.CustomerID = p.CustomerID
                WHERE c.Customer_UserName = %s
            ''', (username,))
            payment = cursor.fetchone()

            cursor.close()

            if payment:
                customer.update(payment)

            return render_template('Account_Student.html', customer=customer)

    return redirect(url_for('index'))


@app.route('/add_payment', methods=['GET', 'POST'])
def add_payment():
    if 'loggedin' in session:
        username = request.args.get('username')
        
        if request.method == 'POST':
            customer_name = request.form['CustomerName']
            building_id = request.form['BuildingID']
            room_id = request.form['RoomID']
            date = request.form['Date']
            date_paid = request.form['DatePaid']
            amount_paid = request.form['AmountPaid']
            status = request.form['Status']
            remarks = request.form['Remarks']

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            cursor.execute('SELECT CustomerID FROM customer WHERE Customer_UserName = %s', (username,))
            customer = cursor.fetchone()

            if customer:
                customer_id = customer['CustomerID']

                cursor.execute(
                    'INSERT INTO contract (CustomerID, Customer_Name, BuildingID, RoomID, Date, DatePaid, AmountPaid, Status, Remarks) '
                    'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)',
                    (customer_id, customer_name, building_id, room_id, date, date_paid, amount_paid, status, remarks)
                )
                mysql.connection.commit()
                cursor.close()

                return redirect(url_for('payment_success'))

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM customer WHERE Customer_UserName = %s', (username,))
        customer = cursor.fetchone()
        cursor.close()

        if customer:
            return render_template('AddPayment.html', username=username, customer=customer)
    
    return redirect(url_for('index'))
    
if __name__ == '__main__':
    app.run(debug=True)