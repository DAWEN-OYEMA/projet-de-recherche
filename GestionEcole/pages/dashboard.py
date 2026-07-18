"""Page Tableau de bord — KPI et graphiques statistiques."""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from sqlalchemy import func
from database import get_session
from models.eleve import Eleve
from models.enseignant import Enseignant
from models.classe import Classe
from models.paiement import Paiement
from models.frais import FraisScolaire
from models.note import Note
from utils.ui import page_header, kpi_row


def render():
    page_header("Tableau de bord", "Vue d'ensemble de l'établissement", "📊")

    session = get_session()
    try:
        nb_eleves = session.query(Eleve).filter(Eleve.actif == 1).count()
        nb_enseignants = session.query(Enseignant).filter(Enseignant.actif == 1).count()
        nb_classes = session.query(Classe).count()

        total_recettes = session.query(func.sum(Paiement.montant_paye)).scalar() or 0
        total_impaye = session.query(func.sum(Paiement.reste)).filter(Paiement.reste > 0).scalar() or 0

        kpi_row([
            ("Élèves", nb_eleves, "👨‍🎓"),
            ("Enseignants", nb_enseignants, "👨‍🏫"),
            ("Classes", nb_classes, "🏛️"),
            ("Recettes", f"{total_recettes:,.0f} FC", "💰"),
            ("Impayés", f"{total_impaye:,.0f} FC", "⚠️"),
        ])

        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)

        # Graphique : effectifs par classe
        with col1:
            classes = session.query(Classe).all()
            if classes:
                df_classes = pd.DataFrame([
                    {"Classe": c.nom, "Effectif": c.effectif}
                    for c in classes
                ])
                fig = px.bar(
                    df_classes, x="Classe", y="Effectif",
                    title="Effectifs par classe",
                    color="Effectif",
                    color_continuous_scale="Blues",
                )
                fig.update_layout(showlegend=False, height=350)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Aucune classe enregistrée.")

        # Graphique : répartition par sexe
        with col2:
            sexe_data = session.query(
                Eleve.sexe, func.count(Eleve.id)
            ).filter(Eleve.actif == 1).group_by(Eleve.sexe).all()

            if sexe_data:
                df_sexe = pd.DataFrame(sexe_data, columns=["Sexe", "Nombre"])
                df_sexe["Sexe"] = df_sexe["Sexe"].map({"M": "Garçons", "F": "Filles"})
                fig = px.pie(
                    df_sexe, values="Nombre", names="Sexe",
                    title="Répartition par sexe",
                    color_discrete_sequence=["#3182ce", "#ed64a6"],
                )
                fig.update_layout(height=350)
                st.plotly_chart(fig, use_container_width=True)

        # Graphique : recettes mensuelles
        col3, col4 = st.columns(2)

        with col3:
            paiements = session.query(Paiement).all()
            if paiements:
                df_pay = pd.DataFrame([{
                    "Mois": p.date_paiement.strftime("%Y-%m"),
                    "Montant": p.montant_paye,
                } for p in paiements])
                df_monthly = df_pay.groupby("Mois")["Montant"].sum().reset_index()
                fig = px.line(
                    df_monthly, x="Mois", y="Montant",
                    title="Recettes mensuelles",
                    markers=True,
                )
                fig.update_layout(height=350)
                st.plotly_chart(fig, use_container_width=True)

        # Graphique : moyennes par matière
        with col4:
            notes = session.query(Note).all()
            if notes:
                df_notes = pd.DataFrame([{
                    "Matière": n.matiere.nom if n.matiere else "?",
                    "Note": n.note,
                } for n in notes])
                df_avg = df_notes.groupby("Matière")["Note"].mean().reset_index()
                df_avg.columns = ["Matière", "Moyenne"]
                fig = px.bar(
                    df_avg, x="Matière", y="Moyenne",
                    title="Moyennes par matière",
                    color="Moyenne",
                    color_continuous_scale="RdYlGn",
                    range_color=[0, 20],
                )
                fig.update_layout(showlegend=False, height=350)
                st.plotly_chart(fig, use_container_width=True)

    finally:
        session.close()
