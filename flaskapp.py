import psycopg2
from flask import Flask, render_template, Response, request, jsonify, redirect, session
import cv2
from YOLO_Video import video_detection
from datetime import datetime
import base64

app = Flask(__name__)
app.config['SECRET_KEY'] = 'bhakti'
app.config['UPLOAD_FOLDER'] = 'static/files'

SCREENSHOT_FOLDER = r'D:\human_intrusion_detection_system\screenshot'
def generate_frames_web(path_x, p1x1=0, p1y1=0, p1x2=0, p1y2=472, p1x3=230, p1y3=472, p1x4=230, p1y4=0, p2x1=230, p2y1=0, p2x2=230, p2y2=472, p2x3=430, p2y3=472, p2x4=430, p2y4=0, p3x1=430, p3y1=0, p3x2=430, p3y2=472, p3x3=614, p3y3=472, p3x4=614, p3y4=0, total_red_alerts=None, total_orange_alerts=None):
    yolo_output = video_detection(path_x, p1x1, p1y1, p1x2, p1y2, p1x3, p1y3, p1x4, p1y4, p2x1, p2y1, p2x2, p2y2, p2x3, p2y3, p2x4, p2y4, p3x1, p3y1, p3x2, p3y2, p3x3, p3y3, p3x4, p3y4)
    for detection_ in yolo_output:
        ref, buffer = cv2.imencode('.jpg', detection_)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n'
               b'X-Total-Red-Alerts: ' + str(total_red_alerts).encode() + b'\r\n'
               b'X-Total-Orange-Alerts: ' + str(total_orange_alerts).encode() + b'\r\n\r\n' + frame + b'\r\n')


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    return render_template('indexproject.html')

@app.route('/logout')
def logout():
    # Clear the session data
    session.clear()
    # Redirect the user to the login or home page
    return redirect('/home')

@app.route("/webcam", methods=['GET', 'POST'])
def webcam():
    return render_template('ui.html')

@app.route('/submit', methods=['POST'])
def submit():
    # Extract form data
    # Assuming form fields are named as p1x1, p1y1, ..., p3y4
    form_data = {k: request.form[k] for k in request.form}

    # Render the output_page.html template with the provided form data
    return render_template('output_page.html', form_data=form_data)

@app.route('/get_total_counts')
def get_total_counts():
    total_red_alerts = len(get_images_from_database("Red"))
    total_orange_alerts = len(get_images_from_database("Orange"))
    return jsonify({'total_red_alerts': total_red_alerts, 'total_orange_alerts': total_orange_alerts})

@app.route('/output_page')
def output_page():
    # Get form data from URL parameters
    form_data = {k: request.args.get(k) for k in request.args}

    # Get total number of red and orange alert types from the database
    total_red_alerts = len(get_images_from_database("Red"))
    total_orange_alerts = len(get_images_from_database("Orange"))

    # Return the frames as a multipart response with total alert counts included in headers
    return Response(generate_frames_web(0, **form_data, total_red_alerts=total_red_alerts, total_orange_alerts=total_orange_alerts), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/about_us')
def about_us():
    # You can pass any necessary data to about_us.html here
    return render_template('about_us.html')

def get_images_from_database(alert_type, start_date=None, end_date=None):
    conn = psycopg2.connect(
        dbname='p_database',
        user='postgres',
        password='Bhakti@2004',
        host='localhost'
    )
    cursor = conn.cursor()
    # query = "SELECT screenshot FROM pro_pids_table WHERE alert_type = %s"
    query = "SELECT screenshot FROM pro_pids_table WHERE alert_type = %s"
    params = [alert_type]

    if start_date and end_date:
        # Convert string dates to datetime objects
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')

        # Adjust end_date to include end of day
        end_date = end_date.replace(hour=23, minute=59, second=59)

        query += " AND timestamp BETWEEN %s AND %s"  # Assuming 'timestamp' is the column name
        params.extend([start_date, end_date])

    cursor.execute(query, tuple(params))
    images = cursor.fetchall()
    conn.close()
    return [base64.b64encode(image[0]).decode('utf-8') for image in images]



@app.route("/red_table")
def red_table():
    # Extract start and end dates from query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    conn = psycopg2.connect(
        dbname='p_database',
        user='postgres',
        password='Bhakti@2004',
        host='localhost'
    )
    cursor = conn.cursor()

    # Build the SQL query based on the date range and alert_type
    query = "SELECT id, timestamp, alert_type, message, screenshot FROM pro_pids_table WHERE alert_type = 'Red'"
    params = []

    if start_date and end_date:
        # Convert string dates to datetime objects
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')

        # Adjust end_date to include end of day
        end_date = end_date.replace(hour=23, minute=59, second=59)

        query += " AND timestamp BETWEEN %s AND %s"  # Assuming 'timestamp' is the column name
        params.extend([start_date, end_date])

    cursor.execute(query, params)

    # Fetch all rows from the table and reverse the order
    rows = cursor.fetchall()[::-1]

    # Close the database connection
    cursor.close()
    conn.close()

    # Convert image data to base64 encoding
    encoded_rows = []
    for row in rows:
        encoded_image = base64.b64encode(row[4]).decode('utf-8')
        encoded_row = list(row)
        encoded_row[4] = encoded_image  # Replace the screenshot data with encoded image
        encoded_rows.append(encoded_row)

    # Render the template with the fetched and encoded data
    return render_template("red_table.html", rows=encoded_rows)

@app.route("/orange_table")
def orange_table():
    # Extract start and end dates from query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    conn = psycopg2.connect(
        dbname='p_database',
        user='postgres',
        password='Bhakti@2004',
        host='localhost'
    )
    cursor = conn.cursor()

    # Build the SQL query based on the date range and alert_type
    query = "SELECT id, timestamp, alert_type, message, screenshot FROM pro_pids_table WHERE alert_type = 'Orange'"
    params = []

    if start_date and end_date:
        # Convert string dates to datetime objects
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')

        # Adjust end_date to include end of day
        end_date = end_date.replace(hour=23, minute=59, second=59)

        query += " AND timestamp BETWEEN %s AND %s"  # Assuming 'timestamp' is the column name
        params.extend([start_date, end_date])

    cursor.execute(query, params)

    # Fetch all rows from the table and reverse the order
    rows = cursor.fetchall()[::-1]

    # Close the database connection
    cursor.close()
    conn.close()

    # Convert image data to base64 encoding
    encoded_rows = []
    for row in rows:
        encoded_image = base64.b64encode(row[4]).decode('utf-8')
        encoded_row = list(row)
        encoded_row[4] = encoded_image  # Replace the screenshot data with encoded image
        encoded_rows.append(encoded_row)

    # Render the template with the fetched and encoded data
    return render_template("orange_table.html", rows=encoded_rows)

if __name__ == "__main__":
    app.run(debug=True)
