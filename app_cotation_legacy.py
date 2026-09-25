import io
import os
import pandas as pd
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

st.set_page_config(
    page_title="Gestion des Bulletins - Secondaire RDC", layout="wide"
)

st.title("🎓 Système de Gestion Scolaire - RDC")

DATA_FILE = "school_data.csv"
ELEVES_FILE = "eleves_classe.csv"
MAXIMAS_FILE = "maximas_data.csv"


def load_data():
  if os.path.exists(DATA_FILE):
    return pd.read_csv(DATA_FILE)
  else:
    return pd.DataFrame(
        columns=[
            "Nom_Eleve",
            "Classe",
            "Option",
            "Cours",
            "P1",
            "P2",
            "Ex_S1",
            "P3",
            "P4",
            "Ex_S2",
        ]
    )


def load_eleves():
  if os.path.exists(ELEVES_FILE):
    return pd.read_csv(ELEVES_FILE)
  else:
    return pd.DataFrame(columns=["Nom_Eleve", "Classe", "Option"])


def load_maximas():
  if os.path.exists(MAXIMAS_FILE):
    return pd.read_csv(MAXIMAS_FILE)
  else:
    return pd.DataFrame(
        columns=[
            "Classe",
            "Option",
            "Cours",
            "Max_P1",
            "Max_P2",
            "Max_Ex1",
            "Max_P3",
            "Max_P4",
            "Max_Ex2",
        ]
    )


if "classe_active" not in st.session_state:
  st.session_state.classe_active = "1ère Commerciale"
if "option_active" not in st.session_state:
  st.session_state.option_active = "Commerciale et Gestion"

if "val_p1" not in st.session_state:
  st.session_state.val_p1 = 20.0
if "val_p2" not in st.session_state:
  st.session_state.val_p2 = 20.0
if "val_ex1" not in st.session_state:
  st.session_state.val_ex1 = 40.0
if "val_p3" not in st.session_state:
  st.session_state.val_p3 = 20.0
if "val_p4" not in st.session_state:
  st.session_state.val_p4 = 20.0
if "val_ex2" not in st.session_state:
  st.session_state.val_ex2 = 40.0


def calculate_proportions():
  p1 = st.session_state.val_p1
  st.session_state.val_p2 = p1
  st.session_state.val_ex1 = p1 + p1
  st.session_state.val_p3 = p1
  st.session_state.val_p4 = p1
  st.session_state.val_ex2 = p1 + p1


st.sidebar.markdown("### 📌 Configuration Classe & Option")
st.session_state.classe_active = st.sidebar.text_input(
    "Classe :", value=st.session_state.classe_active
).strip()
st.session_state.option_active = st.sidebar.text_input(
    "Option :", value=st.session_state.option_active
).strip()

menu = st.sidebar.selectbox(
    "Navigation",
    [
        "Configuration Cours & Maximas",
        "Gestion des Élèves",
        "Gestion des Notes (Par Cours)",
        "Génération Bulletin & PDF",
    ],
)

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚠️ Zone de Danger")
confirmer_reset = st.sidebar.checkbox("Je veux tout effacer et recommencer")
if st.sidebar.button("🗑️ Réinitialiser toutes les données"):
  if confirmer_reset:
    for fichier in [DATA_FILE, ELEVES_FILE, MAXIMAS_FILE]:
      if os.path.exists(fichier):
        os.remove(fichier)
    st.sidebar.success(
        "Toutes les données ont été effacées. Le système est vierge."
    )
    st.rerun()
  else:
    st.sidebar.error(
        "Veuillez cocher la case de confirmation pour réinitialiser."
    )

classe_active = st.session_state.classe_active
option_active = st.session_state.option_active

