def resize_image(img, max_width, max_height):
    width, height = img.size

    # Calculate the aspect ratio
    aspect_ratio = width / height

    # Calculate new dimensions to fit within the maximum width and height while preserving aspect ratio
    if width > max_width:
        width = max_width
        height = int(width / aspect_ratio)
    if height > max_height:
        height = max_height
        width = int(height * aspect_ratio)

    return img.resize((width, height))