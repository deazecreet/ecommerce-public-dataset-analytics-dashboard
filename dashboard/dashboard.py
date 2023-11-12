import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Pengaturan Sidebar
st.sidebar.image('https://bit.ly/ecommerce_logo', use_column_width=True)
st.sidebar.title("E-Commerce Public Dataset Dashboard")
st.sidebar.markdown("Selamat datang di Dashboard Analitik E-Commerce Public Dataset!")
st.sidebar.caption('Made by Azel Rizki Nasution')

# 1
orders_df = pd.read_csv('dashboard/cleaned_ecommerce_dataset/orders_df.csv')

# Konversi kolom tanggal ke datetime
orders_df['order_delivered_customer_date'] = pd.to_datetime(orders_df['order_delivered_customer_date'])
orders_df['order_estimated_delivery_date'] = pd.to_datetime(orders_df['order_estimated_delivery_date'])

st.subheader('Percentage of On-Time Delivery vs Late Delivery')

# Dropdown untuk memilih tahun
years = list(orders_df['order_estimated_delivery_date'].dt.year.unique())
years.append('2016 - 2018')  # Menambahkan opsi "All"
selected_year = st.selectbox('Pilih Tahun', years)

# Filter data berdasarkan tahun yang dipilih
if selected_year == '2016 - 2018':
    filtered_df = orders_df
else:
    filtered_df = orders_df[orders_df['order_estimated_delivery_date'].dt.year == selected_year]

# Mengecek jika order dikirimkan tepat waktu
filtered_df['on_time_delivery'] = filtered_df['order_delivered_customer_date'] <= filtered_df['order_estimated_delivery_date']

# Menghitung persentase order yang dikirim tepat waktu
on_time_percentage = filtered_df['on_time_delivery'].mean() * 100

# Pengaturan plot
fig, ax = plt.subplots(figsize=(2, 2))

# Plot untuk on-time delivery
labels = ['Tepat Waktu', 'Terlambat']
sizes = [on_time_percentage, 100 - on_time_percentage]
colors = ['#66b2ff', '#ff9999']
explode = (0.1, 0)  # explode 1st slice for emphasis

# Plotting pie chart
ax.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
ax.axis('equal')   # Equal aspect ratio ensures that pie is drawn as a circle.

# Menampilkan plot di Streamlit
st.pyplot(fig)

# 2
st.cache_data()
def load_data(file_path):
    return pd.read_csv(file_path)

# Memuat data
order_payments_df = load_data('cleaned_ecommerce_dataset/order_payments_df.csv')

st.subheader('Average Payment Value per Payment Type')

# Dropdown untuk memilih jenis pembayaran untuk dianalisis
selected_payment_types = st.multiselect(
    'Pilih Tipe Pembayaran', 
    options=order_payments_df['payment_type'].unique(),
    default=order_payments_df['payment_type'].unique(),
    key="unique_key_for_payment_types_section_2"
)

# Filter data berdasarkan tipe pembayaran yang dipilih
filtered_df = order_payments_df[order_payments_df['payment_type'].isin(selected_payment_types)]

# Menghitung rata-rata nilai pembayaran untuk setiap tipe pembayaran
avg_payment_per_type = filtered_df.groupby('payment_type')['payment_value'].mean()
avg_payment_per_type = avg_payment_per_type.sort_values(ascending=False)

# Pengaturan plot
fig, ax = plt.subplots(figsize=(12, 6))

# Plot untuk rata-rata nilai pembayaran per tipe
sns.barplot(x=avg_payment_per_type.index, y=avg_payment_per_type.values, palette="viridis", ax=ax)
ax.set_ylabel('Average Value')
ax.set_xlabel('Payment Type')

# Menambahkan label di atas batang
for p in ax.patches:
    ax.annotate(f'{p.get_height():.2f}', 
                (p.get_x() + p.get_width() / 2., p.get_height()), 
                ha='center', va='center', 
                xytext=(0, 7), 
                textcoords='offset points')

# Menampilkan plot di Streamlit
st.pyplot(fig)

