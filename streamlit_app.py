import streamlit as st

pg = st.navigation({
    "Labs": [
        st.Page("Lab1.py", title="Lab 1"),
        st.Page("Lab2.py", title="Lab 2"),
        st.Page("Lab2.py", title="Lab 3"),
        st.Page("Lab2.py", title="Lab 4"),
        st.Page("Lab2.py", title="Lab 5"),
        st.Page("Lab2.py", title="Lab 6"),
        st.Page("Lab2.py", title="Lab 7"),
        st.Page("Lab2.py", title="Lab 8"),
        st.Page("Lab2.py", title="Lab 9"),
        st.Page("Lab2.py", title="Lab 10")
        ]
    }
)    
pg.run()