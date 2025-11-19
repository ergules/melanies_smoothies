# Import python packages
import streamlit as st
import pandas as pd
import requests
from snowflake.snowpark.functions import col

cnx = st.connection("snowflake")
session = cnx.session()
all_ingredients = session.table("smoothies.public.fruit_options").select(col("fruit_name"))

fruitToSearch = session.table("smoothies.public.fruit_options").select(col("fruit_name"),col("search_on"))
pd_df = fruitToSearch.to_pandas()


# Write directly to the app
st.title(":cup_with_straw: Customize your smoothie!")
st.write(
  """Choose the fuits in your Smoothie!
  """
)

order_name = st.text_input("Smoothie name")
if order_name:
    st.text("Name is " + order_name)

ingredient_list = st.multiselect(
    "Choose up to 5",
    all_ingredients,
    max_selections = 5
)

ingredient_str = ''

if ingredient_list :
    for fruit in ingredient_list:
        ingredient_str += fruit + ' '
        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit, 'SEARCH_ON'].iloc[0]

        st.subheader(fruit + 'Nutrition Info:')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
        sf_df = st.dataframe(data = smoothiefroot_response.json(), use_container_width = True)


submit = st.button("Order!")

if submit and ingredient_str :
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
            values ('""" + ingredient_str + """','""" + order_name +"""')"""
    session.sql(my_insert_stmt).collect()
    st.success("Your smoothie ordered : " + order_name)
