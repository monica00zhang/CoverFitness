import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import time

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
if 'fitness_plan_step' not in st.session_state:
    st.session_state.fitness_plan_step = 1
if 'has_fitness_plan' not in st.session_state:
    st.session_state.has_fitness_plan = False
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}
if 'fitness_coach' not in st.session_state:
    # This would be replaced with your actual initialization
    # st.session_state.fitness_coach = AIFitnessCoach()
    st.session_state.fitness_coach = "placeholder"


# Navigation functions
def set_page(page_name):
    st.session_state.page = page_name


def next_step():
    st.session_state.fitness_plan_step += 1


def prev_step():
    st.session_state.fitness_plan_step -= 1


def reset_steps():
    st.session_state.fitness_plan_step = 1


# Placeholder for AIFitnessCoach functions
def mock_health_risk_assessment(user_data):
    """Placeholder function to assess health risks"""
    # In reality, this would use st.session_state.fitness_coach to analyze data
    return {
        'bmi': 23.5,
        'bmi_category': 'Normal',
        'risk_level': 'Low',
        'risks': {
            'BMI Risk': 20,
            'Joint Injury Risk': 15,
            'Cardiovascular Risk': 10,
            'Overtraining Risk': 30,
            'Nutritional Risk': 25
        },
        'recommendations': [
            'Maintain a balanced diet rich in protein and complex carbohydrates',
            'Focus on proper form during strength training',
            'Ensure adequate recovery between workouts'
        ]
    }


def mock_goal_feasibility(user_data):
    """Placeholder function to assess goal feasibility"""
    # In reality, this would use st.session_state.fitness_coach
    current_weight = user_data.get('weight', 70)
    target_weight = user_data.get('target_weight', 65)
    target_months = user_data.get('target_months', 3)

    # Mock data for visualization
    realistic_months = 4

    timeline_data = {
        'Target': [current_weight, target_weight],
        'Realistic': [current_weight, target_weight],
        'Month': [0, target_months if target_months > realistic_months else realistic_months]
    }

    return {
        'is_feasible': target_months >= realistic_months,
        'suggested_timeframe': realistic_months,
        'timeline_data': timeline_data,
        'advice': 'Based on your profile, we recommend a slightly longer timeframe to achieve your goals safely.'
    }


def mock_workout_plan():
    """Placeholder function to generate workout plan"""
    # In reality, this would use st.session_state.fitness_coach
    return {
        'Monday': [
            {'name': 'Squat', 'sets': 3, 'reps': 10, 'rpe': 7, 'img': 'squat.gif'},
            {'name': 'Push-up', 'sets': 3, 'reps': 12, 'rpe': 6, 'img': 'pushup.gif'},
            {'name': 'Plank', 'sets': 3, 'reps': '30s', 'rpe': 8, 'img': 'plank.gif'}
        ],
        'Wednesday': [
            {'name': 'Deadlift', 'sets': 3, 'reps': 8, 'rpe': 8, 'img': 'deadlift.gif'},
            {'name': 'Pull-up', 'sets': 3, 'reps': 5, 'rpe': 9, 'img': 'pullup.gif'},
            {'name': 'Russian Twist', 'sets': 3, 'reps': 20, 'rpe': 7, 'img': 'twist.gif'}
        ],
        'Friday': [
            {'name': 'Bench Press', 'sets': 3, 'reps': 10, 'rpe': 7, 'img': 'bench.gif'},
            {'name': 'Lunges', 'sets': 3, 'reps': 12, 'rpe': 6, 'img': 'lunge.gif'},
            {'name': 'Bicycle Crunch', 'sets': 3, 'reps': 20, 'rpe': 7, 'img': 'bicycle.gif'}
        ]
    }


def mock_meal_plan():
    """Placeholder function to generate meal plan"""
    # In reality, this would use st.session_state.fitness_coach
    return {
        'Monday': {
            'Breakfast': 'Oatmeal with berries and protein powder',
            'Lunch': 'Grilled chicken salad with mixed greens',
            'Dinner': 'Baked salmon with roasted vegetables',
            'Snacks': ['Greek yogurt with honey', 'Handful of almonds']
        },
        'Tuesday': {
            'Breakfast': 'Scrambled eggs with spinach and whole grain toast',
            'Lunch': 'Quinoa bowl with black beans and avocado',
            'Dinner': 'Turkey meatballs with sweet potato mash',
            'Snacks': ['Protein shake', 'Apple with peanut butter']
        }
    }


