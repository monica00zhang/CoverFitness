from typing import Annotated, TypedDict, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
import json
import os

with open("openai_key.txt", "r") as f:
    api_key = f.read().strip()  # strip /n
os.environ["OPENAI_API_KEY"] = api_key

def get_openai_llm(temperature=0):
    return ChatOpenAI(model="gpt-3.5-turbo", temperature=temperature)

class AIHealthCoach:
    def __init__(self):
        print("Initializing AIFitnessCoach")
        self.llm = get_openai_llm()

    def calculate_tdee_and_calorie_goal(self, user_data):
        """
        Calculated based on user basic data:
            1. BMR (basal metabolic rate)
            2. TDEE (total daily energy expenditure)
            3. Recommended daily calorie intake target (to achieve target weight)
        """

        # Get basic data
        age = user_data['age']
        gender = user_data['gender']
        weight = user_data['weight']  # kg
        height = user_data['height']  # cm

        goal_type = user_data['goal_type']
        target_weight = user_data['target_weight']
        target_months = user_data['target_months']

        # 1. Calculate BMR (Mifflin-St Jeor Equation)
        if gender.lower() == 'male':
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161

        # 2. 活动水平系数映射表
        multiplier = 1.2

        # 3. Calculate TDEE (Total Daily Expenditure)
        tdee = bmr * multiplier

        # 4. Calculate the caloric surplus/deficit required for target weight
        weight_diff = abs(target_weight - weight)
        total_calorie_change = weight_diff * 7700  # 1kg ≈ 7700 kcal
        total_days = target_months * 30
        daily_change = total_calorie_change / total_days

        if goal_type.lower() == "lose weight":
            calorie_goal = tdee - daily_change
        elif goal_type.lower() == "gain muscle":
            calorie_goal = tdee + daily_change
        else:
            calorie_goal = tdee  # 维持体重

        return {
            'bmr': round(bmr, 2),
            'tdee': round(tdee, 2),
            'daily_calorie_change': round(daily_change, 2),
            'calorie_goal': round(calorie_goal, 2),
            'goal_type': goal_type
        }

    def generate_meal_plan(self, user_data, plan):
        # Get basic data
        goal_type = user_data['goal_type']
        dietary_preferences = user_data['dietary_preferences']
        dietary_notes = user_data['dietary_notes']

        # 1。
        tdee_info = self.calculate_tdee_and_calorie_goal(user_data)

        meal_cot_prompt = ChatPromptTemplate.from_template("""
        You are a certified nutrition expert specializing in personalized meal planning for fitness goals.

        USER PROFILE:
        - Fitness goal: {goal_type}
        - TDEE (daily calorie needs): {daily_consuming_cal}
        - Dietary preferences: {dietary_preferences}
        - Dietary notes: {dietary_notes}

        EXERCISE SCHEDULE:
        {workout_plan}

        Please design a comprehensive 7-day meal plan with the following requirements:
        1. On exercise days, design meals that support performance and recovery, accounting for the specific exercises performed
        2. On rest days, adjust the meal plan to support the user's fitness goals while maintaining appropriate calorie intake
        3. Ensure all meals accommodate the user's dietary preferences and restrictions
        4. Include macro distribution percentages for each day
        5. Check if the total calories for each day's meal plan is reasonable for the user's physical condition and fitness goal

        Output as structured JSON with the following format for each day:

        {{
          "Monday": {{
            "Total_Calories": 1800,
            "Macro_Distribution": "30% carbs, 40% protein, 30% fat",
            "Exercise": "Swimming (30 min) + Yoga (20 min)",
            "Meals": {{
              "Breakfast": {{
                "Menu": "Vegan protein smoothie with berries and chia seeds",
                "Macros": "300 calories, 25g carbs, 30g protein, 12g fat"
              }},
              "Lunch": {{
                "Menu": "Quinoa bowl with roasted vegetables and tofu",
                "Macros": "650 calories, 40g carbs, 25g protein, 20g fat"
              }},
              "Dinner": {{
                "Menu": "Zucchini noodles with lentil bolognese",
                "Macros": "650 calories, 45g carbs, 35g protein, 20g fat"
              }}
            }},
            "Hydration": "Minimum 2.5 liters of water, +500ml during workout"
          }},"Tuesday":{{ ...}}, ...}}
        """)

        meal_chain = meal_cot_prompt | self.llm | StrOutputParser()
        response = meal_chain.invoke({
                   "goal_type": goal_type,
                   "dietary_preferences": ', '.join(dietary_preferences),
                   "dietary_notes": dietary_notes,
                   "workout_plan": plan,
                   "daily_consuming_cal": tdee_info['tdee'],
               })

        try:
            parsed_response = json.loads(response)

        except Exception as e:
                print("Error parsing LLM response:", e)
                print("Raw response:", response)
                parsed_response = {}

        return parsed_response



