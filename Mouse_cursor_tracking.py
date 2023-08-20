import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import os
import threading
import time
import pandas as pd

class VideoPlayerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Player App")

        self.video_path = ""
        self.human_video_path = ""

        self.video_label = tk.Label(root, text="Select the video to play (mp4 format only):")
        self.video_label.pack(pady=10)

        self.select_button = tk.Button(root, text="Select Video", command=self.select_video)
        self.select_button.pack(pady=5)

        self.play_button = tk.Button(root, text="Play Video", command=self.play_and_capture)
        self.play_button.pack(pady=5)

        self.name_entry_label = tk.Label(root, text="Enter your name:")
        self.name_entry_label.pack(pady=5)

        self.name_entry = tk.Entry(root)
        self.name_entry.pack(pady=5)

        self.video_player = None
        self.camera_thread = None
        self.is_capturing = False
        self.stop_camera = False

        self.start_time_label = tk.Label(root, text="Video Start Time:")
        self.start_time_label.pack(pady=5)

        self.camera_start_time_label = tk.Label(root, text="Camera Start Time:")
        self.camera_start_time_label.pack(pady=5)

        self.end_time_label = tk.Label(root, text="End Time:")
        self.end_time_label.pack(pady=5)

        self.timestamps = []

    def select_video(self):
        self.video_path = filedialog.askopenfilename(title="Select Video File", filetypes=[("Video files", "*.mp4")])

        if self.video_path:
            self.video_label.config(text=f"Selected video: {os.path.basename(self.video_path)}")

    def modify_video_path(self, name):
        directory, filename = os.path.split(self.video_path)
        new_directory = os.path.join(directory, name).replace("\\", "/")

        if not os.path.exists(new_directory):
            os.makedirs(new_directory)
        return new_directory

    def play_and_capture(self):
        if not self.video_path:
            messagebox.showerror("Error", "Please select a video to play.")
            return

        name = self.name_entry.get()
        if not name:
            messagebox.showerror("Error", "Please enter your name.")
            return

        self.is_capturing = True
        self.camera_thread = threading.Thread(target=self.capture_frames, args=(name,))
        self.camera_thread.start()

        start_time = time.strftime("%Y-%m-%d %H:%M:%S")
        self.start_time_label.config(text="Video Start Time: " + start_time)
        self.camera_start_time_label.config(text="Camera Start Time: " + start_time)

        self.set_play_button_text("Playing")

        # Set a delay
        delay = 2  # 2 seconds delay
        time.sleep(delay)

        self.play_video()

        self.is_capturing = False
        self.camera_thread.join()

        end_time = time.strftime("%Y-%m-%d %H:%M:%S")
        self.end_time_label.config(text="End Time: " + end_time)

        self.save_times_to_file(name, start_time, end_time)

    def set_play_button_text(self, text):
        self.play_button.config(text=text)

    def save_times_to_file(self, name, start_time, end_time):
        video_folder = os.path.dirname(self.video_path)
        output_filename = os.path.join(video_folder, f"{name}_video_times.txt")

        with open(output_filename, "w") as file:
            file.write(f"Video Start Time: {start_time}\n")
            file.write(f"Camera Start Time: {start_time}\n")
            file.write(f"End Time: {end_time}")

    def play_video(self):
        cap = cv2.VideoCapture(self.video_path)
        video_fps = cap.get(cv2.CAP_PROP_FPS)

        self.video_start_time = time.time()

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            time.sleep(1 / video_fps)
            cv2.imshow("Video Player", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord(' '):
                self.record_timestamp()

        cap.release()
        cv2.destroyAllWindows()
        self.stop_camera = True

    def record_timestamp(self):
        if self.video_start_time is not None:
            elapsed_time = time.time() - self.video_start_time
            self.timestamps.append(elapsed_time)
            self.save_timestamps_to_csv()

    def save_timestamps_to_csv(self):
        if self.timestamps:
            csv_file = os.path.join(self.human_video_path, "timestamps.csv").replace("\\", "/")
            data = {"Elapsed Time (seconds)": self.timestamps}
            df = pd.DataFrame(data)
            df.to_csv(csv_file, index=False)

    def capture_frames(self, name):
        camera_w = 1280
        camera_h = 720

        capture = cv2.VideoCapture(0)
        capture.set(cv2.CAP_PROP_FRAME_WIDTH, camera_w)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, camera_h)

        camera_fps = capture.get(cv2.CAP_PROP_FPS)

        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.human_video_path = self.modify_video_path(name)
        output_filename = os.path.join(self.human_video_path, f"{name}_{os.path.splitext(os.path.basename(self.video_path))[0]}.avi").replace("\\", "/")
        out = cv2.VideoWriter(output_filename, fourcc, camera_fps, (camera_w, camera_h))

        while self.is_capturing and not self.stop_camera:
            ret, frame = capture.read()
            if not ret:
                break

            out.write(frame)

        capture.release()
        out.release()

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoPlayerApp(root)
    root.mainloop()
