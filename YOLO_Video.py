from ultralytics import YOLO
import cv2
from shapely.geometry import Polygon, Point
import psycopg2
from datetime import datetime
import pygame
import csv


def insert_data_into_database(alert_type, message, screenshot_bytes):
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        database="p_database",
        user="postgres",
        password="Bhakti@2004",
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()
    # Insert data into the database
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("INSERT INTO pro_pids_table (timestamp,alert_type,message, screenshot) VALUES (%s, %s, %s, %s)",
                (timestamp, alert_type, message, psycopg2.Binary(screenshot_bytes)))
    # Commit the transaction
    conn.commit()
    # Close the cursor and connection
    cur.close()
    conn.close()


def play_sound(frequency, duration):
    pygame.mixer.init()
    pygame.mixer.music.load(f'sounds/beep_{frequency}.wav')
    pygame.mixer.music.play()
    pygame.time.delay(duration)
    pygame.mixer.music.stop()

def fetch_data_from_database_and_write_to_csv(table_name, csv_file_path):
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        database="p_database",
        user="postgres",
        password="Bhakti@2004",
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()
    # Execute a query to select all data from the table
    cur.execute(f"SELECT * FROM {table_name}")
    # Fetch all the rows
    rows = cur.fetchall()
    # Write data to CSV file
    with open(csv_file_path, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        # Write header
        writer.writerow(['id', 'timestamp', 'alert_type', 'message'])
        # Write rows
        for row in rows:
            writer.writerow(row)
    # Close the cursor and connection
    cur.close()
    conn.close()


def video_detection(path_x,p1x1, p1y1, p1x2, p1y2, p1x3, p1y3, p1x4, p1y4, p2x1, p2y1, p2x2, p2y2, p2x3, p2y3, p2x4, p2y4, p3x1, p3y1, p3x2, p3y2, p3x3, p3y3, p3x4, p3y4):
    video_capture = path_x
    cap = cv2.VideoCapture(video_capture)

    model = YOLO("YOLO-Weights/yolov8n.pt")
    classNames = ["person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat",
                  "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
                  "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella",
                  "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite", "baseball bat",
                  "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
                  "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli",
                  "carrot", "hot dog", "pizza", "donut", "cake", "chair", "sofa", "pottedplant", "bed",
                  "diningtable", "toilet", "tvmonitor", "laptop", "mouse", "remote", "keyboard", "cell phone",
                  "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors",
                  "teddy bear", "hair drier", "toothbrush"
                  ]

    # Convert the vertices to integers
    polygon1_vertices = [(int(p1x1), int(p1y1)), (int(p1x2), int(p1y2)), (int(p1x3), int(p1y3)), (int(p1x4), int(p1y4))]
    polygon2_vertices = [(int(p2x1), int(p2y1)), (int(p2x2), int(p2y2)), (int(p2x3), int(p2y3)), (int(p2x4), int(p2y4))]
    polygon3_vertices = [(int(p3x1), int(p3y1)), (int(p3x2), int(p3y2)), (int(p3x3), int(p3y3)), (int(p3x4), int(p3y4))]

    # Define the polygons
    polygon1 = Polygon(polygon1_vertices)
    polygon2 = Polygon(polygon2_vertices)
    polygon3 = Polygon(polygon3_vertices)

    screenshot_counter1 = 0
    screenshot_counter2 = 0
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    while True:
        success, img = cap.read()

        # Check if the frame was read successfully
        if not success:
            break

        # Draw polygon vertices on the image
        for vertex in polygon1_vertices:
            cv2.circle(img, vertex, 5, (0, 0, 0), -1)
        for vertex in polygon2_vertices:
            cv2.circle(img, vertex, 5, (0, 0, 0), -1)
        for vertex in polygon3_vertices:
            cv2.circle(img, vertex, 5, (0, 0, 0), -1)

        results = model(img, stream=True)

        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                cls = int(box.cls[0])
                if 0 <= cls < len(classNames) and classNames[cls] == "person":
                    center_x = (x1 + x2) // 2
                    center_y = (y1 + y2) // 2

                    # Check if person detected in red zone
                    if polygon1.contains(Point(center_x, center_y)):
                        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 3)
                        alert_message = "ALERT : Person detected in red zone!"
                        cv2.putText(img, alert_message, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2,cv2.LINE_AA)
                        cv2.putText(img, timestamp, (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1,cv2.LINE_AA)
                        screenshot_path = f"screenshot/red_image_{timestamp}_{screenshot_counter2}.png"
                        cv2.imwrite(screenshot_path, img)
                        _, screenshot_bytes = cv2.imencode('.png', img)
                        insert_data_into_database("Red", alert_message, screenshot_bytes)
                        play_sound(2500, 1000)
                        screenshot_counter2 += 1

                    # Check if person detected in orange zone
                    elif polygon2.contains(Point(center_x, center_y)):
                        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 165, 255), 3)
                        alert_message = "ALERT : Person detected in orange zone!"
                        cv2.putText(img, alert_message, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 2,cv2.LINE_AA)
                        cv2.putText(img, timestamp, (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1,cv2.LINE_AA)
                        screenshot_path = f"screenshot/orange_image_{timestamp}_{screenshot_counter1}.png"
                        cv2.imwrite(screenshot_path, img)
                        _, screenshot_bytes = cv2.imencode('.png', img)
                        insert_data_into_database("Orange", alert_message, screenshot_bytes)
                        play_sound(1500, 800)
                        screenshot_counter1 += 1

                    # Check if person detected in green zone
                    elif polygon3.contains(Point(center_x, center_y)):
                        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 3)
                        alert_message = "Person detected in green zone"
                        cv2.putText(img, alert_message, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2,cv2.LINE_AA)

        yield img

    # Release the video capture object
    # cap.release()
    cv2.destroyAllWindows()

# Fetch data from the table and write to a CSV file
fetch_data_from_database_and_write_to_csv("pro_pids_table", "new_csvfile.csv")
