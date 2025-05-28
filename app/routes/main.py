from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import current_user, login_required

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/home')
def home():
    """Route pour la page d'accueil."""
    return render_template('home.html', title='Accueil')

@main.route('/about')
def about():
    """Route pour la page À propos."""
    return render_template('about.html', title='À propos')

@main.route('/dashboard')
@login_required
def dashboard():
    """Route pour le tableau de bord utilisateur."""
    return render_template('dashboard.html', title='Tableau de bord')