# 3
st.cache_data()
def load_data(file_paths):
    order_items_df = pd.read_csv(file_paths['order_items'])
    products_df = pd.read_csv(file_paths['products'])
    return pd.merge(order_items_df, products_df, on='product_id', how='left')

# Memuat data
file_paths = {
    'order_items': 'cleaned_ecommerce_dataset/order_items_df.csv',
    'products': 'cleaned_ecommerce_dataset/products_df.csv'
}
merged_df = load_data(file_paths)

# Inisialisasi subheader
st.subheader('Top Product Categories by Sales Volume')

# Dropdown untuk memilih jumlah kategori teratas
top_n = st.selectbox('Pilih Jumlah Kategori Teratas', range(1, 21), index=4,
                     key='selectbox1')  # Default ke 10 kategori teratas

# Update subheader berdasarkan pilihan pengguna
st.markdown(f'##### Top {top_n} Product Categories by Sales Volume')

# Menghitung jumlah produk yang terjual per kategori
category_counts_merged = merged_df['product_category_name'].value_counts()

# Pengaturan plot untuk kategori teratas
fig, ax = plt.subplots(figsize=(14, 10))
ax = sns.barplot(y=category_counts_merged.index[:top_n], x=category_counts_merged.values[:top_n], palette="viridis", orient='h')
ax.set_xlabel('Number of Products Sold')
ax.set_ylabel('Product Category')

# Menambahkan label di sebelah kanan batang
for p in ax.patches:
    width = p.get_width()
    ax.text(width + 250, p.get_y() + p.get_height() / 2, '{:1.0f}'.format(width), ha='center', va='center')

# Menampilkan plot di Streamlit
st.pyplot(fig)

# 4
st.cache_data()
def load_data(file_paths):
    order_reviews_df = pd.read_csv(file_paths['order_reviews'])
    orders_df = pd.read_csv(file_paths['orders'])
    customers_df = pd.read_csv(file_paths['customers'])
    return order_reviews_df, orders_df, customers_df

# Memuat data
file_paths = {
    'order_reviews': 'cleaned_ecommerce_dataset/order_reviews_df.csv',
    'orders': 'cleaned_ecommerce_dataset/orders_df.csv',
    'customers': 'cleaned_ecommerce_dataset/customers_df.csv'
}
order_reviews_df, orders_df, customers_df = load_data(file_paths)

# Proses penggabungan data
merged_reviews_orders = pd.merge(order_reviews_df, orders_df, on='order_id', how='left')
final_merged_df = pd.merge(merged_reviews_orders, customers_df, on='customer_id', how='left')
final_merged_df['negative_review'] = final_merged_df['review_score'].isin([1, 2])

# Menghitung persentase ulasan negatif per negara bagian
negative_review_by_state = final_merged_df.groupby('customer_state')['negative_review'].mean().sort_values(ascending=False)

# Inisialisasi subheader
st.subheader('Top States by Negative Reviews')

# Dropdown untuk memilih jumlah negara bagian teratas
top_n_states = st.selectbox('Pilih Jumlah Negara Bagian Teratas', range(1, 21), index=4)

# Update subheader berdasarkan pilihan pengguna
st.markdown(f'##### Top {top_n_states} States by Negative Reviews')

# Pengaturan plot
fig, ax = plt.subplots(figsize=(15, 8))
ax = sns.barplot(x=negative_review_by_state.index[:top_n_states], y=negative_review_by_state.values[:top_n_states] * 100, palette="viridis")
ax.set_ylabel('Percentage of Negative Reviews (%)')
ax.set_xlabel('State')

# Menambahkan label di atas batang
for p in ax.patches:
    ax.annotate(f'{p.get_height():.2f}%', 
                (p.get_x() + p.get_width() / 2., p.get_height()), 
                ha='center', va='center', 
                xytext=(0, 7), 
                textcoords='offset points')

# Menampilkan plot di Streamlit
st.pyplot(fig)

# 5
@st.cache_data()
def load_data(file_path):
    return pd.read_csv(file_path)

# Memuat data
order_payments_df = load_data('cleaned_ecommerce_dataset/order_payments_df.csv')

