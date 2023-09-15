from . import db
from flask_login import UserMixin

class Users(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer,primary_key=True)
    nom = db.Column(db.String(128), nullable=False, unique=False)
    prenom = db.Column(db.String(128), nullable=False, unique=False)
    nom_utilisateur = db.Column(db.String(128), nullable=False,unique=True)
    email = db.Column(db.String(40),unique=True,nullable=False)
    mot_de_passe = db.Column(db.String(200),unique=False,nullable=False)
    is_admin_request = db.Column(db.Boolean, default=False)
    is_validated = db.Column(db.Boolean, default=False)
    notes = db.relationship('Tasks', backref='users', lazy=True)
    services_id = db.Column(db.Integer, db.ForeignKey("services.id"))
    machines = db.relationship("Machines", backref="users", lazy = True)
    commutateurs = db.relationship("Commutateurs", backref="users", lazy = True)
    serveurs = db.relationship("Serveurs", backref="users", lazy = True)
    imprimantes = db.relationship("Imprimantes", backref="users", lazy = True)
    telephones = db.relationship("Telephones", backref="users", lazy = True)

class Services(db.Model):
    __tablename__ = "services"
    id = db.Column(db.Integer,primary_key=True)
    nom = db.Column(db.String(128), nullable=False, unique=False)
    employes = db.relationship("Users", backref="services", lazy=True)
    machines = db.relationship("Machines", backref="services", lazy = True)
    commutateurs = db.relationship("Commutateurs", backref="services", lazy = True)
    serveurs = db.relationship("Serveurs", backref="services", lazy = True)
    imprimantes = db.relationship("Imprimantes", backref="services", lazy = True)
    telephones = db.relationship("Telephones", backref="services", lazy = True)

class Tasks(db.Model):
    __tablename__="tasks"
    id = db.Column(db.Integer, primary_key= True )
    titre  = db.Column (db.String(128), nullable = False, unique=False)
    description = db.Column(db.String(200), nullable=False, unique=False)
    statut = db.Column(db.Integer(), default=0)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

class Types(db.Model):
    __tablename__ ="types"
    id = db.Column(db.Integer(), primary_key=True)
    nom = db.Column(db.String(128), nullable = False, unique = True)
    peripheriques = db.relationship("Peripheriques", backref="types", lazy=True)
    machines = db.relationship("Machines", backref="types", lazy=True)
    commutateurs = db.relationship("Commutateurs", backref="types", lazy=True)
    serveurs = db.relationship("Serveurs", backref="types", lazy=True)
    telephones = db.relationship("Telephones", backref="types", lazy=True)
    imprimantes = db.relationship("Imprimantes", backref="types", lazy=True)

class Marques(db.Model):
    __tablename__ ="marques"
    id = db.Column(db.Integer(), primary_key=True)
    nom = db.Column(db.String(128), nullable = False, unique = True)
    peripheriques = db.relationship("Peripheriques", backref="marques", lazy=True)
    machines = db.relationship("Machines", backref="marques", lazy=True)
    commutateurs = db.relationship("Commutateurs", backref="marques", lazy=True)
    serveurs = db.relationship("Serveurs", backref="marques", lazy=True)
    telephones = db.relationship("Telephones", backref="marques", lazy=True)
    imprimantes = db.relationship("Imprimantes", backref="marques", lazy=True)

class Peripheriques(db.Model):
    __tablename__ ="peripheriques"
    id = db.Column(db.Integer(), primary_key=True)
    nom = db.Column(db.String(128), nullable = False, unique = True)
    no_serie = db.Column(db.String(128), nullable = False, unique = True)
    model = db.Column(db.String(128), nullable = False)
    marque_id = db.Column(db.Integer, db.ForeignKey("marques.id"))
    type_id = db.Column(db.Integer, db.ForeignKey("types.id"))
    machine_id =  db.Column(db.Integer, db.ForeignKey("machines.id"))
    

