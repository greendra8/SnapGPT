from PIL import Image, ImageDraw, ImageFont
from time import sleep

class Overlay:
    def overlay_numbers(self, image_path):
        sleep(1)
        # Open the image file
        with Image.open(image_path) as img:
            draw = ImageDraw.Draw(img)
            
            # Define the size and font of the text
            font_size = 80
            font = ImageFont.truetype("arial.ttf", font_size)
            
            # Define the positions for the numbers
            positions = [(400, 10), (400, 100), (400, 190), (400, 280), (400, 380), (400, 470), (400, 560), (400, 650), (400, 740), (400, 835), (400, 930), (400, 1020), (400, 1110)]
            
            # Draw the numbers
            for i, position in enumerate(positions):
                draw.text(position, str(i), font=font, fill="white")
            
            # Save the image
            img.save(image_path)


