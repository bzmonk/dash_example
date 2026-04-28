import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta
import random
import os

# --- НАСТРОЙКИ СТРАНИЦЫ ---
st.set_page_config(page_title="AI Аналитика Ремонтов", layout="wide", initial_sidebar_state="collapsed")

# --- СТИЛИЗАЦИЯ И ФИКС ЛОГОТИПА ---
st.markdown("""
    <style>
    /* Фикс логотипа, чтобы он никогда не сплющивался */
    img { object-fit: contain !important; }
    
    div[data-testid="stExpander"] { background-color: #ffffff !important; border-radius: 15px !important; border: 1px solid #3b82f6 !important; margin-bottom: 10px; }
    div[data-testid="stExpander"] p, div[data-testid="stExpander"] span { color: #003366 !important; font-weight: bold !important; font-size: 1.1rem; }
    .stButton>button { border-radius: 12px; background-color: #3b82f6 !important; color: white !important; border: none; padding: 10px 20px; transition: all 0.3s; }
    .stButton>button:hover { background-color: #1d4ed8 !important; transform: translateY(-2px); }
    h1, h2, h3, h4 { color: #3b82f6 !important; }
    .stSlider div[data-testid="stThumbValue"] { color: #3b82f6 !important; }
    
    /* Красивая обводка для карточек машин */
    .car-card { border: 1px solid #e5e7eb; border-radius: 10px; padding: 20px; background-color: #f9fafb; margin-bottom: 20px;}
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

# --- ГЕНЕРАЦИЯ ДАННЫХ (Акты ремонтов 2024-2026) ---
@st.cache_data
def get_data(mechanic_name):
    np.random.seed(hash(mechanic_name) % 2**32)
    events = []
    prefixes = ["A", "B", "E", "K", "M", "H", "O", "P", "C", "T"]
    
    cars = []
    for _ in range(random.randint(10, 12)):
        truck = f"{random.choice(prefixes)}{random.randint(100,999)}{random.choice(prefixes)}{random.choice(prefixes)}116"
        trailer = f"XP{random.randint(1000,9999)}16"
        cars.append((truck, trailer))
        
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2026, 12, 31)
    
    for truck, trailer in cars:
        for _ in range(random.randint(15, 40)):
            r_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
            brakes = random.randint(0, 80000) if random.random() > 0.4 else 0
            suspension = random.randint(0, 60000) if random.random() > 0.5 else 0
            engine = random.randint(0, 150000) if random.random() > 0.8 else 0
            electric = random.randint(0, 20000) if random.random() > 0.6 else 0
            other = random.randint(5000, 30000)
            
            total = brakes + suspension + engine + electric + other
            mileage_period = random.randint(8000, 20000)
            
            events.append({
                "Госномер": truck, "Прицеп": trailer,
                "Дата": r_date, "Год": r_date.year, "Месяц": r_date.month,
                "Тормоза": brakes, "Ходовая": suspension, "ДВС": engine, "Электрика": electric, "Прочее": other,
                "Итого": total, "Пробег_период": mileage_period
            })
    return pd.DataFrame(events).sort_values("Дата")

MONTHS = {1: "Янв", 2: "Фев", 3: "Мар", 4: "Апр", 5: "Май", 6: "Июн", 7: "Июл", 8: "Авг", 9: "Сен", 10: "Окт", 11: "Ноя", 12: "Дек"}
REV_MONTHS = {v: k for k, v in MONTHS.items()}

if 'page' not in st.session_state: st.session_state.page = 'main'
if 'mech' not in st.session_state: st.session_state.mech = None
if 'col' not in st.session_state: st.session_state.col = None

# =====================================================================
# ЭКРАН ВЫБОРА
# =====================================================================
if st.session_state.page == 'main':
    h_col1, h_col2 = st.columns([6, 1])
    with h_col1:
        st.title("🚛 Выбор подразделения")
        st.write("Выберите колонну и ответственного механика для анализа рентабельности.")
    with h_col2:
        if os.path.exists("logo.png"):
            st.image("logo.png", use_container_width=True) # CSS object-fit теперь защищает от сплющивания

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
# ДАШБОРД МЕХАНИКА
# =====================================================================
else:
    dh_col1, dh_col2, dh_col3 = st.columns([1, 6, 1])
    with dh_col1:
        if st.button("⬅ Назад"):
            st.session_state.page = 'main'
            st.rerun()
    with dh_col2:
        st.title(f"Аналитика: {st.session_state.mech}")
    with dh_col3:
        if os.path.exists("logo.png"):
            st.image("logo.png", use_container_width=True)

    df_raw = get_data(st.session_state.mech)
    
    # --- ФИЛЬТРЫ ---
    st.markdown("### 📅 Фильтр периода ремонтов")
    f_col1, f_col2 = st.columns([1, 3])
    with f_col1:
        selected_year = st.selectbox("Выберите год:", [2024, 2025, 2026], index=0)
    with f_col2:
        start_m, end_m = st.select_slider("Выберите диапазон месяцев:", options=list(MONTHS.values()), value=("Янв", "Дек"))
        
    start_m_idx = REV_MONTHS[start_m]
    end_m_idx = REV_MONTHS[end_m]

    df_filtered = df_raw[(df_raw['Год'] == selected_year) & (df_raw['Месяц'] >= start_m_idx) & (df_raw['Месяц'] <= end_m_idx)]
    
    if df_filtered.empty:
        st.warning("В выбранном периоде нет записей о ремонтах.")
    else:
        df_agg = df_filtered.groupby(["Госномер", "Прицеп"]).agg({
            "Итого": "sum", "Пробег_период": "sum", "Тормоза": "sum", 
            "Ходовая": "sum", "ДВС": "sum", "Электрика": "sum", "Прочее": "sum"
        }).reset_index()
        df_agg["Руб/Км"] = (df_agg["Итого"] / df_agg["Пробег_период"]).round(2)
        df_agg = df_agg.sort_values("Руб/Км", ascending=False)

        k1, k2, k3 = st.columns(3)
        k1.metric("Ремонтировалось в периоде", len(df_agg))
        k2.metric("Общие затраты", f"{df_agg['Итого'].sum():,.0f} ₽".replace(",", " "))
        k3.metric("Средний Руб/Км", f"{df_agg['Руб/Км'].mean():.2f}")

        st.markdown("---")
        st.subheader(f"⚠️ Рейтинг затрат автомобилей за {start_m}-{end_m} {selected_year}")
        fig = px.bar(df_agg.head(10), x="Госномер", y="Руб/Км", color="Руб/Км", color_continuous_scale="Reds", text="Итого")
        fig.update_traces(texttemplate='%{text:,.0f} ₽', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        st.subheader("🔍 Выбор автомобилей для детального разбора")
        
        # Галочки (мультивыбор)
        selected_cars = st.multiselect(
            "Выберите один или несколько автомобилей (нажмите для выпадающего списка):", 
            options=df_agg["Госномер"].tolist(),
            default=[df_agg["Госномер"].iloc[0]]
        )

        if not selected_cars:
            st.info("Пожалуйста, выберите автомобили.")
        else:
            group_data = df_agg[df_agg["Госномер"].isin(selected_cars)]
            
            # --- БЛОК 1: СВОДКА ПО ГРУППЕ ---
            st.markdown("### 📊 Сводка по выбранной группе")
            total_group_cost = group_data["Итого"].sum()
            total_group_mileage = group_data["Пробег_период"].sum()
            group_cpk = round(total_group_cost / total_group_mileage, 2)
            
            g_col1, g_col2 = st.columns([1, 1])
            with g_col1:
                st.write(f"**Количество авто:** {len(selected_cars)}")
                st.write(f"**Общий пробег группы:** {total_group_mileage:,.0f} км".replace(",", " "))
                st.write(f"**Суммарные траты:** {total_group_cost:,.0f} ₽".replace(",", " "))
                st.info(f"**Средний показатель группы:** `{group_cpk} руб/км`")
            with g_col2:
                costs_group = { "Тормоза": group_data["Тормоза"].sum(), "Ходовая": group_data["Ходовая"].sum(), "ДВС": group_data["ДВС"].sum(), "Электрика": group_data["Электрика"].sum(), "Прочее": group_data["Прочее"].sum()}
                fig_pie_group = px.pie(values=list(costs_group.values()), names=list(costs_group.keys()), hole=0.4, title="Куда ушли деньги (вся группа)")
                fig_pie_group.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=300, margin=dict(t=30, b=0, l=0, r=0)) 
                st.plotly_chart(fig_pie_group, use_container_width=True)

            # --- БЛОК 2: ИНДИВИДУАЛЬНЫЕ АВТОМОБИЛИ ---
            st.markdown("---")
            st.markdown("### 🚘 Разбор каждого выбранного автомобиля")
            
            for car_num in selected_cars:
                car_row = group_data[group_data["Госномер"] == car_num].iloc[0]
                
                # Создаем визуальную "карточку" через контейнер
                with st.container():
                    st.markdown(f"#### Сцепка: `{car_row['Госномер']} / {car_row['Прицеп']}`")
                    
                    c1, c2 = st.columns([1, 1])
                    with c1:
                        st.write(f"**Пробег за период:** {car_row['Пробег_период']:,.0f} км".replace(",", " "))
                        st.write(f"**Потрачено:** {car_row['Итого']:,.0f} ₽".replace(",", " "))
                        st.write(f"**Показатель:** `{car_row['Руб/Км']} руб/км`")
                        
                        # Индивидуальный ИИ-вывод
                        if car_row['Руб/Км'] > 2.5:
                            st.error("**Аномальный расход!** Затраты значительно превышают норму. Рекомендуется технический аудит.")
                        elif car_row['Тормоза'] > car_row['Итого'] * 0.45:
                            st.warning("**Проблема с тормозами.** Более 45% затрат уходит на этот узел. Возможен агрессивный стиль вождения или брак запчастей.")
                        else:
                            st.success("**В пределах нормы.** Траты распределены адекватно пробегу.")
                    
                    with c2:
                        costs_car = { "Тормоза": car_row["Тормоза"], "Ходовая": car_row["Ходовая"], "ДВС": car_row["ДВС"], "Электрика": car_row["Электрика"], "Прочее": car_row["Прочее"]}
                        fig_pie_car = px.pie(values=list(costs_car.values()), names=list(costs_car.keys()), hole=0.5)
                        fig_pie_car.update_traces(textposition='inside', textinfo='percent+label')
                        fig_pie_car.update_layout(showlegend=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=250, margin=dict(t=10, b=10, l=10, r=10)) 
                        st.plotly_chart(fig_pie_car, use_container_width=True)
                
                st.markdown("<hr style='border: 1px dashed #e5e7eb;'>", unsafe_allow_html=True)
