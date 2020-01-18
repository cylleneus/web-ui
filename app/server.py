import flask

from .settings import *

app = flask.Flask('app')

from . import views


def run():
    """Run the Flask server."""

    app.run(
        host=HOST_ADDR,
        port=HOST_PORT,
        debug=DEBUG,
        threaded=not PROCESSES > 1,
        processes=PROCESSES
    )


def main():
    import webbrowser

    run()
    webbrowser.open_new('http://127.0.0.1:5000/')
