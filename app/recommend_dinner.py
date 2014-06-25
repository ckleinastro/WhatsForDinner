from gensim.models import word2vec as gword2vec
import random
from numpy import array, mean, where
import pickle
import pymysql
import sys
import re
from object_class_defs import MealRecord, FoodItem, NutritionList, PortionList, Portion
from app import host, port, user, passwd, db

def themed_dinner(target_num_items, model, clusters, chosen_cluster=-1):
    n_clusters = len(clusters)
    if chosen_cluster == -1:
        food_array = clusters[random.choice(range(n_clusters))]
    else:
        food_array = clusters[chosen_cluster]
    while len(food_array) > 10:
        food_array = food_array[food_array!= model.doesnt_match(food_array)]
    food_list = food_array.tolist()
    expanded_food_list = []
    for seed_food in food_list:
        similar_foods = model.most_similar(seed_food, topn=5)
        random.shuffle(similar_foods)
        for similar_food in similar_foods[:3]:
            if similar_food[0] not in expanded_food_list:
                expanded_food_list.append(similar_food[0])
    final_food_array = array(expanded_food_list)
    while len(final_food_array) > int((target_num_items-1)*1.5):
        final_food_array = final_food_array[final_food_array!= model.doesnt_match(final_food_array)]
    final_food_list = final_food_array.tolist()
    random.shuffle(final_food_list)
    final_food_list = final_food_list[:target_num_items-1]
    final_food_list = final_food_list + [model.most_similar(positive=final_food_list, topn=1)[0][0]]
    string_final_food_list = []
    for food_unicode in final_food_list:
        string_final_food_list.append(str(food_unicode))
    return string_final_food_list

def random_dinner(target_num_items, model, clusters):
    n_clusters = len(clusters)
    paired_items = []
    used_cluster_seeds = []
    while len(paired_items) < target_num_items:
        cluster_seed = random.choice(range(n_clusters))
        if len(clusters[cluster_seed]) > target_num_items:
            if cluster_seed not in used_cluster_seeds:
                used_cluster_seeds.append(cluster_seed)
                food_array = clusters[cluster_seed]
                cluster_ranked_food_list = []
                while len(food_array) > 1:
                    cluster_ranked_food_list.append(model.doesnt_match(food_array))
                    food_array = food_array[food_array!= model.doesnt_match(food_array)]
                cluster_ranked_food_list.append(food_array[0])
                cluster_ranked_food_list.reverse()  # first foods are most "archetypal"
                # Choose one from top portion of list, and one from bottom-middle portion
                main_food_item = cluster_ranked_food_list[random.choice(range(len(cluster_ranked_food_list)/4))]
                second_food_item = cluster_ranked_food_list[random.choice(range(len(cluster_ranked_food_list)/2, int(len(cluster_ranked_food_list)/1.2)))]
                if random.random() > 0.5:
                    paired_items += [main_food_item, second_food_item]
                else:
                    third_food_item = cluster_ranked_food_list[random.choice(range(len(cluster_ranked_food_list)/2, int(len(cluster_ranked_food_list)/1.2)))]
                    while third_food_item == second_food_item:
                        third_food_item = cluster_ranked_food_list[random.choice(range(len(cluster_ranked_food_list)/2, int(len(cluster_ranked_food_list)/1.2)))]
                    paired_items += [main_food_item, second_food_item, third_food_item] 
    paired_items_array = array(paired_items)
    while len(paired_items_array) > target_num_items:
        paired_items_array = paired_items_array[paired_items_array!= model.doesnt_match(paired_items_array)]
    return paired_items_array.tolist()

