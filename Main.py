from flask import Flask, session, redirect, url_for, escape, request, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
from sqlalchemy import or_


# from sqlalchemy.orm import sessionmaker

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cater.db'
db = SQLAlchemy(app)

# Session = sessionmaker(autoflush=False)

###########################################################################################
#                           Model For Application                                         #
###########################################################################################


class Staff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(30), nullable=False)
    name = db.Column(db.String(30), nullable=False)

    def __init__(self, name, username, password):
        self.name = name
        self.username = username
        self.password = password

    def __repr__(self):
        return '<Staff %r>' % self.username


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(30), nullable=False)
    name = db.Column(db.String(30), nullable=False)

    def __init__(self, name, username, password):
        self.name = name
        self.username = username
        self.password = password


    def __repr__(self):
        return '<Customer %r>' % self.username


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    staff_id_1 = db.Column(db.Integer, db.ForeignKey('staff.id'))
    staff_id_2 = db.Column(db.Integer, db.ForeignKey('staff.id'))
    staff_id_3 = db.Column(db.Integer, db.ForeignKey('staff.id'))
    event_name = db.Column(db.String(30), nullable=False)
    event_location = db.Column(db.String(25), nullable=False)
    event_date = db.Column(db.DateTime, nullable=False)

    def __init__(self, event_name, event_location, event_date):
        self.event_name = event_name
        self.event_location = event_location
        self.event_date = event_date

    def __repr__(self):
        return '<Event = %r at %r>' % (self.username, self.place)


@app.cli.command('initdb')
def initdb_command():
    db.drop_all()
    db.create_all()

    print('Initialized database.')


###########################################################################################
#                                    Logic                                                #
###########################################################################################


def build_user_object(user_type):
    if user_type is 'Owner':
        print("")
        # layouts
        # card for new staff creation above list of staff
        # one card for pending work events and one for assigned events
        #
        # Insert into Staff table
        # newStaff = Staff('name', 'username', 'password')
        # db.session.add(newStaff)
        # db.session.commit()
        #
        # All Staff
        # Staff.query.order_by(Staff.name).all()
        #
        # All Scheduled Events or message if none
        #       Event.query.order_by(Staff.event_date).all()
        #       Staff.query.filter_by(id=events[i].staff_id_1).first()
        #       Staff.query.filter_by(id=events[i].staff_id_2).first()
        #       Staff.query.filter_by(id=events[i].staff_id_3).first()
        #
        # Specifically distinguish events without staff
        # Event.query.filter(and_(Event.staff_id_1 == None, Event.staff_id_2 == None, Event.staff_id_3 == None)).first()
    elif user_type is "Staff":
        print("")
        #
        #
        #
        #
        # All Events signed up for
        # Event.query.filter(or_(Event.staff_id_1 == sid, Event.staff_id_2 == sid, Event.staff_id_3 == sid)).all()
        # All Events with at least 1 empty staff
        # Event.query.filter(or_(Event.staff_id_1 == None, Event.staff_id_2 == None, Event.staff_id_3 == None)).all()
        #
        #
        #
        #
        #
        #
        #
        #
        #

    else:
        print("")


def get_user(n, p):
    userinfo = {}

    # Owner
    if n == 'owner' and p == 'pass':
        print("Building Owner Object")
    else:
        # Customer
        customer_query = Customer.query.filter(and_(Customer.username == n, Customer.password == p)).first()
        if customer_query is not None:
            print("")
        else:
            # Staff
            staff_query = Staff.query.filter(and_(Staff.username == n, Staff.password == p)).first()
            if staff_query is not None:
                print("")

    return True

###########################################################################################
#                                    Routes                                               #
###########################################################################################


@app.route('/', methods=["GET", "POST"])
def login():
    if request.method == 'POST' and "id" in session:
        return redirect(url_for("dashboard", username=session["username"]))
    elif request.method == 'POST':
        user = get_user(request.form['username'], request.form['password'])
        print(user)
        return render_template("login.html")
    else:
        return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    owner = {
        'user_type': 'owner',
        'Name': 'Zara',
        'Age': 7,
        'Class': 'First'
    }
    return render_template('dashboard.html', info=owner)


if __name__ == '__main__':
    app.run()