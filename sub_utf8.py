import streamlit as st
import pandas as pd
import random
import os

st.title("Japanese Quiz App")
option = st.selectbox("Choose Mode", ["Kanji", "Vocab"])
lesson = st.radio("Choose Lesson", ["Daily Practice", "Today Lesson", "Practice Don't Know"])

# File paths
if option == "Kanji":
    if lesson == "Today Lesson":
        path = "F:/Japanese/Revise/Kanji1.xlsx"
    elif lesson == "Daily Practice":
        path = "F:/Japanese/Revise/Daily/Kanji.xlsx"
elif option == "Vocab":
    if lesson == "Daily Practice":
        path = "F:/Japanese/Revise/Daily/Vocab.xlsx"
    elif lesson == "Today Lesson":
        path = "F:/Japanese/Revise/Vocab1.xlsx"

# "Don't Know" file (shared for Kanji & Vocab separately)
dont_know_file = f"F:/Japanese/Revise/{option}_DontKnow.xlsx"

# Load data
if lesson == "Practice Don't Know":
    if os.path.exists(dont_know_file):
        mod = pd.read_excel(dont_know_file)
    else:
        st.warning("No 'Don't Know' words yet! Start adding them.")
        st.stop()
else:
    mod = pd.read_excel(path)

# Initialize session state
if "indices" not in st.session_state or "restart_flag" not in st.session_state:
    st.session_state.indices = list(range(len(mod)))
    random.shuffle(st.session_state.indices)
    st.session_state.index_pointer = 0
    st.session_state.restart_flag = False

# Restart button
if st.button("🔄 Restart"):
    st.session_state.indices = list(range(len(mod)))
    random.shuffle(st.session_state.indices)
    st.session_state.index_pointer = 0
    st.session_state.restart_flag = True
    st.rerun()

# Current Question
if st.session_state.index_pointer < len(st.session_state.indices):
    index = st.session_state.indices[st.session_state.index_pointer]
    col = mod.columns[0]
    valu = mod[col].iloc[index]
    f_index = mod.index[mod[col] == valu]

    st.markdown(f"### Q{st.session_state.index_pointer+1}: **{valu}**")

    # Find answer
    if option == "Kanji":
        ans = f"{mod.Reading.loc[f_index].values[0]} :: {mod.Meaning.loc[f_index].values[0]}"
    else:
        if col == "Jap":
            ans = mod.Eng.loc[f_index].values[0]
        else:
            ans = mod.Jap.loc[f_index].values[0]

    # --- Buttons Layout ---
    col1, col2, col3 = st.columns([1, 1, 1.2])

    # Show Answer
    with col1:
        if st.button("Show Answer"):
            st.success(ans)

    # Next
    with col2:
        if st.button("Next ➡"):
            st.session_state.index_pointer += 1
            st.rerun()

    # Add / Remove
    with col3:
        if lesson != "Practice Don't Know":
            if st.button("✅ Add"):
                if os.path.exists(dont_know_file):
                    dontknow_df = pd.read_excel(dont_know_file)
                    # Avoid duplicates
                    if not ((dontknow_df[col] == valu).any()):
                        dontknow_df = pd.concat([dontknow_df, mod.loc[f_index]], ignore_index=True)
                        dontknow_df.to_excel(dont_know_file, index=False)
                        st.info("Added")
                else:
                    mod.loc[f_index].to_excel(dont_know_file, index=False)
                    st.info("Created Don't Know list & added word!")
        elif lesson == "Practice Don't Know":
            if st.button("Remove"):
                dontknow_df = pd.read_excel(dont_know_file)
                dontknow_df = dontknow_df[dontknow_df[col] != valu]  # remove row
                dontknow_df.to_excel(dont_know_file, index=False)
                st.success("Word removed")
                st.session_state.index_pointer += 1
                st.rerun()

else:
    st.success("✅ You have completed ALL questions!")
    st.info("Click '🔄 Restart' to go again.")
