from flask import Blueprint, flash, render_template, request, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import  login_required,  current_user
from .models import Commutateurs, Imprimantes, Licences, Machines, Marques, Peripheriques, Serveurs, Services, Telephones, Types, Users, Tasks
from . import db, mail
import plotly.express as px
from flask_mail import Message
import random
import string
list = ["GET", "POST", "PUT", "PATCH", "DELETE"]
from datetime import datetime, timedelta


views_admin = Blueprint('views_admin',__name__)

# route pour l'acceuil
@views_admin.route('/')
@login_required
def home():
    total_peripheriques = Peripheriques.query.count()
    total_imprimantes = Imprimantes.query.count()
    total_employes = Users.query.count()
    total_serveurs = Serveurs.query.count()
    total_commutateurs = Commutateurs.query.count()
    total_de_machines = Machines.query.count()
    total_telephones = Telephones.query.count()

    ############################################################################

    # Machine par marque
    comptes_marque = db.session.query(Marques.nom, db.func.count(Machines.id)).join(Machines, Marques.id == Machines.marque_id).group_by(Marques.nom).all()
    marques = []
    comptes = []

    for marque, compte in comptes_marque:
        marques.append(marque)
        comptes.append(compte)

    fig = px.pie(names=marques, values=comptes)
    fig2 = px.bar(x=marques, y=comptes, labels={'x': 'Marque', 'y': 'Nombre de Machines'})

 # Configuration des couleurs
    colors = px.colors.qualitative.Plotly

    fig = px.pie(names=marques, values=comptes, title='Nombre de Machines par Marque', color_discrete_sequence=colors)
    fig2 = px.bar(x=marques, y=comptes, labels={'x': 'Marque', 'y': 'Nombre de Machines'}, title='Nombre de Machines par Marque', color=marques, color_discrete_sequence=colors)

    # Comptage des machines en stock
    machines_en_stock = Machines.query.filter_by(user_id=None).count()
    # Comptage total des machines
    total_machines = Machines.query.count()
    # Comptage des machines allouées
    machines_allouees = total_machines - machines_en_stock
    fig_stock_bar = px.bar(x=['Machines Allouées', 'Machines en Stock'], y=[machines_allouees, machines_en_stock], labels={'x': 'Statut', 'y': 'Nombre de Machines'}, title='Répartition des Machines', color=['Machines Allouées', 'Machines en Stock'], color_discrete_sequence=colors)
    fig_stock_pie = px.pie(names=['Machines Allouées', 'Machines en Stock'], values=[machines_allouees, machines_en_stock], title='Répartition des Machines', color_discrete_sequence=colors)    

    # Comptage du nombre de demandes par utilisateur
    comptes_demandes = db.session.query(Users.nom, db.func.count(Tasks.id)).join(Tasks, Users.id == Tasks.user_id).group_by(Users.nom).all()

    utilisateurs = []
    demandes = []

    for utilisateur, demande in comptes_demandes:
        utilisateurs.append(utilisateur)
        demandes.append(demande)

    fig_demandes = px.bar(x=utilisateurs, y=demandes, labels={'x': 'Utilisateur', 'y': 'Nombre de Demandes'}, title='Nombre de Demandes par Utilisateur')
    fig_demandes_line = px.line(x=utilisateurs, y=demandes, labels={'x': 'Utilisateur', 'y': 'Nombre de Demandes'}, title='Nombre de Demandes par Utilisateur')


    return render_template('admin/home.html', total_peripheriques=total_peripheriques, total_imprimantes=total_imprimantes, total_employes=total_employes, total_serveurs=total_serveurs, total_commutateurs=total_commutateurs, total_de_machines=total_de_machines, total_telephones=total_telephones, plot=fig.to_html(full_html=False), plot2=fig2.to_html(full_html=False), plot_stock_bar=fig_stock_bar.to_html(full_html=False), plot_stock_pie=fig_stock_pie.to_html(full_html=False), total_machines=total_machines, plot_demandes=fig_demandes.to_html(full_html=False), plot_demandes_line=fig_demandes_line.to_html(full_html=False))

