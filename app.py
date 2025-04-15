from flask import Flask, render_template
from sqlalchemy.orm import sessionmaker
from models import Patient, Analyse, Resultat  # Importez vos modèles SQLAlchemy
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os



# Charger les variables d'environnement
load_dotenv()

# Initialisation de Flask
app = Flask(__name__)
application = app

# Configuration de la base de données
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

@app.route('/')
def index():
    return "hello"

@app.route('/about')
def about():
    return "laboratoire d'analyses médicales"

@app.route('/<patient_barcode>', methods=['GET'])
def get_results(patient_barcode):
    session = Session()
    try:
        # Rechercher le patient par son code-barres
        patient = session.query(Patient).filter_by(patient_barcode=patient_barcode).first()
        if not patient:
            return "Patient non trouvé", 404

        # Récupérer toutes les analyses associées au patient
        analyses = (
            session.query(Analyse)
            .filter_by(patient_id=patient.id)
            .all()
        )

        if not analyses:
            return "Aucun résultat disponible pour ce patient.", 404

        # Formater les résultats pour chaque analyse
        formatted_results = []
        for analyse in analyses:
            # Vérifier les types d'analyses basés sur les champs booléens
            analysis_types = []
            if analyse.is_nfs:
                analysis_types.append("NFS")
            if analyse.is_groupage:
                analysis_types.append("Groupage Sanguin")
            if analyse.is_frottis:
                analysis_types.append("Frottis")
            if analyse.is_spermo:
                analysis_types.append("Spermogramme")
            if analyse.is_bacterio:
                analysis_types.append("Bactériologie")
            if analyse.is_special:
                analysis_types.append("Analyse Spéciale")
            if analyse.is_autre_analyse:
                analysis_types.append("Autre Analyse")
            if analyse.is_soustraitance:
                analysis_types.append("Soustraitance")

            # Récupérer les résultats spécifiques pour cette analyse
            resultats = session.query(Resultat).filter_by(analyse_id=analyse.id).all()
            formatted_resultats = [
                {
                    "parameter": resultat.parameter.param,
                    "valeur": resultat.valeur,
                    "date": resultat.result_date.strftime("%Y-%m-%d %H:%M:%S") if resultat.result_date else None,
                }
                for resultat in resultats
            ]

            formatted_results.append({
                "analyse_id": analyse.id,
                "types_analyses": analysis_types,
                "resultats": formatted_resultats,
            })

        # Renvoyer les résultats sous forme de page HTML
        return render_template(
            "results.html",
            nom=patient.name,
            prenom=patient.prenom,
            adresse=patient.adresse,
            email=patient.email,
            tel=patient.tel,
            resultats=formatted_results
        )

    except Exception as e:
        return f"Erreur : {str(e)}", 500
    finally:
        session.close()

if __name__ == '__main__':
    app.run(debug=True)