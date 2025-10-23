import os
import requests
import streamlit as st
from streamlit_chat import message
from dotenv import load_dotenv
from langchain.llms import Fireworks
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# تحميل المتغيرات من ملف .env
load_dotenv()

# مفاتيح الـ API
FIREWORKS_API_KEY = os.getenv("FIREWORKS_API_KEY", "fw_3ZeCRggjCvoCQr4MB6Gn4vBV")
SPOONACULAR_API_KEY = os.getenv("SPOONACULAR_API_KEY", "803bffd94314410886102ebcc075ddad")

# تهيئة نموذج Fireworks AI
llm = Fireworks(
    model="sentientfoundation/dobby-unhinged-llama-3-3-70b-new",
    temperature=0.8,
    fireworks_api_key=FIREWORKS_API_KEY
)

# دالة لجلب وصفات من Spoonacular
def get_recipes_from_api(query):
    url = f"https://api.spoonacular.com/recipes/complexSearch?query={query}&number=5&apiKey={SPOONACULAR_API_KEY}"
    try:
        response = requests.get(url)
        data = response.json()
        if "results" in data:
            recipes = [f"{r['title']} 🍽️\n{r['image']}" for r in data["results"]]
            return "\n\n".join(recipes)
        else:
            return "لم أجد وصفات مناسبة لهذا الطبق."
    except Exception as e:
        return f"حدث خطأ أثناء جلب البيانات من Spoonacular: {e}"

# إعداد prompt لتحليل السؤال
prompt_template = PromptTemplate(
    input_variables=["user_input"],
    template="""
أنت مساعد ذكي متخصص في الطبخ. 
حلل طلب المستخدم التالي لتحديد نوع الوجبة أو المكون المطلوب، 
ثم أعطني اسم الوجبة أو المكون فقط بإيجاز.

سؤال المستخدم:
{user_input}
"""
)

chain = LLMChain(llm=llm, prompt=prompt_template)

# واجهة Streamlit
st.set_page_config(page_title="Smart Cooking Assistant", page_icon="🍳")
st.title("🍳 Smart Cooking Assistant (Fireworks + Spoonacular)")
st.write("اسألني عن أي وجبة أو مكون لأعطيك وصفات جاهزة 😋")

if "generated" not in st.session_state:
    st.session_state["generated"] = []
if "past" not in st.session_state:
    st.session_state["past"] = []

user_input = st.text_input("اكتب سؤالك هنا 👇", key="input")

if user_input:
    try:
        # تحليل السؤال عبر Fireworks AI
        analyzed_meal = chain.run({"user_input": user_input}).strip()
        # جلب الوصفات من Spoonacular
        recipes = get_recipes_from_api(analyzed_meal)

        final_answer = f"🍽️ بناءً على سؤالك، إليك وصفات لـ **{analyzed_meal}**:\n\n{recipes}"

        st.session_state.past.append(user_input)
        st.session_state.generated.append(final_answer)
    except Exception as e:
        st.error(f"حدث خطأ: {e}")

# عرض المحادثة
if st.session_state["generated"]:
    for i in range(len(st.session_state["generated"]) - 1, -1, -1):
        message(st.session_state["generated"][i], key=str(i))
        message(st.session_state["past"][i], is_user=True, key=str(i) + "_user")
