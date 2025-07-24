import streamlit as st
import pandas as pd
import plotly.express as px
import openai
import time
import os

# 🌐 Get OpenAI API Key securely from Streamlit secrets
openai.api_key = "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"

# 📂 Load Cleaned Data
data = pd.read_csv("cleaned_data.csv")
data['InvoiceDate'] = pd.to_datetime(data['InvoiceDate'])
data['YearMonth'] = data['InvoiceDate'].dt.to_period('M').astype(str)

# 🖥️ App Layout & Dark Theme
st.set_page_config(page_title="Consumer Insights Dashboard", layout="wide", initial_sidebar_state="expanded")
st.markdown(
    """
    <style>
    .main {
        background-color: #121212;
        color: #ffffff;
    }
    .stButton>button {
        color: #ffffff;
        background-color: #1DB954;
        border-radius: 8px;
        padding: 0.5em 1em;
    }
    .stSpinner {
        color: #1DB954;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🌌 Consumer Insights Dashboard (AI Powered)")
st.markdown("##### 🚀 Made by Vaishnavi Hidadugi for Ultimez Internship")

# 📊 Sidebar Filters
st.sidebar.header("🔎 Filters")
selected_country = st.sidebar.multiselect("🌍 Select Country", sorted(data['Country'].unique()))
selected_year_range = st.sidebar.slider("📅 Select Year Range", min_value=int(data['InvoiceDate'].dt.year.min()), max_value=int(data['InvoiceDate'].dt.year.max()), value=(int(data['InvoiceDate'].dt.year.min()), int(data['InvoiceDate'].dt.year.max())))

# Apply filters
if selected_country:
    data = data[data['Country'].isin(selected_country)]
data = data[(data['InvoiceDate'].dt.year >= selected_year_range[0]) & (data['InvoiceDate'].dt.year <= selected_year_range[1])]

# 📈 Monthly Revenue Trend
st.subheader("📈 Monthly Revenue Trend")
monthly_rev = data.groupby('YearMonth')['TotalPrice'].sum().reset_index()
fig1 = px.area(
    monthly_rev, x='YearMonth', y='TotalPrice', 
    title="📊 Monthly Revenue (Animated)",
    color_discrete_sequence=["#1DB954"],
    template="plotly_dark"
)
fig1.update_traces(mode="lines+markers")
st.plotly_chart(fig1, use_container_width=True)

# 🌍 Top Countries by Revenue
st.subheader("🌍 Top 10 Countries by Revenue")
country_rev = data.groupby('Country')['TotalPrice'].sum().sort_values(ascending=False).head(10).reset_index()
fig2 = px.bar(
    country_rev, x='Country', y='TotalPrice', 
    title="🌟 Top Countries",
    color='TotalPrice',
    color_continuous_scale="Viridis",
    template="plotly_dark"
)
st.plotly_chart(fig2, use_container_width=True)

# 🛍️ Top Products
st.subheader("🛍️ Top 10 Best-Selling Products")
top_products = data.groupby('Description')['TotalPrice'].sum().sort_values(ascending=False).head(10).reset_index()
fig3 = px.bar(
    top_products, x='TotalPrice', y='Description',
    orientation='h',
    title="🔥 Best-Selling Products",
    color='TotalPrice',
    color_continuous_scale="Plasma",
    template="plotly_dark"
)
st.plotly_chart(fig3, use_container_width=True)

# 🤖 AI-Powered Insights Section
st.subheader("🤖 AI-Powered Business Insights")

def get_ai_insights(prompt):
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional business analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=300
        )
        return response.choices[0].message.content.strip()
    except openai.RateLimitError:
        st.warning("⚠️ Rate limit hit. Retrying in 10 seconds...")
        time.sleep(10)
        return get_ai_insights(prompt)
    except Exception as e:
        return f"❌ Error: {e}"

if st.button("🔮 Generate Insights"):
    with st.spinner("🔄 AI is analyzing your data..."):
        summary = f"Top Country: {country_rev.iloc[0]['Country']}, Top Product: {top_products.iloc[0]['Description']}, Recent Monthly Revenue: {monthly_rev.tail(3).to_dict()}"
        insights = get_ai_insights(summary)
        st.success(f"💡 Insights:\n{insights}")

# 📋 Footer
st.markdown("---")
st.markdown("<center>✨ Made with ❤️ by Vaishnavi Hidadugi | Ultimez Internship 2025 ✨</center>", unsafe_allow_html=True)
