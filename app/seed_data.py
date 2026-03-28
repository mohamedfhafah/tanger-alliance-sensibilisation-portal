"""
Script pour initialiser la base de données avec des données d'exemple
"""
from app import db, create_app
from app.models.user import User
from app.models.module import Module, Quiz, Question, Choice
from app.models.badge import Badge
from datetime import datetime, timezone

def seed_modules():
    """Ajoute les modules de formation à la base de données de manière idempotente."""
    
    module_definitions = [
        {
            "title": "Gestion des mots de passe",
            "description": "Apprenez à créer et gérer des mots de passe forts pour protéger vos comptes professionnels et personnels.",
            "content": "Module sur les bonnes pratiques de gestion des mots de passe.",
            "order": 1, "image": "password_module.jpg", "is_active": True
        },
        {
            "title": "Sensibilisation au phishing",
            "description": "Développez votre capacité à identifier et à signaler les tentatives de phishing avant qu'elles ne causent des dommages.",
            "content": "Module sur la détection et la prévention des attaques de phishing.",
            "order": 2, "image": "phishing_module.jpg", "is_active": True
        },
        {
            "title": "Gestion des vulnérabilités",
            "description": "Comprenez comment identifier, signaler et gérer les vulnérabilités pour maintenir la sécurité de l'infrastructure.",
            "content": "Module sur l'identification et la gestion des vulnérabilités.",
            "order": 3, "image": "vulnerability_module.jpg", "is_active": True
        },
        {
            "title": "Protection des données sensibles",
            "description": "Apprenez à protéger les informations confidentielles dans un environnement portuaire et logistique.",
            "content": "Module sur la protection des données sensibles dans le contexte portuaire.",
            "order": 4, "image": "data_protection_module.jpg", "is_active": True
        },
        {
            "title": "Sécurité mobile",
            "description": "Apprenez comment sécuriser les appareils mobiles et les applications professionnelles contre les menaces émergentes.",
            "content": "Module sur la sécurisation des appareils mobiles et applications dans l'environnement professionnel.",
            "order": 5, "image": "mobile_security_module.jpg", "is_active": True
        },
        {
            "title": "Sécurité réseau",
            "description": "Maîtrisez les fondamentaux de la sécurité réseau et les protocoles de protection de l'infrastructure de Tanger Alliance.",
            "content": "Module sur les fondamentaux de la sécurité réseau et la protection de l'infrastructure.",
            "order": 6, "image": "network_security_module.jpg", "is_active": True
        }
    ]

    created_or_existing_modules = []
    newly_created_count = 0

    for mod_data in module_definitions:
        module = Module.query.filter_by(order=mod_data["order"]).first()
        if not module:
            module = Module(**mod_data)
            db.session.add(module)
            print(f"Module '{module.title}' (Order {module.order}) will be created.")
            newly_created_count += 1
        else:
            print(f"Module '{module.title}' (Order {module.order}) already exists.")
        created_or_existing_modules.append(module)

    if newly_created_count > 0:
        db.session.commit()
        print(f"{newly_created_count} new module(s) committed to the database.")
    else:
        print("No new modules to add.")

    # Ensure IDs are available for quiz creation, especially for newly created modules
    # For modules that were just committed, their IDs are now populated.

    module1_obj = next((m for m in created_or_existing_modules if m.order == 1), None)
    module3_obj = next((m for m in created_or_existing_modules if m.order == 3), None)
    module5_obj = next((m for m in created_or_existing_modules if m.order == 5), None)
    module6_obj = next((m for m in created_or_existing_modules if m.order == 6), None)

    if module1_obj and module1_obj.id:
        create_password_quiz(module1_obj.id)
    else:
        print(f"Module 1 (Order 1) not found or has no ID. Skipping password quiz creation.")
        
    if module3_obj and module3_obj.id:
        create_vulnerability_quiz(module3_obj.id)
    else:
        print(f"Module 3 (Order 3) not found or has no ID. Skipping vulnerability quiz creation.")
        
    if module5_obj and module5_obj.id:
        create_mobile_security_quiz(module5_obj.id)
    else:
        print(f"Module 5 (Order 5) not found or has no ID. Skipping mobile security quiz creation.")
        
    if module6_obj and module6_obj.id:
        create_network_security_quiz(module6_obj.id)
    else:
        print(f"Module 6 (Order 6) not found or has no ID. Skipping network security quiz creation.")
        
    return created_or_existing_modules

