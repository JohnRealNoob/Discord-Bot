import discord
from discord.ext import commands
from discord import app_commands

import binascii
import magic 
import mimetypes

import os
        
class DecodeFile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def make_from_hex(self, hex_string):

        binary_data = binascii.unhexlify(hex_string.replace(" ", ""))

        try:
            # Use python-magic to detect the file type
            mime = magic.Magic(mime=True)  # 'mime=True' returns MIME type
            detected_type = mime.from_buffer(binary_data)  # Detect type from the binary data
            
            # If no MIME type is detected, default to 'application/octet-stream'
            if not detected_type:
                detected_type = "application/octet-stream"
            
            # Generate a file extension based on MIME type
            file_extension = mimetypes.guess_extension(detected_type)
            
            # Default to .bin if no extension is found
            if not file_extension:
                file_extension = ".bin"
            
            # Generate a filename based on the detected file type or fallback to .bin
            file_name = f"output{file_extension}"
            
            # Write the binary data to the file
            with open(file_name, 'wb') as file:
                file.write(binary_data)

            return True, file_name
        
        except binascii.Error as e:
            return False, f"Error: Invalid hexadecimal string: {e}"
        except Exception as e:
            return False, f"An error occurred: {e}"
        
    @app_commands.command(name="make_file_hex", description="Make file from base 16")
    async def warn(self, interaction: discord.Interaction, hex_string: str):
        
        success, file_name = self.make_from_hex(hex_string)

        if success:
            await interaction.response.send_message(file=discord.File(file_name))
            os.remove(file_name)
        else:
            await interaction.response.send_message(file_name)

def setup(bot):
    bot.add_cog(DecodeFile(bot))