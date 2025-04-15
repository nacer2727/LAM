from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Table, func, Boolean, TEXT, Enum, Index
from sqlalchemy import event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import enum
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


Base = declarative_base()
# Modèle pour la table 'patients'
class Patient(Base):
    __tablename__ = 'patients'
    id = Column(String, primary_key=True)  # Exemple : "P001"
    patient_barcode = Column(String, nullable=False, unique=True)  # Code à barres unique pour le patient
    name = Column(String, nullable=False)
    prenom = Column(String, nullable=False)
    age = Column(String, nullable=False)
    age_unit = Column(String, nullable=True) 
    date_naissance = Column(DateTime, nullable=True)
    sexe = Column(String, nullable=False)
    email = Column(String, nullable=False)
    tel = Column(String, nullable=False)
    group_sanguin = Column(String, nullable=True)
    ATCD = Column(String, nullable=True)
    adresse = Column(String, nullable=True)  # Adresse du patient
    is_active = Column(Boolean, nullable=True, default=True)  # Statut du patient (actif/archivé)
    date_derniere_consultation = Column(DateTime, nullable=True)  # Dernière consultation
    historique_maladies = Column(TEXT, nullable=True)  # Antécédents médicaux

    
    analyses = relationship("Analyse", back_populates="patient")
    
    def __repr__(self):
        return (f"<Patient(id='{self.id}', patient_barcode='{self.patient_barcode}', "
                f"name='{self.name}', prenom='{self.prenom}')>")
    
class Categorie(Base):
    __tablename__ = 'categories'
    categorie_id = Column(Integer, primary_key=True, autoincrement=True)
    nom = Column(String(50), nullable=False, unique=True)  # Ex: 'biochimique', 'hormonal'
    description = Column(String(255), nullable=True)
    
    parameters = relationship("Parameter", back_populates="categorie")
    def __repr__(self):
        return f"<Categorie(id={self.categorie_id}, nom='{self.nom}')>"
    
    

# Table intermédiaire pour associer les paramètres aux tubes
parameter_tube_table = Table(
    'parameter_tubes',
    Base.metadata,
    Column('parameter_id', Integer, ForeignKey('parameters.parameter_id'), primary_key=True),
    Column('tube_id', Integer, ForeignKey('tubes.tube_id'), primary_key=True)
)
# Table intermédiaire pour associer les paramètres aux types de prélèvements
parameter_prelevements_table = Table(
    'parameter_prelevements',
    Base.metadata,
    Column('parameter_id', Integer, ForeignKey('parameters.parameter_id'), primary_key=True),
    Column('prelevement_type_id', Integer, ForeignKey('prelevement_types.id'), primary_key=True)
)
# Modèle pour la table 'parameters'
class Parameter(Base):
    __tablename__ = 'parameters'
    parameter_id = Column(Integer, primary_key=True, autoincrement=True)
    param = Column(String, nullable=False)  # Nom du paramètre
    nom_param = Column(String, nullable=True)  # abr du paramètre
    prix_u = Column(Float, nullable=False)   # Prix unitaire (ici 10)
    unite = Column(String, nullable=True)  # Unité de mesure
    description = Column(String, nullable=True)  # Description du paramètre
    nombre_utilisations = Column(Integer, nullable=True, default=0)  # Nombre de fois où le paramètre a été utilisé
    categorie_id = Column(Integer, ForeignKey('categories.categorie_id'), nullable=True)
    analyse_details = relationship("AnalyseDetail", back_populates="parameter")
    resultats = relationship("Resultat", back_populates="parameter")  # Ajout de cette relation
    # Relation avec la table Tubes
    tubes = relationship("Tube", secondary=parameter_tube_table, backref="parameters")
    # Relation avec la table PrelevementType
    prelevement_types = relationship("PrelevementType", secondary=parameter_prelevements_table, backref="parameters")
    categorie = relationship("Categorie", back_populates="parameters")
    
    def __repr__(self):
        return f"<Parameter(id={self.parameter_id}, abr='{self.nom_param}', name='{self.param}', prix_u={self.prix_u})>"
    
class AnalyseState(enum.Enum):
    EN_COURS = "EN_COURS"
    TERMINEE = "TERMINEE"
    ANNULEE = "ANNULEE"

# Table intermédiaire pour associer les analyses aux types de prélèvements
analyse_prelevements_table = Table(
    'analyse_prelevements',
    Base.metadata,
    Column('analyse_id', Integer, ForeignKey('analyses.id'), primary_key=True),
    Column('prelevement_type_id', Integer, ForeignKey('prelevement_types.id'), primary_key=True)
)
# Table intermédiaire pour associer les analyses aux tubes
analyse_tubes_table = Table(
    'analyse_tubes',
    Base.metadata,
    Column('analyse_id', Integer, ForeignKey('analyses.id'), primary_key=True),
    Column('tube_id', Integer, ForeignKey('tubes.tube_id'), primary_key=True)
)

