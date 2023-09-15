from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import Users
from . import db


auth = Blueprint('auth',__name__)


@auth.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "GET" :
        return render_template("auth/signup.html")
    else:
        nom = request.form.get("nom")
        prenom = request.form.get("prenom")
        nom_utilisateur = request.form.get("nom_utilisateur")
        email=  request.form.get("email")
        mot_de_passe = request.form.get("mot_de_passe")
        repeat_password = request.form.get("repeat_password")

        if "is_admin_request" in request.form:          
            user = Users.query.filter_by(email=email).first()
            user2 = Users.query.filter_by(nom_utilisateur = nom_utilisateur).first()
            if user or user2: 
                flash("Email or Username already exist", category="error")
                return redirect(url_for("auth.signup"))
            elif len(email) < 4 :
                flash("Email must be greater than 4 characters.", category="error")
                return redirect(url_for("auth.signup"))
            elif len(nom) < 4 : 
                flash("Name must be greater than 2 characters.", category="error")
                return redirect(url_for("auth.signup"))
            elif len(prenom) < 4 : 
                flash("Name must be greater than 2 characters.", category="error")
                return redirect(url_for("auth.signup"))
            elif mot_de_passe != repeat_password :
                flash("Password don't match.", category="error")
                return redirect(url_for("auth.signup"))
            elif len(mot_de_passe) < 7 :
                flash("Password must be greater than 7 characters.", category="error")
                return redirect(url_for("auth.signup"))
            else:
                new_user = Users(nom = nom, prenom = prenom, nom_utilisateur = nom_utilisateur, email=email,  mot_de_passe = generate_password_hash(mot_de_passe, method="scrypt"), is_admin_request = True, is_validated = False)
                db.session.add(new_user)
                db.session.commit()
                flash("Votre demande a été prise en compte, vous recevrez un email de validation", category="success")
                return redirect(url_for("auth.login"))
  
        else:
            flash("Les employés n'ont le droit que de se connecter", category="error")
            return redirect(url_for("auth.login"))


@auth.route("/", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("auth/login.html")
    else:
        nom_utilisateur = request.form.get("nom_utilisateur")
        mot_de_passe = request.form.get("mot_de_passe")
        user = Users.query.filter_by(nom_utilisateur = nom_utilisateur).first()
        if not user or not check_password_hash(user.mot_de_passe, mot_de_passe) :
            flash("Vérifier vos informations de connection", category="error")
            return redirect(url_for("auth.login"))
        elif user : 
            if user.is_admin_request == True and user.is_validated == True : 
                login_user(user)
                flash("Bienvenu administrateur "+ user.nom, category="success")
                return redirect(url_for("views_admin.home"))
            elif user.is_admin_request == False and user.is_validated == True : 
                login_user(user)
                flash("Connexion réussi, bienvenu "+ user.nom, category="success")
                return redirect(url_for("views_client.home"))
            else : 
                flash("compte désactivé", category="error")
                return redirect(url_for("auth.login"))
            
@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Deconnexion réussi", category="success")
    return redirect(url_for("auth.login"))





