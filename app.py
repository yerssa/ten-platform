import streamlit as st
import pandas as pd
import numpy as np
import random
import datetime
import json
import os
import streamlit.components.v1 as components

try:
    from fpdf import FPDF
    HAS_FPDF = True
except ImportError:
    HAS_FPDF = False

# ==========================================
# ТРАНСЛИТЕРАЦИЯ
# ==========================================
def transliterate(text):
    cyrillic_to_latin = {
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'E', 'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Shch', 'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya',
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e', 'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
        'Қ': 'Q', 'қ': 'q', 'Ң': 'N', 'ң': 'n', 'Ғ': 'Gh', 'ғ': 'gh', 'Ү': 'U', 'ү': 'u', 'Ұ': 'U', 'ұ': 'u', 'Ө': 'O', 'ө': 'o', 'Ә': 'A', 'ә': 'a', 'І': 'I', 'і': 'i'
    }
    return ''.join(cyrillic_to_latin.get(c, c) for c in text)

# ==========================================
# МУЛЬТИЯЗЫЧНОСТЬ
# ==========================================
UI = {
    "RU": {
        "title": "TEN",
        "subtitle": "Интеллектуальная олимпиада",
        "name_input": "Введите ваше имя",
        "login_btn": "Войти в систему",
        "logout": "Выйти",
        "dash": "Платформа",
        "logic": "TEN LOGIC",
        "math": "TEN MATH",
        "certs": "Рейтинг и Сертификаты",
        "welcome": "С возвращением",
        "score": "Ваш балл TEN",
        "rank": "Глобальный рейтинг",
        "best_cat": "Лучшая категория",
        "achievements": "Ваши достижения",
        "start_logic": "Начать TEN LOGIC",
        "start_mod1": "Начать Module 1",
        "start_mod2": "Начать Module 2 🔓",
        "start_mod3": "Начать Module 3 🔓",
        "randomize": "🔄 Перемешать",
        "submit": "Отправить ответы",
        "completed": "✅ Завершено!",
        "not_tested": "Не сдавал",
        "leaderboard": "Таблица лидеров",
        "cert_title": "Официальный сертификат",
        "locked": "🔒 ПРОЙДИТЕ ВСЕ ТЕСТЫ ДЛЯ ПОЛУЧЕНИЯ СЕРТИФИКАТА",
        "download_cert": "Скачать PDF Сертификат",
        "answer": "Ответ:",
        "participant": "Участник",
        "total_score": "Общий балл",
        "no_users": "Пока нет участников.",
        "time": "Время:",
        "time_up": "ВРЕМЯ ВЫШЛО!",
        "rand_success": "Вопросы перемешаны!"
    },
    "EN": {
        "title": "TEN",
        "subtitle": "Next-Gen Olympiad",
        "name_input": "Enter your name",
        "login_btn": "Sign In",
        "logout": "Log Out",
        "dash": "Platform",
        "logic": "TEN LOGIC",
        "math": "TEN MATH",
        "certs": "Leaderboard & Certs",
        "welcome": "Welcome back",
        "score": "Your TEN Score",
        "rank": "Global Rank",
        "best_cat": "Best Category",
        "achievements": "Your Achievements",
        "start_logic": "Start TEN LOGIC",
        "start_mod1": "Start Module 1",
        "start_mod2": "Start Module 2 🔓",
        "start_mod3": "Start Module 3 🔓",
        "randomize": "🔄 Randomize",
        "submit": "Submit Answers",
        "completed": "✅ Completed!",
        "not_tested": "Not tested",
        "leaderboard": "Leaderboard",
        "cert_title": "Official Certificate",
        "locked": "🔒 COMPLETE ALL TESTS TO UNLOCK CERTIFICATE",
        "download_cert": "Download PDF Certificate",
        "answer": "Answer:",
        "participant": "Participant",
        "total_score": "Total Score",
        "no_users": "No participants yet.",
        "time": "Time:",
        "time_up": "TIME UP!",
        "rand_success": "Questions randomized!"
    }
}