def create_vulnerability_quiz(module_id):
    """Crée le quiz pour le module de gestion des vulnérabilités de manière idempotente."""

    existing_quiz = Quiz.query.filter_by(module_id=module_id, title="Quiz Avancé - Gestion des Vulnérabilités").first()
    
    if existing_quiz:
        # Vérifier si le quiz existant a déjà des questions
        question_count = Question.query.filter_by(quiz_id=existing_quiz.id).count()
        if question_count > 0:
            print(f"Quiz 'Quiz Avancé - Gestion des Vulnérabilités' for module {module_id} already exists with {question_count} questions.")
            return
        print(f"Quiz 'Quiz Avancé - Gestion des Vulnérabilités' for module {module_id} exists but has no questions. Adding questions...")
        quiz = existing_quiz
    else:
        print(f"Creating new quiz 'Quiz Avancé - Gestion des Vulnérabilités' for module {module_id}...")
    
    quiz = Quiz(
        module_id=module_id,
        title="Quiz Avancé - Gestion des Vulnérabilités",
        description="Évaluez votre maîtrise de l'identification, évaluation et correction des vulnérabilités de sécurité.",
        passing_score=75  # Higher passing score for advanced content
    )
    db.session.add(quiz)
    db.session.commit() # Commit quiz to get its ID
    
    questions_data = [
        {
            "content": "Quelle est la première étape dans un processus de gestion des vulnérabilités ?",
            "explanation": "L'identification et l'inventaire des actifs est la première étape essentielle car on ne peut pas protéger ce qu'on ne connaît pas. Il faut d'abord savoir quels systèmes, applications et équipements composent l'infrastructure.",
            "choices": [
                {"content": "Identification et inventaire des actifs", "is_correct": True},
                {"content": "Correction immédiate des vulnérabilités", "is_correct": False},
                {"content": "Évaluation des risques", "is_correct": False},
                {"content": "Documentation des incidents", "is_correct": False}
            ]
        },
        {
            "content": "Selon l'échelle CVSS, quel score correspond à une vulnérabilité critique ?",
            "explanation": "L'échelle CVSS (Common Vulnerability Scoring System) classe les vulnérabilités de 0.0 à 10.0. Un score de 9.0 à 10.0 correspond à une vulnérabilité critique nécessitant une correction immédiate.",
            "choices": [
                {"content": "9.0 - 10.0", "is_correct": True},
                {"content": "7.0 - 8.9", "is_correct": False},
                {"content": "4.0 - 6.9", "is_correct": False},
                {"content": "0.0 - 3.9", "is_correct": False}
            ]
        },
        {
            "content": "Qu'est-ce qu'une vulnérabilité zero-day ?",
            "explanation": "Une vulnérabilité zero-day est une faille de sécurité qui n'est pas encore connue du fabricant ou pour laquelle aucun correctif n'a encore été publié, ce qui la rend particulièrement dangereuse car elle peut être exploitée sans défense.",
            "choices": [
                {"content": "Une faille de sécurité exploitée avant qu'un correctif soit disponible", "is_correct": True},
                {"content": "Une vulnérabilité découverte le premier jour du mois", "is_correct": False},
                {"content": "Une faille qui n'affecte que les nouveaux systèmes", "is_correct": False},
                {"content": "Un test de pénétration effectué sans autorisation", "is_correct": False}
            ]
        },
        {
            "content": "Quel est le délai recommandé pour corriger une vulnérabilité critique (CVSS 9.0-10.0) ?",
            "explanation": "Les vulnérabilités critiques représentent un risque immédiat et doivent être corrigées dans les 24 à 48 heures maximum pour éviter une exploitation potentielle.",
            "choices": [
                {"content": "24-48 heures", "is_correct": True},
                {"content": "7 jours", "is_correct": False},
                {"content": "30 jours", "is_correct": False},
                {"content": "90 jours", "is_correct": False}
            ]
        },
        {
            "content": "Lequel de ces outils N'est PAS utilisé pour la détection automatisée des vulnérabilités ?",
            "explanation": "Wireshark est un analyseur de protocoles réseau utilisé pour capturer et analyser le trafic réseau, pas pour scanner les vulnérabilités. Les autres outils mentionnés sont spécifiquement conçus pour la détection de vulnérabilités.",
            "choices": [
                {"content": "Wireshark", "is_correct": True},
                {"content": "Nessus", "is_correct": False},
                {"content": "OpenVAS", "is_correct": False},
                {"content": "Qualys VMDR", "is_correct": False}
            ]
        },
        {
            "content": "Quelle méthode de correction N'est PAS appropriée pour traiter les vulnérabilités ?",
            "explanation": "Ignorer les vulnérabilités en espérant qu'elles ne seront pas exploitées n'est jamais une stratégie acceptable. Toute vulnérabilité identifiée doit être traitée par correction, compensation ou acceptation formelle du risque.",
            "choices": [
                {"content": "Ignorer la vulnérabilité en espérant qu'elle ne sera pas exploitée", "is_correct": True},
                {"content": "Appliquer un patch de sécurité", "is_correct": False},
                {"content": "Mettre en place des contrôles compensatoires", "is_correct": False},
                {"content": "Reconfigurer le système pour éliminer la faille", "is_correct": False}
            ]
        },
        {
            "content": "Que signifie CVE dans le contexte de la sécurité informatique ?",
            "explanation": "CVE (Common Vulnerabilities and Exposures) est un système de référencement standardisé qui attribue des identifiants uniques aux vulnérabilités de sécurité connues, facilitant le partage d'informations entre organisations.",
            "choices": [
                {"content": "Common Vulnerabilities and Exposures", "is_correct": True},
                {"content": "Computer Virus Elimination", "is_correct": False},
                {"content": "Critical Vulnerability Examination", "is_correct": False},
                {"content": "Corporate Verification Environment", "is_correct": False}
            ]
        },
        {
            "content": "Quelle est la différence principale entre un scan de vulnérabilités et un test de pénétration ?",
            "explanation": "Un scan de vulnérabilités identifie automatiquement les failles potentielles, tandis qu'un test de pénétration va plus loin en tentant activement d'exploiter ces vulnérabilités pour démontrer leur impact réel.",
            "choices": [
                {"content": "Le scan identifie les vulnérabilités, le test de pénétration les exploite", "is_correct": True},
                {"content": "Le scan est manuel, le test de pénétration est automatisé", "is_correct": False},
                {"content": "Le scan est plus dangereux que le test de pénétration", "is_correct": False},
                {"content": "Il n'y a aucune différence entre les deux", "is_correct": False}
            ]
        },
        {
            "content": "Dans quel ordre doit-on prioriser la correction des vulnérabilités ?",
            "explanation": "La priorisation doit d'abord considérer la criticité (score CVSS), puis l'impact sur les activités métier, car une vulnérabilité critique sur un système non critique peut être moins prioritaire qu'une vulnérabilité moyenne sur un système vital.",
            "choices": [
                {"content": "Criticité CVSS puis impact métier", "is_correct": True},
                {"content": "Impact métier puis criticité CVSS", "is_correct": False},
                {"content": "Date de découverte puis criticité", "is_correct": False},
                {"content": "Facilité de correction puis impact", "is_correct": False}
            ]
        },
        {
            "content": "Quelle pratique est essentielle après avoir corrigé une vulnérabilité ?",
            "explanation": "Après avoir appliqué une correction, il est essentiel de vérifier que la vulnérabilité a effectivement été éliminée et que la correction n'a pas introduit de nouveaux problèmes ou dysfonctionnements.",
            "choices": [
                {"content": "Vérifier que la correction a bien éliminé la vulnérabilité", "is_correct": True},
                {"content": "Attendre 30 jours avant de tester", "is_correct": False},
                {"content": "Redémarrer tous les systèmes", "is_correct": False},
                {"content": "Changer tous les mots de passe", "is_correct": False}
            ]
        }
    ]
        
    for q_idx, q_data in enumerate(questions_data):
        question = Question(
            quiz_id=quiz.id,
            content=q_data["content"],
            explanation=q_data["explanation"],
            type="multiple_choice"
        )
        db.session.add(question)
        db.session.commit() # Commit question to get its ID
        
        for c_data in q_data["choices"]:
            choice = Choice(
                question_id=question.id,
                content=c_data["content"],
                is_correct=c_data["is_correct"]
            )
            db.session.add(choice)
        db.session.commit() # Commit choices for the current question
        
    print(f"Quiz pour le module {module_id} (Gestion des vulnérabilités) créé avec {len(questions_data)} questions.")

