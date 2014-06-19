...
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
...