# 1. CONFIGURATION COURS & MAXIMAS
if menu == "Configuration Cours & Maximas":
  st.subheader(
      f"⚙️ Enregistrement des Cours et Maximas - Classe : {classe_active} |"
      f" Option : {option_active}"
  )
  cours_saisi = st.text_input(
      "Intitulé du Cours (ex: Chimie, Français, Géographie...)"
  ).strip()

  col_m1, col_m2, col_m3, col_m4, col_m5, col_m6 = st.columns(6)
  with col_m1:
    st.number_input(
        "Max P1",
        min_value=0.0,
        key="val_p1",
        on_change=calculate_proportions,
    )
  with col_m2:
    st.number_input("Max P2", min_value=0.0, key="val_p2", disabled=True)
  with col_m3:
    st.number_input("Max Examen S1", min_value=0.0, key="val_ex1", disabled=True)
  with col_m4:
    st.number_input("Max P3", min_value=0.0, key="val_p3", disabled=True)
  with col_m5:
    st.number_input("Max P4", min_value=0.0, key="val_p4", disabled=True)
  with col_m6:
    st.number_input("Max Examen S2", min_value=0.0, key="val_ex2", disabled=True)

  if st.button("Enregistrer ce cours et ses maximas"):
    if cours_saisi and classe_active:
      cours_maj = cours_saisi
      classe_maj = classe_active.upper()
      option_maj = option_active.upper()

      df_maximas = load_maximas()
      if "Option" not in df_maximas.columns:
        df_maximas["Option"] = "TOUTES"

      df_maximas = df_maximas[
          ~(
              (df_maximas["Classe"].str.upper() == classe_maj)
              & (df_maximas["Option"].str.upper() == option_maj)
              & (df_maximas["Cours"].str.upper() == cours_maj.upper())
          )
      ]
      new_max_row = pd.DataFrame([{
          "Classe": classe_maj,
          "Option": option_maj,
          "Cours": cours_maj,
          "Max_P1": st.session_state.val_p1,
          "Max_P2": st.session_state.val_p2,
          "Max_Ex1": st.session_state.val_ex1,
          "Max_P3": st.session_state.val_p3,
          "Max_P4": st.session_state.val_p4,
          "Max_Ex2": st.session_state.val_ex2,
      }])
      df_maximas = pd.concat([df_maximas, new_max_row], ignore_index=True)
      df_maximas.to_csv(MAXIMAS_FILE, index=False)

      df_notes = load_data()
      if "Option" not in df_notes.columns:
        df_notes["Option"] = option_maj
      df_eleves = load_eleves()
      if "Option" not in df_eleves.columns:
        df_eleves["Option"] = option_maj

      eleves_cls = df_eleves[df_eleves["Classe"].str.upper() == classe_maj]
      for _, el in eleves_cls.iterrows():
        existe = df_notes[
            (df_notes["Nom_Eleve"] == el["Nom_Eleve"])
            & (df_notes["Classe"].str.upper() == classe_maj)
            & (df_notes["Cours"].str.upper() == cours_maj.upper())
        ]
        if existe.empty:
          new_note_row = pd.DataFrame([{
              "Nom_Eleve": el["Nom_Eleve"],
              "Classe": classe_maj,
              "Option": option_maj,
              "Cours": cours_maj,
              "P1": 0.0,
              "P2": 0.0,
              "Ex_S1": 0.0,
              "P3": 0.0,
              "P4": 0.0,
              "Ex_S2": 0.0,
          }])
          df_notes = pd.concat([df_notes, new_note_row], ignore_index=True)
      df_notes.to_csv(DATA_FILE, index=False)
      st.success(f"✅ Cours '{cours_maj}' enregistré avec succès !")
    else:
      st.error("Veuillez entrer un intitulé de cours valide.")

  st.markdown("---")
  st.subheader("📚 Cours et Maximas configurés :")
  df_m_actuel = load_maximas()
  if "Option" not in df_m_actuel.columns:
    df_m_actuel["Option"] = "TOUTES"
  df_m_cls = df_m_actuel[
      df_m_actuel["Classe"].str.upper() == classe_active.upper()
  ]
  if not df_m_cls.empty:
    st.dataframe(df_m_cls, use_container_width=True)
  else:
    st.info("Aucun cours configuré pour l'instant.")