# Modèle pour la table 'analyses'
class Analyse(Base):
    __tablename__ = 'analyses'
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(String, ForeignKey('patients.id'), nullable=False)
    dossier_barcode = Column(String, nullable=False, unique=True)  # Code à barres pour le dossier d'analyse
    analyse_date = Column(DateTime, nullable=False)
    facture = Column(Float, nullable=False)   # Facturation pour le total de cette analyse
    remise = Column(Float, nullable=False)     # Remise appliquée
    fac_remise = Column(Float, nullable=False)   # Facturation après remise
    montant_p = Column(Float, nullable=True, default=0)    # Montant déjà payé
    montant_r = Column(Float, nullable=True, default=0)  # Montant restant à payer
    prelevement = Column(String, nullable=False, default="Lab")  # "lab" ou "exterieur"
    state = Column(Enum(AnalyseState, native_enum=False), nullable=True)#, default=AnalyseState.EN_COURS)  # État : "en_cours", "terminée", "annulée"
    notes = Column(TEXT, nullable=True)  # Notes supplémentaires
    date_paiement = Column(DateTime, nullable=True)  # Date de paiement
    mode_paiement = Column(String, nullable=True)  # Mode de paiement
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    priority_analyse = Column(String, nullable=True)
    priority_test = Column(String, nullable=True)
    medecin = Column(String, nullable=True)
    specialite = Column(String, nullable=True)
    etablissement = Column(String, nullable=True) # etat , privé
    taille = Column(String, nullable=True)
    poids = Column(String, nullable=True) #
    ts = Column(String, nullable=True) # tension systolique
    td = Column(String, nullable=True)# tension d
    bc = Column(String, nullable=True) # battement de coeur
    jeun = Column(Boolean, nullable=True, default=True) # a jeun ou non
    prelevement_statut = Column(String, nullable=True) # hemolyse , lactescent , opalescent , 
    date_prelvement = Column(DateTime, nullable=True)
    type_analyse = Column(String, nullable=True)  # Ex: "nfs", "bacterio", "spermo"
    is_nfs = Column(Boolean, default=False)  # Indique si l'analyse inclut 
    is_groupage = Column(Boolean, default=False)  # Indique si l'analyse inclut
    is_frottis = Column(Boolean, default=False)  # Indique si l'analyse inclut 
    is_spermo = Column(Boolean, default=False)  # Indique si l'analyse inclut      
    is_bacterio = Column(Boolean, default=False)  # Indique si l'analyse inclut 
    is_special = Column(Boolean, default=False)  # Indique si l'analyse inclut 
    is_autre_analyse = Column(Boolean, default=False)  # Indique si l'analyse inclut
    is_soustraitance = Column(Boolean, default=False)  # Indique si l'analyse inclut 
    # Nouvelle colonne pour la personne qui fait le prelevement (si prélèvement au labo)
    nurse_id = Column(Integer, ForeignKey('personals.id'), nullable=True)
     # Nouveaux champs pour la validation
    validated_by = Column(Integer, ForeignKey('personals.id'), nullable=True)
    validation_date = Column(DateTime, nullable=True)
    is_stamped = Column(Boolean, nullable=False, default=False) 
    stamped_by = Column(Integer, ForeignKey('personals.id'), nullable=True)  # ID du personnel qui a apposé la griffe
    stamped_at = Column(DateTime, nullable=True)  # Date de la griffe
    id_convention = Column(Integer, ForeignKey('conventions.id'), nullable=True)  # Clé étrangère vers la table Convention
    is_convention = Column(Boolean, default=False)  # Indique si l'analyse est liée à une convention


    patient = relationship("Patient", back_populates="analyses")
    analyse_details = relationship("AnalyseDetail", back_populates="analyse")
    nurse = relationship("Personnel", foreign_keys=[nurse_id], backref="analyses_realisees")
    validator = relationship("Personnel", foreign_keys=[validated_by], backref="analyses_validées")
    prelevement_types = relationship("PrelevementType", secondary=analyse_prelevements_table, backref="analyses") 
    tubes = relationship("Tube", secondary=analyse_tubes_table, backref="analyses")
    frottis_results = relationship("Frottis", back_populates="analyse")
    nfs_results = relationship("NumerationFormuleSanguine", back_populates="analyse")
    groupage_results = relationship("GroupageSanguin", back_populates="analyse")
    spermogramme_results = relationship("SpermogrammeResult", back_populates="analyse")
    bacterio_results = relationship("BacterioResult", back_populates="analyse")

    def __repr__(self):
        return (f"<Analyse(id={self.id}, dossier_barcode='{self.dossier_barcode}', "
                f"patient_id='{self.patient_id}', date='{self.analyse_date}', "
                f"prelevement='{self.prelevement}',type_analyse='{self.type_analyse}', "
                f"is_nfs={self.is_nfs}, nurse_id='{self.nurse_id}', "
                f"validated_by='{self.validated_by}', validation_date='{self.validation_date}',"
                f"montant_payé={self.montant_payé}, montant_restant={self.montant_restant},"
                f"state='{self.state.value}', medecin='{self.medecin}',specialite='{self.specialite}',"
                f"taille='{self.taille}', poids='{self.poids}', ts='{self.ts}',"
                f"td='{self.td}', bc='{self.bc}', jeun='{self.jeun}',"
                f"prelevement_statut='{self.prelevement_statut}',"
                f"date_prelvement='{self.date_prelvement}',etablissement='{self.etablissement}')>")


