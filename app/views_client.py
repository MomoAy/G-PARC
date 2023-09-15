from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import  login_required, current_user
from .models import Users, Tasks
from . import db 
from werkzeug.security import generate_password_hash, check_password_hash
list = ["GET", "POST", "PUT", "PATCH", "DELETE"]


views_client = Blueprint('views_client',__name__)


@views_client.route('/')
@login_required
def home():
    return render_template('client/home.html', user = current_user)

# route pour gérer les demande
@views_client.route("/Faire&une&demande", methods=list)
@login_required
def ask_assist():
    if request.method == "GET":
        return render_template("client/ask_assist.html", user = current_user)
    else:
        id = request.form.get("id")
        titre = request.form.get("titre").strip()
        description = request.form.get("description").strip()

        if len(titre) < 4:
            flash("Le titre est trop court(minimum 4 caractères)", category="error")
            return redirect(url_for("views_client.ask_assist"))
        elif len(description) < 10:
            flash("Description peu explicite", category="error")
            return redirect(url_for("views_client.ask_assist"))
        else:
            new_ask_assist = Tasks(titre = titre, description = description, user_id = id)
            db.session.add(new_ask_assist)
            db.session.commit()
            flash("Votre demande a été enregistré avec succès", category="success")
            return redirect(url_for("views_client.show_assist"))

@views_client.route("/Afficher&les&demandes")
@login_required
def show_assist():
    assist = Tasks.query.all()
    return render_template("client/show_assist.html", data = assist)

#Route pour changer de mot de passe
@views_client.route('/Changer&mon&de&passe', methods=list)
@login_required
def changer_mot_de_passe():
    if request.method == "GET":
        return render_template("client/mot_de_passe.html", user = current_user)
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
            return redirect(url_for("views_client.home"))