def recommend_dinner(dinner_nutrition_target, daily_nutrition_goal, model, clusters, themed=True):
    seed_dinners = []
    for w in range(25):
        if themed:
            seed_dinners.append(themed_dinner(random.choice([4, 5, 6]), model, clusters))
        else:
            seed_dinners.append(random_dinner(random.choice([4, 5, 6]), model, clusters))

    dinner_list_with_scores = []
    conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db)
    cur = conn.cursor()
    for t_dinner in seed_dinners:
        food_item_list = []
        food_weight_list = []
        for food_vocab_name in t_dinner:

            cur.execute("""
            SELECT  food_code, sub_code, mod_code, food_desc,
                    preferred_portion_desc, preferred_portion_weight,
                    calories, carbohydrate, fat, protein, sugar, fiber
            FROM recommended_foods
            WHERE recommended_foods.vocab_desc='%s';""" % food_vocab_name)
            returned_data = cur.fetchall()
    
            chosen_food_match = random.choice(returned_data)

            portion = Portion(chosen_food_match[5], chosen_food_match[4])
    
            portions_list = PortionList(chosen_food_match[0], chosen_food_match[1], [portion])
    
            nutrition = NutritionList(  chosen_food_match[6], chosen_food_match[7],
                                        chosen_food_match[8], chosen_food_match[9],
                                        chosen_food_match[10], chosen_food_match[11])
    
            food = FoodItem(chosen_food_match[0], chosen_food_match[1], 
                            chosen_food_match[2], chosen_food_match[3], nutrition, portions_list)
            food_item_list.append(food)
            food_weight_list.append(chosen_food_match[5])

        dinner = MealRecord(food_item_list, food_weight_list)
        dinner_nutrition = array([dinner.tot_calories, dinner.tot_carbohydrate, 
            dinner.tot_fat, dinner.tot_protein, dinner.tot_sugar, dinner.tot_fiber])
        dinner_goal_offset = dinner_nutrition_target - dinner_nutrition
    
        dinner_score = sum( (abs(dinner_goal_offset/daily_nutrition_goal))**0.5 )
        
        
        # LOWER SCORE IS BETTER
        dinner_list_with_scores.append([dinner_score, dinner])
    
    cur.close()
    conn.close()

    dinner_list_with_scores.sort()
    return dinner_list_with_scores[0][0], dinner_list_with_scores[0][1]
    

def historical_dinner_match(dinner_nutrition_target, daily_nutrition_goal):
    dinner_list_with_scores = []
    conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db)
    cur = conn.cursor()

    counter = 0.1
    while counter < 1.0:
        cutting_limits = [1-counter, 1+counter]
        cur.execute("""
        SELECT  calories, carbohydrate, fat, protein, sugar, fiber,
                dinner_desc, portion_masses
        FROM historical_dinners
        WHERE   ((calories > %f) AND (calories < %f)) AND
                ((carbohydrate > %f) AND (carbohydrate < %f)) AND
                ((fat > %f) AND (fat < %f)) AND
                ((protein > %f) AND (protein < %f)) AND
                ((sugar > %f) AND (sugar < %f)) AND
                ((fiber > %f) AND (fiber < %f));""" % (
                dinner_nutrition_target[0]*cutting_limits[0], dinner_nutrition_target[0]*cutting_limits[1],
                dinner_nutrition_target[1]*cutting_limits[0], dinner_nutrition_target[1]*cutting_limits[1],
                dinner_nutrition_target[2]*cutting_limits[0], dinner_nutrition_target[2]*cutting_limits[1],
                dinner_nutrition_target[3]*cutting_limits[0], dinner_nutrition_target[3]*cutting_limits[1],
                dinner_nutrition_target[4]*cutting_limits[0], dinner_nutrition_target[4]*cutting_limits[1],
                dinner_nutrition_target[5]*cutting_limits[0], dinner_nutrition_target[5]*cutting_limits[1]))
        returned_data = cur.fetchall()
        if len(returned_data) > 10:
            break
        counter += 0.05

    cur.close()
    conn.close()

    dinner_scores = []
    for chosen_food_match in returned_data:
        dinner_nutrition = array(chosen_food_match[:6])
        dinner_goal_offset = dinner_nutrition_target - dinner_nutrition
        dinner_score = sum( (abs(dinner_goal_offset/daily_nutrition_goal))**0.5 )
        dinner_scores.append(dinner_score)
    dinner_scores = array(dinner_scores)
    try:
        best_dinner_index = where(dinner_scores == dinner_scores.min())[0][0]
    except:
        return -1, [], [], [-1, -1, -1, -1, -1, -1]
    
    best_dinner_calories = returned_data[best_dinner_index][0]
    best_dinner_carbohydrate = returned_data[best_dinner_index][1]
    best_dinner_fat = returned_data[best_dinner_index][2]
    best_dinner_protein = returned_data[best_dinner_index][3]
    best_dinner_sugar = returned_data[best_dinner_index][4]
    best_dinner_fiber = returned_data[best_dinner_index][5]
    
    best_dinner_nutrition = (best_dinner_calories, best_dinner_carbohydrate,
        best_dinner_fat, best_dinner_protein, best_dinner_sugar, best_dinner_fiber)
    best_dinner_desc_list = returned_data[best_dinner_index][6].split("|")
    best_dinner_portion_list = returned_data[best_dinner_index][7].split("|")
    best_dinner_score = dinner_scores[best_dinner_index]
    return best_dinner_score, best_dinner_desc_list, best_dinner_portion_list, best_dinner_nutrition

 