class Personnel(Base):
    __tablename__ = 'personals'
    id = Column(Integer, primary_key=True, autoincrement=True)
    matricule = Column(String, nullable=False, unique=True)  # Matricule unique
    nom = Column(String, nullable=False)
    prenom = Column(String, nullable=False)
    role = Column(String, nullable=False)  # Ex: "medecin", "infirmier", etc.
    mot_de_passe = Column(String, nullable=False)  # Stockez ici le mot de passe haché
    last_login = Column(DateTime, nullable=True)  # Dernière connexion
    is_active = Column(Boolean, nullable=False, default=True)  # Compte actif/désactivé
    created_at = Column(DateTime, nullable=False, default=datetime.now)  # Date de création
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)  # Dernière mise à jour
    email = Column(String, nullable=True)  # Email du personnel
    telephone = Column(String, nullable=True)  # Numéro de téléphone
    department = Column(String, nullable=True) #  biochimie, hématologie..... 
    personal_griffe = Column(String, nullable=True)  # Chemin vers la griffe personnelle

    def set_password(self, password):
        self.mot_de_passe = pwd_context.hash(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.mot_de_passe)

    def __repr__(self):
        return f"<Personnel(id={self.id}, nom='{self.nom}', prenom='{self.prenom}', role='{self.role}', is_active={self.is_active})>"
    
    
# Modèle pour la table 'analyse_details'
class AnalyseDetail(Base):
    __tablename__ = 'analyse_details'
    id = Column(Integer, primary_key=True, autoincrement=True)
    analyse_id = Column(Integer, ForeignKey('analyses.id'), nullable=False)
    parameter_id = Column(Integer, ForeignKey('parameters.parameter_id'), nullable=False)
    tube_id = Column(Integer, ForeignKey('tubes.tube_id'), nullable=True)  # Nouveau champ pour le type de tube
    notes = Column(TEXT, nullable=True)  # Notes supplémentaires sur cet élément d'analyse
    
    analyse = relationship("Analyse", back_populates="analyse_details")
    parameter = relationship("Parameter", back_populates="analyse_details")
    tube = relationship("Tube", backref="analyse_details")  # Relation avec la table Tube

    
    def __repr__(self):
        return (f"<AnalyseDetail(id={self.id}, analyse_id={self.analyse_id}, parameter_id={self.parameter_id}, "
                f"fac_remise={self.fac_remise})>")
    
# Modèle pour la table 'resultat'
class Resultat(Base):
    __tablename__ = 'resultat'

    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(String, ForeignKey('patients.id', ondelete='CASCADE'), nullable=False)
    analyse_id = Column(Integer, ForeignKey('analyses.id', ondelete='CASCADE'), nullable=False)
    parameter_id = Column(Integer, ForeignKey('parameters.parameter_id') , nullable=False)  # Id du paramètre sélectionné
    valeur = Column(Float, nullable=True)  # Valeur du résultat
    result_date = Column(DateTime, nullable=True, default=datetime.now)
    validateur_id = Column(Integer, ForeignKey('personals.id'), nullable=True)  # ID du validateur
    comments = Column(TEXT, nullable=True)  # Commentaires sur le résultat
    validation_status= Column(String, nullable=True)
    import_source = Column(String, nullable=True)  # Exemple : "Cobas", "Manuel"
    import_reference = Column(String, nullable=True)  # Référence unique de l'automate
    import_date = Column(DateTime, nullable=True)  # Date de réception du résultat
    # Relation avec la table 'patients'
    patient = relationship("Patient", backref="resultats")
    parameter = relationship("Parameter", back_populates="resultats")
    analyse = relationship("Analyse", backref="resultats")
    validateur = relationship("Personnel", backref="resultats_validés")
    

class AnalyseRappel(Base):
    __tablename__ = 'analyse_rappels'
    id = Column(Integer, primary_key=True, autoincrement=True)
    analyse_id = Column(Integer, ForeignKey('analyses.id'), nullable=False)
    date_rappel = Column(DateTime, nullable=False)
    statut = Column(String, nullable=False, default="non_traite")  # "traite" ou "non_traite"

    analyse = relationship("Analyse", backref="rappels")

# Modèle pour la table 'reference'
class Reference(Base):
    __tablename__ = 'reference'

    id = Column(Integer, primary_key=True, autoincrement=True)
    parametre_id = Column(Integer, ForeignKey('parameters.parameter_id'), nullable=False)
    categorie_age = Column(String, nullable=False)  # Catégorie d'âge ('nouveau_ne', 'enfant', 'adulte')
    sexe = Column(String, nullable=False)  # Sexe ('homme', 'femme')
    valeur_min = Column(Float, nullable=False)
    valeur_max = Column(Float, nullable=False)
    unite = Column(String, nullable=False)
    methode = Column(String, nullable=True)  # Méthode d'analyse
    created_by = Column(String, nullable=True)

    # Relation avec la table 'parameters'
    parametre = relationship("Parameter", back_populates="references")

