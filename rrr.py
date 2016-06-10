"""The app.

Because this is super primitive it just uses a shelf as a database that
will be put wherever the app is executed

The manage endpoint also only requires a username for basic auth and no
password

To set the username, run:

> flask setuser

in the terminal.
"""

import shelve

from flask import Flask, render_template, request, abort, jsonify
from flask_basicauth import BasicAuth
import click

app = Flask(__name__)


# Storage

storage_name = "storage"
"""The storage file for status and mangemant password."""


# Simple Security

with shelve.open(storage_name) as storage:
    try:
        username = storage['username']
    except KeyError:
        app.logger.warning("You should set a username for basic auth!\n"
                           "Run 'flask setuser' in your terminal.")
        username = ''

app.config['BASIC_AUTH_USERNAME'] = username
app.config['BASIC_AUTH_PASSWORD'] = ''
auth = BasicAuth(app)


# Simple CLI to set username

@app.cli.command()
@click.option('--username', prompt=True, help="set username for basic auth")
def setuser(username):
    """Set username for basic auth."""
    with shelve.open(storage_name) as storage:
        storage['username'] = username


# Routes

@app.route('/')
def open_or_not(managemode=False):
    """Main view, displays whether rrr is open."""
    with shelve.open(storage_name) as storage:
            is_open = storage.get('is_open', False)

    return render_template("openornot.html",
                           is_open=is_open, managemode=managemode)


@app.route('/status')
def get_status():
    """Return the status in json."""
    with shelve.open(storage_name) as storage:
        status = "open" if storage.get('is_open', False) else "closed"
    
    return jsonify(status=status)


@app.route('/manage', methods=['GET', 'POST'])
@auth.required
def manage():
    """Show the management menu."""
    if (request.method == 'POST') and ('new_status' in request.form):
        # Get new status
        data = request.form['new_status']

        print(data)

        # Check if valid
        if data not in ['open', 'closed']:
            abort(422, "Only 'open' and 'closed' are allowed values "
                  "for 'new_status'")

        # Store
        with shelve.open(storage_name) as storage:
            storage['is_open'] = (data == 'open')  # True/False

    return open_or_not(managemode=True)
