"""Page Gestion des paiements — frais, paiements, reçus."""

import streamlit as st
import pandas as pd
from datetime import datetime
from sqlalchemy import func
from database import get_session
from models.paiement import Paiement
from models.frais import FraisScolaire
from models.eleve import Eleve
from utils.ui import page_header, show_success, show_error
from utils.helpers import generate_reference, format_currency, format_date, search_filter_df
from utils.export import export_recu_pdf
from utils.auth import get_current_user


def render():
    page_header("Gestion des paiements", "Frais scolaires, encaissements et reçus", "💰")

    tab_paiement, tab_frais, tab_historique = st.tabs([
        "💳 Enregistrer paiement", "📋 Frais scolaires", "📜 Historique"
    ])

    # ── Enregistrer un paiement ───────────────────────────────────
    with tab_paiement:
        session = get_session()
        try:
            eleves = session.query(Eleve).filter(Eleve.actif == 1).all()
            frais_list = session.query(FraisScolaire).all()

            if not eleves:
                st.warning("Aucun élève enregistré.")
            elif not frais_list:
                st.warning("Créez d'abord des frais scolaires (onglet Frais).")
            else:
                eleve_map = {f"{e.matricule} — {e.nom_complet}": e.id for e in eleves}
                frais_map = {f"{f.nom} ({format_currency(f.montant)})": f for f in frais_list}

                with st.form("form_paiement"):
                    eleve_sel = st.selectbox("Élève *", list(eleve_map.keys()))
                    frais_sel = st.selectbox("Type de frais *", list(frais_map.keys()))
                    montant_paye = st.number_input("Montant payé (FC) *", min_value=0, step=1000)
                    mode = st.selectbox("Mode de paiement", ["Espèces", "Mobile Money", "Virement", "Chèque"])

                    frais_obj = frais_map[frais_sel]
                    reste = max(0, frais_obj.montant - montant_paye)
                    st.info(f"Montant total du frais : {format_currency(frais_obj.montant)} | "
                            f"Reste à payer : {format_currency(reste)}")

                    if st.form_submit_button("✅ Enregistrer le paiement", type="primary"):
                        user = get_current_user()
                        ref = generate_reference()
                        paiement = Paiement(
                            eleve_id=eleve_map[eleve_sel],
                            frais_id=frais_obj.id,
                            montant_paye=montant_paye,
                            montant_total=frais_obj.montant,
                            reste=reste,
                            reference=ref,
                            mode_paiement=mode,
                            caissier=user["nom_complet"] if user else "",
                        )
                        session.add(paiement)
                        session.commit()

                        eleve = session.query(Eleve).get(eleve_map[eleve_sel])
                        recu_data = {
                            "reference": ref,
                            "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
                            "eleve": eleve.nom_complet,
                            "matricule": eleve.matricule,
                            "frais": frais_obj.nom,
                            "montant_paye": montant_paye,
                            "reste": reste,
                            "mode": mode,
                            "caissier": user["nom_complet"] if user else "",
                        }
                        pdf_path = export_recu_pdf(recu_data)
                        show_success(f"Paiement enregistré — Réf: {ref}")

                        with open(pdf_path, "rb") as f:
                            st.download_button("🖨️ Télécharger le reçu PDF", f,
                                               file_name=f"recu_{ref}.pdf")
        finally:
            session.close()

    # ── Frais scolaires ───────────────────────────────────────────
    with tab_frais:
        session = get_session()
        try:
            with st.form("form_frais"):
                nom = st.text_input("Nom du frais *", placeholder="Ex: Frais de scolarité")
                montant = st.number_input("Montant (FC) *", min_value=0, step=5000)
                annee = st.text_input("Année scolaire", value="2025-2026")
                description = st.text_area("Description")

                if st.form_submit_button("✅ Créer le frais", type="primary"):
                    if not nom:
                        show_error("Le nom est obligatoire.")
                    else:
                        frais = FraisScolaire(nom=nom, montant=montant,
                                              annee_scolaire=annee, description=description)
                        session.add(frais)
                        session.commit()
                        show_success(f"Frais '{nom}' créé.")
                        st.rerun()

            st.markdown("---")
            frais_list = session.query(FraisScolaire).all()
            if frais_list:
                df = pd.DataFrame([{
                    "Frais": f.nom,
                    "Montant": format_currency(f.montant),
                    "Année": f.annee_scolaire,
                    "Description": f.description or "—",
                } for f in frais_list])
                st.dataframe(df, use_container_width=True, hide_index=True)
        finally:
            session.close()

    # ── Historique ────────────────────────────────────────────────
    with tab_historique:
        session = get_session()
        try:
            paiements = session.query(Paiement).order_by(Paiement.date_paiement.desc()).all()
            if paiements:
                df = pd.DataFrame([{
                    "Référence": p.reference,
                    "Date": format_date(p.date_paiement),
                    "Élève": p.eleve.nom_complet if p.eleve else "—",
                    "Frais": p.frais.nom if p.frais else "—",
                    "Payé": format_currency(p.montant_paye),
                    "Reste": format_currency(p.reste),
                    "Mode": p.mode_paiement,
                    "Caissier": p.caissier or "—",
                } for p in paiements])

                search = st.text_input("🔍 Rechercher...", key="search_pay")
                df_f = search_filter_df(df, search, ["Référence", "Élève", "Frais"])

                total_paye = sum(p.montant_paye for p in paiements)
                total_reste = sum(p.reste for p in paiements if p.reste > 0)

                c1, c2 = st.columns(2)
                c1.metric("Total encaissé", format_currency(total_paye))
                c2.metric("Total impayé", format_currency(total_reste))

                st.dataframe(df_f, use_container_width=True, hide_index=True)
            else:
                st.info("Aucun paiement enregistré.")
        finally:
            session.close()