Parameter.references = relationship("Reference", order_by=Reference.id, back_populates="parametre")


# Modèle pour la table 'parameter_groups'
class ParameterGroup(Base):
    __tablename__ = 'parameter_groups'
    group_id = Column(Integer, primary_key=True, autoincrement=True)
    group_name = Column(String, nullable=False, unique=True)

    # Relation avec les paramètres via une table intermédiaire
    parameters = relationship(
        "Parameter",
        secondary="group_parameters",
        backref="groups"
    )
    def __repr__(self):
        return f"<ParameterGroup(id={self.group_id}, name='{self.group_name}')>"


# Table intermédiaire pour associer les groupes aux paramètres
group_parameters_table = Table(
    'group_parameters',
    Base.metadata,
    Column('group_id', Integer, ForeignKey('parameter_groups.group_id'), primary_key=True),
    Column('parameter_id', Integer, ForeignKey('parameters.parameter_id'), primary_key=True)
)


class Paiement(Base):
    __tablename__ = 'paiements'
    id = Column(Integer, primary_key=True, autoincrement=True)
    analyse_id = Column(Integer, ForeignKey('analyses.id'), nullable=False)
    montant = Column(Float, nullable=False)
    date_paiement = Column(DateTime, nullable=False, default=datetime.now)
    mode_paiement = Column(String, nullable=False)

    analyse = relationship("Analyse", backref="paiements")


class Tube(Base):
    __tablename__ = 'tubes'
    tube_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)  # Exemple : "Hépariné", "EDTA", "Sec", "Citraté"
    description = Column(String, nullable=True)  # Description facultative du tube

class PrelevementType(Base):
    __tablename__ = 'prelevement_types'
    id = Column(Integer, primary_key=True, autoincrement=True) # 0 , 1 , 2 , 3 
    numero = Column(Integer, nullable=False, unique=True) # 0 , 1 , 2 , 3 
    name = Column(String, nullable=False, unique=True)  # Exemple : "0_Liquide Séminal", "1_Sang", "2_Urine U24 ,4_LCR ...
    description = Column(String, nullable=True)        # Description optionnelle du type de prélèvement
    prix = Column(Float, nullable=True)  # Nouveau champ pour le prix du prélèvement


