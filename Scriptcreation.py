import pandas as pd
import numpy as np
from sqlalchemy import create_engine, exc, text

print("Lecture du fichier CSV...")
df = pd.read_csv('fifa_players.csv', sep=',')

df = df.rename(columns={
    'international_reputation(1-5)': 'reputation',
    'weak_foot(1-5)': 'pied_faible',
    'skill_moves(1-5)': 'gestes_techniques'
})

df['id_joueur'] = range(1, len(df) + 1)
df['prenom'] = df['full_name'].str.split().str[0]
df['nom'] = df['full_name'].str.split().str[1:].str.join(' ')

df = df.replace({np.nan: None})

df['birth_date'] = pd.to_datetime(df['birth_date'], format='%m/%d/%Y', errors='coerce').dt.strftime('%Y-%m-%d')
df = df.replace({np.nan: None})

df_nat = pd.DataFrame({'libelle_nationalite': df['nationality'].dropna().unique()})
df_nat['id_nationalite'] = range(1, len(df_nat) + 1)

df_eq = pd.DataFrame({'nom_equipe': df['national_team'].dropna().unique()})
df_eq['id_equipe'] = range(1, len(df_eq) + 1)

all_positions = set()
for pos_str in df['positions'].dropna():
    for p in pos_str.split(','):
        all_positions.add(p.strip())
df_pos = pd.DataFrame({'libelle_poste': list(all_positions)})
df_pos['id_poste'] = range(1, len(df_pos) + 1)

df = df.merge(df_nat, left_on='nationality', right_on='libelle_nationalite', how='left')
df = df.merge(df_eq, left_on='national_team', right_on='nom_equipe', how='left')
df = df.replace({np.nan: None})

engine = create_engine("postgresql://<login>:<mdp>@londres/<dblogin>")

