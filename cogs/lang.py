import discord
from discord.ext import commands
from discord import app_commands
from deep_translator import GoogleTranslator
import Levenshtein
from typing import Optional

from extensions.pagination import Pagination

class Languages(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Dynamically fetch supported languages from GoogleTranslator
        self.translator = GoogleTranslator(source='auto', target='en')
        self.languages = self.translator.get_supported_languages(as_dict=True)

    async def translate_text(self, lang_code: str, text: str) -> str:
        """Translate text to the specified language code."""
        if lang_code not in self.languages:
            return f"Invalid language code `{lang_code}`! Use `/show_languages` to see available options."
        
        try:
            translated = GoogleTranslator(source='auto', target=lang_code).translate(text)
            return f"Translated to {self.languages[lang_code]} (`{lang_code}`): {translated}"
        except ValueError as e:
            return f"Translation failed: {str(e)}"
        except Exception as e:
            return f"An unexpected error occurred: {str(e)}"

    async def search_language_code(self, language_name: str) -> tuple[str, Optional[str]]:
        """Search for a language code by name with fuzzy matching."""
        language_name = language_name.lower()
        reverse_languages = {name.lower(): code for code, name in self.languages.items()}
        available_languages = list(reverse_languages.keys())

        min_distance = float('inf')
        closest_match = None

        for lang in available_languages:
            distance = Levenshtein.distance(language_name, lang)
            if distance < min_distance:
                min_distance = distance
                closest_match = lang

        threshold = 5  # Adjustable threshold
        if min_distance <= threshold:
            lang_code = reverse_languages[closest_match]
            return lang_code, f"Found {self.languages[lang_code]} (`{lang_code}`) for '{language_name}'"
        return None, f"No match found for '{language_name}'. Try `/show_languages` for the full list."

    # Autocomplete function for language codes
    async def language_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        current = current.lower()
        suggestions = []
        for code, name in sorted(self.languages.items(), key=lambda x: x[1]):
            distance = min(Levenshtein.distance(current, code.lower()), Levenshtein.distance(current, name.lower()))
            if distance <= 5:  # Threshold for similarity
                suggestions.append((distance, app_commands.Choice(name=f"{name} ({code})", value=code)))
        # Sort by distance, then take top 25
        return [choice for _, choice in sorted(suggestions, key=lambda x: x[0])][:25]

    # Command: Translate with Autocomplete
    @app_commands.command(name="translate", description="Translate text to a specified language")
    @app_commands.describe(lang_code="The language code (e.g., 'es' for Spanish)", text="Text to translate")
    @app_commands.autocomplete(lang_code=language_autocomplete)
    async def translate(self, interaction: discord.Interaction, lang_code: str, text: str):
        result = await self.translate_text(lang_code, text)
        await interaction.response.send_message(result)

    # Command: Search Language Code
    @app_commands.command(name="search_languages", description="Search for a language code by name")
    @app_commands.describe(lang="The name of the language (e.g., 'Spanish')")
    async def search_lang(self, interaction: discord.Interaction, lang: str):
        code, message = await self.search_language_code(lang)
        await interaction.response.send_message(message)

    # Command: List All Available Languages
    @app_commands.command(name="show_languages", description="Show all supported languages")
    async def show_lang(self, interaction: discord.Interaction):
        async def get_page(page: int):
            items_per_page = 10
            emb = discord.Embed(
                title="Supported Languages",
                description="",
                color=discord.Color.blue()
            )
            offset = (page - 1) * items_per_page
            lang_slice = dict(list(self.languages.items())[offset:offset + items_per_page])
            
            for code, name in lang_slice.items():
                emb.add_field(name=name.capitalize(), value=f"`{code}`", inline=True)
            
            total_pages = Pagination.compute_total_pages(len(self.languages), items_per_page)
            emb.set_footer(text=f"Page {page}/{total_pages} • {len(self.languages)} languages")
            emb.set_author(name=f"Requested by {interaction.user}")
            return emb, total_pages

        await Pagination(interaction, get_page).navigate()

async def setup(bot):
    await bot.add_cog(Languages(bot))