class SpermogrammeResult(Base):
    __tablename__ = 'spermogramme_results'

    id = Column(Integer, primary_key=True, autoincrement=True)
    analyse_id = Column(Integer, ForeignKey('analyses.id'), nullable=False)  # Lien avec l'analyse correspondante
    date_resultat = Column(DateTime, nullable=True, default=datetime.now)  # Date du résultat
    validateur_id = Column(Integer, ForeignKey('personals.id'), nullable=True)  # ID du personnel ayant validé le résultat
    validation_date = Column(DateTime, nullable=True)
    is_stamped = Column(Boolean, nullable=False, default=False)  # Indique si le résultat a reçu une griffe
    stamped_by = Column(Integer, ForeignKey('personals.id'), nullable=True)  # ID du personnel qui a apposé la griffe
    stamped_at = Column(DateTime, nullable=True)  # Date de la griffe
    comments = Column(TEXT, nullable=True)  # Commentaires sur le résultat
    conclusion = Column(TEXT, nullable=True)  # Commentaires sur le résultat

    # Paramètres spécifiques au spermogramme

     # --- Re-seignement ---
    date_collecte = Column(String, nullable=True)
    lieu_collecte = Column(String, nullable=True)
    diffuculte_collecte = Column(String, nullable=True)
    echantillon_complet = Column(String, nullable=True)
    jour_abstinence = Column(String, nullable=True)
    temperature = Column(Float, nullable=True)  # Température (°C)
    couleur = Column(String, nullable=True)  # Couleur (ex. : "Blanc-grisâtre", "Jaunâtre")
    ph = Column(Float, nullable=True)  # pH
    liquefication = Column(String, nullable=True)  # Liquefication (ex. : "Complète", "Partielle")
    viscosité = Column(String, nullable=True)  # Viscosité (ex. : "Normale", "Élevée")
    agglutination = Column(String, nullable=True)  # Agglutination (ex. : "Présente", "Absente")
    agregation = Column(String, nullable=True)  # Agrégation (ex. : "Présente", "Absente")
    cellule_germinale = Column(String, nullable=True)
    traitement = Column(String, nullable=True)
    

    
     # --- Numération ---
    volume = Column(Float, nullable=True)  # Volume du sperme (en mL)
    concentration1 = Column(Float, nullable=True)  # Concentration de spermatozoïdes (en millions/mL)
    concentration2 = Column(Float, nullable=True)  # Concentration de spermatozoïdes (en millions/mL)
    dilution = Column(Float, nullable=True)  # Total de spermatozoïdes calculé

    # --- Cytologie ---
    leucocytes = Column(String, nullable=True)  # Présence de leucocytes (ex. : "Présent", "Absent")
    hematie = Column(String, nullable=True)  # Présence d'hémies (ex. : "Présent", "Absent")
    parasite = Column(String, nullable=True)  # Présence de parasites (ex. : "Présent", "Absent")
    levure = Column(String, nullable=True)  # Présence de levures (ex. : "Présent", "Absent")
    cellules_rondes = Column(String, nullable=True)  # Présence de cellules rondes (ex. : "Présent", "Absent")
    cellules_epitheliales = Column(String, nullable=True)  # Présence de cellules épithéliales (ex. : "Présent", "Absent")

    # --- Mobilité ---
    mob_a = Column(Float, nullable=True)  # % de spermatozoïdes progressifs rapides (Classe A)
    mob_b = Column(Float, nullable=True)  # % de spermatozoïdes progressifs lents (Classe B)
    mob_c = Column(Float, nullable=True)  # % de spermatozoïdes non progressifs (Classe C)
    mob_d = Column(Float, nullable=True)  # % de spermatozoïdes immobiles (Classe D)
    mob_a_b = Column(Float, nullable=True)  # % de mobilité totale (A + B)

     # --- Vitalité ---
    vitalite_vivant = Column(Float, nullable=True)  # % de spermatozoïdes vivants
    vitalite_mort = Column(Float, nullable=True)  # % de spermatozoïdes morts

    # --- Morphologie ---
    morphologie_normale = Column(Float, nullable=True)  # % de formes normales
    morphologie_anormale = Column(Float, nullable=True)  # % de formes anormales

    # Nouveaux champs pour l'index de teratozoospermie et l'index de déformation
    index_teratozoospermie = Column(Float, nullable=True)  # Index de teratozoospermie
    index_deformation = Column(Float, nullable=True)  # Index de déformation

    # --- classe d'Anomalies morphologiques ---
    normal = Column(String, nullable=True)  # Description pas d'anomalie
    anomalie_tete = Column(String, nullable=True)  # Description des anomalies de tête
    anomalie_piece = Column(String, nullable=True)  # Description des anomalies de pièce
    anomalie_flagelle = Column(String, nullable=True)  # Description des anomalies de flagelle
    anomalie_cytoplasme = Column(String, nullable=True)  # Description des anomalies cytoplasmiques

    # Description des anomalies de tête
    taille_tete_normal = Column(String, nullable=True)
    microcephale_tete = Column(String, nullable=True)
    macrocephale_tete = Column(String, nullable=True)
    normal_tete = Column(String, nullable=True)
    conique_a = Column(String, nullable=True)
    mince_b = Column(String, nullable=True)
    ronde_c = Column(String, nullable=True)
    periforme_d = Column(String, nullable=True)
    amorphe_e = Column(String, nullable=True)
    acrosome_normal = Column(String, nullable=True)
    acrosome_anormal = Column(String, nullable=True)
    
    # Description des anomalies de pièce
    p_normale = Column(String, nullable=True)
    taille_anormale = Column(String, nullable=True)
    insertion_asymetrique = Column(String, nullable=True)
    coude = Column(String, nullable=True)

    # Description des anomalies de flagelle
    flagelle_normal = Column(String, nullable=True)  # Description des anomalies de flagelle
    flagelle_anormal = Column(String, nullable=True)
    court = Column(String, nullable=True)
    sans = Column(String, nullable=True)
    irregulier = Column(String, nullable=True)
    enroule = Column(String, nullable=True)
    multiple = Column(String, nullable=True)
    angulation = Column(String, nullable=True)

    # Description des anomalies cytoplasmiques
    cyto_normale = Column(String, nullable=True)
    cyto_anormale = Column(String, nullable=True)
   
    # Relation avec la table Analyse
    analyse = relationship("Analyse", back_populates="spermogramme_results")

    # Relation avec la table Personnel (validateur)
    validateur = relationship(
        "Personnel",
        foreign_keys=[validateur_id],  # Spécifiez ici la clé étrangère pour éviter l'ambiguïté
        backref="spermogramme_validations"
    )

    # Relation avec la table Personnel (stamped_by)
    stamped_validator = relationship(
        "Personnel",
        foreign_keys=[stamped_by],  # Spécifiez ici la clé étrangère pour éviter l'ambiguïté
        backref="spermogramme_griffes"
    )

    def __repr__(self):
        return (f"<SpermogrammeResult(id={self.id}, analyse_id={self.analyse_id}>")