def create_password_quiz(module_id):
    """Crée le quiz pour le module de gestion des mots de passe de manière idempotente."""

    existing_quiz = Quiz.query.filter_by(module_id=module_id, title="Quiz sur la gestion des mots de passe").first()
    if existing_quiz:
        print(f"Quiz 'Quiz sur la gestion des mots de passe' for module {module_id} already exists.")
        return
    
    # Créer le quiz
    quiz = Quiz(
        module_id=module_id,
        title="Quiz sur la gestion des mots de passe",
        description="Testez vos connaissances sur les bonnes pratiques de gestion des mots de passe.",
        passing_score=80
    )
    
    db.session.add(quiz)
    db.session.commit()
    
    # Questions et réponses
    questions_data = [
        {
            "content": "Laquelle de ces pratiques renforce le plus la sécurité de vos mots de passe?",
            "explanation": "Un gestionnaire de mots de passe vous permet de générer et stocker des mots de passe uniques et complexes pour chaque compte.",
            "choices": [
                {"content": "Utiliser le même mot de passe pour tous vos comptes professionnels", "is_correct": False},
                {"content": "Changer votre mot de passe tous les jours", "is_correct": False},
                {"content": "Utiliser un gestionnaire de mots de passe pour générer et stocker des mots de passe uniques", "is_correct": True},
                {"content": "Noter vos mots de passe dans un document sur votre ordinateur", "is_correct": False}
            ]
        },
        {
            "content": "Quelle est la longueur minimale recommandée pour un mot de passe sécurisé?",
            "explanation": "Plus un mot de passe est long, plus il est difficile à craquer par force brute.",
            "choices": [
                {"content": "8 caractères", "is_correct": False},
                {"content": "10 caractères", "is_correct": False},
                {"content": "12 caractères", "is_correct": True},
                {"content": "6 caractères", "is_correct": False}
            ]
        },
        {
            "content": "Parmi ces mots de passe, lequel est le plus sécurisé?",
            "explanation": "Ce mot de passe est le plus sécurisé car il contient des majuscules, des minuscules, des chiffres et des caractères spéciaux, et il est suffisamment long.",
            "choices": [
                {"content": "TangerAlliance2025", "is_correct": False},
                {"content": "password123", "is_correct": False},
                {"content": "P0rt@l!4nc3_S3cur3#75", "is_correct": True},
                {"content": "11111111", "is_correct": False}
            ]
        },
        {
            "content": "Qu'est-ce que l'authentification à deux facteurs (2FA)?",
            "explanation": "L'authentification à deux facteurs combine deux éléments différents pour vérifier votre identité, généralement quelque chose que vous savez (mot de passe) et quelque chose que vous possédez (téléphone).",
            "choices": [
                {"content": "Utiliser deux mots de passe différents pour se connecter", "is_correct": False},
                {"content": "Une méthode qui combine deux éléments différents pour vérifier votre identité", "is_correct": True},
                {"content": "Se connecter à deux comptes en même temps", "is_correct": False},
                {"content": "Demander à deux personnes d'autoriser la connexion", "is_correct": False}
            ]
        },
        {
            "content": "Quelle est la méthode d'authentification à deux facteurs la plus sécurisée parmi les suivantes?",
            "explanation": "Les clés de sécurité physiques offrent une protection supérieure contre le phishing et ne peuvent pas être interceptées comme les SMS ou les emails.",
            "choices": [
                {"content": "Code par SMS", "is_correct": False},
                {"content": "Email de confirmation", "is_correct": False},
                {"content": "Clé de sécurité physique (YubiKey, Google Titan)", "is_correct": True},
                {"content": "Question de sécurité", "is_correct": False}
            ]
        },
        {
            "content": "Selon la politique de Tanger Alliance, quelle est la fréquence de changement de mot de passe requise pour les comptes standard?",
            "explanation": "La politique de Tanger Alliance exige que les mots de passe des comptes standard soient changés tous les 90 jours.",
            "choices": [
                {"content": "Tous les 30 jours", "is_correct": False},
                {"content": "Tous les 60 jours", "is_correct": False},
                {"content": "Tous les 90 jours", "is_correct": True},
                {"content": "Une fois par an", "is_correct": False}
            ]
        },
        {
            "content": "Que devez-vous faire si vous soupçonnez que votre mot de passe a été compromis?",
            "explanation": "En cas de suspicion de compromission, il est crucial de changer immédiatement le mot de passe et d'alerter l'équipe IT pour qu'elle puisse surveiller toute activité suspecte.",
            "choices": [
                {"content": "Attendre la prochaine période de changement obligatoire", "is_correct": False},
                {"content": "Le changer immédiatement et contacter l'équipe de sécurité IT", "is_correct": True},
                {"content": "Simplement ajouter un caractère à votre mot de passe actuel", "is_correct": False},
                {"content": "Partager votre préoccupation avec vos collègues uniquement", "is_correct": False}
            ]
        },
        {
            "content": "Quels comptes chez Tanger Alliance nécessitent obligatoirement l'authentification à deux facteurs?",
            "explanation": "La politique de sécurité de Tanger Alliance impose l'utilisation de l'authentification à deux facteurs pour tous les comptes privilégiés et systèmes critiques.",
            "choices": [
                {"content": "Uniquement les comptes administrateur", "is_correct": False},
                {"content": "Aucun compte", "is_correct": False},
                {"content": "Tous les comptes standard", "is_correct": False},
                {"content": "Les comptes administrateur, accès aux systèmes portuaires, VPN et messagerie", "is_correct": True}
            ]
        },
        {
            "content": "Quel avantage principal offre un gestionnaire de mots de passe?",
            "explanation": "L'avantage principal d'un gestionnaire de mots de passe est qu'il vous permet de gérer facilement des mots de passe uniques et complexes pour chaque compte.",
            "choices": [
                {"content": "Il empêche les attaques de phishing", "is_correct": False},
                {"content": "Il permet d'utiliser le même mot de passe partout", "is_correct": False},
                {"content": "Il permet de gérer des mots de passe uniques et complexes pour chaque compte", "is_correct": True},
                {"content": "Il rend les mots de passe plus courts et faciles à mémoriser", "is_correct": False}
            ]
        },
        {
            "content": "Que se passe-t-il après trop de tentatives échouées de connexion à un compte chez Tanger Alliance?",
            "explanation": "Pour protéger contre les attaques par force brute, le compte est verrouillé après trop de tentatives et nécessite l'intervention du support IT pour être débloqué.",
            "choices": [
                {"content": "Le compte est automatiquement supprimé", "is_correct": False},
                {"content": "Le compte est verrouillé et nécessite l'intervention du support IT", "is_correct": True},
                {"content": "Un indice de mot de passe est automatiquement envoyé", "is_correct": False},
                {"content": "Rien ne se passe, on peut continuer d'essayer", "is_correct": False}
            ]
        }
    ]
    
    # Ajouter les questions et les choix
    for q_data in questions_data:
        question = Question(
            quiz_id=quiz.id,
            content=q_data["content"],
            explanation=q_data["explanation"],
            type="multiple_choice"
        )
        db.session.add(question)
        db.session.commit()
        
        for c_data in q_data["choices"]:
            choice = Choice(
                question_id=question.id,
                content=c_data["content"],
                is_correct=c_data["is_correct"]
            )
            db.session.add(choice)
        
    db.session.commit()
    print(f"Quiz pour le module de gestion des vulnérabilités créé/mis à jour avec {len(questions_data)} questions.")


