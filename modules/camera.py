import cv2
import mediapipe as mp
import time
import numpy as np
from utils.logger import Logger

class CameraDetector:
    def __init__(self):
        self.detection_result = {"human_detected_by_cam": False, "waving_hand": False}
        self.logger = Logger()
        self.logger.info("Camera detector initialized")
        
        # Initialize MediaPipe with optimized settings for Raspberry Pi
        self.mp_drawing_util = mp.solutions.drawing_utils
        self.mp_hand = mp.solutions.hands
        self.mp_pose = mp.solutions.pose
        
        # Optimize hand detection for Raspberry Pi
        self.hands = self.mp_hand.Hands(
            model_complexity=0,  # Use lightest model
            min_detection_confidence=0.6,  # Slightly higher threshold for better performance
            min_tracking_confidence=0.5,
            max_num_hands=1  # Limit to one hand for better performance
        )
        
        # Optimize pose detection for Raspberry Pi
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=0,  # Use lightest model
            enable_segmentation=False,
            min_detection_confidence=0.6,  # Slightly higher threshold
            min_tracking_confidence=0.5
        )
        
        # Initialize camera with optimized settings
        self.cap = cv2.VideoCapture(0)  # Use 0 for Raspberry Pi camera module
        
        # Set optimal camera properties for Raspberry Pi
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 15)  # Lower FPS for better performance
        
        # Try to enable hardware acceleration if available
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        
        self.prev_time = 0
        self.fps = 15
        self.interval = 1 / self.fps
        
        # Initialize frame processing parameters
        self.process_width = 320  # Processing resolution
        self.process_height = 240
        
        # Create a fixed-size buffer for frame processing
        self.frame_buffer = np.zeros((self.process_height, self.process_width, 3), dtype=np.uint8)
        
    def detect(self):
        current_time = time.time()
        
        if current_time - self.prev_time >= self.interval:
            success, img = self.cap.read()
            if not success:
                self.logger.error("Failed to read frame from camera.")
                return self.detection_result
            
            # Optimize frame processing
            try:
                # Resize frame efficiently using pre-allocated buffer
                img = cv2.resize(img, (self.process_width, self.process_height), 
                               dst=self.frame_buffer,
                               interpolation=cv2.INTER_NEAREST)
                
                # Convert color space efficiently
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB, dst=self.frame_buffer)
                
                # Process with MediaPipe
                hand_results = self.hands.process(img)
                pose_results = self.pose.process(img)
                
                human_detected = False
                waving_hand = False
                
                # Process hand landmarks if detected
                if hand_results.multi_hand_landmarks:
                    hand = hand_results.multi_hand_landmarks[0]  # Only process first hand
                    landmarks = hand.landmark
                    if landmarks[4].x > landmarks[3].x and landmarks[8].y < landmarks[6].y:
                        waving_hand = True
                
                # Process pose landmarks if detected
                if pose_results.pose_landmarks:
                    human_detected = True
                
                self.detection_result = {
                    "human_detected_by_cam": human_detected,
                    "waving_hand": waving_hand
                }
                
                self.prev_time = current_time
                
            except Exception as e:
                self.logger.error(f"Error processing frame: {str(e)}")
                
        return self.detection_result
    
    def __del__(self):
        self.cap.release()
        cv2.destroyAllWindows() 