class Machines(db.Model):
    __tablename__ ="machines"
    id = db.Column(db.Integer(), primary_key=True)
    nom = db.Column(db.String(128), nullable = False)
    systeme = db.Column(db.String(128), nullable = False)
    domaine = db.Column(db.String(128), nullable = False)
    bitlocker = db.Column(db.String(128), nullable = False)
    adresse_ip = db.Column(db.String(128), nullable = False)
    no_serie = db.Column(db.String(128), nullable = False)
    model = db.Column(db.String(128), nullable = False)
    kes = db.Column(db.String(128), nullable = False)
    date_achat = db.Column(db.Date, nullable = False)    
    marque_id = db.Column(db.Integer, db.ForeignKey("marques.id"))
    type_id = db.Column(db.Integer, db.ForeignKey("types.id"))
    peripheriques = db.relationship("Peripheriques", backref="machines", lazy = True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    service_id = db.Column(db.Integer, db.ForeignKey("services.id"))

class Commutateurs(db.Model):
    __tablename__ ="commutateurs"
    id = db.Column(db.Integer(), primary_key=True)
    nom = db.Column(db.String(128), nullable = False)
    nb_ports = db.Column(db.Integer, nullable = False)
    no_serie = db.Column(db.String(128), nullable = False)
    model = db.Column(db.String(128), nullable = False)
    date_achat = db.Column(db.Date, nullable = False)
    marque_id = db.Column(db.Integer, db.ForeignKey("marques.id"))
    type_id = db.Column(db.Integer, db.ForeignKey("types.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    service_id = db.Column(db.Integer, db.ForeignKey("services.id"))

class Serveurs(db.Model):
    __tablename__ ="serveurs"
    id = db.Column(db.Integer(), primary_key=True)
    nom = db.Column(db.String(128), nullable = False)
    adresse_ip = db.Column(db.String(128), nullable = False)
    memoire_ram = db.Column(db.String(128), nullable = False)
    stockage = db.Column(db.String(128), nullable = False)
    no_serie = db.Column(db.String(128), nullable = False)
    model = db.Column(db.String(128), nullable = False)
    date_achat = db.Column(db.Date, nullable = False)
    marque_id = db.Column(db.Integer, db.ForeignKey("marques.id"))
    type_id = db.Column(db.Integer, db.ForeignKey("types.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    service_id = db.Column(db.Integer, db.ForeignKey("services.id"))

class Telephones(db.Model):
    __tablename__ ="telephones"
    id = db.Column(db.Integer(), primary_key=True)
    nom = db.Column(db.String(128), nullable = False)
    numero = db.Column(db.Integer, nullable = False)
    no_serie = db.Column(db.String(128), nullable = False)
    model = db.Column(db.String(128), nullable = False)
    date_achat = db.Column(db.Date, nullable = False)
    marque_id = db.Column(db.Integer, db.ForeignKey("marques.id"))
    type_id = db.Column(db.Integer, db.ForeignKey("types.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    service_id = db.Column(db.Integer, db.ForeignKey("services.id"))

class Imprimantes(db.Model):
    __tablename__ ="imprimantes"
    id = db.Column(db.Integer(), primary_key=True)
    nom = db.Column(db.String(128), nullable = False)
    adresse_ip = db.Column(db.String(128), nullable = False)
    no_serie = db.Column(db.String(128), nullable = False)
    model = db.Column(db.String(128), nullable = False)
    date_achat = db.Column(db.Date, nullable = False)
    marque_id = db.Column(db.Integer, db.ForeignKey("marques.id"))
    type_id = db.Column(db.Integer, db.ForeignKey("types.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    service_id = db.Column(db.Integer, db.ForeignKey("services.id"))

class Licences(db.Model):
    __tablename__ = "licences"
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(128), nullable = False)
    key = db.Column(db.String(256), nullable = False)
    date_debut = db.Column(db.Date, nullable = False)
    date_fin = db.Column(db.Date, nullable = False)