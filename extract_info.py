from exif import Image

with open('file_19.jpg', 'rb') as image_file:
    my_image = Image(image_file)
    meta = my_image.has_exif
    print(meta)
    if meta:
        print(my_image.list_all())
        print(my_image.gps_latitude, my_image.gps_longitude)
