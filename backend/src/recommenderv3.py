
#! Adal'ın algoritması - Versiyon 3.0 (Genre, Popularity, Year gibi detaylar da ekli.)

# ---------------------------------
# Hazırlık (Kütüphaneler)
# ---------------------------------
import pandas as pd # Python'un Excel'i olarak Pandas Kütüphanesi. Veriyi tablo halinde tutmamızı, okumamızı ve filtrelememizi sağlar.
#* Neden: .csv dosyasını okuyup hafızada tutmak için.
import os # İşletim sistemiyle konuşur. "Şu dosya orada mı?" kontrolünü yapar. OS Neydi? OS emekti. OS yani Operating System.
#* Neden: Dosya yolu (path) hatalarını önlemek için.
import numpy as np  # Matematiksel ağırlıklandırma için şart.
import re # Metin temizliği için
from sklearn.feature_extraction.text import CountVectorizer # Kelime sayıcı. Metinleri bilgisayarın anlayacağı sayılara (vektörlere) çevirir.
#* Neden: Bilgisayar kelimelerden anlamaz, "1" ve "0"dan anlar. Çevirici lazım.
from sklearn.metrics.pairwise import cosine_similarity # İki sayı dizisi arasındaki benzerliği ölçer.
#* Neden: Hangi filmin diğerine ne kadar benzediğini matematiksel olarak hesaplamak için.
from sklearn.preprocessing import MinMaxScaler # Her sütundaki en küçük sayıya 0, en büyük sayıya 1 der. Aradakileri de orantılar. Her şeyi 0 ile 1 arasına hapseder.

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
        self.normalized_df = None # Sayısal verilerin tutulacağı yer
        #* Neden inite ekliyoruz peki?
        #* Çünkü canısı motor başlar başlamaz ağır işlemleri yapıp bilgisayarı kilitlemeyelim. Veriyi sonra yükleyeceğiz (Lazy Loading).

# ---------------------------------
# Veriyi İçeri Almak (load_data)
# ---------------------------------
    def load_data(self):
            """
            Veriyi yükler ve sayısal sütunları (Yıl, Puan, Popülerlik)
            matematiksel işlem için 0-1 arasına sıkıştırır (Normalization).
            """
            if os.path.exists(self.data_path): # Burdaki amaç: Kör uçuş yapmamak. Dosya orada yoksa programın çökmesini engeller.
            
            # 1. Adım: Dosyayı oku
                self.df = pd.read_csv(self.data_path) # CSV dosyasındaki virgülle ayrılmış yazıları alır, satır ve sütunlardan oluşan bir tabloya (DataFrame) çevirir.
                print(f" Dosya yüklendi! Toplam Film: {len(self.df)}")

            # 2. Adım: Veri Temizliği 

            # Tarihten sadece YILI çekiyoruz. Hatalı tarih varsa 0 yapıyoruz.
                self.df['year'] = pd.to_datetime(self.df['release_date'], errors='coerce').dt.year.fillna(0)

            # Puan ve Popülerlikteki boş yerlere 0 yazalım ki hesap yaparken hata vermesin.
                self.df['popularity'] = self.df['popularity'].fillna(0)
                self.df['vote_average'] = self.df['vote_average'].fillna(0)

            # 3. Normalization (0-1 Sıkıştırma İşlemi)
                scaler = MinMaxScaler()

            # Hangi sütunları sıkıştıracağız?
                cols_to_scale = ['popularity', 'vote_average', 'year']

            # İşlemi yap ve 'normalized_df' içine kaydet
                scaled_data = scaler.fit_transform(self.df[cols_to_scale])
                self.normalized_df = pd.DataFrame(scaled_data, columns=cols_to_scale)
            
                print(" Sayısal veriler (Popülerlik, Puan, Yıl) 0-1 arasına normalize edildi.")

            else:
                print(" Dosya bulunamadı! Yolu kontrol et.")

