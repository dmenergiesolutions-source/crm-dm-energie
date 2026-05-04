from flask import Flask, request, send_file, jsonify, send_from_directory
from flask_cors import CORS
import json, io, datetime, os, sys

FRONTEND = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend')
app = Flask(__name__, static_folder=FRONTEND)
CORS(app, origins=["https://dmenergiesolutions.fr", "https://app.dmenergiesolutions.fr", "http://localhost:3000", "http://localhost:5173", "null"], supports_credentials=False)

# Chemin des assets (logos)
BASE = os.path.dirname(os.path.abspath(__file__))

# Import du moteur PDF
sys.path.insert(0, BASE)

# Override BASE dans pdf_engine
import pdf_engine
pdf_engine.BASE = BASE

from pdf_engine import generate_pdf, build_prestations

@app.route('/')
def index():
    return send_from_directory(FRONTEND, 'index.html')

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'version': '1.0.0'})

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Données manquantes'}), 400

        form = data.get('form', {})
        sim  = data.get('sim', {})
        doc_type = data.get('type', 'devis')
        numero = data.get('numero', f"{datetime.datetime.now().year}-1010")

        prestations = build_prestations(sim)
        if not prestations:
            return jsonify({'error': 'Aucune prestation sélectionnée'}), 400

        devis_data = {
            'numero': numero,
            'type': doc_type,
            'date': datetime.datetime.now().strftime('%d/%m/%Y'),
            'devis_ref': f'Devis n° {form.get("devis_numero","")} du {form.get("devis_date","")}' if doc_type == 'facture' else '',
            'client': {
                'civilite':       form.get('civilite', 'M.'),
                'nom':            form.get('nom', ''),
                'adresse':        form.get('adresse', ''),
                'cp_ville':       form.get('ville', ''),
                'tel':            form.get('tel', ''),
                'email':          form.get('email', 'Néant'),
                'zone':           form.get('zone', 'H1'),
                'chauffage':      form.get('chauffage', ''),
                'logement':       form.get('logement', '') or f"Maison individuelle / +15 ans / {form.get('shab','')} m²",
                'adresse_travaux': form.get('adrtravaux', 'Idem adresse client'),
                'shab':           form.get('shab', ''),
            },
            'audit': {
                'date':     form.get('audit_date', ''),
                'ref':      form.get('audit_ref', ''),
                'logiciel': form.get('audit_logiciel', 'BATI AUDIT, version 1.1.55.0'),
                'cep_ini':  form.get('cep_ini', ''),
                'cep_proj': form.get('cep_proj', ''),
                'dpe_avant':form.get('dpe_avant', ''),
                'dpe_apres':form.get('dpe_apres', ''),
            },
            'notes': form.get('notes', ''),
            'prestations': prestations,
        }

        pdf_buf = generate_pdf(devis_data)
        nom_client = form.get('nom', 'client').replace(' ', '_')
        titre = 'Facture' if doc_type == 'facture' else 'Devis'
        filename = f"{titre}_{numero}_{nom_client}.pdf"

        return send_file(
            pdf_buf,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5050))
    app.run(host='0.0.0.0', port=port, debug=False)