st.subheader('Distribution of Payment Methods')

# Checkbox untuk memilih tipe pembayaran
payment_types = order_payments_df['payment_type'].unique()
selected_payment_types = st.multiselect('Pilih Tipe Pembayaran', payment_types, default=payment_types,
                                        key="unique_key_for_payment_types_section_5")

# Filter data berdasarkan tipe pembayaran yang dipilih
filtered_df = order_payments_df[order_payments_df['payment_type'].isin(selected_payment_types)]

# Menghitung jumlah transaksi untuk setiap tipe pembayaran
payment_type_counts = filtered_df['payment_type'].value_counts()

# Pengaturan plot
fig, ax = plt.subplots(figsize=(12, 8))
sns.barplot(x=payment_type_counts.index, y=payment_type_counts.values, palette="viridis", ax=ax)
ax.set_ylabel('Number of Transactions')
ax.set_xlabel('Payment Type')

# Menambahkan label di atas batang
for p in ax.patches:
    ax.annotate(f'{p.get_height():.0f}', 
                (p.get_x() + p.get_width() / 2., p.get_height()), 
                ha='center', va='center', 
                xytext=(0, 7), 
                textcoords='offset points')

# Menampilkan plot di Streamlit
st.pyplot(fig)

# 6
@st.cache_data()
def load_data(file_paths):
    order_reviews_df = pd.read_csv(file_paths['order_reviews'])
    orders_df = pd.read_csv(file_paths['orders'])
    customers_df = pd.read_csv(file_paths['customers'])
    order_items_df = pd.read_csv(file_paths['order_items'])
    products_df = pd.read_csv(file_paths['products'])
    return order_reviews_df, orders_df, customers_df, order_items_df, products_df

# Memuat data
file_paths = {
    'order_reviews': 'cleaned_ecommerce_dataset/order_reviews_df.csv',
    'orders': 'cleaned_ecommerce_dataset/orders_df.csv',
    'customers': 'cleaned_ecommerce_dataset/customers_df.csv',
    'order_items': 'cleaned_ecommerce_dataset/order_items_df.csv',
    'products': 'cleaned_ecommerce_dataset/products_df.csv'
}
order_reviews_df, orders_df, customers_df, order_items_df, products_df = load_data(file_paths)

# Mendefinisikan review positif dan negatif
final_merged_df['positive_review'] = final_merged_df['review_score'].isin([4, 5])

# Menggabungkan dengan dataset yang telah digabungkan sebelumnya untuk mendapatkan nama kategori produk
final_merged_with_category_df = pd.merge(final_merged_df, order_items_df[['order_id', 'product_id']], on='order_id', how='left')
final_merged_with_category_df = pd.merge(final_merged_with_category_df, products_df[['product_id', 'product_category_name']], on='product_id', how='left')

# Mengelompokkan kategori produk dan menghitung persentase review positif dan negatif
positive_review_by_category = final_merged_with_category_df.groupby('product_category_name')['positive_review'].mean().sort_values(ascending=False)
negative_review_by_category = final_merged_with_category_df.groupby('product_category_name')['negative_review'].mean().sort_values(ascending=False)

st.subheader('Top Product Categories by Reviews')

# Dropdown untuk memilih jumlah kategori teratas
top_n = st.selectbox('Pilih Jumlah Kategori Teratas', range(1, 21), index=4,
                     key='selectbox2')

# Pengaturan plot
fig, axs = plt.subplots(2, 1, figsize=(14, 24))

# Tentukan faktor ekspansi untuk batas x-axis
expansion_factor = 1.15

# Plot untuk ulasan positif
sns.barplot(y=positive_review_by_category.index[:top_n], x=positive_review_by_category.values[:top_n] * 100, palette="viridis", orient='h', ax=axs[0])
axs[0].set_title('Top {} Product Categories with Highest Positive Reviews'.format(top_n))
axs[0].set_xlabel('Percentage of Positive Reviews (%)')
axs[0].set_ylabel('Product Category')

# Menyesuaikan xlim dengan faktor ekspansi
max_value = positive_review_by_category.values[:top_n].max() * 100
axs[0].set_xlim(0, max_value * expansion_factor)

