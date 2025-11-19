import cv2
import numpy as np
from Utils.states import Languages


def find_error_in_image_inspect(response: dict, language:Languages):
    reason = None
    if "name" in response and response["name"] == '':
        if language == Languages.ENGLISH.value:
            reason = "person was not detected in the image"
        else:
            reason = "לא זוהתה דמות בתמונה"
    elif "funny_face" in response and response["funny_face"]:
        if language == Languages.ENGLISH.value:
            reason = "it includes a funny face"
        else:
            reason = "היא כוללת פרצוף מצחיק"
    elif "blurry" in response and response["blurry"]:
        if language == Languages.ENGLISH.value:
            reason = "it is blurry"
        else:
            reason = "היא מטושטשת"
    elif "wearing_sunglasses" in response and response["wearing_sunglasses"]:
        if language == Languages.ENGLISH.value:
            reason = "you are wearing sunglasses"
        else:
            reason = "אתה מרכיב משקפי שמש"
    elif "includes_multiple_people" in response and response["includes_multiple_people"]:
        if language == Languages.ENGLISH.value:
            reason = "includes multiple people"
        else:
            reason = "יש בתמונה מספר אנשים"
    elif "wearing_hat" in response and response["wearing_hat"]:
        if language == Languages.ENGLISH.value:
            reason = "you are wearing a hat"
        else:
            reason = "אתה חובש כובע"
    return reason


def check_if_person(image_path: str):
    image = np.asarray(bytearray(image_path), dtype="uint8")
    # 0 is used for grayscale image
    img = cv2.imdecode(image, 0)
    face_classifier = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    # Detect faces in the image
    face = face_classifier.detectMultiScale(img, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    # Draw rectangles around the faces
    for (x, y, w, h) in face:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv2.imwrite("takar.jpg", img)
    return len(face) != 0

def is_image_black(np_array, threshold=10):
    # Calculate average brightness
    avg_brightness = np.mean(np_array)
    
    # If avg brightness is below threshold, consider it black
    return avg_brightness < threshold
