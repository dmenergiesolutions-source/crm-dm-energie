from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from reportlab.pdfgen import canvas as pdfcanvas
import json, io, os, datetime, base64

BASE = '/home/claude'

# ─── COULEURS ────────────────────────────────────────────────────────────────
BLEU_DM    = colors.HexColor('#1B3A6B')
BLEU_CIEL  = colors.HexColor('#4BA3C7')
BLEU_CTR   = colors.HexColor('#3A7DBF')
GRIS_DESC  = colors.HexColor('#555555')
GRIS_LIGNE = colors.HexColor('#DEDEDE')
GRIS_CLAIR = colors.HexColor('#F7F7F7')
BLANC      = colors.white

# ─── DONNÉES FIXES PAR PRESTATION ───────────────────────────────────────────
PRESTA_DATA = {
    'ite': {
        'titre': "Mise en place d'une isolation thermique des murs par l'extérieur",
        'produit_description': "Marque POLYPROD, Référence POLYPRO-ITE G TH31 140mm, Epaisseur 140 mm\nRésistance thermique 4,5 m².K/W évaluée selon la norme NF EN 12664, la norme NF EN 12667 ou la norme NF EN 12939 pour les isolants non réfléchissants.\nCertification Acermi 15 / 150 / 1045",
        'sous_traitant': "Travaux sous-traités auprès de l'entreprise ITAL-ISOL, 32 RUE CLEMENT ADER, 91280 SAINT-PIERRE-DU-PERRAY\nreprésentée par CHIFA ANDREI, SIRET 90795204800037, Certificat RGE N° E-E201207 attribué le 03/10/2024 valable jusqu'au 02/10/2025, Assurance civile N° AXE2401531",
        'pu_mat_ht': 88.15, 'pu_mat_ttc': 93.00, 'label_mat': 'POLYPRO-ITE G TH31 140mm',
        'pu_mo_ht': 103.32, 'pu_mo_ttc': 109.00, 'label_mo': "Main d'œuvre pour travaux isolation des murs par l'extérieur",
        'unite': 'm²',
    },
    'combles': {
        'titre': "Mise en place d'une isolation thermique en combles perdus",
        'produit_description': "Marque ISOVER, Référence ECOLAINE COMBLES PERDUS, Epaisseur 280 mm\nRésistance thermique 7 m².K/W évaluée selon la norme NF EN 12664, la norme NF EN 12939.\nCertification Acermi 16/018/1186\nAucun aménagement n'a été nécessaire (caches spot, pare-vapeur, écart au feu, contour de trappe, pige de repérage)",
        'sous_traitant': "Travaux sous-traités auprès de l'entreprise ITAL-ISOL, 32 RUE CLEMENT ADER, 91280 SAINT-PIERRE-DU-PERRAY\nreprésentée par CHIFA ANDREI, SIRET 90795204800037, Certificat RGE N° E-E201207 attribué le 03/10/2024 valable jusqu'au 02/10/2025, Assurance civile N° AXE2401531",
        'pu_mat_ht': 28.44, 'pu_mat_ttc': 30.00, 'label_mat': 'ECOLAINE COMBLES PERDUS',
        'pu_mo_ht': 66.35, 'pu_mo_ttc': 70.00, 'label_mo': "Main d'œuvre pour travaux isolation des combles perdus",
        'unite': 'm²',
    },
    'rampants': {
        'titre': "Mise en place d'une isolation thermique en rampants de toiture",
        'produit_description': "Marque ISOVER, Référence ECOLAINE COMBLES PERDUS, Epaisseur 280 mm\nRésistance thermique 7 m².K/W. Certification Acermi 16/018/1186\nAucun aménagement n'a été nécessaire (caches spot, pare-vapeur, écart au feu, contour de trappe, pige de repérage)",
        'sous_traitant': "Travaux sous-traités auprès de l'entreprise ITAL-ISOL, 32 RUE CLEMENT ADER, 91280 SAINT-PIERRE-DU-PERRAY\nreprésentée par CHIFA ANDREI, SIRET 90795204800037, Certificat RGE N° E-E201207 attribué le 03/10/2024 valable jusqu'au 02/10/2025, Assurance civile N° AXE2401531",
        'pu_mat_ht': 28.44, 'pu_mat_ttc': 30.00, 'label_mat': 'ECOLAINE COMBLES PERDUS',
        'pu_mo_ht': 66.35, 'pu_mo_ttc': 70.00, 'label_mo': "Main d'œuvre pour travaux isolation des rampants",
        'unite': 'm²',
    },
    'plancher': {
        'titre': "Mise en place d'une isolation thermique en Plancher bas",
        'produit_description': "Marque POLYPROD, Référence POLYPRO ITI G TH32, Epaisseur 100 mm\nRésistance thermique 3,1 m².K/W évaluée selon la norme NF EN 12664, la norme NF EN 12939.\nCertification Acermi 12 / 150 / 801\nAucun aménagement n'a été nécessaire (caches spot, pare-vapeur, écart au feu, contour de trappe, pige de repérage)",
        'sous_traitant': "Travaux sous-traités auprès de l'entreprise ITAL-ISOL, 32 RUE CLEMENT ADER, 91280 SAINT-PIERRE-DU-PERRAY\nreprésentée par CHIFA ANDREI, SIRET 90795204800037, Certificat RGE N° E-E201207 attribué le 03/10/2024 valable jusqu'au 02/10/2025, Assurance civile N° AXE2401531",
        'pu_mat_ht': 36.97, 'pu_mat_ttc': 39.00, 'label_mat': 'POLYPRO ITI G TH32',
        'pu_mo_ht': 55.92, 'pu_mo_ttc': 59.00, 'label_mo': "Main d'œuvre pour travaux isolation du plancher bas",
        'unite': 'm²',
    },
    'ballon': {
        'titre': "Mise en place d'un chauffe-eau thermodynamique à accumulation",
        'produit_description': "Type d'installation : Sur air extrait\nMarque : THERMOR — Réf : AEROMAX 5 - 200L\nCOP à 7°C : 3,38 mesuré selon les conditions de la norme EN 16147.\nCapacité : 200l — Rendement énergétique Eta wh : 133%",
        'sous_traitant': "Matériel(s) fourni(s) et mis en place par notre société DM ENERGIE SOLUTIONS\nreprésentée par DJELLAL BILLEL, SIRET 90040094600019, Certificat RGE N° QPAC/65683 attribué le 02/10/2024 valable jusqu'au 02/10/2025",
        'pu_mat_ht': 3270.14, 'pu_mat_ttc': 3450.00, 'label_mat': 'AEROMAX 5 - 200L',
        'pu_mo_ht': 1137.44, 'pu_mo_ttc': 1200.00, 'label_mo': "Forfait pose et mise en service d'un chauffe-eau thermodynamique",
        'unite': 'U',
    },
    'vmc': {
        'titre': "Mise en place d'une VMC simple flux",
        'produit_description': "Caisson de ventilation basse consommation\nMarque : ATLANTIC — Référence : ATLANTIC Hygrocosy BC / Type B, Basse consommation\nClasse énergétique : B selon le règlement européen (UE) n° 1254/2014.",
        'sous_traitant': "Travaux sous-traités auprès de l'entreprise OPACTI, 85 AVENUE JEAN JAURES, 91200 ATHIS-MONS\nreprésentée par BENHALIMA KHELLIL, SIRET 89750920400029, Certificat RGE N° 66341 attribué le 19/05/2024 valable jusqu'au 19/05/2025",
        'pu_mat_ht': 1895.73, 'pu_mat_ttc': 2000.00, 'label_mat': 'ATLANTIC Hygrocosy BC / Type B, Basse consommation',
        'pu_mo_ht': 1421.80, 'pu_mo_ttc': 1500.00, 'label_mo': "Pose et mise en service d'une VMC simple flux",
        'unite': 'U',
    },
    'pacae': {
        'titre': "Mise en place d'une pompe à chaleur air/eau",
        'produit_description': "Pompe à chaleur air/eau haute performance\nInstallation complète avec pose du réseau hydraulique et électrique",
        'sous_traitant': "Matériel(s) fourni(s) et mis en place par notre société DM ENERGIE SOLUTIONS\nreprésentée par DJELLAL BILLEL, SIRET 90040094600019, Certificat RGE N° QPAC/65683 attribué le 02/10/2024 valable jusqu'au 02/10/2025",
        'pu_mat_ht': 19005.69, 'pu_mat_ttc': 20051.00, 'label_mat': 'PAC Air/Eau',
        'pu_mo_ht': 1327.01, 'pu_mo_ttc': 1400.00, 'label_mo': "Forfait pose et mise en service d'une pompe à chaleur air/eau",
        'unite': 'U',
    },
}

