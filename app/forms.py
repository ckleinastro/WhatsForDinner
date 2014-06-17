from flask.ext.wtf import Form
from wtforms.fields import TextField, BooleanField, SelectField
from wtforms.validators import Required
import pymysql

class FoodChoiceForm(Form):
    food_choice = TextField('food_choice')
    
class PortionForm(Form):
    portion = SelectField('portion', coerce=int)

def determine_portion_choices(request, food_choice):

    conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='', 
                           db='food_consumption')
    cur = conn.cursor()

    cur.execute("""
    SELECT  food_descriptions.food_code, food_descriptions.sub_code, food_descriptions.mod_code,
            food_weights.portion_weight, food_weights.portion_desc
    FROM food_descriptions
    JOIN food_weights ON
        (food_descriptions.food_code=food_weights.food_code) AND 
        (food_descriptions.sub_code=food_weights.sub_code)
    WHERE food_desc='%s';""" % food_choice)
    returned_data = cur.fetchall()
    cur.close()
    conn.close()
    
    portion_choices = []
    counter = 1
    for row in returned_data:
        print row
        portion_choices.append((counter, row[4]))
        counter += 1
    
    

    form = PortionForm(request.POST, obj=portion)
    form.portion.choices = [(1, "P1"), (2, "P2")]