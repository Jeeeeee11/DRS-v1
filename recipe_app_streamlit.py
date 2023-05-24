import streamlit as st
from recipe_generation import generation_function
from streamlit_ace import st_ace
import requests
import os
from PIL import Image


def search_recipe(title, serper_api_key):
    query = f"{title} dish"
    url = f"https://serpapi.com/search.json?q={query}&tbm=isch&api_key={serper_api_key}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if "images_results" in data:
            images = data["images_results"]
            if images:
                image = images[0]
                return image["original"], image["source"]
    return None, None

# Replace this with your Serper API key
serper_api_key = "4e9bb51dde629184a62c67633138d311a9bef367"

# Rest of the code...

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
                    image_url, recipe_url = search_recipe(dish_title, serper_api_key)
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
