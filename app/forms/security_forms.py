from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, TextAreaField, SubmitField, SelectField, DateField, SelectMultipleField
from wtforms.validators import DataRequired, Email, Optional

class PhishingReportForm(FlaskForm):
    email_sender = StringField('Adresse expéditeur', validators=[DataRequired(), Email()])
    email_subject = StringField('Sujet de l\'email', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Signaler')

class IncidentReportForm(FlaskForm):
    incident_type = SelectField('Type d\'incident', choices=[
        ('phishing', 'Phishing / Tentative d\'hameçonnage'),
        ('malware', 'Malware / Logiciel malveillant'),
        ('data_breach', 'Fuite de données'),
        ('unauthorized', 'Accès non autorisé'),
        ('suspicious', 'Activité suspecte'),
        ('other', 'Autre')
    ], validators=[DataRequired()])
    description = TextAreaField('Description détaillée', validators=[DataRequired()])
    submit = SubmitField('Signaler l\'incident')


class PhishingCampaignForm(FlaskForm):
    """Form for creating phishing simulation campaigns."""
    name = StringField('Nom de la campagne', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    template = SelectField('Template d\'email', choices=[
        ('fake_shipping_manifest', 'Faux manifeste d\'expédition'),
        ('fake_customs_notification', 'Notification douanes frauduleuse'),
        ('fake_portnet_security_alert', 'Alerte sécurité système')
    ], validators=[DataRequired()])

    simulation_title = StringField('Titre de la simulation', validators=[DataRequired()])
    simulation_description = TextAreaField('Description de la simulation', validators=[Optional()])
    start_date = DateField('Date de début', validators=[Optional()])
    end_date = DateField('Date de fin', validators=[Optional()])

    target_all = BooleanField('Cibler tous les utilisateurs')
    target_departments = SelectMultipleField('Départements', choices=[], validators=[Optional()])
    target_users = SelectMultipleField('Utilisateurs spécifiques', choices=[], validators=[Optional()])

    # Legacy fields kept for backward compatibility with older route logic.
    target_selection = SelectField('Ciblage', choices=[
        ('all_users', 'Tous les utilisateurs'),
        ('by_department', 'Par département'),
        ('specific_users', 'Utilisateurs spécifiques')
    ], validators=[Optional()])
    department = SelectField('Département', choices=[], validators=[Optional()])

    submit = SubmitField('Créer la campagne')
