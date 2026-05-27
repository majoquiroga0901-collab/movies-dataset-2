import csv
import json
import os
from datetime import datetime

import streamlit as st

# -----------------------------------
# ARCHIVOS Y DATOS
# -----------------------------------

USERS_FILE = "admin_usuarios.csv"
CLIENTS_FILE = "admin_clientes.csv"
SALES_FILE = "admin_ventas.csv"
HOTELS_FILE = "admin_hoteles_cruceros.json"
PACKAGES_FILE = "admin_packages.json"
CONFIG_FILE = "admin_config.json"

DEFAULT_USERS = {
    "mariajose": {
        "password": "admin2026",
        "rol": "admin",
        "name": "María Jose",
        "status": "active",
    },
    "juanpablo": {
        "password": "asesor2026",
        "rol": "advisor",
        "name": "Juan Pablo",
        "status": "active",
    },
}

DEFAULT_HOTELS_AND_CRUISES = {
    "hoteles": {
        "Orlando": ["Avanti", "Buena Vista Suites"],
        "Las Vegas": ["Tuscany Suites"],
        "Cancún": ["Oasis Palm Lite", "Villa del Palmar"],
        "Punta Cana": ["Ancora"],
        "Puerto Vallarta": ["Crown Paradise", "Krystal Vallarta"],
        "Los Cabos": ["Riu Santa Fe", "Marina Fiesta"],
        "Costa Rica": ["Fiesta Resort", "Occidental Papagayo"],
    },
    "cruises": {
        "5/4": [
            {"departure": "Miami (FL)", "route": "Key West + Cozumel"},
            {"departure": "Fort Lauderdale (FL)", "route": "Key West + Cozumel"},
            {"departure": "Port Canaveral (FL)", "route": "Bahamas + Nassau"},
            {"departure": "Jacksonville (FL)", "route": "Bahamas + Nassau"},
            {"departure": "Tampa (FL)", "route": "Cozumel"},
            {"departure": "Galveston (TX)", "route": "Cozumel"},
            {"departure": "New Orleans (LA)", "route": "Cozumel"},
            {"departure": "Long Beach (CA)", "route": "Catalina + Ensenada"},
        ],
        "6/5": [
            {"departure": "Charleston (SC)", "route": "Bahamas + Nassau"},
            {"departure": "Jacksonville (FL)", "route": "Bahamas + Nassau"},
            {"departure": "Miami (FL)", "route": "Jamaica + Grand Cayman"},
            {"departure": "Miami (FL)", "route": "Grand Turk + Amber Cove"},
            {"departure": "Tampa (FL)", "route": "Grand Cayman + Cozumel"},
            {"departure": "New Orleans (LA)", "route": "Progreso + Cozumel"},
        ],
    },
}

DEFAULT_PACKAGES = {
    "VDL": {
        "requirements": [
            "Married or living together",
            "US/Canada resident or citizen",
            "Women 25+",
            "Men 30+",
            "Families allowed",
            "Children under 11",
        ],
        "includes": [
            "All inclusive",
            "Airport transportation",
            "3 meals included",
            "Alcoholic drinks",
            "Non alcoholic drinks",
            "Premium stays",
            "3 destinations",
            "90 min Time Share",
        ],
        "validity": ["12 months to reserve", "18 months to travel"],
        "destinations": [
            "Cancun",
            "Punta Cana",
            "Puerto Vallarta",
            "Los Cabos",
            "Costa Rica",
            "Bahamas",
        ],
    },
    "HYBRID": {
        "requirements": [
            "Women 25+",
            "US/Canada resident or citizen",
            "No family requirement",
        ],
        "includes": [
            "1 VDL destination",
            "2 Mix & Match destinations",
            "90 min presentation",
        ],
        "validity": ["12 months reserve", "18 months travel"],
        "destinations": ["Cancun", "Las Vegas", "Orlando"],
    },
    "MIX & MATCH": {
        "requirements": [
            "18+",
            "Can travel with 21+ adult",
            "No residency required",
            "No Time Share",
        ],
        "includes": [
            "Open 4/3",
            "Cruise 5/4",
            "Cabin",
            "Snacks",
            "Attractions",
            "2 destinations",
        ],
        "validity": [
            "12 months first reservation",
            "12 additional months second reservation",
        ],
        "destinations": ["USA", "Canada", "Bahamas", "Mexico"],
    },
}

DEFAULT_CONFIG = {
    "zones": {
        "California": "Costa Oeste",
        "Texas": "Zona Central",
        "Florida": "Costa Este",
        "New York": "Costa Este",
        "Puerto Rico": "Puerto Rico",
    },
    "horarios": {
        "Costa Oeste": "6 AM - 2 PM",
        "Zona Central": "7 AM - 4 PM",
        "Costa Este": "9 AM - 5 PM",
        "Puerto Rico": "10 AM - 5 PM",
    },
    "porcentaje_default": 0.06,
    "follow_up_status": [
        "Interested",
        "Pending call",
        "Follow-up",
        "Closed sale",
        "No answer",
        "Not qualified",
    ],
    "permission_matrix": {
        "register_sales": {"advisor": True, "admin": True},
        "delete_users": {"advisor": False, "admin": True},
        "edit_packages": {"advisor": False, "admin": True},
        "view_stats": {"advisor": "Limited", "admin": "Full"},
    },
}

PERMISSION_DESCRIPTIONS = {
    "register_sales": "Register sales",
    "delete_users": "Delete users",
    "edit_packages": "Edit packages",
    "view_stats": "View stats",
}

# -----------------------------------
# UTILIDADES
# -----------------------------------

def ensure_file_exists(path, headers=None, default_data=None):
    if not os.path.exists(path):
        if headers:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(headers)
        elif default_data is not None:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(default_data, f, ensure_ascii=False, indent=2)


def load_csv(path):
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [row for row in reader]


def save_csv(path, fieldnames, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def load_json(path, default_data):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default_data, f, ensure_ascii=False, indent=2)
        return default_data
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default_data


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def parse_children_ages(raw_value):
    if isinstance(raw_value, str):
        parts = [part.strip() for part in raw_value.split(",") if part.strip()]
        return [int(part) for part in parts if part.isdigit()]
    if isinstance(raw_value, list):
        return [int(x) for x in raw_value if isinstance(x, int)]
    return []


def today_str():
    return datetime.now().strftime("%Y-%m-%d")


def format_money(value):
    return f"${value:,.2f}"


def calculate_qualification(client):
    residency = client["Residency"]
    marital_status = client["Marital status"]
    age = int(client["Age"])
    children_ages = parse_children_ages(client.get("Children ages", ""))

    if residency == "Sí":
        if marital_status == "Casado / Convive" and 25 <= age <= 79 and all(a <= 11 for a in children_ages):
            return "VDL"
        if marital_status == "Mujer Soltera" and 25 <= age <= 72:
            return "HÍBRIDO"
        if marital_status == "Hombre Soltero" and 35 <= age <= 59:
            return "VDL"
    if age >= 18 and all(a <= 17 for a in children_ages):
        return "MIX & MATCH"
    return "No qualify"