def seed_quiz_for_module_4():
    """Crée le quiz pour le module 'Protection des données sensibles'."""
    module_pds = Module.query.filter_by(order=4).first()
    if not module_pds:
        print("Module 'Protection des données sensibles' (order=4) non trouvé. Quiz non créé.")
        return

    quiz_title = "Quiz Avancé - Protection des Données Sensibles"
    quiz_description = "Évaluez vos compétences en protection des données sensibles dans l'environnement portuaire de Tanger Alliance."
    
    existing_quiz = Quiz.query.filter_by(module_id=module_pds.id).first()
    if existing_quiz:
        print(f"Quiz '{quiz_title}' pour le module '{module_pds.title}' existe déjà. Vérification des questions.")
        quiz = existing_quiz
    else:
        quiz = Quiz(
            module_id=module_pds.id,
            title=quiz_title,
            description=quiz_description,
            passing_score=75
        )
        db.session.add(quiz)
        db.session.commit() # Commit ici pour que quiz.id soit disponible
        print(f"Quiz '{quiz_title}' créé pour le module '{module_pds.title}'.")

    questions_data = [
        {
            "content": "Parmi les exemples suivants, lequel est généralement considéré comme une donnée sensible dans un contexte portuaire ?",
            "explanation": "Les données sensibles incluent des informations dont la divulgation non autorisée pourrait nuire à l'entreprise ou à des individus. Les manifestes de cargaison contiennent des détails critiques.",
            "choices": [
                {"content": "Le menu de la cantine de la semaine", "is_correct": False},
                {"content": "Les manifestes de cargaison détaillés", "is_correct": True},
                {"content": "Les horaires des navettes pour employés", "is_correct": False},
                {"content": "Le nombre de visiteurs quotidiens du portail web public", "is_correct": False}
            ]
        },
        {
            "content": "Que signifie le principe du 'besoin d'en connaître' (Need-to-know) en matière de protection des données ?",
            "explanation": "Ce principe fondamental vise à limiter l'accès aux informations sensibles uniquement aux personnes dont les fonctions exigent cet accès.",
            "choices": [
                {"content": "Toutes les données doivent être connues de la direction.", "is_correct": False},
                {"content": "Les employés ne doivent accéder qu'aux données strictement nécessaires à l'accomplissement de leurs tâches.", "is_correct": True},
                {"content": "Il faut connaître toutes les lois sur la protection des données.", "is_correct": False},
                {"content": "Les employés peuvent partager librement les informations avec leurs collègues.", "is_correct": False}
            ]
        },
        {
            "content": "Quelle est une bonne pratique essentielle lors du partage d'informations sensibles par email ?",
            "explanation": "Le chiffrement protège le contenu de l'email contre l'interception par des tiers non autorisés.",
            "choices": [
                {"content": "Envoyer l'email à une large liste de diffusion pour s'assurer que la bonne personne le reçoive.", "is_correct": False},
                {"content": "Utiliser un objet d'email très vague comme 'Info'.", "is_correct": False},
                {"content": "Chiffrer l'email et/ou les pièces jointes sensibles.", "is_correct": True},
                {"content": "Stocker les emails sensibles dans le dossier 'Éléments envoyés' pendant plusieurs années.", "is_correct": False}
            ]
        },
        {
            "content": "Quelle réglementation européenne est primordiale pour la protection des données personnelles des individus au sein de l'Union Européenne ?",
            "explanation": "Le RGPD (Règlement Général sur la Protection des Données) est le cadre légal principal pour la protection des données dans l'UE.",
            "choices": [
                {"content": "La loi Sarbanes-Oxley (SOX)", "is_correct": False},
                {"content": "Le Règlement Général sur la Protection des Données (RGPD)", "is_correct": True},
                {"content": "La norme ISO 27001", "is_correct": False},
                {"content": "La loi marocaine 09-08", "is_correct": False}
            ]
        },
        {
            "content": "Le principe de 'minimisation des données' implique que Tanger Alliance doit :",
            "explanation": "La minimisation des données signifie ne collecter, traiter et conserver que les données absolument nécessaires pour une finalité spécifique.",
            "choices": [
                {"content": "Collecter le maximum de données possibles pour anticiper les besoins futurs.", "is_correct": False},
                {"content": "Conserver toutes les données indéfiniment, au cas où.", "is_correct": False},
                {"content": "Collecter et traiter uniquement les données strictement nécessaires à la finalité poursuivie.", "is_correct": True},
                {"content": "Rendre toutes les données anonymes pour minimiser les risques.", "is_correct": False}
            ]
        },
        {
            "content": "Dans le contexte portuaire de Tanger Alliance, quelle information parmi les suivantes ne serait PAS typiquement classée comme donnée sensible nécessitant une protection élevée ?",
            "explanation": "Les plans d'évacuation incendie sont souvent publics pour la sécurité, tandis que les autres options représentent des informations critiques ou personnelles.",
            "choices": [
                {"content": "Le plan d'évacuation incendie affiché publiquement dans les bureaux", "is_correct": True},
                {"content": "Les détails financiers confidentiels des contrats avec les principaux clients", "is_correct": False},
                {"content": "Les listes de passagers et de membres d'équipage des navires accostant", "is_correct": False},
                {"content": "Les codes d'accès aux systèmes de surveillance et de contrôle du port", "is_correct": False}
            ]
        },
        {
            "content": "Le principe de 'limitation de la finalité' signifie que les données collectées pour une raison spécifique (par exemple, la gestion des expéditions) :",
            "explanation": "Ce principe clé de la protection des données assure que les données ne sont utilisées que pour les raisons pour lesquelles elles ont été initialement recueillies, sauf exceptions légales ou consentement.",
            "choices": [
                {"content": "Ne doivent pas être utilisées pour une autre finalité incompatible sans consentement explicite ou base légale claire.", "is_correct": True},
                {"content": "Peuvent être librement partagées avec tous les départements de Tanger Alliance.", "is_correct": False},
                {"content": "Doivent être supprimées immédiatement après leur utilisation initiale, même si une conservation légale est requise.", "is_correct": False},
                {"content": "Sont la propriété de la personne qui les a collectées et peuvent être utilisées à sa discrétion.", "is_correct": False}
            ]
        },
        {
            "content": "Lors de l'utilisation d'un réseau Wi-Fi public (ex: café, aéroport) pour accéder à des informations professionnelles de Tanger Alliance :",
            "explanation": "Les réseaux Wi-Fi publics sont intrinsèquement non sécurisés. Un VPN chiffre votre trafic, le protégeant des interceptions.",
            "choices": [
                {"content": "Il est fortement recommandé d'utiliser un VPN (Virtual Private Network) fourni ou approuvé par Tanger Alliance pour chiffrer la connexion.", "is_correct": True},
                {"content": "Il est sécurisé tant que le site web consulté utilise HTTPS.", "is_correct": False},
                {"content": "Il faut uniquement consulter des emails non sensibles et éviter les pièces jointes.", "is_correct": False},
                {"content": "C'est acceptable pour de courtes périodes si personne ne semble regarder votre écran.", "is_correct": False}
            ]
        },
        {
            "content": "Selon la loi marocaine 09-08, qui est l'autorité principale chargée de veiller à la protection des données à caractère personnel au Maroc ?",
            "explanation": "La CNDP est l'organisme officiel marocain dédié à la protection des données personnelles.",
            "choices": [
                {"content": "La CNDP (Commission Nationale de contrôle de la protection des Données à caractère Personnel)", "is_correct": True},
                {"content": "L'ANRT (Agence Nationale de Réglementation des Télécommunications)", "is_correct": False},
                {"content": "Le Ministère de l'Industrie et du Commerce", "is_correct": False},
                {"content": "La Direction Générale de la Sûreté Nationale (DGSN)", "is_correct": False}
            ]
        },
        {
            "content": "Qui est principalement responsable de la protection des données sensibles chez Tanger Alliance au quotidien ?",
            "explanation": "Bien que les départements spécialisés et la direction aient des rôles clés, la protection des données est une responsabilité partagée par tous les employés.",
            "choices": [
                {"content": "Chaque employé qui manipule, traite ou a accès à des données sensibles dans le cadre de ses fonctions.", "is_correct": True},
                {"content": "Uniquement le département IT et le Responsable de la Sécurité des Systèmes d'Information (RSSI).", "is_correct": False},
                {"content": "Uniquement la direction générale et les chefs de département.", "is_correct": False},
                {"content": "Les auditeurs externes lors de leurs contrôles périodiques.", "is_correct": False}
            ]
        }
    ]
    
    existing_question_contents = [q.content for q in Question.query.filter_by(quiz_id=quiz.id).all()]
    questions_added_count = 0

    for q_data in questions_data:
        if q_data["content"] not in existing_question_contents:
            question = Question(
                quiz_id=quiz.id,
                content=q_data["content"],
                explanation=q_data["explanation"],
                type="multiple_choice"
            )
            db.session.add(question)
            db.session.flush()

            for c_data in q_data["choices"]:
                choice = Choice(
                    question_id=question.id,
                    content=c_data["content"],
                    is_correct=c_data["is_correct"]
                )
                db.session.add(choice)
            questions_added_count += 1
            existing_question_contents.append(q_data["content"])
        
    db.session.commit()
    if questions_added_count > 0:
        print(f"{questions_added_count} nouvelles questions ajoutées au quiz '{quiz.title}'.")
    else:
        print(f"Aucune nouvelle question ajoutée au quiz '{quiz.title}'.")