# Routes pour la gestion des employés
@views_admin.route("/Créer&des&employés", methods=list)
@login_required
def add_employe():

    def generate_password(length):
        num_letters = length // 3
        num_digits = length // 3
        num_special_chars = length // 3

        # If length is not a multiple of 3, add the remainder to num_letters
        num_letters += length % 3

        password = []
        password.extend(random.choices(string.ascii_letters, k=num_letters))
        password.extend(random.choices(string.digits, k=num_digits))
        password.extend(random.choices(string.punctuation, k=num_special_chars))

        random.shuffle(password)

        return ''.join(password)

    if request.method == "GET":
        service = Services.query.all()
        return render_template("admin/add_profil.html", data = service)
    else: 
        nom = request.form.get("nom")
        prenom = request.form.get("prenom")
        nom_utilisateur = request.form.get("nom_utilisateur")
        email=  request.form.get("email")
        mot_de_passe = generate_password(9)
        print(mot_de_passe)
        service_id = request.form.get("service")
        
        user = Users.query.filter_by(email=email).first()
        user2 = Users.query.filter_by(nom_utilisateur = nom_utilisateur).first()
        if user or user2: 
            flash("Email or Username already exist", category="error")
            return redirect(url_for("views_admin.add_employe"))
        elif len(email) < 4 :
            flash("Email trop court", category="error")
            return redirect(url_for("views_admin.add_employe"))
        elif len(nom_utilisateur) < 4 :
            flash("Le nom utilisateur est trop court", category="error")
            return redirect(url_for("views_admin.add_employe"))
        elif len(nom) < 4 : 
            flash("Nom trop court.", category="error")
            return redirect(url_for("views_admin.add_employe"))
        elif len(prenom) < 4 : 
            flash("Prenom trop court", category="error")
            return redirect(url_for("views_admin.add_employe"))
        elif len(mot_de_passe) < 7 :
            flash("le mot de passe doit être de 7 caractère minimum.", category="error")
            return redirect(url_for("views_admin.add_employe"))
        elif "is_validated" in request.form : 
            if "is_admin_request" in request.form :
                new_user = Users(nom = nom, prenom = prenom, nom_utilisateur = nom_utilisateur, email=email,  mot_de_passe = generate_password_hash(mot_de_passe, method="scrypt"), is_admin_request = True, is_validated = True, services_id = service_id)
                # msg = Message('Identifiant de connexion à IT-GTA', sender = 'maestro.master.003@gmail.com', recipients = [new_user.email])
                # msg.body = "Nom utilisateur : "+new_user.nom_utilisateur+"\nMot de passe : "+mot_de_passe
                # mail.send(msg)
                db.session.add(new_user)
                db.session.commit()
                flash("La création d'un profil administrateur actif a réussi", category="success")
                return redirect(url_for("views_admin.employe_list"))
            else: 
                new_user = Users(nom = nom, prenom = prenom, nom_utilisateur = nom_utilisateur, email=email,  mot_de_passe = generate_password_hash(mot_de_passe, method="scrypt"), is_admin_request = False, is_validated = True, services_id = service_id)
                # msg = Message('Identifiant de connexion à IT-GTA', sender = 'maestro.master.003@gmail.com', recipients = [new_user.email])
                # msg.body = "Nom utilisateur : "+new_user.nom_utilisateur+"\nMot de passe : "+mot_de_passe
                # mail.send(msg)
                db.session.add(new_user)
                db.session.commit()
                flash("La création d'un profil utilisateur actif a réussi", category="success")
                return redirect(url_for("views_admin.employe_list"))
        else:
            if "is_admin_request" in request.form :
                new_user = Users(nom = nom, prenom = prenom, nom_utilisateur = nom_utilisateur, email=email,  mot_de_passe = generate_password_hash(mot_de_passe, method="scrypt"), is_admin_request = True, is_validated = False, services_id = service_id)
                # msg = Message('Identifiant de connexion à IT-GTA', sender = 'maestro.master.003@gmail.com', recipients = [new_user.email])
                # msg.body = "Nom utilisateur : "+new_user.nom_utilisateur+"\nMot de passe : "+mot_de_passe
                # mail.send(msg)
                db.session.add(new_user)
                db.session.commit()
                flash("La création d'un profil administrateur actif a réussi", category="success")
                return redirect(url_for("views_admin.employe_list"))
            else: 
                new_user = Users(nom = nom, prenom = prenom, nom_utilisateur = nom_utilisateur, email=email,  mot_de_passe = generate_password_hash(mot_de_passe, method="scrypt"), is_admin_request = False, is_validated = False, services_id = service_id)
                # msg = Message('Identifiant de connexion à IT-GTA', sender = 'maestro.master.003@gmail.com', recipients = [new_user.email])
                # msg.body = "Nom utilisateur : "+new_user.nom_utilisateur+"\nMot de passe : "+mot_de_passe
                # mail.send(msg)
                db.session.add(new_user)
                db.session.commit()
                flash("La création d'un profil utilisateur non actif a réussi", category="success")
                return redirect(url_for("views_admin.employe_list"))

@views_admin.route("/employe&list")
@login_required
def employe_list():
    # data =  Users.query.filter_by(is_admin_request=False).all()
    data = db.session.query(Services, Users).join(Users, Services.id == Users.services_id).all()
    print(data)
    return render_template("admin/liste_employe.html", data = data)

@views_admin.route("/active&employe/<int:id>")
@login_required
def active_employe(id):
    user = Users.query.get(id)
    user.is_validated = True
    db.session.commit()
    flash("Compte utilisateur activé", category="success")
    return redirect(url_for("views_admin.employe_list"))

