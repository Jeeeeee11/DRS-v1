from transformers import AutoModelForSeq2SeqLM
from transformers import AutoTokenizer
from transformers import pipeline
import tensorrt

MODEL_NAME_OR_PATH = "flax-community/t5-recipe-generation"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME_OR_PATH, use_fast=True)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME_OR_PATH)

prefix = "items: "
# generation_kwargs = {
#     "max_length": 512,
#     "min_length": 64,
#     "no_repeat_ngram_size": 3,
#     "early_stopping": True,
#     "num_beams": 10,
#     "length_penalty": 1.5,
# }
generation_kwargs = {
    "max_length": 512,
    "min_length": 64,
    "no_repeat_ngram_size": 3,
    "do_sample": True,
    "top_k": 60,
    "top_p": 0.95,
    "num_return_sequences": 3,  # Generate 3 unique sequences
    "temperature": 0.8
}

special_tokens = tokenizer.all_special_tokens
tokens_map = {
    "<sep>": "--",
    "<section>": "\n"
}

def skip_special_tokens(text, special_tokens):
    for token in special_tokens:
        text = text.replace(token, "")

    return text

def target_postprocessing(texts, special_tokens):
    if not isinstance(texts, list):
        texts = [texts]
    
    new_texts = []
    for text in texts:
        text = skip_special_tokens(text, special_tokens)

        for k, v in tokens_map.items():
            text = text.replace(k, v)

        new_texts.append(text)

    return new_texts

def generation_function(texts, num_recipes=1):
    _inputs = texts if isinstance(texts, list) else [texts]
    inputs = [prefix + inp for inp in _inputs]
    inputs = tokenizer(
        inputs, 
        max_length=256, 
        padding="max_length", 
        truncation=True, 
        return_tensors="pt"
    )

    input_ids = inputs.input_ids
    attention_mask = inputs.attention_mask

    generated_recipes = []
    while len(generated_recipes) < num_recipes:
        output_ids = model.generate(
            input_ids=input_ids, 
            attention_mask=attention_mask,
            **generation_kwargs
        )
        generated = output_ids.detach().cpu().numpy()
        generated_recipe = target_postprocessing(
            tokenizer.batch_decode(generated, skip_special_tokens=False),
            special_tokens
        )

        # Check if generated_recipe is unique and contains only inputted ingredients
        unique = True
        for recipe in generated_recipes:
            if generated_recipe == recipe or not all(ingredient in generated_recipe[0] for ingredient in texts[0].split(',')):
                unique = False
                break

        if unique:
            generated_recipes.append(generated_recipe)

    return generated_recipes[0] if num_recipes == 1 else generated_recipes