def seed_badges():
    """Ajoute les badges à la base de données de manière idempotente."""
    badge_definitions = [
        {
            "module_id": 1, "name": "Gardien des Secrets",
            "description": "Maîtrise l'art de créer et gérer des mots de passe inviolables.",
            "image_filename": "password_guardian.png"
        },
        {
            "module_id": 2, "name": "Détective Anti-Phishing",
            "description": "Expert en identification et neutralisation des tentatives de phishing.",
            "image_filename": "phishing_detective.png"
        },
        {
            "module_id": 3, "name": "Sentinelle des Failles",
            "description": "Vigilant protecteur contre les vulnérabilités et menaces.",
            "image_filename": "vulnerability_sentinel.png"
        },
        {
            "module_id": 4, "name": "Protecteur de Données",
            "description": "Champion de la confidentialité et de la protection des données sensibles.",
            "image_filename": "data_protector.png"
        },
        {
            "module_id": 5, "name": "Expert Sécurité Mobile",
            "description": "Maître de la sécurisation des appareils mobiles et applications professionnelles.",
            "image_filename": "securit_mobile.png"
        },
        {
            "module_id": 6, "name": "Gardien des Réseaux",
            "description": "Protecteur expert de l'infrastructure réseau et des communications sécurisées.",
            "image_filename": "securite_reseaux.png"
        }
    ]

    newly_created_count = 0

    for badge_data in badge_definitions:
        existing_badge = Badge.query.filter_by(module_id=badge_data["module_id"]).first()
        if not existing_badge:
            badge = Badge(
                module_id=badge_data["module_id"],
                name=badge_data["name"],
                description=badge_data["description"],
                image_filename=badge_data["image_filename"]
            )
            db.session.add(badge)
            newly_created_count += 1
    
    if newly_created_count > 0:
        db.session.commit()
        print(f"{newly_created_count} nouveaux badges ajoutés à la base de données.")
    else:
        print("Aucun nouveau badge ajouté. Les badges existants ont été trouvés.")


