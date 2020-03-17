#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import babel
import sys
import logging
import pytz
import dateutil.parser
from datetime import datetime
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import distinct
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from forms import *
from flask_migrate import Migrate

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

@app.before_request
def log_request_info():
    app.logger.debug('Headers: %s', request.headers)
    app.logger.debug('Body: %s', request.get_data())

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
    image_link = db.Column(db.String(500), nullable=False, server_default='https://via.placeholder.com/300')
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
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False, server_default='https://via.placeholder.com/300')
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
  venue_object = {
    'id': venue.id,
    'name': venue.name,
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
    'upcoming_shows_count': 0
  }
  if venue.shows is not None:
    for show in venue.shows:
        artist = Artist.query.filter(Artist.id == show.artist_id).first()
        show_details = {
          'artist_id': artist.id,
          'artist_name':  artist.name,
          'artist_image_link':  artist.image_link,
          'start_time':  show.start_time
        }
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
  error = False
  genres = []
  try:
    venue = Venue(name=request.form['name'])
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.genres = ",".join(request.form.getlist('genres'))
    venue.phone = request.form['phone']
    if request.form['image_link'] : venue.image_link = request.form['image_link']
    if request.form['facebook_link'] : venue.facebook_link = request.form['facebook_link']
    if request.form['website'] : venue.website = request.form['website']
    if request.form.getlist('seeking_talent') : venue.seeking_talent = True 
    if request.form['seeking_description'] : venue.seeking_description = request.form['seeking_description']
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

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  error = False
  try:
    venue = Venue.query.filter(Venue.id == venue_id).first()
    db.session.delete(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    venue_response = {"result": f"Venue ID: #{venue_id} has been deleted!"}
  return jsonify(venue_response)

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
  artist_object = {
    'name': artist.name,
    'id': artist.id,
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
    'upcoming_shows_count': 0
  }
  if artist.shows is not None:
    for show in artist.shows:
      venue = Venue.query.filter(Venue.id == show.venue_id).first()
      show_details = {
        'venue_id': venue.id,
        'venue_name':  venue.name,
        'venue_image_link':  venue.image_link,
        'start_time':  show.start_time
      }
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
  artist = Artist.query.filter(Artist.id == artist_id).first()
  artist_object = {
    'id': artist.id,
    'name': artist.name,
    'genres': artist.genres.split(','),
    'city': artist.city,
    'state': artist.state,
    'phone': artist.phone,
    'website': artist.website,
    'facebook_link': artist.facebook_link,
    'image_link': artist.image_link,
    'seeking_venue': artist.seeking_venue,
    'seeking_description': artist.seeking_description
  }
  return render_template('forms/edit_artist.html', form=form, artist=artist_object)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.filter(Artist.id == artist_id).first()
  error = False
  genres = []
  try:
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.genres = ",".join(request.form.getlist('genres'))
    artist.phone = request.form['phone']
    if request.form['image_link'] : artist.image_link = request.form['image_link']
    if request.form['facebook_link'] : artist.facebook_link = request.form['facebook_link']
    if request.form['website'] : artist.website = request.form['website']
    if request.form.getlist('seeking_venue') : artist.seeking_venue = True 
    if request.form['seeking_description'] : artist.seeking_description = request.form['seeking_description']
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    app.logger.debug(request.form)
    print(sys.exc_info())
  finally:
    db.session.close()
  if not error:
    flash('Artist ' + request.form['name'] + ' was successfully edited!')
  else:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be edited.')
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id): 
  form = VenueForm()
  venue = Venue.query.filter(Venue.id == venue_id).first()
  venue_object = {
    'id': venue.id,
    'name': venue.name,
    'genres': venue.genres.split(','),
    'address': venue.address,
    'city': venue.city,
    'state': venue.state,
    'phone': venue.phone,
    'website': venue.website,
    'facebook_link': venue.facebook_link,
    'image_link': venue.image_link,
    'seeking_talent': venue.seeking_talent,
    'seeking_description': venue.seeking_description
  }
  return render_template('forms/edit_venue.html', form=form, venue=venue_object)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.filter(Venue.id == venue_id).first()
  error = False
  genres = []
  try:
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.genres = ",".join(request.form.getlist('genres'))
    venue.phone = request.form['phone']
    if request.form['image_link'] : venue.image_link = request.form['image_link']
    if request.form['facebook_link'] : venue.facebook_link = request.form['facebook_link']
    if request.form['website'] : venue.website = request.form['website']
    if request.form.getlist('seeking_talent') : venue.seeking_talent = True 
    if request.form['seeking_description'] : venue.seeking_description = request.form['seeking_description']
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    app.logger.debug(request.form)
    print(sys.exc_info())
  finally:
    db.session.close()
  if not error:
    flash('Venue ' + request.form['name'] + ' was successfully edited!')
  else:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be edited.')
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False
  genres = []
  try:
    artist = Artist(name=request.form['name'])
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.genres = ",".join(request.form.getlist('genres'))
    artist.phone = request.form['phone']
    if request.form['image_link'] : artist.image_link = request.form['image_link']
    if request.form['facebook_link'] : artist.facebook_link = request.form['facebook_link']
    if request.form['website'] : artist.website = request.form['website']
    if request.form.getlist('seeking_venue') : artist.seeking_venue = True 
    if request.form['seeking_description'] : artist.seeking_description = request.form['seeking_description']
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

@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  error = False
  try:
    artist = Artist.query.filter(Artist.id == artist_id).first()
    db.session.delete(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  artist_response = {"result": f"Artist ID: #{artist_id} has been deleted!"}
  return jsonify(artist_response)

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
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
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