# Plot untuk ulasan negatif
sns.barplot(y=negative_review_by_category.index[:top_n], x=negative_review_by_category.values[:top_n] * 100, palette="viridis", orient='h', ax=axs[1])
axs[1].set_title('Top {} Product Categories with Highest Negative Reviews'.format(top_n))
axs[1].set_xlabel('Percentage of Negative Reviews (%)')
axs[1].set_ylabel('Product Category')

# Menyesuaikan xlim dengan faktor ekspansi
max_value = negative_review_by_category.values[:top_n].max() * 100
axs[1].set_xlim(0, max_value * expansion_factor)

# Menambahkan label di sebelah kanan bar chart
for ax in axs:
    for p in ax.patches:
        width = p.get_width()
        ax.text(width + (max_value * 0.03), p.get_y() + p.get_height() / 2, '{:.2f}%'.format(width), 
                ha='left', va='center')

plt.tight_layout()

# Menampilkan plot di Streamlit
st.pyplot(fig)

# 7
@st.cache_data()
def load_data(file_path):
    df = pd.read_csv(file_path)
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    df['month_year'] = df['order_purchase_timestamp'].dt.to_period('M')
    return df

# Memuat data
orders_df = load_data('cleaned_ecommerce_dataset/orders_df.csv')

st.subheader("Monthly Sales Trend")

# Slider untuk memilih rentang tahun
year_range = st.slider('Pilih Rentang Tahun', 2016, 2018, (2016, 2018))

st.markdown(f'##### Monthly Sales Trend ({year_range[0]}-{year_range[1]})')

# Filter data berdasarkan rentang tahun yang dipilih
filtered_orders = orders_df[orders_df['order_purchase_timestamp'].dt.year.isin(range(year_range[0], year_range[1] + 1))]

# Group by month_year and count the number of orders
monthly_sales = filtered_orders.groupby('month_year').size()

# Pengaturan plot
fig, ax = plt.subplots(figsize=(15, 7))
monthly_sales.plot(kind='line', marker='o', ax=ax)
ax.set_ylabel('Number of Orders')
ax.set_xlabel('Month-Year')
ax.grid(True, which='both', linestyle='--', linewidth=0.5)

# Menampilkan plot di Streamlit
st.pyplot(fig)

# 9
def load_data(file_path):
    return pd.read_csv(file_path)

# Memuat data
customers_df = load_data('cleaned_ecommerce_dataset/customers_df.csv')

st.subheader('Top Customers by State')

# Dropdown untuk memilih jumlah negara bagian teratas
top_n_states = st.selectbox('Pilih Jumlah Negara Bagian Teratas', range(1, 27), index=4)  # Anggap ada 26 negara bagian

st.markdown(f'##### Top {top_n_states} Number of Customers by State')

# Menghitung jumlah pelanggan per negara bagian
customers_by_state = customers_df['customer_state'].value_counts()

# Pengaturan plot
fig, ax = plt.subplots(figsize=(15, 8))
sns.barplot(x=customers_by_state.index[:top_n_states], y=customers_by_state.values[:top_n_states], palette="viridis", ax=ax)
ax.set_ylabel('Number of Customers')
ax.set_xlabel('State')

# Menambahkan label di atas batang
for p in ax.patches:
    ax.annotate(f'{p.get_height():.0f}', 
                (p.get_x() + p.get_width() / 2., p.get_height()), 
                ha='center', va='center', 
                xytext=(0, 7), 
                textcoords='offset points')

plt.tight_layout()

# Menampilkan plot di Streamlit
st.pyplot(fig)

# 10
@st.cache_data()
def load_data(file_path):
    df = pd.read_csv(file_path)
    return df

# Memuat data ulasan
order_reviews_df = load_data('cleaned_ecommerce_dataset/order_reviews_df.csv')

st.subheader('Distribution of Selected Review Scores')

# Checkbox untuk memilih skor ulasan tertentu
selected_scores = st.multiselect('Pilih Skor Ulasan', options=order_reviews_df['review_score'].unique(), default=order_reviews_df['review_score'].unique())

