from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models.user import User

class LoginForm(FlaskForm):
    """Formulaire de connexion"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    remember = BooleanField('Se souvenir de moi')
    submit = SubmitField('Connexion')

class RegistrationForm(FlaskForm):
    """Formulaire d'inscription"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    department = SelectField('Département', 
                            choices=[
                                ('', 'Sélectionnez votre département'),
                                ('IT', 'IT'),
                                ('Operations', 'Opérations'),
                                ('Admin', 'Administration'),
                                ('Finance', 'Finance'),
                                ('HR', 'Ressources Humaines')
                            ],
                            validators=[DataRequired()])
    password = PasswordField('Mot de passe', 
                             validators=[DataRequired(), 
                                         Length(min=12, message="Le mot de passe doit contenir au moins 12 caractères.")])
    confirm_password = PasswordField('Confirmer le mot de passe', 
                                    validators=[DataRequired(), 
                                                EqualTo('password', message="Les mots de passe doivent correspondre.")])
    submit = SubmitField('S\'inscrire')
    
    def validate_email(self, email):
        """Valide que l'email n'est pas déjà utilisé"""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Cet email est déjà utilisé. Veuillez en choisir un autre.')
    
    def validate_password(self, password):
        """Vérifie que le mot de passe respecte les critères de complexité"""
        pwd = password.data
        
        # Au moins une majuscule
        if not any(char.isupper() for char in pwd):
            raise ValidationError('Le mot de passe doit contenir au moins une majuscule.')
        
        # Au moins une minuscule
        if not any(char.islower() for char in pwd):
            raise ValidationError('Le mot de passe doit contenir au moins une minuscule.')
        
        # Au moins un chiffre
        if not any(char.isdigit() for char in pwd):
            raise ValidationError('Le mot de passe doit contenir au moins un chiffre.')
        
        # Au moins un caractère spécial
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>/?"
        if not any(char in special_chars for char in pwd):
            raise ValidationError('Le mot de passe doit contenir au moins un caractère spécial.')