@views_admin.route("/desactive&employe/<int:id>")
@login_required
def desactive_employe(id):
    user = Users.query.get(id)
    user.is_validated = False
    db.session.commit()
    flash("Compte utilisateur désactivé", category="success")
    return redirect(url_for("views_admin.employe_list"))

@views_admin.route("/employe&ressources&list")
@login_required
def employe_ressources_list():
    data = db.session.query(Users, Machines, Telephones, Services).join(Machines, Machines.user_id == Users.id).outerjoin(Telephones, Telephones.user_id == Users.id).join(Services, Services.id == Users.services_id).all()
    return render_template("admin/employe_ressources_list.html", data = data)

# Routes pour gestion service
@views_admin.route("/add&service", methods=list)
@login_required
def add_service():
    if request.method == "GET":
        return render_template("admin/add_services.html")
    else:
        nom = request.form.get("nom")
        service = Services.query.filter_by(nom=nom).first()
        if service:
            flash("Ce service existe déjà", category="error")
            return redirect(url_for("views_admin.add_service"))
        elif len(nom) < 4 :
            flash("Le nom est trop court", category="error")
            return redirect(url_for("views_admin.add_service"))
        else:
            new_service = Services(nom=nom)
            db.session.add(new_service)
            db.session.commit()
            flash("Service ajouté avec succès", category="success")
            return redirect(url_for("views_admin.service_list"))

@views_admin.route("/services&list")
@login_required
def service_list():
    data = Services.query.all()
    return render_template("admin/service_list.html", data = data)

@views_admin.route("/supprimer&service/<int:id>")
@login_required
def delete_service(id):
    service = Services.query.get(id)
    db.session.delete(service)
    db.session.commit()
    return redirect(url_for("views_admin.service_list"))


@views_admin.route("/modifier&service/<int:id>")
@login_required
def modifier_service(id):
    service = Services.query.get(id)
    if request.method == "GET":
        return render_template("/admin/modifier_service.html")


@views_admin.route("/service&ressources&list")
@login_required
def service_ressources_list():
    data = db.session.query(Services, Machines, Commutateurs, Serveurs, Telephones, Imprimantes).outerjoin(Machines, Machines.service_id == Services.id).outerjoin(Commutateurs, Commutateurs.service_id == Services.id).outerjoin(Serveurs, Serveurs.service_id == Services.id).outerjoin(Telephones, Telephones.service_id == Services.id).outerjoin(Imprimantes, Imprimantes.service_id == Services.id)
    return render_template("admin/service_ressources_list.html", data = data)


# Route pour l'assistance
@views_admin.route("/assistance&en&attente")
@login_required
def wait_assist():
    task_list = db.session.query(Tasks, Users).join(Users, Tasks.user_id == Users.id).filter(Tasks.statut == 0).all() 
    print(task_list)
    return render_template("admin/wait_assist.html", data=task_list)

@views_admin.route("/accept&assist/<int:id>")
@login_required
def accept_assist(id):
    task = Tasks.query.get(id)
    task.statut = 1
    db.session.commit()
    flash ("Demande d'Assistance Accepté!", category="success")
    return redirect (url_for("views_admin.wait_assist"))

@views_admin.route("/refuse&assist/<int:id>")
@login_required
def refuse_assist(id):
    task = Tasks.query.get(id)
    task.statut = 2
    db.session.commit()
    flash ("Demande d'Assistance Refusé!", category="error")
    return redirect (url_for("views_admin.wait_assist"))


@views_admin.route("/liste&assistance&accepte")
@login_required
def accept_assist_list():
    task_list = db.session.query(Tasks, Users).join(Users, Tasks.user_id == Users.id).filter(Tasks.statut == 1).all() 
    return render_template("admin/liste_assist_accept.html", data = task_list)

@views_admin.route("/liste&assistance&refuse")
@login_required
def refuse_assist_list():
    task_list = db.session.query(Tasks, Users).join(Users, Tasks.user_id == Users.id).filter(Tasks.statut == 2).all() 
    return render_template("admin/liste_assist_refuse.html", data = task_list)

#Route pour gerer les types
@views_admin.route('/types', methods = list)
@login_required
def types():
    types = Types.query.all()
    return render_template("admin/type.html", data = types)

@views_admin.route("/add&type", methods = list)
@login_required
def add_type():
        nom = request.form.get("nom")
        type = Types.query.filter_by(nom=nom).first()
        if type:
            flash("Ce type existe déjà", category="error")
            return redirect(url_for("views_admin.types"))
        elif len(nom) < 4 :
            flash("Le nom est trop court", category="error")
            return redirect(url_for("views_admin.types"))
        else:
            nom = nom.upper()
            new_type = Types(nom=nom)
            db.session.add(new_type)
            db.session.commit()
            flash("Nouveau type ajouté avec succès", category="success")
            return redirect(url_for("views_admin.types"))

