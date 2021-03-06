from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, TextAreaField, SubmitField, PasswordField, BooleanField, SelectField, SelectMultipleField
from wtforms.fields.html5 import DateTimeField, DateField, DateTimeLocalField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, length, URL, Optional
from app.models import Artist, Location, Porch, Porchfest
from bson.objectid import ObjectId
from datetime import datetime

BooleanField.false_values = {False, 'false', ''}


class NewArtistForm(FlaskForm):
    bandName = StringField('Band Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_check = PasswordField('Reenter Password', validators=[DataRequired(), EqualTo('password')])
    genre = StringField('Genre', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    state = StringField('State', validators=[length(min=2, max=2, message="Length should be two letters!")])
    zip = StringField('Zip code', validators=[length(min=5, max=5, message="Should be 5 numbers long!")])
    image = StringField('Profile Image url', validators=[Optional()])
    spotify = StringField('Spotify url', validators=[Optional()])  # removed url check because was never accepting
    youtube = StringField('Youtube url', validators=[Optional()])  # removed url check because was never accepting
    facebook = StringField('Facebook url', validators=[Optional()])  # removed url check because was never accepting
    submit = SubmitField('Register')

    def validate_zip(self, zip):
        for c in zip.data:
            if c.isalpha():
                raise ValidationError('Zip code must consist of only integers')

    def validate_spotify(self, spotify):
        # need to fix these to allow there to be no link entered
        if "spotify" not in spotify.data and spotify.data is not None:
            raise ValidationError('Please enter a url for Spotify')

    def validate_youtube(self, youtube):
        if "youtube" not in youtube.data and youtube.data is not None:
            raise ValidationError('Please enter a url for Youtube')

    def validate_facebook(self, facebook):
        if "facebook" not in facebook.data and facebook.data is not None:
            raise ValidationError('Please enter a url for Facebook')

    def validate_email(self, email):
        artist = Artist.objects(email=email.data).first()
        if artist is not None:
            raise ValidationError('Email already being used!')


class EditArtistForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    genre = StringField('Genre', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_email(self, email):
        artist = Artist.objects(email=email.data).first()
        if artist is not None and current_user.email != artist.email:
            raise ValidationError('Email already being used!')


class PorchForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    porchfest_id = SelectField('Choose a Porchfest', validators=[DataRequired()], coerce=ObjectId, id='porchfest')
    # maybe validate by checking address exists with map api
    address = StringField('Address', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    state = StringField('State Abbreviation', validators=[length(min=2, max=2, message="Length should be two letters!")])
    zip = StringField('Zip code', validators=[length(min=5, max=5, message="Should be 5 numbers long!")])
    time_slots = SelectMultipleField('Times Available', validators=[DataRequired()], id='timeslot')
    submit = SubmitField('Submit')

    def validate_email(self, email):
        if Porch.objects(email=self.email.data).first() is not None:
            raise ValidationError('Email is already in use for a porch owner!')

    def validate_porchfest_id(self, porchfest_id):
        porchfest = Porchfest.objects(id=porchfest_id.data).first()
        if porchfest is None:
            raise ValidationError('The selected porchfest does not exist!')

    def validate_address(self, address):
        porch = Porch.objects(address=address.data).first()
        if porch is not None:
            raise ValidationError("Porch is already in the database!")

    def validate_zip(self, zip):
        porchfest = Porchfest.objects(id=self.porchfest_id.data).first()
        if porchfest.location.zip_code != zip.data:
            raise ValidationError('Does not match the zip code of the selected Porchfest!')
        for c in zip.data:
            if c.isalpha():
                raise ValidationError('Zip code must consist of only integers')

    def validate_city(self, city):
        fest_location = Location.objects(zip_code=self.zip.data).first()
        if fest_location is None or fest_location.city != city.data:
            raise ValidationError('Does not match the city of the selected Porchfest!')

    def validate_state(self, state):
        fest_location = Location.objects(zip_code=self.zip.data).first()
        if fest_location is None or fest_location.state != state.data:
            raise ValidationError('Does not match the state of the selected Porchfest!')


class ArtistPorchfestSignUpForm(FlaskForm):
    porchfest = SelectField('Choose a porchfest', validators=[DataRequired()], id='porchfest')
    time_slot = SelectField('When Will your Show Start', validators=[DataRequired()], id='timeslot')
    porch = BooleanField('I already have a porch', id='porch')
    porch_selector = SelectField('Choose a Porch', validators=[], id='porchselect')
    # can check that location matches with location of selected porchfest
    # maybe validate by checking address exists with map api
    # maybe keep this hidden unless the checkbox is clicked
    porch_owner = StringField('Name of porch owner (if you have a porch)', validators=[], id='porch_owner')
    porch_email = StringField('Email of porch owner (if you have a porch)', validators=[], id='porch_email')
    address = StringField('Address (if you have a porch)', validators=[], id='address')
    city = StringField('City (if you have a porch)', validators=[], id='city')
    state = StringField('State (if you have a porch)', validators=[length(min=0, max=2, message="Length should be two letters!")], id='state')
    zip = StringField('Zip code (if you have a porch)', validators=[length(min=0, max=5, message="Should be 5 numbers long!")], id='zip')
    submit = SubmitField('Submit')

    def validate_email(self, email):
        if self.porch.data:
            if email.data == '':
                raise ValidationError('If you have a porch you must enter your email!')
            if not Email(email):
                raise ValidationError('Invalid Email Address')
        else:
            if email.data is not '':
                raise ValidationError('Leave email blank if you do not have a porch yet!')

    def validate_zip(self, zip):
        if self.porch.data:
            if zip.data == "":
                raise ValidationError('If you have a porch you must enter the zip code!')
            fest_location = Porchfest.objects(id=self.porchfest.data).first().location
            if fest_location.zip_code != zip.data:
                raise ValidationError('Does not match the zip code of the selected Porchfest!')
            for c in zip.data:
                if c.isalpha():
                    raise ValidationError('Zip code must consist of only integers')
        else:
            if zip.data != "":
                raise ValidationError('Leave zip code blank if you do not have a porch yet!')

    def validate_city(self, city):
        if self.porch.data:
            if city.data == "":
                raise ValidationError('If you have a porch you must enter the city!')
            fest_location = Porchfest.objects(id=self.porchfest.data).first().location
            if fest_location.city != city.data:
                raise ValidationError('Does not match the city of the selected Porchfest!')
        else:
            if city.data != "":
                raise ValidationError('Leave city blank if you do not have a porch yet!')

    def validate_state(self, state):
        if self.porch.data:
            if state.data == "":
                raise ValidationError('If you have a porch you must enter the state!')
            fest_location = Porchfest.objects(id=self.porchfest.data).first().location
            if fest_location.state != state.data:
                raise ValidationError('Does not match the state of the selected Porchfest!')
        else:
            if state.data != "":
                raise ValidationError('Leave state blank if you do not have a porch yet!')

    def validate_address(self, address):
        # porch already in db and not available at those times
        if self.porch.data:
            if address.data == "":
                raise ValidationError('If you have a porch you must enter the address!')
        else:
            if address.data != "":
                raise ValidationError('Leave address blank if you do not have a porch yet!')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')


class FindAPorchfestForm(FlaskForm):
    porchfest = SelectField('Choose a Porchfest', validators=[DataRequired()], id='select_porchfest')
