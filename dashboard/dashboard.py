import pandas as pd
import seaborn as sns
import streamlit as st
import matplotlib.pyplot as plt
from babel.numbers import format_currency

# Set style for seaborn
sns.set(style='dark')

# Set streamlit option
st.set_option('deprecation.showPyplotGlobalUse', False)

# Load the dataset
try:
    all_df = pd.read_csv("bike_merge.csv")
except FileNotFoundError:
    st.error("File 'bike_merge.csv' tidak ditemukan. Pastikan file tersebut ada di direktori yang benar.")

# Ensure the date columns are correctly formatted
datetime_columns = ["dteday"]
if "dteday" in all_df.columns:
    all_df.sort_values(by="dteday", inplace=True)
    all_df.reset_index(drop=True, inplace=True)
    
    for column in datetime_columns:
        all_df[column] = pd.to_datetime(all_df[column])
else:
    st.error("Kolom 'dteday' tidak ditemukan dalam dataset.")

# Display introduction text in Streamlit
st.write(
    """
    # Hasil Analisis Dataset Bike Sharing :bike:
    Analisis ini akan menguraikan beberapa pertanyaan penting yang mungkin relevan bagi pemilik bisnis, di antaranya:
    1. Musim apa yang memiliki jumlah penyewaan sepeda tertinggi?
    2. Seberapa sering pelanggan menyewa sepeda dalam beberapa bulan terakhir?
    3. Bagaimana pola penyewaan sepeda berdasarkan jam? Pada jam berapa terjadi peningkatan penyewaan?
    """
)

# Validate date range in data
if "dteday" in all_df.columns:
    min_date = all_df["dteday"].min()
    max_date = all_df["dteday"].max()
else:
    min_date = None
    max_date = None

# Sidebar for date range selection
if min_date and max_date:
    with st.sidebar:
        start_date, end_date = st.date_input(
            label='Pilih Rentang Waktu Data: ',
            min_value=min_date,
            max_value=max_date,
            value=[min_date, max_date]
        )
else:
    st.error("Tidak dapat menampilkan rentang tanggal karena kolom 'dteday' tidak ada.")

# Function to create daily orders dataframe
def create_daily_orders_df(df):
    if "dteday" in df.columns:
        daily_orders_df = df.resample('D', on='dteday').agg({"cnt_daily": "sum"}).reset_index().rename(columns={"cnt_daily": "order_count"})
        return daily_orders_df
    else:
        st.error("Kolom 'dteday' tidak ditemukan dalam dataset.")
        return pd.DataFrame()

# Function to create dataframe by season
def create_byseason_df(df):
    if "season_daily" in df.columns and "cnt_daily" in df.columns:
        byseason_df = df.groupby("season_daily").cnt_daily.nunique().reset_index()
        byseason_df.rename(columns={"cnt_daily": "customer_count", "season_daily": "season"}, inplace=True)
        return byseason_df
    else:
        st.error("Kolom 'season_daily' atau 'cnt_daily' tidak ditemukan dalam dataset.")
        return pd.DataFrame()

# Function to create Recency and Frequency dataframe
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

# Filter data based on selected dates
if min_date and max_date:
    main_df = all_df[(all_df["dteday"] >= pd.to_datetime(start_date)) & (all_df["dteday"] <= pd.to_datetime(end_date))]
    byseason_df = create_byseason_df(main_df)
    daily_orders_df = create_daily_orders_df(main_df)
else:
    main_df = pd.DataFrame()

# Display visualization by season
st.title("Demografi Pelanggan")
st.subheader("Jumlah Pelanggan Berdasarkan Musim :fallen_leaf:")

if not byseason_df.empty:
    fig, ax = plt.subplots(figsize=(20, 10))
    colors1 = ["#D3D3D3", "#D3D3D3", "#FFC0CB", "#D3D3D3", "#D3D3D3"]
    
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

# Display season information
st.markdown("## Masing-masing angka pada plot mewakili musim:")
st.markdown("1 -> Cerah, Sedikit berawan, Sebagian berawan")
st.markdown("2 -> Berkabut + Berawan, Berkabut + Awan terpecah, Berkabut + Sedikit berawan")
st.markdown("3 -> Salju ringan, Hujan ringan + Petir + Awan tersebar")
st.markdown("4 -> Hujan deras + Es batu + Petir + Kabut, Salju + Kabut")