@views_admin.route("/delete&type/<int:id>", methods=list)
@login_required
def delete_type(id):
    type = Types.query.get(id)
    db.session.delete(type)
    db.session.commit()
    flash("Element supprimé avec succès", category="success")
    return redirect(url_for("views_admin.types"))

@views_admin.route("/update&type/<int:id>", methods=list)
@login_required
def update_type(id):
    if request.method == "GET":
        data = Types.query.get(id)
        return render_template("admin/update&type.html", data = data)
    else : 
        id = request.form.get("id")
        nom = request.form.get("nom")

        if len(nom) < 4:
            flash("Le nom est trop court, quatres(4) caractères minimum", category="error")
            return redirect(url_for("views_admin.types"))
        else:
            lic = Types.query.get(id) 
            lic.nom = nom
            db.session.commit()
            flash("Type mis à jour avec succès", category="success")
            return redirect(url_for("views_admin.types"))
# # Route pour le dashboard
# @views_admin.route("/dashboard")
# @login_required
# def dahboard():

#     return render_template("admin/dashboard.html")

@views_admin.route('/marques', methods = list)
@login_required
def marques():
    data = Marques.query.all()
    return render_template("admin/marque.html", data = data)

@views_admin.route("/add&marque", methods = list)
@login_required
def add_marque():
        nom = request.form.get("nom")
        marque = Marques.query.filter_by(nom=nom).first()
        if marque:
            flash("Cette marque existe déjà", category="error")
            return redirect(url_for("views_admin.marques"))
        elif len(nom) < 1 :
            flash("Le nom est trop court", category="error")
            return redirect(url_for("views_admin.marques"))
        else:
            nom = nom.upper()
            new_marque = Marques(nom=nom)
            db.session.add(new_marque)
            db.session.commit()
            flash("Nouvelle marque ajouté avec succès", category="success")
            return redirect(url_for("views_admin.marques"))

@views_admin.route("/delete&marque/<int:id>", methods=list)
@login_required
def delete_marque(id):
    marque = Marques.query.get(id)
    db.session.delete(marque)
    db.session.commit()
    flash("Element supprimé avec succès", category="success")
    return redirect(url_for("views_admin.marques"))

@views_admin.route("/update&marque/<int:id>", methods=list)
@login_required
def update_marque(id):
    if request.method == "GET":
        data = Marques.query.get(id)
        return render_template("admin/update&marque.html", data = data)
    else : 
        id = request.form.get("id")
        nom = request.form.get("nom")

        if len(nom) < 4:
            flash("Le nom est trop court, quatres(4) caractères minimum", category="error")
            return redirect(url_for("views_admin.marques"))
        else:
            lic = Marques.query.get(id) 
            lic.nom = nom
            db.session.commit()
            flash("Marque mis à jour avec succès", category="success")
            return redirect(url_for("views_admin.marques"))

#Route pour gérer les péripheriques
@views_admin.route('/peripheriques', methods = list)
@login_required
def peripherique():
        per = db.session.query(Peripheriques, Marques, Types).join(Marques, Peripheriques.marque_id == Marques.id).join(Types, Peripheriques.type_id == Types.id).all()
        print(per)
        marque = Marques.query.all()
        type = Types.query.all()
        return render_template("admin/peripherique.html", data = per, data2 = marque, data3 = type)

@views_admin.route("/add&peripherique", methods = list)
@login_required
def add_peripherique():
        nom = request.form.get("nom").strip()
        marque_id = request.form.get("marque_id")
        type_id = request.form.get("type_id")
        model = request.form.get("model").strip()
        no_serie = request.form.get("no_serie").strip()
        
        # per2 = Peripheriques.query.filter_by(model = model).first()
        per3 = Peripheriques.query.filter_by(no_serie = no_serie).first()
        if len(nom) < 4 :
            flash('Nom de l\'appareil invalide (min 5 caractères)',category='error')
            return redirect(url_for("views_admin.peripherique"))
        # elif per2:
        #     flash('Un appareil avec un modèle identique est déjà enregistré!',category='error')
        #     return redirect(url_for("views_admin.peripherique"))
        elif per3:
            flash('Ce numéro de série existe déjà!',category='error')
            return redirect(url_for("views_admin.peripherique"))
        else:
            model = model.upper()
            no_serie = no_serie.upper()
            new_per = Peripheriques(nom = nom, no_serie = no_serie, model = model, marque_id = marque_id, type_id = type_id)
            db.session.add(new_per)
            db.session.commit()
            flash("Périphérique ajouté avec success!", category="success")
            return redirect(url_for("views_admin.peripherique"))
        
@views_admin.route("/delete&peripherique/<int:id>")
def delete_peripherique(id):
    per = Peripheriques.query.get(id)
    db.session.delete(per)
    db.session.commit()
    flash("Périphérique supprimé avec success", category="success")
    return redirect(url_for("views_admin.peripherique"))

