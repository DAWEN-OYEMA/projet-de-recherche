"""Page Rapports — listes, statistiques, rapport financier (PDF/Excel)."""

import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import func
from database import get_session
from models.eleve import Eleve
from models.enseignant import Enseignant
from models.classe import Classe
from models.paiement import Paiement
from models.note import Note
from utils.ui import page_header
from utils.helpers import format_currency, format_date, df_to_excel
from utils.export import export_table_pdf


def render():
    page_header("Rapports", "Générer et exporter des rapports", "📑")

    tab_eleves, tab_ens, tab_stats, tab_finance = st.tabs([
        "👨‍🎓 Liste élèves", "👨‍🏫 Liste enseignants",
        "📊 Statistiques", "💰 Rapport financier",
    ])

    session = get_session()

    try:
        # ── Liste élèves ──────────────────────────────────────────
        with tab_eleves:
            classes = session.query(Classe).all()
            filtre = st.selectbox("Filtrer par classe", ["Toutes"] + [c.nom for c in classes])

            query = session.query(Eleve).filter(Eleve.actif == 1)
            if filtre != "Toutes":
                cls = session.query(Classe).filter(Classe.nom == filtre).first()
                if cls:
                    query = query.filter(Eleve.classe_id == cls.id)

            eleves = query.all()
            df = pd.DataFrame([{
                "Matricule": e.matricule,
                "Nom complet": e.nom_complet,
                "Sexe": e.sexe,
                "Classe": e.classe.nom if e.classe else "—",
                "Téléphone": e.telephone or "—",
                "Parent": e.parent or "—",
            } for e in eleves])

            st.dataframe(df, use_container_width=True, hide_index=True)
            c1, c2 = st.columns(2)
            with c1:
                path = df_to_excel(df, "rapport_eleves.xlsx")
                with open(path, "rb") as f:
                    st.download_button("📥 Excel", f, file_name="rapport_eleves.xlsx",
                                       use_container_width=True)
            with c2:
                path = export_table_pdf("Liste des élèves", df)
                with open(path, "rb") as f:
                    st.download_button("📄 PDF", f, file_name="rapport_eleves.pdf",
                                       use_container_width=True)

        # ── Liste enseignants ─────────────────────────────────────
        with tab_ens:
            enseignants = session.query(Enseignant).filter(Enseignant.actif == 1).all()
            df = pd.DataFrame([{
                "Nom complet": e.nom_complet,
                "Téléphone": e.telephone or "—",
                "Salaire": e.salaire,
                "Matières": ", ".join(m.nom for m in e.matieres),
            } for e in enseignants])

            st.dataframe(df, use_container_width=True, hide_index=True)
            c1, c2 = st.columns(2)
            with c1:
                path = df_to_excel(df, "rapport_enseignants.xlsx")
                with open(path, "rb") as f:
                    st.download_button("📥 Excel", f, file_name="rapport_enseignants.xlsx",
                                       use_container_width=True)
            with c2:
                path = export_table_pdf("Liste des enseignants", df)
                with open(path, "rb") as f:
                    st.download_button("📄 PDF", f, file_name="rapport_enseignants.pdf",
                                       use_container_width=True)

        # ── Statistiques ──────────────────────────────────────────
        with tab_stats:
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Effectifs par classe")
                classes = session.query(Classe).all()
                if classes:
                    df_cls = pd.DataFrame([
                        {"Classe": c.nom, "Effectif": c.effectif} for c in classes
                    ])
                    fig = px.pie(df_cls, values="Effectif", names="Classe",
                                 title="Répartition des effectifs")
                    st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("Répartition par sexe")
                sexe_data = session.query(
                    Eleve.sexe, func.count(Eleve.id)
                ).filter(Eleve.actif == 1).group_by(Eleve.sexe).all()
                if sexe_data:
                    df_sexe = pd.DataFrame(sexe_data, columns=["Sexe", "Nombre"])
                    df_sexe["Sexe"] = df_sexe["Sexe"].map({"M": "Garçons", "F": "Filles"})
                    fig = px.bar(df_sexe, x="Sexe", y="Nombre", color="Sexe",
                                 title="Garçons vs Filles")
                    st.plotly_chart(fig, use_container_width=True)

            st.subheader("Moyennes par matière")
            notes = session.query(Note).all()
            if notes:
                df_notes = pd.DataFrame([{
                    "Matière": n.matiere.nom if n.matiere else "?",
                    "Note": n.note,
                } for n in notes])
                df_avg = df_notes.groupby("Matière")["Note"].mean().reset_index()
                df_avg.columns = ["Matière", "Moyenne"]
                fig = px.bar(df_avg, x="Matière", y="Moyenne",
                             title="Moyennes générales par matière",
                             color="Moyenne", color_continuous_scale="Viridis")
                st.plotly_chart(fig, use_container_width=True)

                path = export_table_pdf("Statistiques — Moyennes par matière", df_avg)
                with open(path, "rb") as f:
                    st.download_button("📄 Exporter statistiques PDF", f,
                                       file_name="statistiques.pdf")

        # ── Rapport financier ─────────────────────────────────────
        with tab_finance:
            paiements = session.query(Paiement).order_by(Paiement.date_paiement.desc()).all()

            if paiements:
                total_encaisse = sum(p.montant_paye for p in paiements)
                total_impaye = sum(p.reste for p in paiements if p.reste > 0)

                c1, c2, c3 = st.columns(3)
                c1.metric("Total encaissé", format_currency(total_encaisse))
                c2.metric("Total impayé", format_currency(total_impaye))
                c3.metric("Nb paiements", len(paiements))

                df = pd.DataFrame([{
                    "Référence": p.reference,
                    "Date": format_date(p.date_paiement),
                    "Élève": p.eleve.nom_complet if p.eleve else "—",
                    "Frais": p.frais.nom if p.frais else "—",
                    "Montant payé": p.montant_paye,
                    "Reste": p.reste,
                    "Mode": p.mode_paiement,
                } for p in paiements])

                st.dataframe(df, use_container_width=True, hide_index=True)

                # Graphique recettes par mois
                df["Mois"] = pd.to_datetime(df["Date"], format="%d/%m/%Y", errors="coerce").dt.strftime("%Y-%m")
                df_monthly = df.groupby("Mois")["Montant payé"].sum().reset_index()
                fig = px.area(df_monthly, x="Mois", y="Montant payé",
                              title="Évolution des recettes")
                st.plotly_chart(fig, use_container_width=True)

                c1, c2 = st.columns(2)
                with c1:
                    path = df_to_excel(df, "rapport_financier.xlsx")
                    with open(path, "rb") as f:
                        st.download_button("📥 Excel", f, file_name="rapport_financier.xlsx",
                                           use_container_width=True)
                with c2:
                    path = export_table_pdf("Rapport financier", df, orientation="landscape")
                    with open(path, "rb") as f:
                        st.download_button("📄 PDF", f, file_name="rapport_financier.pdf",
                                           use_container_width=True)
            else:
                st.info("Aucun paiement enregistré.")
    finally:
        session.close()