def calculate_commission(amount, percentage):
    try:
        return float(amount) * float(percentage)
    except Exception:
        return 0.0


def read_data():
    ensure_file_exists(USERS_FILE, headers=["Usuario", "Password", "Rol", "Status", "Name"])
    ensure_file_exists(CLIENTS_FILE, headers=[
        "ID",
        "Full name",
        "State",
        "Age",
        "Marital status",
        "Residency",
        "Children count",
        "Children ages",
        "Assigned advisor",
        "Qualification result",
        "Package",
        "Destination",
        "Follow-up status",
        "Notes",
        "Registration date",
    ])
    ensure_file_exists(SALES_FILE, headers=[
        "Date",
        "Client",
        "Advisor",
        "Package",
        "Destination",
        "Cruise",
        "Hotel",
        "Commission",
        "Follow-up status",
    ])
    ensure_file_exists(HOTELS_FILE, default_data=DEFAULT_HOTELS_AND_CRUISES)
    ensure_file_exists(PACKAGES_FILE, default_data=DEFAULT_PACKAGES)
    ensure_file_exists(CONFIG_FILE, default_data=DEFAULT_CONFIG)

    users = load_csv(USERS_FILE)
    if not users:
        users = []
        for username, info in DEFAULT_USERS.items():
            users.append({
                "Usuario": username,
                "Password": info["password"],
                "Rol": info["rol"],
                "Status": info["status"],
                "Name": info["name"],
            })
        save_csv(USERS_FILE, ["Usuario", "Password", "Rol", "Status", "Name"], users)
    clients = load_csv(CLIENTS_FILE)
    sales = load_csv(SALES_FILE)
    hotels_and_cruises = load_json(HOTELS_FILE, DEFAULT_HOTELS_AND_CRUISES)
    packages = load_json(PACKAGES_FILE, DEFAULT_PACKAGES)
    config = load_json(CONFIG_FILE, DEFAULT_CONFIG)
    return users, clients, sales, hotels_and_cruises, packages, config


def save_users(users):
    save_csv(USERS_FILE, ["Usuario", "Password", "Rol", "Status", "Name"], users)


def save_clients(clients):
    save_csv(CLIENTS_FILE, [
        "ID",
        "Full name",
        "State",
        "Age",
        "Marital status",
        "Residency",
        "Children count",
        "Children ages",
        "Assigned advisor",
        "Qualification result",
        "Package",
        "Destination",
        "Follow-up status",
        "Notes",
        "Registration date",
    ], clients)


def save_sales(sales):
    save_csv(SALES_FILE, [
        "Date",
        "Client",
        "Advisor",
        "Package",
        "Estado",
        "Age",
        "Marital status",
        "Residency",
        "Children count",
        "Children ages",
        "Destination",
        "Cruise",
        "Hotel",
        "Commission",
        "Follow-up status",
    ], sales)


def get_user(username, users):
    return next((u for u in users if u["Usuario"] == username), None)


def build_summary(clients, sales, users, current_user=None):
    sales_total = len(sales)
    today = datetime.now().strftime("%Y-%m-%d")
    sales_today = sum(1 for s in sales if s["Date"].startswith(today))
    total_commissions = sum(float(s.get("Commission", 0) or 0) for s in sales)
    registered_clients = len(clients)
    active_advisors = sum(1 for u in users if u["Rol"] == "advisor" and u["Status"] == "active")
    pending_followups = sum(1 for c in clients if c["Follow-up status"] in ["Pending call", "Follow-up"])
    advisor_counts = {}
    package_counts = {}
    destination_counts = {}
    for s in sales:
        advisor_counts[s["Advisor"]] = advisor_counts.get(s["Advisor"], 0) + 1
        package_counts[s["Package"]] = package_counts.get(s["Package"], 0) + 1
        destination_counts[s["Destination"]] = destination_counts.get(s["Destination"], 0) + 1
    best_advisor = max(advisor_counts, key=advisor_counts.get) if advisor_counts else "N/A"
    best_package = max(package_counts, key=package_counts.get) if package_counts else "N/A"
    best_destination = max(destination_counts, key=destination_counts.get) if destination_counts else "N/A"
    conversion_rate = f"{(sales_total / registered_clients * 100):.1f}%" if registered_clients else "0%"
    monthly_revenue = total_commissions  # simplistic as commission total
    if current_user:
        advisor_sales = [s for s in sales if s["Advisor"] == current_user]
        advisor_commission = sum(float(s.get("Commission", 0) or 0) for s in advisor_sales)
    else:
        advisor_commission = 0
    return {
        "sales_total": sales_total,
        "sales_today": sales_today,
        "monthly_revenue": monthly_revenue,
        "active_advisors": active_advisors,
        "registered_clients": registered_clients,
        "pending_followups": pending_followups,
        "best_advisor": best_advisor,
        "best_package": best_package,
        "best_destination": best_destination,
        "conversion_rate": conversion_rate,
        "total_commissions": total_commissions,
        "advisor_commission": advisor_commission,
    }

# -----------------------------------
# APP UI
# -----------------------------------

st.set_page_config(page_title="Cerrador Pro Enterprise", page_icon="💼", layout="wide")

