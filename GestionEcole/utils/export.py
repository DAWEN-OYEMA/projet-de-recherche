"""Export PDF et Excel pour les rapports."""

from datetime import datetime
from pathlib import Path
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from config import EXPORTS_DIR, SCHOOL_NAME


def _get_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="TitleCustom",
        parent=styles["Title"],
        fontSize=18,
        textColor=colors.HexColor("#1e3a5f"),
        spaceAfter=12,
    ))
    styles.add(ParagraphStyle(
        name="SubtitleCustom",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.grey,
        spaceAfter=20,
    ))
    return styles


def export_table_pdf(
    title: str,
    df: pd.DataFrame,
    filename: str | None = None,
    orientation: str = "portrait",
) -> Path:
    """Génère un PDF à partir d'un DataFrame."""
    if filename is None:
        filename = f"rapport_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    filepath = EXPORTS_DIR / filename
    pagesize = landscape(A4) if orientation == "landscape" else A4

    doc = SimpleDocTemplate(
        str(filepath),
        pagesize=pagesize,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = _get_styles()
    elements = []

    elements.append(Paragraph(SCHOOL_NAME, styles["TitleCustom"]))
    elements.append(Paragraph(title, styles["Heading2"]))
    elements.append(Paragraph(
        f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}",
        styles["SubtitleCustom"],
    ))
    elements.append(Spacer(1, 12))

    # Tableau
    data = [df.columns.tolist()] + df.values.tolist()
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a5f")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7fafc")]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(table)

    doc.build(elements)
    return filepath


def export_bulletin_pdf(eleve_data: dict, notes_data: list[dict], moyenne: float, mention: str) -> Path:
    """Génère un bulletin scolaire PDF pour un élève."""
    filename = f"bulletin_{eleve_data['matricule']}_{datetime.now().strftime('%Y%m%d')}.pdf"
    filepath = EXPORTS_DIR / filename

    doc = SimpleDocTemplate(str(filepath), pagesize=A4, rightMargin=2 * cm, leftMargin=2 * cm)
    styles = _get_styles()
    elements = []

    elements.append(Paragraph(SCHOOL_NAME, styles["TitleCustom"]))
    elements.append(Paragraph("BULLETIN SCOLAIRE", styles["Heading2"]))
    elements.append(Spacer(1, 12))

    # Infos élève
    info = [
        ["Matricule", eleve_data.get("matricule", ""), "Classe", eleve_data.get("classe", "")],
        ["Nom complet", eleve_data.get("nom_complet", ""), "Période", eleve_data.get("periode", "")],
    ]
    info_table = Table(info, colWidths=[3 * cm, 6 * cm, 3 * cm, 6 * cm])
    info_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 20))

    # Notes
    if notes_data:
        note_headers = ["Matière", "Type", "Note", "Coef.", "Moy. pond."]
        note_rows = [note_headers]
        for n in notes_data:
            note_rows.append([
                n.get("matiere", ""),
                n.get("type", ""),
                str(n.get("note", "")),
                str(n.get("coefficient", 1)),
                str(n.get("note", "")),
            ])
        note_table = Table(note_rows, repeatRows=1)
        note_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a5f")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(note_table)

    elements.append(Spacer(1, 20))
    elements.append(Paragraph(
        f"<b>Moyenne générale : {moyenne}/20</b> — Mention : <b>{mention}</b>",
        styles["Normal"],
    ))

    doc.build(elements)
    return filepath


def export_recu_pdf(paiement_data: dict) -> Path:
    """Génère un reçu de paiement PDF."""
    filename = f"recu_{paiement_data.get('reference', 'PAY')}.pdf"
    filepath = EXPORTS_DIR / filename

    doc = SimpleDocTemplate(str(filepath), pagesize=A4, rightMargin=2 * cm, leftMargin=2 * cm)
    styles = _get_styles()
    elements = []

    elements.append(Paragraph(SCHOOL_NAME, styles["TitleCustom"]))
    elements.append(Paragraph("REÇU DE PAIEMENT", styles["Heading2"]))
    elements.append(Spacer(1, 20))

    rows = [
        ["Référence", paiement_data.get("reference", "")],
        ["Date", paiement_data.get("date", "")],
        ["Élève", paiement_data.get("eleve", "")],
        ["Matricule", paiement_data.get("matricule", "")],
        ["Frais", paiement_data.get("frais", "")],
        ["Montant payé", f"{paiement_data.get('montant_paye', 0):,.0f} FC"],
        ["Reste à payer", f"{paiement_data.get('reste', 0):,.0f} FC"],
        ["Mode de paiement", paiement_data.get("mode", "Espèces")],
        ["Caissier", paiement_data.get("caissier", "")],
    ]
    table = Table(rows, colWidths=[5 * cm, 10 * cm])
    table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LINEBELOW", (0, -1), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)

    doc.build(elements)
    return filepath
