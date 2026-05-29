import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
st.set_page_config(page_title="Коливання цін на харчові продукти",
                   page_icon = "st,small,507x507-pad,600x600,f8f8f8.jpg",
                   layout= "wide")
df = pd.read_excel("products_change.xlsx")
Image = Image.open("st,small,507x507-pad,600x600,f8f8f8.jpg")
col1, col2 = st.columns([1, 3])
with col1: st.image(Image, width=100)

#Створення sidebar
st.sidebar.header("Параметри")

#Сортування років, продуктів та категорій для створення фільтрів
years = sorted(df["year"].unique())
selected_year = st.sidebar.selectbox("Оберіть рік", years)

categories = sorted(df["category"].unique())
selected_category = st.sidebar.selectbox("Оберіть категорію", categories)

filtered_df = df[
    (df["year"] == selected_year) &
    (df["category"] == selected_category)
]

products = sorted(filtered_df["product_name"].unique())
selected_product = st.sidebar.multiselect("Оберіть продукт", products)
product_df = filtered_df[
    filtered_df["product_name"].isin(selected_product)
]


#Окремо створюю фільтр тільки для вибору року
filtered1_df = df[(df["year"] == selected_year)]


st.title("Коливання цін на харчові продукти")
tab1, tab2, tab3 = st.tabs(["Продукти", "Категорії", "Приріст"])

fig = px.line ( 
        product_df, x = "month" , y = "price", color= "product_name", title=f"Динаміка цін продуктів у категорії {selected_year} році" 
        ) 
fig.update_layout(yaxis_title = "Ціна, грн", xaxis_title="Місяць")
tab1.plotly_chart (fig, use_container_width=True)

fig2 = px.density_heatmap(
    filtered1_df, x="month",y="product_name",z="price",histfunc="avg",title=f"Теплова карта місячного порівняння вартості продуктів у {selected_year} році"
)
fig2.update_layout(
    xaxis_title="Місяць",
    yaxis_title="Назва продукту",
    coloraxis_colorbar_title="Ціна, грн"
)
tab1.plotly_chart(fig2)


#ГраФік середніх цін категорій
filtered_category = df[df["category"] == selected_category]
df_year = filtered_category.groupby("year")["price"].mean().reset_index()
fig_average = px.bar(
    df_year,
    x= "year",
    y = "price",
    color_discrete_sequence=["#FFF600"],
    title=f"Середня вартість за рік на {selected_category}"
)
fig_average.update_layout(yaxis_title = "Ціна, грн", xaxis_title="Рік")
tab2.plotly_chart(fig_average)


fig3 = px.density_heatmap(
filtered1_df, x="month",y="category",z="price",histfunc="avg",title=f"Теплова карта місячного порівняння вартості продуктів категорій у {selected_year} році"
)
fig3.update_layout(
    xaxis_title="Місяць",
    yaxis_title="Категорія",
    coloraxis_colorbar_title="Ціна, грн")
tab2.plotly_chart(fig3)

fig4 = px.density_heatmap(
    df, x="month",y="year",z="price",histfunc="avg",title="Теплова карта цінової зміни за роками"
)
fig4.update_layout(
    xaxis_title="Місяць",
    yaxis_title="Рік",
    coloraxis_colorbar_title="Ціна, грн")
tab2.plotly_chart(fig4)


filtered2 = df[df["year"].isin([selected_year, selected_year - 1])]
yearly = filtered2.groupby(
    ["year", "product_name"]
)["price"].mean().reset_index()
yearly = yearly.sort_values(
    ["product_name", "year"]
)
yearly["prev_price"] = yearly.groupby(
    "product_name"
)["price"].shift(1)

yearly["growth_%"] = (
    (yearly["price"] - yearly["prev_price"])
    / yearly["prev_price"]
) * 100
top6 = yearly[
    yearly["year"] == selected_year
].sort_values(
    "growth_%",
    ascending=False
).head(5)

fig5 = px.bar(
    top6,
    x="growth_%",
    y="product_name",
    color_discrete_sequence=["#00B4D8"],
    orientation="h",
    title=f"Топ-5 продуктів з найбільшим приростом у {selected_year} році"
)
fig5.update_layout(yaxis_title = "Назва продукту", xaxis_title="Відсоткова зміна")
tab3.plotly_chart(fig5, use_container_width=True)

monthly = filtered_df.groupby("month")["price"].mean().reset_index()
monthly["growth_%"] = monthly["price"].pct_change() * 100
monthly = monthly.dropna()
fig6 = px.bar(monthly,  x= "month",
    y = "growth_%",
    color_discrete_sequence=["#FFF600"],
    title=f"Щомісячний відсотковий приріст {selected_category} у {selected_year} році")
fig6.update_layout(yaxis_title = "Відсоткова зміна", xaxis_title="Місяць")
tab3.plotly_chart(fig6)