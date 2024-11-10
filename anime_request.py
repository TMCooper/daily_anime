from function.__init__ import *

url_anime_daily = "https://animeschedule.net"

# Instancier la classe Yui
# yui = Yui()

def main():
    root = tk.Tk()
    app = AnimeViewer(root)
    root.mainloop()

if __name__ == "__main__":
    main()

# # Appeler la méthode sur l'instance
# animes_par_jour, html_render = yui.requesting_anime_daily(url_anime_daily)

# # Sauvegarder le rendu HTML
# Cardinal.save_files(html_render)