try:
    with engine.connect() as co:
        with co.begin():
            print("Suppression des anciennes tables...")
            co.execute(text('DROP TABLE IF EXISTS JOUE_POSTE CASCADE;'))
            co.execute(text('DROP TABLE IF EXISTS STATS_FIFA CASCADE;'))
            co.execute(text('DROP TABLE IF EXISTS STATS_TECHNIQUES CASCADE;'))
            co.execute(text('DROP TABLE IF EXISTS STATS_PHYSIQUES CASCADE;'))
            co.execute(text('DROP TABLE IF EXISTS JOUEUR_EQUIPE_NATIONALE CASCADE;'))
            co.execute(text('DROP TABLE IF EXISTS JOUEUR CASCADE;'))
            co.execute(text('DROP TABLE IF EXISTS POSITION CASCADE;'))
            co.execute(text('DROP TABLE IF EXISTS EQUIPE_NATIONALE CASCADE;'))
            co.execute(text('DROP TABLE IF EXISTS NATIONALITE CASCADE;'))

            print("Créaation des tables...")
            co.execute(text('''CREATE TABLE NATIONALITE (
                id_nationalite numeric PRIMARY KEY,
                libelle_nationalite varchar(100)
            );'''))
            co.execute(text('''CREATE TABLE EQUIPE_NATIONALE (
                id_equipe numeric PRIMARY KEY,
                nom_equipe varchar(100)
            );'''))
            co.execute(text('''CREATE TABLE POSITION (
                id_poste numeric PRIMARY KEY,
                libelle_poste varchar(10)
            );'''))
            co.execute(text('''CREATE TABLE JOUEUR (
                id_joueur numeric PRIMARY KEY,
                nom varchar(150),
                prenom varchar(150),
                date_naissance date,
                age numeric,
                taille_cm numeric,
                poids_kg numeric,
                pied_fort varchar(10),
                morphologie varchar(50),
                id_nationalite numeric REFERENCES NATIONALITE
            );'''))
            co.execute(text('''CREATE TABLE JOUE_POSTE (
                id_joueur numeric REFERENCES JOUEUR,
                id_poste numeric REFERENCES POSITION,
                PRIMARY KEY (id_joueur, id_poste)
            );'''))
            co.execute(text('''CREATE TABLE JOUEUR_EQUIPE_NATIONALE (
                id_joueur numeric PRIMARY KEY REFERENCES JOUEUR,
                id_equipe numeric REFERENCES EQUIPE_NATIONALE,
                note_selection numeric,
                poste_selection varchar(10),
                numero_maillot numeric
            );'''))
            co.execute(text('''CREATE TABLE STATS_PHYSIQUES (
                id_stats_phys numeric PRIMARY KEY,
                id_joueur numeric UNIQUE REFERENCES JOUEUR,
                acceleration numeric, vitesse_sprint numeric, agilite numeric,
                reactivite numeric, equilibre numeric, puissance_frappe numeric,
                detente numeric, endurance numeric, force numeric,
                agressivite numeric, sang_froid numeric
            );'''))
            co.execute(text('''CREATE TABLE STATS_TECHNIQUES (
                id_stats_tech numeric PRIMARY KEY,
                id_joueur numeric UNIQUE REFERENCES JOUEUR,
                centre numeric, finition numeric, jeu_tete numeric,
                passe_courte numeric, volees numeric, dribble numeric,
                effet numeric, coup_franc numeric, passe_longue numeric,
                controle_balle numeric, frappes_lointaines numeric, interceptions numeric,
                positionnement numeric, vision_jeu numeric, penalty numeric,
                marquage numeric, tacle_debout numeric, tacle_glisse numeric
            );'''))
            co.execute(text('''CREATE TABLE STATS_FIFA (
                id_stats_fifa numeric PRIMARY KEY,
                id_joueur numeric UNIQUE REFERENCES JOUEUR,
                note_globale numeric, potentiel numeric, valeur_marchande numeric,
                salaire_hebdomadaire numeric, reputation numeric, pied_faible numeric,
                gestes_techniques numeric, clause_liberatoire numeric
            );'''))

        with co.begin():
            print("1/4 - Insertion des Nationalités, équipes et Positions...")
            for row in df_nat.itertuples():
                co.execute(text("INSERT INTO NATIONALITE VALUES (:id, :lib);"),
                           {'id': row.id_nationalite, 'lib': row.libelle_nationalite})
            for row in df_eq.itertuples():
                co.execute(text("INSERT INTO EQUIPE_NATIONALE VALUES (:id, :nom);"),
                           {'id': row.id_equipe, 'nom': row.nom_equipe})
            for row in df_pos.itertuples():
                co.execute(text("INSERT INTO POSITION VALUES (:id, :lib);"),
                           {'id': row.id_poste, 'lib': row.libelle_poste})

        print("2/4 - Insertion des Joueurs et de leurs Statistiques...")
        nb_ok = 0
        nb_err = 0
        joueurs_inseres = set()
        for row in df.itertuples():
            try:
                with co.begin():
                    co.execute(text('''INSERT INTO JOUEUR VALUES
                        (:id, :nom, :prenom, :date_n, :age, :taille, :poids, :pied, :morph, :id_nat);'''),
                        {'id': row.id_joueur, 'nom': row.nom, 'prenom': row.prenom,
                         'date_n': row.birth_date, 'age': row.age,
                         'taille': row.height_cm, 'poids': row.weight_kgs,
                         'pied': row.preferred_foot, 'morph': row.body_type,
                         'id_nat': row.id_nationalite})

                    co.execute(text('''INSERT INTO STATS_PHYSIQUES VALUES
                        (:id, :id_joueur, :acc, :vit, :agi, :rea, :equ, :pui, :det, :end, :force, :agre, :sang);'''),
                        {'id': row.id_joueur, 'id_joueur': row.id_joueur,
                         'acc': row.acceleration, 'vit': row.sprint_speed, 'agi': row.agility,
                         'rea': row.reactions, 'equ': row.balance, 'pui': row.shot_power,
                         'det': row.jumping, 'end': row.stamina, 'force': row.strength,
                         'agre': row.aggression, 'sang': row.composure})

                    co.execute(text('''INSERT INTO STATS_TECHNIQUES VALUES
                        (:id, :id_joueur, :cen, :fin, :tete, :pass_c, :vol, :dri, :eff,
                         :coup_f, :pass_l, :cont, :frap, :int, :pos, :vis, :pen, :marq, :tac_d, :tac_g);'''),
                        {'id': row.id_joueur, 'id_joueur': row.id_joueur,
                         'cen': row.crossing, 'fin': row.finishing, 'tete': row.heading_accuracy,
                         'pass_c': row.short_passing, 'vol': row.volleys, 'dri': row.dribbling,
                         'eff': row.curve, 'coup_f': row.freekick_accuracy,
                         'pass_l': row.long_passing, 'cont': row.ball_control,
                         'frap': row.long_shots, 'int': row.interceptions,
                         'pos': row.positioning, 'vis': row.vision, 'pen': row.penalties,
                         'marq': row.marking, 'tac_d': row.standing_tackle, 'tac_g': row.sliding_tackle})

                    co.execute(text('''INSERT INTO STATS_FIFA VALUES
                        (:id, :id_joueur, :note, :pot, :val, :sal, :rep, :pied_f, :gestes, :clause);'''),
                        {'id': row.id_joueur, 'id_joueur': row.id_joueur,
                         'note': row.overall_rating, 'pot': row.potential,
                         'val': row.value_euro, 'sal': row.wage_euro,
                         'rep': row.reputation, 'pied_f': row.pied_faible,
                         'gestes': row.gestes_techniques, 'clause': row.release_clause_euro})

                    if row.id_equipe is not None:
                        co.execute(text('''INSERT INTO JOUEUR_EQUIPE_NATIONALE VALUES
                            (:id, :id_eq, :note_sel, :poste_sel, :num);'''),
                            {'id': row.id_joueur, 'id_eq': row.id_equipe,
                             'note_sel': row.national_rating,
                             'poste_sel': row.national_team_position,
                             'num': row.national_jersey_number})

                    nb_ok += 1
                    joueurs_inseres.add(row.id_joueur)

            except Exception as e:
                nb_err += 1
                print(f" Erreur joueur id={row.id_joueur} ({row.full_name}): {e}")
        print(f" {nb_ok} joueurs insérés, {nb_err} erreurs ignorées")

        with co.begin():
            for row in df.itertuples():
                if row.positions is not None and row.id_joueur in joueurs_inseres:
                    joueur_postes = [p.strip() for p in row.positions.split(',')]
                    for poste_str in joueur_postes:
                        id_p = df_pos.loc[df_pos['libelle_poste'] == poste_str, 'id_poste'].values[0]
                        co.execute(text("INSERT INTO JOUE_POSTE VALUES (:id_j, :id_p);"),
                                   {'id_j': row.id_joueur, 'id_p': int(id_p)})
        print("IMPORTATION TERMINÉE AVEC SUCCÉS !")

except exc.SQLAlchemyError as e:
    print("Erreur de base de données :", e)