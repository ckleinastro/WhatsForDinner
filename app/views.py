from flask import render_template
from app import app, host, port, user, passwd, db
from app.helpers.database import con_db


# To create a database connection, add the following
# within your view functions:
# con = con_db(host, port, user, passwd, db)


# ROUTING/VIEW FUNCTIONS
@app.route('/')
@app.route('/index')
def index():
    # Renders index.html.
    return render_template('index.html')

@app.route('/home')
def home():
    # Renders home.html.
    return render_template('home.html')

@app.route('/slides')
def about():
    # Renders slides.html.
    return render_template('slides.html')

@app.route('/author')
def contact():
    # Renders author.html.
    return render_template('author.html')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

from app.helpers.database import con_db, query_db
from app.helpers.filters import format_currency
import jinja2


# ROUTING/VIEW FUNCTIONS
@app.route('/', methods=['GET'])
def index():
    # Create database connection
    con = con_db(host, port, user, passwd, db)

    # Add custom filter to jinja2 env
    jinja2.filters.FILTERS['format_currency'] = format_currency

    var_dict = {
        "country": request.args.get("country"),
        "edu_index": request.args.get("edu_index", '0'),
        "median_age": request.args.get("median_age", '0'),
        "gdp": request.args.get("gdp", '0'),
        "order_by": request.args.get("order_by", "edu_index"),
        "sort": request.args.get("sort", "DESC")
    }

    # Query the database
    data = query_db(con, var_dict)

    # Add data to dictionary
    var_dict["data"] = data

    return render_template('world.html', settings=var_dict)