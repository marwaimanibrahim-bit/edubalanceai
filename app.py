import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime, date
from groq import Groq
import io

try:
    import pypdf
except ImportError:
    pypdf = None

# 1. Page Configuration
st.set_page_config(
    page_title="EduBalance AI",
    page_icon="🎓",
    layout="wide"
)

# 2. Initialize Groq Client
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    st.error("GROQ_API_KEY is missing in Streamlit Secrets!")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

# 3. Session State Initializations
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hello! 👋 Welcome to **EduBalance AI**.\n\n"
                "I'm your advanced AI academic and wellness companion, created to help you excel.\n\n"
                "How can I assist you today?"
            )
        }
    ]

if "mood_logs" not in st.session_state:
    st.session_state.mood_logs = []

# 4. Sidebar Controls & Navigation
with st.sidebar:
    st.title("🎓 EduBalance AI")
    st.markdown("✨ *Created by **Marwa Eman Ibrahim***")
    st.caption("ampionship Edition - Advanced AI Agent")
    
    st.markdown("---")
    st.subheader("👤 Student Profile")
    student_name = st.text_input("Student Name", "Marwa Eman Ibrahim")
    
    st.markdown("---")
    st.header("📌 Navigation Menu")
    app_mode = st.radio(
        "Choose a feature:",
        [
            "💬 AI Companion Chat", 
            "📊 Mood Analytics", 
            "📅 Exam Planner & Export", 
            "📄 Document Analyzer (RAG)", 
            "📝 Smart Quiz Generator"
        ]
    )
    
    st.markdown("---")
    st.header("🧰 Quick Calm Toolkit")
    if st.button("🫁 4-7-8 Breathing Exercise"):
        st.session_state.messages.append({
            "role": "assistant",
            "content": (
                "**🫁 4-7-8 Breathing Exercise:**\n"
                "1. **Inhale** quietly through your nose for **4 seconds**.\n"
                "2. **Hold** your breath for **7 seconds**.\n"
                "3. **Exhale** completely through your mouth for **8 seconds**."
            )
        })

    if st.button("💡 Quick Motivation"):
        st.session_state.messages.append({
            "role": "assistant",
            "content": "✨ *\"Success is the sum of small efforts, repeated day in and day out.\"* Keep going, you've got this!"
        })

# ==========================================
# PAGE 1: AI Chat Companion
# ==========================================
if app_mode == "💬 AI Companion Chat":
    st.title("💬 AI Companion Chat")
    st.caption("Ask questions about your studies, stress relief, or time management.")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if user_input := st.chat_input("Ask your assistant..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            try:
                system_instruction = (
                    f"You are EduBalance AI, an advanced academic and mental health assistant designed for students. "
                    f"The user's name is {student_name}. Keep responses encouraging, highly structured, and clear. "
                    f"Support multilingual queries (English, Pashto, Dari, Arabic)."
                )
                
                api_messages = [{"role": "system", "content": system_instruction}] + [
                    {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
                ]

                response = client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=api_messages,
                    temperature=0.7,
                )
                
                reply = response.choices[0].message.content
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})

            except Exception as e:
                st.error(f"Error connecting to AI: {e}")