def mock_update_plan(feedback):
    """Placeholder function to update plan based on feedback"""
    # In reality, this would use st.session_state.fitness_coach
    return {
        'success': True,
        'updated_workout': mock_workout_plan(),
        'updated_meal_plan': mock_meal_plan(),
        'adjustments': [
            'Reduced workout intensity based on your recovery feedback',
            'Added more protein options to your meal plan'
        ]
    }


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
            st.info("Plan created on: 2023-05-15")

            # Quick stats
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Current Weight", "70 kg", "-2 kg")
            with col2:
                st.metric("Goal Progress", "40%", "5%")

            if st.button("Reset Plan", type="secondary", use_container_width=True):
                st.session_state.has_fitness_plan = False
                set_page('home')
                st.rerun()


# Home page
def display_home():
    st.title("Welcome to Your AI Fitness Assistant! 🏆")

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

    # Mock health metrics
    health_data = mock_health_risk_assessment(st.session_state.user_data)

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

    workout_plan = mock_workout_plan()
    days_tabs = st.tabs(list(workout_plan.keys()))

    for i, day in enumerate(workout_plan.keys()):
        with days_tabs[i]:
            for exercise in workout_plan[day]:
                col1, col2, col3 = st.columns([1, 2, 1])
                with col1:
                    # Placeholder for exercise image/gif
                    st.markdown(f"##### {exercise['name']}")
                    st.image("https://via.placeholder.com/150", width=150)

                with col2:
                    st.markdown(f"**Sets:** {exercise['sets']}")
                    st.markdown(f"**Reps:** {exercise['reps']}")
                    st.markdown(f"**RPE:** {exercise['rpe']}/10")

                with col3:
                    st.button(f"Swap {exercise['name']}", key=f"swap_{day}_{exercise['name']}")

    st.markdown("</div>", unsafe_allow_html=True)

    # Meal plan section
    st.markdown("<div class='card'><div class='card-header'>Your Meal Plan</div>", unsafe_allow_html=True)

    meal_plan = mock_meal_plan()
    meal_days = st.tabs(list(meal_plan.keys()))

    for i, day in enumerate(meal_plan.keys()):
        with meal_days[i]:
            for meal_type, meal in meal_plan[day].items():
                if meal_type != 'Snacks':
                    st.markdown(f"**{meal_type}:** {meal}")
                else:
                    st.markdown("**Snacks:**")
                    for snack in meal:
                        st.markdown(f"- {snack}")

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
    health_data = mock_health_risk_assessment(st.session_state.user_data)

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
    feasibility = mock_goal_feasibility(st.session_state.user_data)

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
    df = pd.DataFrame({
        'Month': [0, 1, 2, 3, 4],
        'Target Plan': [
            st.session_state.user_data.get('weight', 70),
            None,
            None,
            None,
            st.session_state.user_data.get('target_weight', 65)
        ],
        'Realistic Plan': [
            st.session_state.user_data.get('weight', 70),
            None,
            None,
            None,
            st.session_state.user_data.get('target_weight', 65)
        ]
    })

    # Fill in the gaps for a smooth line
    target_months = st.session_state.user_data.get('target_months', 3)
    realistic_months = feasibility['suggested_timeframe']

    current_weight = st.session_state.user_data.get('weight', 70)
    target_weight = st.session_state.user_data.get('target_weight', 65)

    # Target plan line - straight line to goal
    for i in range(1, target_months):
        progress_pct = i / target_months
        df.loc[df['Month'] == i, 'Target Plan'] = current_weight - (current_weight - target_weight) * progress_pct

    # Realistic plan line - slightly curved approach
    for i in range(1, realistic_months):
        # Slower at first, faster later
        if i < realistic_months / 2:
            progress_pct = (i / realistic_months) * 0.8
        else:
            progress_pct = (i / realistic_months) * 1.2
            if progress_pct > 1:
                progress_pct = 1

        df.loc[df['Month'] == i, 'Realistic Plan'] = current_weight - (current_weight - target_weight) * progress_pct

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

            st.success("Your personalized plans have been generated!")
            st.session_state.has_fitness_plan = True

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

    tab1, tab2, tab3 = st.tabs(["Workout Feedback", "Meal Plan Feedback", "Update Plan"])

    with tab1:
        display_workout_feedback()

    with tab2:
        display_meal_feedback()

    with tab3:
        display_plan_update()