# Filter data berdasarkan skor ulasan yang dipilih
filtered_reviews = order_reviews_df[order_reviews_df['review_score'].isin(selected_scores)]

# Menghitung distribusi skor ulasan yang dipilih
review_scores_distribution = filtered_reviews['review_score'].value_counts(normalize=True) * 100
review_scores_distribution = review_scores_distribution.sort_index(ascending=False)

# Pengaturan plot
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(x=review_scores_distribution.index, y=review_scores_distribution.values, palette="viridis", ax=ax)
ax.set_xlabel('Review Score')
ax.set_ylabel('Percentage of Reviews (%)')

# Menambahkan label di atas batang
for p in ax.patches:
    ax.annotate(f'{p.get_height():.2f}%', 
                (p.get_x() + p.get_width() / 2., p.get_height()), 
                ha='center', va='center', 
                xytext=(0, 7), 
                textcoords='offset points')

plt.tight_layout()

# Menampilkan plot di Streamlit
st.pyplot(fig)

# 11
@st.cache_data()
def load_data(file_path):
    return pd.read_csv(file_path)

# Memuat data penjual
sellers_df = load_data('cleaned_ecommerce_dataset/sellers_df.csv')

st.subheader('Top Sellers by State')

# Dropdown untuk memilih jumlah negara bagian teratas
top_n_states = st.selectbox('Pilih Jumlah Negara Bagian Teratas', range(1, 27), index=4,
                            key="selectbox3")  # Anggap ada 26 negara bagian

st.markdown(f'##### Top {top_n_states} Number of Sellers by State')

# Menghitung jumlah penjual per negara bagian
sellers_by_state = sellers_df['seller_state'].value_counts()

# Pengaturan plot
fig, ax = plt.subplots(figsize=(15, 8))
sns.barplot(x=sellers_by_state.index[:top_n_states], y=sellers_by_state.values[:top_n_states], palette="viridis", ax=ax)
ax.set_ylabel('Number of Sellers')
ax.set_xlabel('State')

# Menambahkan label di atas batang
for p in ax.patches:
    ax.annotate(f'{p.get_height():.0f}', 
                (p.get_x() + p.get_width() / 2., p.get_height()), 
                ha='center', va='center', 
                xytext=(0, 7), 
                textcoords='offset points')

plt.tight_layout()

# Menampilkan plot di Streamlit
st.pyplot(fig)

# RFM Analysis
@st.cache_data()
def load_data():
    orders_df = pd.read_csv('cleaned_ecommerce_dataset/orders_df.csv')
    order_payments_df = pd.read_csv('cleaned_ecommerce_dataset/order_payments_df.csv')
    orders_df['order_purchase_timestamp'] = pd.to_datetime(orders_df['order_purchase_timestamp'])
    return orders_df, order_payments_df

# Memuat data
orders_df, order_payments_df = load_data()

# Hitung RFM
# Recency
recency_df = orders_df.groupby('customer_id')['order_purchase_timestamp'].max().reset_index()
recency_df['Recency'] = (recency_df['order_purchase_timestamp'].max() - recency_df['order_purchase_timestamp']).dt.days
recency_df = recency_df[['customer_id', 'Recency']]

# Frequency
frequency_df = orders_df.groupby('customer_id')['order_id'].count().reset_index()
frequency_df.columns = ['customer_id', 'Frequency']

# Monetary
monetary_df = order_payments_df.groupby('order_id')['payment_value'].sum().reset_index()
monetary_df = pd.merge(monetary_df, orders_df[['order_id', 'customer_id']], on='order_id', how='left')
monetary_df = monetary_df.groupby('customer_id')['payment_value'].sum().reset_index()
monetary_df.columns = ['customer_id', 'Monetary']

# Merge RFM
rfm_df = pd.merge(recency_df, frequency_df, on='customer_id')
rfm_df = pd.merge(rfm_df, monetary_df, on='customer_id')

# Skor RFM
rfm_df['R_Score'] = pd.qcut(rfm_df['Recency'], q=4, labels=[4, 3, 2, 1])

