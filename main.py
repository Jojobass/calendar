from flask import Flask, abort, make_response
from flask_restful import Api, Resource, reqparse, inputs, fields, marshal_with, marshal
from flask_sqlalchemy import SQLAlchemy
import sys
import datetime

app = Flask(__name__)
api = Api(app)
db = SQLAlchemy()

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///calendar.db'

db.init_app(app)


# Event and all it's params for the db
class Event(db.Model):
    __tablename__ = 'calendar'
    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String(80), nullable=False)
    date = db.Column(db.Date, nullable=False)

with app.app_context():
    db.create_all()

# arguments for POST in Events
parser_events_post = reqparse.RequestParser()
parser_events_post.add_argument(
    "date",
    type=inputs.date,
    help="The event date with the correct format is required! The correct format is YYYY-MM-DD!",
    required=True,
    location='args'
)
parser_events_post.add_argument(
    "event",
    type=str,
    help="The event name is required!",
    required=True,
    location='args'
)
# arguments for GET in Events
parser_events_get = reqparse.RequestParser()
parser_events_get.add_argument(
    "start_time",
    type=inputs.date,
    help="The event date with the correct format is required! The correct format is YYYY-MM-DD!",
    required=False,
    location='args'
)
parser_events_get.add_argument(
    "end_time",
    type=inputs.date,
    help="The event date with the correct format is required! The correct format is YYYY-MM-DD!",
    required=False,
    location='args'
)

# fields in the response
mfields = {
    "id": fields.Integer,
    "event": fields.String,
    "date": fields.DateTime(dt_format='iso8601')
}


class Events(Resource):
    # @marshal_with(mfields)
    def post(self):
        args = parser_events_post.parse_args()
        db.session.add(Event(event=args["event"], date=args["date"]))
        db.session.commit()
        success = {'message': 'The event has been added!', 'event': args['event'], 'date': str(args['date'].date())}
        return success, 200

    @marshal_with(mfields)
    def get(self):
        args = parser_events_get.parse_args()
        if args['start_time'] and args['end_time']:
            return Event.query.filter(Event.date.between(args['start_time'], args['end_time'])).all()
        else:
            return Event.query.all()


class Today(Resource):
    @marshal_with(mfields)
    def get(self):
        return Event.query.filter(Event.date == datetime.date.today()).all()


class EventByID(Resource):
    @marshal_with(mfields)
    def get(self, event_id):
        event = Event.query.filter(Event.id == event_id).first()
        if event is None:
            abort(404, "The event doesn't exist!")
        return event

    def delete(self, event_id):
        event = Event.query.filter(Event.id == event_id).first()
        if event is None:
            abort(404, "The event doesn't exist!")
        else:
            db.session.delete(event)
            db.session.commit()
            return {"message": "The event has been deleted!"}


class MainPage(Resource):
    # @marshal_with(mfields)
    def get(self):
        response = make_response('''
Welcome to the CalendarAPI!

There are all the function that are currently supported:
[GET /event] - get all events
[GET /event?start_time=<YYYY-MM-DD>&end_time=<YYYY-MM-DD>] - show all events in period (start_time, end_time]
[POST /event?event=<string>&date=<YYYY-MM-DD>] - add new event
[GET /event/today] - get all events for today
[GET /event/<int:event_id>] - get event with id = <event_id></a>''', 200)
        response.mimetype = "text/plain"
        return response



# where is everything located
api.add_resource(MainPage, '/')
api.add_resource(Events, '/event')
api.add_resource(Today, '/event/today')
api.add_resource(EventByID, '/event/<int:event_id>')

# TEST ZONE--------------------------------------------------------------


# do not change the way you run the program
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run(debug=True)
    # app.run(debug=True)