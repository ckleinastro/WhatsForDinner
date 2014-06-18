from flask import render_template, request
from app import app, host, port, user, passwd, db
from app.helpers.database import con_db
from app.recommend_dinner import recommend_dinner, historical_dinner_match
import pymysql


from flask import flash, redirect

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
    
    nutrition_data = [0, 0, 0, 0, 0, 0]
    goal_nutrition_data = [2000, 245, 65, 98, 74, 38]
    
    f = request.form
    
    for key in f.keys():
        for value in f.getlist(key):
            print key,":",value
    
    
    try:
        nutrition_data[0] = float(f["consumed_calories"])
    except:
        nutrition_data[0] = 0
    try:
        nutrition_data[1] = float(f["consumed_carbohydrates"])
    except:
        nutrition_data[1] = 0
    try:
        nutrition_data[2] = float(f["consumed_fat"])
    except:
        nutrition_data[2] = 0
    try:
        nutrition_data[3] = float(f["consumed_protein"])
    except:
        nutrition_data[3] = 0
    try:
        nutrition_data[4] = float(f["consumed_sugar"])
    except:
        nutrition_data[4] = 0
    try:
        nutrition_data[5] = float(f["consumed_fiber"])
    except:
        nutrition_data[5] = 0
    
    try:
        goal_nutrition_data[0] = float(f["goal_calories"])
    except:
        goal_nutrition_data[0] = 2000
    try:
        goal_nutrition_data[1] = float(f["goal_carbohydrates"])
    except:
        goal_nutrition_data[1] = 245
    try:
        goal_nutrition_data[2] = float(f["goal_fat"])
    except:
        goal_nutrition_data[2] = 65
    try:
        goal_nutrition_data[3] = float(f["goal_protein"])
    except:
        goal_nutrition_data[3] = 98
    try:
        goal_nutrition_data[4] = float(f["goal_sugar"])
    except:
        goal_nutrition_data[4] = 74
    try:
        goal_nutrition_data[5] = float(f["goal_fiber"])
    except:
        goal_nutrition_data[5] = 38
    
    create_dinners_flag = True
    if nutrition_data[0] == 0:
        create_dinners_flag = False
        error_text = ["Consumed calories required.", "Unless entered, other values will auto-fill based on consumed calories."]
        return render_template('index.html', create_dinners_flag=create_dinners_flag,
            nutrition_data=nutrition_data, 
            goal_nutrition_data=goal_nutrition_data,
            error_text=error_text)
    
    # auto-fill carbohydrate
    if nutrition_data[1] == 0:
        nutrition_data[1] = nutrition_data[0]*0.1225
        
    # auto-fill fat
    if nutrition_data[2] == 0:
        nutrition_data[2] = nutrition_data[0]*0.0325
    
    # auto-fill protein
    if nutrition_data[3] == 0:
        nutrition_data[3] = nutrition_data[0]*0.049
        
    # auto-fill sugar
    if nutrition_data[4] == 0:
        nutrition_data[4] = nutrition_data[0]*0.037

    # auto-fill fiber
    if nutrition_data[5] == 0:
        nutrition_data[5] = nutrition_data[0]*0.019
    
    random_dinner_flag = False
    data = []
    
    previous_consumed_nutrition = array(nutrition_data)
    daily_nutrition_goal = array(goal_nutrition_data)
    
    clusters = pickle.load(open("food_clustering_results/many_clusters.p", "rb"))
    
    tagged_clusters = []
    tags = []
    tagged_clusters_file = file("food_clustering_results/clusters.txt", "r")
    for line in tagged_clusters_file:
        tag = line.split("|")[0]
        food_array = array(line.split("|")[1:-1])
        tags.append(tag.rstrip())
        tagged_clusters.append(food_array)
    tagged_clusters_file.close()
    tags = array(tags)
    tagged_clusters = array(tagged_clusters)
    
    # print "Cuisine choice:", f["cuisine_choice"]
    cuisine_choice = f["cuisine_choice"]
    if cuisine_choice == "r":
        clusters = tagged_clusters
    else:
        clusters = tagged_clusters[tags==cuisine_choice]
    
    print len(clusters)
    
    model = gword2vec.Word2Vec.load_word2vec_format('food_clustering_results/dinner_associations.bin', binary=True)
    
    dinner_nutrition_target = daily_nutrition_goal - previous_consumed_nutrition
    if not random_dinner_flag:
        score, dinner = recommend_dinner(dinner_nutrition_target, daily_nutrition_goal, model, clusters, themed=True)
    else:
        score, dinner = recommend_dinner(dinner_nutrition_target, daily_nutrition_goal, model, clusters, themed=False)
    
    score_str = "%.2f" % (score)
    
    for n in range(len(dinner.food_item_list)):
        food_desc = dinner.food_item_list[n].full_desc.replace(", NFS", "").replace("NFS", "")
        food_desc = food_desc.split(", NS")[0]
        food_desc = food_desc.lower()
        food_desc = food_desc[0].upper() + food_desc[1:]
        food_portion_desc = dinner.portion_desc_list[n].split("(")[0]
        data.append([food_desc, food_portion_desc])
    
    dinner_nutrition_data = [   str(round(dinner.tot_calories)),
                                str(round(dinner.tot_carbohydrate)), 
                                str(round(dinner.tot_fat)),
                                str(round(dinner.tot_protein)),
                                str(round(dinner.tot_sugar)),
                                str(round(dinner.tot_fiber))]
    
    
    
    hist_score, hist_dinner_desc_list, hist_dinner_portion_list, hist_dinner_nutrition = historical_dinner_match(dinner_nutrition_target, daily_nutrition_goal)
    
    hist_dinner_nutrition_data = []
    for val in hist_dinner_nutrition:
        hist_dinner_nutrition_data.append(str(round(val)))
    
    hist_score_str = "%.2f" % (hist_score)
    
    hist_data = []
    for n in range(len(hist_dinner_desc_list)):
        food_desc = hist_dinner_desc_list[n]
        food_desc = food_desc.split(", NS")[0]
        food_desc = food_desc.lower()
        food_desc = food_desc[0].upper() + food_desc[1:]
        food_portion_desc = hist_dinner_portion_list[n]
        hist_data.append([food_desc, food_portion_desc])
    
    dinner_accuracy = (array(dinner_nutrition_data, dtype=float) / array(dinner_nutrition_target, dtype=float))
    hist_dinner_accuracy = (array(hist_dinner_nutrition_data, dtype=float) / array(dinner_nutrition_target, dtype=float))
    
    dinner_colors = []
    hist_dinner_colors = []
    dinner_simple_score = 0.0
    hist_dinner_simple_score = 0.0
    for n in range(len(dinner_accuracy)):
        if dinner_accuracy[n] > 0.9 and dinner_accuracy[n] < 1.1:
            dinner_colors.append("green")
            dinner_simple_score += 1.0
        elif dinner_accuracy[n] > 0.75 and dinner_accuracy[n] < 1.25:
            dinner_colors.append("black")
            dinner_simple_score += 0.5
        else:
            dinner_colors.append("red")
        if hist_dinner_accuracy[n] > 0.9 and hist_dinner_accuracy[n] < 1.1:
            hist_dinner_colors.append("green")
            hist_dinner_simple_score += 1.0
        elif hist_dinner_accuracy[n] > 0.75 and hist_dinner_accuracy[n] < 1.25:
            hist_dinner_colors.append("black")
            hist_dinner_simple_score += 0.5
        else:
            hist_dinner_colors.append("red")
    
    if dinner_simple_score > 5:
        dinner_simple_score=5
    if hist_dinner_simple_score > 5:
        hist_dinner_simple_score=5
    
    return render_template('index.html', create_dinners_flag=create_dinners_flag,
        nutrition_data=nutrition_data, 
        goal_nutrition_data=goal_nutrition_data,
        cuisine_choice=cuisine_choice,
        dinner_nutrition_target=dinner_nutrition_target,
        score=score_str, 
        data=data, 
        dinner_nutrition_data=dinner_nutrition_data, 
        dinner_colors=dinner_colors,
        hist_score_str=hist_score_str, 
        hist_data=hist_data, 
        hist_dinner_nutrition_data=hist_dinner_nutrition_data, 
        hist_dinner_colors=hist_dinner_colors, 
        dinner_simple_score=dinner_simple_score, 
        hist_dinner_simple_score=hist_dinner_simple_score)



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

