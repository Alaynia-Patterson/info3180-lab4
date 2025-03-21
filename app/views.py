import os
from flask import send_from_directory
from app import app, db, login_manager
from flask import render_template, request, redirect, url_for, flash, session, abort
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from app.models import UserProfile
from app.forms import LoginForm, UploadForm
# Import check_password_hash
from werkzeug.security import check_password_hash  



###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html', name="Mary Jane")


@app.route('/upload', methods=['POST', 'GET'])
@login_required  # Ensure that only logged-in users can access this route
def upload():
    # Instantiate your form class
    form = UploadForm()


    # Validate file upload on submit
    if form.validate_on_submit():
        # Get file data and save to your uploads folder
        file = form.file.data
         # Ensure a file was uploaded
        if file:
            # Save the file to the upload folder (use secure_filename to avoid issues with file names)
            filename = secure_filename(file.filename)
            upload_folder = os.path.join(app.root_path, 'uploads')  
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            file.save(os.path.join(upload_folder, filename))



        flash('File Saved', 'success')
        return redirect(url_for('home')) # Update this to redirect the user to a route that displays all uploaded image files

    return render_template('upload.html', form=form)


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()

    # change this to actually validate the entire form submission
    # and not just one field
    if form.validate_on_submit():  # Validate the entire form submission
        # Get the username and password values from the form.
        username = form.username.data
        password = form.password.data  # Get password from form
        
        # Using your model, query database for a user based on the username
        # and password submitted. Remember you need to compare the password hash.
        # You will need to import the appropriate function to do so.
        # Then store the result of that query to a `user` variable so it can be
        # passed to the login_user() method below.

        # Query the database to find the user by username
        user = UserProfile.query.filter_by(username=username).first()

        # Check if user exists and password matches
        if user and check_password_hash(user.password, password):  # Compare hashed password

            # Gets user id, load into session
            login_user(user)

        

            # Remember to flash a message to the user
            # Flash a success message
            flash('You have successfully logged in!', 'success')
            return redirect(url_for("upload"))  # The user should be redirected to the upload form instead
        else:
            # If login fails, flash an error message
            flash('Invalid username or password', 'danger')
    return render_template("login.html", form=form)

# user_loader callback. This callback is used to reload the user object from
# the user ID stored in the session
@login_manager.user_loader
def load_user(id):
    return db.session.execute(db.select(UserProfile).filter_by(id=id)).scalar()

###
# The functions below should be applicable to all Flask apps.
###

# Flash errors from the form if validation fails
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
), 'danger')

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404




def get_uploaded_images():
    """Retrieve a list of uploaded image filenames from the uploads folder."""
    upload_folder = os.path.join(app.root_path, 'uploads')  
    image_files = []

    # Ensure the directory exists
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    # Iterate through the uploads folder and get file names
    for file in os.listdir(upload_folder):
        if file.lower().endswith(('.png', '.jpg', '.jpeg')):  # Ensure it's an image
            image_files.append(file)

    return image_files  # Return the list of image filenames


@app.route('/uploads/<filename>')
def get_image(filename):
    """Serve an uploaded image by filename."""
    return send_from_directory(os.path.join(app.root_path, 'uploads'), filename)



@app.route('/files')
@login_required
def files():
    """Display a list of uploaded images."""
    image_list = get_uploaded_images()  # Get uploaded images
    return render_template('files.html', images=image_list)  # Pass images to template


@app.route('/logout')
@login_required
def logout():
    """Logs out the user and redirects to home."""
    logout_user()
    flash('You have been logged out.', 'info')  # Flash logout message
    return redirect(url_for('home'))  # Redirect to home page