BLOCS_DATA = {
    '3MXM52A9': {'p1': 8500, 'pu_ht': 8000.00, 'pu_ttc': 8440.00},
    '3MXM68A9': {'p1': 9500, 'pu_ht': 9005.69, 'pu_ttc': 9501.00},
    '5MXM90N9': {'p1': 13000, 'pu_ht': 12322.27, 'pu_ttc': 13000.00},
}
SPLITS_DATA = {
    'CTXM15R': {'pu_ht': 928.91, 'pu_ttc': 980.00},
    'FTXM20N': {'pu_ht': 2072.73, 'pu_ttc': 2280.00},
}

def fmt_eur(val):
    s = f"{val:,.2f}".replace(',', '\u202f').replace('.', ',')
    return s + ' €'

def calc_totaux(prestations):
    total_ht = 0.0
    for p in prestations:
        for l in p['lignes']:
            qte = float(str(l['qte']).replace(' m²','').replace(' U','').replace(',','.').split()[0])
            total_ht += l['pu_ht'] * qte
    tva = round(total_ht * 0.055, 2)
    ttc = round(total_ht + tva, 2)
    return round(total_ht, 2), tva, ttc

def build_prestations(form_data):
    """Construit la liste des prestations à partir des données du formulaire"""
    prestations = []
    actifs = form_data.get('actifs', [])

    for pid in ['ite', 'combles', 'rampants', 'plancher']:
        if pid in actifs:
            d = PRESTA_DATA[pid]
            qte = float(form_data.get(f'{pid}_qte', 0))
            qte_str = f"{qte:.2f}".replace('.', ',') + ' m²'
            prestations.append({
                'titre': d['titre'],
                'produit_description': d['produit_description'],
                'sous_traitant': d['sous_traitant'],
                'lignes': [
                    {'designation': d['label_mat'], 'qte': qte_str, 'pu_ht': d['pu_mat_ht'], 'pu_ttc': d['pu_mat_ttc'], 'tva': '5,50%'},
                    {'designation': d['label_mo'],  'qte': qte_str, 'pu_ht': d['pu_mo_ht'],  'pu_ttc': d['pu_mo_ttc'],  'tva': '5,50%'},
                ]
            })

    for pid in ['ballon', 'vmc', 'pacae']:
        if pid in actifs:
            d = PRESTA_DATA[pid]
            nb = int(form_data.get(f'{pid}_nb', 1))
            qte_str = f"{nb},00 U"
            prestations.append({
                'titre': d['titre'],
                'produit_description': d['produit_description'],
                'sous_traitant': d['sous_traitant'],
                'lignes': [
                    {'designation': d['label_mat'], 'qte': qte_str, 'pu_ht': d['pu_mat_ht'], 'pu_ttc': d['pu_mat_ttc'], 'tva': '5,50%'},
                    {'designation': d['label_mo'],  'qte': '1,00 U', 'pu_ht': d['pu_mo_ht'],  'pu_ttc': d['pu_mo_ttc'],  'tva': '5,50%'},
                ]
            })

    if 'pacaa' in actifs:
        bloc_ref = form_data.get('bloc_ref', '3MXM52A9')
        splits = form_data.get('splits', [])
        bloc = BLOCS_DATA.get(bloc_ref, BLOCS_DATA['3MXM52A9'])
        lignes = [
            {'designation': f'DAIKIN - {bloc_ref}', 'qte': '1,00', 'pu_ht': bloc['pu_ht'], 'pu_ttc': bloc['pu_ttc'], 'tva': '5,50%'},
            {'designation': "Forfait pose et mise en service d'une pompe à chaleur air/air", 'qte': '1,00 Forfait', 'pu_ht': 6635.07, 'pu_ttc': 7000.00, 'tva': '5,50%'},
        ]
        nb_splits = 0
        for sp in splits:
            ref = sp.get('ref', 'CTXM15R')
            qty = int(sp.get('qty', 1))
            nb_splits += qty
            sd = SPLITS_DATA.get(ref, SPLITS_DATA['CTXM15R'])
            lignes.append({'designation': f'Split {ref}', 'qte': f'{qty},00 U', 'pu_ht': sd['pu_ht'], 'pu_ttc': sd['pu_ttc'], 'tva': '5,50%'})
        prestations.append({
            'titre': "Mise en place d'une pompe à chaleur de type air/air",
            'produit_description': f"Marque : DAIKIN — Modèle : MXM\nRéférence : {bloc_ref}\nNombre de splits intérieurs : {nb_splits}",
            'sous_traitant': "Matériel(s) fourni(s) et mis en place par notre société DM ENERGIE SOLUTIONS\nreprésentée par DJELLAL BILLEL, SIRET 90040094600019, Certificat RGE N° QPAC/65683 attribué le 02/10/2024 valable jusqu'au 02/10/2025",
            'lignes': lignes,
        })

    return prestations

