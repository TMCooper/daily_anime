class Cardinal():
    def save_files(html_constructed):
        
        with open('liste_animes2.html', 'w', encoding='utf-8') as file:
            file.write(html_constructed)