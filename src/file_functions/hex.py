import binascii
import magic 
import mimetypes

class Hex:
    def __init__(self, hex_string: str):
        self.hex_string = hex_string
        self.binary_data = binascii.unhexlify(self.hex_string.replace(" ", ""))
        
    def make_from_hex(self):
        try:
            # Use python-magic to detect the file type
            mime = magic.Magic(mime=True)  # 'mime=True' returns MIME type
            detected_type = mime.from_buffer(self.binary_data)  # Detect type from the binary data
            
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
                file.write(self.binary_data)

            return True, file_name
        
        except binascii.Error as e:
            return False, f"Error: Invalid hexadecimal string: {e}"
        except Exception as e:
            return False, f"An error occurred: {e}"