# @views_admin.route("/update&peripherique/<int:id>", methods=list)
# @login_required
# def update_marque(id):
#     if request.method == "GET":
#         per = db.session.query(Peripheriques, Marques, Types).join(Marques, Peripheriques.marque_id == Marques.id).join(Types, Peripheriques.type_id == Types.id).get(id)
#         print(per)
#         return render_template("admin/update&peripherique.html", data = per)
#     else : 
#         id = request.form.get("id")
#         nom = request.form.get("nom").strip()
#         marque_id = request.form.get("marque_id")
#         type_id = request.form.get("type_id")
#         model = request.form.get("model").strip()
#         no_serie = request.form.get("no_serie").strip()

#         if len(nom) < 4:
#             flash("Le nom est trop court, quatres(4) caractères minimum", category="error")
#             return redirect(url_for("views_admin.marques"))
#         else:
#             lic = Peripheriques.query.get(id) 
#             lic.nom = nom
#             lic.marque_id = marque_id
#             lic.type_id = type_id
#             lic.model = model
#             lic.no_serie = no_serie
#             db.session.commit()
#             flash("Péripherique mis à jour avec succès", category="success")
#             return redirect(url_for("views_admin.peripherique"))




# Route pour gérer les machines
@views_admin.route('/machines',methods = list)
@login_required
def machine():
    marque = Marques.query.all()
    type = Types.query.all()
    data = db.session.query(Machines, Marques, Types, Peripheriques).join(Marques, Marques.id == Machines.marque_id).join(Types, Types.id == Machines.type_id).outerjoin(Peripheriques, Peripheriques.machine_id == Machines.id).all()
    return render_template("admin/machine.html", data = data, data2 = marque, data3 = type)

@views_admin.route('add&machine', methods = list)
@login_required
def add_machine():
    nom = request.form.get("nom").strip()
    marque_id = request.form.get("marque_id")
    type_id = request.form.get("type_id")
    systeme = request.form.get("systeme").strip()
    domaine = request.form.get("domaine").strip()
    bitlocker = request.form.get("bitlocker").strip()
    adresse_ip = request.form.get("adresse_ip").strip()
    model = request.form.get("model").strip()
    no_serie = request.form.get("no_serie").strip()
    date_achat = request.form.get("date_achat")
    kes = request.form.get("kes")

    machine = Machines.query.filter_by(nom = nom).first()
    machine2 = Machines.query.filter_by(adresse_ip = adresse_ip).first()
    # machine3 = Machines.query.filter_by(model = model).first()
    machine4 = Machines.query.filter_by(no_serie = no_serie).first()

    if len (nom) < 4 :
        flash ("Le Nom doit contenir au moins quatre(4) caractères.",category='error')
        return redirect(url_for("views_admin.machine"))
    elif machine2:
        flash('Une machine avec cette IP existe deja !', category="error")
        return redirect(url_for("views_admin.machine"))
    # elif machine3:
    #     flash('Une machine avec ce modele existe deja !', category="error")
    #     return redirect(url_for("views_admin.machine"))
    elif machine:
        flash('Une machine avec ce nom existe deja !', category="error")
        return redirect(url_for("views_admin.machine"))
    elif machine4:
        flash('Une machine avec ce numero de serie existe deja !', category="error")
        return redirect(url_for("views_admin.machine"))
    else:
        model = model.upper()
        no_serie = no_serie.upper()
        bitlocker = bitlocker.upper()
        domaine = domaine.upper()
        kes = kes.upper()
        systeme = systeme.upper()
        new_machine = Machines(nom = nom, systeme = systeme, domaine = domaine, bitlocker = bitlocker, adresse_ip = adresse_ip, model = model, no_serie = no_serie, kes = kes, date_achat = date_achat, marque_id = marque_id, type_id = type_id)
        db.session.add(new_machine)
        db.session.commit()
        flash("Machine ajouté avec succès", category="success")
        return redirect(url_for("views_admin.machine"))

# Route pour commutateurs
@views_admin.route("/commutateurs", methods=list)
@login_required
def commutateur ():
    data =  db.session.query(Commutateurs, Marques, Types).join(Marques, Marques.id == Commutateurs.marque_id).join(Types, Types.id == Commutateurs.type_id).all()
    marque = Marques.query.all()
    type = Types.query.all()
    return render_template("admin/commutateur.html", data = data, data2 = marque, data3 = type)

