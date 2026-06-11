import streamlit as st
import pandas as pd
import plotly.express as px
import pickle
import os

# Konfigurasi halaman utama
st.set_page_config(page_title="Smart Energy Analytics", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# CONFIG & PATH SETTING (Absolute Path)
# ==========================================
BASE_PATH = "/home/nurmiyaty/uas-bigdata/output"
model_path = f"{BASE_PATH}/model_ai/linear_model.pkl"

# ==========================================
# CUSTOM ESTETIC CSS (Tema Coksu & Cokelat Tua)
# ==========================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    /* Mengatur font utama aplikasi */
    html, body, [class*="css"], .stMarkdown {
        font-family: 'Poppins', sans-serif !important;
    }
    
    /* Mengatur styling card KPI */
    .kpi-card {
        background-color: #F5EBE6; /* Coksu Kalem */
        border-left: 5px solid #6F4E37; /* Cokelat Tua */
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .kpi-title {
        color: #8B7355;
        font-size: 14px;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }
    .kpi-value {
        color: #4A3525;
        font-size: 28px;
        font-weight: 700;
        margin-top: 5px;
    }
    
    /* Mengubah warna Sidebar */
    [data-testid="stSidebar"] {
        background-color: #EEDC8240; /* Soft Warm Accent */
        border-right: 1px solid #E6D7CB;
    }
    </style>
""", unsafe_allow_html=True)

# Title Dashboard
st.markdown("<h1 style='color: #4A3525; font-weight: 700; margin-bottom: 0px;'>⚡ Smart Energy Consumption Analytics Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #8B7355; font-size: 16px; margin-top: 0px;'>Sistem Monitoring dan Prediksi Lonjakan Konsumsi Listrik Industri berbasis IoT</p>", unsafe_allow_html=True)
st.markdown("<hr style='border-top: 2px solid #E6D7CB;'/>", unsafe_allow_html=True)

# Memuat Data dari Parquet menggunakan Pandas
@st.cache_data
def load_parquet_data():
    df_total = pd.read_parquet(f"{BASE_PATH}/energy_total")
    df_time = pd.read_parquet(f"{BASE_PATH}/energy_time")
    df_ml = pd.read_parquet(f"{BASE_PATH}/ml_energy")
    return df_total, df_time, df_ml

try:
    df_total, df_time, df_ml = load_parquet_data()
    
    # ==========================================
    # SIDEBAR FILTER
    # ==========================================
    st.sidebar.markdown("<h2 style='color: #4A3525; font-size: 20px; font-weight: 700;'>🤎 Filter Navigasi</h2>", unsafe_allow_html=True)
    sector_list = df_time['sector'].unique()
    selected_sector = st.sidebar.selectbox("Pilih Sektor Kawasan:", sector_list)

    # Filter data berdasarkan sektor terpilih
    df_time_filtered = df_time[df_time['sector'] == selected_sector].sort_values(by="window_start")
    total_power_sector = df_total[df_total['sector'] == selected_sector]['total_power'].values[0]
    grand_total_power = df_total['total_power'].sum()

    # ==========================================
    # KPI METRICS CUSTOM CARD
    # ==========================================
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
            <div class='kpi-card'>
                <div class='kpi-title'>🏢 Sektor Terpilih</div>
                <div class='kpi-value'>{selected_sector}</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class='kpi-card'>
                <div class='kpi-title'>🔌 Total Konsumsi Sektor</div>
                <div class='kpi-value'>{total_power_sector:,.2f} kWh</div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
            <div class='kpi-card'>
                <div class='kpi-title'>🌍 Total Konsumsi Seluruh Kawasan</div>
                <div class='kpi-value'>{grand_total_power:,.2f} kWh</div>
            </div>
        """, unsafe_allow_html=True)

    # ==========================================
    # VISUALISASI UTAMA (Dua Kolom)
    # ==========================================
    col_graph1, col_graph2 = st.columns([2, 1])

    with col_graph1:
        st.markdown(f"<h3 style='color: #4A3525; font-size: 18px; font-weight: 600;'>📈 Tren Konsumsi Energi Setiap 10 Menit ({selected_sector})</h3>", unsafe_allow_html=True)
        fig_line = px.line(
            df_time_filtered, 
            x='window_start', 
            y='total_power_10m', 
            labels={'window_start': 'Waktu / Timestamp', 'total_power_10m': 'Konsumsi Daya (kWh)'},
            markers=True
        )
        # Set warna garis menjadi Cokelat Tua Estetik
        fig_line.update_traces(line_color='#6F4E37', marker=dict(color='#A37A5C', size=6))
        fig_line.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=True, gridcolor='#F0E6DF'),
            yaxis=dict(showgrid=True, gridcolor='#F0E6DF')
        )
        st.plotly_chart(fig_line, use_container_width=True)

    with col_graph2:
        st.markdown("<h3 style='color: #4A3525; font-size: 18px; font-weight: 600;'>📊 Distribusi Energi Sektor</h3>", unsafe_allow_html=True)
        # Grafik Lingkaran (Pie Chart) kontribusi energi
        fig_pie = px.pie(
            df_total, 
            values='total_power', 
            names='sector',
            color_discrete_sequence=['#4A3525', '#8B7355', '#D2B48C'] # Palet gradasi cokelat tua ke coksu
        )
        fig_pie.update_layout(margin=dict(t=20, b=20, l=10, r=10))
        st.plotly_chart(fig_pie, use_container_width=True)

    # ==========================================
    # AI PREDICTION & STRUCTURED TABLE DATA
    # ==========================================
    st.markdown("<hr style='border-top: 2px solid #E6D7CB;'/>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #4A3525; font-weight: 700;'>🔮 AI Forecasting Dashboard (Linear Regression)</h3>", unsafe_allow_html=True)
    
    if os.path.exists(model_path):
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        
        # Interactive Slider Tool
        input_hour = st.slider("Pilih Jam Operasional (Hour) untuk Simulasi Interaktif:", 0, 23, 12)
        pred_value = model.predict([[input_hour]])[0]
        st.info(f"💡 Estimasi Prediksi Konsumsi Listrik pada pukul **{input_hour}:00** adalah sebesar **{pred_value:,.2f} kWh**")
        
        # MEMBUAT DATA TABEL TERSTRUKTUR RAPI (Simulasi 24 Jam)
        st.markdown("<br><h4 style='color: #6F4E37; font-size: 16px; font-weight: 600;'>📋 Tabel Terstruktur Hasil Prediksi Masa Depan (00:00 - 23:00)</h4>", unsafe_allow_html=True)
        
        # Generate list jam dari 0 s.d 23
        hours_list = list(range(24))
        predictions = model.predict([[h] for h in hours_list])
        
        # Buat Dataframe hasil ramalan AI
        df_forecast = pd.DataFrame({
            "Jam / Periode": [f"Pukul {h:02d}:00" for h in hours_list],
            "Status Beban Waktu": ["Beban Rendah (Off-Peak)" if h < 7 or h > 22 else "Beban Puncak Industri (Peak Hour)" if 8 <= h <= 17 else "Beban Peralihan" for h in hours_list],
            "Prediksi Kebutuhan Energi (kWh)": [round(p, 2) for p in predictions]
        })
        
        # Berikan style styling dataframe agar rapi dan serasi tema cokelat
        st.dataframe(
            df_forecast.style.format({"Prediksi Kebutuhan Energi (kWh)": "{:,.2f} kWh"})
            .background_gradient(cmap='YlOrBr', subset=["Prediksi Kebutuhan Energi (kWh)"]),
            use_container_width=True
        )
        
    else:
        st.warning("Model AI tidak ditemukan. Silakan jalankan `main_engine.py` terlebih dahulu.")

except Exception as e:
    st.error(f"Gagal memuat data Parquet atau Model AI. Pastikan main_engine.py sudah sukses dieksekusi! Error: {e}")