QUIZ_DATA = {
    "RU": {
        "logic": [
            {"q": "В исследовании 80% участников, которые пьют кофе каждый день, сообщили о высокой продуктивности. Какой вывод наиболее обоснован?", "opts": ["Кофе повышает продуктивность.", "Продуктивные люди чаще пьют кофе.", "Между употреблением кофе и продуктивностью есть связь, но причинность не доказана.", "Кофе никак не связан с продуктивностью."], "ans_idx": 2},
            {"q": "«Мой дедушка курил всю жизнь и прожил до 90 лет. Поэтому курение не обязательно вредно». Какая ошибка здесь допущена?", "opts": ["«Твой дедушка просто был исключением».", "Это доказывает, что курение безопасно.", "Один пример не отменяет статистические данные.", "Значит, всё зависит только от генетики."], "ans_idx": 2},
            {"q": "Человек говорит: «Этот план либо сработает, либо полностью провалится». Что стоит поставить под сомнение?", "opts": ["Сам план", "Его уверенность", "Предположение, что существует только два результата", "Его опыт"], "ans_idx": 2},
            {"q": "Если два сайта дают разную информацию, что лучше сделать?", "opts": ["Выбрать тот, который первым появился", "Выбрать тот, который нравится", "Проверить несколько надёжных источников", "Выбрать тот, где звучит убедительнее"], "ans_idx": 2},
            {"q": "Если человек сделал правильный поступок, но только потому, что боялся наказания — можно ли назвать его поступок моральным?", "opts": ["Да", "Нет", "Зависит от ситуации", "Важнее результат, чем причина"], "ans_idx": 1},
            {"q": "Что важнее при принятии решения: намерение человека или последствия его поступка?", "opts": ["Намерение", "Последствия", "Оба одинаково важны", "Зависит от ситуации"], "ans_idx": 2},
            {"q": "Если большинство людей уверены в чём-то, но у одного человека есть доказательства обратного — кому ты поверишь?", "opts": ["Большинству", "Одному человеку", "Тому, у кого сильнее доказательства", "Никому"], "ans_idx": 2},
            {"q": "Если невозможно доказать, что утверждение ложно, означает ли это, что оно может считаться истинным?", "opts": ["Да", "Нет, отсутствие опровержения не является доказательством", "Иногда", "Если большинство верит"], "ans_idx": 1},
            {"q": "Что сильнее влияет на убеждения человека?", "opts": ["Факты", "Личный опыт", "Окружение", "Всё перечисленное"], "ans_idx": 3},
            {"q": "Если человек изменил своё мнение после появления новых доказательств, это скорее говорит о том, что он:", "opts": ["Не уверен в себе", "Непостоянен", "Способен критически пересматривать свои убеждения", "Не имеет позиции"], "ans_idx": 2}
        ],
        "mod1": [
            {"q": "Если $3x - y = 12$ и $y = 3$, чему равно $x$?", "opts": ["3", "4", "5", "6"], "ans_idx": 2},
            {"q": "Чему равно 15% от 80?", "opts": ["10", "12", "15", "18"], "ans_idx": 1},
            {"q": "В прямоугольном треугольнике один острый угол равен 35°. Чему равен второй острый угол?", "opts": ["45°", "55°", "65°", "90°"], "ans_idx": 1}
        ],
        "mod2h": [
            {"q": "Если $f(x) = x^2 - 4x + 3$, чему равно $f(2)$?", "opts": ["-1", "0", "1", "3"], "ans_idx": 0},
            {"q": "Система уравнений: $x + y = 10$ и $x - y = 2$. Найдите значение $x \cdot y$.", "opts": ["16", "20", "24", "25"], "ans_idx": 2},
            {"q": "Площадь круга равна 49π. Чему равна длина его окружности?", "opts": ["7π", "14π", "21π", "49π"], "ans_idx": 1}
        ],
        "mod2e": [
            {"q": "Если $2x = 10$, чему равно $x + 3$?", "opts": ["5", "8", "10", "13"], "ans_idx": 1},
            {"q": "Чему равен периметр прямоугольника с длиной 5 и шириной 3?", "opts": ["8", "15", "16", "20"], "ans_idx": 2},
            {"q": "Упростите: $3x + 2y - x + 4y$", "opts": ["2x + 6y", "4x + 6y", "2x + 2y", "x + y"], "ans_idx": 0}
        ],
        "mod3": [
            {"q": "Если $x^2 + y^2 = 25$ и $xy = 12$, чему равно значение $(x+y)^2$?", "opts": ["37", "49", "60", "144"], "ans_idx": 1},
            {"q": "Объем шара равен $36\pi$. Чему равен его радиус?", "opts": ["2", "3", "4", "6"], "ans_idx": 1},
            {"q": "Если $3^{x+1} = 81$, чему равно $x$?", "opts": ["2", "3", "4", "5"], "ans_idx": 1}
        ]
    },
    "EN": {
        "logic": [
            {"q": "In a study, 80% of participants who drink coffee daily reported high productivity. Which conclusion is most justified?", "opts": ["Coffee increases productivity.", "Productive people drink coffee more often.", "There is a correlation between coffee and productivity, but causation is not proven.", "Coffee is not related to productivity."], "ans_idx": 2},
            {"q": "«My grandfather smoked his whole life and lived to 90. Therefore, smoking is not necessarily harmful.» What is the error here?", "opts": ["«Your grandfather was just an exception.»", "This proves that smoking is safe.", "A single example does not invalidate statistical data.", "It means everything depends only on genetics."], "ans_idx": 2},
            {"q": "A person says: «This plan will either work perfectly or fail completely.» What should be questioned?", "opts": ["The plan itself", "His confidence", "The assumption that there are only two outcomes", "His experience"], "ans_idx": 2},
            {"q": "If two websites provide different information, what is the best course of action?", "opts": ["Choose the one that appeared first", "Choose the one you like more", "Check multiple reliable sources", "Choose the one that sounds more convincing"], "ans_idx": 2},
            {"q": "If a person did the right thing only because they feared punishment, can their action be considered moral?", "opts": ["Yes", "No", "Depends on the situation", "The result is more important than the reason"], "ans_idx": 1},
            {"q": "What is more important when making a decision: a person's intention or the consequences of their action?", "opts": ["Intention", "Consequences", "Both are equally important", "Depends on the situation"], "ans_idx": 2},
            {"q": "If most people are certain of something, but one person has evidence to the contrary, who would you believe?", "opts": ["The majority", "The one person", "The one with stronger evidence", "No one"], "ans_idx": 2},
            {"q": "If it is impossible to prove a statement false, does that mean it can be considered true?", "opts": ["Yes", "No, the absence of refutation is not proof", "Sometimes", "If the majority believes it"], "ans_idx": 1},
            {"q": "What has the strongest influence on a person's beliefs?", "opts": ["Facts", "Personal experience", "Environment", "All of the above"], "ans_idx": 3},
            {"q": "If a person changes their mind after new evidence appears, this most likely indicates that they are:", "opts": ["Insecure", "Inconsistent", "Capable of critically revising their beliefs", "Without a firm position"], "ans_idx": 2}
        ],
        "mod1": [
            {"q": "If $3x - y = 12$ and $y = 3$, what is the value of $x$?", "opts": ["3", "4", "5", "6"], "ans_idx": 2},
            {"q": "What is 15% of 80?", "opts": ["10", "12", "15", "18"], "ans_idx": 1},
            {"q": "In a right triangle, one acute angle is 35°. What is the other acute angle?", "opts": ["45°", "55°", "65°", "90°"], "ans_idx": 1}
        ],
        "mod2h": [
            {"q": "If $f(x) = x^2 - 4x + 3$, what is $f(2)$?", "opts": ["-1", "0", "1", "3"], "ans_idx": 0},
            {"q": "System of equations: $x + y = 10$ and $x - y = 2$. Find the value of $x \cdot y$.", "opts": ["16", "20", "24", "25"], "ans_idx": 2},
            {"q": "A circle has an area of 49π. What is its circumference?", "opts": ["7π", "14π", "21π", "49π"], "ans_idx": 1}
        ],
        "mod2e": [
            {"q": "If $2x = 10$, what is $x + 3$?", "opts": ["5", "8", "10", "13"], "ans_idx": 1},
            {"q": "What is the perimeter of a rectangle with length 5 and width 3?", "opts": ["8", "15", "16", "20"], "ans_idx": 2},
            {"q": "Simplify: $3x + 2y - x + 4y$", "opts": ["2x + 6y", "4x + 6y", "2x + 2y", "x + y"], "ans_idx": 0}
        ],
        "mod3": [
            {"q": "If $x^2 + y^2 = 25$ and $xy = 12$, what is the value of $(x+y)^2$?", "opts": ["37", "49", "60", "144"], "ans_idx": 1},
            {"q": "A sphere has a volume of $36\pi$. What is its radius?", "opts": ["2", "3", "4", "6"], "ans_idx": 1},
            {"q": "If $3^{x+1} = 81$, what is $x$?", "opts": ["2", "3", "4", "5"], "ans_idx": 1}
        ]
    }
}