@views_admin.route("/add&commutateur", methods=list)
@login_required
def add_commutateur():
    nom = request.form.get("nom").strip()
    marque_id = request.form.get("marque_id")
    type_id = request.form.get("type_id")
    model = request.form.get("model").strip()
    no_serie = request.form.get("no_serie").strip()
    date_achat = request.form.get("date_achat")
    nb_ports = request.form.get("nb_ports")

    # com = Commutateurs.query.filter_by(model = model).first()
    com2 = Commutateurs.query.filter_by(no_serie = no_serie).first()

    if len(nom) < 4 : 
        flash ('Le Nom du commutateur doit comporter au minimum quatre(4) caracteres.', category ="error" )
        return redirect(url_for("views_admin.commutateur"))
    # elif com : 
    #     flash ( 'Un commutateur avec le même numero modèle existe déjà !', category ='error' )
    #     return redirect(url_for("views_admin.commutateur"))
    elif com2 :
        flash ("Un commutateur avec la même numéro de série existe déjà!",category='error')
        return redirect(url_for("views_admin.commutateur"))
    else : 
        new_com = Commutateurs(nom = nom, nb_ports = nb_ports, model = model, no_serie = no_serie, date_achat = date_achat, marque_id = marque_id, type_id = type_id)
        db.session.add(new_com)
        db.session.commit()
        flash("Commutateur ajouté avec success", category = "success")
        return redirect(url_for('views_admin.commutateur'))
    


# Route pour les serveurs 
@views_admin.route("/serveurs", methods=list)
@login_required
def serveur():
    data =  db.session.query(Serveurs, Marques, Types).join(Marques, Marques.id == Serveurs.marque_id).join(Types, Types.id == Serveurs.type_id).all()
    marque = Marques.query.all()
    type = Types.query.all()
    return render_template("admin/serveur.html", data = data, data2 = marque, data3 = type)

@views_admin.route("/add&serveur", methods=list)
@login_required
def add_serveur():
    nom = request.form.get("nom").strip()
    marque_id = request.form.get("marque_id")
    type_id = request.form.get("type_id")
    model = request.form.get("model").strip()
    no_serie = request.form.get("no_serie").strip()
    date_achat = request.form.get("date_achat")
    adresse_ip = request.form.get("adresse_ip").strip()
    memoire_ram = request.form.get("memoire_ram").strip()
    stockage = request.form.get("stockage").strip()
    

    # com = Serveurs.query.filter_by(model = model).first()
    com2 = Serveurs.query.filter_by(no_serie = no_serie).first()

    if len(nom) < 4 : 
        flash ('Le Nom du commutateur doit comporter au minimum quatre(4) caracteres.', category ="error" )
        return redirect(url_for("views_admin.serveur"))
    # elif com : 
    #     flash ( 'Un serveur avec le même numero modèle existe déjà !', category ='error' )
    #     return redirect(url_for("views_admin.serveur"))
    elif com2 :
        flash ("Un commutateur avec la même numéro de série existe déjà!",category='error')
        return redirect(url_for("views_admin.serveur"))
    else : 
        new_sev = Serveurs(nom = nom, adresse_ip = adresse_ip, memoire_ram = memoire_ram, stockage = stockage, date_achat = date_achat, marque_id = marque_id, type_id = type_id, model = model, no_serie = no_serie)
        db.session.add(new_sev)
        db.session.commit()
        flash("Serveur ajouté avec success", category = "success")
        return redirect(url_for('views_admin.serveur'))
    
# Route pour les imprimantes 
@views_admin.route("/imprimantes", methods=list)
@login_required
def imprimante ():
    data =  db.session.query(Imprimantes, Marques, Types).join(Marques, Marques.id == Imprimantes.marque_id).join(Types, Types.id == Imprimantes.type_id).all()
    marque = Marques.query.all()
    type = Types.query.all()
    return render_template("admin/imprimante.html", data = data, data2 = marque, data3 = type)

@views_admin.route("/add&imprimante", methods=list)
@login_required
def add_imprimante():
    nom = request.form.get("nom").strip()
    marque_id = request.form.get("marque_id")
    type_id = request.form.get("type_id")
    model = request.form.get("model").strip()
    no_serie = request.form.get("no_serie").strip()
    date_achat = request.form.get("date_achat")
    adresse_ip = request.form.get("adresse_ip").strip()
    

    imp2 = Imprimantes.query.filter_by(no_serie = no_serie).first()

    if len(nom) < 4 : 
        flash ('Le Nom de l\'imprimante doit comporter au minimum quatre(4) caracteres.', category ="error" )
        return redirect(url_for("views_admin.imprimante"))
    # elif imp : 
    #     flash ( 'Une imprimante avec le même numero modèle existe déjà !', category ='error' )
    #     return redirect(url_for("views_admin.imprimante"))
    elif imp2 :
        flash ("Une imprimante avec la même numéro de série existe déjà!",category='error')
        return redirect(url_for("views_admin.imprimante"))
    else : 
        new_imp = Imprimantes(nom = nom, adresse_ip = adresse_ip, date_achat = date_achat, marque_id = marque_id, type_id = type_id, model = model, no_serie = no_serie)
        db.session.add(new_imp)
        db.session.commit()
        flash("Imprimante ajoutée avec success", category = "success")
        return redirect(url_for('views_admin.imprimante'))

