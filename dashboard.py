import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

st.set_option('deprecation.showPyplotGlobalUse', False)
all_df = pd.read_csv("bike_merge.csv")

datetime_columns = ["dteday"]
all_df.sort_values(by="dteday", inplace=True)
all_df.reset_index(inplace=True)
 
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

st.write(
    """
    # Hasil Analisis Dataset Bike Sharing :bike:
    Pada analisis ini, akan menginterpretasikan beberapa hal
    yang mungkin dipertanyakan oleh pemilik bisnis. Diantaranya:
    1. Pada musim apa jumlah penyewa sepeda paling banyak?
    2. Seberapa sering seorang pelanggaan melakukan sewa dalam beberapa bulan terakhir?
    3. Bagaimana pola jumlah sewa berdasarkan jam? 
       pada jam berapa sewa mengalami peningkatan?
    """
)

min_date = all_df["dteday"].min()
max_date = all_df["dteday"].max()
 
with st.sidebar:
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Data Ini Diperoleh pada Rentang Waktu: ',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='dteday').agg({
        "cnt_daily": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "cnt_daily": "order_count",
    }, inplace=True)
    
    return daily_orders_df

def create_byseason_df(df):
    byseason_df = df.groupby(by="season_daily").cnt_daily.nunique().reset_index()
    byseason_df.rename(columns={
        "cnt_daily": "customer_count",
        "season_daily": "season"
    }, inplace=True)
    
    return byseason_df

tanggal_sekarang = all_df['dteday'].max()
def create_rf_df(df):
    rf_df = df.groupby(by="mnth_daily", as_index=False).agg({
        'dteday': lambda x: (tanggal_sekarang - x.max()).days,
        'cnt_daily': 'count'
    }).reset_index()

# Mengganti nama kolom
    rf_df = pd.DataFrame({
        'month': rf_df['mnth_daily'],  
        'recency': rf_df['dteday'],
        'frequency': rf_df['cnt_daily']
    })
# Menampilkan DataFrame RF
    return rf_df

main_df = all_df[(all_df["dteday"] >= str(start_date)) & 
                (all_df["dteday"] <= str(end_date))]
byseason_df = create_byseason_df(main_df)
daily_orders_df = create_daily_orders_df(main_df)


st.title("Demografi Pelanggan")
st.subheader("Jumlah Pelanggan Berdasarkan Musim :fallen_leaf: ")

fig, ax = plt.subplots(figsize=(20, 10))

colors1 = ["#D3D3D3", "#D3D3D3", "#FFC0CB", "#D3D3D3", "#D3D3D3"]
sns.barplot(
    y="customer_count",
    x="season",
    data=byseason_df.sort_values(by="customer_count", ascending=False),
    palette=colors1,
    ax=ax
)

# Atur tata letak plot
ax.set_title("Jumlah Pelanggan Berdasarkan Musim", loc="center", fontsize=30)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='x', labelsize=25)
ax.tick_params(axis='y', labelsize=20)

# Tampilkan plot menggunakan Streamlit
st.pyplot(fig)

st.markdown("## Masing-masing angka pada plot mempresentasikan musim:")
st.markdown("1 -> Clear, Few clouds, Partly cloudy, Partly cloudy")
st.markdown("2 -> Mist + Cloudy, Mist + Broken clouds, Mist + Few clouds, Mist")
st.markdown("3 -> Light Snow, Light Rain + Thunderstorm + Scattered clouds, Light Rain + Scattered clouds")
st.markdown("4 -> Heavy Rain + Ice Pallets + Thunderstorm + Mist, Snow + Fog")


def main1():
    st.title("Interpretasi untuk Menjawab Pertanyaan Ke-1")

    # Tombol untuk menampilkan keterangan
    if st.button("Tampilkan Keterangan 1"):
        st.success(" Berdasarkan data di atas, diperoleh bahwa jumlah pelanggan terbanyak ketika berada di musim Light Snow, Light Rain + Thunderstorm + Scattered clouds, Light Rain + Scattered clouds. Hal tersebut memungkinkan karena pelanggan tentunya ingin mengendarai sepeda dengan suasana yang tidak terik panas sehingga pada cuaca tersebut menjadi waktu yang tepat untuk bermain sepeda.")

if __name__ == "__main__":
    main1()

# Create the RF DataFrame
rf_df = create_rf_df(all_df)

# Streamlit app
st.title("Analisisis RF :mag: ")

# Display RF DataFrame
st.subheader("Recency dan Frequency Pada Setiap Bulan:")
st.write(rf_df)

# Metrics for average Recency and Frequency
avg_recency = round(rf_df.recency.mean(), 1)
avg_frequency = round(rf_df.frequency.mean(), 2)

# Display average Recency and Frequency
col1, col2 = st.columns(2)
with col1:
    st.metric("Average Recency (months)", value=avg_recency)

with col2:
    st.metric("Average Frequency", value=avg_frequency)

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(25, 15))

# recency
recency_df = rf_df.sort_values(by="recency", ascending=True).head(12)
colors_recency = ["#90CAF9"] * len(recency_df)
sns.barplot(y="recency", x="month", data=recency_df, palette=colors_recency, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Bulan ke-", fontsize=30)
ax[0].set_title("By Recency", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=35)

# frequency
frequency_df = rf_df.sort_values(by="frequency", ascending=False).head(12)
colors_frequency = ["#90CAF9"] * len(frequency_df)
sns.barplot(y="frequency", x="month", data=frequency_df, palette=colors_frequency, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Bulan ke-", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=35)

# Display plots
st.pyplot(fig)

def main2():
    st.title("Interpretasi untuk Menjawab Pertanyaan Ke-2")

    # Tombol untuk menampilkan keterangan
    if st.button("Tampilkan Keterangan 2"):
        st.success("Pada beberapa bulan terakhir, pelanggan melakukan penyewaan cukup sering yang dapat dilihat dari recency yang nilainya semakin rendah. Jumlah penyewa juga cukup banyak dalam beberapa bulan terakhir yang dapat dilihat dari nilai frekuensinya.")

if __name__ == "__main__":
    main2()


all_df['dteday'] = pd.to_datetime(all_df['dteday'])
all_df.set_index('dteday', inplace=True)

# Judul
st.title("Pola Waktu Jumlah Penyewa Sepeda")

# Pilih rentang jam menggunakan slider
selected_hour_range = st.slider("Pilih Rentang Jam", min_value=0, max_value=23, value=(0, 23))

# Memilih data sesuai dengan rentang jam yang dipilih
selected_data = all_df[(all_df['hr'] >= selected_hour_range[0]) & (all_df['hr'] <= selected_hour_range[1])]

# Plot grafik
plt.figure(figsize=(12, 6))
sns.lineplot(x=selected_data['hr'], y=selected_data['cnt_hourly'], ci=None, color='blue')
plt.title("Pola Jumlah Penyewa Sepeda Harian Berdasarkan Waktu")
plt.xlabel("Tanggal")
plt.ylabel("Jumlah Penyewa Sepeda Harian")
plt.xticks(rotation=45, ha='right')

st.pyplot(plt.gcf())

def main3():
    st.title("Interpretasi Grafik untuk Menjawab Pertanyaan Ke-3")

    # Tombol untuk menampilkan keterangan
    if st.button("Tampilkan Keterangan 3"):
        st.success("Jumlah penyewa sepeda rata-rata meningkat pada jam 16.00-17.00, artinya pelanggan banyak bermain sepeda di waktu sore.")

if __name__ == "__main__":
    main3()
