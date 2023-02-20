from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired, Optional


class BarOrderForm(FlaskForm):

	handled_by = StringField("Namn", validators=[InputRequired()])
	submit = SubmitField("Lägg beställning")


class ItemDietForm(FlaskForm):
	diet = StringField("Specialkost", validators=[Optional()])
	submit = SubmitField("Spara")