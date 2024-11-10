import tkinter as tk
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import pytz
from PIL import Image, ImageTk
from io import BytesIO
from tkinter import ttk
from collections import defaultdict

class AnimeViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Anime Viewer")
        self.root.state('zoomed')
        
        self.jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        self.animes_par_jour = {jour: [] for jour in self.jours}
        self.last_refresh = None
        
        self.root.bind('<Control-r>', self.refresh_data)
        
        self.setup_ui()
        self.charger_donnees()

    def setup_ui(self):
        # Frame principale avec configuration de poids
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Barre de navigation
        self.nav_frame = ttk.Frame(self.main_frame)
        self.nav_frame.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        
        # Boutons des jours
        for i, jour in enumerate(self.jours):
            self.nav_frame.grid_columnconfigure(i, weight=1)
            btn = ttk.Button(
                self.nav_frame,
                text=jour,
                command=lambda j=jour: self.afficher_jour(j)
            )
            btn.grid(row=0, column=i, padx=2, sticky='ew')

        # Bouton de rafraîchissement
        refresh_btn = ttk.Button(
            self.nav_frame,
            text="Rafraîchir (Ctrl+R)",
            command=lambda: self.refresh_data(None)
        )
        refresh_btn.grid(row=0, column=len(self.jours), padx=2)

        # Zone de contenu scrollable
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.grid(row=1, column=0, sticky='nsew')
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        # Canvas et scrollbar
        self.canvas = tk.Canvas(self.content_frame)
        self.scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.grid(row=0, column=0, sticky='nsew')
        self.scrollbar.grid(row=0, column=1, sticky='ns')
        
        self.canvas.bind('<Enter>', self._bound_to_mousewheel)
        self.canvas.bind('<Leave>', self._unbound_to_mousewheel)
        self.canvas.bind('<Configure>', self._on_canvas_configure)

    def _bound_to_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def refresh_data(self, event):
        self.charger_donnees(force_refresh=True)
        jour_actuel = self.jours[datetime.now().weekday()]
        self.afficher_jour(jour_actuel)

    def charger_donnees(self, force_refresh=False):
        if not force_refresh and self.last_refresh:
            return
            
        try:
            url = "https://animeschedule.net"
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            anime_list = soup.find_all('div', class_='timetable-column-show')
            temp_animes = defaultdict(lambda: defaultdict(dict))  # Changé en dict pour éviter les doublons
            
            for anime in anime_list:
                try:
                    titre = anime.find('h2', class_='show-title-bar').get_text().strip()
                    episode = anime.find('span', class_='show-episode').get_text().strip()
                    time_element = anime.find('time', class_='show-air-time')
                    image = anime.find('img', class_='show-poster')
                    
                    if time_element and image:
                        date_str = time_element['datetime']
                        date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        date_paris = date_obj.astimezone(pytz.timezone('Europe/Paris'))
                        
                        heure_key = date_paris.strftime('%H:%M')
                        jour_index = date_paris.weekday()
                        jour = self.jours[jour_index]
                        
                        image_url = image.get('data-src') or image.get('src')
                        
                        # Utiliser le titre comme clé unique pour éviter les doublons
                        temp_animes[jour][heure_key][titre] = {
                            "titre": titre,
                            "episode": episode,
                            "horaire": date_paris,
                            "image": image_url
                        }
                            
                except Exception as e:
                    print(f"Erreur lors du traitement d'un anime: {e}")
                    continue
            
            # Conversion des données temporaires en format final
            self.animes_par_jour = {jour: [] for jour in self.jours}
            for jour in self.jours:
                for heure in sorted(temp_animes[jour].keys()):
                    # Convertir le dictionnaire des animes en liste
                    animes_heure = list(temp_animes[jour][heure].values())
                    self.animes_par_jour[jour].extend(animes_heure)
            
            self.last_refresh = datetime.now()
            
        except Exception as e:
            print(f"Erreur lors du chargement des données: {e}")
            self.afficher_erreur(f"Erreur lors du chargement des données: {str(e)}")

    # ... (reste du code inchangé)

    def afficher_jour(self, jour):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        ttk.Label(
            self.scrollable_frame,
            text=f"Animes du {jour}",
            font=('Helvetica', 14, 'bold')
        ).pack(pady=10)
        
        if self.last_refresh:
            ttk.Label(
                self.scrollable_frame,
                text=f"Dernière mise à jour : {self.last_refresh.strftime('%H:%M:%S')}",
                font=('Helvetica', 10)
            ).pack(pady=(0, 10))
        
        grid_frame = ttk.Frame(self.scrollable_frame)
        grid_frame.pack(fill=tk.BOTH, expand=True, padx=10)
        
        grid_frame.grid_columnconfigure(0, weight=1)
        grid_frame.grid_columnconfigure(1, weight=1)
        
        animes = self.animes_par_jour.get(jour, [])
        if not animes:
            ttk.Label(
                self.scrollable_frame,
                text="Aucun anime pour ce jour",
                font=('Helvetica', 10, 'italic')
            ).pack(pady=20)
            return
        
        animes_sorted = sorted(animes, key=lambda x: x['horaire'])
        
        for i, anime in enumerate(animes_sorted):
            self.creer_carte_anime(grid_frame, anime, i)

    def creer_carte_anime(self, parent, anime, index):
        frame = ttk.Frame(parent, relief="solid", borderwidth=1)
        frame.grid(row=index//2, column=index%2, padx=10, pady=10, sticky="nsew")
        
        ttk.Label(
            frame,
            text=anime["titre"],
            font=('Helvetica', 12, 'bold'),
            wraplength=300
        ).pack(pady=(5,0))
        
        self.afficher_image_anime(frame, anime["image"])
        
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
            label.image = photo
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