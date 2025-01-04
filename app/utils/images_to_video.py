import cv2
import os

def images_to_video(image_folder: str, video_path: str, fps: int = 30, image_format: str = ".png"):
    images = [img for img in os.listdir(image_folder) if img.endswith(image_format)]
    images.sort()  # Ensure the images are in the correct order

    if not images:
        print("No images found in the folder.")
        return

    first_image_path = os.path.join(image_folder, images[0])
    frame = cv2.imread(first_image_path)
    if frame is None:
        print(f"Error: Failed to load the first image {first_image_path}")
        return
    height, width, layers = frame.shape

    video = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'H264'), fps, (width, height))

    for image in images:
        image_path = os.path.join(image_folder, image)
        frame = cv2.imread(image_path)
        if frame is None:
            print(f"Error: Failed to load image {image_path}")
            continue
        video.write(frame)

    video.release()