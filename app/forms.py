from flask.ext.wtf import Form
from wtforms.fields import TextField, BooleanField
from wtforms.validators import Required

class NutritionForm(Form):
        user_previous_consumed_nutrition = TextField('user_previous_consumed_nutrition')
        random_dinner_flag = BooleanField('random_dinner_flag', default = False)