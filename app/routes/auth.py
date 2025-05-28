from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, current_user, logout_user, login_required
from app import db, bcrypt
from app.models.user import User
from app.forms.auth_forms import LoginForm, RegistrationForm

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
            flash('Connexion réussie!', 'success')
            return redirect(next_page if next_page else url_for('main.dashboard'))
        else:
            flash('Connexion échouée. Vérifiez votre email et votre mot de passe.', 'danger')
    
    return render_template('auth/login.html', title='Connexion', form=form)

@auth.route('/logout')
def logout():
    """Route pour la déconnexion des utilisateurs."""
    logout_user()
    flash('Vous avez été déconnecté.', 'info')
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
            password=hashed_password,
            department=form.department.data,
            role='user'
        )
        db.session.add(user)
        db.session.commit()
        flash('Compte créé avec succès! Vous pouvez maintenant vous connecter.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='Inscription', form=form)
