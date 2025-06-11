from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField, DateField, SelectMultipleField
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
        ('shipping_manifest', 'Faux manifeste d\'expédition'),
        ('customs_notification', 'Notification douanes frauduleuse'),
        ('port_security_alert', 'Alerte sécurité système'),
        ('ceo_fraud', 'Email de PDG frauduleux'),
        ('generic_phishing', 'Template générique')
    ], validators=[DataRequired()])
    
    target_selection = SelectField('Ciblage', choices=[
        ('all_users', 'Tous les utilisateurs'),
        ('by_department', 'Par département'),
        ('specific_users', 'Utilisateurs spécifiques')
    ], validators=[DataRequired()])
    
    department = SelectField('Département', choices=[
        ('', 'Sélectionner un département'),
        ('Logistique', 'Logistique'),
        ('Douanes', 'Douanes'),
        ('Sécurité', 'Sécurité'),
        ('IT', 'IT'),
        ('RH', 'Ressources Humaines'),
        ('Commercial', 'Commercial'),
        ('Finance', 'Finance'),
        ('Direction', 'Direction')
    ], validators=[Optional()])
    
    start_date = DateField('Date de début', validators=[Optional()])
    submit = SubmitField('Créer la campagne')