class BacterioResult(Base):
    __tablename__ = 'bacterio_results'

    id = Column(Integer, primary_key=True, autoincrement=True)
    analyse_id = Column(Integer, ForeignKey('analyses.id'), nullable=False)  # Lien avec l'analyse correspondante
    germe_identifie = Column(Integer, ForeignKey('germes.id'), nullable=True)
    germe_identifie2 = Column(String, nullable=True)  # Exemple : "Escherichia coli"
    comptage_colonies = Column(Integer, nullable=True)  # Exemple : 10^5 CFU/mL pour ECBU
    presence_leucocytes = Column(String, nullable=True)  # Exemple : "Présent", "Absent"
    antibiogramme = Column(TEXT, nullable=True)  # Sensibilité aux antibiotiques (texte libre ou structuré)
    conclusion = Column(TEXT, nullable=True)  # Interprétation clinique
    validateur_id = Column(Integer, ForeignKey('personals.id'), nullable=True)  # ID du personnel ayant validé le résultat
    validation_date = Column(DateTime, nullable=True)
    is_stamped = Column(Boolean, nullable=False, default=False)  # Indique si le résultat a reçu une griffe
    stamped_by = Column(Integer, ForeignKey('personals.id'), nullable=True)  # ID du personnel qui a apposé la griffe
    stamped_at = Column(DateTime, nullable=True)  # Date de la griffe
    type_prelevement = Column(String, nullable=True)
    antibio_results = relationship("AntibioResult", back_populates="bacterio_results")
    analyse = relationship("Analyse", back_populates="bacterio_results")    
# Table d'association entre Germes et Milieux de culture
germes_milieux = Table(
    'germes_milieux', Base.metadata,
    Column('germe_id', Integer, ForeignKey('germes.id'), primary_key=True),
    Column('milieu_id', Integer, ForeignKey('milieux_culture.id'), primary_key=True)
)

class Germe(Base):
    __tablename__ = 'germes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nom = Column(String, nullable=False, unique=True)  # Exemple : "Escherichia coli"
    genre = Column(String, nullable=False)  # Exemple : "Escherichia"
    espece = Column(String, nullable=False)  # Exemple : "coli"
    gram = Column(String, nullable=False)  # Positif ou Négatif
    morphologie = Column(String)  # Bacille, Cocci, Spirale, etc.
    mobilite = Column(Boolean, default=False)  # Mobile ou non
    aero_anaero = Column(String)  # Aérobie, Anaérobie, Facultatif
    pathogenicite = Column(String)  # Infections causées
    croissance_optimum = Column(Float)  # Température de croissance en °C
    test_biologique = Column(String)  # Ex : Oxydase, Catalase, Urease
    aspect_colonie = Column(String)  # Description visuelle

    # Relations
    resistances = relationship("Resistance", back_populates="germe")
    milieux_culture = relationship("MilieuCulture", secondary=germes_milieux, back_populates="germes")

class MilieuCulture(Base):
    __tablename__ = 'milieux_culture'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nom = Column(String, nullable=False, unique=True)  # Ex : Gélose MacConkey, gélose chocolat
    description = Column(String)  # Détails sur le milieu
    
    germes = relationship("Germe", secondary=germes_milieux, back_populates="milieux_culture")

class Antibiotique(Base):
    __tablename__ = 'antibiotiques'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nom = Column(String, nullable=False, unique=True)  # Ex : Amoxicilline, Ciprofloxacine
    code = Column(String, nullable=False, unique=True)
    categorie = Column(String, nullable=True)
    description = Column(String, nullable=True)

    antibio_results = relationship("AntibioResult", back_populates="antibiotique")

class Resistance(Base):
    __tablename__ = 'resistances'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    germe_id = Column(Integer, ForeignKey('germes.id'), nullable=False)
    antibiotique_id = Column(Integer, ForeignKey('antibiotiques.id'), nullable=False)
    
    germe = relationship("Germe", back_populates="resistances")
    antibiotique = relationship("Antibiotique")


class AntibioResult(Base):
    __tablename__ = 'antibio_results'
    id = Column(Integer, primary_key=True, autoincrement=True)
    bacterio_result_id = Column(Integer, ForeignKey('bacterio_results.id'), nullable=False)
    antibiotique_id = Column(Integer, ForeignKey('antibiotiques.id'))
    resultat = Column(String, nullable=True)  # Exemple : "Sensible", "Résistant", "Intermédiaire"
    diametre = Column(Float, nullable=True)
    cmi = Column(Float, nullable=True)
    
    bacterio_results = relationship("BacterioResult", back_populates="antibio_results")
    antibiotique = relationship("Antibiotique", back_populates="antibio_results")
    

# Modèle pour la table 'antibio_groups'
class AntibioGroup(Base):
    __tablename__ = 'antibio_groups'
    group_id = Column(Integer, primary_key=True, autoincrement=True)
    group_name = Column(String, nullable=False, unique=True)

    # Relation avec les ATB via une table intermédiaire
    antibiotiques = relationship(
        "Antibiotique",
        secondary="group_antibio",
        backref="groups"
    )
    def __repr__(self):
        return f"<AntibioGroup(id={self.group_id}, name='{self.group_name}')>"


# Table intermédiaire pour associer les groupes aux ATB
group_antibiotiques_table = Table(
    'group_antibio',
    Base.metadata,
    Column('group_id', Integer, ForeignKey('antibio_groups.group_id'), primary_key=True),
    Column('antibiotique_id', Integer, ForeignKey('antibiotiques.id'), primary_key=True)
)