# Menggunakan nilai absolut untuk Frequency
unique_frequencies = frequency_df['Frequency'].unique()
if len(unique_frequencies) > 4:
    rfm_df['F_Score'] = pd.cut(rfm_df['Frequency'], bins=4, labels=[1, 2, 3, 4])
else:
    # Jika tidak cukup variasi, gunakan jumlah unik dari Frequency untuk membuat bins
    rfm_df['F_Score'] = pd.cut(rfm_df['Frequency'], bins=len(unique_frequencies), labels=range(1, len(unique_frequencies) + 1))

rfm_df['M_Score'] = pd.qcut(rfm_df['Monetary'], q=4, labels=[1, 2, 3, 4])

# Tambahkan filter untuk skor RFM
st.header("RFM Score Analysis")

# Pastikan ada nilai default yang valid untuk multiselect
default_r_scores = list(rfm_df['R_Score'].unique())
default_f_scores = list(rfm_df['F_Score'].unique())
default_m_scores = list(rfm_df['M_Score'].unique())

selected_r_score = st.multiselect('Select R Score', options=default_r_scores, default=default_r_scores)
selected_f_score = st.multiselect('Select F Score', options=default_f_scores, default=default_f_scores)
selected_m_score = st.multiselect('Select M Score', options=default_m_scores, default=default_m_scores)

# Filter data berdasarkan pilihan
filtered_rfm_df = rfm_df[rfm_df['R_Score'].isin(selected_r_score) & rfm_df['F_Score'].isin(selected_f_score) & rfm_df['M_Score'].isin(selected_m_score)]

# Visualisasi distribusi skor RFM
fig, axs = plt.subplots(2, 2, figsize=(15, 10))

# R_Score
sns.countplot(data=filtered_rfm_df, x='R_Score', ax=axs[0, 0], color='#2DA7E4')
axs[0, 0].set_title('Distribution of R_Score')
axs[0, 0].set_ylabel('Number of Customers')
for p in axs[0, 0].patches:
    axs[0, 0].annotate(f'{p.get_height():.0f}', 
                       (p.get_x() + p.get_width() / 2., p.get_height()), 
                       ha='center', va='center', 
                       xytext=(0, 5), 
                       textcoords='offset points')

# F_Score
sns.countplot(data=filtered_rfm_df, x='F_Score', ax=axs[0, 1], color='#2DA7E4')
axs[0, 1].set_title('Distribution of F_Score')
axs[0, 1].set_ylabel('Number of Customers')
for p in axs[0, 1].patches:
    axs[0, 1].annotate(f'{p.get_height():.0f}', 
                       (p.get_x() + p.get_width() / 2., p.get_height()), 
                       ha='center', va='center', 
                       xytext=(0, 5), 
                       textcoords='offset points')

# M_Score
sns.countplot(data=filtered_rfm_df, x='M_Score', ax=axs[1, 0], color='#2DA7E4')
axs[1, 0].set_title('Distribution of M_Score')
axs[1, 0].set_ylabel('Number of Customers')
for p in axs[1, 0].patches:
    axs[1, 0].annotate(f'{p.get_height():.0f}', 
                       (p.get_x() + p.get_width() / 2., p.get_height()), 
                       ha='center', va='center', 
                       xytext=(0, 5), 
                       textcoords='offset points')

# RFM_Score
filtered_rfm_df['RFM_Score'] = filtered_rfm_df[['R_Score', 'F_Score', 'M_Score']].sum(axis=1)
sns.countplot(data=filtered_rfm_df, x='RFM_Score', ax=axs[1, 1], color='#2DA7E4')
axs[1, 1].set_title('Distribution of RFM_Score')
axs[1, 1].set_ylabel('Number of Customers')
for p in axs[1, 1].patches:
    axs[1, 1].annotate(f'{p.get_height():.0f}', 
                       (p.get_x() + p.get_width() / 2., p.get_height()), 
                       ha='center', va='center', 
                       xytext=(0, 5), 
                       textcoords='offset points')

plt.tight_layout()
st.pyplot(fig)

st.caption('Copyright © 2023 Azel Rizki Nasution')