# ==========================================
# ДЕРЕКТЕР БАЗАСЫ
# ==========================================
DB_FILE = "ten_database.json"

def init_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w', encoding='utf-8') as f: 
            json.dump({"users": {}, "logs": []}, f, ensure_ascii=False, indent=4)

def load_db():
    init_db()
    with open(DB_FILE, 'r', encoding='utf-8') as f: db = json.load(f)
    fake_users = ["Ayan", "Dias", "Alikhan", "НУ"]
    changed = False
    for fake in fake_users:
        if fake in db.get("users", {}):
            del db["users"][fake]
            changed = True
    if changed: save_db(db)
    return db

def save_db(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f: 
        json.dump(data, f, ensure_ascii=False, indent=4)

def log_action(username, action):
    db = load_db()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db["logs"].insert(0, {"Уақыты": timestamp, "Қолданушы": username, "Әрекет": action})
    save_db(db)

def update_user_score(username, logic, math_score, total):
    db = load_db()
    if total == 0 and username in db.get("users", {}): pass 
    else:
        db["users"][username] = {"logic": logic, "math": math_score, "total": total}
        save_db(db)

# ==========================================
# БАПТАУЛАР МЕН ДИЗАЙН (PREMIUM DARK UI CSS)
# ==========================================
st.set_page_config(page_title="TEN Platform", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* Глобальный фон и текст */
    [data-testid="stAppViewContainer"] { background-color: #000000; color: #ffffff; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #09090b !important; border-right: 1px solid #27272a; }
    
    /* Заголовки */
    h1, h2, h3, p, label, span { color: #ffffff !important; }
    
    /* Карточки (Метрики и формы) */
    [data-testid="stMetric"], .stForm, .css-1r6slb0, [data-testid="stExpander"] {
        background-color: #141415 !important;
        border: 1px solid #27272a !important;
        border-radius: 12px !important;
        padding: 15px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5);
    }
    
    /* Стили кнопок (Белый премиум-стиль как на макете) */
    .stButton > button, .stDownloadButton > button { 
        background-color: #ffffff !important; 
        border: none !important;
        border-radius: 8px !important; 
        width: 100% !important; 
        padding: 12px !important;
        transition: 0.3s;
    }
    .stButton > button *, .stDownloadButton > button * {
        color: #000000 !important;
        font-weight: 600 !important;
    }
    .stButton > button:hover, .stDownloadButton > button:hover { 
        background-color: #e4e4e7 !important; 
        transform: translateY(-2px);
    }
    
    /* Вторичные кнопки (Перемешать и тд) */
    .stButton[data-testid="stButton"] button:nth-of-type(2) {
        background-color: #27272a !important;
    }
    .stButton[data-testid="stButton"] button:nth-of-type(2) * {
        color: #ffffff !important;
    }

    /* Инпуты */
    .stTextInput>div>div>input { 
        background-color: #000000 !important; 
        color: #ffffff !important; 
        border: 1px solid #27272a !important; 
        border-radius: 8px !important; 
        padding: 10px !important;
    }
    
    /* Таблицы */
    [data-testid="stDataFrame"] { background-color: #141415; border-radius: 12px; border: 1px solid #27272a; }
    
    /* Меню навигации Sidebar (Radio buttons) */
    div[role="radiogroup"] > label {
        padding: 10px 15px;
        background-color: transparent;
        border-radius: 8px;
        transition: 0.2s;
        margin-bottom: 5px;
    }
    div[role="radiogroup"] > label:hover { background-color: #27272a; }
    div[role="radiogroup"] > label[data-checked="true"] {
        background-color: #ffffff;
    }
    div[role="radiogroup"] > label[data-checked="true"] p {
        color: #000000 !important;
        font-weight: bold;
    }
    
    /* Убрать верхний отступ */
    .block-container { padding-top: 2rem !important; }
    header {visibility: hidden;} footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# СЕССИЯ ЖАДЫ
# ==========================================
if 'lang' not in st.session_state: st.session_state.lang = "RU"
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'is_admin' not in st.session_state: st.session_state.is_admin = False
if 'user_name' not in st.session_state: st.session_state.user_name = ""
if 'cert_id' not in st.session_state: st.session_state.cert_id = f"TEN-2026-{random.randint(10000,99999)}"

if 'logic_started' not in st.session_state: st.session_state.logic_started = False
if 'logic_submitted' not in st.session_state: st.session_state.logic_submitted = False
if 'logic_score_100' not in st.session_state: st.session_state.logic_score_100 = 0.0

if 'math_mod1_started' not in st.session_state: st.session_state.math_mod1_started = False
if 'math_mod1_submitted' not in st.session_state: st.session_state.math_mod1_submitted = False
if 'math_mod1_score' not in st.session_state: st.session_state.math_mod1_score = 0
if 'math_mod2_started' not in st.session_state: st.session_state.math_mod2_started = False
if 'math_mod2_submitted' not in st.session_state: st.session_state.math_mod2_submitted = False
if 'math_mod2_score' not in st.session_state: st.session_state.math_mod2_score = 0
if 'math_mod2_type' not in st.session_state: st.session_state.math_mod2_type = "Hard"
if 'math_mod3_started' not in st.session_state: st.session_state.math_mod3_started = False
if 'math_mod3_submitted' not in st.session_state: st.session_state.math_mod3_submitted = False
if 'math_mod3_score' not in st.session_state: st.session_state.math_mod3_score = 0
if 'math_total_score_100' not in st.session_state: st.session_state.math_total_score_100 = 0.0

if 'seeds' not in st.session_state:
    st.session_state.seeds = {
        'logic': random.randint(1, 10000), 'mod1': random.randint(1, 10000),
        'mod2h': random.randint(1, 10000), 'mod2e': random.randint(1, 10000), 'mod3': random.randint(1, 10000)
    }

def get_shuffled_quiz(quiz_type, lang):
    rng = random.Random(st.session_state.seeds[quiz_type])
    questions = QUIZ_DATA[lang][quiz_type][:]
    q_objs = []
    for q in questions:
        opts = q["opts"][:]
        ans_text = opts[q["ans_idx"]]
        rng.shuffle(opts)
        q_objs.append({"q": q["q"], "options": opts, "answer": ans_text})
    rng.shuffle(q_objs)
    return q_objs

def reroll_seed(quiz_type):
    st.session_state.seeds[quiz_type] = random.randint(1, 10000)

# ==========================================
# 1. АВТОРИЗАЦИЯ (LOGIN MODAL STYLE)
# ==========================================
if not st.session_state.logged_in:
    col_lang, _ = st.columns([1, 7])
    with col_lang:
        st.session_state.lang = st.selectbox("🌐", ["RU", "EN"], label_visibility="collapsed")
    
    t = UI[st.session_state.lang]
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown(f"<h1 style='text-align: center; font-size: 3rem;'>🧠 {t['title']}</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: #a1a1aa !important;'>{t['subtitle']}</p><br>", unsafe_allow_html=True)
        
        name = st.text_input(t["name_input"], placeholder="Иван Иванов")
        if st.button(t["login_btn"]):
            if name:
                if name.strip().upper() == "TEN10Y":
                    st.session_state.is_admin = True
                    st.session_state.user_name = "FOUNDER"
                    log_action("FOUNDER", "Admin logged in")
                else:
                    st.session_state.is_admin = False
                    st.session_state.user_name = name.strip()
                    log_action(st.session_state.user_name, "User logged in")
                st.session_state.logged_in = True
                st.rerun()

# ==========================================
# 2. ОСНОВАТЕЛЬ КАБИНЕТІ (АДМИН)
# ==========================================
elif st.session_state.is_admin:
    st.sidebar.markdown("### 👑 FOUNDER")
    if st.sidebar.button("LOGOUT"):
        st.session_state.clear()
        st.rerun()

    st.title("👑 FOUNDER DASHBOARD")
    db = load_db()
    tab_users, tab_logs = st.tabs(["👥 Users", "🕵️ Logs"])
    with tab_users:
        if db.get("users"):
            users_list = [{"Participant": u, "TEN LOGIC (40%)": d["logic"], "TEN MATH (60%)": d["math"], "Total Score": d["total"]} for u, d in db["users"].items()]
            df_users = pd.DataFrame(users_list).sort_values(by="Total Score", ascending=False).reset_index(drop=True)
            df_users.insert(0, 'Rank', [f"#{i+1}" for i in range(len(df_users))])
            st.dataframe(df_users, use_container_width=True, hide_index=True)
    with tab_logs:
        if db.get("logs"): st.dataframe(pd.DataFrame(db["logs"]), use_container_width=True, hide_index=True)

# ==========================================
# 3. ПЛАТФОРМА (УЧАСТНИКИ) - MODERN UI
# ==========================================
else:
    t = UI[st.session_state.lang]
    
    # Подсчет баллов
    user_logic_score = round(st.session_state.logic_score_100, 1)
    user_math_score = round(st.session_state.math_total_score_100, 1)
    raw_total = (user_logic_score * 0.4) + (user_math_score * 0.6) if user_math_score > 0 else (user_logic_score * 0.4)
    total_score = round(raw_total, 1)

    current_user_name = st.session_state.user_name
    update_user_score(current_user_name, user_logic_score, user_math_score, total_score)
    
    db = load_db()
    users_list = [{t["participant"]: u, "TEN LOGIC": d["logic"], "TEN MATH": d["math"], t["total_score"]: d["total"]} for u, d in db.get("users", {}).items()]
    ld_data = pd.DataFrame(users_list).sort_values(by=t["total_score"], ascending=False).reset_index(drop=True)
    
    if not ld_data.empty:
        ld_data.insert(0, 'Rank', [f"#{i+1}" for i in range(len(ld_data))])
        user_idx_list = ld_data[ld_data[t["participant"]] == current_user_name].index
        user_idx = user_idx_list[0] if len(user_idx_list) > 0 else 0
        
        if total_score == 0.0:
            rank_display = "—"
        else:
            rank_percent = max(1, round(((user_idx + 1) / len(ld_data)) * 100))
            rank_display = f"#{user_idx + 1} (Top {rank_percent}%)"
    else:
        rank_display = "—"

    # --- SIDEBAR MODERN ---
    with st.sidebar:
        st.markdown("<h2 style='margin-bottom: 20px;'>🧠 TEN</h2>", unsafe_allow_html=True)
        nav_choice = st.radio("Меню", [t["dash"], t["logic"], t["math"], t["certs"]], label_visibility="collapsed")
        
        st.markdown("<div style='margin-top: 50vh;'></div>", unsafe_allow_html=True)
        st.markdown(f"<div style='padding: 10px; background: #141415; border-radius: 8px; border: 1px solid #27272a;'>👤 {current_user_name}</div>", unsafe_allow_html=True)
        if st.button(t["logout"]):
            log_action(current_user_name, "Logout")
            st.session_state.clear()
            st.rerun()

    # --- МЕНЮ 1: ПЛАТФОРМА (DASHBOARD) ---
    if nav_choice == t["dash"]:
        st.markdown(f"<h1 style='font-size: 2.2rem;'>{t['welcome']}, {current_user_name} 👋</h1>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        col1.metric(t["score"], f"{total_score} / 100")
        col2.metric(t["rank"], rank_display)
        
        st.markdown("<br><h3 style='color: #a1a1aa !important; font-size: 1.2rem;'>Доступные экзамены</h3>", unsafe_allow_html=True)
        
        # Карточка TEN LOGIC
        st.markdown("""
        <div style="background: linear-gradient(145deg, #18181b, #09090b); border: 1px solid #27272a; border-radius: 12px; padding: 20px; margin-bottom: 15px;">
            <h2>🧩 TEN LOGIC</h2>
            <p style="color: #a1a1aa !important;">Тест на критическое мышление и логический анализ.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Карточка TEN MATH
        st.markdown("""
        <div style="background: linear-gradient(145deg, #18181b, #09090b); border: 1px solid #27272a; border-radius: 12px; padding: 20px;">
            <h2>📐 TEN MATH</h2>
            <p style="color: #a1a1aa !important;">Адаптивное тестирование по математике (Modules 1-3).</p>
        </div>
        """, unsafe_allow_html=True)

    # --- МЕНЮ 2: TEN LOGIC ---
    elif nav_choice == t["logic"]:
        st.markdown("<h1>🧩 TEN LOGIC</h1>", unsafe_allow_html=True)
        if not st.session_state.logic_started:
            col_btn1, col_btn2 = st.columns([1,3])
            with col_btn1:
                if st.button(t["start_logic"]):
                    st.session_state.logic_started = True
                    st.rerun()
            with col_btn2:
                if st.button(t["randomize"], key="rand_log"):
                    reroll_seed('logic')
                    st.success(t["rand_success"])
                    
        elif not st.session_state.logic_submitted:
            components.html(
                f"""
                <div id="ltimer" style="font-family: 'Inter', sans-serif; font-size: 18px; font-weight: bold; color: #fff; background: #141415; border: 1px solid #27272a; border-radius: 8px; padding: 10px; width: 150px; text-align: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.5);">15:00</div>
                <script>
                    var time = 900;
                    var timer = setInterval(function() {{
                        var m = Math.floor(time / 60); var s = time % 60;
                        document.getElementById("ltimer").innerHTML = "{t['time']} " + m + ":" + (s<10?"0":"") + s;
                        time--;
                        if (time < 0) {{ clearInterval(timer); document.getElementById("ltimer").innerHTML = "{t['time_up']}"; }}
                    }}, 1000);
                </script>
                """, height=50
            )
            with st.form("logic_form"):
                answers = []
                quiz_list = get_shuffled_quiz('logic', st.session_state.lang)
                for i, q in enumerate(quiz_list):
                    st.markdown(f"<b>{i+1}. {q['q']}</b>", unsafe_allow_html=True)
                    ans = st.radio(t["answer"], q['options'], key=f"logic_q_{i}", label_visibility="collapsed", index=None)
                    answers.append((ans, q['answer']))
                    st.markdown("<hr style='border-color: #27272a;'>", unsafe_allow_html=True)
                if st.form_submit_button(t["submit"]):
                    correct = sum(1 for a, truth in answers if a and truth in a)
                    st.session_state.logic_score_100 = (correct / len(quiz_list)) * 100
                    st.session_state.logic_submitted = True
                    st.rerun()
        else: 
            st.success(t["completed"])
            st.markdown(f"<h2 style='text-align:center;'>SCORE: {user_logic_score} / 100</h2>", unsafe_allow_html=True)

    # --- МЕНЮ 3: TEN MATH ---
    elif nav_choice == t["math"]:
        st.markdown("<h1>📐 TEN MATH</h1>", unsafe_allow_html=True)
        if not st.session_state.math_mod1_started:
            col_btn1, col_btn2 = st.columns([1,3])
            with col_btn1:
                if st.button(t["start_mod1"]):
                    st.session_state.math_mod1_started = True
                    st.rerun()
            with col_btn2:
                if st.button(t["randomize"], key="rand_math"):
                    reroll_seed('mod1')
                    reroll_seed('mod2h')
                    reroll_seed('mod2e')
                    reroll_seed('mod3')
                    st.success(t["rand_success"])
                    
        elif not st.session_state.math_mod1_submitted:
            with st.form("mod1_form"):
                ans1 = []
                quiz_mod1 = get_shuffled_quiz('mod1', st.session_state.lang)
                for i, q in enumerate(quiz_mod1):
                    st.write(f"**{i+1}. {q['q']}**")
                    ans = st.radio(t["answer"], q['options'], key=f"m1_{i}", label_visibility="collapsed", index=None)
                    ans1.append((ans, q['answer']))
                    st.markdown("<hr style='border-color: #27272a;'>", unsafe_allow_html=True)
                if st.form_submit_button(t["submit"]):
                    corr = sum(1 for a, truth in ans1 if a and truth in a)
                    st.session_state.math_mod1_score = corr
                    st.session_state.math_mod1_submitted = True
                    if corr >= 2: st.session_state.math_mod2_type = "Hard"
                    else: st.session_state.math_mod2_type = "Easy"
                    st.rerun()
        else:
            st.success(f"✅ Module 1 Completed! Score: {st.session_state.math_mod1_score}")
            if not st.session_state.math_mod2_started:
                if st.button(t["start_mod2"]):
                    st.session_state.math_mod2_started = True
                    st.rerun()
            elif not st.session_state.math_mod2_submitted:
                with st.form("mod2_form"):
                    ans2 = []
                    t_type = 'mod2h' if st.session_state.math_mod2_type == "Hard" else 'mod2e'
                    quiz_mod2 = get_shuffled_quiz(t_type, st.session_state.lang)
                    for i, q in enumerate(quiz_mod2):
                        st.write(f"**{i+1}. {q['q']}**")
                        ans = st.radio(t["answer"], q['options'], key=f"m2_{i}", label_visibility="collapsed", index=None)
                        ans2.append((ans, q['answer']))
                        st.markdown("<hr style='border-color: #27272a;'>", unsafe_allow_html=True)
                    if st.form_submit_button(t["submit"]):
                        st.session_state.math_mod2_score = sum(1 for a, truth in ans2 if a and truth in a)
                        st.session_state.math_mod2_submitted = True
                        st.rerun()
            else:
                st.success(f"✅ Module 2 Completed! Score: {st.session_state.math_mod2_score}")
                if not st.session_state.math_mod3_started:
                    if st.button(t["start_mod3"]):
                        st.session_state.math_mod3_started = True
                        st.rerun()
                elif not st.session_state.math_mod3_submitted:
                    with st.form("mod3_form"):
                        ans3 = []
                        quiz_mod3 = get_shuffled_quiz('mod3', st.session_state.lang)
                        for i, q in enumerate(quiz_mod3):
                            st.write(f"**{i+1}. {q['q']}**")
                            ans = st.radio(t["answer"], q['options'], key=f"m3_{i}", label_visibility="collapsed", index=None)
                            ans3.append((ans, q['answer']))
                            st.markdown("<hr style='border-color: #27272a;'>", unsafe_allow_html=True)
                        if st.form_submit_button(t["submit"]):
                            st.session_state.math_mod3_score = sum(1 for a, truth in ans3 if a and truth in a)
                            st.session_state.math_mod3_submitted = True
                            tot = st.session_state.math_mod1_score + st.session_state.math_mod2_score + st.session_state.math_mod3_score
                            total_q = len(QUIZ_DATA[st.session_state.lang]['mod1']) + len(QUIZ_DATA[st.session_state.lang]['mod2h']) + len(QUIZ_DATA[st.session_state.lang]['mod3'])
                            st.session_state.math_total_score_100 = (tot / total_q) * 100
                            st.rerun()
                else:
                    st.success(t["completed"])
                    st.markdown(f"<h2 style='text-align:center;'>SCORE: {user_math_score} / 100</h2>", unsafe_allow_html=True)

    # --- МЕНЮ 4: РЕЙТИНГ И СЕРТИФИКАТ ---
    elif nav_choice == t["certs"]:
        st.markdown("<h1>🏆 Рейтинг и Сертификаты</h1>", unsafe_allow_html=True)
        col_lead, col_stats = st.columns([1.5, 1])
        
        with col_lead:
            st.markdown(f"<h3 style='color: #a1a1aa !important; font-size: 1.2rem;'>{t['leaderboard']}</h3>", unsafe_allow_html=True)
            if not ld_data.empty: 
                st.dataframe(ld_data, hide_index=True, use_container_width=True)
            else: 
                st.info(t["no_users"])
            
        with col_stats:
            st.markdown(f"<h3 style='color: #a1a1aa !important; font-size: 1.2rem;'>{t['cert_title']}</h3>", unsafe_allow_html=True)
            if not st.session_state.logic_submitted or not st.session_state.math_mod3_submitted:
                st.markdown(f"""
                <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444; border-radius: 8px; padding: 15px; color: #fca5a5;">
                    {t['locked']}
                </div>
                """, unsafe_allow_html=True)
            else:
                if not HAS_FPDF: st.error("pip install fpdf")
                else:
                    def create_pdf(name, logic, math_val, total, cert_id, rank):
                        pdf = FPDF(orientation='L', unit='mm', format='A4')
                        pdf.add_page()
                        pdf.set_draw_color(212, 175, 55)
                        pdf.set_line_width(2)
                        pdf.rect(10, 10, 277, 190)
                        pdf.set_draw_color(30, 30, 30)
                        pdf.set_line_width(0.5)
                        pdf.rect(13, 13, 271, 184)
                        pdf.ln(15)
                        pdf.set_font("Times", 'B', 32)
                        pdf.cell(0, 15, "TEN CERTIFICATE", ln=True, align='C')
                        pdf.cell(0, 15, "OF ACHIEVEMENT", ln=True, align='C')
                        pdf.set_text_color(212, 175, 55)
                        pdf.set_font("Times", 'B', 16)
                        pdf.cell(0, 10, "- + -", ln=True, align='C')
                        pdf.set_text_color(0, 0, 0)
                        pdf.set_font("Times", 'I', 16)
                        pdf.cell(0, 15, "This certificate is awarded to", ln=True, align='C')
                        safe_name = transliterate(str(name)).encode('ascii', 'replace').decode('ascii')
                        pdf.set_font("Times", 'B', 34)
                        pdf.cell(0, 20, safe_name, ln=True, align='C')
                        pdf.line(60, 110, 237, 110)
                        pdf.set_font("Times", '', 14)
                        pdf.cell(0, 15, "for successfully completing the TEN Competition with the following results:", ln=True, align='C')
                        pdf.ln(5)
                        pdf.set_font("Times", 'B', 16)
                        pdf.cell(0, 8, f"TEN LOGIC: {logic} / 100", ln=True, align='C')
                        pdf.cell(0, 8, f"TEN MATH: {math_val} / 100", ln=True, align='C')
                        pdf.cell(0, 8, f"Overall TEN Score: {total} / 100", ln=True, align='C')
                        pdf.cell(0, 8, f"Overall Rank: {rank}", ln=True, align='C')
                        pdf.set_y(165)
                        pdf.set_font("Times", '', 12)
                        date_str = datetime.datetime.now().strftime("%d.%m.%Y")
                        pdf.set_x(40)
                        pdf.cell(50, 8, date_str, ln=False, align='C')
                        pdf.line(40, 173, 90, 173)
                        pdf.set_y(174)
                        pdf.set_x(40)
                        pdf.set_font("Times", 'I', 10)
                        pdf.cell(50, 5, "Date", ln=False, align='C')
                        
                        if os.path.exists("sign.jpg"):
                            pdf.image("sign.jpg", x=215, y=145, w=30)
                        else:
                            pdf.set_y(160)
                            pdf.set_x(200)
                            pdf.set_font("Times", 'I', 18)
                            pdf.cell(60, 8, "YRS", ln=False, align='C')
                            
                        pdf.line(200, 173, 260, 173)
                        pdf.set_y(174)
                        pdf.set_x(200)
                        pdf.set_font("Times", 'B', 10)
                        pdf.cell(60, 5, "FOUNDER", ln=False, align='C')
                        pdf.set_y(179)
                        pdf.set_x(200)
                        pdf.set_font("Times", 'I', 10)
                        pdf.cell(60, 5, "CEO MEIMANKHAN YERSAIYN", ln=False, align='C')
                        pdf.set_y(165)
                        pdf.set_x(135)
                        pdf.set_text_color(212, 175, 55)
                        pdf.set_font("Times", 'B', 24)
                        pdf.cell(30, 10, "(TEN)", ln=False, align='C')
                        pdf.set_y(185)
                        pdf.set_text_color(100, 100, 100)
                        pdf.set_font("Times", '', 10)
                        pdf.cell(0, 5, f"Certificate ID: {cert_id}", ln=True, align='C')
                        return pdf.output(dest='S').encode('latin-1')

                    pdf_data = create_pdf(current_user_name, user_logic_score, user_math_score, total_score, st.session_state.cert_id, rank_display)
                    st.download_button(label=t["download_cert"], data=pdf_data, file_name=f"{st.session_state.cert_id}.pdf", mime="application/pdf")