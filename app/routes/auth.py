from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, current_user, logout_user, login_required
from app import db, bcrypt, mail
from app.models.user import User
from app.forms.auth_forms import LoginForm, RegistrationForm, RequestResetForm, ResetPasswordForm
from flask_mail import Message

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Route pour la connexion des utilisateurs."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            # Mettre à jour la date de dernière connexion
            user.update_last_login()
            db.session.commit()
            flash('Vous êtes connecté', 'success')
            return redirect(next_page if next_page else url_for('main.dashboard'))
        else:
            flash('Identifiants invalides', 'danger')
    
    return render_template('auth/login.html', title='Connexion', form=form)

@auth.route('/logout')
def logout():
    """Route pour la déconnexion des utilisateurs."""
    logout_user()
    flash('Vous êtes déconnecté', 'info')
    return redirect(url_for('main.home'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """Route pour l'inscription des utilisateurs."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(
            email=form.email.data,
            firstname=form.firstname.data,
            lastname=form.lastname.data,
            password=hashed_password,
            department=form.department.data,
            role='user'
        )
        db.session.add(user)
        db.session.commit()
        flash('Compte créé avec succès! Vous pouvez maintenant vous connecter.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='Inscription', form=form)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Demande de réinitialisation de mot de passe - Portail Sécurité Tanger Alliance',
                  sender=current_app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[user.email])
    msg.body = f'''Pour réinitialiser votre mot de passe, veuillez visiter le lien suivant:
{url_for('auth.reset_token', token=token, _external=True)}

Si vous n'avez pas demandé cette réinitialisation, veuillez ignorer cet e-mail.
Ce lien expirera dans 30 minutes.
'''
    mail.send(msg)

@auth.route('/reset_password', methods=['GET', 'POST'])
def request_reset():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_reset_email(user)
            flash('Instructions envoyées', 'info')
            return redirect(url_for('auth.login'))
        else:
            # Flash message already handled by form validator if email doesn't exist
            # but good to have a fallback or specific message if needed.
            flash('Si un compte avec cet email existe, un email de réinitialisation a été envoyé.', 'info') 
            # Security practice: don't confirm if email exists or not directly here
            return redirect(url_for('auth.login')) # Redirect to login to avoid enumeration
    return render_template('auth/request_reset.html', title='Réinitialiser le mot de passe', form=form)

@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('Le jeton de réinitialisation est invalide ou a expiré.', 'warning')
        return redirect(url_for('auth.request_reset'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Votre mot de passe a été mis à jour ! Vous pouvez maintenant vous connecter.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_token.html', title='Réinitialiser le mot de passe', form=form, token=token)
