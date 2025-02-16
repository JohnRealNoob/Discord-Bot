from deep_translator import GoogleTranslator
import Levenshtein
from data.lang_list import LANGUAGES

class Language:
    def __init__(self):
        self.languages = LANGUAGES

    async def translate_text(self, lang_code, text) -> str:      
        # Check if the provided language code is valid
        if lang_code not in self.languages:
            return "Invalid language code! Please use a valid one."

        try:
            # Translate the text using deep-translator
            translated_text = GoogleTranslator(source='auto', target=lang_code).translate(text)
            return f"Translated to {self.languages[lang_code]}: {translated_text}"
        except Exception as e:
            return f"An error occurred during translation: {str(e)}"

    async def search_language_code(self, language_name: str) -> str:
        # Normalize the input to lowercase for case-insensitive comparison
        language_name = language_name.lower()

        # Create a reverse dictionary from LANGUAGES
        reverse_languages = {name.lower(): code for code, name in self.languages.items()}

        # List of available languages
        available_languages = list(reverse_languages.keys())

        # Initialize the minimum distance and closest match
        min_distance = float('inf')
        closest_match = None

        # Find the closest match using Levenshtein distance
        for lang in available_languages:
            distance = Levenshtein.distance(language_name, lang)
            if distance < min_distance:
                min_distance = distance
                closest_match = lang

        # Define a threshold for considering a match
        threshold = 5  # This value can be adjusted based on requirements

        if min_distance <= threshold:
            lang_code = reverse_languages[closest_match]
            return lang_code
        else:
            return "Language not found. Please make sure the language name is correct."
        
    async def list_all_languages(self, page: int = 0, items_per_page: int = 10) -> str:
        languages_list = [f"{name.title()} (`{code}`)" for code, name in self.languages.items()]
        total_pages = len(languages_list) // items_per_page + (1 if len(languages_list) % items_per_page > 0 else 0)
        
        start = page * items_per_page
        end = start + items_per_page
        page_content = "\n".join(languages_list[start:end])
        
        return page_content, total_pages