def generate_pdf(devis_data):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
        leftMargin=15*mm, rightMargin=15*mm,
        topMargin=10*mm, bottomMargin=22*mm)
    W = A4[0] - 30*mm
    story = []

    # Styles
    s_normal   = ParagraphStyle('n',  fontSize=8,   leading=12, textColor=colors.black)
    s_small    = ParagraphStyle('sm', fontSize=7.5, leading=11, textColor=GRIS_DESC)
    s_bold     = ParagraphStyle('b',  fontSize=8,   leading=12, fontName='Helvetica-Bold', textColor=colors.black)
    s_col_hd   = ParagraphStyle('ch', fontSize=8,   leading=11, fontName='Helvetica-Bold', alignment=TA_CENTER, textColor=BLANC)
    s_right    = ParagraphStyle('r',  fontSize=8,   leading=12, alignment=TA_RIGHT)
    s_center   = ParagraphStyle('c',  fontSize=8,   leading=12, alignment=TA_CENTER)
    s_tsec     = ParagraphStyle('ts', fontSize=8.5, leading=13, fontName='Helvetica-Bold', textColor=BLEU_DM)
    s_dnum     = ParagraphStyle('dn', fontSize=14,  leading=17, fontName='Helvetica-Bold', textColor=BLEU_DM)
    s_cnm      = ParagraphStyle('cn', fontSize=12,  leading=15, fontName='Helvetica-Bold', textColor=BLEU_DM)
    s_contact  = ParagraphStyle('ct', fontSize=7.5, leading=11, textColor=BLEU_CTR)
    s_tot_lbl  = ParagraphStyle('tl', fontSize=8.5, leading=12, fontName='Helvetica-Bold', textColor=colors.black)
    s_tot_val  = ParagraphStyle('tv', fontSize=8.5, leading=12, fontName='Helvetica-Bold', alignment=TA_RIGHT, textColor=colors.black)
    s_rac_lbl  = ParagraphStyle('rl', fontSize=10,  leading=13, fontName='Helvetica-Bold', textColor=BLANC)
    s_rac_val  = ParagraphStyle('rv', fontSize=10,  leading=13, fontName='Helvetica-Bold', alignment=TA_RIGHT, textColor=BLANC)
    s_ligne    = ParagraphStyle('lg', fontSize=8,   leading=12, textColor=colors.black)
    s_tot_ht   = ParagraphStyle('th', fontSize=8,   leading=12, fontName='Helvetica-Bold', alignment=TA_RIGHT)

    # ── EN-TÊTE
    logo_dm = Image(f'{BASE}/Logo_DM.PNG', width=58*mm, height=19*mm)
    logo_qp = Image(f'{BASE}/Qualipac_v2_transparent.png', width=30*mm, height=19*mm)
    logo_vp = Image(f'{BASE}/ventil_v2_transparent.png', width=32*mm, height=19*mm)

    left_col = Table([[logo_dm],[Paragraph('Tél : 06 43 84 02 28', s_contact)],[Paragraph('dmenergiesolutions@gmail.com', s_contact)]], colWidths=[80*mm])
    left_col.setStyle(TableStyle([('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0),('TOPPADDING',(0,0),(-1,-1),1),('BOTTOMPADDING',(0,0),(-1,-1),1),('VALIGN',(0,0),(-1,-1),'TOP')]))

    rge_col = Table([[logo_qp, logo_vp]], colWidths=[29*mm, 33*mm])
    rge_col.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('ALIGN',(0,0),(-1,-1),'RIGHT'),('LEFTPADDING',(0,0),(-1,-1),3),('RIGHTPADDING',(0,0),(-1,-1),0),('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),0)]))

    header = Table([[left_col,'',rge_col]], colWidths=[80*mm, W-80*mm-62*mm, 62*mm])
    header.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('ALIGN',(2,0),(2,0),'RIGHT'),('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0),('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),0)]))
    story.append(header)
    story.append(Spacer(1, 3*mm))
    story.append(HRFlowable(width=W, thickness=0.8, color=BLEU_CIEL, spaceAfter=5*mm))

    # ── BLOC DEVIS ou FACTURE + CLIENT
    c = devis_data['client']
    is_facture = devis_data.get('type') == 'facture'
    titre_doc = 'FACTURE' if is_facture else 'DEVIS'
    left_items = [
        Paragraph(f'<b>{titre_doc} : {devis_data["numero"]}</b>', s_dnum),
        Spacer(1, 3*mm),
        Paragraph(f'Numéro Client : <b>DES-{devis_data.get("devis_ref","").split("n° ")[-1].split(" ")[0] if is_facture else devis_data["numero"]}</b>', s_normal),
        Paragraph(f'Date de {"facture" if is_facture else "devis"} : <b>{devis_data["date"]}</b>', s_normal),
    ]
    if is_facture and devis_data.get('devis_ref'):
        left_items.append(Paragraph(f'{devis_data["devis_ref"]}', s_normal))
    left_items.append(Paragraph(f'Adresse des travaux : <b>{c["adresse_travaux"]}</b>', s_normal))
    right_items = [
        Paragraph(f'<b>{c["civilite"]} {c["nom"]}</b>', s_cnm),
        Spacer(1, 2*mm),
        Paragraph(c['adresse'], s_normal),
        Paragraph(c['cp_ville'], s_normal),
        Spacer(1, 1*mm),
        Paragraph(f'Tél : {c["tel"]}', s_normal),
        Paragraph(f'E-mail : {c["email"]}', s_normal),
        Spacer(1, 1*mm),
        Paragraph(f'Zone : {c["zone"]}', s_normal),
        Paragraph(f'Type de chauffage : {c["chauffage"]}', s_normal),
        Paragraph(f'Type de logement : {c["logement"]}', s_normal),
    ]
    info_table = Table([[left_items, '', right_items]], colWidths=[W*0.38, W*0.12, W*0.50])
    info_table.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0),('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),0),('LINEBEFORE',(2,0),(2,-1),0.5,GRIS_LIGNE),('LEFTPADDING',(2,0),(2,-1),12)]))
    story.append(info_table)

    # ── INTRO AUDIT
    audit = devis_data.get('audit', {})
    shab = c.get('shab', '')
    chauffage_type = c.get('chauffage', '')
    story.append(Spacer(1, 4*mm))
    intro = f"Rénovation thermique d'ampleur d'une maison individuelle existante de surface habitable (Shab) {shab} m², ayant un équipement de production de chaleur utilisant {chauffage_type}."
    story.append(Paragraph(intro, s_normal))
    if audit.get('date'):
        story.append(Spacer(1, 2*mm))
        story.append(Paragraph(f"L'audit énergétique a été réalisé le {audit.get('date','')} par le bureau d'étude AUDIT ENERGETIQUE SOLUTION, n° SIRET 91204062300015, n° RGE étude 24085928 sous la référence {audit.get('ref','')}, en utilisant le logiciel {audit.get('logiciel','BATI AUDIT')}.", s_normal))
        story.append(Spacer(1, 2*mm))
        story.append(Paragraph('<b>Caractéristiques du bâtiment données par l\'étude énergétique :</b>', s_bold))
        if audit.get('cep_ini') and audit.get('cep_proj'):
            story.append(Paragraph(f"* Cep initial : <b>{audit.get('cep_ini')} kWh/m².an</b>  * Cep projet : <b>{audit.get('cep_proj')} kWh/m².an</b>", s_normal))
        if audit.get('dpe_avant') and audit.get('dpe_apres'):
            story.append(Paragraph(f"* Classe avant les travaux de rénovation : <b>{audit.get('dpe_avant')}</b>", s_normal))
            story.append(Paragraph(f"* Classe après les travaux de rénovation : <b>{audit.get('dpe_apres')}</b>", s_normal))
        travaux_label = 'Travaux réalisés :' if is_facture else 'Travaux à réaliser :'
        story.append(Paragraph(f'<b>{travaux_label}</b>', s_bold))
    story.append(Spacer(1, 4*mm))

    # ── EN-TÊTE TABLEAU
    col_w = [W*0.38, W*0.10, W*0.11, W*0.11, W*0.08, W*0.11, W*0.11]
    hrow = [Paragraph(h, s_col_hd) for h in ['Détail','Qté','P.U HT','P.U TTC','TVA','Total HT','Total TTC']]
    htable = Table([hrow], colWidths=col_w)
    htable.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),BLEU_CIEL),('VALIGN',(0,0),(-1,0),'MIDDLE'),('TOPPADDING',(0,0),(-1,0),6),('BOTTOMPADDING',(0,0),(-1,0),6),('LEFTPADDING',(0,0),(0,0),6),('RIGHTPADDING',(0,0),(-1,0),4)]))
    story.append(htable)

    # ── PRESTATIONS
    for presta in devis_data['prestations']:
        rows = []
        spans = []

        def add_span_row(content):
            rows.append([content,'','','','','',''])
            spans.append(('SPAN',(0,len(rows)-1),(-1,len(rows)-1)))

        add_span_row(Paragraph(f'— {presta["titre"]}', s_tsec))
        add_span_row(Spacer(1, 1*mm))
        if presta.get('produit_description'):
            add_span_row(Paragraph(presta['produit_description'].replace('\n','<br/>'), s_small))
        if presta.get('sous_traitant'):
            add_span_row(Paragraph(presta['sous_traitant'].replace('\n','<br/>'), s_small))
        add_span_row(Spacer(1, 1*mm))

        for l in presta['lignes']:
            qte_str = l['qte']
            qte_val = float(qte_str.replace(' m²','').replace(' U','').replace(' Forfait','').replace(',','.').split()[0])
            ht = l['pu_ht'] * qte_val
            ttc = l['pu_ttc'] * qte_val
            rows.append([
                Paragraph(f'<b>{l["designation"]}</b>', s_ligne),
                Paragraph(qte_str, s_center),
                Paragraph(fmt_eur(l['pu_ht']), s_right),
                Paragraph(fmt_eur(l['pu_ttc']), s_right),
                Paragraph(l['tva'], s_center),
                Paragraph(f'<b>{fmt_eur(ht)}</b>', s_tot_ht),
                Paragraph(f'<b>{fmt_eur(ttc)}</b>', s_tot_ht),
            ])

        add_span_row(Spacer(1, 2*mm))
        ptable = Table(rows, colWidths=col_w)
        ts = TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),4),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),('BACKGROUND',(0,0),(-1,0),GRIS_CLAIR),('TOPPADDING',(0,0),(-1,0),7),('BOTTOMPADDING',(0,0),(-1,0),7),('LINEBELOW',(0,-1),(-1,-1),0.5,GRIS_LIGNE)])
        for sp in spans:
            ts.add(*sp)
        ptable.setStyle(ts)
        story.append(ptable)
        story.append(Spacer(1, 3*mm))

    # ── GESTION DÉCHETS
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph('<b>Gestion des déchets</b>', s_bold))
    story.append(Spacer(1, 1*mm))
    story.append(Paragraph("Gestion, évacuation et traitements des déchets de chantier comprenant la main d'œuvre liée à la dépose et au tri, le transport des déchets de chantiers vers un ou plusieurs points de collecte et coûts de traitement.", s_small))
    if devis_data.get('notes'):
        story.append(Spacer(1, 3*mm))
        story.append(Paragraph(devis_data['notes'], s_small))
    story.append(Spacer(1, 6*mm))

    # ── TOTAUX
    total_ht, tva, total_ttc = calc_totaux(devis_data['prestations'])
    tot_data = [
        [Paragraph('Total H.T', s_tot_lbl), Paragraph(fmt_eur(total_ht), s_tot_val)],
        [Paragraph('Total TVA (5,50%)', s_tot_lbl), Paragraph(fmt_eur(tva), s_tot_val)],
        [Paragraph('<b>Total TTC</b>', s_tot_lbl), Paragraph(f'<b>{fmt_eur(total_ttc)}</b>', s_tot_val)],
        [Paragraph('<b>Reste à payer</b>', s_rac_lbl), Paragraph(f'<b>{fmt_eur(total_ttc)}</b>', s_rac_val)],
    ]
    tot_table = Table(tot_data, colWidths=[W*0.72, W*0.28])
    tot_table.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'MIDDLE'),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('BACKGROUND',(0,0),(-1,2),colors.HexColor('#EBF5FA')),('BOX',(0,0),(-1,2),0.5,BLEU_CIEL),('INNERGRID',(0,0),(-1,2),0.5,colors.HexColor('#C5E0EE')),('BACKGROUND',(0,3),(-1,3),BLEU_CIEL),('BOX',(0,3),(-1,3),0.5,BLEU_CIEL),('TOPPADDING',(0,3),(-1,3),7),('BOTTOMPADDING',(0,3),(-1,3),7)]))

    # KeepTogether : totaux + signature jamais coupés entre deux pages
    from reportlab.platypus import KeepTogether
    bloc_final = KeepTogether([
        tot_table,
        Spacer(1, 8*mm),
        Paragraph('Apposer signature précédée de la mention "Bon pour accord"', s_small),
        Spacer(1, 18*mm),
        HRFlowable(width=65*mm, thickness=0.5, color=BLEU_DM),
    ])
    story.append(bloc_final)

    # ── PIED DE PAGE
    class PageCountCanvas(pdfcanvas.Canvas):
        def __init__(self, *args, **kwargs):
            pdfcanvas.Canvas.__init__(self, *args, **kwargs)
            self._saved_page_states = []
        def showPage(self):
            self._saved_page_states.append(dict(self.__dict__))
            self._startPage()
        def save(self):
            num_pages = len(self._saved_page_states)
            for state in self._saved_page_states:
                self.__dict__.update(state)
                self.draw_footer(num_pages)
                pdfcanvas.Canvas.showPage(self)
            pdfcanvas.Canvas.save(self)
        def draw_footer(self, total):
            self.saveState()
            self.setFont('Helvetica', 6.5)
            self.setFillColor(colors.HexColor('#666666'))
            self.drawCentredString(A4[0]/2, 14*mm, "DM Energie Solution - 17 rue Alexandre Dumas, 91260 Juvisy sur Orge - Tél : 06638402286 - email : dmenergiesolutions@gmail.com")
            self.drawCentredString(A4[0]/2, 10*mm, "SAS au capital de 10 000 Euros - Siret : 90040094600019 - N° TVA Intra. FR06900400946 - Code Ape: 4322B")
            self.setFont('Helvetica', 7)
            self.drawRightString(A4[0]-15*mm, 10*mm, f"{self._pageNumber}/{total}")
            self.setStrokeColor(GRIS_LIGNE)
            self.setLineWidth(0.5)
            self.line(15*mm, 18*mm, A4[0]-15*mm, 18*mm)
            self.restoreState()

    doc.build(story, canvasmaker=PageCountCanvas)
    buf.seek(0)
    return buf

