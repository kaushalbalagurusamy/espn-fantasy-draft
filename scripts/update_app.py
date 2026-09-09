with open("app.py", "r") as f:
    content = f.read()

# Make sure state always syncs from disk if session state history is shorter than disk history
sync_code = """
# Initialize or sync session state
if 'draft_state' not in st.session_state:
    st.session_state.draft_state = DraftState()
else:
    # Auto-sync if disk has newer state
    st.session_state.draft_state.load_from_disk()
"""

content = content.replace("""# Initialize or sync session state
if 'draft_state' not in st.session_state:
    st.session_state.draft_state = DraftState()""", sync_code)

with open("app.py", "w") as f:
    f.write(content)
print("Updated app.py with auto-sync from disk!")