# Route pour les telephones 
@views_admin.route("/telephones", methods=list)
@login_required
def telephone ():
    data =  db.session.query(Telephones, Marques, Types).join(Marques, Marques.id == Telephones.marque_id).join(Types, Types.id == Telephones.type_id).all()
    marque = Marques.query.all()
    type = Types.query.all()
    return render_template("admin/telephone.html", data = data, data2 = marque, data3 = type)

@views_admin.route("/add&telephone", methods=list)
@login_required
def add_telephone():
    nom = request.form.get("nom").strip()
    marque_id = request.form.get("marque_id")
    type_id = request.form.get("type_id")
    model = request.form.get("model").strip()
    no_serie = request.form.get("no_serie").strip()
    date_achat = request.form.get("date_achat")
    numero = request.form.get("numero").strip()
    

    # tel = Telephones.query.filter_by(model = model).first()
    tel2 = Telephones.query.filter_by(no_serie = no_serie).first()

    if len(nom) < 4 : 
        flash ('Le Nom du telephone doit comporter au minimum quatre(4) caracteres.', category ="error" )
        return redirect(url_for("views_admin.imprimante"))
    # elif tel : 
    #     flash ( 'Un telephone avec le même numero modèle existe déjà !', category ='error' )
    #     return redirect(url_for("views_admin.imprimante"))
    elif tel2 :
        flash ("Un telephone avec la même numéro de série existe déjà!",category='error')
        return redirect(url_for("views_admin.imprimante"))
    else : 
        new_tel = Telephones(nom = nom, numero = numero, date_achat = date_achat, marque_id = marque_id, type_id = type_id, model = model, no_serie = no_serie)
        db.session.add(new_tel)
        db.session.commit()
        flash("Telephone ajouté avec success", category = "success")
        return redirect(url_for('views_admin.telephone'))
    

# Route por gérer les licences logicielles
def get_expiry_class(expiry_date):
        today = datetime.now()
        expiry_date = datetime.strptime(expiry_date, "%Y-%m-%d")
        remaining_days = (expiry_date - today).days
        return remaining_days

@views_admin.route("/licences", methods = list)
@login_required
def licence() :
    data = Licences.query.all()
    return render_template("admin/licence.html", data = data)

@views_admin.route("/add&licence", methods = list)
@login_required
def add_licence() : 
    nom = request.form.get("nom")
    key = request.form.get("key")
    date_debut = request.form.get("date_debut")
    date_fin = request.form.get("date_fin")

    lic = Licences.query.filter_by(nom = nom).first()
    lic2 = Licences.query.filter_by(key = key).first()
    if len(nom) < 4:
        flash("Le nom est trop court, quatres(4) carctères minimum", category="error")
        return redirect(url_for("views_admin.licence"))
    elif len(key) > 255:
        flash("La clée est trop longue", category="error")
        return redirect(url_for("views_admin.licence"))
    elif lic : 
        flash("Cette licence existe déjà", category="error")
        return redirect(url_for("views_admin.licence"))
    elif lic2 : 
        flash("Une clé similaire pour une autre licence existe déjà", category="error")
        return redirect(url_for("views_admin.licence"))
    else:
        new_lic = Licences(nom = nom, key = key, date_debut = date_debut, date_fin = date_fin)
        db.session.add(new_lic)
        db.session.commit()
        flash("Nouvelle licence ajouté avec succès", category="success")
        return redirect(url_for("views_admin.licence"))

@views_admin.route("/delete&licence/<int:id>", methods=list)
@login_required
def delete_licence(id):
    lic = Licences.query.get(id)
    db.session.delete(lic)
    db.session.commit()
    flash("Element supprimé avec success", category="success")
    return redirect(url_for('views_admin.licence'))

# Routee pour toute annulation
# @views_admin.route('/annuler',methods=list)
# @login_required
# def annuler():
#     return redirect(url_for(ad))

@views_admin.route("/update&licence/<int:id>", methods = list)
@login_required
def update_licence(id):
    if request.method == "GET":
        data = Licences.query.get(id)
        return render_template("admin/update&licence.html", data = data)
    else : 
        id = request.form.get("id")
        nom = request.form.get("nom")
        key = request.form.get("key")
        date_debut = request.form.get("date_debut")
        date_fin = request.form.get("date_fin")

        if len(nom) < 4:
            flash("Le nom est trop court, quatres(4) caractères minimum", category="error")
            return redirect(url_for("views_admin.licence"))
        else:
            lic = Licences.query.get(id) 
            lic.nom = nom
            lic.key = key
            lic.date_debut = date_debut
            lic.date_fin = date_fin
            db.session.commit()
            flash("Licence mis à jour avec succès", category="success")
            return redirect(url_for("views_admin.licence"))


