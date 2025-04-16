import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()

openai_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Load job questions from JSON file
with open('db.json', 'r', encoding='utf-8') as f:
    job_data = json.load(f)

# إعداد صفحة ستريملت
st.set_page_config(page_title="محاكاة المقابلة", layout="centered")
st.title("🤖 محاكاة مقابلة تقنية باللغة العربية")

# تعريف التعليمات للنموذج
SYSTEM_PROMPT = """
تحدث باللغة العربية فقط، وباللهجة السورية.

أنت مساعد افتراضي هدفه محاكاة مقابلة تقنية حقيقية وتقييم إجابات المستخدم بشكل احترافي.

أدوارك:

1. **ابدأ المحادثة** بسؤال المستخدم: "شو اسم الوظيفة يلي بدك تتقدم عليها؟"

2. **صِغ سؤالًا واحدًا فقط في كل مرة**، وركّز فقط على الأسئلة التقنية المتعلقة بالوظيفة. 
   - استخدم مصطلحات تقنية إنجليزية كما هي (لا تترجمها).

3. **قيّم الإجابات**:
   - إذا كانت الإجابة صحيحة: امدح المستخدم باختصار ثم اسأل السؤال التالي.
   - إذا كانت خاطئة: 
     - بسّط السؤال وأعد طرحه.
     - أعطِ تلميحًا إذا أخطأ أول مرة.
     - إذا أخطأ مرتين: انتقل للسؤال التالي مباشرة، بدون توضيح الجواب.

4. **اختم المحادثة** بعد عدة أسئلة (مثلاً 10 أسئلة):
   - لخّص أداء المستخدم باختصار.
   - شجّعه بطريقة إيجابية (مثال: لا تخاف من الأخطاء، كلها جزء من التعلّم).
   - اسأله: "في شي تاني حاب تتدرّب عليه؟"
"""


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "assistant", "content": "مرحباً !معك سارة! شو اسم الوظيفة يلي بدك تتدرب عليها؟"}
    ]
    st.session_state.job_selected = False
    st.session_state.job_description = ""

# Display chat history
for msg in st.session_state.messages[1:]:
    with st.chat_message("user" if msg["role"] == "user" else "assistant"):
        st.markdown(msg["content"])

# User input
user_input = st.chat_input("اكتب ردّك هون...")

if user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with st.chat_message("user"):
        st.markdown(user_input)

    # If job not selected yet, find matching job
    if not st.session_state.job_selected:
        selected_job = None
        for job in job_data:
            if job["job_title"].lower() in user_input.lower():
                selected_job = job
                break
        
        if selected_job:
            st.session_state.job_selected = True
            st.session_state.job_description = selected_job["job_description"]
            
            # Add job context to system message
            job_context = {
                "role": "system",
                "content": f"الوظيفة المطلوبة: {selected_job['job_title']}. الوصف: {selected_job['job_description']}"
            }
            st.session_state.messages.insert(1, job_context)
    
    # Get assistant response
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=st.session_state.messages,
            temperature=0.7,
            max_tokens=500
        )
        assistant_reply = response.choices[0].message.content
        
        # Add assistant reply
        st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
        
        with st.chat_message("assistant"):
            st.markdown(assistant_reply)

    except Exception as e:
        st.error(f"⚠️ حدث خطأ أثناء التواصل مع النموذج: {str(e)}")