def create_mobile_security_quiz(module_id):
    """Crée le quiz pour le module de sécurité mobile"""
    
    # Vérifier si le quiz existe déjà
    existing_quiz = Quiz.query.filter_by(module_id=module_id).first()
    if existing_quiz:
        print(f"Quiz pour le module {module_id} (Sécurité mobile) existe déjà.")
        return
    
    quiz = Quiz(
        module_id=module_id,
        title="Quiz - Sécurité mobile",
        description="Testez vos connaissances sur la sécurité des appareils mobiles",
        passing_score=70
    )
    db.session.add(quiz)
    db.session.flush()  # Pour obtenir l'ID du quiz
    
    questions_data = [
        {
            "content": "Quelle est la première mesure de sécurité à prendre sur un appareil mobile professionnel ?",
            "explanation": "Le verrouillage par code PIN/mot de passe/biométrie est la première ligne de défense contre l'accès non autorisé.",
            "choices": [
                {"content": "Installer un antivirus", "is_correct": False},
                {"content": "Configurer un verrouillage par code PIN/mot de passe", "is_correct": True},
                {"content": "Désactiver le WiFi", "is_correct": False},
                {"content": "Supprimer toutes les applications", "is_correct": False}
            ]
        },
        {
            "content": "Que devez-vous faire avant d'installer une application professionnelle ?",
            "explanation": "Il est essentiel de vérifier que l'application provient d'une source officielle et approuvée par l'entreprise.",
            "choices": [
                {"content": "L'installer immédiatement", "is_correct": False},
                {"content": "Vérifier qu'elle provient d'une source officielle", "is_correct": True},
                {"content": "Demander à un collègue", "is_correct": False},
                {"content": "La télécharger depuis n'importe quel site", "is_correct": False}
            ]
        },
        {
            "content": "Quelle est la meilleure pratique pour les mises à jour d'applications mobiles ?",
            "explanation": "Les mises à jour automatiques garantissent que les derniers correctifs de sécurité sont appliqués rapidement.",
            "choices": [
                {"content": "Ne jamais mettre à jour", "is_correct": False},
                {"content": "Mettre à jour seulement une fois par an", "is_correct": False},
                {"content": "Activer les mises à jour automatiques", "is_correct": True},
                {"content": "Attendre que l'application ne fonctionne plus", "is_correct": False}
            ]
        },
        {
            "content": "Comment protéger les données sensibles sur un appareil mobile ?",
            "explanation": "Le chiffrement des données garantit que même en cas de vol, les informations restent inaccessibles.",
            "choices": [
                {"content": "Les stocker en texte brut", "is_correct": False},
                {"content": "Utiliser le chiffrement des données", "is_correct": True},
                {"content": "Les partager par email", "is_correct": False},
                {"content": "Les sauvegarder sur une clé USB", "is_correct": False}
            ]
        },
        {
            "content": "Que faire si votre appareil mobile professionnel est perdu ou volé ?",
            "explanation": "L'effacement à distance empêche l'accès aux données sensibles de l'entreprise.",
            "choices": [
                {"content": "Attendre qu'il réapparaisse", "is_correct": False},
                {"content": "Signaler immédiatement et demander l'effacement à distance", "is_correct": True},
                {"content": "Changer tous ses mots de passe personnels", "is_correct": False},
                {"content": "Acheter un nouvel appareil", "is_correct": False}
            ]
        }
    ]
    
    for i, q_data in enumerate(questions_data, 1):
        question = Question(
            quiz_id=quiz.id,
            content=q_data["content"],
            explanation=q_data["explanation"]
        )
        db.session.add(question)
        db.session.flush()
        
        for j, choice_data in enumerate(q_data["choices"], 1):
            choice = Choice(
                question_id=question.id,
                content=choice_data["content"],
                is_correct=choice_data["is_correct"]
            )
            db.session.add(choice)
    
    db.session.commit()
    print(f"Quiz de sécurité mobile créé pour le module {module_id}")