# Route pour gérer les allocations de machine
@views_admin.route("/allocations", methods = list)
@login_required
def allocation():
    if request.method == "GET":
        data = Users.query.all()
        datas = Services.query.all()
        data2 = Machines.query.filter(Machines.user_id == None).all()
        data3 = Commutateurs.query.filter(Commutateurs.user_id == None).all()
        data4 = Imprimantes.query.filter(Imprimantes.user_id == None).all()
        data5 = Serveurs.query.filter(Serveurs.user_id == None).all()
        data6 = Telephones.query.filter(Telephones.user_id == None).all()
        return render_template("admin/allocation_equipement.html", data = data, datas = datas, data2 = data2, data3 = data3, data4 = data4, data5 = data5, data6 = data6)
    else: 
        entite = request.form.get("entite")
        objet_id = request.form.get("objet_id")
        type = request.form.get("type")
        equipement_id = request.form.get("equipement_id")
        if entite == "Employe":
            if type == "Machines":
                equipement = Machines.query.get(equipement_id)
                equipement.user_id = objet_id
                db.session.commit()
                flash("Machine attribué avec success", category="success")
                return redirect(url_for("views_admin.employe_ressources_list"))
            elif type == "Commutateurs":
                equipement = Commutateurs.query.get(equipement_id)
                equipement.user_id = objet_id
                db.session.commit()
                flash("Commutateurs attribué avec success", category="success")
                return redirect(url_for("views_admin.employe_ressources_list"))
            elif type == "Imprimantes":
                equipement = Imprimantes.query.get(equipement_id)
                equipement.user_id = objet_id
                db.session.commit()
                flash("Imprimante attribué avec success", category="success")
                return redirect(url_for("views_admin.employe_ressources_list"))
            elif type == "Serveurs":
                equipement = Serveurs.query.get(equipement_id)
                equipement.user_id = objet_id
                db.session.commit()
                flash("Serveurs attribué avec success", category="success")
                return redirect(url_for("views_admin.employe_ressources_list"))
            elif type == "Telephones":
                equipement = Telephones.query.get(equipement_id)
                equipement.user_id = objet_id
                db.session.commit()
                flash("Telephone attribué avec success", category="success")
                return redirect(url_for("views_admin.employe_ressources_list"))
        else : 
            if type == "Machines":
                equipement = Machines.query.get(equipement_id)
                equipement.service_id = objet_id
                db.session.commit()
                flash("Machine attribué avec success", category="success")
                return redirect(url_for("views_admin.service_ressources_list"))
            elif type == "Commutateurs":
                equipement = Commutateurs.query.get(equipement_id)
                equipement.service_id = objet_id
                db.session.commit()
                flash("Commutateurs attribué avec success", category="success")
                return redirect(url_for("views_admin.service_ressources_list"))
            elif type == "Imprimantes":
                equipement = Imprimantes.query.get(equipement_id)
                equipement.service_id = objet_id
                db.session.commit()
                flash("Imprimante attribué avec success", category="success")
                return redirect(url_for("views_admin.service_ressources_list"))
            elif type == "Serveurs":
                equipement = Serveurs.query.get(equipement_id)
                equipement.service_id = objet_id
                db.session.commit()
                flash("Serveurs attribué avec success", category="success")
                return redirect(url_for("views_admin.service_ressources_list"))
            elif type == "Telephones":
                equipement = Telephones.query.get(equipement_id)
                equipement.service_id = objet_id
                db.session.commit()
                flash("Telephone attribué avec success", category="success")
                return redirect(url_for("views_admin.service_ressources_list"))
            
#Route pour changer de mot de passe
@views_admin.route('/password', methods=list)
@login_required
def changer_mot_de_passe():
    if request.method == "GET":
        return render_template("admin/mot_de_passe.html", user = current_user)
    else:
        id = request.form.get("id")
        mot_de_passe = request.form.get("mot_de_passe")
        repeat_password = request.form.get("repeat_password")
        
        user = Users.query.get(id)
        if len(mot_de_passe) < 7 :
            flash("Mot de passe trop court", category="error")
            return redirect(url_for("views_client.changer_mot_de_passe"))
        elif mot_de_passe != repeat_password :
            flash("Les mots de passe sont différents", category="error")
            return redirect(url_for("views_client.changer_mot_de_passe"))
        elif check_password_hash(user.mot_de_passe, mot_de_passe) :
            flash("Vous avez entrez votre ancien mot passe, changer de mot de passe s'il vous plaît", category="error")
            return redirect(url_for("views_client.changer_mot_de_passe"))
        else:
            user.mot_de_passe = generate_password_hash(mot_de_passe, method="scrypt")
            db.session.commit()
            flash("Mot de passe changé avec success", category="success")
            return redirect(url_for("views_admin.home"))