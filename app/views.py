from flask import render_template, request
from app import app, host, port, user, passwd, db
from app.recommend_dinner import recommend_dinner, historical_dinner_match, generated_dinner_match
from app.top_foods import top_eight_foods

from flask import flash, redirect

from gensim.models import word2vec as gword2vec
from numpy import array, loadtxt, histogram
import pickle





# ROUTING/VIEW FUNCTIONS
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods = ['GET', 'POST'])
def index():
    # Renders index.html.
    nutrition_data = [1400, 170, 45, 70, 50, 25]
    goal_nutrition_data = [2500, 305, 80, 120, 90, 45]
    f = request.form

    try:
        consumed_calories = float(f["consumed_calories"])
        nutrition_data[0] = consumed_calories
    except:
        consumed_calories = "Calories"
    
    
        
        
    create_dinners_flag = True
    if type(consumed_calories) == str:
        create_dinners_flag = False
        error_text = "Consumed calories required."
        return render_template('index.html', create_dinners_flag=create_dinners_flag,
            consumed_calories=consumed_calories, error_text=error_text)
    if consumed_calories < 0:
        create_dinners_flag = False
        error_text = "Consumed calories must be 0 or larger."
        return render_template('index.html', create_dinners_flag=create_dinners_flag,
            consumed_calories=consumed_calories, error_text=error_text)
    
    # auto-fill carbohydrate
    nutrition_data[1] = consumed_calories*0.1225
    # auto-fill fat
    nutrition_data[2] = consumed_calories*0.0325
    # auto-fill protein
    nutrition_data[3] = consumed_calories*0.049
    # auto-fill sugar
    nutrition_data[4] = consumed_calories*0.037
    # auto-fill fiber
    nutrition_data[5] = consumed_calories*0.019
    
    random_dinner_flag = False
    data = []
    
    previous_consumed_nutrition = array(nutrition_data)
    daily_nutrition_goal = array(goal_nutrition_data)
    dinner_nutrition_target = daily_nutrition_goal - previous_consumed_nutrition
    try:
        cuisine_choice = f["cuisine_choice"]
    except:
        cuisine_choice = "r"
    
    score, dinner_desc_list, dinner_portion_list, dinner_nutrition = generated_dinner_match(dinner_nutrition_target, daily_nutrition_goal, cuisine_choice)


    dinner_nutrition_data = []
    for val in dinner_nutrition:
        dinner_nutrition_data.append(str(round(val)))
    
    score_str = "%.2f" % (score)
    
    data = []
    for n in range(len(dinner_desc_list)):
        food_desc = dinner_desc_list[n]
        food_desc = food_desc.split(", NS")[0]
        food_desc = food_desc.lower()
        food_desc = food_desc[0].upper() + food_desc[1:]
        food_portion_desc = dinner_portion_list[n]
        data.append([food_desc, food_portion_desc])
    
    dinner_accuracy = (array(dinner_nutrition_data, dtype=float) / array(dinner_nutrition_target, dtype=float))
    
    dinner_colors = []
    dinner_simple_score = 0.0
    for n in range(len(dinner_accuracy)):
        if dinner_accuracy[n] > 0.9 and dinner_accuracy[n] < 1.1:
            dinner_colors.append("green")
            dinner_simple_score += 1.0
        elif dinner_accuracy[n] > 0.75 and dinner_accuracy[n] < 1.25:
            dinner_colors.append("black")
            dinner_simple_score += 0.5
        else:
            dinner_colors.append("red")
    
    if dinner_simple_score > 5:
        dinner_simple_score=5
    
    half_score_flag = True
    if int(dinner_simple_score) - dinner_simple_score == 0:
        half_score_flag = False
        
    int_dinner_simple_score = int(dinner_simple_score)
    
    dinner_nutrition_target = ["%.1f"%b for b in dinner_nutrition_target]
    print dinner_nutrition_target
    
    return render_template('index.html', create_dinners_flag=create_dinners_flag,
        consumed_calories=consumed_calories, 
        cuisine_choice=cuisine_choice,
        dinner_nutrition_target=dinner_nutrition_target,
        score=score_str, 
        data=data, 
        dinner_nutrition_data=dinner_nutrition_data, 
        dinner_colors=dinner_colors,
        dinner_simple_score=dinner_simple_score,
        int_dinner_simple_score=int_dinner_simple_score, half_score_flag=half_score_flag)


# ROUTING/VIEW FUNCTIONS
@app.route('/', methods=['GET', 'POST'])
@app.route('/advanced', methods = ['GET', 'POST'])
def advanced():
    # Renders advanced.html.
    nutrition_data = [0, 0, 0, 0, 0, 0]
    goal_nutrition_data = [2000, 245, 65, 98, 74, 38]
    f = request.form