class Barcode(Base):
    __tablename__ = 'barcodes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    barcode_value = Column(String, nullable=False, unique=True)  # Valeur du code à barres
    analyse_id = Column(Integer, ForeignKey('analyses.id'), nullable=False)  # Lien vers l'analyse
    prelevement_type_id = Column(Integer, ForeignKey('prelevement_types.id'), nullable=False)  # Type de prélèvement
    tube_id = Column(Integer, ForeignKey('tubes.tube_id'), nullable=False)  # Tube utilisé
    created_at = Column(DateTime, nullable=False, default=datetime.now)  # Date de création

    analyse = relationship("Analyse", backref="barcodes")
    prelevement_type = relationship("PrelevementType", backref="barcodes")
    tube = relationship("Tube", backref="barcodes")

    def __repr__(self):
        return f"<Barcode {self.barcode_value}>"


class Frottis(Base):
    __tablename__ = "frottis"
    id = Column(Integer, primary_key=True, autoincrement=True)
    analyse_id = Column(Integer, ForeignKey("analyses.id"), nullable=False)  # Lien avec la table patients
    type_frottis = Column(String, nullable=True)
    #frottis du sang peripherique
    comment_hematies1 = Column(String, nullable=True)  # Nombre d'hématies observées
    comment_hematies2 = Column(String, nullable=True)  # Nombre d'hématies observées
    comment_hematies3 = Column(String, nullable=True)  # Nombre d'hématies observées
    pnn = Column(String, nullable=True)  # Nombre de  	POLYNUCLEAIRES NEUTROPHILES  observés  
    eosinophile = Column(String, nullable=True)  # Nombre de EOSINOPHILES observés 	
    basophile = Column(String, nullable=True)  # Nombre de basophile observés 	 	 
    lymphocyte  = Column(String, nullable=True)  # Nombre de LYMPHOCYTES  observés 		 
    monocyte = Column(String, nullable=True)  # Nombre de MONOCYTES  observés 		 
    comment_equ_leuc = Column(String, nullable=True)  # 	  	 
    comment_pla1 = Column(String, nullable=True)  # 
    comment_pla2 = Column(String, nullable=True)  # 	 
    conclusion = Column(String, nullable=True)  # conclusion frottis sanguin
    #frottis de la moelle
    richesse_moelle  = Column(String, nullable=True)  
    megacaryocyte  = Column(String, nullable=True)  
    proerythroblaste  = Column(String, nullable=True)  
    erythroblaste_basophile  = Column(String, nullable=True)  
    erythroblaste_polychromatophile = Column(String, nullable=True)  
    erythroblaste_acidophile = Column(String, nullable=True)  	 
    lignee_neutrophile   = Column(String, nullable=True)  
    promyelocyte  = Column(String, nullable=True)  	 
    myelocyte  = Column(String, nullable=True) 	 
    metamyelocyte = Column(String, nullable=True) 
    pnn = Column(String, nullable=True)  	 
    lignee_eosinophile = Column(String, nullable=True) 
    lignee_basophile = Column(String, nullable=True) 
    Lymphocytes  = Column(String, nullable=True) 
    blastes  = Column(String, nullable=True) 
    Monocytes  = Column(String, nullable=True) 
    Plasmocytes  = Column(String, nullable=True) 
    Autres  = Column(String, nullable=True) 
    conclusion = Column(String, nullable=True)  
    flore_bacterienne = Column(String, nullable=True)

    analyse = relationship("Analyse", back_populates="frottis_results") 

    __table_args__ = (
        Index('idx_frottis_analyse_id', 'analyse_id'),  # Index sur analyse_id
        Index('idx_frottis_type', 'type_frottis'),      # Index sur type_frottis
    )

