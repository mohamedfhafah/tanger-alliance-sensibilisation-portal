from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, IntegerField, FloatField, HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional, NumberRange

class UserForm(FlaskForm):
    username = StringField('Nom d\'utilisateur', validators=[Optional(), Length(max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    firstname = StringField('Prénom', validators=[Optional(), Length(max=50)])
    lastname = StringField('Nom', validators=[Optional(), Length(max=50)])
    password = PasswordField('Mot de passe', validators=[Optional(), Length(min=8)])
    password_confirm = PasswordField('Confirmer le mot de passe', 
                                   validators=[Optional(), EqualTo('password', message='Les mots de passe doivent correspondre')])
    department = SelectField('Département', choices=[
        ('it', 'Informatique & Technologie'),
        ('operations', 'Opérations'),
        ('finance', 'Finance & Administration'),
        ('commercial', 'Commercial & Marketing'),
        ('rh', 'Ressources Humaines'),
        ('security', 'Sécurité'),
        ('other', 'Autre')
    ], validators=[DataRequired()])
    role = SelectField('Rôle', choices=[
        ('user', 'Utilisateur'),
        ('admin', 'Administrateur')
    ], validators=[DataRequired()])
    submit = SubmitField('Enregistrer')

class ModuleForm(FlaskForm):
    title = StringField('Titre', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    content = TextAreaField('Contenu', validators=[DataRequired()])
    order = IntegerField('Ordre d\'affichage', validators=[DataRequired(), NumberRange(min=1)])
    is_active = BooleanField('Actif')
    submit = SubmitField('Enregistrer')
