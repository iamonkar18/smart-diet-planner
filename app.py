import random
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from utils import (
    calculate_bmr,
    activity_multiplier,
    calorie_target,
    macro_targets,
    bmi_and_category,
    today_str,
)
from foods import build_full_day_plan
from profiles import get_usernames, get_user, create_user
from tracking import (
    save_weight,
    load_weight,
    save_calories,
    load_calories,
    save_note,
    load_notes,
)
from export_pdf import build_pdf


# ------------- THEME --------------

def apply_theme():
    theme = st.session_state.get("theme", "Light")
    if theme == "Dark":
        st.markdown(
            """
            <style>
            body { background-color: #111827; color: #e5e7eb; }
            .stApp { background-color: #111827; color: #e5e7eb; }
            </style>
            """,
            unsafe_allow_html=True,
        )


# ------------- SESSION INIT -------------

if "theme" not in st.session_state:
    st.session_state["theme"] = "Light"

if "meal_seeds" not in st.session_state:
    st.session_state["meal_seeds"] = {
        "breakfast": random.randint(0, 1_000_000),
        "lunch": random.randint(0, 1_000_000),
        "snack": random.randint(0, 1_000_000),
        "dinner": random.randint(0, 1_000_000),
    }

if "current_plan" not in st.session_state:
    st.session_state["current_plan"] = pd.DataFrame()

apply_theme()

st.set_page_config(page_title="Smart Diet Planner", page_icon="🥗", layout="wide")
st.title("Smart Diet Planner")


# ------------- SIDEBAR: LOGIN -------------

st.sidebar.subheader("User Login / Profile")

existing_users = get_usernames()
choice = st.sidebar.radio("Login option", ["Select existing user", "Create new user"])

username = None
profile = None

if choice == "Select existing user" and existing_users:
    username = st.sidebar.selectbox("Choose user", existing_users)
    if username:
        profile = get_user(username)
elif choice == "Create new user":
    new_username = st.sidebar.text_input("New username (no spaces)").strip()

    new_name = st.sidebar.text_input("Full name", key="new_name")
    new_age = st.sidebar.number_input(
        "Age", min_value=10, max_value=100, value=22, key="new_age"
    )
    new_gender = st.sidebar.selectbox(
        "Gender", ["Male", "Female", "Other"], key="new_gender"
    )
    new_height = st.sidebar.number_input(
        "Height (cm)", min_value=120, max_value=220, value=170, key="new_height"
    )
    new_veg_default = st.sidebar.checkbox(
        "Veg by default?", value=True, key="new_veg_default"
    )

    if st.sidebar.button("Create user"):
        if not new_username:
            st.sidebar.error("Username cannot be empty")
        else:
            try:
                profile = create_user(
                    new_username, new_name, int(new_age),
                    new_gender, float(new_height), new_veg_default
                )
                username = new_username
                st.sidebar.success("User created! Re-select from list if needed.")
            except ValueError as e:
                st.sidebar.error(str(e))

    st.info("Create or select a user from the sidebar to begin.")
    st.stop()

username = profile["username"]
st.sidebar.write(f"Logged in as **{profile['name']}** ({username})")

# ------------- SIDEBAR: SETTINGS -------------

st.sidebar.subheader("App Settings")
theme_choice = st.sidebar.selectbox("Theme", ["Light", "Dark"], index=0 if st.session_state["theme"] == "Light" else 1)
st.session_state["theme"] = theme_choice
apply_theme()

st.sidebar.subheader("Diet Inputs")

age = st.sidebar.number_input(
    "Age", 10, 100, int(profile["age"]), key="profile_age"
)
gender = st.sidebar.selectbox(
    "Gender",
    ["Male", "Female", "Other"],
    index=["Male", "Female", "Other"].index(profile["gender"]),
    key="profile_gender",
)
height_cm = st.sidebar.number_input(
    "Height (cm)", 120, 220, int(profile["height_cm"]), key="profile_height"
)
weight_kg = st.sidebar.number_input(
    "Current Weight (kg)", 30.0, 200.0, 70.0, key="profile_weight"
)

