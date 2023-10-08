import secrets

import sqlalchemy
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash

from forms import RegisterForm, LoginForm
from models import db, User

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex()
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db.init_app(app)
csrf = CSRFProtect(app)
app.config.from_object(__name__)


@app.cli.command('init-db')
def init_db():
    """
    Initializes the database.
    This function creates all the necessary tables in the database using the `db.create_all()` method. If the operation
    is successful, it prints '[+] OK' to indicate that the tables were created.
    If an exception occurs during the creation of the tables, it prints '[-] Error'.
    Parameters: None
    Returns: None
    """
    try:
        db.create_all()
        print('[+] OK')
    except Exception as e:
        print(f'[-] Error\n{e}')


@app.route('/')
def index():
    """
    Renders the index.html template with the given context.
    Returns: The rendered HTML page.
    """
    context = {
        'title': 'Index Page',
    }
    return render_template('index.html', context=context)


@app.route('/register/', methods=['GET', 'POST'])
def register():
    """
    Register a new user.

    This function handles the registration process for new users. It accepts both GET and POST requests.
    If the request method is POST, it validates the user registration form and adds the new user to the database.
    If the registration is successful, a success message is flashed and the user is redirected to the index page.
    If the request method is GET, it renders the registration form.

    Parameters:
    - None

    Returns:
    - If the registration is successful, it redirects the user to the index page.
    - If the registration fails or the request method is GET, it renders the registration form.

    """
    form = RegisterForm()
    if form.validate_on_submit():
        password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password_hash=password)
        try:
            db.session.add(user)
            db.session.commit()
        except sqlalchemy.exc.IntegrityError as error:
            flash(f'Error: User already exists', 'error')
            print(error)
            return render_template('register.html', form=form)
        flash('You have successfully registered!', 'success')
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    """
    Route for handling the login page.
    This function is responsible for rendering the login page and handling the login form submission.
    It checks if the request method is POST, validates the form data, and attempts to log in the user.
    If the login is successful, the user is redirected to the index page. If the login fails,
    an error message is flashed and the login page is rendered again with the login form.
    Returns:
        The rendered login template with the login form.
    """
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and check_password_hash(user.password_hash, form.password.data):
                session['logged_user'] = True
                flash('You have successfully logged in!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid username or password', 'error')
    return render_template('login.html', form=form)


@app.route('/logout/')
def logout():
    """
    Logs out the current user.
    Returns: The user is redirected to the login page.
    """
    session.pop('logged_user', None)
    flash('You have successfully logged out!', 'success')
    return redirect(url_for('login'))


@app.route('/about/')
def about():
    context = {
        'title': 'About Page'
    }
    return render_template('about.html', context=context)


@app.errorhandler(404)
def errorhandler(e):
    """
    Handle a 404 error.
    Args: e: The error object.
    Returns: A rendered template and the HTTP status code 404.
    """
    context = {
        'title': 'Страница не найдена',
        'url': request.base_url,
    }
    return render_template('page404.html', context=context), 404


if __name__ == '__main__':
    app.run(debug=True)
