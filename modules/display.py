import cv2
import threading
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import random
import os

class DisplayManager:
    def __init__(self, screen_width, screen_height, audio_manager):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.audio_manager = audio_manager
        self.loop_max = 3
        
        # Pre-allocate buffers for better performance
        self.background = np.zeros((self.screen_height, self.screen_width, 3), dtype=np.uint8)
        self.display_buffer = np.zeros((self.screen_height, self.screen_width, 3), dtype=np.uint8)
        
        # Set environment variable for OpenCV on Raspberry Pi
        os.environ["OPENCV_VIDEOIO_PRIORITY_MSMF"] = "0"  # Disable MSMF
        os.environ["OPENCV_VIDEOIO_DEBUG"] = "0"  # Disable debug messages
        
        # Initialize window once
        cv2.namedWindow("Robot", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("Robot", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        
        # Cache font for text rendering
        self.font_path = "./resources/AmericanTypewriter.ttc"
        try:
            self.font = ImageFont.truetype(self.font_path, 300)
        except Exception as e:
            print(f"Font Error {e}")
            self.font = None
            
    def optimize_video_capture(self, cap):
        """Optimize video capture settings for Raspberry Pi"""
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimize buffer size
        cap.set(cv2.CAP_PROP_FPS, 30)  # Set optimal FPS
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))  # Use MJPEG codec
        return cap
        
    def display_eye(self, video_path):
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Cannot open video: {video_path}")
            return

        cap = self.optimize_video_capture(cap)
        video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Calculate scaling factors once
        aspect_ratio = video_width / video_height
        new_width = min(self.screen_width, int(aspect_ratio * self.screen_height))
        new_height = min(self.screen_height, int(self.screen_width / aspect_ratio))
        start_x = (self.screen_width - new_width) // 2
        start_y = (self.screen_height - new_height) // 2

        loop_count = 0
        while loop_count < self.loop_max:
            ret, frame = cap.read()
            if not ret:
                loop_count += 1
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            # Efficient frame resizing using pre-allocated buffer
            resized_frame = cv2.resize(frame, (new_width, new_height), 
                                     dst=self.display_buffer[:new_height, :new_width],
                                     interpolation=cv2.INTER_NEAREST)
            
            # Efficient frame copying using pre-allocated background
            self.background[:] = 0
            self.background[start_y:start_y+new_height, start_x:start_x+new_width] = resized_frame

            cv2.imshow("Robot", self.background)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        
    def display_eye_with_audio(self, video_path, audio_path):
        audio_thread = threading.Thread(target=self.audio_manager.play_audio, args=(audio_path,))
        audio_thread.start()
        self.display_eye(video_path)
        audio_thread.join()
        
        greeting_thread = threading.Thread(target=self.audio_manager.play_greeting)
        greeting_thread.start()
        self.display_eye(video_path)
        greeting_thread.join()

    def display_eye_with_audio_no_greeting(self, video_path, audio_path):
        audio_thread = threading.Thread(target=self.audio_manager.play_audio, args=(audio_path,))
        audio_thread.start()
        self.display_eye(video_path)
        audio_thread.join()
        
    def scroll_text(self):
        if self.font is None:
            return
            
        textArr = ["HAPPY NEW YEAR", "CUNG CHÚC TÂN XUÂN", "CHÚC MỪNG NĂM MỚI", "XUÂN ẤT TỴ 2025"]
        text = random.choice(textArr)
        
        # Pre-calculate text dimensions
        text_bbox = self.font.getbbox(text)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        y_pos = (self.screen_height + text_height) // 2 - text_height

        # Create PIL image buffer once
        pil_img = Image.fromarray(self.background)
        draw = ImageDraw.Draw(pil_img)
        
        x_pos = self.screen_width
        count = 0
        
        while count < 1:
            # Clear background efficiently
            self.background[:] = 0
            pil_img = Image.fromarray(self.background)
            draw = ImageDraw.Draw(pil_img)

            # Draw text with shadow
            draw.text((x_pos + 10, y_pos + 10), text, font=self.font, fill=(255, 255, 255))
            draw.text((x_pos, y_pos), text, font=self.font, fill=(0, 0, 255))

            # Convert back to numpy array efficiently
            self.background[:] = np.array(pil_img)

            x_pos -= 30
            if x_pos + text_width < 0:
                x_pos = self.screen_width
                count += 1

            cv2.imshow('Robot', self.background)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break 