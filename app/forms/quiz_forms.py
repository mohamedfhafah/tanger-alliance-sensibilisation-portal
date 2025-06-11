from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, BooleanField, FloatField, HiddenField, IntegerField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

class QuizForm(FlaskForm):
    module_id = HiddenField('ID du Module')
    title = StringField('Titre', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional()])
    passing_score = FloatField('Score de passage (%)', validators=[DataRequired(), NumberRange(min=0, max=100)])
    submit = SubmitField('Enregistrer')

class QuestionForm(FlaskForm):
    quiz_id = HiddenField('ID du Quiz')
    content = TextAreaField('Question', validators=[DataRequired()])
    explanation = TextAreaField('Explication', validators=[Optional()])
    submit = SubmitField('Enregistrer')

class ChoiceForm(FlaskForm):
    question_id = HiddenField('ID de la Question')
    content = StringField('Réponse', validators=[DataRequired()])
    is_correct = BooleanField('Correcte')
    submit = SubmitField('Enregistrer')
