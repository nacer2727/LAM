from flask import Flask, jsonify, request, render_template
from sqlalchemy.orm import sessionmaker
from models import Patient, Analyse, Resultat  # Importez vos modèles SQLAlchemy
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os


# Charger les variables d'environnement
load_dotenv()

# Initialisation de Flask
app = Flask(__name__)

# Configuration de la base de données
DATABASE_URL = os.getenv("DATABASE_URL")
#DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

@app.route('/<patient_barcode>', methods=['GET'])
def get_results(patient_barcode):
    session = Session()
    try:
        # Rechercher le patient par son code-barres
        patient = session.query(Patient).filter_by(patient_barcode=patient_barcode).first()
        if not patient:
            return "Patient non trouvé", 404

        # Récupérer toutes les analyses terminées et payées pour ce patient
        analyses = (
            session.query(Analyse)
            .filter_by(patient_id=patient.id)
            .filter(Analyse.state == "TERMINEE")
            .filter(Analyse.montant_r == 0)
            .all()
        )

        if not analyses:
            return "Aucun résultat disponible pour ce patient.", 404

        # Formater les résultats pour chaque analyse
        formatted_results = []
        for analyse in analyses:
            resultats = session.query(Resultat).filter_by(analyse_id=analyse.id).all()
            formatted_resultats = [
                {
                    "parameter": resultat.parameter.param,
                    "valeur": resultat.valeur,
                    "date": resultat.result_date.strftime("%Y-%m-%d %H:%M:%S"),
                }
                for resultat in resultats
            ]
            formatted_results.append({
                "analyse_id": analyse.id,
                "resultats": formatted_resultats,
            })

        # Renvoyer les résultats sous forme de page HTML
        return render_template(
            "results.html",
            nom=patient.name,
            prenom=patient.prenom,
            resultats=formatted_results
        )

    except Exception as e:
        return f"Erreur : {str(e)}", 500
    finally:
        session.close()

if __name__ == '__main__':
    app.run(debug=True)