
import os
import streamlit as st
from groq import Groq

# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Student Helper Agent",
    page_icon="🎓",
    layout="wide"
)

# ============================================================
# 2. CUSTOM CSS
# ============================================================

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #f5f8ff, #ffffff);
}

[data-testid="stSidebar"] {
    background-color: #172943;
}

[data-testid="stSidebar"] * {
    color: white;
}

.hero {
    background: linear-gradient(120deg, #e7efff, #eaf8ff);
    padding: 28px;
    border-radius: 18px;
    margin-bottom: 24px;
    border: 1px solid #dbeafe;
}

.hero h1 {
    color: #173b78;
    margin-bottom: 10px;
}

.hero p {
    color: #25466f;
    font-size: 17px;
}

.answer-box {
    background: #f0faf7;
    border: 1px solid #d5eee6;
    border-radius: 16px;
    padding: 22px;
}

.small-note {
    color: #56708e;
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# 3. API KEY CONFIGURATION
# ============================================================

# Read the API key from Streamlit secrets first.
# If unavailable, try the Windows environment variable.

api_key = os.getenv("GROQ_API_KEY", "")

try:
    api_key = st.secrets.get("GROQ_API_KEY", api_key)
except Exception:
    # This also handles a missing local secrets.toml file.
    pass

# ============================================================
# 4. SIDEBAR NAVIGATION
# ============================================================

with st.sidebar:

    st.markdown("# 🎓 Student Helper")
    st.markdown("### Agent")
    st.caption("Ask • Learn • Grow")

    st.divider()

    page = st.radio(
        "Navigation",
        [
            "Home",
            "About",
            "Tips for Students"
        ],
        key="navigation_page"
    )

    st.divider()

    st.markdown("🌱 **Keep learning!**")
    st.write(
        "Small steps every day lead to big success."
    )

    st.divider()

    if api_key.strip():
        st.success("✅ API key found")
    else:
        st.warning("⚠️ API key missing")

    st.caption("Powered by Python + Groq")

# ============================================================
# 5. AGENT FUNCTION
# ============================================================

def student_helper_agent(
    student_class,
    subject,
    question,
    client
):
    """
    Generate a student-friendly answer using a Groq LLM.
    """

    instructions = f"""
You are a friendly Student Helper Agent for school students.

Student class: {student_class}
Subject: {subject}

Your responsibilities:
1. Explain concepts at the student's class level.
2. Use simple words and everyday examples.
3. Explain difficult ideas step by step.
4. Include a practical example.
5. Give one practice question at the end.
6. For mathematics, show calculation steps.
7. Correct misunderstandings politely.
8. If uncertain, acknowledge the uncertainty.
9. Keep answers educational and organized.
10. Use age-appropriate language.
11. Do not invent textbook facts or references.

Use this answer structure where appropriate:

### Simple Explanation
Explain the concept in easy words.

### Step-by-Step Explanation
Explain the main points in order.

### Example
Give a practical example.

### Practice Question
Ask one question for the student to solve.

Adapt the detail and vocabulary to Class {student_class}.
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": instructions
            },
            {
                "role": "user",
                "content": question
            }
        ],
        temperature=0.4,
        max_completion_tokens=2048
    )

    answer = response.choices[0].message.content

    if not answer:
        return "The AI returned an empty answer. Please try again."

    return answer.strip()

# ============================================================
# 6. HOME PAGE
# ============================================================

if page == "Home":

    # Welcome banner
    st.markdown("""
    <div class="hero">
        <h1>🎓 Welcome to Student Helper Agent</h1>
        <p>
        Ask questions, understand concepts in simple words,
        solve problems step by step, and practice what you learn.
        </p>
    </div>
    """, unsafe_allow_html=True)

    left, right = st.columns(
        [0.9, 1.5],
        gap="large"
    )

    # --------------------------------------------------------
    # LEFT COLUMN: QUESTION FORM
    # --------------------------------------------------------

    with left:

        st.subheader("📝 Ask Your Question")

        with st.form("student_question_form"):

            student_class = st.selectbox(
                "Student Class",
                list(range(1, 11)),
                index=5,
                format_func=lambda x: f"Class {x}"
            )

            subject = st.selectbox(
                "Subject",
                [
                    "Science",
                    "Mathematics",
                    "English",
                    "Computer Science",
                    "Physics",
                    "Chemistry",
                    "Biology",
                    "Urdu",
                    "Social Studies",
                    "General Knowledge",
                    "Other"
                ]
            )

            question = st.text_area(
                "Your Question",
                placeholder=(
                    "Example: Explain photosynthesis "
                    "with an example."
                ),
                height=150
            )

            submitted = st.form_submit_button(
                "🚀 Get Answer",
                use_container_width=True
            )

        st.caption(
            "Ask about any school subject for Classes 1–10."
        )

    # --------------------------------------------------------
    # RIGHT COLUMN: ANSWER AREA
    # --------------------------------------------------------

    with right:

        st.subheader("💬 Student Helper Agent")

        if submitted:

            # Validate the API key
            if not api_key or not api_key.strip():

                st.error(
                    "Groq API key is missing. Configure "
                    "GROQ_API_KEY in .streamlit/secrets.toml."
                )

            # Validate the student's question
            elif not question or not question.strip():

                st.warning(
                    "Please enter your question first."
                )

            else:

                try:
                    # Create the Groq client
                    client = Groq(api_key=api_key)

                    # Call the LLM
                    with st.spinner(
                        "Your Student Helper Agent is thinking..."
                    ):

                        answer = student_helper_agent(
                            student_class=student_class,
                            subject=subject,
                            question=question.strip(),
                            client=client
                        )

                    # Save answer and question in session state
                    st.session_state["last_answer"] = answer
                    st.session_state["last_question"] = (
                        question.strip()
                    )
                    st.session_state["last_class"] = (
                        student_class
                    )
                    st.session_state["last_subject"] = subject

                except Exception as e:

                    st.error(
                        "The request failed. Check your API key, "
                        "model availability, internet connection, "
                        "and Groq usage limits."
                    )

                    # Useful during development in VS Code
                    st.exception(e)

        # Display the last successful answer
        last_answer = st.session_state.get("last_answer")

        if last_answer:

            with st.container(border=True):

                st.markdown(
                    f"**Class {st.session_state['last_class']} "
                    f"· {st.session_state['last_subject']}**"
                )

                st.markdown(last_answer)

            st.button(
                "🗑️ Clear Answer",
                use_container_width=True,
                on_click=lambda: [
                    st.session_state.pop(key, None)
                    for key in [
                        "last_answer",
                        "last_question",
                        "last_class",
                        "last_subject"
                    ]
                ]
            )

        else:

            st.info(
                "👋 Hello, student! Enter a question on the "
                "left and click Get Answer to begin learning."
            )

# ============================================================
# 7. ABOUT PAGE
# ============================================================

elif page == "About":

    st.title("ℹ️ About Student Helper Agent")

    st.write("""
Student Helper Agent is an AI-powered learning assistant
designed to help school students understand their lessons.

### Features

- Simple explanations
- Step-by-step problem solving
- Everyday examples
- Practice questions
- Support for Classes 1–10
- AI-powered responses through Groq

### Technology Stack

- Python
- Streamlit
- Groq API
- GPT-OSS 20B language model
""")

    st.info(
        "Always check important answers against your textbook "
        "and your teacher's guidance."
    )

# ============================================================
# 8. TIPS FOR STUDENTS PAGE
# ============================================================

elif page == "Tips for Students":

    st.title("💡 Tips for Better Learning")

    st.markdown("""
### How to use Student Helper Agent effectively

1. Ask one clear question at a time.
2. Select the correct class and subject.
3. Mention the topic you find difficult.
4. Ask for a step-by-step explanation.
5. Try the practice question yourself.
6. Ask the agent to explain anything you do not understand.
7. Verify important facts with your textbook.

### Example Questions

- Mathematics: Explain fractions with examples.
- Science: How do plants prepare their food?
- English: Explain the present perfect tense.
- Computer Science: What is a Python variable?
- Physics: Explain Newton's first law of motion.
""")

    st.success(
        "Learn a little every day and practise what you learn!"
    )