# ==========================================
# PAGE 2: Mood & Stress Analytics
# ==========================================
elif app_mode == "📊 Mood Analytics":
    st.title("📊 Daily Mood & Stress Tracker")
    st.write("Track your energy and stress levels to visualize your well-being over time.")
    
    with st.form("mood_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            log_date = st.date_input("Date", date.today())
        with col2:
            energy_lvl = st.slider("Energy Level (1-10)", 1, 10, 7)
        with col3:
            stress_lvl = st.slider("Stress Level (1-10)", 1, 10, 4)
            
        submit_mood = st.form_submit_button("Log Today's Mood")
        
        if submit_mood:
            st.session_state.mood_logs.append({
                "Date": log_date.strftime("%Y-%m-%d"),
                "Energy": energy_lvl,
                "Stress": stress_lvl
            })
            st.success("Mood logged successfully!")

    if st.session_state.mood_logs:
        df = pd.DataFrame(st.session_state.mood_logs)
        fig = px.line(
            df, 
            x="Date", 
            y=["Energy", "Stress"], 
            markers=True,
            title="Energy vs Stress Levels Over Time",
            color_discrete_map={"Energy": "#2ECC71", "Stress": "#E74C3C"}
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No mood records yet. Log your first check-in above!")

# ==========================================
# PAGE 3: Exam Planner & Export
# ==========================================
elif app_mode == "📅 Exam Planner & Export":
    st.title("📅 Smart Exam Countdown & Study Planner")
    st.write("Plan your exams efficiently with AI-generated schedules and export options.")
    
    col_a, col_b = st.columns(2)
    with col_a:
        exam_name = st.text_input("Exam / Subject Name", "Computer Science")
    with col_b:
        exam_date = st.date_input("Exam Date", date.today())

    if "study_plan_text" not in st.session_state:
        st.session_state.study_plan_text = ""

    if st.button("Generate Study Schedule"):
        days_left = (exam_date - date.today()).days
        
        if days_left < 0:
            st.warning("Please select a future date!")
        else:
            st.metric(label="Days Remaining until Exam", value=f"{days_left} Days")
            
            with st.spinner("AI is generating a personalized study schedule..."):
                prompt = (
                    f"Create a professional day-by-day study and break schedule for the subject '{exam_name}'. "
                    f"There are {days_left} days left until the exam. "
                    f"Include study techniques like Pomodoro, revision strategies, and stress-prevention tips."
                )
                try:
                    plan_resp = client.chat.completions.create(
                        model="openai/gpt-oss-120b",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.7,
                    )
                    st.session_state.study_plan_text = plan_resp.choices[0].message.content
                except Exception as e:
                    st.error(f"Could not generate schedule: {e}")

    if st.session_state.study_plan_text:
        st.markdown("### 📋 Your AI Study Plan:")
        st.markdown(st.session_state.study_plan_text)
        
        # Export feature
        st.download_button(
            label="📥 Download Study Plan as Text File",
            data=st.session_state.study_plan_text,
            file_name=f"{exam_name}_Study_Plan.txt",
            mime="text/plain"
        )

# ==========================================
# PAGE 4: Document Analyzer (RAG Feature)
# ==========================================
elif app_mode == "📄 Document Analyzer (RAG)":
    st.title("📄 Document & Study Material Analyzer")
    st.write("Upload your lecture notes (PDF or TXT) and let AI analyze them for you.")
    
    uploaded_file = st.file_uploader("Upload a study document", type=["pdf", "txt"])
    
    extracted_text = ""
    if uploaded_file is not None:
        if uploaded_file.type == "application/pdf" and pypdf is not None:
            reader = pypdf.PdfReader(uploaded_file)
            for page in reader.pages:
                extracted_text += page.extract_text() or ""
        elif uploaded_file.type == "text/plain":
            extracted_text = str(uploaded_file.read(), "utf-8")
        
        st.success(f"File uploaded successfully! ({len(extracted_text)} characters extracted)")
        
        doc_query = st.text_input("Ask a question about this document:")
        if st.button("Analyze Document"):
            if not doc_query:
                st.warning("Please enter a question.")
            else:
                with st.spinner("Analyzing document content..."):
                    prompt = (
                        f"Based on the following document content, answer the user's question clearly and professionally.\n\n"
                        f"Document Content:\n{extracted_text[:4000]}\n\n"
                        f"Question: {doc_query}"
                    )
                    try:
                        doc_resp = client.chat.completions.create(
                            model="openai/gpt-oss-120b",
                            messages=[{"role": "user", "content": prompt}],
                            temperature=0.7,
                        )
                        st.markdown("### 🤖 Analysis Result:")
                        st.markdown(doc_resp.choices[0].message.content)
                    except Exception as e:
                        st.error(f"Error analyzing document: {e}")

# ==========================================
# PAGE 5: Smart Quiz Generator
# ==========================================
elif app_mode == "📝 Smart Quiz Generator":
    st.title("📝 Smart Quiz & Flashcard Generator")
    st.write("Generate custom practice quizzes instantly to test your knowledge.")
    
    quiz_topic = st.text_input("Enter subject or topic for the quiz", "Health Science & Nutrition")
    num_questions = st.slider("Number of Questions", 3, 10, 5)
    
    if st.button("Generate Quiz"):
        with st.spinner("Generating quiz questions..."):
            quiz_prompt = (
                f"Create {num_questions} multiple-choice quiz questions with answers and explanations "
                f"for the topic: '{quiz_topic}'. Format them clearly."
            )
            try:
                quiz_resp = client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=[{"role": "user", "content": quiz_prompt}],
                    temperature=0.7,
                )
                st.markdown("### 🧠 Your Custom Practice Quiz:")
                st.markdown(quiz_resp.choices[0].message.content)
            except Exception as e:
                st.error(f"Could not generate quiz: {e}")
