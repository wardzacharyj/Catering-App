from flask import Flask, session, redirect, url_for, escape, request, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
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
    username = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(30), nullable=False)
    name = db.Column(db.String(30), nullable=False)

    def __init__(self, name, username, password):
        self.name = name
        self.username = username
        self.password = password

    def __repr__(self):
        return '<Staff %r>' % self.username

    def as_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "password": self.password,
            "name": self.name

        }


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
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


def build_user_object(o_id, name, user_type):

    user_info = {'user_type': user_type, 'name': 'Owner'}
    print("BUILDING USER OBJECTS %r %r %r" % (o_id, name, user_type))
    if user_type == 'Owner':
        print("IN OWNER")

        # Save Owner Name
        user_info['name'] = 'Owner'

        # All Staff
        user_info['staff_list'] = [staff.as_dict() for staff in Staff.query.order_by(Staff.name).all()]

        # All Events with at least one staff assigned
        user_info['events_with_staff'] = Event.query.filter(
            or_(
                Event.staff_id_1 is not None, Event.staff_id_2 is not None, Event.staff_id_3 is not None)).all()

        # All Events with no staff assigned
        user_info['events_no_staff'] = Event.query.filter(
            and_(
                Event.staff_id_1 is None, Event.staff_id_2 is None, Event.staff_id_3 is None)).all()

    elif user_type == "Staff":
        # Save Staff Name
        user_info['id'] = o_id

        user_info['name'] = name

        # All Events signed up for
        user_info['my_events'] = Event.query.filter(
            or_(
                Event.staff_id_1 == o_id, Event.staff_id_2 == o_id, Event.staff_id_3 == o_id)).all()

        # All Events with at least 1 empty staff
        user_info['open_events'] = Event.query.filter(
            or_(Event.staff_id_1 is None, Event.staff_id_2 is None, Event.staff_id_3 is None)).all()
    else:
        # Save Name
        user_info['id'] = o_id
        user_info['name'] = name

        # All Events scheduled
        user_info['my_reservations'] = Event.query.filter_by(customer_id=o_id).all()

    return user_info


def get_user(n, p):
    # Owner
    if n == 'owner' and p == 'pass':
        print("Building Owner Object")
        return build_user_object(None, 'Owner', 'Owner')
    else:
        # Customer
        customer = Customer.query.filter(and_(Customer.username == n, Customer.password == p)).first()
        if customer is not None:
            print("Building Customer Object")
            return build_user_object(customer.id, customer.name, 'Customer')
        else:
            # Staff
            staff = Staff.query.filter(and_(Staff.username == n, Staff.password == p)).first()
            if staff is not None:
                print("Building Staff Object")
                return build_user_object(staff.id, staff.name, 'Staff')

    return None


###########################################################################################
#                               User Specific Posts                                       #
###########################################################################################


# For Owner
@app.route('/create_new_staff', methods=["POST"])
def create_new_staff():
    print('Trying to create staff')

    n = request.form['staff_name']
    u = request.form['staff_username']
    p = request.form['staff_password']

    if (n is not None) and (u is not None) and (p is not None):
        try:
            new_staff = Staff(n, u, p)
            db.session.add(new_staff)
            db.session.commit()
        except IntegrityError:
            print('Error User exists')
            flash('Sorry a user with that username already exists')
            return redirect(url_for("dashboard"))
        print("New Staff Member Added to the roster")
    else:
        print("Form was invalid")

    return redirect(url_for("dashboard", info=session["info"]))


# For Staff
@app.route('/sign_up_for_event', methods=["POST"])
def sign_up_for_event():
    staff_id = request.form['staff_id']
    event_id = request.form['event_id']

    # Check if form is valid
    if (staff_id is not None) and (event_id is not None):
        event = Event.query.filter_by(id=event_id).first()

        # Check if Event exists
        if event is not None:
            # Try to assign
            if event.staff_id_1 is None:
                event.staff_id_1 = staff_id
                db.session.commit()
            elif event.staff_id_2 is None:
                event.staff_id_2 = staff_id
                db.session.commit()
            elif event.staff_id_3 is None:
                event.staff_id_3 = staff_id
                db.session.commit()
            else:
                print("That event is already fully scheduled")
        else:
            print("Invalid Signup: Event ID was not found")

        print("New Staff Member Added to the roster")
    else:
        print("Form was invalid")

    # Fix
    return render_template('dashboard.html')


# For Customer
@app.route('/cancel_event', methods=["POST"])
def cancel_event():
    event_id = request.form['event_id']

    # Check if form is valid
    if event_id is not None:
        event = Event.query.filter_by(id=event_id).first()

        # Check if Event exists
        if event is not None:
            db.session.delete(event)
            db.session.commit()
            print("Removed the event")
        else:
            print("Event not found")
    else:
        print("Form was invalid")
    # Fix
    return render_template('dashboard.html')


###########################################################################################
#                               Universal Routes                                          #
###########################################################################################

@app.route('/', methods=["GET", "POST"])
def default():
    if "info" in session:
        return redirect(url_for("dashboard", info=session["info"]))

    return render_template('login.html')


@app.route('/login', methods=["GET", "POST"])
def sign_in():
    print("SIGN_IN")
    session.clear()
    if request.method == 'GET':
        return redirect(url_for('default'))

    auth = get_user(request.form['username'], request.form['password'])
    if auth:
        session["info"] = auth
        return redirect(url_for("dashboard", info=session["info"]))
    else:
        error = "Sorry Invalid Credentials"
        return render_template('login.html', error=error)


@app.route('/signup', methods=["GET", "POST"])
def sign_up():
    print("SIGN_UP")
    if request.method == 'GET':
        return redirect(url_for('default'))

    user = get_user(request.form['username'], request.form['password'])
    if user is not None:
        return redirect(url_for("dashboard", info=user))

    error = "Sorry Invalid Credentials"
    return render_template('login.html', error=error)


@app.route('/dashboard', methods=["GET", "POST"])
def dashboard():
    if "info" in session:
        # renew object
        print("Already Logged in")

        if session['info']['user_type'] == "Owner":
            session['info'] = build_user_object(None, session['info']['name'], session['info']['user_type'])
        else:
            session["info"] = build_user_object(session['info']['id'],
                                                session['info']['name'], session['info']['user_type'])

        return render_template('dashboard.html', info=session['info'])
    else:
        print("Not Logged in")
        return redirect(url_for("default"))


@app.route('/logout',  methods=["GET", "POST"])
def logout():
    session.clear()
    return redirect(url_for("default"))


app.secret_key = "this is a terrible secret key"


if __name__ == '__main__':
    app.run()
