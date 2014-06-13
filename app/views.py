from flask import render_template, request
from app import app, host, port, user, passwd, db
from app.helpers.database import con_db
from app.recommend_dinner import recommend_dinner

from flask import flash, redirect

from forms import NutritionForm

import pickle
import pymysql
from gensim.models import word2vec as gword2vec
from numpy import array

# To create a database connection, add the following
# within your view functions:
# con = con_db(host, port, user, passwd, db)


# ROUTING/VIEW FUNCTIONS
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods = ['GET', 'POST'])
def index():
    # Renders index.html.
    form = NutritionForm()
    data = []
    nutrition_data = form.user_previous_consumed_nutrition.data
    random_dinner_flag = form.random_dinner_flag.data
    error_text = ""
    if nutrition_data:
        if len(nutrition_data.split(",")) == 6:
            previous_consumed_nutrition = array(map(float, nutrition_data.split(",")))
            clusters = pickle.load(open("food_clustering_results/many_clusters.p", "rb"))
            model = gword2vec.Word2Vec.load_word2vec_format('food_clustering_results/dinner_associations.bin', binary=True)
            daily_nutrition_goal = array([2000, 245, 65, 98, 74, 38])
            dinner_nutrition_target = daily_nutrition_goal - previous_consumed_nutrition
            if not random_dinner_flag:
                score, dinner = recommend_dinner(dinner_nutrition_target, daily_nutrition_goal, model, clusters, themed=True)
            else:
                score, dinner = recommend_dinner(dinner_nutrition_target, daily_nutrition_goal, model, clusters, themed=False)
            data.append("Generated dinner has score %.2f:" % score)
            for n in range(len(dinner.food_item_list)):
                if len(dinner.food_item_list[n].full_desc) < 50:
                    print_string = "%s - %s" % (dinner.food_item_list[n].full_desc, dinner.portion_desc_list[n])
                else:
                    print_string =  "%s ... - %s" % (dinner.food_item_list[n].full_desc[:50], dinner.portion_desc_list[n])
                data.append(print_string)
            data.append("This nutritious dinner will supplement your daily consumption:")
            
            dinner_nutrition_data = [   str(round(dinner.tot_calories)),
                                        str(round(dinner.tot_carbohydrate)), 
                                        str(round(dinner.tot_fat)),
                                        str(round(dinner.tot_protein)),
                                        str(round(dinner.tot_sugar)),
                                        str(round(dinner.tot_fiber))]
            
        else:
            error_text = "Please submit 6 comma-separated numerical values for your previously-consumed nutrition."
            return render_template('index.html', form=form, error_text=error_text)

        return render_template('index.html', form=form, data=data, error_text=error_text, dinner_nutrition_data=dinner_nutrition_data)
    

    
    return render_template('index.html', form=form)


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

