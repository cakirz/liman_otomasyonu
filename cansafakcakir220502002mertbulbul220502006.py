#Bu liman otomasyonu Can Şafak Çakır ve Mert Bülbül tarfından hazırlanmıştır.
import csv
import time

class Tır:
    def __init__(self, plaka, ülke, tonaj, yük_miktarı, maliyet, geliş_zamanı):
        self.plaka = plaka
        self.ülke = ülke
        self.tonaj = tonaj
        self.yük_miktarı = yük_miktarı
        self.maliyet = maliyet
        self.geliş_zamanı = geliş_zamanı

class Gemi:
    def __init__(self, geliş_zamanı, gemi_adı, kapasite, gidecek_ülke):
        self.geliş_zamanı = geliş_zamanı
        self.gemi_adı = gemi_adı
        self.kapasite = kapasite
        self.gidecek_ülke = gidecek_ülke
        self.yük_miktarı = 0

class YüklemeAlanı:
    def __init__(self, alan_numarası, kapasite=750):
        self.alan_numarası = alan_numarası
        self.kapasite = kapasite
        self.mevcut_yük = 0


def olaylar_dosyasını_oku(dosya_yolu="olaylar.csv"):
    tırlar = []
    with open(dosya_yolu, newline='', encoding='utf-8') as csvfile:
        okuyucu = csv.DictReader(csvfile)
        for satır in okuyucu:
            plaka = satır['tır_plakası']
            ülke = satır['ülke']
            tonaj = int(satır['20_ton_adet']) * 20 + int(satır['30_ton_adet']) * 30
            yük_miktarı = int(satır['yük_miktarı'])
            maliyet = float(satır['maliyet'])
            geliş_zamanı = float(satır['geliş_zamanı'])
            tırlar.append(Tır(plaka, ülke, tonaj, yük_miktarı, maliyet, geliş_zamanı))
    return tırlar

def gemiler_dosyasını_oku(dosya_yolu="gemiler.csv"):
    gemiler = []
    with open(dosya_yolu, newline='', encoding='utf-8') as csvfile:
        okuyucu = csv.DictReader(csvfile)
        for satır in okuyucu:
            geliş_zamanı = float(satır['geliş_zamanı'])
            gemi_adı = satır['gemi_adı']
            kapasite = int(satır['kapasite'])
            gidecek_ülke = satır['gidecek_ülke']
            gemiler.append(Gemi(geliş_zamanı, gemi_adı, kapasite, gidecek_ülke))
    return gemiler

def tırları_indir(tırlar, yükleme_alanları):
    sonuç_mesajları = []

    tırlar.sort(key=lambda x: x.plaka)

    for tır in tırlar:# İndirme işlemi gerçekleştir
        sonuç = yükleri_indir(tır, yükleme_alanları)
        sonuç_mesajları.append(sonuç)

    return sonuç_mesajları


def yükleri_indir(tır, yükleme_alanları):# Yükü limana indirir
    for alan in yükleme_alanları:
        if alan.mevcut_yük + tır.tonaj <= alan.kapasite:
            alan.mevcut_yük += tır.tonaj
            return f"{tır.plaka} - Ülke: {tır.ülke} - Yük {tır.tonaj} ton indirildi - Maliyet: {tır.maliyet} TL"
    return f"{tır.plaka} - Ülke: {tır.ülke} - Yük indirme başarısız, liman dolu"


def gemiye_yükle(gemi, tır, yükleme_alanları, sistem_durumu, vinç_kapasitesi, zaman_limiti):
    kalan_kapasite = gemi.kapasite - gemi.yük_miktarı # Gemi kapasitesi kontrolü
    if kalan_kapasite < vinç_kapasitesi:
        return f"{gemi.gemi_adı} - Yük yükleme başarısız, gemi kapasitesi yetersiz"

    if tır.tonaj < vinç_kapasitesi:# TIR'ın kapasitesi kontrolü
        return f"{gemi.gemi_adı} - Yük yükleme başarısız, TIR kapasitesi yetersiz"

    başlangıç_zamanı = time.time()
    geçen_zaman = 0

    # Limanda yük olup olmadığını, uygun tırın gelip gelmediğini ve 30 tonluk tırları kontrol et
    while geçen_zaman < zaman_limiti:
        for alan in yükleme_alanları:
            if alan.mevcut_yük >= vinç_kapasitesi:

                uygun_tırlar = [t for t in sistem_durumu['tırlar'] if t.tonaj == 30 ]
                if uygun_tırlar:
                    seçilen_tır = uygun_tırlar.pop(0)
                elif uygun_tırlar :
                    seçilen_tır = uygun_tırlar.pop(0)
                else:
                    seçilen_tır = tır

                alan.mevcut_yük -= seçilen_tır.tonaj
                gemi.yük_miktarı += seçilen_tır.tonaj
                sistem_durumu['yüklenen_gemiler'][gemi.gemi_adı] = {'tır': seçilen_tır}

                return f"{gemi.gemi_adı} - Yük {vinç_kapasitesi} ton gemiye yüklendi (Tır: {seçilen_tır.plaka})"
        geçen_zaman = time.time() - başlangıç_zamanı


        for tır in sistem_durumu['tırlar']: # Zamanla devam ediyor
            sonuç = yükleri_indir(tır, yükleme_alanları)
            print(sonuç)


        time.sleep(1) # Zamanı beklemek için

    # Limanda yük kalmadı veya zaman limiti aşıldı hata mesajı
    return f"{gemi.gemi_adı} - Yük yükleme başarısız, liman boş veya zaman limiti aşıldı"


def menüyü_göster():
    print("1. Tırları İndir")
    print("2. Gemilere Yükle")
    print("3. Çıkış")

def ana_program():
    yükleme_alanları = [YüklemeAlanı(1), YüklemeAlanı(2)] # Limanda 2 istif alanı mevcut
    vinç_kapasitesi = 20  # Vinç kapasitesi (20 ton)
    zaman_limiti = float('inf')  # Zaman limiti

    # Tırlar ve gemileri dosyadan oku
    tırlar = olaylar_dosyasını_oku()
    gemiler = gemiler_dosyasını_oku()

    sistem_durumu = {'tırlar': tırlar, 'gemiler': gemiler, 'yüklenen_gemiler': {}}# İlgili sistem durumu değişkenleri


    while True: # Simülasyon başlangıcı
        print("Liman Durumu:") # Limanın durumu gösteriliyor
        for alan in yükleme_alanları:
            print(f"Istif Alanı {alan.alan_numarası}: {alan.mevcut_yük}/{alan.kapasite} ton")

        menüyü_göster()
        seçim = input("Seçiminizi yapın (1-3): ")

        if seçim == '1':
            sonuç = tırları_indir(sistem_durumu['tırlar'], yükleme_alanları)
            for r in sonuç:
                print(r)
        elif seçim == '2':
            for gemi in sistem_durumu['gemiler']:
                if gemi.gemi_adı not in sistem_durumu['yüklenen_gemiler']:
                    tır = sistem_durumu['tırlar'].pop(0)
                    sonuç = gemiye_yükle(gemi, tır, yükleme_alanları, sistem_durumu, vinç_kapasitesi, zaman_limiti)

                    print(sonuç)
                    if sonuç.endswith("yüklendi"):
                        sistem_durumu['yüklenen_gemiler'][gemi.gemi_adı] = True
        elif seçim == '3':
            print("Çıkış yapılıyor...")
            break
        else:
            print("Geçersiz seçim. Lütfen tekrar deneyin.")

if __name__ == "__main__":
    ana_program()