#     for key in f.keys():
#         for value in f.getlist(key):
#             print key,":",value
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
        return render_template('advanced.html', create_dinners_flag=create_dinners_flag,
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
    
    return render_template('advanced.html', create_dinners_flag=create_dinners_flag,
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

@app.route('/slides')
def slides():
    # Renders slides.html.
    return render_template('slides.html')
    
@app.route('/clusters', methods = ['GET', 'POST'])
def show_cluster_analysis():
    f = request.form
    
    try:
        calc_top_flag = f["calc_top_flag"]
    except:
        calc_top_flag = False
            
    try:
        cuisine_choice = f["cuisine_choice"]
    except:
        cuisine_choice = "r"
        
    try:
        nutrient_choice = f["nutrient_choice"]
    except:
        nutrient_choice = "calories"
    
    try:
        hist_bound = int(f["hist_bound"])
    except:
        if nutrient_choice == "calories": hist_bound = 4000
        if nutrient_choice == "carbohydrates": hist_bound = 500
        if nutrient_choice == "fat": hist_bound = 200
        if nutrient_choice == "protein": hist_bound = 200
        if nutrient_choice == "sugar": hist_bound = 200
        if nutrient_choice == "fiber": hist_bound = 50
        else:
            hist_bound = 4000
    try:
        hist_bound_min = int(f["hist_bound_min"])
    except:
        hist_bound_min = 0


    if nutrient_choice == "calories" and hist_bound > 4000:
        hist_bound = 4000
    if nutrient_choice == "carbohydrates" and hist_bound > 500:
        hist_bound = 500
    if nutrient_choice == "fat" and hist_bound > 200:
        hist_bound = 200
    if nutrient_choice == "protein" and hist_bound > 200:
        hist_bound = 200
    if nutrient_choice == "sugar" and hist_bound > 200:
        hist_bound = 200
    if nutrient_choice == "fiber" and hist_bound > 50:
        hist_bound = 50
    
    if hist_bound_min > hist_bound: hist_bound_min=0
    
    pie_char_data = array([
        ('r', 0.46091192964423006, 0.3569472805074319, 0.18944281468647645),
        ('b', 0.5802051752319279, 0.30941463127217367, 0.1338963691513483),
        ('i', 0.4515032389154221, 0.39134772346363905, 0.17040828109485243),
        ('s', 0.36463121176563357, 0.4246055124908824, 0.23218032495582572),
        ('a', 0.34931124999085267, 0.4493337126604725, 0.18464774739257359),
        ('c', 0.33452270577542714, 0.43979258791519976, 0.2223958849343472),
        ('as', 0.46257023462263896, 0.34166056356137803, 0.209490428808256),
        ('m', 0.45526312192356677, 0.3754555351105417, 0.1984557875065679),
        ('h', 0.43982360238932189, 0.34867959936879961, 0.20476673227122424)], 
      dtype=[('cuisine_code', 'S2'), ('carb_cals', '<f8'), ('fat_cals', '<f8'), ('protein_cals', '<f8')])



    
    cuisine_specific_pie_char_data = pie_char_data[pie_char_data["cuisine_code"]==cuisine_choice]
    chart_data = []
    chart_data.append(cuisine_specific_pie_char_data["carb_cals"])
    chart_data.append(cuisine_specific_pie_char_data["fat_cals"])
    chart_data.append(cuisine_specific_pie_char_data["protein_cals"])
        
    hist_data = loadtxt("food_clustering_results/%s_%s.txt" % (cuisine_choice, nutrient_choice))

    hist_data = hist_data[(hist_data<hist_bound) & (hist_data>hist_bound_min)]

    hist_bin_thresholds = histogram(hist_data, range=[hist_bound_min, hist_bound], bins=25)[1].tolist()
    hist_data = hist_data.tolist()
    
    if calc_top_flag:
        top_foods_list, chart_data = top_eight_foods(cuisine_choice, nutrient_choice, hist_bound_min, hist_bound)
        top_five_foods = []
        for n in range(5):
            top_five_foods.append([top_foods_list[n][0], "%.2f" % (top_foods_list[n][1]) ])
    else:
        top_five_foods = []
    
    # Renders clusters.html.
    return render_template('clusters.html', 
        cuisine_choice=cuisine_choice, chart_data=chart_data,
        nutrient_choice=nutrient_choice,
        hist_data=hist_data, hist_bound=hist_bound, hist_bound_min=hist_bound_min, 
        hist_bin_thresholds=hist_bin_thresholds, top_five_foods=top_five_foods, calc_top_flag=calc_top_flag)

@app.route('/clustersmap')
def clustersmap():
    # Renders clustersmap.html.
    return render_template('clustersmap.html')

@app.route('/author')
def contact():
    # Renders author.html.
    return render_template('author.html')

@app.route('/network')
def show_cluster_network():
    # Renders author.html.
    return render_template('network.html')


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

