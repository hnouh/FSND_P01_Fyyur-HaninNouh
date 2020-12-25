#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from sqlalchemy.orm import aliased
import datetime


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), primary_key=True)
    start_time = db.Column(db.DateTime)
    venue = db.relationship("Venue",back_populates="artists")
    artist = db.relationship("Artist",back_populates="venues")

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120)) 
    venues = db.relationship('Show', back_populates="artist")

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String(120)) 
    artists = db.relationship('Show', back_populates="venue")
    # TODO: implement any missing fields, as a database migration using Flask-Migrate


# db.create_all()

# TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
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
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.

    # data1=Venue.query.distinct(Venue.city).all()
    # data2=Venue.query.distinct(Venue.state).all()

    # alias1ForVenue = aliased(Venue)
    # alias2ForVenue = aliased(Venue)
    # datanew = alias1ForVenue.query.with_entities(Venue.id,Venue.name,Venue.state,Venue.city).join(alias2ForVenue, alias1ForVenue.id == alias2ForVenue.id)
    # data =alias1ForVenue.query.join(alias2ForVenue, alias1ForVenue.city == alias2ForVenue.city & alias1ForVenue.id != alias2ForVenue.id).distinct(Venue.state).all()
    # data = alias1ForVenue.query.join(alias2ForVenue, alias1ForVenue.city == alias2ForVenue.city & alias1ForVenue.id != alias2ForVenue.id)    
    
    data=Venue.query.group_by(Venue.id).all()

    return render_template('pages/venues.html',len = len(list(data)), areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    whichVenue=request.form.get('search_term')
    smallwhichVenue=whichVenue.lower()
    response=Venue.query.filter(Venue.name.like(smallwhichVenue)).all()
    # response = {
    #     "count": 1,
    #     "data": [{
    #         "id": 2,
    #         "name": "The Dueling Pianos Bar",
    #         "num_upcoming_shows": 0,
    #     }]
    # }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    data = Venue.query.filter_by(id=venue_id).one()
    dataNumUp=Show.query.filter_by(venue_id=venue_id).join(Venue, Show.venue_id == Venue.id).count()
    dataUp=Show.query.with_entities(Show.start_time,Artist.image_link,Artist.id,Artist.name,Venue.id,Venue.name,Venue.image_link).filter_by(venue_id=venue_id).join(Artist, Show.artist_id == Artist.id).join(Venue, Show.venue_id == Venue.id)
    print(dataUp)

    return render_template('pages/show_venue.html',len = len(list(dataUp)), venue=data, dataShownNum=dataNumUp, dataShow=dataUp)

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
    form = VenueForm()
    if request.method == 'POST':
        newVenue = Venue(name=form.name.data, city=form.city.data, state=form.state.data, address=form.address.data,
                         phone=form.phone.data, image_link=form.image_link.data, genres=form.genres.data, facebook_link=form.facebook_link.data)
        db.session.add(newVenue)
        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
        return redirect(url_for('venues'))
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    else:
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be listed.')
        return render_template('forms/new_venue.html', form=form)
        # return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    VenueToDelete = Venue.query.filter_by(id=venue_id).one()
    db.session.delete(VenueToDelete)
    db.session.commit()
    return redirect(url_for('venues'))

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    data = Artist.query.all()
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    whichArtist=request.form.get('search_term')
    smallwhichArtist=whichArtist.lower()
    response=Artist.query.filter(Artist.name.like(smallwhichArtist)).all()
    
    # query = Artist.query.all()
    # query2 = search(query, whichArtist)
    # response= query2.data.name
 
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artists table, using artist_id
    data = Artist.query.filter_by(id=artist_id).one()
    # data2 = Artist.query.filter_by(id=artist_id).join(Show, Artist.id == Show.artist_id).join(Venue, Venue.id==Show.venue_id)
    
    now = datetime.datetime.now()
    
    dataNumUp=Show.query.filter_by(artist_id=artist_id).join(Artist, Show.artist_id == Artist.id).count()
    dataUp=Show.query.with_entities(Show.start_time,Artist.image_link,Artist.id,Artist.name,Venue.id,Venue.name,Venue.image_link).filter_by(artist_id=artist_id).join(Artist, Show.artist_id == Artist.id).join(Venue, Show.venue_id == Venue.id)
    print(dataUp)
    
    # for x in len(list(dataUp)):
    #     print(dataUp[x][0])
        # if now < dataUp[x][0]

   

    return render_template('pages/show_artist.html',len = len(list(dataUp)), artist=data, dataShownNum=dataNumUp, dataShow=dataUp)
    # return render_template('pages/show_artist.html',len = len(list(dataUp)), artist=data ,artistData=data2, dataShownNum=dataNumUp, dataShow=dataUp)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.filter_by(id=artist_id).one()
    # TODO: populate form with fields from artist with ID <artist_id>
    if request.method == 'GET':
        form.name.data = artist.name
        form.city.data = artist.city
        form.state.data = artist.state
        form.phone.data = artist.phone
        form.image_link.data = artist.image_link
        form.genres.data = artist.genres
        form.facebook_link.data = artist.facebook_link
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    form = ArtistForm()
    artist = Artist.query.filter_by(id=artist_id).one()
    if request.method == 'POST':
        newName = request.form.get("name")
        artist.name = newName
        newCity = request.form.get("city")
        artist.city = newCity
        newState = request.form.get("state")
        artist.state = newState
        newPhone = request.form.get("phone")
        artist.phone = newPhone
        newImage_link = request.form.get("image_link")
        artist.image_link = newImage_link
        newGenres = request.form.get("genres")
        artist.genres = newGenres
        newFacebook_link = request.form.get("facebook_link")
        artist.facebook_link = newFacebook_link
        db.session.commit()
        return redirect(url_for('show_artist', artist_id=artist_id))
    else:
        return render_template('forms/edit_artist.html', artist=artist)


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.filter_by(id=venue_id).one()
    if request.method == 'GET':
        form.name.data = venue.name
        form.city.data = venue.city
        form.state.data = venue.state
        form.address.data = venue.address
        form.phone.data = venue.phone
        form.image_link.data = venue.image_link
        form.genres.data = venue.genres
        form.facebook_link.data = venue.facebook_link
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    form = VenueForm()
    venue = Venue.query.filter_by(id=venue_id).one()
    if request.method == 'POST':
        newName = request.form.get("name")
        venue.name = newName
        newCity = request.form.get("city")
        venue.city = newCity
        newState = request.form.get("state")
        venue.state = newState
        newAddress = request.form.get("address")
        venue.address = newAddress
        newPhone = request.form.get("phone")
        venue.phone = newPhone
        newImage_link = request.form.get("image_link")
        venue.image_link = newImage_link
        newGenres = request.form.get("genres")
        venue.genres = newGenres
        newFacebook_link = request.form.get("facebook_link")
        venue.facebook_link = newFacebook_link
        db.session.commit()
        return redirect(url_for('show_venue', venue_id=venue_id))
    else:
        return render_template('forms/edit_venue.html', venue=venue)


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
    form = ArtistForm()
    if request.method == 'POST':
        newArtist = Artist(name=form.name.data, city=form.city.data, state=form.state.data, phone=form.phone.data,
                           image_link=form.image_link.data, genres=form.genres.data, facebook_link=form.facebook_link.data)
        db.session.add(newArtist)
        db.session.commit()
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
        return redirect(url_for('artists'))
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    else:
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be listed.')
        return render_template('forms/new_artist.html', form=form)
        # return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------


@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    # data1 = Artist.query.join(Show, Artist.id == Show.artist_id, isouter=True )
    # data2 = Venue.query.join(Show, Venue.id == Show.venue_id , isouter=True)
    data = Artist.query.with_entities(Show.start_time,Artist.image_link,Artist.id,Artist.name,Venue.id,Venue.name).join(Show, Artist.id == Show.artist_id).outerjoin(Venue, Venue.id == Show.venue_id)

    return render_template('pages/shows.html',len = len(list(data)), shows=data)


@ app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form=ShowForm()
    return render_template('forms/new_show.html', form=form)


@ app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    form=ShowForm()
    if request.method == 'POST':
        newShow=Show(artist_id=form.artist_id.data,
                       venue_id=form.venue_id.data, start_time=form.start_time.data)
        db.session.add(newShow)
        db.session.commit()
        # on successful db insert, flash success
        flash('Show was successfully listed!')
        return redirect(url_for('shows'))
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    else:
        flash('An error occurred. Show could not be listed.')
        return render_template('forms/new_show.html', form=form)
        # return render_template('pages/home.html')


@ app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@ app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler=FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
