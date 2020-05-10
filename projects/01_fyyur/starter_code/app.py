# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import sys

import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from datetime import datetime

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String(256), nullable=False)
    website = db.Column(db.String(512))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(1024))
    shows = db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self):
        return "<Venue {}, {}, {}, {}>".format(self.id, self.name, self.city, self.state)


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(512))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(1024))
    shows = db.relationship('Show', backref='artist', lazy=True)

    def __repr__(self):
        return "<Artist {}, {}, {}, {}>".format(self.id, self.name, self.city, self.state)


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return "<Show {}, {}, {}>".format(self.artist_id, self.venue_id, self.start_time)


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(str(value))
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    data = []
    venue_query_result = Venue.query.with_entities(
        Venue.city, Venue.state
    ).group_by(Venue.city, Venue.state).order_by(Venue.state)

    for v in venue_query_result:
        venue_name_query_result = Venue.query.with_entities(
            Venue.id, Venue.name
        ).filter(
            Venue.city == v.city, Venue.state == v.state
        ).order_by(Venue.id).all()

        venues_arr = []
        for vn in venue_name_query_result:
            venue_obj = {
                "id": vn.id,
                "name": vn.name,
                "num_upcoming_shows": Show.query.filter(Show.id == vn.id, Show.start_time > datetime.now()).count()
            }
            venues_arr.append(venue_obj)

        obj = {
            "city": v.city,
            "state": v.state,
            "venues": venues_arr
        }
        data.append(obj)

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # search for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = request.form.get('search_term', '')
    data = []
    venue_query = Venue.query.with_entities(Venue.id, Venue.name).filter(
        Venue.name.ilike("%{}%".format(search_term))
    ).order_by(Venue.id).all()

    for v in venue_query:
        obj = {
            "id": v.id,
            "name": v.name,
            "num_upcoming_shows": Show.query.filter(Show.venue_id == v.id, Show.start_time > datetime.now()).count()
        }
        data.append(obj)

    response = {
        "count": len(venue_query),
        "data": data
    }

    return render_template('pages/search_venues.html', results=response, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    venue_query = Venue.query.get(venue_id)
    data = venue_query.__dict__
    data["genres"] = data["genres"].split(",")

    data["past_shows"] = []
    data["past_shows_count"] = Show.query.filter(Show.venue_id == venue_query.id,
                                                 Show.start_time <= datetime.now()).count()
    data["upcoming_shows"] = []
    data["upcoming_shows_count"] = Show.query.filter(Show.venue_id == venue_query.id,
                                                     Show.start_time > datetime.now()).count()

    join_query = Show.query.join(Artist, Artist.id == Show.artist_id).add_columns(
        Artist.id.label("artist_id"),
        Artist.name.label("artist_name"),
        Artist.image_link.label("artist_image_link"),
        Show.start_time.label("start_time")
    )

    if data["past_shows_count"] > 0:
        data["past_shows"] = join_query.filter(
            Show.venue_id == venue_query.id,
            Show.start_time <= datetime.now()
        ).all()

    if data["upcoming_shows_count"] > 0:
        data["upcoming_shows"] = join_query.filter(
            Show.venue_id == venue_query.id,
            Show.start_time > datetime.now()
        ).all()

    return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error = False
    form_data = {}

    try:
        form_data["name"] = request.form["name"]
        form_data["city"] = request.form["city"]
        form_data["state"] = request.form["state"]
        form_data["address"] = request.form["address"]
        form_data["phone"] = request.form["phone"]
        form_data["genres"] = ", ".join(request.form.getlist("genres"))
        form_data["facebook_link"] = request.form["facebook_link"]

        new_venue = Venue(
            name=form_data["name"],
            city=form_data["city"],
            state=form_data["state"],
            address=form_data["address"],
            phone=form_data["phone"],
            genres=form_data["genres"],
            facebook_link=form_data["facebook_link"],
            image_link="",
            website="",
            seeking_talent=False,
            seeking_description=""
        )

        db.session.add(new_venue)
        db.session.commit()

    except:
        error = True
        db.session.rollback()
        print(sys.exc_info(), file=sys.stderr)

    finally:
        db.session.close()
        if error:
            # on unsuccessful db insert, flash an error
            flash('An error occurred. Venue {} could not be listed.'.format(form_data["name"]))
        else:
            # on successful db insert, flash success
            flash('Venue {} was successfully listed!'.format(form_data['name']))

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    error = False

    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()

    except:
        error = True
        db.session.rollback()
        print(sys.exc_info(), file=sys.stderr)

    finally:
        db.session.close()
        if error:
            return jsonify({"success": False})

    return jsonify({"success": True})


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    artist_query = Artist.query.with_entities(Artist.id, Artist.name).order_by(Artist.id).all()
    return render_template('pages/artists.html', artists=artist_query)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # search for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get('search_term', '')
    data = []
    artist_query = Artist.query.with_entities(Artist.id, Artist.name).filter(
        Artist.name.ilike("%{}%".format(search_term))
    ).order_by(Artist.id).all()

    for a in artist_query:
        obj = {
            "id": a.id,
            "name": a.name,
            "num_upcoming_shows": Show.query.filter(Show.artist_id == a.id, Show.start_time > datetime.now()).count()
        }
        data.append(obj)

    response = {
        "count": len(artist_query),
        "data": data
    }

    return render_template('pages/search_artists.html', results=response, search_term=search_term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    artist_query = Artist.query.get(artist_id)
    data = artist_query.__dict__
    data["genres"] = data["genres"].split(",")

    data["past_shows"] = []
    data["past_shows_count"] = Show.query.filter(Show.artist_id == artist_query.id,
                                                 Show.start_time <= datetime.now()).count()
    data["upcoming_shows"] = []
    data["upcoming_shows_count"] = Show.query.filter(Show.artist_id == artist_query.id,
                                                     Show.start_time > datetime.now()).count()

    join_query = Show.query.join(
        Venue, Venue.id == Show.venue_id
    ).add_columns(
        Venue.id.label("venue_id"),
        Venue.name.label("venue_name"),
        Venue.image_link.label("venue_image_link"),
        Show.start_time.label("start_time")
    )

    if data["past_shows_count"] > 0:
        data["past_shows"] = join_query.filter(
            Show.artist_id == artist_query.id,
            Show.start_time <= datetime.now()
        ).all()

    if data["upcoming_shows_count"] > 0:
        data["upcoming_shows"] = join_query.filter(
            Show.artist_id == artist_query.id,
            Show.start_time > datetime.now()
        ).all()

    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    return render_template('forms/edit_artist.html', form=form, artist=Artist.query.get(artist_id))


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    error = False

    try:
        artist = Artist.query.get(artist_id)
        artist.name = request.form["name"]
        artist.city = request.form["city"]
        artist.state = request.form["state"]
        artist.phone = request.form["phone"]
        artist.genres = ", ".join(request.form.getlist("genres"))
        artist.facebook_link = request.form["facebook_link"]
        db.session.commit()

    except:
        error = True
        db.session.rollback()
        print(sys.exc_info(), file=sys.stderr)

    finally:
        db.session.close()
        if error:
            flash('An error occurred while updating Artist info.')
        else:
            flash('Artist info updated successfully.')

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    return render_template('forms/edit_venue.html', form=form, venue=Venue.query.get(venue_id))


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    error = False

    try:
        venue = Venue.query.get(venue_id)
        venue.name = request.form["name"]
        venue.city = request.form["city"]
        venue.state = request.form["state"]
        venue.address = request.form["address"]
        venue.phone = request.form["phone"]
        venue.genres = ", ".join(request.form.getlist("genres"))
        venue.facebook_link = request.form["facebook_link"]
        db.session.commit()

    except:
        error = True
        db.session.rollback()
        print(sys.exc_info(), file=sys.stderr)

    finally:
        db.session.close()
        if error:
            flash('An error occurred while updating Venue info.')
        else:
            flash('Venue info updated successfully.')

    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    error = False
    form_data = {}

    try:
        form_data["name"] = request.form["name"]
        form_data["city"] = request.form["city"]
        form_data["state"] = request.form["state"]
        form_data["phone"] = request.form["phone"]
        form_data["genres"] = ", ".join(request.form.getlist("genres"))
        form_data["facebook_link"] = request.form["facebook_link"]

        new_artist = Artist(
            name=form_data["name"],
            city=form_data["city"],
            state=form_data["state"],
            phone=form_data["phone"],
            genres=form_data["genres"],
            facebook_link=form_data["facebook_link"],
            image_link="",
            website="",
            seeking_venue=False,
            seeking_description=""
        )

        db.session.add(new_artist)
        db.session.commit()

    except:
        error = True
        db.session.rollback()
        print(sys.exc_info(), file=sys.stderr)

    finally:
        db.session.close()
        if error:
            flash('An error occurred. Artist {} could not be listed.'.format(form_data["name"]))
        else:
            flash('Artist {} was successfully listed!'.format(form_data['name']))

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    data = Show.query.join(
        Artist, Artist.id == Show.artist_id
    ).join(
        Venue, Venue.id == Show.venue_id
    ).add_columns(
        Venue.id.label("venue_id"),
        Venue.name.label("venue_name"),
        Artist.id.label("artist_id"),
        Artist.name.label("artist_name"),
        Artist.image_link.label("artist_image_link"),
        Show.start_time.label("start_time")
    ).all()

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    error = False
    form_data = {}

    try:
        form_data["artist_id"] = request.form["artist_id"]
        form_data["venue_id"] = request.form["venue_id"]
        form_data["start_time"] = request.form["start_time"]

        new_show = Show(
            venue_id=form_data["artist_id"],
            artist_id=form_data["venue_id"],
            start_time=form_data["start_time"]
        )

        db.session.add(new_show)
        db.session.commit()

    except:
        error = True
        db.session.rollback()
        print(sys.exc_info(), file=sys.stderr)

    finally:
        db.session.close()
        if error:
            flash('An error occurred. Show could not be listed.')
        else:
            flash('Show was successfully listed!')

    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ---------------------------------------------------------------------------- #
# Launch.
# ---------------------------------------------------------------------------- #

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