# def generated_dinner_match(dinner_nutrition_target, daily_nutrition_goal, cuisine_code):
def generated_dinner_match(dinner_nutrition_target, cuisine_code):

    conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db)
    cur = conn.cursor()
    
    counter = 0.5
    while counter < 1.0:
        cutting_limits = [1-counter, 1+counter]
        if cuisine_code == "h":
            cur.execute("""
            SELECT  calories, carbohydrate, fat, protein, sugar, fiber,
                    dinner_desc, portion_masses
            FROM historical_dinners
            WHERE   ((calories > %f) AND (calories < %f)) AND
                    ((carbohydrate > %f) AND (carbohydrate < %f)) AND
                    ((fat > %f) AND (fat < %f)) AND
                    ((protein > %f) AND (protein < %f)) AND
                    ((sugar > %f) AND (sugar < %f)) AND
                    ((fiber > %f) AND (fiber < %f));""" % (
                    dinner_nutrition_target[0]*cutting_limits[0], dinner_nutrition_target[0]*cutting_limits[1],
                    dinner_nutrition_target[1]*cutting_limits[0], dinner_nutrition_target[1]*cutting_limits[1],
                    dinner_nutrition_target[2]*cutting_limits[0], dinner_nutrition_target[2]*cutting_limits[1],
                    dinner_nutrition_target[3]*cutting_limits[0], dinner_nutrition_target[3]*cutting_limits[1],
                    dinner_nutrition_target[4]*cutting_limits[0], dinner_nutrition_target[4]*cutting_limits[1],
                    dinner_nutrition_target[5]*cutting_limits[0], dinner_nutrition_target[5]*cutting_limits[1]))
        else:
            cur.execute("""
            SELECT  calories, carbohydrate, fat, protein, sugar, fiber,
                    dinner_desc, portion_masses
            FROM %s_generated_dinners
            WHERE   ((calories > %f) AND (calories < %f)) AND
                    ((carbohydrate > %f) AND (carbohydrate < %f)) AND
                    ((fat > %f) AND (fat < %f)) AND
                    ((protein > %f) AND (protein < %f)) AND
                    ((sugar > %f) AND (sugar < %f)) AND
                    ((fiber > %f) AND (fiber < %f));""" % (cuisine_code,
                    dinner_nutrition_target[0]*cutting_limits[0], dinner_nutrition_target[0]*cutting_limits[1],
                    dinner_nutrition_target[1]*cutting_limits[0], dinner_nutrition_target[1]*cutting_limits[1],
                    dinner_nutrition_target[2]*cutting_limits[0], dinner_nutrition_target[2]*cutting_limits[1],
                    dinner_nutrition_target[3]*cutting_limits[0], dinner_nutrition_target[3]*cutting_limits[1],
                    dinner_nutrition_target[4]*cutting_limits[0], dinner_nutrition_target[4]*cutting_limits[1],
                    dinner_nutrition_target[5]*cutting_limits[0], dinner_nutrition_target[5]*cutting_limits[1]))

        
        
        
        returned_data = cur.fetchall()
        if len(returned_data) > 10:
            break
        counter += 0.05

    cur.close()
    conn.close()

