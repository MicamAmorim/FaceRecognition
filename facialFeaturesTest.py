import cv2
import face_recognition
import numpy as np
# Carregar imagem com OpenCV
image = cv2.imread("Data/me.jpg")

# Face Detection
face_locations = face_recognition.face_locations(image)

for (top, right, bottom, left) in face_locations:
    # Draw a box around the face
    cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)


cv2.imshow("Image", image)
cv2.waitKey(0)

cv2.destroyAllWindows()

# Facial Landmarks Detection
face_landmarks_list = face_recognition.face_landmarks(image)

facial_features = [
        'chin',
        'left_eyebrow',
        'right_eyebrow',
        'nose_bridge',
        'nose_tip',
        'left_eye',
        'right_eye',
        'top_lip',
        'bottom_lip']


for face_landmarks in face_landmarks_list:
    for facial_feature in facial_features:
        for point in face_landmarks[facial_feature]:
            image = cv2.circle(image, point, 2, (255,60,170),2)
            
            
cv2.imshow("Image", image)
cv2.waitKey(0)
cv2.destroyAllWindows()




