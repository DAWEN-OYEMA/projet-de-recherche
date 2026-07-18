"""Page Gestion des enseignants."""

import streamlit as st
import pandas as pd
from database import get_session
from models.enseignant import Enseignant
from models.matiere import Matiere
from utils.ui import page_header, show_success, show_error
from utils.helpers import search_filter_df, df_to_excel, format_currency


def render():
    page_header("Gestion des enseignants", "Ajouter, modifier et gérer les enseignants", "👨‍🏫")

    tab_liste, tab_ajout = st.tabs(["📋 Liste", "➕ Ajouter / Modifier"])

    with tab_liste:
        session = get_session()
        try:
            enseignants = session.query(Enseignant).filter(Enseignant.actif == 1).all()
            df = pd.DataFrame([{
                "ID": e.id,
                "Nom": e.nom,
                "Postnom": e.postnom or "",
                "Prénom": e.prenom,
                "Téléphone": e.telephone or "",
                "Adresse": e.adresse or "",
                "Salaire": format_currency(e.salaire),
                "Matières": ", ".join(m.nom for m in e.matieres),
            } for e in enseignants])

            search = st.text_input("🔍 Rechercher...", key="search_ens")
            df_f = search_filter_df(df, search, ["Nom", "Prénom", "Matières"])

            st.dataframe(df_f, use_container_width=True, hide_index=True)

            if st.button("📥 Exporter Excel"):
                path = df_to_excel(df_f.drop(columns=["ID"], errors="ignore"), "enseignants.xlsx")
                with open(path, "rb") as f:
                    st.download_button("⬇️ Télécharger", f, file_name="enseignants.xlsx")
        finally:
            session.close()

    with tab_ajout:
        session = get_session()
        try:
            matieres = session.query(Matiere).all()
            matiere_names = [m.nom for m in matieres]
            mode = st.radio("Action", ["Ajouter", "Modifier", "Supprimer"], horizontal=True, key="ens_mode")

            if mode == "Ajouter":
                with st.form("form_add_ens"):
                    c1, c2 = st.columns(2)
                    with c1:
                        nom = st.text_input("Nom *")
                        postnom = st.text_input("Postnom")
                        prenom = st.text_input("Prénom *")
                    with c2:
                        telephone = st.text_input("Téléphone")
                        adresse = st.text_input("Adresse")
                        salaire = st.number_input("Salaire (FC)", min_value=0, step=10000)

                    selected_matieres = st.multiselect("Matières enseignées", matiere_names)

                    if st.form_submit_button("✅ Enregistrer", type="primary"):
                        if not nom or not prenom:
                            show_error("Nom et prénom obligatoires.")
                        else:
                            ens = Enseignant(
                                nom=nom, postnom=postnom, prenom=prenom,
                                telephone=telephone, adresse=adresse, salaire=salaire,
                            )
                            for mn in selected_matieres:
                                mat = session.query(Matiere).filter(Matiere.nom == mn).first()
                                if mat:
                                    ens.matieres.append(mat)
                            session.add(ens)
                            session.commit()
                            show_success(f"Enseignant {prenom} {nom} enregistré.")

                # Ajout rapide de matière (hors formulaire)
                st.markdown("---")
                new_matiere = st.text_input("Ajouter une nouvelle matière")
                if st.button("➕ Créer matière") and new_matiere:
                    if session.query(Matiere).filter(Matiere.nom == new_matiere).first():
                        show_error("Cette matière existe déjà.")
                    else:
                        session.add(Matiere(nom=new_matiere))
                        session.commit()
                        show_success(f"Matière '{new_matiere}' créée.")
                        st.rerun()

            elif mode == "Modifier":
                enseignants = session.query(Enseignant).filter(Enseignant.actif == 1).all()
                if not enseignants:
                    st.info("Aucun enseignant.")
                else:
                    ens_map = {e.nom_complet: e.id for e in enseignants}
                    sel = st.selectbox("Enseignant", list(ens_map.keys()))
                    ens = session.query(Enseignant).get(ens_map[sel])

                    with st.form("form_edit_ens"):
                        c1, c2 = st.columns(2)
                        with c1:
                            nom = st.text_input("Nom", value=ens.nom)
                            postnom = st.text_input("Postnom", value=ens.postnom or "")
                            prenom = st.text_input("Prénom", value=ens.prenom)
                        with c2:
                            telephone = st.text_input("Téléphone", value=ens.telephone or "")
                            adresse = st.text_input("Adresse", value=ens.adresse or "")
                            salaire = st.number_input("Salaire", value=ens.salaire, step=10000)

                        current_mat = [m.nom for m in ens.matieres]
                        selected_matieres = st.multiselect("Matières", matiere_names, default=current_mat)

                        if st.form_submit_button("💾 Mettre à jour", type="primary"):
                            ens.nom, ens.postnom, ens.prenom = nom, postnom, prenom
                            ens.telephone, ens.adresse, ens.salaire = telephone, adresse, salaire
                            ens.matieres.clear()
                            for mn in selected_matieres:
                                mat = session.query(Matiere).filter(Matiere.nom == mn).first()
                                if mat:
                                    ens.matieres.append(mat)
                            session.commit()
                            show_success("Enseignant mis à jour.")

            elif mode == "Supprimer":
                enseignants = session.query(Enseignant).filter(Enseignant.actif == 1).all()
                ens_map = {e.nom_complet: e.id for e in enseignants}
                sel = st.selectbox("Enseignant à supprimer", list(ens_map.keys()))
                if st.button("🗑️ Supprimer", type="primary"):
                    ens = session.query(Enseignant).get(ens_map[sel])
                    ens.actif = 0
                    session.commit()
                    show_success(f"{ens.nom_complet} supprimé.")
                    st.rerun()
        finally:
            session.close()
