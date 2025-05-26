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

# Function to reset all processing-related session state variables
# This ensures a clean slate when user clicks "Start Over"
def reset_processing():
    """Reset all processing-related session state"""
    # List of all session state keys that need to be cleared for a fresh start
    keys_to_reset = [
        'processing_progress',  # Tracks how many items have been processed (integer counter)
        'processing_active',    # Boolean flag indicating if processing is currently running
        'processed_data',       # Stores the final DataFrame with all similarity scores calculated
        'df_to_process',        # Holds the original DataFrame that's being worked on during processing
        'stage',                # Current app stage ('description', 'upload', or 'results')
        'target_desc',          # The user's input company description used for comparisons
        'results'               # Final sorted results ready for display
    ]
    # Loop through each key and delete it if it exists in session state
    for key in keys_to_reset:
        if key in st.session_state:
            del st.session_state[key]  # Completely remove the variable from memory
    # Set the app back to the initial description input stage
    st.session_state.stage = 'description'

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

# Initialize all session state variables if they don't exist
# Session state persists data across Streamlit reruns (page refreshes)
if 'stage' not in st.session_state:
    st.session_state.stage = 'description'  # Start at description input stage
if 'target_desc' not in st.session_state:
    st.session_state.target_desc = ""  # User's company description
if 'results' not in st.session_state:
    st.session_state.results = None  # Final processed results
# NEW: Additional session state variables for robust processing
if 'processing_progress' not in st.session_state:
    st.session_state.processing_progress = 0  # Counter: how many items processed so far
if 'processing_active' not in st.session_state:
    st.session_state.processing_active = False  # Flag: is processing currently running
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None  # Backup of completed processing results

# STAGE 1: Description input stage
# User enters their company description for comparison
if st.session_state.stage == 'description':
    with st.form("company_description"):
        st.write("Escribe aquí la descripción.")
        target_desc = st.text_area("", height=150)
        submitted = st.form_submit_button("Submit Description")
        
        # When form is submitted with valid description, move to file upload stage
        if submitted and target_desc:
            st.session_state.target_desc = target_desc
            st.session_state.stage = 'upload'
            st.rerun()  # Refresh page to show upload stage

# STAGE 2: File upload and processing stage
# This is where the major efficiency improvements are implemented
elif st.session_state.stage == 'upload':
    # Show a snippet of the target description for reference
    st.write(f"**Target Description:** {st.session_state.target_desc[:100]}...")
    
    file = st.file_uploader("Sube el archivo de Excel")
    if file is not None:
        try:
            # EFFICIENCY IMPROVEMENT: Only initialize processing once
            # Check if we're not already processing AND haven't completed processing
            if not st.session_state.processing_active and st.session_state.processed_data is None:
                # Initial setup: Read and prepare the Excel file
                df = pd.read_excel(file, skiprows=6).iloc[:-2].drop(columns=['Deal ID'], errors='ignore')
                
                # Validate that required column exists
                if 'Description' not in df.columns:
                    st.error("Excel file must have a 'Description' column")
                    st.stop()
                
                # EFFICIENCY IMPROVEMENT: Store dataframe in session state for persistence
                # This prevents re-reading the file on every rerun
                st.session_state.df_to_process = df
                st.session_state.processing_active = True  # Mark processing as active
                st.session_state.processing_progress = 0   # Reset progress counter
            
            # MAIN PROCESSING LOOP: Handle active processing
            if st.session_state.processing_active:
                df = st.session_state.df_to_process  # Get the stored dataframe
                
                # User warning to prevent interruptions
                st.warning("⚠️ Processing in progress. Please don't refresh the page or navigate away until complete.")
                
                # EFFICIENCY IMPROVEMENT: Real-time progress display that survives reruns
                progress_bar = st.progress(st.session_state.processing_progress / len(df))
                status_text = st.text(f"Processing item {st.session_state.processing_progress + 1} of {len(df)}")
                
                # CORE EFFICIENCY IMPROVEMENT: Process one item per rerun instead of all at once
                # This prevents long-running operations that can be interrupted
                if st.session_state.processing_progress < len(df):
                    # Get the current row to process
                    idx = df.index[st.session_state.processing_progress]
                    
                    # Add similarity column to dataframe if it doesn't exist yet
                    if 'Similarity Ranking' not in df.columns:
                        df.insert(df.columns.get_loc('Description') + 1, 'Similarity Ranking', 0)
                    
                    # Process the current item: call API to get similarity rating
                    df.at[idx, 'Similarity Ranking'] = rate_similarity(
                        str(df.at[idx, 'Description']), 
                        st.session_state.target_desc
                    )
                    
                    # EFFICIENCY IMPROVEMENT: Update progress and save state after each item
                    st.session_state.processing_progress += 1  # Increment counter
                    st.session_state.df_to_process = df        # Save updated dataframe
                    
                    # Small delay to prevent overwhelming the system, then continue processing
                    time.sleep(0.1)  # Brief pause
                    st.rerun()       # Trigger next iteration
                
                else:
                    # PROCESSING COMPLETE: All items have been processed
                    df = df.sort_values('Similarity Ranking', ascending=True)  # Sort by similarity
                    st.session_state.results = df           # Store final results
                    st.session_state.processed_data = df    # Backup of results
                    st.session_state.processing_active = False  # Mark processing as complete
                    st.session_state.stage = 'results'     # Move to results stage
                    st.rerun()  # Show results page
            
            # EFFICIENCY IMPROVEMENT: Handle case where processing was already completed
            # This prevents reprocessing if user navigates back
            elif st.session_state.processed_data is not None:
                st.success("Processing completed! Moving to results...")
                st.session_state.results = st.session_state.processed_data
                st.session_state.stage = 'results'
                st.rerun()
                
        except Exception as e:
            # Error handling: Stop processing on any error
            st.error(f"Error processing Excel file: {str(e)}")
            st.session_state.processing_active = False

# STAGE 3: Results display stage
elif st.session_state.stage == 'results':
    st.write("### Results")
    if st.session_state.results is not None:
        # Show summary of best matches (rankings 1-3 are considered strong matches)
        top_matches = st.session_state.results[st.session_state.results['Similarity Ranking'] <= 3]
        if len(top_matches) > 0:
            st.write(f"**Found {len(top_matches)} strong matches (ranking ≤ 3)**")
        
        # Display the complete results table with similarity rankings
        st.dataframe(st.session_state.results)
        
        # Provide download option for results
        csv = st.session_state.results.to_csv(index=False)
        st.download_button(
            label="Download results as CSV",
            data=csv,
            file_name="similarity_analysis.csv",
            mime="text/csv"
        )
        
        # EFFICIENCY IMPROVEMENT: Use centralized reset function
        # This ensures complete cleanup of all session state variables
        if st.button("Start Over"):
            reset_processing()  # Clean reset of all variables
            st.rerun()          # Return to description stage
    else:
        # Error case: No results available
        st.error("No results to display. Please start over.")
        if st.button("Start Over"):
            reset_processing()  # Clean reset
            st.rerun()