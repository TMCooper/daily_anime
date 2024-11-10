import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
from function.Tohru import Tohru

class Yui:
    def __init__(self):
        self.jours_semaine = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        
    def parse_date(self, date_string):
        """Parse une date ISO 8601 et retourne un objet datetime"""
        try:
            # Remplacer 'Z' par '+00:00' pour la compatibilité
            if date_string.endswith('Z'):
                date_string = date_string[:-1] + '+00:00'
            return datetime.fromisoformat(date_string)
        except Exception as e:
            print(f"Erreur lors du parsing de la date {date_string}: {e}")
            return None

    def requesting_anime_daily(self, url_anime_daily):
        titre_tab = []
        image_tag_tab = []
        image_tab = []
        horaire_tab = []
        episode_tab = []
        
        animes_par_jour = {jour: [] for jour in self.jours_semaine}
        
        try:
            response = requests.get(url_anime_daily)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            anime_list = soup.find_all('div', class_='timetable-column-show')
            anime_titles = set()
            
            for anime in anime_list:
                try:
                    title_element = anime.find('h2', class_='show-title-bar')
                    episode_element = anime.find('span', class_='show-episode')
                    time_element = anime.find('time', class_='show-air-time')
                    image_element = anime.find('img', class_='show-poster')
                    
                    if title_element and episode_element:
                        anime_name = title_element.get_text().strip()
                        
                        if anime_name not in anime_titles:
                            anime_titles.add(anime_name)
                            
                            episodes = episode_element.get_text().strip()
                            air_time = time_element['datetime'] if time_element else None
                            
                            # Utiliser la nouvelle méthode de parsing de date
                            if air_time:
                                date_obj = self.parse_date(air_time)
                                if date_obj:
                                    air_time = date_obj.isoformat()
                                else:
                                    continue
                            
                            image_src = image_element.get('data-src') if image_element else None
                            if not image_src:
                                image_src = image_element.get('src') if image_element else "Image non disponible"
                            
                            # Incrémentation des listes
                            titre_tab.append(anime_name)
                            episode_tab.append(episodes)
                            horaire_tab.append(air_time)
                            image_tab.append(image_src)
                            
                            image_tag = f'<img src="{image_src}" alt="{anime_name}" class="anime-poster">'
                            image_tag_tab.append(image_tag)
                            
                except Exception as e:
                    print(f"Erreur lors du traitement d'un anime : {str(e)}")
                    continue
            
            # Création du rendu HTML avec Tohru
            html_render = Tohru.making_html_render(
                titre_tab,
                image_tag_tab,
                image_tab,
                horaire_tab,
                episode_tab,
                timezone='Europe/Paris'
            )
            
            return animes_par_jour, html_render
            
        except requests.RequestException as e:
            print(f"Erreur lors de la requête : {str(e)}")
            return {}, ""