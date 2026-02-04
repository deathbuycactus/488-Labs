import streamlit as st

pg = st.navigation({
    "Labs": [
        st.Page("Lab1.py", title="Lab 1"),
        st.Page("Lab2.py", title="Lab 2"),
        st.Page("Lab3.py", title="Lab 3", default=True),
        st.Page("Lab4.py", title="Lab 4"),
        st.Page("Lab5.py", title="Lab 5"),
        st.Page("Lab6.py", title="Lab 6"),
        st.Page("Lab7.py", title="Lab 7"),
        st.Page("Lab8.py", title="Lab 8"),
        st.Page("Lab9.py", title="Lab 9"),
        ]
    }
)    
pg.run()