def create_network_security_quiz(module_id):
    """Crée le quiz pour le module de sécurité réseau"""
    
    # Vérifier si le quiz existe déjà
    existing_quiz = Quiz.query.filter_by(module_id=module_id).first()
    if existing_quiz:
        print(f"Quiz pour le module {module_id} (Sécurité réseau) existe déjà.")
        return
    
    quiz = Quiz(
        module_id=module_id,
        title="Quiz - Sécurité réseau",
        description="Testez vos connaissances sur la sécurité des réseaux",
        passing_score=70
    )
    db.session.add(quiz)
    db.session.flush()  # Pour obtenir l'ID du quiz
    
    questions_data = [
        {
            "content": "Quel est le rôle principal d'un pare-feu (firewall) ?",
            "explanation": "Un pare-feu contrôle le trafic réseau entrant et sortant selon des règles de sécurité prédéfinies.",
            "choices": [
                {"content": "Accélérer la connexion internet", "is_correct": False},
                {"content": "Contrôler le trafic réseau selon des règles de sécurité", "is_correct": True},
                {"content": "Stocker les mots de passe", "is_correct": False},
                {"content": "Gérer les emails", "is_correct": False}
            ]
        },
        {
            "content": "Qu'est-ce qu'une attaque par déni de service (DDoS) ?",
            "explanation": "Une attaque DDoS vise à rendre un service indisponible en le surchargeant de requêtes.",
            "choices": [
                {"content": "Vol de mots de passe", "is_correct": False},
                {"content": "Surcharge d'un service pour le rendre indisponible", "is_correct": True},
                {"content": "Installation de logiciels malveillants", "is_correct": False},
                {"content": "Écoute des communications", "is_correct": False}
            ]
        },
        {
            "content": "Pourquoi utiliser un VPN (Virtual Private Network) ?",
            "explanation": "Un VPN chiffre les communications et masque l'adresse IP pour sécuriser les connexions.",
            "choices": [
                {"content": "Pour accélérer internet", "is_correct": False},
                {"content": "Pour chiffrer les communications et masquer l'IP", "is_correct": True},
                {"content": "Pour bloquer les publicités", "is_correct": False},
                {"content": "Pour économiser de la bande passante", "is_correct": False}
            ]
        },
        {
            "content": "Qu'est-ce que le protocole HTTPS ?",
            "explanation": "HTTPS est la version sécurisée de HTTP qui chiffre les données échangées entre le navigateur et le serveur.",
            "choices": [
                {"content": "Un protocole de messagerie", "is_correct": False},
                {"content": "HTTP sécurisé avec chiffrement SSL/TLS", "is_correct": True},
                {"content": "Un système de fichiers", "is_correct": False},
                {"content": "Un protocole de transfert de fichiers", "is_correct": False}
            ]
        },
        {
            "content": "Quelle est la meilleure pratique pour sécuriser un réseau WiFi d'entreprise ?",
            "explanation": "WPA3 est le protocole de sécurité WiFi le plus récent et le plus sécurisé.",
            "choices": [
                {"content": "Utiliser WEP", "is_correct": False},
                {"content": "Laisser le réseau ouvert", "is_correct": False},
                {"content": "Utiliser WPA3 avec un mot de passe fort", "is_correct": True},
                {"content": "Cacher le nom du réseau seulement", "is_correct": False}
            ]
        }
    ]
    
    for i, q_data in enumerate(questions_data, 1):
        question = Question(
            quiz_id=quiz.id,
            content=q_data["content"],
            explanation=q_data["explanation"]
        )
        db.session.add(question)
        db.session.flush()
        
        for j, choice_data in enumerate(q_data["choices"], 1):
            choice = Choice(
                question_id=question.id,
                content=choice_data["content"],
                is_correct=choice_data["is_correct"]
            )
            db.session.add(choice)
    
    db.session.commit()
    print(f"Quiz de sécurité réseau créé pour le module {module_id}")

