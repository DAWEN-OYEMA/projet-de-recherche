"""Page Gestion des cours (emploi du temps)."""

import streamlit as st
import pandas as pd
from datetime import time
from database import get_session
from models.cours import Cours
from models.matiere import Matiere
from models.enseignant import Enseignant
from models.classe import Classe
from utils.ui import page_header, show_success, show_error


JOURS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"]


def render():
    page_header("Gestion des cours", "Matières, horaires et emploi du temps", "📚")

    session = get_session()
    try:
        tab_edt, tab_ajout = st.tabs(["📅 Emploi du temps", "➕ Ajouter / Supprimer"])

        with tab_edt:
            cours_list = session.query(Cours).all()
            if cours_list:
                df = pd.DataFrame([{
                    "Jour": c.jour,
                    "Heure début": c.heure_debut.strftime("%H:%M"),
                    "Heure fin": c.heure_fin.strftime("%H:%M"),
                    "Matière": c.matiere.nom if c.matiere else "—",
                    "Enseignant": c.enseignant.nom_complet if c.enseignant else "—",
                    "Classe": c.classe.nom if c.classe else "—",
                    "Salle": c.salle or "—",
                } for c in cours_list])

                filtre_classe = st.selectbox(
                    "Filtrer par classe",
                    ["Toutes"] + sorted(df["Classe"].unique().tolist()),
                )
                if filtre_classe != "Toutes":
                    df = df[df["Classe"] == filtre_classe]

                st.dataframe(df.sort_values(["Jour", "Heure début"]),
                             use_container_width=True, hide_index=True)
            else:
                st.info("Aucun cours planifié.")

        with tab_ajout:
            matieres = session.query(Matiere).all()
            enseignants = session.query(Enseignant).filter(Enseignant.actif == 1).all()
            classes = session.query(Classe).all()

            if not matieres:
                st.warning("Créez d'abord des matières (via Enseignants).")
            elif not enseignants or not classes:
                st.warning("Créez d'abord des enseignants et des classes.")
            else:
                mode = st.radio("Action", ["Ajouter", "Supprimer"], horizontal=True)

                if mode == "Ajouter":
                    with st.form("form_cours"):
                        matiere = st.selectbox("Matière", [m.nom for m in matieres])
                        enseignant = st.selectbox("Enseignant", [e.nom_complet for e in enseignants])
                        classe = st.selectbox("Classe", [c.nom for c in classes])
                        jour = st.selectbox("Jour", JOURS)
                        c1, c2 = st.columns(2)
                        with c1:
                            h_debut = st.time_input("Heure début", value=time(8, 0))
                        with c2:
                            h_fin = st.time_input("Heure fin", value=time(9, 0))
                        salle = st.text_input("Salle")

                        if st.form_submit_button("✅ Ajouter", type="primary"):
                            mat = session.query(Matiere).filter(Matiere.nom == matiere).first()
                            ens = next(e for e in enseignants if e.nom_complet == enseignant)
                            cls = session.query(Classe).filter(Classe.nom == classe).first()
                            cours = Cours(
                                matiere_id=mat.id, enseignant_id=ens.id,
                                classe_id=cls.id, jour=jour,
                                heure_debut=h_debut, heure_fin=h_fin, salle=salle,
                            )
                            session.add(cours)
                            session.commit()
                            show_success(f"Cours {matiere} ajouté pour {classe}.")
                            st.rerun()

                elif mode == "Supprimer":
                    cours_list = session.query(Cours).all()
                    if cours_list:
                        labels = [
                            f"{c.jour} {c.heure_debut.strftime('%H:%M')} — "
                            f"{c.matiere.nom} ({c.classe.nom})"
                            for c in cours_list
                        ]
                        cours_map = dict(zip(labels, [c.id for c in cours_list]))
                        sel = st.selectbox("Cours à supprimer", list(cours_map.keys()))
                        if st.button("🗑️ Supprimer", type="primary"):
                            session.delete(session.query(Cours).get(cours_map[sel]))
                            session.commit()
                            show_success("Cours supprimé.")
                            st.rerun()
    finally:
        session.close()
