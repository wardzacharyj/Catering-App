from flask import Flask, session, redirect, url_for, escape, request, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_
from sqlalchemy import or_

# from sqlalchemy.orm import sessionmaker

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cater.db'
db = SQLAlchemy(app)

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

    def as_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "password": self.password,
            "name": self.name

        }


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    staff_id_1 = db.Column(db.Integer, db.ForeignKey('staff.id'))
    staff_id_2 = db.Column(db.Integer, db.ForeignKey('staff.id'))
    staff_id_3 = db.Column(db.Integer, db.ForeignKey('staff.id'))
    event_name = db.Column(db.String(30), nullable=False)
    event_location = db.Column(db.String(25), nullable=False)
    event_date = db.Column(db.String(18), nullable=False)

    def __init__(self, customer_id, event_name, event_location, event_date):
        self.customer_id = customer_id
        self.event_name = event_name
        self.event_location = event_location
        self.event_date = event_date

    def __repr__(self):
        return '<Event = %r %r %r %r %r>' % (self.id, self.customer_id,
                                             self.staff_id_1, self.staff_id_2, self.staff_id_3)

    def as_dict(self):
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "staff_id_1": self.staff_id_1,
            "staff_id_2": self.staff_id_2,
            "staff_id_3": self.staff_id_3,
            "event_name": self.event_name,
            "event_location": self.event_location,
            "event_date": self.event_date,

        }


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
        e_with_staff = [event.as_dict() for event in Event.query.filter(
            or_(
                Event.staff_id_1.isnot(None), Event.staff_id_2.isnot(None), Event.staff_id_3.isnot(None))).all()]

        for e in e_with_staff:
            s1 = Staff.query.filter_by(id=e['staff_id_1']).first()
            s2 = Staff.query.filter_by(id=e['staff_id_2']).first()
            s3 = Staff.query.filter_by(id=e['staff_id_3']).first()
            if s1:
                e.staff_id_1 = s1['name']
            if s2:
                e.staff_id_2 = s2['name']
            if s3:
                e.staff_id_3 = s3['name']

        user_info['events_with_staff'] = e_with_staff

        # All Events with no staff assigned
        e_no_staff = [event.as_dict() for event in Event.query.filter(
            and_(
                Event.staff_id_1.is_(None), Event.staff_id_2.is_(None), Event.staff_id_3.is_(None))).all()]

        for e in e_no_staff:
            s1 = Staff.query.filter_by(id=e['staff_id_1']).first()
            s2 = Staff.query.filter_by(id=e['staff_id_2']).first()
            s3 = Staff.query.filter_by(id=e['staff_id_3']).first()
            if s1:
                e.staff_id_1 = s1['name']
            if s2:
                e.staff_id_2 = s2['name']
            if s3:
                e.staff_id_3 = s3['name']

        user_info['events_no_staff'] = e_no_staff


    elif user_type == "Staff":
        # Save Staff Name
        user_info['id'] = o_id

        user_info['name'] = name

        # All Events signed up for
        m_event = [event.as_dict() for event in Event.query.filter(
            or_(
                Event.staff_id_1 == o_id, Event.staff_id_2 == o_id, Event.staff_id_3 == o_id)).all()]

        for e in m_event:
            e.staff_id_1 = (Staff.query.filter_by(id=e.staff_id_1).first()).name
            e.staff_id_2 = (Staff.query.filter_by(id=e.staff_id_2).first()).name
            e.staff_id_3 = (Staff.query.filter_by(id=e.staff_id_3).first()).name

        user_info['my_events'] = m_event

        # All Events with at least 1 empty staff
        o_event = [event.as_dict() for event in Event.query.filter(
            or_(Event.staff_id_1.is_(None), Event.staff_id_2.is_(None), Event.staff_id_3.is_(None))).all()]

        user_info['open_events'] = o_event
    else:
        # Save Name
        user_info['id'] = o_id
        user_info['name'] = name

        # All Events scheduled
        # [staff.as_dict() for staff in Staff.query.order_by(Staff.name).all()]
        my_res = [event.as_dict() for event in Event.query.filter_by(customer_id=o_id).all()]
        print(my_res)
        for e in my_res:
            s1 = Staff.query.filter_by(id=e['staff_id_1']).first()
            s2 = Staff.query.filter_by(id=e['staff_id_2']).first()
            s3 = Staff.query.filter_by(id=e['staff_id_3']).first()
            if s1:
                e.staff_id_1 = s1['name']
            if s2:
                e.staff_id_2 = s2['name']
            if s3:
                e.staff_id_3 = s3['name']

        user_info['my_reservations'] = my_res

    return user_info


