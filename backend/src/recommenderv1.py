
#! Adal'ın algoritması

import pandas as pd #pd kısaltmasıyla pandas kütüphanesini çağırdık, pd genel kullanımda bu şekilde
import os #OS Neydi? os emekti, şaka, OS meaning of Operating System.
from sklearn.feature_extraction.text import CountVectorizer # "Kelimeleri say ve bana kaç adım sağa, kaç adım yukarı gideceğimi söyleyen listeyi (vektörü) çıkar" 
                                                            #diyen araçtır.
from sklearn.metrics.pairwise import cosine_similarity #"O noktalar arasındaki açıyı ölç ve bana 0 ile 1 arasında bir puan ver" diyen matematikçidir.

class MovieRecommender:
    def __init__(self, data_path: str):
        """
        Adal'ın Movie Recommender algoritması
        Algoritma benzer çıkış yıllarına, türe, puanlamaya bakıyor
        
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

    def create_similarity_matrix(self):
        # Bilgisayara "Kelimeleri saymaya başla" diyoruz
        # Boş olan türler (genre) varsa hata vermemesi için fillna('') ekliyoruz
        cv = CountVectorizer()
        count_matrix = cv.fit_transform(self.df['genres'].fillna(''))

        # Puanları hesapla ve hafızaya (self) kaydet
        self.similarity_matrix = cosine_similarity(count_matrix)
        print(" Benzerlik motoru Adal tarafından başarıyla kuruldu!")

    def get_recommendations(self, movie_title: str):
        try:
            # 1. Girilen filmin tablodaki yerini (index) bulalım; Aramayı küçült
            search_term = movie_title.lower().strip()
            
            # 2. 'original_title' içinde bu kelime geçiyor mu? (Tam eşitlik bekleme)
            mask = self.df['original_title'].str.lower().str.contains(search_term, na=False)
            idx = self.df[mask].index[0]

            # 2. Bu filmin diğerleriyle olan puanlarını bir listeye alalım
            # (enumerate kullanıyoruz ki hangi puanın hangi filme ait olduğunu unutmayalım)
            sim_scores = list(enumerate(self.similarity_matrix[idx]))
            
            # 3. Puanlara göre büyükten küçüğe sıralayalım (X[1] puandır)
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            
            # 4. İlk film kendisidir, o yüzden 1'den 6'ya kadar olanları (en benzer 5) alalım
            sim_scores = sim_scores[1:6]
            
            # 5. Bu indexleri film isimlerine geri çevirelim
            movie_indices = [i[0] for i in sim_scores]
            return self.df['title'].iloc[movie_indices].tolist()
            
        except IndexError:
            return ["Hata: Film veritabanında bulunamadı!"]



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

    # Motoru çalıştır
    adal_motoru.create_similarity_matrix()
    
    # Gerçekten oluştu mu? Boyutuna bakalım:
    print(f" Matris Hazır! Boyut: {adal_motoru.similarity_matrix.shape}") #Burada veriyi elde ettik aslında.

    #Gelen veriyle konuşmamız lazım; bakalım motorumuz çalışıyor mu?
    test_film = "     toy story      " # Veritabanında olduğundan emin olduğun bir film yaz
    oneriler = adal_motoru.get_recommendations(test_film)

    # TEST: Sadece 'toy story' yazıyoruz, parantez falan yok!
    test_film = "toy story" 
    oneriler = adal_motoru.get_recommendations(test_film)
    
    print(f"\n '{test_film}' için öneriler:")
    for i, film in enumerate(oneriler, 1):
        print(f"{i}. {film}")