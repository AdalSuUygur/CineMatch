
#! Adal'ın algoritması - Versiyon 2.0 (Metadata Destekli)

# ---------------------------------
# Hazırlık (Kütüphaneler)
# ---------------------------------
import pandas as pd # Python'un Excel'i olarak Pandas Kütüphanesi. Veriyi tablo halinde tutmamızı, okumamızı ve filtrelememizi sağlar.
#* Neden: .csv dosyasını okuyup hafızada tutmak için.
import os # İşletim sistemiyle konuşur. "Şu dosya orada mı?" kontrolünü yapar. OS Neydi? OS emekti. OS yani Operating System.
#* Neden: Dosya yolu (path) hatalarını önlemek için.
from sklearn.feature_extraction.text import CountVectorizer # Kelime sayıcı. Metinleri bilgisayarın anlayacağı sayılara (vektörlere) çevirir.
#* Neden: Bilgisayar kelimelerden anlamaz, "1" ve "0"dan anlar. Çevirici lazım.
from sklearn.metrics.pairwise import cosine_similarity # İki sayı dizisi arasındaki benzerliği ölçer.
#* Neden: Hangi filmin diğerine ne kadar benzediğini matematiksel olarak hesaplamak için.

# ---------------------------------
# Kalıbı Kurmak (Class ve Init)
# ---------------------------------
class MovieRecommender: # Recommender motorumuz.

    def __init__(self, data_path: str): # Başlatıcı, kontak çevirdiğinde yapılacak ayarlar.
        """
        Adal'ın Movie Recommender algoritması
        """
        self.data_path = data_path # Dosyanın nerede olduğunu hafızaya atar. Beyin bedava.
        self.df = None # Verisizken patlamayalım. Henüz yüklemedik çünkü de veriyi destur.
        self.similarity_matrix = None # Henüz hesaplama yapmadık, sonuçlar için yer ayırdık.
        #* Neden inite ekliyoruz peki?
        #* Çünkü canısı motor başlar başlamaz ağır işlemleri yapıp bilgisayarı kilitlemeyelim. Veriyi sonra yükleyeceğiz (Lazy Loading).

# ---------------------------------
# Veriyi İçeri Almak (load_data)
# ---------------------------------
    def load_data(self):
            """
            Yeni veri setini yükler ve kontrol eder.
            """
            if os.path.exists(self.data_path): # Burdaki amaç: Kör uçuş yapmamak. Dosya orada yoksa programın çökmesini engeller.

                self.df = pd.read_csv(self.data_path) # CSV dosyasındaki virgülle ayrılmış yazıları alır, satır ve sütunlardan oluşan bir tabloya (DataFrame) çevirir.
                print(f" Dosya yüklendi! Toplam Film: {len(self.df)}")
                print("Örnek veri (ilk satır):")
                print(self.df.iloc[0]['llm_metadata']) # Buradaki amaç, verinin doğru formatta gelip gelmediğini gözle teyit etmek.

            else:
                print(" Dosya bulunamadı!")

# ---------------------------------
# Beyin (Matris Oluşturma)
# ---------------------------------
    def create_similarity_matrix(self): # Burası projenin beyni 
        """
        Artık sadece türlere değil, llm_metadata içindeki tüm bilgilere
        (Tür, Yıl, Puan, Popülerlik) bakarak benzerlik kuruyoruz.
        """
        # Türkçe ve İngilizce kelimeleri analiz edecek
        cv = CountVectorizer() # Kelime sayma machine
        
        #* self.df['llm_metadata'].fillna(''): Tablodaki llm_metadata sütununu alıyoruz ve boş bir hücre varsa hata vermesin diye orayı boşlukla dolduruyoruz (fillna).
        #* cv.fit_transform(...): Tüm filmlerin açıklamalarını alıyor ve devasa bir sayı tablosuna çeviriyor.
        count_matrix = cv.fit_transform(self.df['llm_metadata'].fillna(''))
        
        #* cosine_similarity(count_matrix): Her filmin sayı dizisini diğerleriyle karşılaştırır.
        self.similarity_matrix = cosine_similarity(count_matrix)
        print(" Gelişmiş Benzerlik Matrisi oluşturuldu!")

# ---------------------------------
# Cevap Verme (get_recommendations)
# ---------------------------------
    def get_recommendations(self, movie_title: str):
        try:
            # 1. Arama terimini temizle
            search_term = movie_title.lower().strip()
            # 2. 'original_title' içinde arama yap (En güvenli sütun burası)
            #* str.contains: "içinde geçiyor mu?" diye soruyoruz.
            #* na=False: Eğer veritabanında ismi olmayan (boş) bir film varsa, hata verme, onu "bulunamadı" say.
            mask = self.df['original_title'].str.lower().str.contains(search_term, na=False)
            
            # --- GÜVENLİK KİLİDİ ---
            # Eğer maske tamamen False ise (hiçbir şey bulunamadıysa):
            if not mask.any():
                return [f"Üzgünüm, veritabanımızda '{movie_title}' diye bir film bulamadım. Başka bir tane dener misin?"]
            # -----------------------

            idx = self.df[mask].index[0] # idx: Bulunan filmin satır numarası
            
            # 3. Benzerlik puanlarını al ve sırala
            sim_scores = list(enumerate(self.similarity_matrix[idx])) # enumerate kullanıyoruz ki hangi puanın hangi filme ait olduğunu unutmayalım

            #* sorted: Puanı en yüksek olanı en başa al (reverse=True).
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            
            # 4. En iyi 5 filmi seç (İlk film kendisi olduğu için [1:6] alıyoruz)
            sim_scores = sim_scores[1:6]

            # Dönüşüm (Hayır kafkanınki değil)
            movie_indices = [i[0] for i in sim_scores]
            # Sonuçları 'original_title' olarak döndür
            return self.df['original_title'].iloc[movie_indices].tolist()
            
        except Exception as e:
            return [f"Bir hata oluştu: {str(e)}"]

# ---------------------------------
# TEST BLOĞU
# ---------------------------------
if __name__ == "__main__":
    current_dir = os.path.dirname(__file__)
    
    # YENİ DOSYA İSMİ BURADA:
    yol = os.path.abspath(os.path.join(current_dir, '..', 'data', 'movies_with_metadata.csv'))
    
    adal_motoru = MovieRecommender(yol)
    adal_motoru.load_data()
    
    # Sadece veri yüklendiyse devam et
    if adal_motoru.df is not None:
        adal_motoru.create_similarity_matrix()
        
        # Test edelim: (inputla test, ama 2000e kadar idi veriler test aşamasında.)
        test_film = input("Film ismi: ")
        print(f"\n '{test_film}' için Adal'ın Önerileri:")
        oneriler = adal_motoru.get_recommendations(test_film)
        
        for i, film in enumerate(oneriler, 1):
            print(f"{i}. {film}")