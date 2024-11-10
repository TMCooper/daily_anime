from datetime import datetime
import pytz

class Tohru:
    @staticmethod
    def making_html_render(titre_tab, image_tag_tab, image_tab, horaire_tab, episode_tab, timezone='UTC'):
        # Liste des jours dans l'ordre
        jours_ordre = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

        # Obtenir le jour actuel
        jour_actuel = datetime.now(pytz.timezone(timezone)).strftime("%A")

        # Dictionnaire pour organiser les animes par jour
        animes_par_jour = {jour: [] for jour in jours_ordre}

        # Fuseau horaire spécifié
        tz = pytz.timezone(timezone)

        # Organisation des données
        for titre, image_tag, image, horaire, episode in zip(titre_tab, image_tag_tab, image_tab, horaire_tab, episode_tab):
            try:
                if horaire:
                    # Conversion de la date ISO en objet datetime
                    date_obj = datetime.fromisoformat(horaire)
                    date_obj = date_obj.astimezone(tz)
                    
                    # Déterminer le jour de la semaine
                    jour = jours_ordre[date_obj.weekday()]
                    
                    # Ajouter l'anime dans la liste du jour correspondant
                    animes_par_jour[jour].append({
                        "titre": titre,
                        "image": image,
                        "image_tag": image_tag,
                        "horaire": date_obj,
                        "date": date_obj.strftime("%d %B %Y"),
                        "episode": episode
                    })
            except Exception as e:
                print(f"Erreur lors du traitement de l'horaire: {e}")
                continue

        # Trouver le nombre maximal d'animes par jour
        max_animes_par_jour = max(len(animes) for animes in animes_par_jour.values())

        # Construction du HTML
        html_render = '''
        <html>
            <head>
                <title>Liste d'animes</title>
                <style>
                    table { width: 100%; border-collapse: collapse; }
                    th, td { padding: 10px; border: 1px solid #ddd; text-align: left; vertical-align: top; }
                    th { background-color: #f4f4f4; }
                    img { width: 100px; height: auto; }
                    .current-day { background-color: #B0E0E6; font-weight: bold; }
                </style>
            </head>
            <body>
                <h1>Liste des Animes de la semaine</h1>
                <table>
                    <thead>
                        <tr>
        '''

        # En-têtes des jours
        for jour in jours_ordre:
            day_class = "current-day" if jour == jour_actuel else ""
            html_render += f'<th class="{day_class}">{jour}</th>'

        html_render += '''
                        </tr>
                    </thead>
                    <tbody>
        '''

        # Contenu du tableau
        for i in range(max_animes_par_jour):
            html_render += "<tr>"
            for jour in jours_ordre:
                html_render += "<td>"
                if i < len(animes_par_jour[jour]):
                    anime = animes_par_jour[jour][i]
                    horaire_str = anime['horaire'].strftime("%H:%M")

                    html_render += f'''
                        <div>
                            <p><strong>{anime["titre"]}</strong></p>
                            {anime["image_tag"]}
                            <p>Horaire : {horaire_str}</p>
                            <p>Date : {anime["date"]}</p>
                            <p>Épisode : {anime["episode"]}</p>
                        </div>
                    '''
                html_render += "</td>"
            html_render += "</tr>"

        html_render += '''
                    </tbody>
                </table>
            </body>
        </html>
        '''

        return html_render