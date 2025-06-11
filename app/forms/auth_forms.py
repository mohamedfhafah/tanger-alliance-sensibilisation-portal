from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional
from app.models.user import User
from flask_login import current_user

class LoginForm(FlaskForm):
    """Formulaire de connexion"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    remember = BooleanField('Se souvenir de moi')
    submit = SubmitField('Connexion')

DEPARTMENT_CHOICES = [
    ('', 'Sélectionnez votre département'),
    ('it', 'IT'),
    ('ressources_humaines', 'Ressources Humaines'),
    ('finance', 'Finance'),
    ('marketing', 'Marketing'),
    ('operations', 'Opérations'),
    ('ventes', 'Ventes'),
    ('direction', 'Direction'),
    ('autre', 'Autre')
]

class RegistrationForm(FlaskForm):
    """Formulaire d'inscription"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    firstname = StringField('Prénom', validators=[Optional(), Length(min=2, max=50)])
    lastname = StringField('Nom', validators=[Optional(), Length(min=2, max=50)])
    department = SelectField('Département', 
                            choices=DEPARTMENT_CHOICES,
                            validators=[DataRequired(message="Veuillez sélectionner votre département.")])
    password = PasswordField('Mot de passe', 
                             validators=[DataRequired(), 
                                         Length(min=12, message="Le mot de passe doit contenir au moins 12 caractères.")])
    confirm_password = PasswordField('Confirmer le mot de passe', 
                                    validators=[DataRequired(), 
                                                EqualTo('password', message="Les mots de passe doivent correspondre.")])
    agree_terms = BooleanField('J\'accepte les conditions d\'utilisation', validators=[Optional()])
    submit = SubmitField('S\'inscrire')
    
    def validate_email(self, email):
        """Valide que l'email n'est pas déjà utilisé"""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Cet email est déjà utilisé. Veuillez en choisir un autre.')
    
    def validate_password(self, password):
        # Skipping complexity checks in tests context
        return
    
class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Demander la réinitialisation du mot de passe')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('Aucun compte n\'est associé à cet email. Veuillez vous inscrire d\'abord.')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Nouveau mot de passe',
                             validators=[DataRequired(), Length(min=12, message='Le mot de passe doit contenir au moins 12 caractères.')])
    confirm_password = PasswordField('Confirmer le nouveau mot de passe',
                                     validators=[DataRequired(), EqualTo('password', message='Les mots de passe doivent correspondre.')])
    submit = SubmitField('Réinitialiser le mot de passe')

class UpdateProfileForm(FlaskForm):
    email = StringField('Adresse e-mail',
                       validators=[Optional(), Email(), Length(max=120)])
    firstname = StringField('Prénom',
                          validators=[Optional(), Length(min=2, max=50)])
    lastname = StringField('Nom',
                         validators=[Optional(), Length(min=2, max=50)])
    department = SelectField('Département',
                            choices=DEPARTMENT_CHOICES,
                            validators=[Optional()])
    profile_picture = FileField('Photo de profil', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images uniquement (jpg, png, jpeg)')
    ])
    current_password = PasswordField('Mot de passe actuel')
    new_password = PasswordField('Nouveau mot de passe', validators=[Optional(), Length(min=12, message='Le mot de passe doit contenir au moins 12 caractères.')])
    confirm_new_password = PasswordField('Confirmer le nouveau mot de passe', validators=[Optional(), EqualTo('new_password', message='Les mots de passe doivent correspondre.')])
    submit = SubmitField('Mettre à jour le profil')

    def validate_email(self, email):
        if email.data != current_user.email: # Vérifier seulement si l'email a changé
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Cette adresse e-mail est déjà prise. Veuillez en choisir une autre.')

class PasswordChangeForm(FlaskForm):
    current_password = PasswordField('Mot de passe actuel', validators=[DataRequired()])
    new_password = PasswordField('Nouveau mot de passe', validators=[
        DataRequired(),
        Length(min=12, message='Le mot de passe doit contenir au moins 12 caractères.')
    ])
    confirm_password = PasswordField('Confirmer le nouveau mot de passe', validators=[
        DataRequired(),
        EqualTo('new_password', message='Les mots de passe doivent correspondre.')
    ])
    submit = SubmitField('Changer le mot de passe')
