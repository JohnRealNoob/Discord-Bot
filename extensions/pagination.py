import discord
from typing import Callable, Optional

class Pagination(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, get_page: Callable):
        self.interaction = interaction
        self.get_page = get_page
        self.total_pages: Optional[int] = None
        self.index = 1
        super().__init__(timeout=100)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.interaction.user:
            await interaction.response.send_message(
                embed=discord.Embed(description="Only the command author can use this.", color=discord.Color.red()),
                ephemeral=True
            )
            return False
        return True

    async def navigate(self):
        emb, self.total_pages = await self.get_page(self.index)
        if self.total_pages == 1:
            await self.interaction.response.send_message(embed=emb)
        else:
            self.update_buttons()
            await self.interaction.response.send_message(embed=emb, view=self)

    async def edit_page(self, interaction: discord.Interaction):
        emb, self.total_pages = await self.get_page(self.index)
        self.update_buttons()
        await interaction.response.edit_message(embed=emb, view=self)

    def update_buttons(self):
        self.children[0].disabled = self.index == 1  # Previous
        self.children[1].disabled = self.index == self.total_pages  # Next
        # Toggle between first/last page for the third button
        self.children[2].emoji = "⏮️" if self.index > 1 else "⏭️"
        self.children[2].disabled = self.total_pages <= 1

    @discord.ui.button(emoji="◀️", style=discord.ButtonStyle.blurple)
    async def previous(self, interaction: discord.Interaction, button: discord.Button):
        self.index -= 1
        await self.edit_page(interaction)

    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.blurple)
    async def next(self, interaction: discord.Interaction, button: discord.Button):
        self.index += 1
        await self.edit_page(interaction)

    @discord.ui.button(emoji="⏭️", style=discord.ButtonStyle.blurple)
    async def jump(self, interaction: discord.Interaction, button: discord.Button):
        self.index = 1 if self.index > 1 else self.total_pages
        await self.edit_page(interaction)

    async def on_timeout(self):
        await self.interaction.edit_original_response(view=None)

    @staticmethod
    def compute_total_pages(total_results: int, results_per_page: int) -> int:
        return ((total_results - 1) // results_per_page) + 1