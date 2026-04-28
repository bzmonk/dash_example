import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta
import random
import os

# --- НАСТРОЙКИ СТРАНИЦЫ ---
st.set_page_config(page_title="AI Аналитика Ремонтов", layout="wide", initial_sidebar_state="collapsed")

# --- СТИЛИЗАЦИЯ (Фикс темной темы и закругления) ---
st.markdown("""
    <style>
    /* Настройка плашек колонн */
    div[data-testid="stExpander"] {
        background-color: #ffffff !important;
        border-radius: 15px !important;
        border: 1px solid #3b82f6 !important;
        margin-bottom: 10px;
    }
    /* Текст внутри плашек (названия колонн) */
    div[data-testid="stExpander"] p, div[data-testid="stExpander"] span {
        color: #003366 !important; 
        font-weight: bold !important;
        font-size: 1.1rem;
    }
    /* Кнопки механиков */
    .stButton>button {
        border-radius: 12px;
        background-color: #3b82f6 !important;
        color: white !important;
        border: none;
        padding: 10px 20px;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #1d4ed8 !important;
        transform: translateY(-2px);
    }
    /* Заголовки */
    h1, h2, h3 {
        color: #3b82f6 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- ДАННЫЕ КОМПАНИИ ---
FLEET_STRUCTURE = {
    "Колонна 1": ["Ахметнянов Руслан Равилевич", "Сергиевский Антон Сергеевич"],
    "Колонна 2": ["Галиев Анас Рашитович"],
    "Колонна 3": ["Назаров Андрей Михайлович"],
    "Колонна 4": ["Анисимов Владислав Николаевич", "Захаров Данил Анатольевич"],
    "Колонна 5": ["Захаров Андрей Юрьевич", "Иванов Михаил Сергеевич"],
    "Колонна Перемещение": ["Назаров Андрей Михайлович"]
}

# --- ГЕНЕРАЦИЯ ДАННЫХ (Симуляция) ---
@st.cache_data
def get_data(mechanic_name):
    np.random.seed(hash(mechanic_name) % 2**32)
    cars = []
    prefixes = ["A", "B", "E", "K", "M", "H", "O", "P", "C", "T"]
    for i in range(random.randint(10, 15)):
        truck_num = f"{random.choice(prefixes)}{random.randint(100,999)}{random.choice(prefixes)}{random.choice(prefixes)}116"
        trailer_num = f"XP{random.randint(1000,9999)}16"
        mileage = random.randint(150000, 600000)
        brakes = random.randint(30000, 350000); suspension = random.randint(20000, 200000)
        engine = random.randint(5000, 400000); electric = random.randint(2000, 50000)
        total = brakes + suspension + engine + electric + random.randint(5000, 100000)
        cpk = round(total / mileage, 2)
        last_date = datetime.now() - timedelta(days=random.randint(1, 60))
        cars.append({
            "Госномер": truck_num, "Прицеп": trailer_num, "Пробег": mileage,
            "Тормоза": brakes, "Ходовая": suspension, "ДВС": engine, "Электрика": electric,
            "Итого": total, "Руб/Км": cpk, "Дата рем.": last_date.strftime("%d.%m.%Y"),
            "Сумма рем.": random.randint(20000, 150000), "Что делали": random.choice(["Замена суппортов", "Ремонт ГБЦ", "Замена сайлентблоков", "Ремонт ПГУ", "Замена дисков/колодок"])
        })
    return pd.DataFrame(cars).sort_values("Руб/Км", ascending=False)

# --- ЛОГИКА ПЕРЕКЛЮЧЕНИЯ СТРАНИЦ ---
if 'page' not in st.session_state: st.session_state.page = 'main'
if 'mech' not in st.session_state: st.session_state.mech = None
if 'col' not in st.session_state: st.session_state.col = None

# =====================================================================
# ЭКРАН ВЫБОРА
# =====================================================================
if st.session_state.page == 'main':
    h_col1, h_col2 = st.columns([5, 1])
    with h_col1:
        st.title("🚛 Выбор подразделения") # ЗАМЕНИЛ ИКОНКУ ЗАВОДА НА ФУРУ
        st.write("Выберите колонну и ответственного механика для анализа рентабельности.")
    with h_col2:
        # Проверка наличия логотипа
        if os.path.exists("logo.png"):
            st.image("logo.png", use_container_width=True)
        else:
            st.caption("Логотип не найден")

    st.markdown("---")
    
    sc1, sc2, sc3 = st.columns([1, 2, 1])
    with sc2:
        for col_name, mechanics in FLEET_STRUCTURE.items():
            with st.expander(f"📁 {col_name}"):
                for m in mechanics:
                    if st.button(f"👤 {m}", key=f"btn_{col_name}_{m}"):
                        st.session_state.mech = m
                        st.session_state.col = col_name
                        st.session_state.page = 'dashboard'
                        st.rerun()

# =====================================================================
# ДАШБОРД
# =====================================================================
else:
    dh_col1, dh_col2, dh_col3 = st.columns([1, 4, 1])
    with dh_col1:
        if st.button("⬅ Назад"):
            st.session_state.page = 'main'
            st.rerun()
    with dh_col2:
        st.title(f"Аналитика: {st.session_state.mech}")
    with dh_col3:
        if os.path.exists("logo.png"):
            st.image("logo.png", width=100)

    df = get_data(st.session_state.mech)
    
    # Сводка
    k1, k2, k3 = st.columns(3)
    k1.metric("Машин в работе", len(df))
    k2.metric("Общие затраты", f"{df['Итого'].sum():,.0f} ₽")
    k3.metric("Средний Руб/Км", f"{df['Руб/Км'].mean():.2f}")

    st.markdown("---")
    st.subheader("⚠️ Проблемные авто (высокий Руб/Км)")
    fig = px.bar(df.head(5), x="Госномер", y="Руб/Км", color="Руб/Км", color_continuous_scale="Reds")
    st.plotly_chart(fig, use_container_width=True)

    # Аудит конкретной машины
    st.markdown("---")
    selected_car = st.selectbox("Выберите автомобиль для аудита:", df["Госномер"])
    car = df[df["Госномер"] == selected_car].iloc[0]

    det1, det2 = st.columns([1, 1])
    with det1:
        st.markdown(f"### Сцепка: `{car['Госномер']} / {car['Прицеп']}`")
        st.write(f"**Пробег:** {car['Пробег']:,.0f} км")
        st.write(f"**Показатель:** {car['Руб/Км']} руб/км")
        st.info(f"**Последний ремонт ({car['Дата рем.']}):** {car['Что делали']} на {car['Сумма рем.']:,.0f} ₽")
        
        st.subheader("🤖 Вывод ИИ:")
        if car["Руб/Км"] > 2.0:
            st.error("Критический перерасход. Рекомендуется проверить качество запчастей тормозной системы и работу водителя.")
        else:
            st.success("Машина в норме. Текущие затраты соответствуют пробегу.")
            
    with det2:
        costs = {"Тормоза": car["Тормоза"], "Ходовая": car["Ходовая"], "ДВС": car["ДВС"], "Электрика": car["Электрика"]}
        fig_pie = px.pie(values=list(costs.values()), names=list(costs.keys()), hole=0.4, title="Куда ушли деньги")
        st.plotly_chart(fig_pie, use_container_width=True)
