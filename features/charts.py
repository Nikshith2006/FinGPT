import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression

def show_charts(df):

    st.subheader("Category Distribution")

    cat = df.groupby("Category")["Amount"].sum()

    if not cat.empty:

        fig,ax=plt.subplots()
        ax.pie(cat,labels=cat.index,autopct="%1.1f%%")

        st.pyplot(fig)

    st.subheader("Daily Spending")

    daily=df.groupby(df["Date"])["Amount"].sum()

    fig2,ax2=plt.subplots()
    daily.plot(kind="bar",ax=ax2)

    st.pyplot(fig2)