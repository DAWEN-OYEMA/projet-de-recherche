"""Page Gestion des élèves — CRUD, import/export Excel, fiche imprimable."""

import streamlit as st
import pandas as pd
from datetime import date
from database import get_session
from models.eleve import Eleve
from models.classe import Classe
from utils.ui import page_header, show_success, show_error
from utils.helpers import (
    generate_matricule, save_photo, df_to_excel,
    read_excel, search_filter_df, format_date,
)
from utils.export import export_table_pdf


def _eleves_to_df(eleves) -> pd.DataFrame:
    return pd.DataFrame([{
        "ID": e.id,
        "Matricule": e.matricule,
        "Nom": e.nom,
        "Postnom": e.postnom or "",
        "Prénom": e.prenom,
        "Sexe": e.sexe,
        "Date naissance": format_date(e.date_naissance),
        "Adresse": e.adresse or "",
        "Téléphone": e.telephone or "",
        "Parent": e.parent or "",
        "Classe": e.classe.nom if e.classe else "—",
    } for e in eleves])


def render():
    page_header("Gestion des élèves", "Ajouter, modifier, rechercher et exporter", "👨‍🎓")

    tab_liste, tab_ajout, tab_import = st.tabs([
        "📋 Liste des élèves", "➕ Ajouter / Modifier", "📥 Importer Excel"
    ])

    # ── Onglet Liste ──────────────────────────────────────────────
    with tab_liste:
        session = get_session()
        try:
            eleves = session.query(Eleve).filter(Eleve.actif == 1).all()
            df = _eleves_to_df(eleves)

            search = st.text_input("🔍 Rechercher un élève...", key="search_eleve")
            df_filtered = search_filter_df(
                df, search, ["Matricule", "Nom", "Postnom", "Prénom", "Classe", "Parent"]
            )

            st.dataframe(df_filtered, use_container_width=True, hide_index=True)

            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("📥 Exporter Excel", use_container_width=True):
                    path = df_to_excel(df_filtered, "eleves_export.xlsx")
                    with open(path, "rb") as f:
                        st.download_button("⬇️ Télécharger Excel", f,
                                           file_name="eleves.xlsx", use_container_width=True)
            with col2:
                if st.button("📄 Exporter PDF", use_container_width=True):
                    pdf_df = df_filtered.drop(columns=["ID"], errors="ignore")
                    path = export_table_pdf("Liste des élèves", pdf_df)
                    with open(path, "rb") as f:
                        st.download_button("⬇️ Télécharger PDF", f,
                                           file_name="eleves.pdf", use_container_width=True)
            with col3:
                eleve_ids = df_filtered["ID"].tolist() if not df_filtered.empty else []
                if eleve_ids:
                    selected_id = st.selectbox(
                        "Imprimer fiche",
                        eleve_ids,
                        format_func=lambda x: df_filtered.loc[
                            df_filtered["ID"] == x, "Prénom"
                        ].values[0] + " " + df_filtered.loc[
                            df_filtered["ID"] == x, "Nom"
                        ].values[0],
                    )
                    if st.button("🖨️ Imprimer fiche", use_container_width=True):
                        eleve = session.query(Eleve).get(selected_id)
                        if eleve:
                            fiche_df = pd.DataFrame([{
                                "Champ": k, "Valeur": v
                            } for k, v in {
                                "Matricule": eleve.matricule,
                                "Nom complet": eleve.nom_complet,
                                "Sexe": eleve.sexe,
                                "Date naissance": format_date(eleve.date_naissance),
                                "Adresse": eleve.adresse or "—",
                                "Téléphone": eleve.telephone or "—",
                                "Parent": eleve.parent or "—",
                                "Classe": eleve.classe.nom if eleve.classe else "—",
                            }.items()])
                            path = export_table_pdf(
                                f"Fiche élève — {eleve.nom_complet}", fiche_df
                            )
                            with open(path, "rb") as f:
                                st.download_button("⬇️ Télécharger fiche PDF", f,
                                                   file_name=f"fiche_{eleve.matricule}.pdf")
        finally:
            session.close()

    # ── Onglet Ajout / Modification ───────────────────────────────
    with tab_ajout:
        session = get_session()
        try:
            classes = session.query(Classe).all()
            classe_options = {c.nom: c.id for c in classes}

            mode = st.radio("Action", ["Ajouter", "Modifier", "Supprimer"], horizontal=True)

            if mode == "Ajouter":
                with st.form("form_add_eleve", clear_on_submit=True):
                    c1, c2 = st.columns(2)
                    with c1:
                        nom = st.text_input("Nom *")
                        postnom = st.text_input("Postnom")
                        prenom = st.text_input("Prénom *")
                        sexe = st.selectbox("Sexe *", ["M", "F"])
                    with c2:
                        date_naiss = st.date_input("Date de naissance", value=date(2010, 1, 1))
                        adresse = st.text_input("Adresse")
                        telephone = st.text_input("Téléphone")
                        parent = st.text_input("Parent / Tuteur")
                    classe_nom = st.selectbox("Classe", ["—"] + list(classe_options.keys()))
                    photo = st.file_uploader("Photo", type=["jpg", "jpeg", "png"])

                    if st.form_submit_button("✅ Enregistrer", type="primary"):
                        if not nom or not prenom:
                            show_error("Le nom et le prénom sont obligatoires.")
                        else:
                            matricule = generate_matricule()
                            photo_path = save_photo(photo, matricule) if photo else None
                            eleve = Eleve(
                                matricule=matricule,
                                nom=nom, postnom=postnom, prenom=prenom,
                                sexe=sexe, date_naissance=date_naiss,
                                adresse=adresse, telephone=telephone,
                                parent=parent,
                                classe_id=classe_options.get(classe_nom) if classe_nom != "—" else None,
                                photo=photo_path,
                            )
                            session.add(eleve)
                            session.commit()
                            show_success(f"Élève {prenom} {nom} enregistré (matricule: {matricule})")

            elif mode == "Modifier":
                eleves = session.query(Eleve).filter(Eleve.actif == 1).all()
                if not eleves:
                    st.info("Aucun élève à modifier.")
                else:
                    eleve_map = {f"{e.matricule} — {e.nom_complet}": e.id for e in eleves}
                    selected = st.selectbox("Sélectionner l'élève", list(eleve_map.keys()))
                    eleve = session.query(Eleve).get(eleve_map[selected])

                    with st.form("form_edit_eleve"):
                        c1, c2 = st.columns(2)
                        with c1:
                            nom = st.text_input("Nom", value=eleve.nom)
                            postnom = st.text_input("Postnom", value=eleve.postnom or "")
                            prenom = st.text_input("Prénom", value=eleve.prenom)
                            sexe = st.selectbox("Sexe", ["M", "F"],
                                                index=0 if eleve.sexe == "M" else 1)
                        with c2:
                            date_naiss = st.date_input("Date de naissance",
                                                       value=eleve.date_naissance or date(2010, 1, 1))
                            adresse = st.text_input("Adresse", value=eleve.adresse or "")
                            telephone = st.text_input("Téléphone", value=eleve.telephone or "")
                            parent = st.text_input("Parent", value=eleve.parent or "")

                        current_classe = eleve.classe.nom if eleve.classe else "—"
                        classe_nom = st.selectbox(
                            "Classe", ["—"] + list(classe_options.keys()),
                            index=(["—"] + list(classe_options.keys())).index(current_classe)
                            if current_classe in classe_options or current_classe == "—" else 0,
                        )
                        photo = st.file_uploader("Nouvelle photo", type=["jpg", "jpeg", "png"])

                        if st.form_submit_button("💾 Mettre à jour", type="primary"):
                            eleve.nom = nom
                            eleve.postnom = postnom
                            eleve.prenom = prenom
                            eleve.sexe = sexe
                            eleve.date_naissance = date_naiss
                            eleve.adresse = adresse
                            eleve.telephone = telephone
                            eleve.parent = parent
                            eleve.classe_id = classe_options.get(classe_nom) if classe_nom != "—" else None
                            if photo:
                                eleve.photo = save_photo(photo, eleve.matricule)
                            session.commit()
                            show_success(f"Élève {eleve.nom_complet} mis à jour.")

            elif mode == "Supprimer":
                eleves = session.query(Eleve).filter(Eleve.actif == 1).all()
                if not eleves:
                    st.info("Aucun élève à supprimer.")
                else:
                    eleve_map = {f"{e.matricule} — {e.nom_complet}": e.id for e in eleves}
                    selected = st.selectbox("Élève à supprimer", list(eleve_map.keys()))
                    st.warning("Cette action désactivera l'élève (suppression logique).")
                    if st.button("🗑️ Confirmer la suppression", type="primary"):
                        eleve = session.query(Eleve).get(eleve_map[selected])
                        eleve.actif = 0
                        session.commit()
                        show_success(f"Élève {eleve.nom_complet} supprimé.")
                        st.rerun()
        finally:
            session.close()

    # ── Onglet Import Excel ───────────────────────────────────────
    with tab_import:
        st.markdown("#### Importer des élèves depuis Excel")
        st.markdown("Colonnes attendues : **Nom**, **Prénom**, **Sexe** (M/F), Postnom, Date naissance, Adresse, Téléphone, Parent, Classe")

        uploaded = st.file_uploader("Fichier Excel (.xlsx)", type=["xlsx"])
        if uploaded:
            df_import = read_excel(uploaded)
            st.dataframe(df_import.head(10), use_container_width=True)

            if st.button("📥 Importer", type="primary"):
                session = get_session()
                try:
                    classes = {c.nom: c.id for c in session.query(Classe).all()}
                    count = 0
                    for _, row in df_import.iterrows():
                        if pd.isna(row.get("Nom")) or pd.isna(row.get("Prénom")):
                            continue
                        classe_nom = str(row.get("Classe", "")).strip()
                        eleve = Eleve(
                            matricule=generate_matricule(),
                            nom=str(row["Nom"]),
                            postnom=str(row.get("Postnom", "")) if not pd.isna(row.get("Postnom")) else None,
                            prenom=str(row["Prénom"]),
                            sexe=str(row.get("Sexe", "M")).upper()[:1],
                            adresse=str(row.get("Adresse", "")) if not pd.isna(row.get("Adresse")) else None,
                            telephone=str(row.get("Téléphone", "")) if not pd.isna(row.get("Téléphone")) else None,
                            parent=str(row.get("Parent", "")) if not pd.isna(row.get("Parent")) else None,
                            classe_id=classes.get(classe_nom),
                        )
                        session.add(eleve)
                        count += 1
                    session.commit()
                    show_success(f"{count} élève(s) importé(s) avec succès.")
                except Exception as e:
                    session.rollback()
                    show_error(f"Erreur d'import : {e}")
                finally:
                    session.close()
