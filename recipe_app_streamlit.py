import streamlit as st
from recipe_generation import generation_function
from streamlit_ace import st_ace
import requests
import os
from PIL import Image


def search_recipe(title, ingredients, app_id, app_key):
    query = f"{title} {', '.join(ingredients)} dish"
    url = f"https://api.edamam.com/search?q={query}&app_id={app_id}&app_key={app_key}&from=0&to=1"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data["hits"]:
            recipe = data["hits"][0]["recipe"]
            return recipe["image"], recipe["url"]
    return None, None

# Replace these with your Edamam API credentials
app_id = "b0676972"
app_key = "f0125506ff24f7a645dc0f6771731116"

# Custom CSS for styling
st.markdown(
    """
<style>
    .reportview-container .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    h1 {
        font-size: 4rem;
    }
    h2 {
        font-size: 3rem;
    }
    .stButton>button {
        background-color: #000000;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 8px 15px;
    }
</style>
""",
    unsafe_allow_html=True,
)

st.title("Chef Transformer")

# Intro text
st.write(
    "Welcome to the Chef Transformer! Enter a list of ingredients separated by commas, "
    "and the Chef Transformer will generate recipes for you."
)

# Input text using streamlit_ace
items = st_ace(
    placeholder="Enter ingredients (e.g., chicken, brown rice, carrots, garlic, soy sauce, olive oil)",
    language="markdown",
    theme="xcode",
    keybinding="sublime",
    font_size=18,
    height=150,
)

# Generate recipes button
if st.button("Generate Recipes"):
    if items:
        items_list = [items]
        generated_recipes = generation_function(items_list, num_recipes=3)
        ingredients_list = [ingredient.strip() for ingredient in items.split(',')]

        image_urls = []
        recipe_urls = []
        dish_titles = []

        for recipe in generated_recipes:
            text = recipe[0]
            sections = text.split("\n")
            for section in sections:
                section = section.strip()
                if section.startswith("title:"):
                   section = section.replace("title:", "")
                   dish_title = section.strip().capitalize()
                   image_url, recipe_url = search_recipe(dish_title, ingredients_list, app_id, app_key)
                   image_urls.append(image_url)
                   recipe_urls.append(recipe_url)
                   dish_titles.append(dish_title)

        for idx, recipe in enumerate(generated_recipes):
            text = recipe[0]
            sections = text.split("\n")
            for section in sections:
                section = section.strip()
                if section.startswith("title:"):
                    section = section.replace("title:", "")
                    headline = "Title"
                elif section.startswith("ingredients:"):
                    section = section.replace("ingredients:", "")
                    headline = "Ingredients"
                elif section.startswith("directions:"):
                    section = section.replace("directions:", "")
                    headline = "Directions"

                if headline == "Title":
                    st.markdown(f"**{headline}: {section.strip().capitalize()}**", unsafe_allow_html=True)
                elif headline == "Ingredients":
                    section_info = [f"{i+1}. {info.strip().capitalize()}" for i, info in enumerate(section.split("--"))]
                    st.markdown(f"**{headline}:**", unsafe_allow_html=True)
                    for ingredient_info in section_info:
                        ingredient_bold = ingredient_info
                        for ingredient in ingredients_list:
                            if ingredient.lower() in ingredient_info.lower():
                                ingredient_bold = ingredient_info.replace(ingredient, f"**{ingredient}**")
                        st.markdown(ingredient_bold, unsafe_allow_html=True)
                else:
                    section_info = [f"{i+1}. {info.strip().capitalize()}" for i, info in enumerate(section.split("--"))]
                    st.markdown(f"**{headline}:**", unsafe_allow_html=True)
                    st.write("\n".join(section_info))

            if image_urls[idx]:
                st.image(image_urls[idx], caption=dish_titles[idx], width=256)
                st.markdown(f"**[View Recipe]({recipe_urls[idx]})**")

            st.write("-" * 130)

    else:
        st.warning("Please enter ingredients.")
