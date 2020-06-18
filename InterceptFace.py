import cv2


def crop_face(imagePath):


    # Read the image
    image = cv2.imread(imagePath)
    # turn the image to Gray
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Create the haar cascade
    faceCascade =cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    # Detect face in the image
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5
    )
    # print("Found {0} faces!".format(len(faces)))

    #
    x,y,w,h = faces[0]
    image = image[y:y+h, x:x+w]
    # cv2.imwrite("F:\\kejian\\2020 spring\\computer network\\final project\\code\\DeepFakeDetection-master\\Experiments_DeepFakeDetection\\res1.jpg", image)
    return image


