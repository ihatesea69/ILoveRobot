"""
Configuration settings for Raspberry Pi 5 optimization
"""

# Camera settings
CAMERA_SETTINGS = {
    'width': 640,
    'height': 480,
    'fps': 15,
    'buffer_size': 1,
    'device_index': 0  # Use Pi Camera Module
}

# Processing settings
PROCESSING = {
    'width': 320,
    'height': 240,
    'max_hands': 1,
    'detection_confidence': 0.6,
    'tracking_confidence': 0.5,
    'model_complexity': 0
}

# Display settings
DISPLAY = {
    'video_codec': 'MJPG',
    'video_fps': 30,
    'buffer_size': 1,
    'font_size': 300
}

# Performance optimizations
PERFORMANCE = {
    'enable_threading': True,
    'enable_multiprocessing': False,  # Multiprocessing can be heavy on Pi
    'use_hardware_acceleration': True,
    'opencv_threads': 4  # Limit OpenCV threads
}

# System optimizations
SYSTEM = {
    'disable_gui': True,  # Run headless for better performance
    'priority_nice': -10,  # Higher process priority
    'gpu_mem': 128,  # MB allocated to GPU
    'overclock': False  # Enable only if proper cooling
}

# Debug settings
DEBUG = {
    'enable_logging': True,
    'log_level': 'INFO',
    'show_fps': False,
    'show_detection_boxes': False
} 