def display_workout_feedback():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Workout Feedback")

    # Mock workout data
    workout_days = ["Monday", "Wednesday", "Friday"]
    selected_day = st.selectbox("Select workout day to provide feedback", workout_days)

    st.write("#### How did your workout go?")

    # Overall workout rating
    workout_rating = st.slider(
        "Rate your overall workout experience:",
        min_value=1,
        max_value=10,
        value=7,
        help="1 = Very difficult/painful, 10 = Perfect/easy"
    )

    # Completed exercises
    st.write("#### Exercises Completed")

    # Mock exercises for the selected day
    exercises = mock_workout_plan()[selected_day]

    for exercise in exercises:
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            st.write(f"**{exercise['name']}**")
            st.caption(f"{exercise['sets']} sets × {exercise['reps']} reps")

        with col2:
            completed = st.checkbox("Completed", key=f"completed_{exercise['name']}", value=True)

        with col3:
            if completed:
                difficulty = st.select_slider(
                    "Difficulty",
                    options=["Too Easy", "Just Right", "Too Hard"],
                    value="Just Right",
                    key=f"diff_{exercise['name']}"
                )

    # Energy level and recovery
    st.write("#### Recovery & Energy")

    col1, col2 = st.columns(2)
    with col1:
        energy = st.select_slider(
            "Energy level during workout:",
            options=["Very Low", "Low", "Medium", "High", "Very High"],
            value="Medium"
        )

    with col2:
        soreness = st.select_slider(
            "Muscle soreness after previous workout:",
            options=["None", "Mild", "Moderate", "Severe"],
            value="Mild"
        )

    # Additional notes
    notes = st.text_area("Additional notes or specific exercise feedback:", height=100)

    if st.button("Submit Workout Feedback", use_container_width=True):
        st.success("Feedback submitted! We'll use this to optimize your next workout.")

    st.markdown("</div>", unsafe_allow_html=True)


def display_meal_feedback():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Meal Plan Feedback")

    # Day selection
    meal_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    selected_day = st.selectbox("Select day to provide meal feedback", meal_days)

    # Mock meal data
    meal_types = ["Breakfast", "Lunch", "Dinner", "Snacks"]

    st.write("#### How well did you follow your meal plan?")

    adherence = st.slider(
        "Overall meal plan adherence:",
        min_value=0,
        max_value=100,
        value=80,
        format="%d%%",
        help="0% = Did not follow at all, 100% = Followed exactly"
    )

    st.write("#### Meal-specific feedback")

    for meal in meal_types:
        st.write(f"**{meal}**")

        col1, col2 = st.columns(2)
        with col1:
            followed = st.radio(
                f"Did you eat the recommended {meal.lower()}?",
                ["Yes, exactly", "Yes, with modifications", "No, ate something else"],
                key=f"followed_{meal}",
                horizontal=True
            )

        with col2:
            satisfaction = st.select_slider(
                f"{meal} satisfaction:",
                options=["Not satisfied", "Somewhat satisfied", "Satisfied", "Very satisfied"],
                value="Satisfied",
                key=f"satisfaction_{meal}"
            )

        st.text_area(f"Notes about your {meal.lower()}:", key=f"notes_{meal}")
        st.divider()

    # Hunger and energy levels
    st.write("#### Overall Nutrition Feedback")

    col1, col2 = st.columns(2)
    with col1:
        hunger = st.select_slider(
            "Hunger level throughout the day:",
            options=["Always hungry", "Sometimes hungry", "Rarely hungry", "Never hungry"],
            value="Sometimes hungry"
        )

    with col2:
        energy = st.select_slider(
            "Energy level throughout the day:",
            options=["Very Low", "Low", "Medium", "High", "Very High"],
            value="Medium"
        )

    # Additional notes
    cravings = st.text_area("Any specific cravings or foods you missed?", height=100)

    if st.button("Submit Meal Feedback", use_container_width=True):
        st.success("Feedback submitted! We'll use this to optimize your next meal plan.")

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

    # Update request
    st.write("#### Request Plan Updates")

    update_options = st.multiselect(
        "What would you like to update in your plan?",
        ["Increase workout intensity", "Decrease workout intensity",
         "Change workout days", "Focus on different muscle groups",
         "Adjust calorie intake", "Change meal preferences",
         "Add more variety to meals", "Simplify meal preparation"]
    )

    specific_requests = st.text_area("Any specific requests or changes you'd like to make?", height=100)

    if st.button("Update My Plans", type="primary", use_container_width=True):
        with st.spinner("Updating your personalized plans..."):
            # This would normally use st.session_state.fitness_coach to update plans
            # Mock progress bar to simulate AI processing
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress_bar.progress(i + 1)

            # Get mock updated plan
            updates = mock_update_plan({
                'weight': current_weight,
                'update_options': update_options,
                'specific_requests': specific_requests
            })

            st.success("Your plans have been updated based on your feedback!")

            # Show summary of changes
            st.subheader("Changes Made")
            for adjustment in updates['adjustments']:
                st.info(adjustment)

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