class AIFitnessCoach:
    def __init__(self):
        print("Initializing AIFitnessCoach")
        self.llm = get_openai_llm()

    # 计算 BMI 并确定身体状况和目标
    def _get_bmi(self, user_data):
        height_m = user_data['height'] / 100  # Convert cm to meters
        bmi = round(user_data['weight'] / (height_m ** 2), 1)
        return bmi

    def health_risk_assessment(self, user_data):
        """Placeholder function to assess health risks via LLM"""

        # 先算 BMI（如果你希望直接传进去）
        user_data['bmi'] = self._get_bmi(user_data)

        health_risk_prompt = ChatPromptTemplate.from_template("""
            You are a certified fitness and nutrition expert. Analyze the user's profile and detect potential health risks.

            User Profile:
            {user_data}

            Perform the following tasks:

            1. Calculate and classify the BMI category (Underweight / Normal / Overweight / Obese) based on the user's BMI value.
            2. Assess the following risks (scale: 1 = very healthy, 100 = very severe), based on BMI, user history (e.g., eating disorders, joint injuries), and goal:
               - BMI Risk
               - Joint Injury Risk
               - Cardiovascular Risk
               - Overtraining Risk
               - Nutritional Risk
            3. Provide one short recommendation (~20 words each) from:
               - Diet perspective
               - Workout perspective

            Return the result as a JSON object with:
            - bmi (float)
            - bmi_category (string)
            - risk_level (Low / Moderate / High, based on combined risk)
            - risks (dict with keys above and values 1–100)
            - recommendations (list of 2 short sentences)
            """)

        health_risk_chain = health_risk_prompt | self.llm | StrOutputParser()

        result = health_risk_chain.invoke({
            "user_data": user_data
        })

        parsed_response = json.loads(result)
        return parsed_response

    def _calculate_realistic_months(self, goal_type, current_weight, target_weight):
        weight_diff = abs(current_weight - target_weight)

        # Safe rate rules
        if goal_type == "Lose Weight":
            safe_rate = 0.5  # kg per week
        elif goal_type == "Gain Muscle":
            safe_rate = 0.25
        else:
            safe_rate = 0.4  # fallback for rehabilitation/general

        weeks_needed = weight_diff / safe_rate
        realistic_months = round(weeks_needed / 4)
        return realistic_months, safe_rate

    def enhanced_goal_feasibility(self, user_data):
        goal_type = user_data['goal_type']

        current_weight = user_data['weight']
        target_weight = user_data['target_weight']

        target_months = user_data['target_months']

        realistic_months, safe_rate = self._calculate_realistic_months(goal_type, current_weight, target_weight)
        is_feasible = target_months >= realistic_months

        # LLM for personalized advice
        cot_prompt = ChatPromptTemplate.from_template("""
                 You are a certified health coach AI.
                The user wants to {goal_type} from {current_weight} kg to {target_weight} kg in {target_months} months.
                The assumed safe rate is {safe_rate} kg per week.

                First, evaluate whether this safe rate is reasonable based on the user's current body state:
                    - Consider basic metabolic rate (BMR), which is roughly 22 * weight in kg
                    - Factor in realistic weekly weight fluctuation ranges from clinical research:
                        - For fat loss: 0.5–1.0 kg/week
                        - For muscle gain: 0.2–0.5 kg/week
                    - If the safe rate appears too fast or too slow based on the user's body state:
                        - Recommend a more appropriate safe rate
                        - Recalculate the realistic timeframe accordingly:
                            -  weight_diff = abs({current_weight} - {target_weight})
                            -  weeks_needed = weight_diff / safe_rate
                            -  realistic_months = round(weeks_needed / 4)

                Then, determine if the goal is achievable within {target_months} months based on this analysis. Return `is_feasible` as either true or false.

                Finally, give the advice: explaining why the goal timeframe might need to be adjusted or not, considering the user's body state and health perspective:
                    - Based on the recalculated safe rate and BMR, explain whether the goal is realistic within the given timeframe.
                    - Provide reasoning for adjusting the timeframe if necessary (e.g., faster or slower rate of progress due to body type, metabolism, and other health factors).
                    - If the goal timeframe is feasible, explain why this is a safe and sustainable approach.
                    - The explanation should include insights on the safe rate's appropriateness, the user's BMR, and how it impacts their ability to achieve the goal.
                    - keep your word around 30-70 words


                Output JSON:
                {{
                    "is_feasible": true/false,
                    "suggested_timeframe": realistic_months,
                    "advice": "text"
                    }}
                    """)

        feasibility_chain = cot_prompt | self.llm | StrOutputParser()
        response = feasibility_chain.invoke({
            "goal_type": goal_type.lower(),
            "current_weight": current_weight,
            "target_weight": target_weight,
            "target_months": target_months,
            "safe_rate": safe_rate})

        parsed_response = json.loads(response)

        # Optional: Combine with visualization data
        timeline_data = {
            'Target': [current_weight, target_weight],
            'Realistic': [current_weight, target_weight],
            'Month': [0, target_months if target_months >= parsed_response['suggested_timeframe'] else parsed_response[
                'suggested_timeframe']]
        }

        return {
            'is_feasible': parsed_response['is_feasible'],
            'suggested_timeframe': parsed_response['suggested_timeframe'],
            'timeline_data': timeline_data,
            'advice': parsed_response['advice']}

    def calculate_tdee_and_calorie_goal(self, user_data):
        """
        Calculated based on user basic data:
            1. BMR (basal metabolic rate)
            2. TDEE (total daily energy expenditure)
            3. Recommended daily calorie intake target (to achieve target weight)
        """

        # Get basic data
        age = user_data['age']
        gender = user_data['gender']
        weight = user_data['weight']  # kg
        height = user_data['height']  # cm

        goal_type = user_data['goal_type']
        target_weight = user_data['target_weight']
        target_months = user_data['target_months']

        # 1. Calculate BMR (Mifflin-St Jeor Equation)
        if gender.lower() == 'male':
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161

        # 2. 活动水平系数映射表
        multiplier = 1.2

        # 3. Calculate TDEE (Total Daily Expenditure)
        tdee = bmr * multiplier

        # 4. Calculate the caloric surplus/deficit required for target weight
        weight_diff = abs(target_weight - weight)
        total_calorie_change = weight_diff * 7700  # 1kg ≈ 7700 kcal
        total_days = target_months * 30
        daily_change = total_calorie_change / total_days

        if goal_type.lower() == "lose weight":
            calorie_goal = tdee - daily_change
        elif goal_type.lower() == "gain muscle":
            calorie_goal = tdee + daily_change
        else:
            calorie_goal = tdee  # 维持体重

        return {
            'bmr': round(bmr, 2),
            'tdee': round(tdee, 2),
            'daily_calorie_change': round(daily_change, 2),
            'calorie_goal': round(calorie_goal, 2),
            'goal_type': goal_type
        }

    def estimate_weekly_exercise_target(self, tdee_info):
        # 1. weekly calorie goal
        daily_calorie_change, goal_type = tdee_info['daily_calorie_change'], tdee_info['goal_type']
        weekly_net_change = daily_calorie_change * 7

        # 2. calorie diff for working out
        if goal_type.lower() == "lose weight":
            exercise_contrib_ratio = 0.25
        elif goal_type.lower() == "gain muscle":
            exercise_contrib_ratio = 0.15
        else:
            exercise_contrib_ratio = 0.3  # default

        weekly_exercise_target = abs(weekly_net_change) * exercise_contrib_ratio
        return round(weekly_exercise_target, 2)

    def search_sport_range(self, user_data, activity_list=None):

        height_cm = user_data['height']
        weight_kg = user_data['weight']
        bmi = user_data['bmi']

        preferences = user_data['workout_preferences']
        # METs （：MET）
        base_mets = {
            "Weight training": 3.5 * 1.05,
            "Cardio": 6.0 * 1.05,
            "HIIT": 8.0 * 1.05,
            "Yoga": 2.5 * 1.05,
            "Pilates": 3.0 * 1.05,
            "Bodyweight": 4.0 * 1.05,
            "Swimming": 6.0 * 1.05,
            "Running": 9.8 * 1.05,
            "Cycling": 7.5 * 1.05
        }

        #
        if activity_list:
            base_mets = {k: v for k, v in base_mets.items() if k in activity_list}

        # kcal/min = MET * 3.5 * weight / 200
        result = {}
        for activity, met in base_mets.items():
            if activity in preferences:
                kcal_min = met * 3.5 * weight_kg / 200
                result[activity] = round(kcal_min, 2)

        return result

    def generate_workout_plan(self, user_data, sport_range=""):
        goal_type = user_data['goal_type']
        fitness_level = user_data['fitness_level']
        workout_days = user_data['workout_days']
        workout_duration = user_data['workout_duration']
        focus_areas = user_data['focus_areas']

        """ 1.  """
        tdee_info = self.calculate_tdee_and_calorie_goal(user_data)
        target_consuming_cal = self.estimate_weekly_exercise_target(tdee_info)

        if sport_range == "":
            sport_range = {'Yoga':2.5 , 'Bodyweight exercises':5, 'Swimming':7}

        selected_sport_context = ", ".join(
            [f"{sport} ({mets} kcal/min)" for sport, mets in sport_range.items()]
        )

        cot_prompt = ChatPromptTemplate.from_template("""
            You are a certified health and fitness coach AI.

            Help design a personalized weekly workout plan for a user. The plan must:
            - Match user's fitness goal: {goal_type}
            - Match user's current fitness level: {fitness_level}
            - Fit user’s schedule: available {workout_days} days per week, {workout_duration} minutes per session
            - Fit user’s preference: top exercises are {selected_sport_context}
            - Satisfy weekly calorie consumption target: {target_consuming_cal} kcal/week
            - Distribute daily workouts reasonably

            Tasks:
            1. From the listed exercises, choose a daily set for each of the {workout_days} days.
                - Each day should contain 2-4 actions (can vary).
                - Each action should include:
                    • Name
                    • Duration (minutes)
                    • Estimated calorie burn
                    • Primary target muscle group
                - Try not to repeat same muscle group across consecutive days.
                - Maintain variety.
            2. Make sure daily total:
                - Duration ≈ {workout_duration} ± 10 minutes
                - Total calorie burn ≈ {target_consuming_cal} / {workout_days} kcal
            3. Incorporate user's focus areas: {focus_areas}
                - At least one action per day should match a focus area.
            4. For each day, suggest an order of exercises for optimal effectiveness and recovery.

            Output structured JSON:
            {{
                "weekly_plan": [
                    {{
                        "day": "Monday",
                        "exercises": [
                            {{
                                "name": "Swimming",
                                "duration_min": 30,
                                "calories_burned": 210,
                                "target_muscle": "Full body"
                            }},
                            ...
                        ],
                        "total_duration": 60,
                        "total_calories": 450
                    }},
                    ...
                ]
            }}
        """)
        workout_chain = cot_prompt | self.llm | StrOutputParser()
        response = workout_chain.invoke({
            "goal_type": goal_type,
            "fitness_level": fitness_level,
            "workout_days": ', '.join(workout_days),
            "workout_duration": workout_duration,
            "selected_sport_context": selected_sport_context,
            "target_consuming_cal": target_consuming_cal,
            "focus_areas": focus_areas
        })

        try:
            parsed_response = json.loads(response)
        except Exception as e:
            print("Error parsing LLM response:", e)
            print("Raw response:", response)
            parsed_response = {}

        return parsed_response

    def adjust_workout_plan(self, plan, adjust_intensity, adjust_exercises, user_data, sport_range=""):
        goal_type = user_data['goal_type']
        fitness_level = user_data['fitness_level']
        workout_days = user_data['workout_days']
        workout_duration = user_data['workout_duration']
        focus_areas = user_data['focus_areas']

        # 1。
        tdee_info = self.calculate_tdee_and_calorie_goal(user_data)
        target_consuming_cal = self.estimate_weekly_exercise_target(tdee_info)

        if sport_range == "":
            sport_range = {'Yoga':2.5 , 'Bodyweight exercises':5, 'Swimming':7}

        selected_sport_context = ", ".join(
            [f"{sport} ({mets} kcal/min)" for sport, mets in sport_range.items()]
        )

        adjust_prompt = ChatPromptTemplate.from_template("""
        You are a certified health and fitness coach AI.
        The user wants to adjust their workout plan based on recent feedback.

        Here is the current weekly workout plan to revise:
        {orginal_plan}
        
        Adjustment instructions:
        - Adjust workout intensity based on feedback: {adjust_intensity}
        - Add more of these exercise types: {adjust_exercises}

        Now adjust the plan by completing the following tasks:
        1. From the listed exercises, choose a daily set for each of the {workout_days} days.
            - Each day should contain 2-4 actions (can vary).
            - Each action should include:
                • Name
                • Duration (minutes)
                • Estimated calorie burn
                • Primary target muscle group
            - Avoid repeating the same muscle group on consecutive days.
            - Maintain variety.

        2. Make sure daily totals:
            - Duration ≈ {workout_duration} ± 10 minutes
            - Total calorie burn ≈ {target_consuming_cal} / {workout_days} kcal
        
        3. Incorporate user's focus areas: {focus_areas}
            - At least one action per day should target a focus area.
        
        4. Suggest the best exercise order for each day to maximize effectiveness and recovery.

        Context:
        - User's goal: {goal_type}
        - User's fitness level: {fitness_level}
        - Preferred exercises and METs: {selected_sport_context}
        
        Output a valid JSON like:
        {{
            "weekly_plan": [
                {{
                    "day": "Monday",
                    "exercises": [
                        {{
                            "name": "Swimming",
                            "duration_min": 30,
                            "calories_burned": 210,
                            "target_muscle": "Full body"
                        }},
                        ...
                    ],
                    "total_duration": 60,
                    "total_calories": 450
                }},
                ...
            ]
        }}
        Make sure your output is well-structured and JSON-compatible.
        """)


        workout_chain = adjust_prompt | self.llm | StrOutputParser()
        response = workout_chain.invoke({
            "orginal_plan":plan,
            "adjust_intensity":adjust_intensity,
            "adjust_exercises":adjust_exercises,
            "goal_type": goal_type,
            "fitness_level": fitness_level,
            "workout_days": ', '.join(workout_days),
            "workout_duration": workout_duration,
            "selected_sport_context": selected_sport_context,
            "target_consuming_cal": target_consuming_cal,
            "focus_areas": focus_areas
        })

        try:
            parsed_response = json.loads(response)
        except Exception as e:
            print("Error parsing LLM response:", e)
            print("Raw response:", response)
            parsed_response = {}

        return parsed_response







