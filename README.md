# CineMatch 🎬

CineMatch, kullanıcıların film zevklerini analiz ederek onlara en uygun önerileri sunan yapay zeka destekli bir platformdur. Sadece popüler olanı değil, gerçekten sevebileceğiniz yapımları keşfetmenizi sağlar.

## 🏗️ Proje Yapısı

Projeyi iki ana parça üzerinden kurguladık:

- **Backend (Python / FastAPI):** İşin mutfak kısmı burada. Film verilerinin işlenmesi, kullanıcı analizleri ve öneri algoritmasının tüm matematiksel hesaplamaları Python ile FastAPI üzerinde koşturuluyor.
- **Frontend (Next.js / React):** Kullanıcının gördüğü vitrin kısmı. Modern ve hızlı bir arayüz için Next.js kullandık. Chatbot etkileşimi ve film keşif süreci burada gerçekleşiyor.

## 🧠 Nasıl Çalışıyor? (Algoritmalar)

Arka planda tek bir kriter yerine hibrit bir modelle çalışıyoruz. Öneriler şu üçlüye dayanıyor:

1. **Metin Benzerliği (Cosine Similarity):** Filmlerin özetleri, türleri ve anahtar kelimelerini "vektör" dediğimiz sayılara döküyoruz. Beğendiğiniz bir filme matematiksel olarak en yakın olan diğer filmleri bu şekilde buluyoruz.
2. **Tür Ağırlıklandırma:** Eğer korku filmi sevmiyorsanız, popüler olsa bile önünüze korku filmi düşürmüyoruz. Seçtiğiniz türlere ekstra puan vererek listeyi kişiselleştiriyoruz.
3. **Popülerlik Dengesi:** Sadece niş filmler değil, dünyanın sevdiği popüler yapımları da sisteme dahil ederek (Scikit-learn kullanarak normalize ediyoruz) daha dengeli bir liste sunuyoruz.

## 👥 Ekip & Görevler

- **Owner/Backend A (Adal):** Öneri motoru ve sistem mimarisi.
- **Data (Dilara):** Kaggle veri temizleme.
- **Frontend (Sude):** Next.js UI geliştirme.
- **AI (Batuhan):** LLM entegrasyonu.
- **Backend B (Enes):** Kullanıcı profilleri ve DB.

## 🕒 Deadline

30.01.2026 - 13:05

## 🚀 Kurulum

Projeyi kendi bilgisayarınızda çalıştırmak için:

### Backend
1. `backend` klasörüne gidin.
2. Bir sanal ortam oluşturun: `python -m venv venv`
3. Sanal ortamı aktif edin: `.\venv\Scripts\activate` (Windows) veya `source venv/bin/activate` (Mac/Linux)
4. Gerekli paketleri kurun: `pip install -r requirements.txt`

### Frontend
1. `frontend` klasörüne gidin.
2. Bağımlılıkları yükleyin: `npm install`

## 🛠️ Kullanım

1. **Backend:** `main.py` dosyasını çalıştırarak API'yi ayağa kaldırın.
2. **Frontend:** `npm run dev` komutuyla arayüzü başlatın.
3. Tarayıcınızda `localhost:3000` (veya terminalde çıkan adres) üzerinden CineMatch dünyasına giriş yapın.

