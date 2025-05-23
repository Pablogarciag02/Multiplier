import re
import os
import time
import hashlib
import pandas as pd
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

# Password protection 
def check_password():
    """Returns `True` if the user had the correct password."""
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        entered_password = st.session_state["password"]
        hashed_entered = hashlib.sha256(entered_password.encode()).hexdigest()
        correct_password_hash = "79c5816af2430a28cbada522cf77d5c0a4a74b6d0b0fd2f377cc8d1e92e4a8ea" 
        
        if hashed_entered == correct_password_hash:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    # Return True if password is validated
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password
    st.text_input(
        "Enter Password", 
        type="password", 
        on_change=password_entered, 
        key="password"
    )
    
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    
    return False

# Only run the main app if password is correct
if not check_password():
    st.stop()


#loading environment variables for the api key
load_dotenv()

API_KEY = os.getenv('API_KEY')
BASE_URL = 'https://api.deepseek.com'

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)


def rate_similarity(desc: str, target: str) -> int:
    if not desc:
        return 5
    
    prompt = f"""Rate the business-model similarity between the text below and the target company on a 1-10 scale:
1-2 = Very similar business models (strong comparables)
3-4 = Similar with some differences  
5-6 = Moderately similar
7-8 = Different business models
9-10 = Completely unrelated

Respond with only the integer.

Target:
{target}

Candidate:
{desc}"""
    
    for attempt in range(2):  # Try twice
        try:
            resp = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are an experienced investment analyst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0, max_tokens=5
            ).choices[0].message.content
            m = re.search(r'[1-9]|10', resp)  # Updated regex for 1-10
            return int(m.group()) if m else 10
        except Exception as e:
            if attempt == 0:  # First failure, try once more
                time.sleep(1)
                continue
            st.error(f"API error: {str(e)}")
            return 10

st.title("Deal Multiple Company Similarity Analisis")

st.markdown("""
### Rating Scale Explanation

| Rating  | Description                                           |
|:--------|:------------------------------------------------------|
| 1–2     | Very similar business models (strong comparables)     |
| 3–4     | Similar with some differences                         |
| 5–6     | Moderately similar                                    |
| 7–8     | Different business models                             |
| 9–10    | Completely unrelated                                  |
""")

# Use session state to keep track of the workflow stage
if 'stage' not in st.session_state:
    st.session_state.stage = 'description'
if 'target_desc' not in st.session_state:
    st.session_state.target_desc = ""
if 'results' not in st.session_state:
    st.session_state.results = None

# Description input stage
if st.session_state.stage == 'description':
    with st.form("company_description"):
        st.write("Escribe aquí la descripción.")
        target_desc = st.text_area("", height=150)
        submitted = st.form_submit_button("Submit Description")
        
        if submitted and target_desc:
            st.session_state.target_desc = target_desc
            st.session_state.stage = 'upload'
            st.rerun()

# File upload stage
elif st.session_state.stage == 'upload':
    st.write(f"**Target Description:** {st.session_state.target_desc[:100]}...")
    
    file = st.file_uploader("Sube el archivo de Excel")
    if file is not None:
        try:
            # Process the Excel file
            df = pd.read_excel(file, skiprows=6).iloc[:-2].drop(columns=['Deal ID'], errors='ignore')
            
            # Add this validation block:
            if 'Description' not in df.columns:
                st.error("Excel file must have a 'Description' column")
                st.stop()
            
            # Add similarity column
            df.insert(df.columns.get_loc('Description') + 1 if 'Description' in df.columns else len(df.columns), 
                     'Similarity Ranking', 0)
            
            # Process each row with visible progress
            progress_placeholder = st.empty()
            progress_bar = progress_placeholder.progress(0)
            status_text = st.empty()
            
            for i, idx in enumerate(df.index):
                status_text.text(f"Processing item {i+1} of {len(df)}")
                df.at[idx, 'Similarity Ranking'] = rate_similarity(
                    str(df.at[idx, 'Description']), 
                    st.session_state.target_desc
                )
                progress_bar.progress((i + 1) / len(df))
            
            status_text.text("Processing complete!")

            #Ordena los resultados en base a similitud de manera ascendiente.
            df = df.sort_values('Similarity Ranking', ascending=True)
            
            # Store results and move to results stage
            st.session_state.results = df
            st.session_state.stage = 'results'
            st.rerun()
            
        except Exception as e:
            st.error(f"Error processing Excel file: {str(e)}")

# Results display stage
elif st.session_state.stage == 'results':
    st.write("### Results")
    if st.session_state.results is not None:
        #Show summary of top matches
        top_matches = st.session_state.results[st.session_state.results['Similarity Ranking'] <= 3]
        if len(top_matches) > 0:
            st.write(f"**Found {len(top_matches)} strong matches (ranking ≤ 3)**")
        # Display the dataframe with similarity rankings
        st.dataframe(st.session_state.results)
        
        # Add download button
        csv = st.session_state.results.to_csv(index=False)
        st.download_button(
            label="Download results as CSV",
            data=csv,
            file_name="similarity_analysis.csv",
            mime="text/csv"
        )
        
        # Add option to start over
        if st.button("Start Over"):
            st.session_state.stage = 'description'
            st.session_state.target_desc = ""
            st.session_state.results = None
            st.rerun()
    else:
        st.error("No results to display. Please start over.")
        if st.button("Start Over"):
            st.session_state.stage = 'description'
            st.rerun()