# ---------------------------------
# Beyin (Matris Oluşturma)
# ---------------------------------
    def create_similarity_matrix(self): # Burası projenin beyni 
        """
        Hem kelimelere (Text) hem de sayılara (Metadata) bakarak
        Hibrit bir benzerlik matrisi oluşturur.
        """
        # 1. Adım: Metin Hazırlığı
        def clear_text(text):
            return re.sub(r'\b\d{4}\b', '', str(text))

        # Metadata içindeki yılları siliyoruz. Çünkü yılı zaten ayrıca hesaplayacağız.
        # llm_metadata sütununu temizle
        clean_metadata = self.df['llm_metadata'].fillna('').apply(clear_text)

        # 2. Adım: Metin Benzerliği
        cv = CountVectorizer()
        text_matrix = cv.fit_transform(clean_metadata)
        
        # Sadece kelimelere göre benzerlik (0 ile 1 arası)
        text_sim = cosine_similarity(text_matrix)
        print(" Metin tabanlı benzerlik hesaplandı.")

        # 3. Adım: Sayısal Benzerlik

        num_sim = cosine_similarity(self.normalized_df) # Popülerlik, Puan ve Yıl açısından ne kadar benziyorlar?
        print(" Sayısal veriye dayalı benzerlik hesaplandı.")

        # 4. Adım HİBRİT KARIŞIM
        # %70 Metin (Konu) + %30 Sayısal (Puan/Yıl)
        self.similarity_matrix = (text_sim * 0.85) + (num_sim * 0.15)
        
        print(f" HİBRİT Benzerlik Matrisi oluşturuldu! (Boyut: {self.similarity_matrix.shape})")

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

            # Filmin satır numarasını (indeksini) al
            idx = self.df[mask].index[0] # idx: Bulunan filmin satır numarası
            
            # 3. Benzerlik puanlarını al ve sırala
            sim_scores = list(enumerate(self.similarity_matrix[idx])) # enumerate kullanıyoruz ki hangi puanın hangi filme ait olduğunu unutmayalım

            #* sorted: Puanı en yüksek olanı en başa al (reverse=True).
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            
            # 4. En iyi 5 filmi seç (İlk film kendisi olduğu için [1:6] alıyoruz)
            # x[0] filmin satır numarasıdır. Eğer satır numarası idx (aranan film) değilse listeye al.
            sim_scores = [x for x in sim_scores if x[0] != idx]
            sim_scores = sim_scores[:5]

            # 5. Sonuçları hazırla: Dönüşüm (Hayır kafkanınki değil)
            movie_indices = [i[0] for i in sim_scores]

            # Sonuçları liste biçiminde döndür
            movie_titles = self.df['title'].iloc[movie_indices].fillna('İsimsiz Film').tolist()
            return movie_titles
            
        except Exception as e:
            return [f"Bir hata oluştu: {str(e)}"]

# ---------------------------------
# TEST BLOĞU
# ---------------------------------
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # EĞER data klasörü backend'in içindeyse bunu kullan:
    yol = os.path.join(current_dir, '..', 'data', 'movies_with_metadata.csv')
    
    # EĞER dosya bulunamazsa bir de kök dizine bak diyelim (Garantiye alalım):
    if not os.path.exists(yol):
        yol = os.path.join(current_dir, '..', '..', 'data', 'movies_with_metadata.csv')

    print(f" Denenen dosya yolu: {yol}")

    adal_motoru = MovieRecommender(yol)
    adal_motoru.load_data()
    
    if adal_motoru.df is not None:
        adal_motoru.create_similarity_matrix()
        test_film = input("\n🎥 Hangi filmi çok sevdin?: ")
        oneriler = adal_motoru.get_recommendations(test_film)
        
        print(f"\n '{test_film}' Seven Bunları da Sevdi:")
        for i, film in enumerate(oneriler, 1):
            print(f"{i}. {film}")