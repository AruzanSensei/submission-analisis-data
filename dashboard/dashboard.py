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
    daily_orders_df = pd.DataFrame()

st.write("\n")

# Pertanyaan 1
st.title("1. Pola Waktu Penyewaan :clock7:")

# Slider pemilihan rentang jam
selected_hour_range = st.slider("Pilih Rentang Jam", min_value=0, max_value=30, value=(10, 20))

# Memfilter data berdasarkan rentang jam
if "hr" in all_df.columns and "cnt_hourly" in all_df.columns:
    selected_data = all_df[(all_df['hr'] >= selected_hour_range[0]) & (all_df['hr'] <= selected_hour_range[1])]

    # Plot pola per jam
    plt.figure(figsize=(12, 6))
    sns.lineplot(x=selected_data['hr'], y=selected_data['cnt_hourly'], ci=None, color='blue')
    plt.title("Pola Jumlah Penyewa Sepeda Harian Berdasarkan Waktu")
    plt.xlabel("Jam")
    plt.ylabel("Jumlah Penyewa Sepeda Harian")
    plt.xticks(rotation=45, ha='right')
    st.pyplot(plt.gcf())
else:
    st.warning("Kolom 'hr' atau 'cnt_hourly' tidak ditemukan dalam dataset.")

st.text_area("KESIMPULAN:", "Penyewaan sepeda rata-rata meningkat pada jam 16.00-17.00, menunjukkan bahwa pelanggan lebih sering menyewa sepeda di sore hari.")

# Pertanyaan 2
st.title("2. Analisis RF :mag:")
st.subheader("Recency dan Frequency pada Setiap Bulan:")

# Membuat DataFrame RF
rf_df = create_rf_df(all_df)

if not rf_df.empty:
    st.write(rf_df)
    
    # Menampilkan metrik rata-rata Recency dan Frequency
    avg_recency = round(rf_df.recency.mean(), 1)
    avg_frequency = round(rf_df.frequency.mean(), 2)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Rata-rata Recency (hari)", value=avg_recency)

    with col2:
        st.metric("Rata-rata Frequency", value=avg_frequency)

    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))

    # Plot untuk Recency
    recency_df = rf_df.sort_values(by="recency", ascending=True).head(12)
    colors_recency = ["#469536"] * len(recency_df)
    sns.barplot(y="recency", x="month", data=recency_df, palette=colors_recency, ax=ax[0])
    ax[0].set_ylabel(None)
    ax[0].set_xlabel("Bulan ke-", fontsize=30)
    ax[0].set_title("Berdasarkan Recency", fontsize=50)
    ax[0].tick_params(axis='y', labelsize=30)
    ax[0].tick_params(axis='x', labelsize=35)

    # Plot untuk Frequency
    frequency_df = rf_df.sort_values(by="frequency", ascending=False).head(12)
    colors_frequency = ["#469536"] * len(frequency_df)
    sns.barplot(y="frequency", x="month", data=frequency_df, palette=colors_frequency, ax=ax[1])
    ax[1].set_ylabel(None)
    ax[1].set_xlabel("Bulan ke-", fontsize=30)
    ax[1].set_title("Berdasarkan Frequency", fontsize=50)
    ax[1].tick_params(axis='y', labelsize=30)
    ax[1].tick_params(axis='x', labelsize=35)

    st.pyplot(fig)
else:
    st.warning("Tidak ada data untuk menampilkan analisis RF.")

st.text_area("KESIMPULAN:", "Pada beberapa bulan terakhir, pelanggan sering melakukan penyewaan sepeda, ditunjukkan oleh nilai recency yang rendah dan frekuensi yang tinggi.")

# Pertanyaan 3
st.title("3. Demografi Pelanggan :fallen_leaf:")
st.subheader("Jumlah Pelanggan Berdasarkan Musim")

if not byseason_df.empty:
    fig, ax = plt.subplots(figsize=(20, 10))
    colors1 = ["#D3D3D3", "#D3D3D3", "#469536", "#D3D3D3", "#D3D3D3"]
    
    sns.barplot(
        x="season", 
        y="customer_count", 
        data=byseason_df.sort_values(by="customer_count", ascending=False),
        palette=colors1, 
        ax=ax
    )

    ax.set_title("Jumlah Pelanggan Berdasarkan Musim", fontsize=30)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=25)
    ax.tick_params(axis='y', labelsize=20)
    st.pyplot(fig)
else:
    st.warning("Tidak ada data untuk menampilkan jumlah pelanggan berdasarkan musim.")

# Menampilkan informasi tentang musim
st.write("## Masing-masing angka pada plot mewakili musim:")
st.write("1 > Cerah, Sedikit berawan, Sebagian berawan")
st.write("2 > Berkabut + Berawan, Berkabut + Awan terpecah, Berkabut + Sedikit berawan")
st.write("3 > Salju ringan, Hujan ringan + Petir + Awan tersebar")
st.write("4 > Hujan deras + Es batu + Petir + Kabut, Salju + Kabut")

st.text_area("KESIMPULAN:", "Jumlah pelanggan terbanyak tercatat saat musim salju ringan dan hujan ringan dengan petir serta awan tersebar. Ini menunjukkan bahwa pelanggan cenderung menyewa sepeda ketika cuaca tidak terlalu panas, membuatnya nyaman untuk bersepeda.")
