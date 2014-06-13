import re

class Portion:
    'weight, description pair'
    def __init__(self, weight, desc):
        self.weight = weight
        self.desc = desc
        
    def print_summary(self):
        print "%.2f g - %s" % (self.weight, self.desc)

class PortionList:
    'Common portions (weight in g, portion description)'
    def __init__(self, food_code, sub_code, list_of_portions):
        self.food_code = food_code
        self.sub_code = sub_code
        self.list_of_portions = list_of_portions
    
    def print_summary(self):
        print "food_code: %d, sub_code: %d" % (self.food_code, self.sub_code)
        for portion in list_of_portions:
            print "\t", 
            portion.print_summary()

class NutritionList:
    'calories, carbohydrate, fat, protein, sugar, fiber per 100 g'
    def __init__(self, calories, carbohydrate, fat, protein, sugar, fiber):
        self.calories = calories
        self.carbohydrate = carbohydrate
        self.fat = fat
        self.protein = protein
        self.sugar = sugar
        self.fiber = fiber
    
    def print_summary(self):
        print "%06.2f %06.2f %06.2f %06.2f %06.2f %06.2f" % (self.calories, 
            self.carbohydrate, self.fat, self.protein, self.sugar, self.fiber)

class FoodItem:
    'Decription of an item of food'
    def __init__(self, food_code, sub_code, mod_code, full_desc, nutrition_list, 
    portion_list):
        self.food_code = food_code
        self.sub_code = sub_code
        self.mod_code = mod_code
        self.full_desc = full_desc
        self.nutrition_list = nutrition_list
        self.portion_list = portion_list
        self.short_desc = re.split(r'[,()]+', self.full_desc)[0]
    
    def print_summary(self):
        print "%s" % self.short_desc
        nutrition_list.print_summary()

class MealRecord:
    'Full components of a dinner'
    def __init__(self, food_item_list, food_weight_list):
        self.food_item_list = food_item_list
        self.food_weight_list = food_weight_list
        assert(len(self.food_item_list) == len(self.food_weight_list))
        self.num_items = len(food_item_list)
        self.calories_list = []
        self.carbohydrate_list = []
        self.fat_list = [] 
        self.protein_list = []
        self.sugar_list = []
        self.fiber_list = []
        self.tot_calories = 0
        self.tot_carbohydrate = 0
        self.tot_fat = 0
        self.tot_protein = 0
        self.tot_sugar = 0
        self.tot_fiber = 0
        self.portion_multiplier_list = []
        self.portion_desc_list = []
        for n in range(self.num_items):
            self.calories_list.append(food_item_list[n].nutrition_list.calories * self.food_weight_list[n]/100.0)
            self.tot_calories += food_item_list[n].nutrition_list.calories * self.food_weight_list[n]/100.0
            self.carbohydrate_list.append(food_item_list[n].nutrition_list.carbohydrate * self.food_weight_list[n]/100.0)
            self.tot_carbohydrate += food_item_list[n].nutrition_list.carbohydrate * self.food_weight_list[n]/100.0
            self.fat_list.append(food_item_list[n].nutrition_list.fat * self.food_weight_list[n]/100.0)
            self.tot_fat += food_item_list[n].nutrition_list.fat * self.food_weight_list[n]/100.0
            self.protein_list.append(food_item_list[n].nutrition_list.protein * self.food_weight_list[n]/100.0)
            self.tot_protein += food_item_list[n].nutrition_list.protein * self.food_weight_list[n]/100.0
            self.sugar_list.append(food_item_list[n].nutrition_list.sugar * self.food_weight_list[n]/100.0)
            self.tot_sugar += food_item_list[n].nutrition_list.sugar * self.food_weight_list[n]/100.0
            self.fiber_list.append(food_item_list[n].nutrition_list.fiber * self.food_weight_list[n]/100.0)
            self.tot_fiber += food_item_list[n].nutrition_list.fiber * self.food_weight_list[n]/100.0
            
            num_portion_types = len(food_item_list[n].portion_list.list_of_portions)
            candidate_portion_multiplier_and_desc_list = []
            for m in range(num_portion_types):
                multiplier = self.food_weight_list[n] / food_item_list[n].portion_list.list_of_portions[m].weight
                candidate_portion_multiplier_and_desc_list.append([(1.0/multiplier + multiplier/1.0)/2.0, 
                multiplier, food_item_list[n].portion_list.list_of_portions[m].desc])
            portion_multiplier_and_desc = sorted(candidate_portion_multiplier_and_desc_list, reverse=False)[0]
            self.portion_multiplier_list.append(portion_multiplier_and_desc[1])
            self.portion_desc_list.append(portion_multiplier_and_desc[2])
            
    def print_summary(self):
        for n in range(self.num_items):
            print "%.2f x %s of %s" % (self.portion_multiplier_list[n], self.portion_desc_list[n], self.food_item_list[n].short_desc)
        print "%06.2f %06.2f %06.2f %06.2f %06.2f %06.2f" % (self.tot_calories, 
            self.tot_carbohydrate, self.tot_fat, self.tot_protein, self.tot_sugar, self.tot_fiber)
            
    def print_meal_table(self):
        for n in range(self.num_items):
            if len(self.food_item_list[n].full_desc) < 50:
                print "%s - %s" % (self.food_item_list[n].full_desc, self.portion_desc_list[n])
            else:
                print "%s ... - %s" % (self.food_item_list[n].full_desc[:50], self.portion_desc_list[n])
        print "%06.2f %06.2f %06.2f %06.2f %06.2f %06.2f" % (self.tot_calories, 
            self.tot_carbohydrate, self.tot_fat, self.tot_protein, self.tot_sugar, self.tot_fiber)