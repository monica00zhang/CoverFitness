import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import time
from PromptEngineer import AIFitnessCoach, AIHealthCoach

# Set page configuration
st.set_page_config(
    page_title="AI Fitness Assistant",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }

    .card-header {
        border-bottom: 1px solid #e9ecef;
        padding-bottom: 10px;
        margin-bottom: 15px;
        font-weight: bold;
    }

    .nav-btn {
        border-radius: 5px;
        padding: 10px 15px;
        margin: 5px;
    }

    .centered {
        display: flex;
        justify-content: center;
    }

    .exercise-card {
        background-color: white;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }

    .meal-card {
        background-color: #f1f8e9;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Initialize session state variables if they don't exist
if 'page' not in st.session_state:
    st.session_state.page = 'home'

if 'user_data' not in st.session_state:
    st.session_state.user_data = {}

if 'fitness_coach' not in st.session_state:
    st.session_state.fitness_coach = AIFitnessCoach()
if 'fitness_plan_step' not in st.session_state:
    st.session_state.fitness_plan_step = 1
if 'has_fitness_plan' not in st.session_state:
    st.session_state.has_fitness_plan = False
if 'fitness_plan_storage' not in st.session_state:
    st.session_state.fitness_plan_storage = {}  # key: plan_id or tag, value: plan_data

if 'nutritiest' not in st.session_state:
    st.session_state.nutritiest = AIHealthCoach()
if 'has_meal_plan' not in st.session_state:
    st.session_state.has_meal_plan = False
if 'meal_plan_storage' not in st.session_state:
    st.session_state.meal_plan_storage = {}  # key: plan_id or tag, value: plan_data



# Navigation functions
def set_page(page_name):
    st.session_state.page = page_name


def next_step():
    st.session_state.fitness_plan_step += 1


def prev_step():
    st.session_state.fitness_plan_step -= 1


def reset_steps():
    st.session_state.fitness_plan_step = 1


def store_fitness_plan(new_plan):
    # Storage the plan
    plan_id = f"plan_{int(time.time())}"

    # save to session_state
    st.session_state.fitness_plan_storage[plan_id] = new_plan
    st.session_state.has_fitness_plan = True
    st.session_state.current_plan_id = plan_id  # This is correctly tracking the ID

def get_current_plan():
    # Use the current plan ID to get the latest plan directly
    if hasattr(st.session_state, 'current_plan_id') and st.session_state.current_plan_id in st.session_state.fitness_plan_storage:
        return st.session_state.fitness_plan_storage[st.session_state.current_plan_id]
    elif st.session_state.fitness_plan_storage:
        # Fallback to the last added plan if ID is missing
        latest_plan_id, latest_plan = list(st.session_state.fitness_plan_storage.items())[-1]
        st.session_state.current_plan_id = latest_plan_id  # Update the ID
        return latest_plan
    return None  # Return None if no plans exist

def store_meal_plan(new_plan):
    # Storage the plan
    plan_id = f"plan_{int(time.time())}"
    # save to session_state
    st.session_state.meal_plan_storage[plan_id] = new_plan
    st.session_state.has_meal_plan = True
    st.session_state.current_meal_plan_id = plan_id

def get_current_meal_plan():
    latest_plan_id, latest_plan = list(st.session_state.meal_plan_storage.items())[-1]
    return latest_plan

# Sidebar navigation
def display_sidebar():
    with st.sidebar:
        st.title("💪 AI Fitness Assistant")

        st.divider()

        # Main navigation
        st.header("Main Menu")
        if st.button("🏋️‍♀️ Fitness Planner", use_container_width=True):
            set_page('fitness_planner')


        if st.button("📊 Progress Tracker", use_container_width=True):
            set_page('progress_tracker')

        st.divider()

        # Only show these options if a plan exists
        if st.session_state.has_fitness_plan:
            st.header("Your Plan")
            st.info("Plan created on: 2025-04")




# Home page
def display_home():
    st.title("Welcome to Cover-Fitness Assistant! 🏆")

    st.markdown("""
    <div class="card">
        <h3>How It Works</h3>
        <p>This AI-powered fitness assistant helps you create a personalized workout and nutrition plan based on your goals, preferences, and health status.</p>
        <ul>
            <li><b>Fitness Planner:</b> Create a new fitness plan tailored to your needs</li>
            <li><b>Progress Tracker:</b> Update your plan based on your progress and feedback</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="card">
            <div class="card-header">🏋️‍♀️ Create Fitness Plan</div>
            <p>Get a personalized workout and meal plan based on your goals, fitness level, and preferences.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start Fitness Planner", key="start_planner", use_container_width=True):
            set_page('fitness_planner')

    with col2:
        st.markdown("""
        <div class="card">
            <div class="card-header">📊 Track Progress</div>
            <p>Update your plan by providing feedback on your workouts and meals.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Go to Progress Tracker", key="start_tracker", use_container_width=True):
            set_page('progress_tracker')


# Fitness Planner pages
def display_fitness_planner():
    st.title("🏋️‍♀️ Personal Fitness Planner")

    # If we already have a plan, show the dashboard
    if st.session_state.has_fitness_plan:
        display_fitness_dashboard()
    else:
        # Otherwise show the multi-step form
        display_fitness_planner_steps()

def display_fitness_dashboard():
    st.subheader("Your Fitness Dashboard")

    # Health metrics section
    st.markdown("<div class='card'><div class='card-header'>Health Assessment</div>", unsafe_allow_html=True)

    #
    if 'health_data' in st.session_state:
        health_data = st.session_state.health_data
    else:
        st.warning("Health data not found. Please complete the health assessment.")
        return

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.metric("BMI", f"{health_data['bmi']:.1f}", "Normal range")
    with col2:
        st.metric("Risk Level", health_data['risk_level'])
    with col3:
        st.metric("Goal Feasibility", "High")

    # Radar chart for risks
    fig = go.Figure()
    categories = list(health_data['risks'].keys())
    values = list(health_data['risks'].values())

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Risk Factors'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

    for rec in health_data['recommendations']:
        st.info(rec)

    st.markdown("</div>", unsafe_allow_html=True)

    # Workout plan section
    st.markdown("<div class='card'><div class='card-header'>Your Workout Plan</div>", unsafe_allow_html=True)

    # Workout Plan
    if 'fitness_plan_storage' in st.session_state and st.session_state.fitness_plan_storage:
        workout_plan = get_current_plan()
    else:
        st.warning("No saved workout plan found. Please generate one first.")
        return

    # 展示计划
    # display each day
    for day_plan in workout_plan['weekly_plan']:
        day = day_plan['day']
        exercises = day_plan['exercises']
        total_duration = day_plan['total_duration']
        total_calories = day_plan['total_calories']

        with st.expander(f"💪 {day} Plan ({total_duration} min · 🔥 {round(total_calories)} kcal)"):
            for i, ex in enumerate(exercises, 1):
                st.markdown(f"""
                        <div style='padding: 10px; border-left: 4px solid #4CAF50; margin-bottom: 10px; background-color: #f9f9f9;'>
                            <b>{i}. {ex['name']}</b><br>
                            ⏱️ Duration: {ex['duration_min']} min<br>
                            🔥 Calories Burned: {ex['calories_burned']} kcal<br>
                            🎯 Target Muscle: {ex['target_muscle']}
                        </div>
                    """, unsafe_allow_html=True)

                st.markdown(
                    f"<b>Total Time:</b> {total_duration} min &nbsp;&nbsp;&nbsp; <b>Total Calories:</b> {round(total_calories)} kcal",
                    unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Meal plan section
    st.markdown("<div class='card'><div class='card-header'>Your Meal Plan</div>", unsafe_allow_html=True)

    # get current workout plan
    # Create tabs for each day of the week
    if 'meal_plan_storage' in st.session_state and st.session_state.meal_plan_storage:
        meal_plan = get_current_meal_plan()
    else:
        st.warning("No saved workout plan found. Please generate one first.")
        return
    days = list(meal_plan.keys())
    tabs = st.tabs(days)

    # Display content for each day
    for i, day in enumerate(days):
        with tabs[i]:
            day_data = meal_plan[day]

            # Display day summary in columns
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Calories", day_data.get("Total_Calories", "N/A"))
            with col2:
                st.markdown(f"**Macro Distribution:**  \n{day_data.get('Macro_Distribution', 'N/A')}")
            with col3:
                st.markdown(f"**Exercise:**  \n{day_data.get('Exercise', 'Rest day')}")

            # Display hydration information
            st.info(f"💧 {day_data.get('Hydration', 'Stay hydrated throughout the day')}")

            # Display meals in expandable sections
            st.markdown("### Meals")
            meals = day_data.get("Meals", {})

            for meal_name, meal_data in meals.items():
                with st.expander(f"{meal_name}: {meal_data.get('Menu', '')}"):
                    st.markdown(f"**Macros:** {meal_data.get('Macros', 'Not specified')}")

                    # Display any additional meal details if present
                    for key, value in meal_data.items():
                        if key not in ["Menu", "Macros"]:
                            st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")

    st.markdown("</div>", unsafe_allow_html=True)

    # Button to start over
    if st.button("Create New Fitness Plan", use_container_width=True):
        reset_steps()
        set_page('fitness_planner')
        st.session_state.has_fitness_plan = False
        st.rerun()

def display_fitness_planner_steps():
    # Progress bar
    total_steps = 4
    current_step = st.session_state.fitness_plan_step
    progress = current_step / total_steps

    st.progress(progress)
    st.write(f"Step {current_step} of {total_steps}")

    # Dynamic step content
    if current_step == 1:
        display_step1_user_data()
    elif current_step == 2:
        display_step2_health_risk()
    elif current_step == 3:
        display_step3_goal_feasibility()
    elif current_step == 4:
        display_step4_generate_plan()

    # Navigation buttons
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if current_step > 1:
            if st.button("← Previous", key="prev_btn", use_container_width=True):
                prev_step()
                st.rerun()

    with col3:
        if current_step < total_steps:
            if st.button("Next →", key="next_btn", use_container_width=True):
                # Save form data would happen here
                next_step()
                st.rerun()
        else:
            if st.button("Finish", key="finish_btn", type="primary", use_container_width=True):
                st.session_state.has_fitness_plan = True
                reset_steps()
                st.rerun()


def display_step1_user_data():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("1. Tell Us About Yourself")

    # Personal information
    st.write("#### Personal Information")
    col1, col2 = st.columns(2)

    with col1:
        age = st.number_input("Age", min_value=18, max_value=100, value=30)
        height = st.number_input("Height (cm)", min_value=100, max_value=250, value=170)

    with col2:
        gender = st.selectbox("Gender", ["Male", "Female", "Non-binary", "Prefer not to say"])
        weight = st.number_input("Weight (kg)", min_value=30, max_value=300, value=70)

    # Dietary preferences
    st.write("#### Dietary Preferences")
    dietary_prefs = st.multiselect(
        "Select your dietary preferences",
        ["Vegetarian", "Vegan", "Pescatarian", "Keto", "Paleo", "Gluten-free", "Dairy-free"]
    )
    dietary_notes = st.text_area("Additional dietary notes or allergies", height=100)

    # Fitness level
    st.write("#### Fitness Experience")
    fitness_level = st.select_slider(
        "Fitness Level",
        options=["Beginner", "Intermediate", "Advanced"],
        value="Beginner"
    )

    # Goals
    st.write("#### Your Goals")

    goal_type = st.selectbox(
        "What is your primary goal?",
        ["Lose weight", "Gain muscle", "Improve fitness", "Rehabilitation"]
    )

    if goal_type == "Lose weight" or goal_type == "Gain muscle":
        col1, col2 = st.columns(2)
        with col1:
            target_number = st.number_input(
                f"Target {'loss' if goal_type == 'Lose weight' else 'gain'} (kg)",
                min_value=1,
                max_value=50,
                value=5
            )
        with col2:
            target_months = st.number_input(
                "Timeframe (months)",
                min_value=1,
                max_value=24,
                value=3
            )

    focus_areas = st.multiselect(
        "Focus Areas (max 3)",
        ["Neck", "Lower back", "Wrists", "Shoulders", "Hips", "Knees", "Ankles and feet", "Upper back"],
        max_selections=3
    )

    constraints = st.multiselect(
        "Do you have any constraints?",
        ["Joint injury", "Back pain", "Limited mobility", "Heart condition", "Diabetes", "High blood pressure", "None"]
    )

    # Available time
    st.write("#### Available Time")

    workout_days = st.multiselect(
        "Which days can you workout?",
        ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        default=["Monday", "Wednesday", "Friday"]
    )

    workout_duration = st.slider(
        "How long can you workout per session?",
        min_value=15,
        max_value=120,
        value=45,
        step=15,
        format="%d minutes"
    )

    # Workout preferences
    st.write("#### Workout Preferences")

    workout_preferences = st.multiselect(
        "What types of workouts do you prefer?",
        ["Weight training", "Cardio", "HIIT", "Yoga", "Pilates", "Bodyweight", "Swimming", "Running", "Cycling"],
        default=["Weight training", "Cardio"]
    )

    # Save data to session state
    if st.button("Save Information", use_container_width=True):
        st.session_state.user_data = {
            'age': age,
            'gender': gender,
            'height': height,
            'weight': weight,
            'dietary_preferences': dietary_prefs,
            'dietary_notes': dietary_notes,
            'fitness_level': fitness_level,
            'goal_type': goal_type,
            'target_weight': weight - target_number if goal_type == "Lose weight" else weight + target_number,
            'target_months': target_months,
            'focus_areas': focus_areas,
            'constraints': constraints,
            'workout_days': workout_days,
            'workout_duration': workout_duration,
            'workout_preferences': workout_preferences
        }
        st.success("Information saved!")

    st.markdown("</div>", unsafe_allow_html=True)



def display_step2_health_risk():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("2. Health Risk Assessment")

    # This would normally use actual user data from session state
    if not st.session_state.user_data:
        st.warning("Please complete the previous step first.")
        return

    # Mock up a health assessment
    health_data = st.session_state.fitness_coach.health_risk_assessment(st.session_state.user_data)
    st.session_state.health_data = health_data

    # Display BMI
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Your BMI", f"{health_data['bmi']:.1f}")
        st.write(f"Category: **{health_data['bmi_category']}**")

    with col2:
        st.metric("Overall Risk Level", health_data['risk_level'])

        # Color code based on risk level
        risk_color = {
            'Low': 'green',
            'Moderate': 'orange',
            'High': 'red'
        }.get(health_data['risk_level'], 'blue')

        st.markdown(f"<p style='color: {risk_color};'>This assessment is based on the information you provided.</p>",
                    unsafe_allow_html=True)

    # Radar chart for risk visualization
    st.write("#### Risk Factors Analysis")

    fig = go.Figure()
    categories = list(health_data['risks'].keys())
    values = list(health_data['risks'].values())

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Risk Factors'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

    # Recommendations
    st.write("#### Recommendations")
    for rec in health_data['recommendations']:
        st.info(rec)

    st.markdown("</div>", unsafe_allow_html=True)



def display_step3_goal_feasibility():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("3. Goal Feasibility Assessment")

    # Check if user data exists
    if not st.session_state.user_data:
        st.warning("Please complete the previous steps first.")
        return

    # Get goal feasibility data - would normally be calculated from AIFitnessCoach
    feasibility = st.session_state.fitness_coach.enhanced_goal_feasibility(st.session_state.user_data)

    # Display goal feasibility
    if feasibility['is_feasible']:
        st.success("✅ Your goal appears to be realistic and achievable!")
    else:
        st.warning(
            f"⚠️ Your goal timeline may be too aggressive. We suggest {feasibility['suggested_timeframe']} months instead of {st.session_state.user_data.get('target_months', 3)} months.")

    st.write(feasibility['advice'])

    # Visual comparison chart
    st.write("#### Goal Timeline Comparison")

    # Create a progress timeline chart
    # Fill in the gaps for a smooth line
    target_months = st.session_state.user_data['target_months']
    realistic_months = feasibility['suggested_timeframe']
    timeline =  (target_months if target_months >= realistic_months else realistic_months)+1

    current_weight = st.session_state.user_data['weight']
    target_weight = st.session_state.user_data['target_weight']

    df = pd.DataFrame({
        'Month': [i for i in range(timeline)],
        'Target Plan': [st.session_state.user_data['weight']] +
                       [None] * (timeline - 2) +
                       [st.session_state.user_data['target_weight']],
        'Realistic Plan': [st.session_state.user_data['weight']] +
                       [None] * (timeline - 2) +
                       [st.session_state.user_data['target_weight']]
    })

    # Target plan line - straight line to goal
    for i in range(1, target_months):
        progress_pct = i / target_months
        df.loc[df['Month'] == i, 'Target Plan'] = current_weight - (current_weight - target_weight) * progress_pct

    # Realistic plan line - slightly curved approach
    for i in range(1, realistic_months+1):
        # Slower at first, faster later
        if i < realistic_months / 2:
            progress_pct = (i / realistic_months) * 0.8
        else:
            progress_pct = (i / realistic_months) * 1.2
            if progress_pct > 1:
                progress_pct = 1

        df.loc[df['Month'] == i, 'Realistic Plan'] = current_weight - (current_weight - target_weight) * progress_pct
    df.loc[realistic_months + 1:, 'Realistic Plan'] = np.nan

    fig = px.line(df, x='Month', y=['Target Plan', 'Realistic Plan'],
                  title='Weight Change Over Time',
                  labels={'value': 'Weight (kg)', 'variable': 'Plan Type'})

    st.plotly_chart(fig, use_container_width=True)

    # Adjust goal if necessary
    st.write("#### Adjust Your Goal")

    col1, col2 = st.columns(2)
    with col1:
        adjusted_target = st.number_input(
            "Target Weight (kg)",
            min_value=30.0,
            max_value=200.0,
            value=float(st.session_state.user_data.get('target_weight', 65)),
            step=0.5
        )

    with col2:
        adjusted_months = st.number_input(
            "Target Timeframe (months)",
            min_value=1,
            max_value=24,
            value=feasibility['suggested_timeframe']
        )

    if st.button("Update Goal", use_container_width=True):
        st.session_state.user_data['target_weight'] = adjusted_target
        st.session_state.user_data['target_months'] = adjusted_months
        st.success("Goal updated!")

    st.markdown("</div>", unsafe_allow_html=True)


def display_step4_generate_plan():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("4. Generate Your Personalized Plans")

    if not st.session_state.user_data:
        st.warning("Please complete the previous steps first.")
        return

    st.write("We're ready to generate your personalized fitness and meal plans based on your profile!")

    # Summary of inputs
    st.write("#### Your Profile Summary")

    user_data = st.session_state.user_data

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Current Weight", f"{user_data.get('weight', 70)} kg")
    with col2:
        st.metric("Target Weight", f"{user_data.get('target_weight', 65)} kg")
    with col3:
        st.metric("Timeframe", f"{user_data.get('target_months', 3)} months")

    st.write(f"**Goal:** {user_data.get('goal_type', 'Improve fitness')}")
    st.write(f"**Focus Areas:** {', '.join(user_data.get('focus_areas', ['General fitness']))}")
    st.write(f"**Workout Days:** {', '.join(user_data.get('workout_days', ['Monday', 'Wednesday', 'Friday']))}")

    # Generate button
    st.write("#### Generate Plans")
    st.write("Click the button below to generate your personalized workout and meal plans.")

    if st.button("Generate My Plans!", type="primary", use_container_width=True):
        with st.spinner("Creating your personalized plans..."):
            # This would normally use st.session_state.fitness_coach to generate plans
            # Mock progress bar to simulate AI processing
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress_bar.progress(i + 1)

            ## workout
            cur_workout_plan = st.session_state.fitness_coach.generate_workout_plan(st.session_state.user_data)
            store_fitness_plan(cur_workout_plan)

            ## meal
            meal_plan = st.session_state.nutritiest.generate_meal_plan(st.session_state.user_data, cur_workout_plan)
            store_meal_plan(meal_plan)

            st.success("Your personalized plans have been generated!")


    st.markdown("</div>", unsafe_allow_html=True)


# Progress Tracker pages
def display_progress_tracker():
    st.title("📊 Progress Tracker")

    if not st.session_state.has_fitness_plan:
        st.warning("You don't have an active fitness plan. Please create one first.")
        if st.button("Create Fitness Plan", use_container_width=True):
            set_page('fitness_planner')
            st.rerun()
        return

    st.subheader("Update Your Progress & Get Plan Adjustments")

    tab1, tab2 = st.tabs(["Workout Tracker",  "Adjust Plan"])

    with tab1:
        display_workout_feedback()

    with tab2:
        display_plan_update()


def display_workout_feedback():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Workout Feedback")


    # Load the newest plan
    plan = get_current_plan()

    # Mock workout data
    workout_days = st.session_state.user_data['workout_days']
    selected_day = st.selectbox("Select workout day to provide feedback", workout_days)


    # 找到选中日期的训练数据
    day_plan = next((d for d in plan['weekly_plan'] if d['day'] == selected_day), None)

    if day_plan:
        st.write("#### Exercises Completed")

        exercises = day_plan['exercises']

        for exercise in exercises:
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"**{exercise['name']}**")
                st.caption(
                    f"⏱️ Duration: {exercise['duration_min']} min  \n"
                    f"🔥 Calories: {exercise['calories_burned']} kcal  \n"
                    f"🎯 Muscle: {exercise['target_muscle']}"
                )

            with col2:
                # 勾选是否完成（带 day 区分 key）
                st.checkbox("Completed", key=f"completed_{exercise['name']}_{selected_day}", value=False)

    else:
        st.warning(f"No workout found for {selected_day}")

    # Progress chart
    st.write("#### Your Weight Progress")

    # Mock progress data
    progress_dates = [(datetime.now() - timedelta(days=x * 7)).strftime('%Y-%m-%d') for x in range(4, -1, -1)]
    progress_weights = [71.5, 70.8, 70.3, 69.6, 69.0]  # Most recent last

    progress_df = pd.DataFrame({
            'Date': progress_dates,
            'Weight': progress_weights
        })

    fig = px.line(progress_df, x='Date', y='Weight',
                      title='Weight Progress Over Time',
                      markers=True)

    # Add target line
    fig.add_hline(y=65, line_dash="dash", line_color="green", annotation_text="Target")

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)



def display_plan_update():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Update Your Fitness Plan")

    st.write(
        "Based on your feedback, we can adjust your fitness and meal plans to better match your progress and preferences.")

    # Progress tracking
    st.write("#### Track Your Progress")

    col1, col2 = st.columns(2)
    with col1:
        current_weight = st.number_input(
            "Current Weight (kg)",
            min_value=30.0,
            max_value=250.0,
            value=69.0,  # Slightly lower than initial weight to show progress
            step=0.1
        )

    with col2:
        measurement_date = st.date_input(
            "Measurement Date",
            value=datetime.now()
        )

    st.write("## 📝 Update Your Fitness Plan")

    # 当前训练感受（单选）
    adjust_intensity = st.radio(
        "My current plan feels:",
        ["Too intense", "Just right", "Not challenging enough"],
        key="intensity_feedback"
    )

    # 希望增加内容（多选）
    preferred_additions = st.multiselect(
        "I'd like more:",
        ["Strength training", "Cardio options", "Mobility exercises", "Recovery guidance"],
        key="preferred_additions"
    )

    # 可视化一下用户的选择（可选）
    st.markdown("### ✅ Your Feedback Summary")
    st.markdown(f"**Feeling:** {adjust_intensity}")
    st.markdown(f"**Wants more of:** {', '.join(preferred_additions) if preferred_additions else 'Nothing specific'}")

    if st.button("Update My Plans", type="primary", use_container_width=True):
        with st.spinner("Updating your personalized plans..."):
            # This would normally use st.session_state.fitness_coach to update plans
            # Mock progress bar to simulate AI processing
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress_bar.progress(i + 1)

            # Get mock updated plan
            old_plan = get_current_plan()
            updates_plan = st.session_state.fitness_coach.adjust_workout_plan(old_plan, adjust_intensity, preferred_additions,
                                                                              st.session_state.user_data, sport_range="")
            ## push new plan in to ku
            store_fitness_plan(updates_plan)
            st.success("Your plans have been updated based on your feedback!")

            # Show summary of changes
            st.subheader("Changes Made")
            st.markdown("### Updated Workout Plan:")

            for day_plan in updates_plan["weekly_plan"]:
                st.markdown(f"**{day_plan['day']}**")

                for exercise in day_plan['exercises']:
                    st.markdown(
                        f"- **{exercise['name']}**: {exercise['duration_min']} min, {exercise['calories_burned']} kcal, Target Muscle: {exercise['target_muscle']}")

                st.markdown(
                    f"**Total Duration**: {day_plan['total_duration']} min, **Total Calories**: {round(day_plan['total_calories'], 2)} kcal")

                # 加入分隔线，强调每一天的结束
                st.markdown("---")

            # 突显更新
            st.markdown(
                "<br><div style='background-color: #dff0d8; padding: 10px; border-radius: 5px;'><strong>Plan updated successfully!</strong></div>",
                unsafe_allow_html=True)

            # 可以再加一个总结：
            total_weekly_calories = sum(day['total_calories'] for day in updates_plan['weekly_plan'])
            st.success(f"🔥 Total Estimated Weekly Burn: {round(total_weekly_calories)} kcal")



    st.markdown("</div>", unsafe_allow_html=True)


# Main app logic
def main():
    display_sidebar()

    # Display the appropriate page based on session state
    if st.session_state.page == 'home':
        display_home()
    elif st.session_state.page == 'fitness_planner':
        display_fitness_planner()
    elif st.session_state.page == 'progress_tracker':
        display_progress_tracker()


if __name__ == "__main__":
    main()