def get_user(n, p):
    # Owner
    if n == 'owner' and p == 'pass':
        print("Building Owner Object")
        return build_user_object(None, 'Owner', 'Owner')
    else:
        # Customer
        customer = Customer.query.filter(and_(Customer.username == n, Customer.password == p)).first()
        if customer:
            print("Building Customer Object")
            return build_user_object(customer.id, customer.name, 'Customer')
        else:
            # Staff
            staff = Staff.query.filter(and_(Staff.username == n, Staff.password == p)).first()
            if staff:
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

    if (len(n) > 0) and (len(u) > 0) and (len(p) > 0):
        try:
            new_staff = Staff(n, u, p)
            db.session.add(new_staff)
            db.session.commit()
        except IntegrityError:
            flash('Sorry a user with that username already exists')
            return redirect(url_for("dashboard"))
    else:
        flash('Make sure you fill out the entire form')
        return redirect(url_for("dashboard"))


# For Staff
@app.route('/sign_up_for_event', methods=["POST"])
def sign_up_for_event():
    staff_id = request.form['staff_id']
    event_id = request.form['event_id']

    # Check if form is valid
    if (len(staff_id) > 0) and (len(event_id) > 0):
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
@app.route('/create_event', methods=["POST"])
def create_event():

    name = request.form['event_name']
    place = request.form['event_place']
    date = request.form['event_date']

    if (len(name) > 0) and (len(place) > 0) and (len(date) > 0):
        e = Event.query.filter_by(event_date=date).first()
        if e:
            flash('Sorry there is already an event scheduled for that day')
            return redirect(url_for('dashboard'))
        else:
            print(session['info'])
            event = Event(session['info']['id'], name, place, date)
            db.session.add(event)
            db.session.commit()
            return redirect(url_for('dashboard'))

    else:
        flash('The form was filled out incorrectly, please be careful to fill all the fields')
        return redirect(url_for('dashboard.html'))


# For Customer
@app.route('/cancel_event/<event_index>')
def cancel_event(event_index):
    print('Cancel Event Session: %r' % (session['info']))
    delete_event_id = session['info']['my_reservations'][int(event_index)]['id']
    event = Event.query.filter_by(id=delete_event_id).first()
    db.session.delete(event)
    db.session.commit()
    '''
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
    '''
    return redirect(url_for('dashboard'))


###########################################################################################
#                               Universal Routes                                          #
###########################################################################################

@app.route('/', methods=["GET", "POST"])
def default():
    if "info" in session:
        return redirect(url_for("dashboard"))

    return render_template('login.html')


@app.route('/login', methods=["GET", "POST"])
def sign_in():
    print("SIGN_IN")
    if request.method == 'GET':
        return redirect(url_for('default'))

    auth = get_user(request.form['username'], request.form['password'])
    if auth:
        session["info"] = auth
        return redirect(url_for("dashboard"))
    else:
        print('Invalid Credentials')
        flash('Sorry Invalid Credentials')
        return render_template('login.html')


@app.route('/signup', methods=["GET", "POST"])
def signup():
    print("SIGN_UP")
    if request.method == 'GET':
        return redirect(url_for('default'))

    name = request.form['name']
    username = request.form['username']
    password = request.form['password']

    if (len(name) > 0) and (len(username) > 0) and (len(password) > 0):
        c = Customer.query.filter_by(username=username).first()
        if c:
            flash('Another Customer already has that username')
            return render_template('default')
        else:
            customer = Customer(name, username, password)
            db.session.add(customer)
            db.session.commit()
            session['info'] = get_user(username, password)
            print(session['info'])
            return redirect(url_for("dashboard"))
    else:
        flash('Please Fill out all the fields before signing up')
        return render_template('login.html')


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

        print('Session: %r' % (session['info']))

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
