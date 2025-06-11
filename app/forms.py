from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, IntegerField, FloatField, HiddenField, SelectMultipleField, DateTimeField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional, NumberRange
from app.models.user import User
from flask_login import current_user

# Formulaires d'authentification
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    remember = BooleanField('Se souvenir de moi')
    submit = SubmitField('Connexion')

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirmer le mot de passe', 
                                   validators=[DataRequired(), EqualTo('password', message='Les mots de passe doivent correspondre')])
    department = SelectField('Département', choices=[
        ('', 'Sélectionnez votre département'),
        ('it', 'Informatique & Technologie'),
        ('operations', 'Opérations'),
        ('finance', 'Finance & Administration'),
        ('commercial', 'Commercial & Marketing'),
        ('rh', 'Ressources Humaines'),
        ('security', 'Sécurité'),
        ('other', 'Autre')
    ], validators=[DataRequired()])
    submit = SubmitField('S\'inscrire')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Cet email est déjà utilisé. Veuillez en choisir un autre.')

class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Demander la réinitialisation')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            # Sécurité : ne pas révéler si l'email existe ou non
            # Pour éviter l'énumération des emails existants
            pass

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Nouveau mot de passe', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirmer le mot de passe', 
                                    validators=[DataRequired(), EqualTo('password', message='Les mots de passe doivent correspondre')])
    submit = SubmitField('Réinitialiser le mot de passe')

# Formulaire de mise à jour du profil
class UpdateProfileForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    firstname = StringField('Prénom', validators=[DataRequired(), Length(max=50)])
    lastname = StringField('Nom', validators=[DataRequired(), Length(max=50)])
    department = SelectField('Département', choices=[
        ('it', 'Informatique & Technologie'),
        ('operations', 'Opérations'),
        ('finance', 'Finance & Administration'),
        ('commercial', 'Commercial & Marketing'),
        ('rh', 'Ressources Humaines'),
        ('security', 'Sécurité'),
        ('other', 'Autre')
    ], validators=[DataRequired()])
    profile_picture = FileField('Photo de profil', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images uniquement (jpg, png, jpeg)')
    ])
    current_password = PasswordField('Mot de passe actuel', validators=[Optional()])
    new_password = PasswordField('Nouveau mot de passe', validators=[Optional(), Length(min=8)])
    confirm_new_password = PasswordField('Confirmer le nouveau mot de passe', 
                                        validators=[EqualTo('new_password', message='Les mots de passe doivent correspondre')])
    submit = SubmitField('Mettre à jour')
    
    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Cet email est déjà utilisé par un autre compte.')

# Formulaires d'administration
class UserForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe', validators=[Optional(), Length(min=8)])
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

class QuizForm(FlaskForm):
    title = StringField('Titre', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional()])
    passing_score = FloatField('Score de passage (%)', validators=[DataRequired(), NumberRange(min=0, max=100)])
    submit = SubmitField('Enregistrer')

class QuestionForm(FlaskForm):
    quiz_id = HiddenField('ID du Quiz')
    text = TextAreaField('Question', validators=[DataRequired()])
    submit = SubmitField('Enregistrer')

class ChoiceForm(FlaskForm):
    question_id = HiddenField('ID de la Question')
    text = StringField('Réponse', validators=[DataRequired()])
    is_correct = BooleanField('Correcte')
    submit = SubmitField('Enregistrer')

class PhishingReportForm(FlaskForm):
    email_sender = StringField('Adresse expéditeur', validators=[DataRequired(), Email()])
    email_subject = StringField('Sujet de l\'email', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Signaler')

class PhishingCampaignForm(FlaskForm):
    name = StringField('Nom de la campagne', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    template = SelectField('Template d\'email', choices=[
        ('fake_shipping_manifest', 'Faux Manifeste d\'Expédition'),
        ('fake_customs_notification', 'Fausse Notification Douanes'),
        ('fake_portnet_security_alert', 'Fausse Alerte Sécurité PortNet')
    ], validators=[DataRequired()])
    
    simulation_title = StringField('Titre de la simulation', validators=[DataRequired(), Length(max=100)])
    simulation_description = TextAreaField('Description de la simulation', validators=[Optional()])
    
    start_date = DateTimeField('Date de début', validators=[Optional()])
    end_date = DateTimeField('Date de fin', validators=[Optional()])
    
    # Options de ciblage
    target_all = BooleanField('Cibler tous les utilisateurs')
    target_departments = SelectMultipleField('Départements ciblés', choices=[
        ('it', 'Informatique & Technologie'),
        ('operations', 'Opérations'),
        ('finance', 'Finance & Administration'),
        ('commercial', 'Commercial & Marketing'),
        ('rh', 'Ressources Humaines'),
        ('security', 'Sécurité'),
        ('other', 'Autre')
    ])
    target_users = SelectMultipleField('Utilisateurs spécifiques')
    
    submit = SubmitField('Créer la campagne')