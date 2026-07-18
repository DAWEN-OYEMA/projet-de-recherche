"""Page Gestion des classes."""

import streamlit as st
import pandas as pd
from database import get_session
from models.classe import Classe
from models.enseignant import Enseignant
from utils.ui import page_header, show_success, show_error


def render():
    page_header("Gestion des classes", "Créer et gérer les classes", "🏛️")

    session = get_session()
    try:
        tab_liste, tab_gestion = st.tabs(["📋 Liste des classes", "➕ Créer / Supprimer"])

        with tab_liste:
            classes = session.query(Classe).all()
            df = pd.DataFrame([{
                "ID": c.id,
                "Classe": c.nom,
                "Niveau": c.niveau or "—",
                "Titulaire": c.titulaire.nom_complet if c.titulaire else "—",
                "Effectif": c.effectif,
            } for c in classes])
            st.dataframe(df, use_container_width=True, hide_index=True)

        with tab_gestion:
            enseignants = session.query(Enseignant).filter(Enseignant.actif == 1).all()
            ens_options = {e.nom_complet: e.id for e in enseignants}

            mode = st.radio("Action", ["Créer", "Supprimer"], horizontal=True)

            if mode == "Créer":
                with st.form("form_classe"):
                    nom = st.text_input("Nom de la classe *", placeholder="Ex: 6ème A")
                    niveau = st.text_input("Niveau", placeholder="Ex: Primaire, Secondaire")
                    titulaire = st.selectbox("Titulaire", ["—"] + list(ens_options.keys()))

                    if st.form_submit_button("✅ Créer la classe", type="primary"):
                        if not nom:
                            show_error("Le nom est obligatoire.")
                        elif session.query(Classe).filter(Classe.nom == nom).first():
                            show_error("Cette classe existe déjà.")
                        else:
                            classe = Classe(
                                nom=nom,
                                niveau=niveau,
                                titulaire_id=ens_options.get(titulaire) if titulaire != "—" else None,
                            )
                            session.add(classe)
                            session.commit()
                            show_success(f"Classe '{nom}' créée.")
                            st.rerun()

            elif mode == "Supprimer":
                classes = session.query(Classe).all()
                if not classes:
                    st.info("Aucune classe.")
                else:
                    cls_map = {c.nom: c.id for c in classes}
                    sel = st.selectbox("Classe à supprimer", list(cls_map.keys()))
                    classe = session.query(Classe).get(cls_map[sel])
                    if classe.effectif > 0:
                        st.warning(f"Cette classe contient {classe.effectif} élève(s). "
                                   "Réaffectez-les avant de supprimer.")
                    if st.button("🗑️ Supprimer", type="primary"):
                        if classe.effectif > 0:
                            show_error("Impossible : la classe contient des élèves.")
                        else:
                            session.delete(classe)
                            session.commit()
                            show_success(f"Classe '{sel}' supprimée.")
                            st.rerun()
    finally:
        session.close()