class NumerationFormuleSanguine(Base):
    __tablename__ = "nfs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    analyse_id = Column(Integer, ForeignKey('analyses.id'), nullable=False)  # Lien avec l'analyse correspondante
    date_resultat = Column(DateTime, nullable=True, default=datetime.now)  # Date du résultat
    validateur_id = Column(Integer, ForeignKey('personals.id'), nullable=True)  # ID du personnel ayant validé le résultat
    validation_date = Column(DateTime, nullable=True)
    is_stamped = Column(Boolean, nullable=False, default=False)  # Indique si le résultat a reçu une griffe
    stamped_by = Column(Integer, ForeignKey('personals.id'), nullable=True)  # ID du personnel qui a apposé la griffe
    stamped_at = Column(DateTime, nullable=True)  # Date de la griffe
    comments = Column(TEXT, nullable=True)  # Commentaires sur le résultat
    conclusion = Column(TEXT, nullable=True)  # Commentaires sur le résultat
    analyse = relationship("Analyse", back_populates="nfs_results")

    # Paramètres globaux
    hemoglobine = Column(Float)  # g/dL
    hematocrite = Column(Float)  # %
    globules_rouges = Column(Float)  # millions/mm³
    globules_blancs = Column(Float)  # G/L
    plaquettes = Column(Float)  # G/L

    # Paramètres des globules rouges
    vgm = Column(Float)  # fL
    tcmh = Column(Float)  # pg
    ccmh = Column(Float)  # g/dL
    rdw = Column(Float)  # %
    reticulocytes = Column(Float)  # ‰
    ipr = Column(Float)  # Indice de production réticulocytaire

    # Paramètres des globules blancs (leucocytes)
    neutrophiles = Column(Float)  # %
    eosinophiles = Column(Float)  # %
    basophiles = Column(Float)  # %
    lymphocytes = Column(Float)  # %
    monocytes = Column(Float)  # %

    # Paramètres des plaquettes
    vpm = Column(Float)  # fL
    pdw = Column(Float)  # %
    ipf = Column(Float)  # %
    
    # Autres paramètres optionnels
    ret_he = Column(Float)  # Hémoglobine réticulocytaire
    indice_hypochrome = Column(Float)  # %
    irf = Column(Float)  # Fraction immature des réticulocytes
    nlr = Column(Float)  # Neutrophiles / Lymphocytes
    plr = Column(Float)  # Plaquettes / Lymphocytes
    mlr = Column(Float)  # Monocytes / Lymphocytes

    def __repr__(self):
        return (
            f"<NFS(id={self.id}, date={self.date_resultat}, "
            f"Hb={self.hemoglobine} g/dL, Ht={self.hematocrite} %, "
            f"GR={self.globules_rouges} millions/mm³, GB={self.globules_blancs} G/L, "
            f"Plaquettes={self.plaquettes} G/L)>")


class GroupageSanguin(Base):
    __tablename__ = "groupage_sanguin"

    id = Column(Integer, primary_key=True, autoincrement=True)
    analyse_id = Column(Integer, ForeignKey('analyses.id'), nullable=False)  # Lien avec l'analyse correspondante
    date_resultat = Column(DateTime, nullable=True, default=datetime.now)  # Date du résultat
    validateur_id = Column(Integer, ForeignKey('personals.id'), nullable=True)  # ID du personnel ayant validé le résultat
    validation_date = Column(DateTime, nullable=True)
    is_stamped = Column(Boolean, nullable=False, default=False)  # Indique si le résultat a reçu une griffe
    stamped_by = Column(Integer, ForeignKey('personals.id'), nullable=True)  # ID du personnel qui a apposé la griffe
    stamped_at = Column(DateTime, nullable=True)  # Date de la griffe
    conclusion = Column(TEXT, nullable=True)  # Commentaires sur le résultat

    # Référence au patient (optionnelle, si vous avez une table `patients`)
    patient_id = Column(String, ForeignKey("patients.id"), nullable=False)

    # Résultats du groupage ABO
    groupe_sanguin = Column(String(2), nullable=True, doc="Groupe sanguin (A, B, AB, O)")
    rhésus = Column(String(3), nullable=True, doc="Facteur Rhésus (+ ou -)")

    # Détection d'anticorps irréguliers
    anticorps_irreguliers = Column(Boolean, default=True, doc="Présence d'anticorps irréguliers")
    details_anticorps = Column(TEXT, nullable=True, doc="Détails sur les anticorps détectés")

    # Informations supplémentaires
    methode_utilisee = Column(String(50), nullable=True, doc="Méthode utilisée pour le test")
    commentaires = Column(TEXT, nullable=True, doc="Commentaires ou observations")
    analyse = relationship("Analyse", back_populates="groupage_results") 
    def __repr__(self):
        return (
            f"<GroupageSanguin(id={self.id}, date={self.date_analyse}, "
            f"groupe_sanguin={self.groupe_sanguin}, rhésus={self.rhésus}, "
            f"anticorps_irreguliers={self.anticorps_irreguliers})>")





class Laboratoire(Base):
    __tablename__ = 'mon_laboratoire'
    id = Column(Integer, primary_key=True, autoincrement=True)
   # is_default = Column(Boolean, nullable=False, default=True, unique=True)  # Assure qu'il n'y a qu'un seul laboratoire par défaut
    nom = Column(String, nullable=False)  # Nom du laboratoire
    docteur = Column(String, nullable=False)  # Nom du medecin
    specialite = Column(String, nullable=False)  # specialité
    numero_agr = Column(String, nullable=True)  # AGR du laboratoire
    griffe_path = Column(String, nullable=True)  # Chemin vers la griffe du laboratoire
    email = Column(String, nullable=True)  # Email du laboratoire
    adresse = Column(String, nullable=True)  # Adresse physique
    telephone1 = Column(String, nullable=True)  # Numéro de téléphone
    telephone2 = Column(String, nullable=True)  # Numéro de téléphone
    site_web = Column(String, nullable=True)  # Site web
    logo_path = Column(String, nullable=True)  # Chemin vers le logo du laboratoire
    horaire_ouverture = Column(String, nullable=True)  # Horaire du laboratoire


    def __repr__(self):
        return f"<Laboratoire(id={self.id}, nom='{self.nom}', email='{self.email}')>"



