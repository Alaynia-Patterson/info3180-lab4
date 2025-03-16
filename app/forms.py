from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired
from wtforms import FileField
from flask_wtf.file import FileRequired, FileAllowed

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])



class UploadForm(FlaskForm):
    file = FileField('File', validators=[
        FileRequired(),  # Ensure file is uploaded
        FileAllowed(['jpg', 'png'], 'Images only!')  # Only allow jpg and png files
    ])