# 2. GESTION DES ÉLÈVES
elif menu == "Gestion des Élèves":
  st.subheader(
      f"👥 Gestion des Élèves - Classe : {classe_active} | Option :"
      f" {option_active}"
  )

  with st.form("form_ajout_eleve", clear_on_submit=True):
    nouvel_eleve = st.text_input("Nom complet de l'élève")
    btn_ajout = st.form_submit_button("Ajouter l'élève")

    if btn_ajout:
      if nouvel_eleve.strip() and classe_active:
        nom_maj = nouvel_eleve.strip().upper()
        classe_maj = classe_active.upper()
        option_maj = option_active.upper()

        df_eleves_current = load_eleves()
        if "Option" not in df_eleves_current.columns:
          df_eleves_current["Option"] = option_maj
        df_notes_current = load_data()
        if "Option" not in df_notes_current.columns:
          df_notes_current["Option"] = option_maj

        existing = df_eleves_current[
            (df_eleves_current["Nom_Eleve"].str.upper() == nom_maj)
            & (df_eleves_current["Classe"].str.upper() == classe_maj)
        ]

        if not existing.empty:
          st.warning("⚠️ Cet élève existe déjà dans cette classe.")
        else:
          new_row_eleve = pd.DataFrame(
              [{"Nom_Eleve": nom_maj, "Classe": classe_maj, "Option": option_maj}]
          )
          df_eleves_current = pd.concat(
              [df_eleves_current, new_row_eleve], ignore_index=True
          )
          df_eleves_current.to_csv(ELEVES_FILE, index=False)

          df_max = load_maximas()
          if "Option" not in df_max.columns:
            df_max["Option"] = option_maj
          cours_classe = df_max[
              df_max["Classe"].str.upper() == classe_maj
          ]["Cours"].tolist()

          new_rows_notes = []
          for c_nom in cours_classe:
            new_rows_notes.append({
                "Nom_Eleve": nom_maj,
                "Classe": classe_maj,
                "Option": option_maj,
                "Cours": c_nom,
                "P1": 0.0,
                "P2": 0.0,
                "Ex_S1": 0.0,
                "P3": 0.0,
                "P4": 0.0,
                "Ex_S2": 0.0,
            })
          if new_rows_notes:
            df_notes_current = pd.concat(
                [df_notes_current, pd.DataFrame(new_rows_notes)],
                ignore_index=True,
            )
            df_notes_current.to_csv(DATA_FILE, index=False)
          st.success(f"✅ Élève {nom_maj} ajouté avec succès !")
      else:
        st.error("Veuillez renseigner un nom d'élève.")

  st.markdown("---")
  st.subheader("Liste des élèves inscrits")
  df_eleves_current = load_eleves()
  if "Option" not in df_eleves_current.columns:
    df_eleves_current["Option"] = option_active.upper()
  eleves_classe_actuelle = df_eleves_current[
      df_eleves_current["Classe"].str.upper() == classe_active.upper()
  ]

  if not eleves_classe_actuelle.empty:
    st.dataframe(eleves_classe_actuelle, use_container_width=True)
    eleve_a_supprimer = st.selectbox(
        "Sélectionner un élève à supprimer :",
        ["-- Choisir --"] + sorted(eleves_classe_actuelle["Nom_Eleve"].tolist()),
    )
    if eleve_a_supprimer != "-- Choisir --":
      if st.button("Supprimer cet élève définitivement"):
        df_eleves_current = df_eleves_current[
            ~(
                (df_eleves_current["Nom_Eleve"] == eleve_a_supprimer)
                & (
                    df_eleves_current["Classe"].str.upper()
                    == classe_active.upper()
                )
            )
        ]
        df_eleves_current.to_csv(ELEVES_FILE, index=False)
        df_notes_current = load_data()
        df_notes_current = df_notes_current[
            ~(
                (df_notes_current["Nom_Eleve"] == eleve_a_supprimer)
                & (
                    df_notes_current["Classe"].str.upper()
                    == classe_active.upper()
                )
            )
        ]
        df_notes_current.to_csv(DATA_FILE, index=False)
        st.success(f"L'élève {eleve_a_supprimer} a été supprimé.")
        st.rerun()
  else:
    st.info("Aucun élève enregistré pour cette classe.")