activity_level = st.sidebar.selectbox(
    "Activity Level",
    [
        "Sedentary (little or no exercise)",
        "Light (1-3 days/week)",
        "Moderate (3-5 days/week)",
        "Active (6-7 days/week)",
        "Very active (hard exercise & physical job)",
    ],
)

goal = st.sidebar.radio("Goal", ["Lose weight", "Maintain weight", "Gain weight"])
veg_only = st.sidebar.checkbox("Veg-Only Mode", value=bool(profile.get("veg_default", True)))

# Weight tracking save button
if st.sidebar.button("Save Today's Weight"):
    save_weight(username, weight_kg)
    st.sidebar.success("Weight saved!")


# ------------- MAIN: TOP CARDS -------------

col1, col2, col3, col4 = st.columns(4)

bmi, bmi_cat = bmi_and_category(weight_kg, height_cm)
with col1:
    st.metric("BMI", f"{bmi}", bmi_cat)

bmr = calculate_bmr(gender, weight_kg, height_cm, age)
with col2:
    st.metric("BMR", f"{bmr:.0f} kcal")

tdee = bmr * activity_multiplier(activity_level)
with col3:
    st.metric("TDEE", f"{tdee:.0f} kcal")

target_cal = calorie_target(tdee, goal)
with col4:
    st.metric("Target Calories", f"{target_cal:.0f} kcal", goal)


# ------------- GENERATE / REGENERATE MEALS -------------

st.markdown("### Generate / Edit Your Meal Plan")

macro = macro_targets(weight_kg, target_cal)

top_c1, top_c2, top_c3 = st.columns(3)
with top_c1:
    st.metric("Protein Target", f"{macro['protein_g']} g")
with top_c2:
    st.metric("Carbs Target", f"{macro['carbs_g']} g")
with top_c3:
    st.metric("Fats Target", f"{macro['fat_g']} g")

btn_generate = st.button("Generate Full Day Plan")

regen_cols = st.columns(4)
with regen_cols[0]:
    regen_breakfast = st.button("Regenerate Breakfast")
with regen_cols[1]:
    regen_lunch = st.button("Regenerate Lunch")
with regen_cols[2]:
    regen_snack = st.button("Regenerate Snack")
with regen_cols[3]:
    regen_dinner = st.button("Regenerate Dinner")

# Update seeds on regenerate
if regen_breakfast:
    st.session_state["meal_seeds"]["breakfast"] = random.randint(0, 1_000_000)
if regen_lunch:
    st.session_state["meal_seeds"]["lunch"] = random.randint(0, 1_000_000)
if regen_snack:
    st.session_state["meal_seeds"]["snack"] = random.randint(0, 1_000_000)
if regen_dinner:
    st.session_state["meal_seeds"]["dinner"] = random.randint(0, 1_000_000)

if btn_generate or regen_breakfast or regen_lunch or regen_snack or regen_dinner:
    plan_df = build_full_day_plan(target_cal, veg_only, st.session_state["meal_seeds"])
    st.session_state["current_plan"] = plan_df.copy()

plan_df = st.session_state["current_plan"]

if plan_df.empty:
    st.info("Click **Generate Full Day Plan** to create a meal plan.")
