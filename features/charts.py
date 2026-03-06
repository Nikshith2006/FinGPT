import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression

def show_charts(user_expenses):

    st.subheader("📊 Category Distribution")

    cat = user_expenses.groupby("Category")["Amount"].sum()

    if not cat.empty:
        fig1,ax1 = plt.subplots()
        ax1.pie(cat,labels=cat.index,autopct="%1.1f%%")
        st.pyplot(fig1)
