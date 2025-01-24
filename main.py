import cv2
import face_recognition
import numpy as np
# Carregar imagem com OpenCV
image = cv2.imread("Data/barackObama.jpg")

# Face Detection
face_locations = face_recognition.face_locations(image)

for (top, right, bottom, left) in face_locations:
    # Draw a box around the face
    cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)


cv2.imshow("Image", image)
cv2.waitKey(0)

cv2.destroyAllWindows()