st.markdown(
    """
    <style>
    .stApp {
        background-color: #f4f6f8;
    }
    .card {
        padding: 20px;
        border-radius: 14px;
        background: white;
        box-shadow: 0 8px 20px rgba(0,0,0,0.05);
        margin-bottom: 16px;
    }
    .card h3 {
        margin: 0 0 8px 0;
    }
    .card-value {
        font-size: 28px;
        font-weight: 700;
        margin-bottom: 6px;
    }
    .metric {
        color: #6b7280;
    }
    .success-box {
        border-left: 6px solid #2ecc71;
        background: #eefaf1;
        color: #145a32;
        padding: 14px;
        border-radius: 12px;
    }
    .warning-box {
        border-left: 6px solid #e74c3c;
        background: #fdecec;
        color: #78281f;
        padding: 14px;
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

ensure_file_exists(USERS_FILE, headers=["Usuario", "Password", "Rol", "Status", "Name"])
ensure_file_exists(CLIENTS_FILE, headers=[
    "ID",
    "Full name",
    "State",
    "Age",
    "Marital status",
    "Residency",
    "Children count",
    "Children ages",
    "Assigned advisor",
    "Qualification result",
    "Package",
    "Destination",
    "Follow-up status",
    "Notes",
    "Registration date",
])
ensure_file_exists(SALES_FILE, headers=[
    "Date",
    "Client",
    "Advisor",
    "Package",
    "Estado",
    "Age",
    "Marital status",
    "Residency",
    "Children count",
    "Children ages",
    "Destination",
    "Cruise",
    "Hotel",
    "Commission",
    "Follow-up status",
])
ensure_file_exists(HOTELS_FILE, default_data=DEFAULT_HOTELS_AND_CRUISES)
ensure_file_exists(PACKAGES_FILE, default_data=DEFAULT_PACKAGES)
ensure_file_exists(CONFIG_FILE, default_data=DEFAULT_CONFIG)

users, clients, sales, hotels_and_cruises, packages, config = read_data()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = ""
    st.session_state.rol = ""
    st.session_state.name = ""

st.sidebar.title("🔐 Login")
usuario = st.sidebar.text_input("Usuario", key="login_usuario")
password = st.sidebar.text_input("Contraseña", type="password", key="login_password")

if st.sidebar.button("Ingresar"):
    usuario_key = usuario.strip().lower()
    user = get_user(usuario_key, users)
    if user and user["Password"] == password and user["Status"] == "active":
        st.session_state.logged_in = True
        st.session_state.user = usuario_key
        st.session_state.name = user.get("Name", usuario_key)
        st.session_state.rol = user.get("Rol", "advisor")
        st.sidebar.success(f"Bienvenido {st.session_state.name}")
    else:
        st.sidebar.error("Usuario o contraseña incorrecta, o cuenta inactiva.")

if st.session_state.logged_in:
    if st.sidebar.button("Cerrar sesión"):
        st.session_state.logged_in = False
        st.session_state.user = ""
        st.session_state.name = ""
        st.session_state.rol = ""
        st.rerun()

if not st.session_state.logged_in:
    st.warning("Inicia sesión para acceder al panel")
    st.stop()

role = st.session_state.rol
username = st.session_state.user
name = st.session_state.name

menu_options = []
if role == "admin":
    menu_options = [
        "📊 Dashboard",
        "👥 Users",
        "📞 Clients",
        "🛒 Sales",
        "🏨 Hotels & Cruises",
        "📦 Packages",
        "💰 Commissions",
        "📈 Statistics",
        "📜 Sales History",
        "⚙️ Settings",
    ]
else:
    menu_options = [
        "🏠 Home",
        "📞 New Client",
        "🛒 New Sale",
        "📋 Registered Clients",
        "🌴 Destinations & Cruises",
        "📦 Package Qualification",
        "💰 My Commissions",
        "📈 My Statistics",
        "🗓️ Follow-ups",
        "📝 Sales History",
        "⚙️ My Profile",
    ]

page = st.sidebar.radio("Panel", menu_options)

summary = build_summary(clients, sales, users, current_user=name if role == "advisor" else None)


# -----------------------------------
# PÁGINAS ADMIN
# -----------------------------------

def dashboard_page():
    st.title("📊 Dashboard")
    st.markdown("### Main admin screen")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total sales", summary["sales_total"])
    col2.metric("Sales today", summary["sales_today"])
    col3.metric("Monthly revenue", format_money(summary["monthly_revenue"]))
    col4, col5, col6 = st.columns(3)
    col4.metric("Active advisors", summary["active_advisors"])
    col5.metric("Registered clients", summary["registered_clients"])
    col6.metric("Pending follow-ups", summary["pending_followups"])
    col7, col8, col9 = st.columns(3)
    col7.metric("Best advisor", summary["best_advisor"])
    col8.metric("Best selling package", summary["best_package"])
    col9.metric("Most sold destination", summary["best_destination"])
    st.markdown(f"**Conversion rate:** {summary['conversion_rate']}")
    st.markdown(f"**Total commissions:** {format_money(summary['total_commissions'])}")
    st.markdown("---")
    st.markdown("### Cards")
    card_col1, card_col2, card_col3 = st.columns(3)
    card_col1.markdown("""
        <div class='card'>
            <h3>💰 Revenue</h3>
            <div class='card-value'>{}</div>
            <div class='metric'>Total commissions</div>
        </div>
    """.format(format_money(summary["monthly_revenue"])), unsafe_allow_html=True)
    card_col2.markdown("""
        <div class='card'>
            <h3>📞 Clients</h3>
            <div class='card-value'>{}</div>
            <div class='metric'>Registered clients</div>
        </div>
    """.format(summary["registered_clients"]), unsafe_allow_html=True)
    card_col3.markdown("""
        <div class='card'>
            <h3>📈 Conversion</h3>
            <div class='card-value'>{}</div>
            <div class='metric'>Conversion rate</div>
        </div>
    """.format(summary["conversion_rate"]), unsafe_allow_html=True)
    extra_col1, extra_col2, extra_col3 = st.columns(3)
    extra_col1.markdown("""
        <div class='card'>
            <h3>👨‍💼 Advisors</h3>
            <div class='card-value'>{}</div>
            <div class='metric'>Active advisors</div>
        </div>
    """.format(summary["active_advisors"]), unsafe_allow_html=True)
    extra_col2.markdown("""
        <div class='card'>
            <h3>🌴 Destinations</h3>
            <div class='card-value'>{}</div>
            <div class='metric'>Unique destinations</div>
        </div>
    """.format(len(set([s["Destination"] for s in sales if s.get("Destination")]))) , unsafe_allow_html=True)
    extra_col3.markdown("""
        <div class='card'>
            <h3>🚢 Cruises</h3>
            <div class='card-value'>{}</div>
            <div class='metric'>Cruise departures</div>
        </div>
    """.format(sum(len(v) for v in hotels_and_cruises["cruises"].values())), unsafe_allow_html=True)
    st.markdown("---")
    st.subheader("Sales per day")
    daily = {}
    for sale in sales:
        day = sale["Date"][:10]
        daily[day] = daily.get(day, 0) + 1
    if daily:
        st.bar_chart(daily)
    else:
        st.info("No sales data yet.")
    st.subheader("Sales per advisor")
    advisor_counts = {}
    for sale in sales:
        advisor_counts[sale["Advisor"]] = advisor_counts.get(sale["Advisor"], 0) + 1
    if advisor_counts:
        st.bar_chart(advisor_counts)
    else:
        st.info("No sales data yet.")
    st.subheader("Most sold packages")
    package_counts = {}
    for sale in sales:
        package_counts[sale["Package"]] = package_counts.get(sale["Package"], 0) + 1
    if package_counts:
        st.bar_chart(package_counts)
    else:
        st.info("No package data yet.")
    st.subheader("Monthly growth")
    monthly = {}
    for sale in sales:
        month = sale["Date"][:7]
        monthly[month] = monthly.get(month, 0) + 1
    if monthly:
        st.line_chart(monthly)
    else:
        st.info("No monthly sales data.")


def users_page():
    st.title("👥 Users")
    st.markdown("### Admin controls all users")
    st.dataframe(users)
    st.markdown("---")
    st.subheader("Create advisor or admin")
    with st.form("create_user"):
        new_user = st.text_input("Usuario")
        new_name = st.text_input("Nombre completo")
        new_password = st.text_input("Contraseña", type="password")
        role = st.selectbox("Rol", ["admin", "advisor"])
        status = st.selectbox("Status", ["active", "inactive"])
        if st.form_submit_button("Guardar usuario"):
            if not new_user or not new_password:
                st.error("Usuario y contraseña son obligatorios.")
            else:
                if get_user(new_user.strip().lower(), users):
                    st.error("El usuario ya existe.")
                else:
                    users.append({
                        "Usuario": new_user.strip().lower(),
                        "Password": new_password,
                        "Rol": role,
                        "Status": status,
                        "Name": new_name.strip() or new_user.strip(),
                    })
                    save_users(users)
                    st.success("Usuario guardado.")
                    st.rerun()
    st.markdown("---")
    st.subheader("Manage existing users")
    selected = st.selectbox("Seleccionar usuario", [u["Usuario"] for u in users])
    if selected:
        user = get_user(selected, users)
        if user:
            st.write(f"**Nombre:** {user['Name']}")
            st.write(f"**Rol:** {user['Rol']}")
            st.write(f"**Status:** {user['Status']}")
            col1, col2 = st.columns(2)
            if col1.button("Bloquear / Desbloquear usuario"):
                user["Status"] = "inactive" if user["Status"] == "active" else "active"
                save_users(users)
                st.success("Estado actualizado.")
                st.rerun()
            if col2.button("Eliminar usuario"):
                if user["Usuario"] == username:
                    st.error("No puedes eliminar tu propia cuenta.")
                else:
                    users[:] = [u for u in users if u["Usuario"] != user["Usuario"]]
                    save_users(users)
                    st.success("Usuario eliminado.")
                    st.rerun()
            new_pass = st.text_input("Nueva contraseña", type="password")
            new_role = st.selectbox("Nuevo rol", ["admin", "advisor"], index=0 if user["Rol"] == "admin" else 1)
            if st.button("Actualizar usuario"):
                if new_pass:
                    user["Password"] = new_pass
                user["Rol"] = new_role
                save_users(users)
                st.success("Usuario actualizado.")
                st.rerun()


def clients_page():
    st.title("📞 Clients")
    st.markdown("### Full customer management module")
    search_name = st.text_input("Buscar cliente")
    filter_advisor = st.selectbox("Filtrar por asesor", ["Todos"] + [u["Name"] for u in users if u["Rol"] == "advisor"])
    filter_package = st.selectbox("Filtrar por paquete", ["Todos", "VDL", "HÍBRIDO", "MIX & MATCH"])
    filter_status = st.selectbox("Filtrar por estado", ["Todos"] + config["follow_up_status"])
    filtered = clients
    if search_name:
        filtered = [c for c in filtered if search_name.lower() in c["Full name"].lower()]
    if filter_advisor != "Todos":
        filtered = [c for c in filtered if c["Assigned advisor"] == filter_advisor]
    if filter_package != "Todos":
        filtered = [c for c in filtered if c["Package"] == filter_package]
    if filter_status != "Todos":
        filtered = [c for c in filtered if c["Follow-up status"] == filter_status]

    st.dataframe(filtered)
    st.markdown("---")
    st.subheader("Add or update client")
    with st.form("client_form"):
        full_name = st.text_input("Full name")
        state = st.text_input("State")
        age = st.number_input("Age", min_value=18, max_value=100, value=30)
        marital_status = st.selectbox("Marital status", ["Casado / Convive", "Mujer Soltera", "Hombre Soltero"])
        residency = st.selectbox("Residency", ["Sí", "No"])
        children_count = st.number_input("Children count", min_value=0, max_value=10, value=0)
        children_ages = st.text_input("Children ages (comma separated)")
        assigned_advisor = st.selectbox("Assigned advisor", [u["Name"] for u in users if u["Rol"] == "advisor"])
        follow_up_status = st.selectbox("Follow-up status", config["follow_up_status"])
        notes = st.text_area("Notes")
        if st.form_submit_button("Guardar cliente"):
            qualification = calculate_qualification({
                "Residency": residency,
                "Marital status": marital_status,
                "Age": age,
                "Children ages": children_ages,
            })
            package = qualification if qualification != "No qualify" else "MIX & MATCH"
            destination = "Cancún" if package == "VDL" else "Las Vegas" if package == "HÍBRIDO" else "Bahamas"
            client_id = str(len(clients) + 1)
            clients.append({
                "ID": client_id,
                "Full name": full_name,
                "State": state,
                "Age": str(age),
                "Marital status": marital_status,
                "Residency": residency,
                "Children count": str(children_count),
                "Children ages": children_ages,
                "Assigned advisor": assigned_advisor,
                "Qualification result": qualification,
                "Package": package,
                "Destination": destination,
                "Follow-up status": follow_up_status,
                "Notes": notes,
                "Registration date": today_str(),
            })
            save_clients(clients)
            st.success("Cliente guardado.")
            st.rerun()

    st.markdown("---")
    st.subheader("Manage filtered client")
    selected_client = st.selectbox("Seleccionar cliente para borrar", [c["ID"] + " - " + c["Full name"] for c in filtered] if filtered else [])
    if selected_client:
        selected_id = selected_client.split(" - ")[0]
        client = next((c for c in clients if c["ID"] == selected_id), None)
        if client:
            if st.button("Borrar cliente seleccionado"):
                clients[:] = [c for c in clients if c["ID"] != selected_id]
                save_clients(clients)
                st.success("Cliente borrado.")
                st.rerun()


def sales_page():
    st.title("🛒 Sales")
    st.markdown("### Registro de ventas")

    zonas = {
        "Alabama": "Costa Este",
        "Alaska": "Costa Oeste",
        "Arizona": "Costa Oeste",
        "Arkansas": "Zona Central",
        "California": "Costa Oeste",
        "North Carolina": "Costa Este",
        "South Carolina": "Costa Este",
        "Colorado": "Costa Oeste",
        "Connecticut": "Costa Este",
        "North Dakota": "Zona Central",
        "South Dakota": "Zona Central",
        "Delaware": "Costa Este",
        "Florida": "Costa Este",
        "Georgia": "Costa Este",
        "Hawaii": "Costa Oeste",
        "Idaho": "Costa Oeste",
        "Illinois": "Zona Central",
        "Indiana": "Zona Central",
        "Iowa": "Zona Central",
        "Kansas": "Zona Central",
        "Kentucky": "Zona Central",
        "Louisiana": "Zona Central",
        "Maine": "Costa Este",
        "Maryland": "Costa Este",
        "Massachusetts": "Costa Este",
        "Michigan": "Zona Central",
        "Minnesota": "Zona Central",
        "Mississippi": "Zona Central",
        "Missouri": "Zona Central",
        "Montana": "Costa Oeste",
        "Nebraska": "Zona Central",
        "Nevada": "Costa Oeste",
        "New Jersey": "Costa Este",
        "New York": "Costa Este",
        "New Hampshire": "Costa Este",
        "New Mexico": "Costa Oeste",
        "Ohio": "Zona Central",
        "Oklahoma": "Zona Central",
        "Oregon": "Costa Oeste",
        "Pennsylvania": "Costa Este",
        "Rhode Island": "Costa Este",
        "Tennessee": "Zona Central",
        "Texas": "Zona Central",
        "Utah": "Costa Oeste",
        "Vermont": "Costa Este",
        "Virginia": "Costa Este",
        "West Virginia": "Costa Este",
        "Washington": "Costa Oeste",
        "Wisconsin": "Zona Central",
        "Wyoming": "Costa Oeste",
    }

    horarios = {
        "Costa Oeste": "6 AM - 2 PM",
        "Zona Central": "7 AM - 4 PM",
        "Costa Este": "9 AM - 5 PM",
    }

    destinos_vdl = [
        "Cancún",
        "Punta Cana",
        "Puerto Vallarta",
        "Los Cabos",
        "Bahamas",
        "Costa Rica",
    ]

    destinos_mix = [
        "Las Vegas",
        "Phoenix",
        "San Diego",
        "Los Ángeles",
        "Bahamas",
        "México",
    ]

    cruceros = {
        "Miami": "Key West + Cozumel",
        "Port Canaveral": "Bahamas + Nassau",
        "Long Beach": "Ensenada + Islas Catalina",
        "New Orleans": "Cozumel + Progreso",
    }

    def hijos_validos_vdl(edades):
        return all(edad_hijo <= 11 for edad_hijo in edades)

    def hijos_validos_mix(edades):
        return all(edad_hijo <= 17 for edad_hijo in edades)

    if "sale_cliente" not in st.session_state:
        st.session_state.sale_cliente = ""
    if "sale_estado" not in st.session_state:
        st.session_state.sale_estado = sorted(zonas.keys())[0]
    if "sale_estado_civil" not in st.session_state:
        st.session_state.sale_estado_civil = "Casado / Convive"
    if "sale_edad" not in st.session_state:
        st.session_state.sale_edad = 30
    if "sale_residencia" not in st.session_state:
        st.session_state.sale_residencia = "Sí"
    if "sale_cantidad_hijos" not in st.session_state:
        st.session_state.sale_cantidad_hijos = 0

    cliente = st.text_input("Cliente", key="sale_cliente")
    estado = st.selectbox("Estado", sorted(zonas.keys()), key="sale_estado")
    estado_civil = st.selectbox(
        "Estado civil",
        [
            "Casado / Convive",
            "Mujer Soltera",
            "Hombre Soltero",
        ],
        key="sale_estado_civil",
    )
    edad = st.number_input("Edad", 18, 100, 30, key="sale_edad")
    residencia = st.selectbox("Residencia", ["Sí", "No"], key="sale_residencia")
    cantidad_hijos = st.number_input("Cantidad hijos", 0, 10, 0, key="sale_cantidad_hijos")
    edades_hijos = []
    if cantidad_hijos > 0:
        st.subheader("Edades hijos")
        for i in range(cantidad_hijos):
            clave_hijo = f"sale_hijo_{i}"
            if clave_hijo not in st.session_state:
                st.session_state[clave_hijo] = 0
            edad_hijo = st.number_input(f"Edad hijo {i+1}", 0, 25, value=st.session_state[clave_hijo], key=clave_hijo)
            edades_hijos.append(edad_hijo)

    paquete = "MIX & MATCH"
    vigencia = "24 meses"
    beneficios = []
    destinos = []
    califica = False

    if residencia == "Sí":
        if estado_civil == "Casado / Convive":
            if 30 <= edad <= 70:
                if hijos_validos_vdl(edades_hijos):
                    paquete = "VDL"
                    vigencia = "12 meses reservar / 18 vacacionar"
                    beneficios = [
                        "All inclusive",
                        "3 comidas",
                        "Bebidas alcohólicas",
                        "Transporte aeropuerto-hotel",
                        "90 mins Time Share",
                    ]
                    destinos = destinos_vdl
                    califica = True
        elif estado_civil == "Mujer Soltera":
            if 25 <= edad <= 70:
                paquete = "HÍBRIDO"
                beneficios = [
                    "1 destino VDL",
                    "2 Mix & Match",
                    "90 mins Time Share",
                ]
                destinos = ["Cancún", "Las Vegas", "Orlando"]
                califica = True
        elif estado_civil == "Hombre Soltero":
            if 35 <= edad <= 59:
                paquete = "VDL"
                beneficios = [
                    "All inclusive",
                    "Hospedaje premium",
                    "Transporte incluido",
                ]
                destinos = ["Puerto Vallarta", "Los Cabos", "Lake Havasu"]
                califica = True

    if not califica:
        if edad >= 18:
            if hijos_validos_mix(edades_hijos):
                paquete = "MIX & MATCH"
                beneficios = [
                    "Sin Time Share",
                    "Open 4/3",
                    "Crucero 5/4",
                    "12 meses para reservar",
                ]
                destinos = destinos_mix

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Resultado")
        if paquete == "VDL":
            st.success(f"✅ CALIFICA PARA VDL — Vigencia: {vigencia}")
        elif paquete == "HÍBRIDO":
            st.success("✅ CALIFICA PARA HÍBRIDO")
        else:
            st.warning("⚠️ ENVIAR A MIX & MATCH")

        st.subheader("Beneficios")
        for beneficio in beneficios:
            st.write("✅", beneficio)

        st.subheader("Destinos recomendados")
        for destino in destinos:
            st.write("🌴", destino)

        st.subheader("Cruceros disponibles")
        for salida, ruta in cruceros.items():
            st.write(f"🚢 {salida} → {ruta}")

    with col2:
        zona = zonas[estado]
        st.subheader("Zona")
        st.info(f"Zona: {zona}\n\nHorario: {horarios[zona]}")

        deducible = st.number_input("Deducible", 200, 500, 399)
        porcentaje = st.selectbox("Porcentaje comisión", [6, 8])
        comision = deducible * (porcentaje / 100)
        st.metric("Comisión estimada", f"${comision:,.2f}")

        def limpiar_formulario():
            st.session_state.sale_cliente = ""
            st.session_state.sale_estado = sorted(zonas.keys())[0]
            st.session_state.sale_estado_civil = "Casado / Convive"
            st.session_state.sale_edad = 30
            st.session_state.sale_residencia = "Sí"
            st.session_state.sale_cantidad_hijos = 0
            for i in range(10):
                clave_hijo = f"sale_hijo_{i}"
                if clave_hijo in st.session_state:
                    del st.session_state[clave_hijo]

        st.button("Limpiar formulario", on_click=limpiar_formulario)

        advisor_name = name or "Tu asesor"
        client_label = cliente or "cliente"
        speech_text = f"Hola {client_label},\n\nSoy {advisor_name} y quiero proponerte el paquete {paquete}. "
        if paquete == "VDL":
            speech_text += "Este paquete es ideal para tu perfil porque ofrece hospedaje premium, transporte incluido y acceso a experiencias All Inclusive."
        elif paquete == "HÍBRIDO":
            speech_text += "Lo recomiendo para tu perfil como mujer soltera, ya que combina un destino VDL con opciones flexibles Mix & Match."
        else:
            speech_text += "Con MIX & MATCH puedes reservar en varios destinos y aprovechar una vigencia flexible sin Time Share."
        speech_text += f"\n\nTu destino recomendado es {destinos[0] if destinos else 'un destino disponible'}.\n\n¿Te gustaría avanzar con esta opción?"

        st.subheader("Texto para asesor")
        st.text_area("Copy para cerrar la venta", speech_text, height=180)

        if st.button("Registrar Venta"):
            sales.append({
                "Date": datetime.now().isoformat(sep=" ", timespec="seconds"),
                "Client": cliente,
                "Advisor": name,
                "Package": paquete,
                "Estado": estado,
                "Age": str(edad),
                "Marital status": estado_civil,
                "Residency": residencia,
                "Children count": str(cantidad_hijos),
                "Children ages": ", ".join(str(x) for x in edades_hijos),
                "Destination": destinos[0] if destinos else "",
                "Cruise": ", ".join([f"{k} → {v}" for k, v in cruceros.items()]),
                "Hotel": "",
                "Commission": f"{comision:.2f}",
                "Follow-up status": "Closed sale",
            })
            save_sales(sales)
            st.success("Venta registrada correctamente")


def hotels_cruises_page():
    st.title("🏨 Hotels & Cruises")
    st.markdown("### Admin manages destinations dynamically")
    st.subheader("Hoteles")
    for city, hotel_list in hotels_and_cruises["hoteles"].items():
        st.markdown(f"**{city}**")
        for h in hotel_list:
            st.write(f"- {h}")
    st.markdown("---")
    st.subheader("Add hotel")
    with st.form("add_hotel"):
        city = st.text_input("City")
        hotel_name = st.text_input("Hotel")
        if st.form_submit_button("Agregar hotel"):
            if city and hotel_name:
                hotels_and_cruises["hoteles"].setdefault(city, [])
                if hotel_name not in hotels_and_cruises["hoteles"][city]:
                    hotels_and_cruises["hoteles"][city].append(hotel_name)
                    save_json(HOTELS_FILE, hotels_and_cruises)
                    st.success("Hotel agregado.")
                    st.rerun()
                else:
                    st.warning("El hotel ya existe.")
            else:
                st.error("Ciudad y hotel son obligatorios.")
    st.subheader("Remove hotel")
    with st.form("remove_hotel"):
        city_remove = st.selectbox("Ciudad", [c for c in hotels_and_cruises["hoteles"].keys()])
        hotel_remove = st.selectbox("Hotel", hotels_and_cruises["hoteles"].get(city_remove, []))
        if st.form_submit_button("Eliminar hotel"):
            hotels_and_cruises["hoteles"][city_remove].remove(hotel_remove)
            if not hotels_and_cruises["hoteles"][city_remove]:
                del hotels_and_cruises["hoteles"][city_remove]
            save_json(HOTELS_FILE, hotels_and_cruises)
            st.success("Hotel eliminado.")
            st.rerun()
    st.markdown("---")
    st.subheader("Cruises")
    for category, cruise_list in hotels_and_cruises["cruises"].items():
        st.markdown(f"**{category} Cruises**")
        for cruise in cruise_list:
            st.write(f"- {cruise['departure']} → {cruise['route']}")
    st.markdown("---")
    st.subheader("Add cruise")
    with st.form("add_cruise"):
        category = st.selectbox("Category", ["5/4", "6/5"])
        departure = st.text_input("Departure")
        route = st.text_input("Route")
        if st.form_submit_button("Agregar cruise"):
            if departure and route:
                hotels_and_cruises["cruises"].setdefault(category, [])
                hotels_and_cruises["cruises"][category].append({"departure": departure, "route": route})
                save_json(HOTELS_FILE, hotels_and_cruises)
                st.success("Cruise agregado.")
                st.rerun()
            else:
                st.error("Departure y route son obligatorios.")


def packages_page():
    st.title("📦 Packages")
    st.markdown("### Admin can fully edit package rules")
    for package_name, info in packages.items():
        st.subheader(package_name)
        requirements = st.text_area(f"Requirements {package_name}", value="\n".join(info["requirements"]), key=f"req_{package_name}")
        includes = st.text_area(f"Includes {package_name}", value="\n".join(info["includes"]), key=f"inc_{package_name}")
        validity = st.text_area(f"Validity {package_name}", value="\n".join(info["validity"]), key=f"val_{package_name}")
        destinations = st.text_area(f"Destinations {package_name}", value="\n".join(info["destinations"]), key=f"dest_{package_name}")
        if st.button(f"Guardar {package_name}", key=f"save_pkg_{package_name}"):
            packages[package_name]["requirements"] = [line.strip() for line in requirements.split("\n") if line.strip()]
            packages[package_name]["includes"] = [line.strip() for line in includes.split("\n") if line.strip()]
            packages[package_name]["validity"] = [line.strip() for line in validity.split("\n") if line.strip()]
            packages[package_name]["destinations"] = [line.strip() for line in destinations.split("\n") if line.strip()]
            save_json(PACKAGES_FILE, packages)
            st.success(f"Package {package_name} updated.")
            st.rerun()


def commissions_page():
    st.title("💰 Commissions")
    advisor_totals = {}
    advisor_sales = {}
    for sale in sales:
        advisor_totals[sale["Advisor"]] = advisor_totals.get(sale["Advisor"], 0) + float(sale.get("Commission", 0) or 0)
        advisor_sales[sale["Advisor"]] = advisor_sales.get(sale["Advisor"], 0) + 1
    total = summary["total_commissions"]
    st.metric("Comisión total", format_money(total))
    rows = []
    for advisor, amount in advisor_totals.items():
        rows.append({"Advisor": advisor, "Sales": advisor_sales.get(advisor, 0), "Earnings": format_money(amount)})
    st.dataframe(rows)
    st.subheader("Ventas individuales")
    st.dataframe(sales)


def statistics_page():
    st.title("📈 Statistics")
    st.metric("Best advisor", summary["best_advisor"])
    st.metric("Most sold package", summary["best_package"])
    st.metric("Most sold destination", summary["best_destination"])
    st.metric("Conversion percentage", summary["conversion_rate"])
    states = {}
    package_clients = {}
    monthly_clients = {}
    daily_performance = {}
    for client in clients:
        states[client["State"]] = states.get(client["State"], 0) + 1
        package_clients[client["Package"]] = package_clients.get(client["Package"], 0) + 1
        month = client["Registration date"][:7]
        monthly_clients[month] = monthly_clients.get(month, 0) + 1
    for sale in sales:
        day = sale["Date"][:10]
        daily_performance[day] = daily_performance.get(day, 0) + 1
    if states:
        st.subheader("Sales by state")
        st.bar_chart(states)
    if package_clients:
        st.subheader("Clients by package")
        st.pie_chart(package_clients)
    if monthly_clients:
        st.subheader("Monthly growth")
        st.line_chart(monthly_clients)
    if daily_performance:
        st.subheader("Daily performance")
        st.line_chart(daily_performance)


def sales_history_page(is_admin=True):
    st.title("📜 Sales History")
    st.markdown("### Full database of all sales")
    if sales:
        search_client = st.text_input("Buscar cliente")
        filter_advisor = st.text_input("Filtrar por asesor") if not is_admin else st.selectbox("Filtrar por asesor", ["Todos"] + [u["Name"] for u in users if u["Rol"] == "advisor"])
        filtered = sales
        if search_client:
            filtered = [s for s in filtered if search_client.lower() in s["Client"].lower()]
        if filter_advisor and filter_advisor != "Todos":
            filtered = [s for s in filtered if s["Advisor"] == filter_advisor]
        st.dataframe(filtered)
        st.markdown("---")
        if filtered:
            selected_sale = st.selectbox(
                "Seleccionar venta para borrar",
                [f"{idx + 1} - {sale['Date']} - {sale['Client']} - {sale['Package']}" for idx, sale in enumerate(filtered)],
            )
            if selected_sale:
                delete_index = int(selected_sale.split(" - ")[0]) - 1
                sale_to_delete = filtered[delete_index]
                if st.button("Borrar venta seleccionada"):
                    sales.remove(sale_to_delete)
                    save_sales(sales)
                    st.success("Venta borrada.")
                    st.rerun()
        csv_data = "Date,Client,Advisor,Package,Destination,Cruise,Hotel,Commission,Follow-up status\n"
        for row in filtered:
            csv_data += ",".join([row[k].replace(",", ";") for k in ["Date", "Client", "Advisor", "Package", "Destination", "Cruise", "Hotel", "Commission", "Follow-up status"]]) + "\n"
        st.download_button("Export CSV", csv_data, file_name="sales_history.csv", mime="text/csv")
    else:
        st.info("No hay ventas registradas aún.")


def settings_page():
    st.title("⚙️ Settings")
    st.subheader("Work schedules")
    new_schedules = {}
    for zona, hora in config["horarios"].items():
        new_schedules[zona] = st.text_input(f"Horario {zona}", value=hora, key=f"hora_{zona}")
    st.subheader("Zones")
    zones_text = st.text_area("Mapa de zonas (estado: zona)", value=json.dumps(config["zones"], ensure_ascii=False, indent=2), height=220)
    st.subheader("Commission percentage")
    percentage_default = st.number_input("Porcentaje (%)", 0.0, 100.0, value=config.get("porcentaje_default", 0.06) * 100)
    if st.button("Guardar configuración"):
        try:
            config["zones"] = json.loads(zones_text)
            config["horarios"] = new_schedules
            config["porcentaje_default"] = percentage_default / 100
            save_json(CONFIG_FILE, config)
            st.success("Configuración guardada.")
        except json.JSONDecodeError:
            st.error("Zona mapping debe ser JSON válido")


def permissions_page():
    st.title("🔐 Permissions")
    matrix = config.get("permission_matrix", DEFAULT_CONFIG["permission_matrix"])
    st.markdown("### Permission examples")
    table = []
    for perm_key, values in matrix.items():
        table.append({
            "Permission": PERMISSION_DESCRIPTIONS.get(perm_key, perm_key),
            "Advisor": values.get("advisor"),
            "Admin": values.get("admin"),
        })
    st.dataframe(table)


# -----------------------------------
# PÁGINAS ADVISOR
# -----------------------------------

def advisor_home():
    st.title("🏠 Home")
    st.metric("Daily sales", summary["sales_today"])
    st.metric("Pending follow-ups", summary["pending_followups"])
    st.metric("Personal commission", format_money(summary["advisor_commission"]))
    st.markdown("---")
    st.subheader("Latest clients")
    my_clients = [c for c in clients if c["Assigned advisor"] == name]
    st.dataframe(my_clients[-5:])


def new_client_page():
    st.title("📞 New Client")
    with st.form("new_client"):
        full_name = st.text_input("Name")
        state = st.text_input("State")
        age = st.number_input("Age", min_value=18, max_value=100, value=30)
        marital_status = st.selectbox("Marital status", ["Casado / Convive", "Mujer Soltera", "Hombre Soltero"])
        residency = st.selectbox("Residency", ["Sí", "No"])
        children_count = st.number_input("Children count", min_value=0, max_value=10, value=0)
        children_ages = st.text_input("Children ages (comma separated)")
        interest = st.selectbox("Interest level", ["High", "Medium", "Low"])
        preferred_package = st.selectbox("Preferred package", ["VDL", "HÍBRIDO", "MIX & MATCH"])
        if st.form_submit_button("Guardar cliente"):
            qualification = calculate_qualification({
                "Residency": residency,
                "Marital status": marital_status,
                "Age": age,
                "Children ages": children_ages,
            })
            package = preferred_package if qualification == preferred_package else qualification
            if package == "No qualify":
                package = "MIX & MATCH"
            destination = "Cancún" if package == "VDL" else "Las Vegas" if package == "HÍBRIDO" else "Bahamas"
            client_id = str(len(clients) + 1)
            clients.append({
                "ID": client_id,
                "Full name": full_name,
                "State": state,
                "Age": str(age),
                "Marital status": marital_status,
                "Residency": residency,
                "Children count": str(children_count),
                "Children ages": children_ages,
                "Assigned advisor": name,
                "Qualification result": qualification,
                "Package": package,
                "Destination": destination,
                "Follow-up status": "Interested",
                "Notes": f"Interest: {interest}",
                "Registration date": today_str(),
            })
            save_clients(clients)
            st.success("Cliente registrado.")
            if qualification != "No qualify":
                st.success(f"Califica para {qualification}.")
            else:
                st.warning("No califica para VDL / HÍBRIDO. Enviar a MIX & MATCH.")
            st.rerun()


def registered_clients_page():
    st.title("📋 Registered Clients")
    my_clients = [c for c in clients if c["Assigned advisor"] == name]
    search_name = st.text_input("Buscar cliente")
    if search_name:
        my_clients = [c for c in my_clients if search_name.lower() in c["Full name"].lower()]
    st.dataframe(my_clients)
    st.markdown("---")
    st.subheader("Update status or add notes")
    client_ids = [c["ID"] for c in my_clients]
    if client_ids:
        selected_id = st.selectbox("Select client", client_ids)
        client = next((c for c in my_clients if c["ID"] == selected_id), None)
        if client:
            new_status = st.selectbox("Follow-up status", config["follow_up_status"], index=config["follow_up_status"].index(client["Follow-up status"]) if client["Follow-up status"] in config["follow_up_status"] else 0)
            new_note = st.text_area("Add note")
            if st.button("Guardar cambios"):
                client["Follow-up status"] = new_status
                if new_note:
                    client["Notes"] = client["Notes"] + "\n" + new_note if client["Notes"] else new_note
                save_clients(clients)
                st.success("Cliente actualizado.")
                st.rerun()
    else:
        st.info("No tienes clientes registrados aún.")


def destinations_cruises_page():
    st.title("🌴 Destinations & Cruises")
    st.markdown("### Destinations")
    for city, hotel_list in hotels_and_cruises["hoteles"].items():
        st.write(f"**{city}**")
        for hotel in hotel_list:
            st.write(f"- {hotel}")
    st.markdown("---")
    st.markdown("### Cruises")
    for category, cruise_list in hotels_and_cruises["cruises"].items():
        st.write(f"**{category}**")
        for cruise in cruise_list:
            st.write(f"- {cruise['departure']} → {cruise['route']}")


def package_qualification_page():
    st.title("📦 Package Qualification")
    with st.form("qualification_form"):
        age = st.number_input("Age", min_value=18, max_value=100, value=30)
        marital_status = st.selectbox("Marital status", ["Casado / Convive", "Mujer Soltera", "Hombre Soltero"])
        residency = st.selectbox("Residency", ["Sí", "No"])
        children_ages = st.text_input("Children ages (comma separated)")
        if st.form_submit_button("Calcular calificación"):
            qualification = calculate_qualification({
                "Residency": residency,
                "Marital status": marital_status,
                "Age": age,
                "Children ages": children_ages,
            })
            if qualification == "No qualify":
                st.warning("No califica para VDL / HÍBRIDO. Enviar a MIX & MATCH.")
            else:
                st.success(f"Califica para {qualification}.")
            if qualification == "VDL":
                st.write("Destinations: Cancun, Punta Cana, Puerto Vallarta, Los Cabos, Costa Rica, Bahamas")
            elif qualification == "HÍBRIDO":
                st.write("Destinations: Cancun, Las Vegas, Orlando")
            else:
                st.write("Destinations: USA, Canada, Bahamas, Mexico")


def my_commissions_page():
    st.title("💰 My Commissions")
    advisor_sales = [s for s in sales if s["Advisor"] == name]
    daily = sum(1 for s in advisor_sales if s["Date"].startswith(today_str()))
    weekly = sum(1 for s in advisor_sales if datetime.strptime(s["Date"], "%Y-%m-%d %H:%M:%S").isocalendar()[1] == datetime.now().isocalendar()[1]) if advisor_sales else 0
    monthly = sum(1 for s in advisor_sales if s["Date"][0:7] == today_str()[0:7])
    total = sum(float(s.get("Commission", 0) or 0) for s in advisor_sales)
    st.metric("Daily commission", format_money(sum(float(s.get("Commission", 0) or 0) for s in advisor_sales if s["Date"].startswith(today_str()))))
    st.metric("Weekly commission", format_money(sum(float(s.get("Commission", 0) or 0) for s in advisor_sales if datetime.strptime(s["Date"], "%Y-%m-%d %H:%M:%S").isocalendar()[1] == datetime.now().isocalendar()[1])))
    st.metric("Monthly commission", format_money(sum(float(s.get("Commission", 0) or 0) for s in advisor_sales if s["Date"][0:7] == today_str()[0:7])))
    st.metric("Total earnings", format_money(total))
    st.metric("Sales count", len(advisor_sales))
    st.metric("Commission percentage", f"{int(config.get('porcentaje_default', 0.06)*100)}%")
    st.markdown("---")
    st.dataframe(advisor_sales)


def my_statistics_page():
    st.title("📈 My Statistics")
    my_clients = [c for c in clients if c["Assigned advisor"] == name]
    total_clients = len(my_clients)
    closed_sales = sum(1 for c in my_clients if c["Follow-up status"] == "Closed sale")
    lost_clients = sum(1 for c in my_clients if c["Follow-up status"] == "No answer")
    best_destination = "N/A"
    destination_counts = {}
    for c in my_clients:
        destination_counts[c["Destination"]] = destination_counts.get(c["Destination"], 0) + 1
    if destination_counts:
        best_destination = max(destination_counts, key=destination_counts.get)
    st.metric("Registered clients", total_clients)
    st.metric("Closed sales", closed_sales)
    st.metric("Lost clients", lost_clients)
    st.metric("Best destination", best_destination)
    st.markdown("---")
    st.bar_chart(destination_counts)


def followups_page():
    st.title("🗓️ Follow-ups")
    follow_up_clients = [c for c in clients if c["Assigned advisor"] == name and c["Follow-up status"] in ["Pending call", "Follow-up"]]
    if follow_up_clients:
        st.dataframe(follow_up_clients)
    else:
        st.info("No pending follow-ups.")
    st.markdown("---")
    st.subheader("Update follow-up")
    ids = [c["ID"] for c in follow_up_clients]
    if ids:
        selected = st.selectbox("Seleccionar cliente", ids)
        client = next((c for c in follow_up_clients if c["ID"] == selected), None)
        if client:
            new_status = st.selectbox("Nuevo estado", config["follow_up_status"], index=config["follow_up_status"].index(client["Follow-up status"]))
            note = st.text_area("Agregar nota")
            if st.button("Guardar seguimiento"):
                client["Follow-up status"] = new_status
                if note:
                    client["Notes"] += "\n" + note if client["Notes"] else note
                save_clients(clients)
                st.success("Seguimiento actualizado.")
                st.rerun()


def my_profile_page():
    st.title("⚙️ My Profile")
    user = get_user(username, users)
    st.write(f"**Usuario:** {user['Usuario']}")
    st.write(f"**Nombre:** {user['Name']}")
    st.write(f"**Rol:** {user['Rol']}")
    with st.form("profile_form"):
        new_password = st.text_input("Nueva contraseña", type="password")
        if st.form_submit_button("Actualizar contraseña"):
            if new_password:
                user["Password"] = new_password
                save_users(users)
                st.success("Contraseña actualizada.")
            else:
                st.error("Ingresa una nueva contraseña.")


# -----------------------------------
# RUTEO PRINCIPAL
# -----------------------------------

if role == "admin":
    if page == "📊 Dashboard":
        dashboard_page()
    elif page == "👥 Users":
        users_page()
    elif page == "📞 Clients":
        clients_page()
    elif page == "🛒 Sales":
        sales_page()
    elif page == "🏨 Hotels & Cruises":
        hotels_cruises_page()
    elif page == "📦 Packages":
        packages_page()
    elif page == "💰 Commissions":
        commissions_page()
    elif page == "📈 Statistics":
        statistics_page()
    elif page == "📜 Sales History":
        sales_history_page(is_admin=True)
    elif page == "⚙️ Settings":
        settings_page()
else:
    if page == "🏠 Home":
        advisor_home()
    elif page == "📞 New Client":
        new_client_page()
    elif page == "🛒 New Sale":
        sales_page()
    elif page == "📋 Registered Clients":
        registered_clients_page()
    elif page == "🌴 Destinations & Cruises":
        destinations_cruises_page()
    elif page == "📦 Package Qualification":
        package_qualification_page()
    elif page == "💰 My Commissions":
        my_commissions_page()
    elif page == "📈 My Statistics":
        my_statistics_page()
    elif page == "🗓️ Follow-ups":
        followups_page()
    elif page == "📝 Sales History":
        sales_history_page(is_admin=False)
    elif page == "⚙️ My Profile":
        my_profile_page()
