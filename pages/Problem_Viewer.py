import streamlit as st
import json
import io
import contextlib

# Load problems
@st.cache_resource
def load_data():
    with open("problems.json", "r", encoding="utf-8") as f:
        return json.load(f)

problems = load_data()

st.title("📘 Problem Solver")

# Problem selection
problem_ids = [str(p["id"]) for p in problems]
selected_id = st.selectbox("Select a problem ID:", problem_ids)
problem = next((p for p in problems if str(p["id"]) == selected_id), None)

if problem:
    st.header(f"Problem {problem['id']} - {problem['difficulty']}")
    st.write("**Tags:**", ", ".join(problem["tags"]))
    st.markdown("**Description:**")
    st.write(problem["problemDescription"])
    
    st.markdown("**Starter Code:**")
    starter_code = problem["starterCode"]

    # Code editor
    user_code = st.text_area("✍️ Write your solution here:", value=starter_code, height=300)

    # Run button
    if st.button("Run Code"):
        try:
            # Define a dictionary to execute code safely
            local_env = {}
            exec(user_code, {}, local_env)

            # Get the solution class
            Solution = local_env.get("Solution")
            if Solution is None:
                st.error("❌ No class Solution found in your code.")
            else:
                solver = Solution()
                results = []
                for tc in problem["testCases"]:
                    # Extract input like "n = 7"
                    exec(tc["input"], {}, local_env)
                    # Call method dynamically (find method name from starterCode)
                    method_name = starter_code.split("def ")[1].split("(")[0]
                    method = getattr(solver, method_name)
                    
                    # Run and compare
                    output = method(**local_env)
                    expected = eval(tc["output"])
                    results.append((tc["input"], output, expected, output == expected))

                # Show results
                st.subheader("📊 Test Results")
                for inp, out, exp, ok in results:
                    if ok:
                        st.success(f"✅ Input: {inp} | Output: {out} | Expected: {exp}")
                    else:
                        st.error(f"❌ Input: {inp} | Output: {out} | Expected: {exp}")

        except Exception as e:
            st.error(f"⚠️ Error while running code: {e}")
