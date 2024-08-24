import pandas as pd
import seaborn as sns
import streamlit as st
import matplotlib.pyplot as plt
from babel.numbers import format_currency

# Mengatur gaya untuk seaborn
sns.set(style='dark')

# Mengatur opsi Streamlit
st.set_option('deprecation.showPyplotGlobalUse', False)

# Memuat dataset
try:
    all_df = pd.read_csv("dashboard/main_data.csv")
except FileNotFoundError:
    st.error("File 'dashboard/main_data' tidak ditemukan. Pastikan file tersebut ada di direktori yang benar.")

# Memastikan kolom tanggal diformat dengan benar
datetime_columns = ["dteday"]
if "dteday" in all_df.columns:
    all_df["dteday"] = pd.to_datetime(all_df["dteday"])
    all_df.sort_values(by="dteday", inplace=True)
    all_df.reset_index(drop=True, inplace=True)
else:
    st.error("Kolom 'dteday' tidak ditemukan dalam dataset.")

# Menampilkan teks pengantar di Streamlit
st.write(
    """
    # Analisis Data Bike Sharing :bar_chart:
    _Analisis ini akan menguraikan beberapa pertanyaan penting yang mungkin relevan bagi pemilik bisnis, di antaranya:_
    1. Bagaimana pola jumlah penyewaan sepeda berdasarkan waktu, baik secara jam maupun bulanan? Pada jam dan bulan berapa penyewaan meningkat?
    2. Seberapa sering pelanggan menyewa sepeda dalam beberapa bulan terakhir?
    3. Pada musim apa jumlah penyewaan sepeda mencapai puncaknya?
    """
)

st.write("\n")

# Memvalidasi rentang tanggal dalam data
if "dteday" in all_df.columns:
    min_date = all_df["dteday"].min()
    max_date = all_df["dteday"].max()
else:
    min_date = None
    max_date = None

# Sidebar untuk pemilihan rentang waktu tanggal
if min_date and max_date:
    start_date, end_date = st.date_input(
        label='Pilih Rentang Waktu Data: ',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
else:
    start_date, end_date = min_date, max_date
    st.error("Tidak dapat menampilkan rentang tanggal karena kolom 'dteday' tidak ada.")

# Fungsi untuk membuat dataframe pesanan harian
def create_daily_orders_df(df):
    if "dteday" in df.columns:
        daily_orders_df = df.resample('D', on='dteday').agg({"cnt_daily": "sum"}).reset_index().rename(columns={"cnt_daily": "order_count"})
        return daily_orders_df
    else:
        st.error("Kolom 'dteday' tidak ditemukan dalam dataset.")
        return pd.DataFrame()

# Fungsi untuk membuat dataframe berdasarkan musim
def create_byseason_df(df):
    if "season_daily" in df.columns and "cnt_daily" in df.columns:
        byseason_df = df.groupby("season_daily").cnt_daily.nunique().reset_index()
        byseason_df.rename(columns={"cnt_daily": "customer_count", "season_daily": "season"}, inplace=True)
        return byseason_df
    else:
        st.error("Kolom 'season_daily' atau 'cnt_daily' tidak ditemukan dalam dataset.")
        return pd.DataFrame()

# Fungsi untuk membuat dataframe Recency dan Frequency
def create_rf_df(df):
    if "dteday" in df.columns and "mnth_daily" in df.columns:
        tanggal_sekarang = df['dteday'].max()
        rf_df = df.groupby("mnth_daily", as_index=False).agg({
            'dteday': lambda x: (tanggal_sekarang - x.max()).days,
            'cnt_daily': 'count'
        }).rename(columns={'mnth_daily': 'month', 'dteday': 'recency', 'cnt_daily': 'frequency'})
        return rf_df
    else:
        st.error("Kolom 'dteday' atau 'mnth_daily' tidak ditemukan dalam dataset.")
        return pd.DataFrame()

# Memfilter data berdasarkan tanggal yang dipilih
if min_date and max_date:
    main_df = all_df[(all_df["dteday"] >= pd.to_datetime(start_date)) & (all_df["dteday"] <= pd.to_datetime(end_date))]
    byseason_df = create_byseason_df(main_df)
    daily_orders_df = create_daily_orders_df(main_df)
else:
    main_df = pd.DataFrame()
    byseason_df = pd.DataFrame()
    daily_orders
