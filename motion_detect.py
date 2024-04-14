import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
import pygame
import time
from pytz import timezone 
from datetime import datetime

# Initialize PiCamera
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 30
rawCapture = PiRGBArray(camera, size=(640, 480))

# Initialize pygame
pygame.mixer.init()
#beep_sound = pygame.mixer.Sound("dog-barking.mp3") 

pygame.mixer.music.load("dog-barking.mp3")

#pygame.mixer.init()

# Function to play MP3 file through Bluetooth speaker
def play_mp3():
    # Connect to the Bluetooth speaker
    # Load and play the MP3 file
    #pygame.mixer.music.load("dog-barking.mp3")  # Replace "path_to_your_audio_file.mp3" with the path to your MP3 file
    pygame.mixer.music.play()

    # Wait for the audio to finish playing
    while pygame.mixer.music.get_busy():
    	continue

# Allow the camera to warm up
time.sleep(1)

play_sound=0

# Function to detect motion
def detect_motion():
    # Initialize previous frame
    frame_prev_gray = None
    
    # Capture frames from the camera
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        # Convert frame to numpy array
        image = frame.array
        
        # Convert frame to grayscale
        frame_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        if frame_prev_gray is not None:
            # Calculate absolute difference between the current frame and the previous frame
            frame_diff = cv2.absdiff(frame_gray, frame_prev_gray)
            
            # Apply a threshold to the difference image
            _, thresh = cv2.threshold(frame_diff, 230, 255, cv2.THRESH_BINARY)
            
            # Find contours in the thresholded image
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if len(contours)>1:
                print("Motion detected:"+ str(len(contours)))
            if len(contours)>1:
                #play_mp3()
                ind_time = datetime.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d %H:%M:%S.%f')
                print("Range Motion detected at "+ind_time)
                print("Checking for wind")
                # Check for motion blobs
                play_flag=0
                for contour in contours:
                   x, y, w, h = cv2.boundingRect(contour)
                   area = cv2.contourArea(contour)
                   print("Area: "+str(area))
                   if area > 10:  # Adjust the area threshold as needed
                      print("Contour area large. Intrusion detected, playing sound")
                      play_flag=1
                      cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                      
                if play_flag==1:
                     play_mp3()
                     timestamp = time.strftime("%Y%m%d_%H%M%S")
                     image_filename = f"pics/motion-"+str(timestamp)+".jpg"
                     cv2.imwrite(image_filename, image)

	    # Draw bounding boxes around moving objects
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # Display the frame
        #cv2.imshow('Motion Detection', image)
        
        # Clear the stream in preparation for the next frame
        rawCapture.truncate(0)
        
        # Update previous frame
        frame_prev_gray = frame_gray.copy()
        
        # Check for key press
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):  # Press 'q' to exit
            break

# Call the function to detect motion
detect_motion()

# Release PiCamera resources
camera.close()
cv2.destroyAllWindows()

