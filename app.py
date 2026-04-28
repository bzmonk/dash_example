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
    img { object-fit: contain !important; }
    div[data-testid="stExpander"] { background-color: #ffffff !important; border-radius: 15px !important; border: 1px solid #3b82f6 !important; margin-bottom: 10px; }
    div[data-testid="stExpander"] p, div[data-testid="stExpander"] span { color: #003366 !important; font-weight: bold !important; font-size: 1.1rem; }
    .stButton>button { border-radius: 12px; background-color: #3b82f6 !important; color: white !important; border: none; padding: 10px 20px; transition: all 0.3s; }
    .stButton>button:hover { background-color: #1d4ed8 !important; transform: translateY(-2px); }
    h1, h2, h3, h4 { color: #3b82f6 !important; }
    .stSlider div[data-testid="stThumbValue"] { color: #3b82f6 !important; }
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

TRUCK_BRANDS = ["CHENGLONG", "DONGFENG", "FAW", "RENAULT T 4X2", "SCANIA", "SHACMAN", "SITRAK", "КАМАЗ"]
TRAILER_BRANDS = ["BONUM", "CTTM CARGOLINE", "FLIEGL", "Grunwald", "ISO PAKCS", "KOLUMAN", "KRONE", "ORTHAUS", "SCHMITZ", "UAT", "WAGNERMAIER", "WIELTON", "Сторонний", "ТЗА", "ТОНАР"]

# --- ГЕНЕРАЦИЯ ДАННЫХ ---
@st.cache_data
def get_data(mechanic_name):
    seed_val = hash(mechanic_name) % 2**32
    np.random.seed(seed_val)
    random.seed(seed_val)
    
    events = []
    prefixes = ["A", "B", "E", "K", "M", "H", "O", "P", "C", "T"]
    
    cars = []
    fleet_size = random.randint(5, 25) 
    
    for _ in range(fleet_size):
        truck = f"{random.choice(prefixes)}{random.randint(100,999)}{random.choice(prefixes)}{random.choice(prefixes)}116"
        truck_brand = random.choice(TRUCK_BRANDS)
        truck_year = random.randint(2015, 2024)
        
        trailer = f"XP{random.randint(1000,9999)}16"
        trailer_brand = random.choice(TRAILER_BRANDS)
        trailer_year = random.randint(2015, 2024)
        
        combo_name = f"{truck} / {trailer}"
        cars.append({"combo": combo_name, "truck": truck, "t_brand": truck_brand, "t_year": truck_year, 
                     "trailer": trailer, "tr_brand": trailer_brand, "tr_year": trailer_year})
        
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2026, 12, 31)
    
    for car in cars:
        # Ремонты ТЯГАЧА
        for _ in range(random.randint(10, 30)):
            r_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
            brakes = random.randint(0, 50000) if random.random() > 0.4 else 0
            suspension = random.randint(0, 40000) if random.random() > 0.5 else 0
            engine = random.randint(0, 150000) if random.random() > 0.8 else 0
            electric = random.randint(0, 20000) if random.random() > 0.6 else 0
            other = random.randint(5000, 20000)
            total = brakes + suspension + engine + electric + other
            mileage = random.randint(5000, 15000)
            
            events.append({
                "Сцепка": car['combo'], "Госномер": car['truck'], "Марка": car['t_brand'], "Год_ТС": car['t_year'],
                "Марка_Тягача": car['t_brand'], "Марка_Прицепа": car['tr_brand'], # Добавлено для удобного фильтра сцепки
                "Тип": "Тягач", "Дата": r_date, "Год": r_date.year, "Месяц": r_date.month,
                "Тормоза": brakes, "Ходовая": suspension, "ДВС": engine, "Электрика": electric, "Прочее": other,
                "Итого": total, "Пробег_период": mileage
            })
            
        # Ремонты ПРИЦЕПА
        for _ in range(random.randint(5, 20)):
            r_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
            brakes = random.randint(0, 60000) if random.random() > 0.3 else 0
            suspension = random.randint(0, 50000) if random.random() > 0.4 else 0
            engine = 0
            electric = random.randint(0, 10000) if random.random() > 0.7 else 0
            other = random.randint(2000, 15000)
            total = brakes + suspension + engine + electric + other
            mileage = random.randint(5000, 15000)
            
            events.append({
                "Сцепка": car['combo'], "Госномер": car['trailer'], "Марка": car['tr_brand'], "Год_ТС": car['tr_year'],
                "Марка_Тягача": car['t_brand'], "Марка_Прицепа": car['tr_brand'],
                "Тип": "Прицеп", "Дата": r_date, "Год": r_date.year, "Месяц": r_date.month,
                "Тормоза": brakes, "Ходовая": suspension, "ДВС": engine, "Электрика": electric, "Прочее": other,
                "Итого": total, "Пробег_период": mileage
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
            st.image("logo.png", use_container_width=True)

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
    
    st.markdown("### 🎛️ Фильтры аналитики")
    
    # 1. Выбор категории
    view_mode = st.radio("Выберите объект анализа:", ["Сцепка", "Тягач", "Прицеп"], horizontal=True)
    
    # 2. Фильтры периода
    f_col1, f_col2 = st.columns([1, 3])
    with f_col1:
        selected_year = st.selectbox("Выберите год:", [2024, 2025, 2026], index=0)
    with f_col2:
        start_m, end_m = st.select_slider("Выберите диапазон месяцев:", options=list(MONTHS.values()), value=("Янв", "Дек"))
        
    start_m_idx = REV_MONTHS[start_m]
    end_m_idx = REV_MONTHS[end_m]

    # Базовая фильтрация по дате
    df_filtered = df_raw[(df_raw['Год'] == selected_year) & (df_raw['Месяц'] >= start_m_idx) & (df_raw['Месяц'] <= end_m_idx)]
    
    # 3. Фильтры Марки и Года (зависят от выбранной категории)
    st.markdown("#### 🏷️ Характеристики техники (оставьте пустым для выбора всех)")
    filter_col1, filter_col2 = st.columns(2)
    
    if view_mode == "Тягач":
        df_filtered = df_filtered[df_filtered['Тип'] == "Тягач"]
        all_brands = sorted(df_filtered['Марка'].unique())
        all_years = sorted(df_filtered['Год_ТС'].unique())
        
        with filter_col1:
            sel_brands = st.multiselect("Марка тягача:", all_brands)
        with filter_col2:
            sel_years = st.multiselect("Год выпуска:", all_years)
            
        if sel_brands: df_filtered = df_filtered[df_filtered['Марка'].isin(sel_brands)]
        if sel_years:  df_filtered = df_filtered[df_filtered['Год_ТС'].isin(sel_years)]
        group_cols = ["Госномер", "Марка", "Год_ТС"]

    elif view_mode == "Прицеп":
        df_filtered = df_filtered[df_filtered['Тип'] == "Прицеп"]
        all_brands = sorted(df_filtered['Марка'].unique())
        all_years = sorted(df_filtered['Год_ТС'].unique())
        
        with filter_col1:
            sel_brands = st.multiselect("Марка прицепа:", all_brands)
        with filter_col2:
            sel_years = st.multiselect("Год выпуска:", all_years)
            
        if sel_brands: df_filtered = df_filtered[df_filtered['Марка'].isin(sel_brands)]
        if sel_years:  df_filtered = df_filtered[df_filtered['Год_ТС'].isin(sel_years)]
        group_cols = ["Госномер", "Марка", "Год_ТС"]

    else: # Сцепка
        all_t_brands = sorted(df_filtered['Марка_Тягача'].unique())
        all_tr_brands = sorted(df_filtered['Марка_Прицепа'].unique())
        
        with filter_col1:
            sel_t_brands = st.multiselect("Марка тягача (в составе сцепки):", all_t_brands)
        with filter_col2:
            sel_tr_brands = st.multiselect("Марка прицепа (в составе сцепки):", all_tr_brands)
            
        if sel_t_brands: df_filtered = df_filtered[df_filtered['Марка_Тягача'].isin(sel_t_brands)]
        if sel_tr_brands: df_filtered = df_filtered[df_filtered['Марка_Прицепа'].isin(sel_tr_brands)]
        group_cols = ["Сцепка"]
    
    if df_filtered.empty:
        st.warning(f"Нет данных по выбранным фильтрам для категории: {view_mode}.")
    else:
        # Агрегация данных
        df_agg = df_filtered.groupby(group_cols).agg({
            "Итого": "sum", "Пробег_период": "sum", "Тормоза": "sum", 
            "Ходовая": "sum", "ДВС": "sum", "Электрика": "sum", "Прочее": "sum"
        }).reset_index()
        
        # Формирование названия
        if view_mode != "Сцепка":
            df_agg["Название_Отображение"] = df_agg["Госномер"] + " (" + df_agg["Марка"] + ", " + df_agg["Год_ТС"].astype(str) + " г.)"
        else:
            df_agg["Название_Отображение"] = df_agg["Сцепка"]

        df_agg["Руб/Км"] = (df_agg["Итого"] / df_agg["Пробег_период"]).round(2)
        df_agg = df_agg.sort_values("Руб/Км", ascending=False)

        k1, k2, k3 = st.columns(3)
        k1.metric(f"Уникальных ед. ({view_mode.lower()})", len(df_agg))
        k2.metric("Общие затраты", f"{df_agg['Итого'].sum():,.0f} ₽".replace(",", " "))
        k3.metric("Средний Руб/Км", f"{df_agg['Руб/Км'].mean():.2f}")

        st.markdown("---")
        st.subheader(f"⚠️ Топ-10 затрат ({view_mode})")
        fig = px.bar(df_agg.head(10), x="Название_Отображение", y="Руб/Км", color="Руб/Км", color_continuous_scale="Reds", text="Итого")
        fig.update_traces(texttemplate='%{text:,.0f} ₽', textposition='outside')
        fig.update_layout(xaxis_title="Техника", yaxis_title="Руб / Км")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        st.subheader("🔍 Детальный разбор")
        
        selected_cars = st.multiselect(
            "Выберите конкретную технику из отфильтрованного списка:", 
            options=df_agg["Название_Отображение"].tolist(),
            default=[df_agg["Название_Отображение"].iloc[0]] if not df_agg.empty else []
        )

        if not selected_cars:
            st.info("Пожалуйста, выберите технику.")
        else:
            group_data = df_agg[df_agg["Название_Отображение"].isin(selected_cars)]
            
            # --- СВОДКА ПО ГРУППЕ ---
            st.markdown("### 📊 Сводка по выбранной группе")
            total_group_cost = group_data["Итого"].sum()
            total_group_mileage = group_data["Пробег_период"].sum()
            group_cpk = round(total_group_cost / total_group_mileage, 2) if total_group_mileage > 0 else 0
            
            g_col1, g_col2 = st.columns([1, 1])
            with g_col1:
                st.write(f"**Выбрано единиц:** {len(selected_cars)}")
                st.write(f"**Общий пробег группы:** {total_group_mileage:,.0f} км".replace(",", " "))
                st.write(f"**Суммарные траты:** {total_group_cost:,.0f} ₽".replace(",", " "))
                st.info(f"**Средний показатель группы:** `{group_cpk} руб/км`")
            with g_col2:
                costs_group = { "Тормоза": group_data["Тормоза"].sum(), "Ходовая": group_data["Ходовая"].sum(), "ДВС": group_data["ДВС"].sum(), "Электрика": group_data["Электрика"].sum(), "Прочее": group_data["Прочее"].sum()}
                costs_group = {k: v for k, v in costs_group.items() if v > 0} 
                fig_pie_group = px.pie(values=list(costs_group.values()), names=list(costs_group.keys()), hole=0.4, title="Распределение затрат группы")
                fig_pie_group.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=300, margin=dict(t=30, b=0, l=0, r=0)) 
                st.plotly_chart(fig_pie_group, use_container_width=True)

            # --- ИНДИВИДУАЛЬНЫЕ КАРТОЧКИ ---
            st.markdown("---")
            st.markdown(f"### ⚙️ Карточки техники ({view_mode})")
            
            for car_name in selected_cars:
                car_row = group_data[group_data["Название_Отображение"] == car_name].iloc[0]
                
                with st.container():
                    st.markdown(f"#### 🔹 {car_row['Название_Отображение']}")
                    
                    c1, c2 = st.columns([1, 1])
                    with c1:
                        st.write(f"**Пробег за период:** {car_row['Пробег_период']:,.0f} км".replace(",", " "))
                        st.write(f"**Потрачено:** {car_row['Итого']:,.0f} ₽".replace(",", " "))
                        st.write(f"**Показатель:** `{car_row['Руб/Км']} руб/км`")
                        
                        if car_row['Руб/Км'] > 3.0:
                            st.error("**Аномальный расход!** Затраты значительно превышают норму.")
                        elif car_row['Тормоза'] > car_row['Итого'] * 0.45:
                            st.warning("**Проблема с тормозами.** Более 45% затрат уходит на этот узел.")
                        elif car_row['ДВС'] > car_row['Итого'] * 0.5:
                            st.warning("**Внимание на двигатель.** Высокая доля затрат на моторный отсек.")
                        else:
                            st.success("**В пределах нормы.** Траты распределены адекватно пробегу.")
                    
                    with c2:
                        costs_car = { "Тормоза": car_row["Тормоза"], "Ходовая": car_row["Ходовая"], "ДВС": car_row["ДВС"], "Электрика": car_row["Электрика"], "Прочее": car_row["Прочее"]}
                        costs_car = {k: v for k, v in costs_car.items() if v > 0}
                        fig_pie_car = px.pie(values=list(costs_car.values()), names=list(costs_car.keys()), hole=0.5)
                        fig_pie_car.update_traces(textposition='inside', textinfo='percent+label')
                        fig_pie_car.update_layout(showlegend=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=250, margin=dict(t=10, b=10, l=10, r=10)) 
                        st.plotly_chart(fig_pie_car, use_container_width=True)
                
                st.markdown("<hr style='border: 1px dashed #e5e7eb;'>", unsafe_allow_html=True)
