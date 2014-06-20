import pymysql
import collections
from numpy import array, ma, mean
from app import host, port, user, passwd, db

def top_eight_foods(cuisine_code, nutrient, hist_bound_min, hist_bound):
    print host, port, user, passwd, db
    if nutrient == "carbohydrates": nutrient = "carbohydrate"
    conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db)
    cur = conn.cursor()

    if cuisine_code == "h":
        cur.execute("""
            SELECT dinner_desc
            FROM historical_dinners
            WHERE (%s < %f) AND (%s > %f);""" % (nutrient, hist_bound, nutrient, hist_bound_min))
        returned_data = cur.fetchall()
        cur.execute("""
        SELECT calories, carbohydrate, fat, protein, sugar, fiber
        FROM historical_dinners
        WHERE (%s < %f) AND (%s > %f);""" % (nutrient, hist_bound, nutrient, hist_bound_min))
        nutrition_data = cur.fetchall()
        nutrition_data = array(nutrition_data)
    else:
        cur.execute("""
            SELECT dinner_desc
            FROM %s_generated_dinners
            WHERE (%s < %f) AND (%s > %f);""" % (cuisine_code, nutrient, hist_bound, nutrient, hist_bound_min))
        returned_data = cur.fetchall()
        cur.execute("""
        SELECT calories, carbohydrate, fat, protein, sugar, fiber
        FROM %s_generated_dinners
        WHERE (%s < %f) AND (%s > %f);""" % (cuisine_code, nutrient, hist_bound, nutrient, hist_bound_min))
        nutrition_data = cur.fetchall()
        nutrition_data = array(nutrition_data)
    cur.close()
    conn.close()
    
    
    cals = ma.masked_array(nutrition_data[:,0], 0>=(nutrition_data[:,0]))

    mcarb = ma.masked_array(nutrition_data[:,1]*4/cals, (0>=nutrition_data[:,1]))
    mfat = ma.masked_array(nutrition_data[:,2]*9/cals, (0>=nutrition_data[:,2]))
    mpro = ma.masked_array(nutrition_data[:,3]*4/cals, (0>=nutrition_data[:,3]))

    pie_chart_data = [mean(mcarb), mean(mfat), mean(mpro)]
    
    
    
    n_dinners = float(len(returned_data))

    base_foods_list = []
    for dinner_list in returned_data:
        base_food_words = []
        food_list = dinner_list[0].split("|")
        for food_desc in food_list:
            base_foods = []
            for food_item in food_desc.split(","):
                base_food = food_item.split("(")[0].lstrip().rstrip().lower()
                if base_food != "":
                    base_foods.append(base_food)
            food_desc_words = list(set(base_foods))
            base_food_words += food_desc_words
        base_foods_list += base_food_words



    counter=collections.Counter(base_foods_list)

    unique_phrases = counter.keys()
    phrase_freq = counter.values()  # higher means more closely connected

    common_nonfood_phrases = ["raw", "cooked", "fat not added in cooking", 
        "white", "from fresh", "regular", "cola-type", "salted", "unsweetened",
        "green", "fluid", "cow's", "lean only eaten", "fried", "from frozen", "roasted", 
        "soft", "tap", "fat added in cooking", "mature", "red", "breast", "sugar-free", 
        "baked or fried", "skin not eaten", "broiled", "or baked", 
        "ns as to fat added in cooking", "bottled", "from canned", "tub", "leaf", 
        "string", "coated", "mashed", "baked", "ns as to form", "ns as to type", 
        "stick", "broiled or baked", "decaffeinated", "prepared with skin", "dry", 
        "fruit-flavored", "caffeine free", "yellow", 
        "fat added in cooking w/ vegetable oil (include oil)", "meatless", 
        "made with sour cream and/or buttermilk and oil", "cheddar or american type", 
        "deep fried", "presweetened with sugar", "not homemade", "table", "2% fat", 
        "whole", "canned", "made with vinegar and oil", "wheat or cracked wheat", 
        "reduced calorie", "prepackaged or deli", "flavors other than chocolate", 
        "processed", "lean and fat eaten", "thin crust", "american or cheddar type", 
        "skin eaten", "whole wheat", "wing", "skin/coating eaten", 
        "corn or cornmeal base", "peel not eaten", "ns as to fat eaten", "lean", 
        "or extra lean)", "ns as to percent lean (formerly ns as to regular", 
        "ground beef or patty", "fat added in cooking w/ animal fat or meat drippings",
        "drumstick", "ns as to skin eaten", "ns as to 100%", "natural", 
        "fat added in cooking w/ butter", "flour (wheat)", "granulated or lump", 
        "breaded", "chips", "boiled", "beef or meat", "with pork", "with beef",
        "crab meat and cream cheese filled", "with shrimp", "with chicken", 
        "and/or dark-green leafy", "and dark-green leafy", "no sauce",
        "with chicken or turkey", "with beef and/or pork", "baby food",
        "tomato-based sauce", "toddler", "hawaiian style", "strained",
        "chinese style", "plain", "fat free", "rye", "ripe", "dried", 
        "with chocolate chips", "sour dough", "high fiber", "buckwheat", "with fruit",
        "lowfat", "canned or frozen", "100% whole wheat or 100% whole grain", 
        "nut and honey", "mandarin", "chocolate chip", "multi-bran", "fruit", 
        "oat bran", "or multigrain", "bran", "cooked or canned", "kellogg's",
        "with ham or bacon", "malted", "ns as to sweetened or unsweetened; sweetened", 
        "ns as to type of sweetener", "with potatoes and/or onions", "with sugar", 
        "low sodium", "on bun", "thick crust", "with mayonnaise or salad dressing", 
        "ns as to type of crust", "regular crust", "1/4 lb meat", 
        "prepared from frozen", "with tomato and/or catsup", "sweet", "with lettuce",
        "or hot dog", "wiener", "tomato and spread", "low-calorie or diet", 
        "or romaine lettuce", "chicory", "escarole", 
        "fat added in cooking w/ vegetable oil", "japanese", "homemade-style", 
        "creamed", "home-made style", "with cheese sauce", "pickled", "no beans", 
        "tomato- based sauce", "uncooked", "homemade", "and cheese", 
        "cheese and lettuce", "tomato and sour cream", "and lettuce", "reduced fat", 
        "light", "imitation", "half and half", "filled", "nonbutterfat", 
        "sour dressing", "low calorie", "frozen", "floured or breaded", "floured",
        "or battered", "fried w/ vegetable oil", "battered", "ns as to cooking method", 
        "baked or broiled", "baked or broiled w/ butter", 
        "baked or broiled w/ vegetable oil", "fried w/ margarine", "catfish", 
        "baked or broiled w/o fat", "smoked", "steamed or boiled", 
        "breaded or battered", "steamed", "fried w/ animal fat or meat drippings", 
        "baked or broiled  w/o fat", "baked or broiled w/ animal fat or meat drippings", 
        "fried w/ butter", "and/or poultry", "made from home recipe"]

    cleaned_common_phrases = []
    common_phrases = counter.most_common(len(unique_phrases))
    num_top = 8
    num_count = 0
    for phrase_entry in common_phrases:
        if num_count >= num_top:
            break
        else:
            phrase = phrase_entry[0]
            if phrase not in common_nonfood_phrases:
                num_count += 1
                cleaned_common_phrases.append((phrase, phrase_entry[1]/n_dinners))

#     for phrase_entry in cleaned_common_phrases:
#         print "%0.3f\t%s" % (phrase_entry[1], phrase_entry[0])







    return cleaned_common_phrases, pie_chart_data