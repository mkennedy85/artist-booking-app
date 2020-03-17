#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from datetime import datetime
import pytz
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import distinct
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from forms import *
from flask_migrate import Migrate
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref='venue', lazy=True)

    def get_venue(venue):
      data = {'id': venue.id, 'name': venue.name}
      return data

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref='artist', lazy=True)

class Show(db.Model):
    __tablename__ = 'show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    start_time = db.Column(db.String(120), nullable=False)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():

  data=[]
  areas = Venue.query.distinct('city', 'state').all()
  for area in areas:
    venues = Venue.query.filter(Venue.city == area.city, Venue.state == area.state).all()
    record = {
      'city': area.city,
      'state': area.state,
      'venues': [venue.get_venue() for venue in venues],
    }
    data.append(record)

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():

  venues_object = Venue.query.filter(Venue.name.ilike(f"%{request.form.get('search_term', '')}%")).all()

  search_object = {
    'count': len(venues_object),
    'data': []
  }

  for venue in venues_object:
    shows = Show.query.filter(Show.artist_id == venue.id).all()
    venue_object = {
      'id': venue.id,
      'name': venue.name,
      'num_upcoming_shows': len(shows)
    }
    search_object['data'].append(venue_object)

  return render_template('pages/search_venues.html', results=search_object, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

  venue = Venue.query.join(Venue.shows, full=True).filter(Venue.id == venue_id).first()

  venue_object = {'name': venue.name,
                  'genres': venue.genres.split(','),
                  'address': venue.address,
                  'city': venue.city,
                  'state': venue.state,
                  'phone': venue.phone,
                  'website': venue.website,
                  'facebook_link': venue.facebook_link,
                  'image_link': venue.image_link,
                  'seeking_talent': venue.seeking_talent,
                  'seeking_description': venue.seeking_description,
                  'past_shows': [],
                  'upcoming_shows': [],
                  'upcoming_shows_count': 0}
  if venue.shows is not None:
    for show in venue.shows:
        artist = Artist.query.filter(Artist.id == show.artist_id).first()
        show_details = {'artist_id': artist.id,
                  'artist_name':  artist.name,
                  'artist_image_link':  artist.image_link,
                  'start_time':  show.start_time}
        if dateutil.parser.parse(show.start_time) >= datetime.utcnow().replace(tzinfo=pytz.utc):
          venue_object['upcoming_shows'].append(show_details)
          venue_object['upcoming_shows_count'] += 1
        else:
          venue_object['past_shows'].append(show_details)

  return render_template('pages/show_venue.html', venue=venue_object)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  
  if request.content_type == 'application/x-www-form-urlencoded':
    try:
      venue = Venue(name=request.form['name'])
      venue.city = request.form['city']
      venue.state = request.form['state']
      venue.address = request.form['address']
      venue.genres = ",".join(request.form['genres'])
      venue.phone = request.form['phone']
      venue.website = request.form['website']
      venue.image_link = request.form['image_link']
      venue.facebook_link = request.form['facebook_link']
      venue.seeking_talent = request.form['seeking_talent']
      venue.seeking_description = request.form['seeking_description']
      db.session.add(venue)
      db.session.commit()
    except:
      error = True
      db.session.rollback()
      app.logger.debug(request.form)
      print(sys.exc_info())
    finally:
      db.session.close()
    if not error:
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    else:
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    return render_template('pages/home.html')
  elif (request.content_type == 'application/json'):
    try:
      venue = Venue(name=request.get_json()['name'])
      venue.city = request.get_json()['city']
      venue.state = request.get_json()['state']
      venue.address = request.get_json()['address']
      venue.genres = ",".join(request.get_json()['genres'])
      venue.phone = request.get_json()['phone']
      venue.website = request.get_json()['website']
      venue.image_link = request.get_json()['image_link']
      venue.facebook_link = request.get_json()['facebook_link']
      venue.seeking_talent = request.get_json()['seeking_talent']
      venue.seeking_description = request.get_json()['seeking_description']
      db.session.add(venue)
      db.session.commit()
    except:
      error = True
      db.session.rollback()
      app.logger.debug(request.form)
      print(sys.exc_info())
    finally:
      db.session.close()
    if not error:
      return f"""{request.get_json()['name']} has been successfully created"""
    else:
      return f"""{request.get_json()['name']} could not be created"""
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():

  artists = Artist.query.all()
  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():

  artists_object = Artist.query.filter(Artist.name.ilike(f"%{request.form.get('search_term', '')}%")).all()

  search_object = {
    'count': len(artists_object),
    'data': []
  }

  for artist in artists_object:
    shows = Show.query.filter(Show.artist_id == artist.id).all()
    artist_object = {
      'id': artist.id,
      'name': artist.name,
      'num_upcoming_shows': len(shows)
    }
    search_object['data'].append(artist_object)

  return render_template('pages/search_artists.html', results=search_object, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

  artist = Artist.query.join(Artist.shows, full=True).filter(Artist.id == artist_id).first()

  artist_object = {'name': artist.name,
                'genres': artist.genres.split(','),
                'city': artist.city,
                'state': artist.state,
                'phone': artist.phone,
                'website': artist.website,
                'facebook_link': artist.facebook_link,
                'image_link': artist.image_link,
                'seeking_venue': artist.seeking_venue,
                'seeking_description': artist.seeking_description,
                'past_shows': [],
                'upcoming_shows': [],
                'upcoming_shows_count': 0}
  if artist.shows is not None:
    for show in artist.shows:
      venue = Venue.query.filter(Venue.id == show.venue_id).first()
      show_details = {'venue_id': venue.id,
                'venue_name':  venue.name,
                'venue_image_link':  venue.image_link,
                'start_time':  show.start_time}
      if dateutil.parser.parse(show.start_time) >= datetime.utcnow().replace(tzinfo=pytz.utc):
        artist_object['upcoming_shows'].append(show_details)
        artist_object['upcoming_shows_count'] += 1
      else:
        artist_object['past_shows'].append(show_details)

  return render_template('pages/show_artist.html', artist=artist_object)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
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
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  
  if request.content_type == 'application/x-www-form-urlencoded':
    try:
      artist = Artist(name=request.form['name'])
      artist.city = request.form['city']
      artist.state = request.form['state']
      artist.genres = ",".join(request.form['genres'])
      artist.phone = request.form['phone']
      artist.image_link = request.form['image_link']
      artist.facebook_link = request.form['facebook_link']
      artist.seeking_venue = request.form['seeking_venue']
      db.session.add(artist)
      db.session.commit()
    except:
      error = True
      db.session.rollback()
      app.logger.debug(request.form)
      print(sys.exc_info())
    finally:
      db.session.close()
    if not error:
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    else:
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    return render_template('pages/home.html')
  elif (request.content_type == 'application/json'):
    try:
      artist = Artist(name=request.get_json()['name'])
      artist.city = request.get_json()['city']
      artist.state = request.get_json()['state']
      artist.genres = ",".join(request.get_json()['genres'])
      artist.phone = request.get_json()['phone']
      artist.website = request.get_json()['website']
      artist.image_link = request.get_json()['image_link']
      artist.facebook_link = request.get_json()['facebook_link']
      artist.seeking_venue = request.get_json()['seeking_venue']
      artist.seeking_description = request.get_json()['seeking_description']
      db.session.add(artist)
      db.session.commit()
    except:
      error = True
      db.session.rollback()
      app.logger.debug(request.form)
      print(sys.exc_info())
    finally:
      db.session.close()
    if not error:
      return f"""{request.get_json()['name']} has been successfully created"""
    else:
      return f"""{request.get_json()['name']} could not be created"""
    return render_template('pages/home.html')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  
  shows = Show.query.all()
  shows_object = []

  for show in shows:
    if dateutil.parser.parse(show.start_time) >= datetime.utcnow().replace(tzinfo=pytz.utc):
      artist = Artist.query.filter(Artist.id == show.artist_id).first()
      venue = Venue.query.filter(Venue.id == show.venue_id).first()
      show_object = {
        'venue_id': show.venue_id,
        'venue_name': venue.name,
        'artist_id': artist.id,
        'artist_name': artist.name,
        'artist_image_link': artist.image_link,
        'start_time': show.start_time
      }
      shows_object.append(show_object)

  return render_template('pages/shows.html', shows=shows_object)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  error = False
  
  if request.content_type == 'application/x-www-form-urlencoded':
    try:
      start_time = datetime.strptime(request.form['start_time'], '%Y-%m-%d %H:%M:%S').replace(tzinfo=pytz.utc).isoformat()
      show = Show(start_time=start_time)
      show.venue_id = request.form['venue_id']
      show.artist_id = request.form['artist_id']
      db.session.add(show)
      db.session.commit()
    except:
      error = True
      db.session.rollback()
      app.logger.debug(request.form)
      print(sys.exc_info())
    finally:
      db.session.close()
    if not error:
      flash('Show for artist ' + request.form['artist_id'] + ' at venue ' + request.form['venue_id'] + ' was successfully listed!')
    else:
      flash('An error occurred. Show for artist ' + request.form['artist_id'] + ' at venue ' + request.form['venue_id'] + ' could not be listed.')
    return render_template('pages/home.html')
  elif (request.content_type == 'application/json'):
    try:
      show = Show(start_time=request.get_json()['start_time'])
      show.venue_id = request.get_json()['venue_id']
      show.artist_id = request.get_json()['artist_id']
      db.session.add(show)
      db.session.commit()
    except:
      error = True
      db.session.rollback()
      app.logger.debug(request.form)
      print(sys.exc_info())
    finally:
      db.session.close()
    return render_template('pages/home.html')
  # on successful db insert, flash success
  flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