# 3. GESTION DES NOTES (PAR COURS)
elif menu == "Gestion des Notes (Par Cours)":
  st.subheader(
      f"📝 Saisie des Notes - Classe : {classe_active} | Option :"
      f" {option_active}"
  )

  df_maximas = load_maximas()
  if "Option" not in df_maximas.columns:
    df_maximas["Option"] = option_active.upper()
  cours_disponibles = sorted(
      df_maximas[
          df_maximas["Classe"].str.upper() == classe_active.upper()
      ]["Cours"]
      .dropna()
      .unique()
      .tolist()
  )

  if cours_disponibles:
    cours_selection = st.selectbox(
        "Sélectionnez le cours à coter :", cours_disponibles
    )
    df_notes_all = load_data()
    if "Option" not in df_notes_all.columns:
      df_notes_all["Option"] = option_active.upper()

    df_notes_filtre = df_notes_all[
        (df_notes_all["Classe"].str.upper() == classe_active.upper())
        & (df_notes_all["Cours"].str.upper() == cours_selection.upper())
    ]

    if not df_notes_filtre.empty:
      with st.form("form_maj_notes"):
        notes_mises_a_jour = []
        for index, row in df_notes_filtre.iterrows():
          st.markdown(f"**{row['Nom_Eleve']}**")
          col_n1, col_n2, col_n3, col_n4, col_n5, col_n6 = st.columns(6)
          with col_n1:
            p1 = st.number_input(
                f"P1 ({row['Nom_Eleve']})",
                min_value=0.0,
                value=float(row["P1"]),
                key=f"p1_{index}",
            )
          with col_n2:
            p2 = st.number_input(
                f"P2 ({row['Nom_Eleve']})",
                min_value=0.0,
                value=float(row["P2"]),
                key=f"p2_{index}",
            )
          with col_n3:
            ex1 = st.number_input(
                f"Ex 1 ({row['Nom_Eleve']})",
                min_value=0.0,
                value=float(row["Ex_S1"]),
                key=f"ex1_{index}",
            )
          with col_n4:
            p3 = st.number_input(
                f"P3 ({row['Nom_Eleve']})",
                min_value=0.0,
                value=float(row["P3"]),
                key=f"p3_{index}",
            )
          with col_n5:
            p4 = st.number_input(
                f"P4 ({row['Nom_Eleve']})",
                min_value=0.0,
                value=float(row["P4"]),
                key=f"p4_{index}",
            )
          with col_n6:
            ex2 = st.number_input(
                f"Ex 2 ({row['Nom_Eleve']})",
                min_value=0.0,
                value=float(row["Ex_S2"]),
                key=f"ex2_{index}",
            )

          notes_mises_a_jour.append({
              "Nom_Eleve": row["Nom_Eleve"],
              "Classe": row["Classe"],
              "Option": row.get("Option", option_active.upper()),
              "Cours": row["Cours"],
              "P1": p1,
              "P2": p2,
              "Ex_S1": ex1,
              "P3": p3,
              "P4": p4,
              "Ex_S2": ex2,
          })
          st.markdown("---")

        btn_save_notes = st.form_submit_button("Enregistrer les modifications")
        if btn_save_notes:
          for updated in notes_mises_a_jour:
            mask = (
                (df_notes_all["Nom_Eleve"] == updated["Nom_Eleve"])
                & (
                    df_notes_all["Classe"].str.upper()
                    == updated["Classe"].upper()
                )
                & (
                    df_notes_all["Cours"].str.upper()
                    == updated["Cours"].upper()
                )
            )
            df_notes_all.loc[mask, "P1"] = updated["P1"]
            df_notes_all.loc[mask, "P2"] = updated["P2"]
            df_notes_all.loc[mask, "Ex_S1"] = updated["Ex_S1"]
            df_notes_all.loc[mask, "P3"] = updated["P3"]
            df_notes_all.loc[mask, "P4"] = updated["P4"]
            df_notes_all.loc[mask, "Ex_S2"] = updated["Ex_S2"]
          df_notes_all.to_csv(DATA_FILE, index=False)
          st.success("Notes mises à jour avec succès !")
          st.rerun()

      # TABLEAU RÉCAPITULATIF VISIBLE EN DESSOUS DU FORMULAIRE
      st.markdown("---")
      st.subheader("📊 Aperçu des notes enregistrées (Base de données)")
      df_notes_frais = load_data()
      df_notes_affiche = df_notes_frais[
          (df_notes_frais["Classe"].str.upper() == classe_active.upper())
          & (df_notes_frais["Cours"].str.upper() == cours_selection.upper())
      ]
      st.dataframe(
          df_notes_affiche[
              ["Nom_Eleve", "P1", "P2", "Ex_S1", "P3", "P4", "Ex_S2"]
          ],
          use_container_width=True,
      )

    else:
      st.info("Aucun élève trouvé pour ce cours.")
  else:
    st.warning("⚠️ Aucun cours configuré.")

