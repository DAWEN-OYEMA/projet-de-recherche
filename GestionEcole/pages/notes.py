"""Page Gestion des notes — saisie, moyennes, classement, bulletins."""

import streamlit as st
import pandas as pd
import plotly.express as px
from database import get_session
from models.note import Note
from models.eleve import Eleve
from models.matiere import Matiere
from models.classe import Classe
from utils.ui import page_header, show_success, show_error
from utils.helpers import calculate_moyenne, get_mention
from utils.export import export_bulletin_pdf


PERIODES = ["1er Trimestre", "2ème Trimestre", "3ème Trimestre"]
TYPES_EVAL = ["Devoir", "Examen", "Interrogation"]


def render():
    page_header("Gestion des notes", "Saisie, moyennes, classement et bulletins", "📝")

    tab_saisie, tab_classement, tab_bulletin = st.tabs([
        "✏️ Saisie des notes", "🏆 Classement", "📄 Bulletins"
    ])

    session = get_session()
    try:
        # ── Saisie ────────────────────────────────────────────────────
        with tab_saisie:
            eleves = session.query(Eleve).filter(Eleve.actif == 1).all()
            matieres = session.query(Matiere).all()

            if not eleves or not matieres:
                st.warning("Créez d'abord des élèves et des matières.")
            else:
                with st.form("form_note"):
                    eleve_map = {f"{e.matricule} — {e.nom_complet}": e.id for e in eleves}
                    eleve_sel = st.selectbox("Élève *", list(eleve_map.keys()))
                    matiere_sel = st.selectbox("Matière *", [m.nom for m in matieres])
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        note_val = st.number_input("Note /20 *", min_value=0.0, max_value=20.0, step=0.5)
                    with c2:
                        coef = st.number_input("Coefficient", min_value=1, max_value=5, value=1)
                    with c3:
                        type_eval = st.selectbox("Type", TYPES_EVAL)
                    periode = st.selectbox("Période", PERIODES)

                    if st.form_submit_button("✅ Enregistrer la note", type="primary"):
                        mat = session.query(Matiere).filter(Matiere.nom == matiere_sel).first()
                        note = Note(
                            eleve_id=eleve_map[eleve_sel],
                            matiere_id=mat.id,
                            note=note_val,
                            coefficient=coef,
                            type_evaluation=type_eval,
                            periode=periode,
                        )
                        session.add(note)
                        session.commit()
                        show_success(f"Note {note_val}/20 enregistrée.")

                st.markdown("---")
                notes = session.query(Note).order_by(Note.date_saisie.desc()).limit(50).all()
                if notes:
                    df = pd.DataFrame([{
                        "Élève": n.eleve.nom_complet if n.eleve else "—",
                        "Matière": n.matiere.nom if n.matiere else "—",
                        "Note": f"{n.note}/20",
                        "Coef.": n.coefficient,
                        "Type": n.type_evaluation,
                        "Période": n.periode,
                    } for n in notes])
                    st.dataframe(df, use_container_width=True, hide_index=True)

        # ── Classement ────────────────────────────────────────────────
        with tab_classement:
            classes = session.query(Classe).all()
            if not classes:
                st.info("Aucune classe.")
            else:
                classe_sel = st.selectbox("Classe", [c.nom for c in classes])
                periode_sel = st.selectbox("Période", PERIODES, key="periode_classement")

                cls = session.query(Classe).filter(Classe.nom == classe_sel).first()
                eleves = session.query(Eleve).filter(
                    Eleve.classe_id == cls.id, Eleve.actif == 1
                ).all()

                rankings = []
                for eleve in eleves:
                    notes = session.query(Note).filter(
                        Note.eleve_id == eleve.id, Note.periode == periode_sel
                    ).all()
                    moy = calculate_moyenne(notes)
                    rankings.append({
                        "Rang": 0,
                        "Élève": eleve.nom_complet,
                        "Matricule": eleve.matricule,
                        "Moyenne": moy,
                        "Mention": get_mention(moy),
                        "Nb notes": len(notes),
                    })

                rankings.sort(key=lambda x: x["Moyenne"], reverse=True)
                for i, r in enumerate(rankings):
                    r["Rang"] = i + 1

                if rankings:
                    df_rank = pd.DataFrame(rankings)
                    st.dataframe(df_rank, use_container_width=True, hide_index=True)

                    fig = px.bar(
                        df_rank, x="Élève", y="Moyenne",
                        title=f"Classement — {classe_sel} ({periode_sel})",
                        color="Moyenne",
                        color_continuous_scale="RdYlGn",
                        range_color=[0, 20],
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Aucune note pour cette classe/période.")

        # ── Bulletins ─────────────────────────────────────────────────
        with tab_bulletin:
            eleves = session.query(Eleve).filter(Eleve.actif == 1).all()
            if not eleves:
                st.info("Aucun élève.")
            else:
                eleve_map = {f"{e.matricule} — {e.nom_complet}": e for e in eleves}
                eleve_sel = st.selectbox("Élève", list(eleve_map.keys()), key="bulletin_eleve")
                periode_sel = st.selectbox("Période", PERIODES, key="periode_bulletin")

                eleve = eleve_map[eleve_sel]
                notes = session.query(Note).filter(
                    Note.eleve_id == eleve.id, Note.periode == periode_sel
                ).all()

                if notes:
                    notes_data = [{
                        "matiere": n.matiere.nom if n.matiere else "?",
                        "type": n.type_evaluation,
                        "note": n.note,
                        "coefficient": n.coefficient,
                    } for n in notes]

                    moy = calculate_moyenne(notes)
                    mention = get_mention(moy)

                    df_notes = pd.DataFrame([{
                        "Matière": nd["matiere"],
                        "Type": nd["type"],
                        "Note": f"{nd['note']}/20",
                        "Coef.": nd["coefficient"],
                    } for nd in notes_data])
                    st.dataframe(df_notes, use_container_width=True, hide_index=True)

                    c1, c2 = st.columns(2)
                    c1.metric("Moyenne générale", f"{moy}/20")
                    c2.metric("Mention", mention)

                    if st.button("📄 Générer le bulletin PDF", type="primary"):
                        eleve_data = {
                            "matricule": eleve.matricule,
                            "nom_complet": eleve.nom_complet,
                            "classe": eleve.classe.nom if eleve.classe else "—",
                            "periode": periode_sel,
                        }
                        path = export_bulletin_pdf(eleve_data, notes_data, moy, mention)
                        with open(path, "rb") as f:
                            st.download_button("⬇️ Télécharger bulletin", f,
                                               file_name=f"bulletin_{eleve.matricule}.pdf")
                else:
                    st.info("Aucune note pour cet élève et cette période.")
    finally:
        session.close()
