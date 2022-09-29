from PIL import Image
from PIL.ExifTags import TAGS
from PIL.ExifTags import GPSTAGS

with open('file_19.jpg', 'rb') as image_file:
    img = Image.open(image_file)
# iterating over all EXIF data fields
exif_table = {}
for k, v in img.getexif().items():
    tag = TAGS.get(k)
    exif_table[tag] = v
print(exif_table)

gps_info = {}
for k, v in exif_table['GPSInfo'].items():
    geo_tag = GPSTAGS.get(k)
    gps_info[geo_tag] = v
print(gps_info)
