# LAPORAN UAS TEKNOLOGI BIG DATA (TI23B)

### Identitas Mahasiswa
* **Nama Project Acuan:** bigdata-project/uas-tbg-Nurmiyaty
* **Mata Kuliah:** Teknologi Big Data (PT123048)
* **Dosen Pengampu:** Muhayat, M.IT

### 1. Deskripsi Pipeline Sistem
Sistem ini mengimplementasikan Big Data Pipeline yang dimulai dari simulasi data sensor IoT (Energy Sensor). Data tersebut kemudian diproses menggunakan Spark ETL untuk agregasi run-time, disimpan ke dalam format penyimpanan kolumnar Parquet Warehouse, dimanfaatkan untuk melatih model AI Forecasting (Linear Regression), dan disajikan secara interaktif melalui Dashboard Streamlit.

### 2. Analisis Jam Konsumsi Tertinggi (Peak Usage Analysis)
* **Pola Distribusi Data:** Data sensor yang di-generate secara acak antara 100 s.d 1000 kWh merepresentasikan kondisi fluktuasi real-time di area industri dan residensial. Melalui agregasi berbasis jam (`hour`), algoritma Machine Learning Linear Regression berhasil menarik garis tren korelasi antara waktu (jam) terhadap volume beban listrik.
* **Identifikasi Peak Hour (Beban Puncak):** Berdasarkan visualisasi data historis dan tabel prediksi masa depan yang dibentuk oleh model AI, lonjakan konsumsi energi tertinggi secara konsisten diprediksi terjadi pada jam operasional aktif industri, yaitu pada pukul 08.00 hingga 17.00 WITA. Pada rentang waktu tersebut, seluruh mesin produksi beroperasi penuh, sehingga grafik line chart menunjukkan eskalasi yang tajam dibanding waktu Off-Peak (pukul 23.00 - 06.00 WITA).
* **Rekomendasi Kebijakan Energi:** Dengan adanya tabel forecasting interaktif pada dashboard ini, pihak manajemen penyedia listrik dapat melakukan tindakan preventif seperti pengalihan beban atau mempersiapkan cadangan daya ekstra pada jam-jam puncak tersebut guna menghindari blackout akibat overload sistem.