# 4. GÉNÉRATION BULLETIN & PDF (PLATYPUS ENGINE)
elif menu == "Génération Bulletin & PDF":
  st.subheader(
      f"📄 Génération de l'extrait de bulletin - Classe : {classe_active}"
  )

  df_notes = load_data()
  df_maximas = load_maximas()
  if "Option" not in df_notes.columns:
    df_notes["Option"] = option_active.upper()
  if "Option" not in df_maximas.columns:
    df_maximas["Option"] = option_active.upper()

  eleves_classe = df_notes[
      df_notes["Classe"].str.upper() == classe_active.upper()
  ]

  if not eleves_classe.empty:
    eleves_disponibles = sorted(
        eleves_classe["Nom_Eleve"].dropna().unique().tolist()
    )
    eleve_selectionne = st.selectbox(
        "Sélectionner l'élève pour le bulletin :", eleves_disponibles
    )

    if st.button("Générer le Bulletin PDF Officiel & Propre"):
      data_eleve = eleves_classe[
          eleves_classe["Nom_Eleve"] == eleve_selectionne
      ]
      opt_eleve = (
          str(data_eleve.iloc[0]["Option"])
          if "Option" in data_eleve.columns and pd.notna(data_eleve.iloc[0]["Option"])
          else option_active
      )
      max_classe = df_maximas[
          df_maximas["Classe"].str.upper() == classe_active.upper()
      ]

      buffer = io.BytesIO()
      doc = SimpleDocTemplate(
          buffer,
          pagesize=letter,
          rightMargin=30,
          leftMargin=30,
          topMargin=30,
          bottomMargin=30,
      )
      elements = []
      styles = getSampleStyleSheet()

      title_style = ParagraphStyle(
          'TitleStyle',
          parent=styles['Heading1'],
          fontName='Helvetica-Bold',
          fontSize=14,
          textColor=colors.HexColor('#ffffff'),
          alignment=1,
      )
      main_title_style = ParagraphStyle(
          'MainTitle',
          parent=styles['Heading2'],
          fontName='Helvetica-Bold',
          fontSize=12,
          textColor=colors.HexColor('#1e293b'),
          alignment=1,
      )
      cell_bold = ParagraphStyle(
          'CellBold',
          parent=styles['Normal'],
          fontName='Helvetica-Bold',
          fontSize=8,
          textColor=colors.HexColor('#0f172a'),
      )
      cell_max = ParagraphStyle(
          'CellMax',
          parent=styles['Normal'],
          fontName='Helvetica-Oblique',
          fontSize=7,
          textColor=colors.HexColor('#64748b'),
      )
      th_style = ParagraphStyle(
          'ThStyle',
          parent=styles['Normal'],
          fontName='Helvetica-Bold',
          fontSize=7.5,
          textColor=colors.white,
          alignment=1,
      )
      info_style = ParagraphStyle(
          'InfoStyle',
          parent=styles['Normal'],
          fontName='Helvetica-Bold',
          fontSize=9,
          textColor=colors.HexColor('#1e293b'),
      )

      header_data = [
          [
              Paragraph(
                  'COMPLEXE SCOLAIRE MWANGAZA<br/><font size=8>GESTION DE'
                  ' SCOLARITÉ - Année 2026-2027</font>',
                  title_style,
              )
          ]
      ]
      header_table = Table(header_data, colWidths=[552])
      header_table.setStyle(
          TableStyle([
              ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#1e3d59')),
              ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
              ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
              ('TOPPADDING', (0, 0), (-1, -1), 12),
              ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
          ])
      )
      elements.append(header_table)
      elements.append(Spacer(1, 15))

      elements.append(Paragraph('EXTRAIT DU BULLETIN', main_title_style))
      elements.append(Spacer(1, 10))

      info_data = [
          [
              Paragraph(f'<b>ELEVE :</b> {eleve_selectionne}', info_style),
              Paragraph(f'<b>CLASSE :</b> {classe_active}', info_style),
          ],
          [
              Paragraph(f'<b>OPTION :</b> {opt_eleve}', info_style),
              Paragraph('<b>Année scolaire :</b> 2026-2027', info_style),
          ],
      ]
      info_table = Table(info_data, colWidths=[300, 252])
      info_table.setStyle(
          TableStyle([
              ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
              ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
              ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
              ('TOPPADDING', (0, 0), (-1, -1), 8),
              ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
              ('LEFTPADDING', (0, 0), (-1, -1), 10),
          ])
      )
      elements.append(info_table)
      elements.append(Spacer(1, 15))

      table_rows = [[
          Paragraph('MATIERE', th_style),
          Paragraph('P1', th_style),
          Paragraph('P2', th_style),
          Paragraph('EX S1', th_style),
          Paragraph('TOT S1', th_style),
          Paragraph('P3', th_style),
          Paragraph('P4', th_style),
          Paragraph('EX S2', th_style),
          Paragraph('TOT S2', th_style),
          Paragraph('TOTAL', th_style),
      ]]

      tot_p1, tot_p2, tot_ex1, tot_tots1 = 0.0, 0.0, 0.0, 0.0
      tot_p3, tot_p4, tot_ex2, tot_tots2, tot_general = 0.0, 0.0, 0.0, 0.0, 0.0
      m_tot_p1, m_tot_p2, m_tot_ex1, m_tot_tots1 = 0.0, 0.0, 0.0, 0.0
      m_tot_p3, m_tot_p4, m_tot_ex2, m_tot_tots2, m_tot_general = (
          0.0,
          0.0,
          0.0,
          0.0,
          0.0,
      )

      for _, row in data_eleve.iterrows():
        cours_nom = str(row['Cours']).upper()
        p1, p2, ex1 = float(row['P1']), float(row['P2']), float(row['Ex_S1'])
        tot_s1 = p1 + p2 + ex1
        p3, p4, ex2 = float(row['P3']), float(row['P4']), float(row['Ex_S2'])
        tot_s2 = p3 + p4 + ex2
        total_cours = tot_s1 + tot_s2

        m_row = max_classe[max_classe['Cours'].str.upper() == cours_nom]
        if not m_row.empty:
          mp1 = float(m_row.iloc[0]['Max_P1'])
          mp2 = float(m_row.iloc[0]['Max_P2'])
          mex1 = float(m_row.iloc[0]['Max_Ex1'])
          mp3 = float(m_row.iloc[0]['Max_P3'])
          mp4 = float(m_row.iloc[0]['Max_P4'])
          mex2 = float(m_row.iloc[0]['Max_Ex2'])
        else:
          mp1, mp2, mex1, mp3, mp4, mex2 = 20.0, 20.0, 40.0, 20.0, 20.0, 40.0

        mtot_s1 = mp1 + mp2 + mex1
        mtot_s2 = mp3 + mp4 + mex2
        m_total_cours = mtot_s1 + mtot_s2

        tot_p1 += p1
        tot_p2 += p2
        tot_ex1 += ex1
        tot_tots1 += tot_s1
        tot_p3 += p3
        tot_p4 += p4
        tot_ex2 += ex2
        tot_tots2 += tot_s2
        tot_general += total_cours

        m_tot_p1 += mp1
        m_tot_p2 += mp2
        m_tot_ex1 += mex1
        m_tot_tots1 += mtot_s1
        m_tot_p3 += mp3
        m_tot_p4 += mp4
        m_tot_ex2 += mex2
        m_tot_tots2 += mtot_s2
        m_tot_general += m_total_cours

        table_rows.append([
            Paragraph(f'<b>{cours_nom}</b>', cell_bold),
            Paragraph(str(p1), cell_bold),
            Paragraph(str(p2), cell_bold),
            Paragraph(str(ex1), cell_bold),
            Paragraph(str(tot_s1), cell_bold),
            Paragraph(str(p3), cell_bold),
            Paragraph(str(p4), cell_bold),
            Paragraph(str(ex2), cell_bold),
            Paragraph(str(tot_s2), cell_bold),
            Paragraph(str(total_cours), cell_bold),
        ])
        table_rows.append([
            Paragraph('MAX', cell_max),
            Paragraph(str(mp1), cell_max),
            Paragraph(str(mp2), cell_max),
            Paragraph(str(mex1), cell_max),
            Paragraph(str(mtot_s1), cell_max),
            Paragraph(str(mp3), cell_max),
            Paragraph(str(mp4), cell_max),
            Paragraph(str(mex2), cell_max),
            Paragraph(str(mtot_s2), cell_max),
            Paragraph(str(m_total_cours), cell_max),
        ])

      table_rows.append([
          Paragraph('<b>POINTS TOTAUX</b>', cell_bold),
          Paragraph(f'<b>{tot_p1}</b>', cell_bold),
          Paragraph(f'<b>{tot_p2}</b>', cell_bold),
          Paragraph(f'<b>{tot_ex1}</b>', cell_bold),
          Paragraph(f'<b>{tot_tots1}</b>', cell_bold),
          Paragraph(f'<b>{tot_p3}</b>', cell_bold),
          Paragraph(f'<b>{tot_p4}</b>', cell_bold),
          Paragraph(f'<b>{tot_ex2}</b>', cell_bold),
          Paragraph(f'<b>{tot_tots2}</b>', cell_bold),
          Paragraph(f'<b>{tot_general}</b>', cell_bold),
      ])
      table_rows.append([
          Paragraph('<b>MAX GENERAUX</b>', cell_max),
          Paragraph(str(m_tot_p1), cell_max),
          Paragraph(str(m_tot_p2), cell_max),
          Paragraph(str(m_tot_ex1), cell_max),
          Paragraph(str(m_tot_tots1), cell_max),
          Paragraph(str(m_tot_p3), cell_max),
          Paragraph(str(m_tot_p4), cell_max),
          Paragraph(str(m_tot_ex2), cell_max),
          Paragraph(str(m_tot_tots2), cell_max),
          Paragraph(str(m_tot_general), cell_max),
      ])

      grade_table = Table(
          table_rows,
          colWidths=[122, 45, 45, 45, 50, 45, 45, 45, 50, 60],
      )

      t_style = [
          ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2b6cb0')),
          ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
          ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
          ('TOPPADDING', (0, 0), (-1, -1), 4),
          ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
      ]

      row_count = len(data_eleve)
      for idx in range(row_count):
        r_idx = 1 + (idx * 2)
        if idx % 2 == 0:
          t_style.append(
              ('BACKGROUND', (0, r_idx), (-1, r_idx + 1), colors.HexColor('#f8fafc'))
          )

      tot_row_start = 1 + (row_count * 2)
      t_style.append(
          (
              'BACKGROUND',
              (0, tot_row_start),
              (-1, tot_row_start + 1),
              colors.HexColor('#e2e8f0'),
          )
      )

      grade_table.setStyle(TableStyle(t_style))
      elements.append(grade_table)

      doc.build(elements)
      buffer.seek(0)

      st.download_button(
          label="📥 Télécharger le bulletin PDF ultra-propre",
          data=buffer,
          file_name=f"bulletin_propre_{eleve_selectionne}_{classe_active}.pdf",
          mime="application/pdf",
      )
  else:
    st.warning("Aucune donnée trouvée pour cette classe.")