#     dinner_scores = []
    simple_dinner_scores = []
    for chosen_food_match in returned_data:
        dinner_nutrition = array(chosen_food_match[:6])
#         dinner_goal_offset = dinner_nutrition_target - dinner_nutrition
#         dinner_score = sum( (abs(dinner_goal_offset/daily_nutrition_goal))**0.5 )
#         dinner_scores.append(dinner_score)
        dinner_accuracy = (array(dinner_nutrition, dtype=float) / array(dinner_nutrition_target, dtype=float))
        dinner_simple_score = 0.0
        for n in range(len(dinner_accuracy)):
            if dinner_accuracy[n] > 0.9 and dinner_accuracy[n] < 1.1:
                dinner_simple_score += 1.0
            elif dinner_accuracy[n] > 0.75 and dinner_accuracy[n] < 1.25:
                dinner_simple_score += 0.5
            else:
                continue
        if dinner_simple_score > 5:
            dinner_simple_score=5
        simple_dinner_scores.append(dinner_simple_score)
    
#     dinner_scores = array(dinner_scores)
    simple_dinner_scores = array(simple_dinner_scores)
    if len(simple_dinner_scores) == 0:
        return -1, [], [], [-1, -1, -1, -1, -1, -1]
    best_simple_dinner_score = simple_dinner_scores.max()

    if sum(simple_dinner_scores>=(best_simple_dinner_score)) > 10:
        best_dinner_index = random.choice(where(simple_dinner_scores>=(best_simple_dinner_score))[0].tolist())
    elif sum(simple_dinner_scores>=(best_simple_dinner_score-0.5)) > 10:
        best_dinner_index = random.choice(where(simple_dinner_scores>=(best_simple_dinner_score-0.5))[0].tolist())
    elif sum(simple_dinner_scores>=(best_simple_dinner_score-1)) > 10:
        best_dinner_index = random.choice(where(simple_dinner_scores>=(best_simple_dinner_score-1))[0].tolist())
    elif sum(simple_dinner_scores>=(best_simple_dinner_score-1.5)) > 10:
        best_dinner_index = random.choice(where(simple_dinner_scores>=(best_simple_dinner_score-1.5))[0].tolist())
    else:
        best_dinner_index = random.choice(where(simple_dinner_scores>=(0))[0].tolist())
    
    best_dinner_calories = returned_data[best_dinner_index][0]
    best_dinner_carbohydrate = returned_data[best_dinner_index][1]
    best_dinner_fat = returned_data[best_dinner_index][2]
    best_dinner_protein = returned_data[best_dinner_index][3]
    best_dinner_sugar = returned_data[best_dinner_index][4]
    best_dinner_fiber = returned_data[best_dinner_index][5]

    best_dinner_nutrition = (best_dinner_calories, best_dinner_carbohydrate,
        best_dinner_fat, best_dinner_protein, best_dinner_sugar, best_dinner_fiber)
    best_dinner_desc_list = returned_data[best_dinner_index][6].split("|")
    best_dinner_portion_list = returned_data[best_dinner_index][7].split("|")
    if cuisine_code != "h":
        simplified_best_dinner_portion_list = []
        for portion_desc in best_dinner_portion_list:
            simplified_best_dinner_portion_list.append(portion_desc.split("x ")[1])
        best_dinner_portion_list = simplified_best_dinner_portion_list
        
        
#     best_dinner_score = dinner_scores[best_dinner_index]
    best_dinner_simple_score = simple_dinner_scores[best_dinner_index]
    
#     return best_dinner_score, best_dinner_desc_list, best_dinner_portion_list, best_dinner_nutrition
    return best_dinner_desc_list, best_dinner_portion_list, best_dinner_nutrition