else:
    st.markdown("### Editable Meal Plan")
    edited_df = st.data_editor(
        plan_df,
        num_rows="dynamic",
        use_container_width=True,
        key="meal_editor",
    )
    st.session_state["current_plan"] = edited_df

    totals = edited_df[["calories", "protein_g", "carbs_g", "fat_g"]].sum()
    st.markdown("#### Daily Nutrition Summary")
    st.write(
        f"- **Calories:** {totals['calories']:.0f} kcal\n"
        f"- **Protein:** {totals['protein_g']:.1f} g\n"
        f"- **Carbs:** {totals['carbs_g']:.1f} g\n"
        f"- **Fats:** {totals['fat_g']:.1f} g"
    )

    diff = totals["calories"] - target_cal
    st.info(f"Difference from target: {diff:+.0f} kcal")

    # Pie charts
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.subheader("Macro Distribution")
        fig, ax = plt.subplots()
        labels = ["Protein", "Carbs", "Fats"]
        values = [max(totals["protein_g"], 0.1), max(totals["carbs_g"], 0.1), max(totals["fat_g"], 0.1)]
        ax.pie(values, labels=labels, autopct="%1.1f%%")
        ax.axis("equal")
        st.pyplot(fig)

    with chart_col2:
        st.subheader("Calories by Meal")
        meal_cal = edited_df.groupby("meal_type")["calories"].sum()
        fig2, ax2 = plt.subplots()
        ax2.pie(meal_cal.values, labels=meal_cal.index, autopct="%1.1f%%")
        ax2.axis("equal")
        st.pyplot(fig2)

    # Save calories
    if st.button("Save Today's Calories Summary"):
        save_calories(username, target_cal, float(totals["calories"]))
        st.success("Calorie summary saved for today.")

    # PDF export
    pdf_bytes = build_pdf(
        edited_df,
        {
            "Target Calories": f"{target_cal:.0f}",
            "Actual Calories": f"{totals['calories']:.0f}",
            "Protein (g)": f"{totals['protein_g']:.1f}",
            "Carbs (g)": f"{totals['carbs_g']:.1f}",
            "Fats (g)": f"{totals['fat_g']:.1f}",
        },
        profile["name"],
        today_str(),
    )
    st.download_button(
        "Download Plan as PDF",
        data=pdf_bytes,
        file_name=f"diet_plan_{today_str()}.pdf",
        mime="application/pdf",
    )

# ------------- TABS: WEIGHT, CALORIES, NOTES -------------

st.markdown("---")
tab1, tab2, tab3 = st.tabs(["📉 Weight Tracking", "🔥 Calorie History", "📝 Daily Notes"])

with tab1:
    st.subheader("Weight Progress")
    df_w = load_weight(username)
    if df_w.empty:
        st.info("No weight data yet. Save from the sidebar.")
    else:
        df_w = df_w.sort_values("date")
        st.dataframe(df_w, use_container_width=True)
        fig, ax = plt.subplots()
        ax.plot(df_w["date"], df_w["weight"], marker="o")
        ax.set_xlabel("Date")
        ax.set_ylabel("Weight (kg)")
        ax.set_title("Weight Over Time")
        plt.xticks(rotation=45)
        st.pyplot(fig)

with tab2:
    st.subheader("Calorie History")
    df_c = load_calories(username)
    if df_c.empty:
        st.info("No calorie data yet. Save from the main section.")
    else:
        df_c = df_c.sort_values("date")
        st.dataframe(df_c, use_container_width=True)

        # Last 7 days bar chart
        last7 = df_c.tail(7)
        st.markdown("**Last 7 entries (Actual vs Target)**")
        fig3, ax3 = plt.subplots()
        x = range(len(last7))
        ax3.bar(x, last7["target_cal"], label="Target")
        ax3.bar(x, last7["actual_cal"], bottom=0, alpha=0.6, label="Actual")
        ax3.set_xticks(x)
        ax3.set_xticklabels(last7["date"], rotation=45)
        ax3.set_ylabel("Calories")
        ax3.legend()
        st.pyplot(fig3)

with tab3:
    st.subheader("Daily Notes / Journal")
    note = st.text_area("Write your note for today")
    if st.button("Save Note"):
        save_note(username, note)
        st.success("Note saved.")
    df_n = load_notes(username)
    if df_n.empty:
        st.info("No notes yet.")
    else:
        df_n = df_n.sort_values("date", ascending=False)
        st.dataframe(df_n, use_container_width=True)

