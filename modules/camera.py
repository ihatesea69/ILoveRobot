import cv2
import mediapipe as mp
import time
from utils.logger import Logger

class CameraDetector:
    def __init__(self):
        self.detection_result = {"human_detected_by_cam": False, "waving_hand": False}
        self.logger = Logger()
        self.logger.info("Camera detector initialized")
        
        # Initialize MediaPipe
        self.mp_drawing_util = mp.solutions.drawing_utils
        self.mp_hand = mp.solutions.hands
        self.mp_pose = mp.solutions.pose
        
        self.hands = self.mp_hand.Hands(
            model_complexity=0,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5
        )
        
        self.cap = cv2.VideoCapture(1)
        self.prev_time = 0
        self.fps = 10
        self.interval = 1 / self.fps
        
    def detect(self):
        current_time = time.time()
        
        if current_time - self.prev_time >= self.interval:
            success, img = self.cap.read()
            if not success:
                print("Failed to read frame from camera.")
                return self.detection_result
            
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            hand_results = self.hands.process(img)
            pose_results = self.pose.process(img)
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            
            human_detected = False
            waving_hand = False
            
            if hand_results.multi_hand_landmarks:
                for hand in hand_results.multi_hand_landmarks:
                    self.mp_drawing_util.draw_landmarks(img, hand, self.mp_hand.HAND_CONNECTIONS)
                    landmarks = hand.landmark
                    if landmarks[4].x > landmarks[3].x and landmarks[8].y < landmarks[6].y:
                        waving_hand = True
            
            if pose_results.pose_landmarks:
                self.mp_drawing_util.draw_landmarks(
                    img, pose_results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS
                )
                human_detected = True
            
            self.detection_result = {
                "human_detected_by_cam": human_detected,
                "waving_hand": waving_hand
            }
            
            self.prev_time = current_time
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.cap.release()
                cv2.destroyAllWindows()
                
        return self.detection_result
    
    def __del__(self):
        self.cap.release() 