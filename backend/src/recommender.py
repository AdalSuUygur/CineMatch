
#! Adal'ın algoritması

import pandas as pd #pd kısaltmasıyla pandas kütüphanesini çağırdık, pd genel kullanımda bu şekilde
import os #OS Neydi? os emekti, şaka, OS meaning of Operating System.

class MovieRecommender:
    def __init__(self, data_path: str):
        """
        Adal'ın Movie Recommender algoritması
        
        """
        self.data_path = data_path
        self.df = None

    def load_data(self):
        """
        Bilgisayara "Dosya orada mı? diye soruyoruz.
        Gerekli veri setini verir.
        """
        if os.path.exists(self.data_path):
            self.df = pd.read_csv(self.data_path)
            print("Dosya bulundu, yükleniyor...")
        else:
            print("Dosya bulunamadı!")

# TEST BLOĞU
if __name__ == "__main__":
    # Bu satır, şu anki dosyanın (recommender.py) tam adresini bulur
    current_dir = os.path.dirname(__file__)
    
    # Adresi şu anki dosyaya göre tarif ediyoruz:
    # 'recommender.py' bir üst klasöre çık (..), 'data'ya gir, 'movies.csv'yi al
    yol = os.path.abspath(os.path.join(current_dir, '..', 'data', 'movies.csv'))
    
    print(f"Aranan tam yol: {yol}") # Hangi adrese baktığını terminalde görelim
    
    adal_motoru = MovieRecommender(yol)
    adal_motoru.load_data()