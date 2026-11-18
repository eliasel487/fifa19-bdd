#!/bin/python3
import pandas as pd
from sqlalchemy import create_engine, exc, text
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# Configuration de la connexion
engine = create_engine("postgresql://<login>:<mdp>@londres/<dblogin>")

try:
    with engine.connect() as co:
        # --- 1. GARDIENS ---
        df_gk = pd.read_sql(text('''
            SELECT nom, note_globale, potentiel
            FROM (
                SELECT DISTINCT ON (j.id_joueur)
                       j.id_joueur,
                       j.prenom || ' ' || j.nom AS nom,
                       sf.note_globale,
                       sf.potentiel
                FROM JOUEUR j
                JOIN STATS_FIFA sf ON j.id_joueur = sf.id_joueur
                JOIN NATIONALITE n ON j.id_nationalite = n.id_nationalite
                WHERE n.libelle_nationalite = 'France'
                  AND j.id_joueur IN (
                      SELECT jp.id_joueur FROM JOUE_POSTE jp
                      JOIN POSITION p ON jp.id_poste = p.id_poste
                      WHERE p.libelle_poste = 'GK'
                  )
                ORDER BY j.id_joueur
            ) AS sous_requete
            ORDER BY note_globale DESC
            LIMIT 10;
        '''), con=co)

        fig = df_gk.plot(x='nom', y=['note_globale', 'potentiel'], kind='bar')
        fig.set_title('Gardiens français - Note globale et potentiel (Top 10)')
        fig.set_xlabel('Gardien')
        fig.set_ylabel('Note FIFA')
        fig.set_ylim(0, 100)
        fig.set_xticklabels(df_gk['nom'], rotation=30, ha='right')
        fig.legend(['Note globale', 'Potentiel'])
        fig.axhline(df_gk['note_globale'].iloc[2], color='red', linestyle='--', linewidth=1.5)
        plt.tight_layout()
        plt.show()

        # --- 2. DEFENSEURS ---
        df_def = pd.read_sql(text('''
            SELECT nom, marquage, tacle_debout, tacle_glisse, force
            FROM (
                SELECT DISTINCT ON (j.id_joueur)
                       j.id_joueur,
                       j.prenom || ' ' || j.nom AS nom,
                       sf.note_globale,
                       st.marquage,
                       st.tacle_debout,
                       st.tacle_glisse,
                       sp.force
                FROM JOUEUR j
                JOIN STATS_TECHNIQUES st ON j.id_joueur = st.id_joueur
                JOIN STATS_PHYSIQUES sp ON j.id_joueur = sp.id_joueur
                JOIN STATS_FIFA sf ON j.id_joueur = sf.id_joueur
                JOIN NATIONALITE n ON j.id_nationalite = n.id_nationalite
                WHERE n.libelle_nationalite = 'France'
                  AND j.id_joueur IN (
                      SELECT jp.id_joueur FROM JOUE_POSTE jp
                      JOIN POSITION p ON jp.id_poste = p.id_poste
                      WHERE p.libelle_poste IN ('CB', 'LB', 'RB', 'LWB', 'RWB')
                  )
                ORDER BY j.id_joueur
            ) AS sous_requete
            ORDER BY note_globale DESC
            LIMIT 15;
        '''), con=co)

        fig2 = df_def.plot(x='nom', y=['marquage', 'tacle_debout', 'tacle_glisse', 'force'], kind='bar')
        fig2.set_title('Défenseurs français - Marquage, Tacles, Force (Top 15)')
        fig2.set_xlabel('Défenseur')
        fig2.set_ylabel('Note FIFA')
        fig2.set_ylim(0, 110)
        fig2.set_xticklabels(df_def['nom'], rotation=40, ha='right')
        fig2.legend(['Marquage', 'Tacle debout', 'Tacle glissé', 'Force'])
        fig2.axvline(8.5, color='red', linestyle='--', linewidth=1.5)
        plt.tight_layout()
        plt.show()

        # --- 3. MILIEUX ---
        df_mil = pd.read_sql(text('''
            SELECT nom, vision_jeu, interceptions, endurance
            FROM (
                SELECT DISTINCT ON (j.id_joueur)
                       j.id_joueur,
                       j.prenom || ' ' || j.nom AS nom,
                       sf.note_globale,
                       st.vision_jeu,
                       st.interceptions,
                       sp.endurance
                FROM JOUEUR j
                JOIN STATS_TECHNIQUES st ON j.id_joueur = st.id_joueur
                JOIN STATS_PHYSIQUES sp ON j.id_joueur = sp.id_joueur
                JOIN STATS_FIFA sf ON j.id_joueur = sf.id_joueur
                JOIN NATIONALITE n ON j.id_nationalite = n.id_nationalite
                WHERE n.libelle_nationalite = 'France'
                  AND j.id_joueur IN (
                      SELECT jp.id_joueur FROM JOUE_POSTE jp
                      JOIN POSITION p ON jp.id_poste = p.id_poste
                      WHERE p.libelle_poste IN ('CM', 'CAM', 'CDM')
                  )
                ORDER BY j.id_joueur
            ) AS sous_requete
            ORDER BY note_globale DESC
            LIMIT 15;
        '''), con=co)

        fig3 = df_mil.plot(x='nom', y=['vision_jeu', 'interceptions', 'endurance'], kind='bar')
        fig3.set_title('Milieux français - Vision, Interceptions, Endurance (Top 15)')
        fig3.set_xlabel('Milieu')
        fig3.set_ylabel('Note FIFA')
        fig3.set_ylim(0, 110)
        fig3.set_xticklabels(df_mil['nom'], rotation=40, ha='right')
        fig3.legend(['Vision de jeu', 'Interceptions', 'Endurance'])
        fig3.axvline(6.5, color='red', linestyle='--', linewidth=1.5)
        plt.tight_layout()
        plt.show()

        # --- 4. ATTAQUANTS ---
        df_att = pd.read_sql(text('''
            SELECT nom, finition, vitesse_sprint, dribble
            FROM (
                SELECT DISTINCT ON (j.id_joueur)
                       j.id_joueur,
                       j.prenom || ' ' || j.nom AS nom,
                       sf.note_globale,
                       st.finition,
                       sp.vitesse_sprint,
                       st.dribble
                FROM JOUEUR j
                JOIN STATS_TECHNIQUES st ON j.id_joueur = st.id_joueur
                JOIN STATS_PHYSIQUES sp ON j.id_joueur = sp.id_joueur
                JOIN STATS_FIFA sf ON j.id_joueur = sf.id_joueur
                JOIN NATIONALITE n ON j.id_nationalite = n.id_nationalite
                WHERE n.libelle_nationalite = 'France'
                  AND j.id_joueur IN (
                      SELECT jp.id_joueur FROM JOUE_POSTE jp
                      JOIN POSITION p ON jp.id_poste = p.id_poste
                      WHERE p.libelle_poste IN ('ST', 'CF', 'LW', 'RW', 'LM', 'RM')
                  )
                ORDER BY j.id_joueur
            ) AS sous_requete
            ORDER BY note_globale DESC
            LIMIT 15;
        '''), con=co)

        fig4 = df_att.plot(x='nom', y=['finition', 'vitesse_sprint', 'dribble'], kind='bar')
        fig4.set_title('Attaquants français - Finition, Vitesse, Dribble (Top 15)')
        fig4.set_xlabel('Attaquant')
        fig4.set_ylabel('Note FIFA')
        fig4.set_ylim(0, 110)
        fig4.set_xticklabels(df_att['nom'], rotation=40, ha='right')
        fig4.legend(['Finition', 'Vitesse sprint', 'Dribble'])
        fig4.axvline(6.5, color='red', linestyle='--', linewidth=1.5)
        plt.tight_layout()
        plt.show()

        # --- 5. LES 26 DE DESCHAMPS ---
        df_26 = pd.read_sql(text('''
            (SELECT nom, note_globale, 'Gardien' AS ligne
             FROM (
                 SELECT DISTINCT ON (j.id_joueur)
                        j.id_joueur,
                        j.prenom || ' ' || j.nom AS nom,
                        sf.note_globale
                 FROM JOUEUR j
                 JOIN STATS_FIFA sf ON j.id_joueur = sf.id_joueur
                 JOIN NATIONALITE n ON j.id_nationalite = n.id_nationalite
                 WHERE n.libelle_nationalite = 'France'
                   AND j.id_joueur IN (
                       SELECT jp.id_joueur FROM JOUE_POSTE jp
                       JOIN POSITION p ON jp.id_poste = p.id_poste
                       WHERE p.libelle_poste = 'GK'
                   )
                 ORDER BY j.id_joueur
             ) t ORDER BY note_globale DESC LIMIT 3)
            UNION ALL
            (SELECT nom, note_globale, 'Defenseur' AS ligne
             FROM (
                 SELECT DISTINCT ON (j.id_joueur)
                        j.id_joueur,
                        j.prenom || ' ' || j.nom AS nom,
                        sf.note_globale
                 FROM JOUEUR j
                 JOIN STATS_FIFA sf ON j.id_joueur = sf.id_joueur
                 JOIN NATIONALITE n ON j.id_nationalite = n.id_nationalite
                 WHERE n.libelle_nationalite = 'France'
                   AND j.id_joueur IN (
                       SELECT jp.id_joueur FROM JOUE_POSTE jp
                       JOIN POSITION p ON jp.id_poste = p.id_poste
                       WHERE p.libelle_poste IN ('CB', 'LB', 'RB', 'LWB', 'RWB')
                   )
                 ORDER BY j.id_joueur
             ) t ORDER BY note_globale DESC LIMIT 9)
            UNION ALL
            (SELECT nom, note_globale, 'Milieu' AS ligne
             FROM (
                 SELECT DISTINCT ON (j.id_joueur)
                        j.id_joueur,
                        j.prenom || ' ' || j.nom AS nom,
                        sf.note_globale
                 FROM JOUEUR j
                 JOIN STATS_FIFA sf ON j.id_joueur = sf.id_joueur
                 JOIN NATIONALITE n ON j.id_nationalite = n.id_nationalite
                 WHERE n.libelle_nationalite = 'France'
                   AND j.id_joueur IN (
                       SELECT jp.id_joueur FROM JOUE_POSTE jp
                       JOIN POSITION p ON jp.id_poste = p.id_poste
                       WHERE p.libelle_poste IN ('CM', 'CAM', 'CDM')
                   )
                 ORDER BY j.id_joueur
             ) t ORDER BY note_globale DESC LIMIT 7)
            UNION ALL
            (SELECT nom, note_globale, 'Attaquant' AS ligne
             FROM (
                 SELECT DISTINCT ON (j.id_joueur)
                        j.id_joueur,
                        j.prenom || ' ' || j.nom AS nom,
                        sf.note_globale
                 FROM JOUEUR j
                 JOIN STATS_FIFA sf ON j.id_joueur = sf.id_joueur
                 JOIN NATIONALITE n ON j.id_nationalite = n.id_nationalite
                 WHERE n.libelle_nationalite = 'France'
                   AND j.id_joueur IN (
                       SELECT jp.id_joueur FROM JOUE_POSTE jp
                       JOIN POSITION p ON jp.id_poste = p.id_poste
                       WHERE p.libelle_poste IN ('ST', 'CF', 'LW', 'RW', 'LM', 'RM')
                   )
                 ORDER BY j.id_joueur
             ) t ORDER BY note_globale DESC LIMIT 7)
            ORDER BY ligne, note_globale DESC;
        '''), con=co)

        couleurs = {'Gardien': 'grey', 'Defenseur': '#002395',
                    'Milieu': '#ED2939', 'Attaquant': '#1a7a4a'}

        fig5 = df_26.plot(x='nom', y='note_globale', kind='bar', legend=False,
                          color=[couleurs[l] for l in df_26['ligne']])
        fig5.set_title('Liste des 26 de Deschamps - Note globale FIFA 19')
        fig5.set_xlabel('Joueur')
        fig5.set_ylabel('Note globale')
        fig5.set_ylim(0, 100)
        fig5.set_xticklabels(df_26['nom'], rotation=45, ha='right')
        fig5.legend(handles=[
            Patch(color='grey',    label='Gardien'),
            Patch(color='#002395', label='Defenseur'),
            Patch(color='#ED2939', label='Milieu'),
            Patch(color='#1a7a4a', label='Attaquant'),
        ])
        plt.tight_layout()
        plt.show()

        # --- 6. MOYENNES FRANCE ---
        df_fr_moy = pd.read_sql(text('''
            SELECT
                ROUND(AVG(sf.note_globale), 1)   AS note_globale,
                ROUND(AVG(st.finition), 1)        AS finition,
                ROUND(AVG(st.vision_jeu), 1)      AS vision_jeu,
                ROUND(AVG(st.dribble), 1)         AS dribble,
                ROUND(AVG(sp.vitesse_sprint), 1)  AS vitesse_sprint,
                ROUND(AVG(sp.endurance), 1)       AS endurance,
                ROUND(AVG(sp.force), 1)           AS force
            FROM JOUEUR j
            JOIN STATS_FIFA sf        ON j.id_joueur = sf.id_joueur
            JOIN STATS_TECHNIQUES st  ON j.id_joueur = st.id_joueur
            JOIN STATS_PHYSIQUES sp   ON j.id_joueur = sp.id_joueur
            JOIN NATIONALITE n        ON j.id_nationalite = n.id_nationalite
            WHERE n.libelle_nationalite = 'France';
        '''), con=co)

        categories = ['Note globale', 'Finition', 'Vision de jeu',
                      'Dribble', 'Vitesse sprint', 'Endurance', 'Force']
        valeurs = df_fr_moy.iloc[0].values

        fig6, ax6 = plt.subplots(figsize=(10, 5))
        bars = ax6.bar(categories, valeurs, color='#002395', edgecolor='white')
        ax6.set_title('France - Moyennes des stats clés (tous joueurs FIFA 19)')
        ax6.set_ylabel('Note moyenne FIFA')
        ax6.set_ylim(0, 100)
        for bar, val in zip(bars, valeurs):
            ax6.text(bar.get_x() + bar.get_width() / 2,
                     bar.get_height() + 1, str(val),
                     ha='center', va='bottom', fontsize=9, color='black')
        plt.tight_layout()
        plt.show()

except exc.SQLAlchemyError as e:
    print("Erreur de base de données :", e)