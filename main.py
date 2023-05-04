import argparse
import re

import cv2
import imutils
import pytesseract
from PIL import Image
from imutils.perspective import four_point_transform

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

not_keep_list = ["Card", "Total"]

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True, help="path to input receipt image")
ap.add_argument("-d", "--debug", type=int, default=-1,
                help = "wheter or not we are visualizing each step of the pipeline")
args = vars(ap.parse_args())

orig = cv2.imread(args["image"])
image = orig.copy()
image = imutils.resize(image, width=500)
ratio = orig.shape[1] / float(image.shape[1])

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (5, 5,), 0)
edged = cv2.Canny(blurred, 75, 200)
cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:5]
cardCnt = None
for c in cnts:
	peri = cv2.arcLength(c, True)
	approx = cv2.approxPolyDP(c, 0.02 * peri, True)
	print(len(approx))
	if len(approx) == 4:
		cardCnt = approx
		break

if cardCnt is None:
	raise Exception(("Could not find receipt outline. "
		"Try debugging your edge detection and contour steps."))

if args["debug"] > 0:
	output = image.copy()
	cv2.drawContours(output, [cardCnt], -1, (0, 255, 0), 2)
	cv2.imshow("Business Card Outline", output)
	cv2.waitKey(0)
card = four_point_transform(orig, cardCnt.reshape(4, 2) * ratio)

cv2.imshow("Business Card Transform", card)
cv2.waitKey(0)
rgb = cv2.cvtColor(card, cv2.COLOR_BGR2RGB)
text = pytesseract.image_to_string(rgb)

phoneNums = re.findall(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]', text)
emails = re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", text)

nameExp = r"^[\w'\-,.][^0-9_!¡?÷?¿/\\+=@#$%ˆ&*(){}|~<>;:[\]]{2,}"
names = re.findall(nameExp, text)

print("test.png")
print("=============")


print("\n")
print("images.txt'")
print("======")

for email in emails:
	print(image.strip())


for name in names:
	print(name.strip())
print("PHONE NUMBERS")
print("=============")

for num in phoneNums:
	print(num.strip())

print("\n")
print("EMAILS")
print("======")

for email in emails:
	print(email.strip())

# show the name/job title header
print("\n")
print("NAME/JOB TITLE")
print("==============")

for name in names:
	print(name.strip())