def create_admin_user():
    """Crée un utilisateur administrateur si aucun n'existe"""
    
    # Vérifier si un admin existe déjà
    if User.query.filter_by(role='admin').first():
        print("Un administrateur existe déjà dans la base de données.")
        return
    
    # Créer un nouvel administrateur
    from app import bcrypt
    admin_password = os.environ.get('TANGER_ADMIN_PASSWORD')
    if not admin_password:
        raise RuntimeError(
            "La variable d'environnement TANGER_ADMIN_PASSWORD doit être définie "
            "avant l'initialisation du compte administrateur."
        )
    hashed_password = bcrypt.generate_password_hash(admin_password).decode('utf-8')
    
    admin = User(
        email='admin@tangeralliance.com',
        password=hashed_password,
        role='admin',
        department='IT Security',
        created_at=datetime.now(timezone.utc)
    )
    
    db.session.add(admin)
    db.session.commit()
    print("Utilisateur administrateur créé avec succès.")

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
        create_admin_user()
        seed_modules()
        # Appeler les fonctions de seeding pour les quiz après la création des modules
        # Assurez-vous que seed_quiz_for_module_1() et seed_quiz_for_module_3() sont définies et appelées si elles existent.
        # Exemple : 
        # if callable(globals().get('seed_quiz_for_module_1')):
        #     seed_quiz_for_module_1()
        # if callable(globals().get('seed_quiz_for_module_3')):
        #     seed_quiz_for_module_3()
        seed_quiz_for_module_4() # Ajout pour le nouveau module
        seed_badges()
        print("Initialisation de la base de données terminée.")
