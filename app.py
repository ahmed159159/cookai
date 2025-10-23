import os
try:
# استخدام واجهة Fireworks المباشرة
resp = llm.invoke(prompt)
# بعض المكتبات ترجع dict أو كائن مختلف؛ نتعامل مع str
if isinstance(resp, dict) and "text" in resp:
keywords = resp["text"].strip()
else:
keywords = str(resp).strip()
# تنظيف: إذا النص طويل جدًا اقتطاع
if len(keywords) > 200:
keywords = keywords[:200]
return keywords
except Exception as e:
st.error(f"LLM extraction failed: {e}")
return user_input




# واجهة Streamlit
st.set_page_config(page_title="Cook Assistant", page_icon="🍳")
st.title("Cook Assistant — Fireworks AI + Spoonacular")
st.write("اكتب مكونات أو وصفة ترغب بها، وسأبحث لك عن وصفات مناسبة باستخدام Spoonacular.")


if "generated" not in st.session_state:
st.session_state["generated"] = []
if "past" not in st.session_state:
st.session_state["past"] = []


user_input = st.text_input("📝 اكتب طلبك (مثال: \"دجاج وطماطم وصفة سريعة\")", key="input")


if st.button("ابحث") or (user_input and user_input.strip()):
query_for_api = extract_keywords_with_llm(user_input)
spoon = search_recipe(query_for_api, number=5)


if spoon.get("error"):
output = f"❌ خطأ من Spoonacular: {spoon.get('error')}"
else:
results = spoon.get("results", [])
if not results:
output = f"لم أجد وصفات لطلبك ({query_for_api}). حاول كلمات بحث أبسط."
else:
parts = [f"🔍 **تحليل البحث:** {query_for_api}\n"]
for r in results:
parts.append(format_recipe_short(r))
output = "\n\n".join(parts)


st.session_state.past.append(user_input)
st.session_state.generated.append(output)


# عرض المحادثة
if st.session_state["generated"]:
for i in range(len(st.session_state["generated"]) - 1, -1, -1):
message(st.session_state["generated"][i], key=str(i))
message(st.session_state["past"][i], is_user=True, key=str(i) + "_user")


# Footer
st.markdown("---")
st.markdown("**ملاحظات:**\n- ضع مفاتيح API في متغيرات البيئة على Railway (FIREWORKS_API_KEY, SPOONACULAR_API_KEY).\n- لا ترفع المفاتيح على GitHub.")
