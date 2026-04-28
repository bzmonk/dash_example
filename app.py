import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta
import random

# --- НАСТРОЙКИ СТРАНИЦЫ И СТИЛИ ---
st.set_page_config(page_title="AI Аналитика Ремонтов", layout="wide", initial_sidebar_state="collapsed")

# Кастомный CSS для решения проблемы с темной темой и красивого отображения
st.markdown("""
    <style>
    /* Делаем текст на плашках (expander) темно-синим при любой теме */
    div[data-testid="stExpander"] {
        background-color: #f0f2f6 !important;
        border-radius: 15px !important;
        border: 1px solid #d1d5db;
        transition: all 0.3s ease;
    }
    div[data-testid="stExpander"] p, div[data-testid="stExpander"] span {
        color: #1e3a8a !important; /* Темно-синий цвет шрифта */
        font-weight: 600;
    }
    div[data-testid="stExpander"]:hover {
        border-color: #3b82f6;
        box-shadow: 0 4px 10px rgba(255,255,255,0.1);
    }
    .stButton>button {
        border-radius: 10px;
        width: 100%;
        transition: all 0.2s;
        color: #ffffff !important; /* Белый текст на кнопках механиков */
        background-color: #2563eb !important; /* Синие кнопки */
        border: none;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        background-color: #1d4ed8 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- СТРУКТУРА КОМПАНИИ ---
FLEET_STRUCTURE = {
    "Колонна 1": ["Ахметнянов Руслан Равилевич", "Сергиевский Антон Сергеевич"],
    "Колонна 2": ["Галиев Анас Рашитович"],
    "Колонна 3": ["Назаров Андрей Михайлович"],
    "Колонна 4": ["Анисимов Владислав Николаевич", "Захаров Данил Анатольевич"],
    "Колонна 5": ["Захаров Андрей Юрьевич", "Иванов Михаил Сергеевич"],
    "Колонна Перемещение": ["Назаров Андрей Михайлович"]
}

# --- ГЕНЕРАЦИЯ ДАННЫХ (осталась прежней) ---
@st.cache_data
def generate_mechanic_data(mechanic_name):
    np.random.seed(hash(mechanic_name) % 2**32)
    num_cars = np.random.randint(8, 15)
    data = []
    for _ in range(num_cars):
        truck_plate = f"{random.choice(['А','В','Е','К','М','Н','О','Р','С','Т','У','Х'])}{random.randint(100,999)}{random.choice(['АА','ВВ','ЕЕ','КК','ММ'])}{random.choice(['77','777','799','116','163'])}"
        trailer_plate = f"{random.choice(['АА','ВВ','ЕЕ','КК'])}{random.randint(1000,9999)}{random.choice(['77','777','116'])}"
        mileage = random.randint(100000, 800000)
        brakes = random.randint(50000, 400000)
        suspension = random.randint(30000, 250000)
        engine = random.randint(10000, 300000)
        electric = random.randint(5000, 80000)
        trailer_repairs = random.randint(10000, 150000)
        total_cost = brakes + suspension + engine + electric + trailer_repairs
        cpk = round(total_cost / mileage, 2)
        last_repair_date = datetime.now() - timedelta(days=random.randint(1, 45))
        last_repair_cost = random.randint(15000, 120000)
        last_repair_reasons = ["Замена тормозных дисков и колодок", "Ремонт форсунок ДВС", "Переборка суппортов", "Сайлентблоки полурессоры", "Замена датчика NOx", "Диагностика пневмосистемы"]
        last_repair_desc = random.choice(last_repair_reasons)
        data.append({
            "Тягач (Гос. номер)": truck_plate,
            "Прицеп (Гос. номер)": trailer_plate,
            "Пробег": mileage, "Тормозная система": brakes, "Ходовая часть": suspension,
            "ДВС и трансмиссия": engine, "Электрика": electric, "Ремонт прицепа": trailer_repairs,
            "Итого затрат": total_cost, "Руб/Км (CPK)": cpk,
            "Дата последнего ремонта": last_repair_date.strftime("%d.%m.%Y"),
            "Стоимость посл. ремонта": last_repair_cost, "Суть посл. ремонта": last_repair_desc
        })
    df = pd.DataFrame(data)
    df = df.sort_values(by="Руб/Км (CPK)", ascending=False).reset_index(drop=True)
    return df

# --- УПРАВЛЕНИЕ СОСТОЯНИЕМ ---
if 'view' not in st.session_state: st.session_state.view = 'selection'
if 'selected_mechanic' not in st.session_state: st.session_state.selected_mechanic = None
if 'selected_column' not in st.session_state: st.session_state.selected_column = None

def go_to_dashboard(mechanic, column):
    st.session_state.selected_mechanic = mechanic
    st.session_state.selected_column = column
    st.session_state.view = 'dashboard'

def go_to_selection():
    st.session_state.view = 'selection'
    st.session_state.selected_mechanic = None

# =====================================================================
# ЭКРАН 1: ВЫБОР КОЛОННЫ И МЕХАНИКА
# =====================================================================
if st.session_state.view == 'selection':
    
    # --- БЛОК ЗАГОЛОВКА И ЛОГОТИПА ---
    header_col1, header_col2 = st.columns([5, 1]) # Разделяем экран 5 к 1
    
    with header_col1:
        st.title("🏭 Выбор подразделения")
        st.markdown("<p style='color: #888; font-size: 1.1rem;'>Выберите колонну и ответственного механика для анализа рентабельности ремонтов.</p>", unsafe_allow_html=True)
        
    with header_col2:
        # ВНИМАНИЕ: Замени .png на правильное расширение, если у тебя картинка другая (например, .jpg)
        logo_path = r"C:\Users\Danil\Desktop\logo\logo.png" 
        try:
            st.image(logo_path, use_container_width=True)
        except Exception as e:
            st.error("Логотип не найден по указанному пути.")

    st.markdown("---")
    
    # --- МЕНЮ ВЫБОРА ---
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        for column_name, mechanics in FLEET_STRUCTURE.items():
            with st.expander(f"📁 {column_name}", expanded=False):
                st.write("**Ответственные механики:**")
                for mech in mechanics:
                    if st.button(f"👤 {mech}", key=f"btn_{column_name}_{mech}"):
                        go_to_dashboard(mech, column_name)
                        st.rerun()

# =====================================================================
# ЭКРАН 2: ДАШБОРД (остался прежним, только добавил логотип на этот экран тоже)
# =====================================================================
elif st.session_state.view == 'dashboard':
    mechanic = st.session_state.selected_mechanic
    column = st.session_state.selected_column
    
    header_col1, header_col2 = st.columns([5, 1])
    with header_col1:
        if st.button("⬅ Назад к выбору колонны"):
            go_to_selection()
            st.rerun()
        st.title(f"🛠️ Аналитика ремонтов: {mechanic}")
        st.caption(f"Подразделение: {column}")
    with header_col2:
        try:
            st.image(r"C:\Users\Danil\Desktop\logo\logo.png", use_container_width=True)
        except:
            pass
            
    df = generate_mechanic_data(mechanic)
    
    # --- KPI БЛОК ДЛЯ РУКОВОДИТЕЛЯ ---
    st.markdown("### 📊 Общая сводка (Executive Summary)")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Машин в парке", len(df))
    kpi2.metric("Суммарные затраты", f"{df['Итого затрат'].sum():,.0f} ₽".replace(',', ' '))
    kpi3.metric("Средний показатель руб/км", f"{df['Руб/Км (CPK)'].mean():.2f} ₽")
    sum_costs = df[['Тормозная система', 'Ходовая часть', 'ДВС и трансмиссия', 'Электрика', 'Ремонт прицепа']].sum()
    kpi4.metric("Главная статья расходов", sum_costs.idxmax())
    st.markdown("---")
    
    # --- ТОП ПРОБЛЕМНЫХ АВТОМОБИЛЕЙ ---
    st.markdown("### 🚨 Проблемные автомобили (Антирейтинг по стоимости 1 км пути)")
    st.info("💡 ИИ-совет: Нормальный показатель CPK (затраты на ремонт / пробег) не должен превышать 1.5 - 2.0 руб/км. Машины в красной зоне работают в убыток или требуют капитального пересмотра логики обслуживания.")
    
    fig_bar = px.bar(
        df.head(5), x="Тягач (Гос. номер)", y="Руб/Км (CPK)", color="Руб/Км (CPK)",
        text="Итого затрат", color_continuous_scale="Reds"
    )
    fig_bar.update_traces(texttemplate='%{text:,.0f} ₽', textposition='outside')
    st.plotly_chart(fig_bar, use_container_width=True)
    
    # --- ДЕТАЛЬНЫЙ РАЗБОР КОНКРЕТНОЙ МАШИНЫ ---
    st.markdown("### 🔍 Детальный аудит сцепки")
    selected_truck = st.selectbox("Выберите сцепку для детального анализа:", df["Тягач (Гос. номер)"])
    car_data = df[df["Тягач (Гос. номер)"] == selected_truck].iloc[0]
    col_info, col_chart = st.columns([1, 1.2])
    
    with col_info:
        st.markdown(f"#### Сцепка: `{car_data['Тягач (Гос. номер)']} / {car_data['Прицеп (Гос. номер)']}`")
        st.write(f"**Пробег:** {car_data['Пробег']:,.0f} км".replace(',', ' '))
        st.write(f"**Показатель:** `{car_data['Руб/Км (CPK)']} руб/км`")
        st.markdown("##### 🕒 Последний визит в сервис:")
        st.write(f"**Дата:** {car_data['Дата последнего ремонта']}")
        st.write(f"**Стоимость:** {car_data['Стоимость посл. ремонта']:,.0f} ₽".replace(',', ' '))
        st.write(f"**Работы:** *{car_data['Суть посл. ремонта']}*")
        st.markdown("##### 🤖 Вывод AI-Аналитика:")
        
        if car_data['Тормозная система'] > car_data['Итого затрат'] * 0.4:
            st.warning("**Диагноз:** Аномальные расходы на тормозную систему.\n\n**Меры:** Проверить ретардер, выгрузить лог вождения из телематики, проверить бренд колодок.")
        elif car_data['Ремонт прицепа'] > car_data['Итого затрат'] * 0.3:
            st.error("**Диагноз:** Перерасход бюджета на прицеп.\n\n**Меры:** Обязательная проверка геометрии осей (соосность), диагностика ABS/EBS прицепа.")
        elif car_data['Руб/Км (CPK)'] > 2.5 and car_data['Пробег'] > 500000:
            st.error(f"**Диагноз:** Автомобиль исчерпал ресурс (CPK = {car_data['Руб/Км (CPK)']}).\n\n**Меры:** Подготовить расчет TCO и сравнить с лизингом нового тягача.")
        else:
            st.success("**Диагноз:** Штатная эксплуатация.\n\n**Меры:** Плановое ТО. Обратить внимание на превентивную замену ремней навесного оборудования.")

    with col_chart:
        costs = {"Тормоза": car_data["Тормозная система"], "Ходовая": car_data["Ходовая часть"], "ДВС/КПП": car_data["ДВС и трансмиссия"], "Электрика": car_data["Электрика"], "Прицеп": car_data["Ремонт прицепа"]}
        pie_df = pd.DataFrame(list(costs.items()), columns=["Категория", "Сумма"])
        fig_pie = px.pie(pie_df, values="Сумма", names="Категория", hole=0.5, color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)") 
        st.plotly_chart(fig_pie, use_container_width=True)