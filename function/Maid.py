# main.py
import tkinter as tk
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import pytz
from PIL import Image, ImageTk
from io import BytesIO
from tkinter import ttk

class AnimeViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Anime Viewer")
        self.root.state('zoomed')
        
        # Configuration initiale
        self.jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        self.animes_par_jour = {jour: [] for jour in self.jours}
        self.setup_ui()
        self.charger_donnees()

    def setup_ui(self):
        # Frame principale
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Barre de navigation
        self.nav_frame = ttk.Frame(self.main_frame)
        self.nav_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Boutons des jours
        for jour in self.jours:
            btn = ttk.Button(
                self.nav_frame,
                text=jour,
                command=lambda j=jour: self.afficher_jour(j)
            )
            btn.pack(side=tk.LEFT, padx=2)

        # Zone de contenu scrollable
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.content_frame)
        self.scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

    def charger_donnees(self):
        try:
            url = "https://animeschedule.net"
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Récupération des animes
            anime_list = soup.find_all('div', class_='timetable-column-show')
            
            # Reset des données
            self.animes_par_jour = {jour: [] for jour in self.jours}
            
            for anime in anime_list:
                try:
                    titre = anime.find('h2', class_='show-title-bar').get_text().strip()
                    episode = anime.find('span', class_='show-episode').get_text().strip()
                    time_element = anime.find('time', class_='show-air-time')
                    image = anime.find('img', class_='show-poster')
                    
                    if time_element and image:
                        # Conversion de l'heure en Europe/Paris
                        date_str = time_element['datetime']
                        date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        date_paris = date_obj.astimezone(pytz.timezone('Europe/Paris'))
                        
                        # Déterminer le jour en français
                        jour_index = date_paris.weekday()
                        jour = self.jours[jour_index]
                        
                        # Récupérer l'URL de l'image
                        image_url = image.get('data-src') or image.get('src')
                        
                        # Ajouter l'anime au jour correspondant
                        self.animes_par_jour[jour].append({
                            "titre": titre,
                            "episode": episode,
                            "horaire": date_paris,
                            "image": image_url
                        })
                        
                except Exception as e:
                    print(f"Erreur lors du traitement d'un anime: {e}")
                    continue
            
            # Afficher le jour actuel
            jour_actuel = self.jours[datetime.now().weekday()]
            self.afficher_jour(jour_actuel)
            
        except Exception as e:
            print(f"Erreur lors du chargement des données: {e}")
            self.afficher_erreur(f"Erreur lors du chargement des données: {str(e)}")

    def afficher_jour(self, jour):
        # Nettoyer l'affichage précédent
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Titre du jour
        ttk.Label(
            self.scrollable_frame,
            text=f"Animes du {jour}",
            font=('Helvetica', 14, 'bold')
        ).pack(pady=10)
        
        # Grid pour les animes
        grid_frame = ttk.Frame(self.scrollable_frame)
        grid_frame.pack(fill=tk.BOTH, expand=True, padx=10)
        
        animes = self.animes_par_jour.get(jour, [])
        if not animes:
            ttk.Label(
                self.scrollable_frame,
                text="Aucun anime pour ce jour",
                font=('Helvetica', 10, 'italic')
            ).pack(pady=20)
            return
        
        # Afficher les animes en grille
        for i, anime in enumerate(animes):
            self.creer_carte_anime(grid_frame, anime, i)

    def creer_carte_anime(self, parent, anime, index):
        frame = ttk.Frame(parent, relief="solid", borderwidth=1)
        frame.grid(row=index//2, column=index%2, padx=10, pady=10, sticky="nsew")
        
        # Titre
        ttk.Label(
            frame,
            text=anime["titre"],
            font=('Helvetica', 12, 'bold'),
            wraplength=300
        ).pack(pady=(5,0))
        
        # Image
        self.afficher_image_anime(frame, anime["image"])
        
        # Informations
        ttk.Label(
            frame,
            text=f"Épisode: {anime['episode']}",
            font=('Helvetica', 10)
        ).pack()
        
        ttk.Label(
            frame,
            text=f"Horaire: {anime['horaire'].strftime('%H:%M')}",
            font=('Helvetica', 10)
        ).pack()

    def afficher_image_anime(self, parent, url):
        try:
            response = requests.get(url)
            img = Image.open(BytesIO(response.content))
            img = img.resize((150, 200), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            label = ttk.Label(parent, image=photo)
            label.image = photo  # Garder une référence!
            label.pack(pady=5)
        except Exception as e:
            ttk.Label(
                parent,
                text="Image non disponible",
                font=('Helvetica', 10, 'italic')
            ).pack(pady=5)

    def afficher_erreur(self, message):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        ttk.Label(
            self.scrollable_frame,
            text=message,
            font=('Helvetica', 12, 'bold'),
            foreground='red'
        ).pack(pady=20)

def main():
    root = tk.Tk()
    app = AnimeViewer(root)
    root.mainloop()

if __name__ == "__main__":
    main()