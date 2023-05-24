import streamlit as st
from recipe_generation import generation_function
from streamlit_ace import st_ace
import requests
import os
from PIL import Image
from serpapi import GoogleSearch


def search_recipe(title, api_key):
    query = f"{title} dish"
    params = {
        "q": query,
        "tbm": "isch",
        "api_key": 4e9bb51dde629184a62c67633138d311a9bef367,
    }
    search = GoogleSearch(params)
    results = search.get_dict()

    if "images_results" in results:
        images = results["images_results"]
        if images:
            image_url = images[0]["original"]
            return image_url
    return None

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
        
        for recipe in generated_recipes:
            text = recipe[0]
            sections = text.split("\n")
        for section in sections:
            section = section.strip()
            if section.startswith("title:"):
                section = section.replace("title:", "")
                headline = "Title"
                dish_title = section.strip().capitalize()
                image_url = search_recipe(dish_title, api_key)
            # ... rest of the section logic

        if image_url:
            st.image(image_url, caption=dish_title, width=256)
            st.markdown(f"**[View Recipe]({recipe_url})**")

        for recipe in generated_recipes:
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

            st.write("-" * 130)
            
    else:
        st.warning("Please enter ingredients.")
