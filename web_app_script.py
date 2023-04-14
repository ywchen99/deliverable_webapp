import datetime

import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine

DB_USER = "deliverable_taskforce"
DB_PASSWORD = "learn_sql_2023"
DB_HOSTNAME = "training.postgres.database.azure.com"
DB_NAME = "deliverable"

engine = create_engine(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOSTNAME}:5432/{DB_NAME}")
result = engine.execute("SELECT 1")
result.first()

apptitle = "Deliverable: Visual Insights"
st.title("Deliverable Insights 2022")

date_range = st.sidebar.date_input(
    "Select date range (only for the year 2022)",
    [datetime.date(2022, 1, 1), datetime.date(2022, 12, 31)],
)


@st.cache_data()
def get_data():
    df = pd.read_sql_query(
        """
        select
            rev.datetime::date AS datetime, 
            count(rev.restaurant_id) AS count,
            res.location_city
        from
            reviews rev
        inner join restaurants res
            on res.restaurant_id = rev.restaurant_id
        where
            res.location_city IN ('Amsterdam', 'Rotterdam','Groningen') AND
            datetime BETWEEN '2022-01-01' AND '2022-12-31'
        group by (rev.datetime::date), (res.location_city)
        order by (datetime)
        """,
        con=engine,
    )
    return df


df = get_data()

df_filtered = df.loc[df["datetime"].between(date_range[0], date_range[1])]
fig_filtered = px.line(
    df_filtered,
    x="datetime",
    y="count",
    title="Number of Reviews Per Day",
    color="location_city",
    labels={"datetime": "Date", "count": "Frequency", "location_city": "City"},
)
st.plotly_chart(fig_filtered, theme=None)


st.title("COVID Insights 2022")


@st.cache_data()
def get_data2():
    df_2 = pd.read_sql_query(
        """
        select
            municipality_name,
            total_reported,
            date_of_publication
        from
            municipality_totals_daily
        where
            municipality_name in ('Amsterdam', 'Rotterdam', 'Groningen')
            and
                date_of_publication between '2022-01-01' and '2022-12-31'
        group by
            (date_of_publication::date),
            (municipality_name),
            (total_reported)
        order by
            (date_of_publication)
        """,
        con=engine,
    )
    return df_2


df_2 = get_data2()

df2_filtered = df_2.loc[df_2["date_of_publication"].between(date_range[0], date_range[1])]
fig2_filtered = px.line(
    df2_filtered,
    x="date_of_publication",
    y="total_reported",
    title="Number of COVID Infections per day",
    labels={
        "date_of_publication": "Date of Publication",
        "total_reported": "Total Reported Infections",
        "municipality_name": "Municipality",
    },
    color="municipality_name",
)
st.plotly_chart(fig2_filtered, theme=None)

# Reset Button
if st.sidebar.button("Reset"):
    date_range = [datetime.date(2022, 1, 1), datetime.date(2022, 12, 31)]
    df_filtered = df.loc[df["datetime"].between(date_range[0], date_range[1])]
    df2_filtered = df_2.loc[df_2["date_of_publication"].between(date_range[0], date_range[1])]
