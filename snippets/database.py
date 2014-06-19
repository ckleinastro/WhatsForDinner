import pymysql
import sys
import simplejson as json


# Returns MySQL database connection
def con_db(host, port, user, passwd, db):
    try:
        con = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db)

    except pymysql.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])
        sys.exit(1)

    return con


def query_db(con, dict):
    data_array = []

    # Request args
    edu_index = dict["edu_index"]
    median_age = dict["median_age"]
    gdp = dict["gdp"]
    order_by = dict["order_by"]
    sort = dict["sort"]

    # Query database
    cur = con.cursor()
    cur.execute(
        """
        SELECT id, country, median_age, gdp, edu_index
        FROM world_index
        WHERE edu_index >= {0}
        AND median_age >= {1}
        AND gdp >= {2}
        ORDER BY {3} {4}
        """.format(edu_index, median_age, gdp, order_by, sort)
    )

    data = cur.fetchall()
    for country in data:
        index = {}

        index["id"] = country[0]
        index["country"] = country[1]
        index["median_age"] = float(json.dumps(country[2]))
        index["gdp"] = country[3]
        index["edu_index"] = float(json.dumps(country[4]))

        data_array.append(index)

    cur.close()
    con.close()
    return data_array