# Interpretation function for first question
def main1():
    st.title("Interpretasi untuk Pertanyaan Ke-1")

    if st.button("Tampilkan Keterangan 1"):
        st.success("Jumlah pelanggan terbanyak tercatat saat musim salju ringan dan hujan ringan dengan petir serta awan tersebar. Ini menunjukkan bahwa pelanggan cenderung menyewa sepeda ketika cuaca tidak terlalu panas, membuatnya nyaman untuk bersepeda.")

if __name__ == "__main__":
    main1()

# Create the RF DataFrame
rf_df = create_rf_df(all_df)

# Display RF DataFrame
st.title("Analisis RF :mag:")
st.subheader("Recency dan Frequency pada Setiap Bulan:")
if not rf_df.empty:
    st.write(rf_df)
    
    # Display metrics for average Recency and Frequency
    avg_recency = round(rf_df.recency.mean(), 1)
    avg_frequency = round(rf_df.frequency.mean(), 2)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Rata-rata Recency (hari)", value=avg_recency)

    with col2:
        st.metric("Rata-rata Frequency", value=avg_frequency)

    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(25, 15))

    # Plot for Recency
    recency_df = rf_df.sort_values(by="recency", ascending=True).head(12)
    colors_recency = ["#90CAF9"] * len(recency_df)
    sns.barplot(y="recency", x="month", data=recency_df, palette=colors_recency, ax=ax[0])
    ax[0].set_ylabel(None)
    ax[0].set_xlabel("Bulan ke-", fontsize=30)
    ax[0].set_title("Berdasarkan Recency", fontsize=50)
    ax[0].tick_params(axis='y', labelsize=30)
    ax[0].tick_params(axis='x', labelsize=35)

    # Plot for Frequency
    frequency_df = rf_df.sort_values(by="frequency", ascending=False).head(12)
    colors_frequency = ["#90CAF9"] * len(frequency_df)
    sns.barplot(y="frequency", x="month", data=frequency_df, palette=colors_frequency, ax=ax[1])
    ax[1].set_ylabel(None)
    ax[1].set_xlabel("Bulan ke-", fontsize=30)
    ax[1].set_title("Berdasarkan Frequency", fontsize=50)
    ax[1].tick_params(axis='y', labelsize=30)
    ax[1].tick_params(axis='x', labelsize=35)

    st.pyplot(fig)
else:
    st.warning("Tidak ada data untuk menampilkan analisis RF.")

# Interpretation function for second question
def main2():
    st.title("Interpretasi untuk Pertanyaan Ke-2")

    if st.button("Tampilkan Keterangan 2"):
        st.success("Pada beberapa bulan terakhir, pelanggan sering melakukan penyewaan sepeda, ditunjukkan oleh nilai recency yang rendah dan frekuensi yang tinggi.")

if __name__ == "__main__":
    main2()

# Ensure the datetime column is properly set as index
if "dteday" in all_df.columns:
    all_df['dteday'] = pd.to_datetime(all_df['dteday'])
    all_df.set_index('dteday', inplace=True)

# Display title
st.title("Pola Waktu Penyewaan Sepeda")

# Hour range selection slider
selected_hour_range = st.slider("Pilih Rentang Jam", min_value=0, max_value=23, value=(0, 23))

# Filter data by hour range
if "hr" in all_df.columns and "cnt_hourly" in all_df.columns:
    selected_data = all_df[(all_df['hr'] >= selected_hour_range[0]) & (all_df['hr'] <= selected_hour_range[1])]

    # Plot hourly pattern
    plt.figure(figsize=(12, 6))
    sns.lineplot(x=selected_data['hr'], y=selected_data['cnt_hourly'], ci=None, color='blue')
    plt.title("Pola Jumlah Penyewa Sepeda Harian Berdasarkan Waktu")
    plt.xlabel("Jam")
    plt.ylabel("Jumlah Penyewa Sepeda Harian")
    plt.xticks(rotation=45, ha='right')
    st.pyplot(plt.gcf())
else:
    st.warning("Kolom 'hr' atau 'cnt_hourly' tidak ditemukan dalam dataset.")

# Interpretation function for third question
def main3():
    st.title("Interpretasi Grafik untuk Pertanyaan Ke-3")

    if st.button("Tampilkan Keterangan 3"):
        st.success("Penyewaan sepeda rata-rata meningkat pada jam 16.00-17.00, menunjukkan bahwa pelanggan lebih sering menyewa sepeda di sore hari.")

if __name__ == "__main__":
    main3()
