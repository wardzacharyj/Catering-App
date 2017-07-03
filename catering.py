from flask import Flask, session, redirect, url_for, escape, request, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_
from sqlalchemy import or_


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///catering.db'
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
    if user_type == 'Owner':
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
                e['staff_id_1'] = s1.name
            if s2:
                e['staff_id_2'] = s2.name
            if s3:
                e['staff_id_3'] = s3.name

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
                Event.staff_id_1 == user_info['id'], Event.staff_id_2 == user_info['id'],
                Event.staff_id_3 == user_info['id'])).all()]

        for e in m_event:
            print()
            try:
                e['staff_id_1'] = ((Staff.query.filter_by(id=e['staff_id_1']).first()).as_dict())['name']
            except AttributeError:
                pass

            try:
                e['staff_id_2'] = ((Staff.query.filter_by(id=e['staff_id_2']).first()).as_dict())['name']
            except AttributeError:
                pass

            try:
                e['staff_id_3'] = ((Staff.query.filter_by(id=e['staff_id_3']).first()).as_dict())['name']
            except AttributeError:
                pass

        user_info['my_events'] = m_event

        # All Events with at least 1 empty staff
        pre_query = Event.query.filter(or_(Event.staff_id_1.is_(None),
                                           Event.staff_id_2.is_(None), Event.staff_id_3.is_(None))).all()
        filtered_list = []
        for e in pre_query:
            if e.staff_id_1 != o_id and e.staff_id_2 != o_id and e.staff_id_3 != o_id:
                s1 = Staff.query.filter_by(id=e.staff_id_1).first()
                s2 = Staff.query.filter_by(id=e.staff_id_2).first()
                s3 = Staff.query.filter_by(id=e.staff_id_3).first()
                if s1:
                    e.staff_id_1 = s1.name
                if s2:
                    e.staff_id_2 = s2.name
                if s3:
                    e.staff_id_3 = s3.name
                filtered_list.append(e)

        o_event = [event.as_dict() for event in filtered_list]

        user_info['open_events'] = o_event
    else:
        # Save Name
        user_info['id'] = o_id
        user_info['name'] = name

        # All Events scheduled
        my_res = [event.as_dict() for event in Event.query.filter_by(customer_id=o_id).all()]

        for e in my_res:
            s1 = Staff.query.filter_by(id=e['staff_id_1']).first()
            s2 = Staff.query.filter_by(id=e['staff_id_2']).first()
            s3 = Staff.query.filter_by(id=e['staff_id_3']).first()
            if s1:
                e['staff_id_1'] = s1.name
            if s2:
                e['staff_id_2'] = s2.name
            if s3:
                e['staff_id_3'] = s3.name

        user_info['my_reservations'] = my_res

    return user_info


def get_user(n, p):
    # Owner
    if n == 'owner' and p == 'pass':
        return build_user_object(None, 'Owner', 'Owner')
    else:
        # Customer
        customer = Customer.query.filter(and_(Customer.username == n, Customer.password == p)).first()
        if customer:
            return build_user_object(customer.id, customer.name, 'Customer')
        else:
            # Staff
            staff = Staff.query.filter(and_(Staff.username == n, Staff.password == p)).first()
            if staff:
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

    if u == 'owner':
        flash('Sorry a user with that username already exists')
        return redirect(url_for('dashboard'))

    if (len(n) > 0) and (len(u) > 0) and (len(p) > 0):
        try:
            new_staff = Staff(n, u, p)
            user = Customer.query.filter_by(username=n).first()
            if user:
                flash('Sorry a user with that username already exists')
            else:
                db.session.add(new_staff)
                db.session.commit()
        except IntegrityError:
            flash('Sorry a user with that username already exists')
    else:
        flash('Make sure you fill out the entire form')

    return redirect(url_for("dashboard"))


# For Staff
@app.route('/unsubscribe_for_event/<event_index>')
def unsubscribe_for_event(event_index):

    event_id = session['info']['my_events'][int(event_index)]['id']
    event = Event.query.filter_by(id=event_id).first()

    # Check if Event exists
    if event:
        if event.staff_id_1 == session['info']['id']:
            event.staff_id_1 = None
            db.session.commit()
        elif event.staff_id_2 == session['info']['id']:
            event.staff_id_2 = None
            db.session.commit()
        elif event.staff_id_3 == session['info']['id']:
            event.staff_id_3 = None
            db.session.commit()
        else:
            print("Error with staff id")

    return redirect(url_for('dashboard'))


@app.route('/sign_up_for_event/<event_index>')
def sign_up_for_event(event_index):

    event_id = session['info']['open_events'][int(event_index)]['id']
    event = Event.query.filter_by(id=event_id).first()

    # Check if Event exists
    if event is not None:
        if event.staff_id_1 is None:
            event.staff_id_1 = session['info']['id']
            db.session.add(event)
            db.session.commit()
        elif event.staff_id_2 is None:
            event.staff_id_2 = session['info']['id']
            db.session.add(event)
            db.session.commit()
        elif event.staff_id_3 is None:
            event.staff_id_3 = session['info']['id']
            db.session.add(event)
            db.session.commit()
        else:
            print("That event is already fully scheduled")
    else:
        print("Invalid Signup: Event ID was not found")

    return redirect(url_for('dashboard'))


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
            event = Event(session['info']['id'], name, place, date)
            db.session.add(event)
            db.session.commit()
            return redirect(url_for('dashboard'))

    else:
        flash('The form was filled out incorrectly, please be careful to fill all the fields')
        return redirect(url_for('dashboard'))


# For Customer
@app.route('/cancel_event/<event_index>')
def cancel_event(event_index):
    delete_event_id = session['info']['my_reservations'][int(event_index)]['id']
    event = Event.query.filter_by(id=delete_event_id).first()
    db.session.delete(event)
    db.session.commit()
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

    if username == "owner":
        flash('That username is already taken')
        return render_template('login.html')

    if (len(name) > 0) and (len(username) > 0) and (len(password) > 0):
        c = Customer.query.filter_by(username=username).first()
        s = Staff.query.filter_by(username=username).first()
        if c or s:
            flash('Another Customer already has that username')
            return render_template('login.html')
        else:
            customer = Customer(name, username, password)
            db.session.add(customer)
            db.session.commit()
            session['info'] = get_user(username, password)
            return redirect(url_for("dashboard"))
    else:
        flash('Please Fill out all the fields before signing up')
        return render_template('login.html')


@app.route('/dashboard', methods=["GET", "POST"])
def dashboard():
    if "info" in session:
        # renew object

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
