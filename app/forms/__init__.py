# Ce fichier permet d'importer les formulaires directement depuis le package
from .auth_forms import LoginForm, RegistrationForm, RequestResetForm, ResetPasswordForm, UpdateProfileForm
from .admin_forms import UserForm, ModuleForm
from .quiz_forms import QuizForm, QuestionForm, ChoiceForm
from .security_forms import PhishingReportForm, IncidentReportForm, PhishingCampaignForm
