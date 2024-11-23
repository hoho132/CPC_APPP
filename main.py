import os
from flask import Flask, request, jsonify
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime

app = Flask(__name__)

# Authenticate Google Sheets API
def authenticate_google_sheets():
    creds = None
    try:
        creds = service_account.Credentials.from_service_account_file(
            r"C:\Users\hanyo\OneDrive\Desktop\Project Beta\attendanceapp-442302-efaa947b3062.json",  # Adjust the path here
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        service = build('sheets', 'v4', credentials=creds)
        print("Google Sheets authenticated.")
        return service
    except Exception as e:
        print(f"Error authenticating with Google Sheets: {e}")
        return None

# Function to calculate the current week based on the semester's start date
def calculate_current_week():
    # Define the semester start date
    semester_start_date = datetime(2024, 1, 1)  # Adjust to your semester start date
    current_date = datetime.today()

    # Calculate the difference in days
    delta = current_date - semester_start_date

    # Calculate the week number (assuming a 7-day week)
    week_number = (delta.days // 7) + 1
    return week_number

# Function to get session based on the day of the week
def get_session_for_today():
    today = datetime.today()
    if today.weekday() == 1:  # Tuesday (0 is Monday, 1 is Tuesday)
        return "Session 1 (S1)"
    elif today.weekday() == 2:  # Wednesday (0 is Monday, 2 is Wednesday)
        return "Session 2 (S2)"
    else:
        return "No session today"

# Update the attendance in Google Sheets
# Update the attendance in Google Sheets
def update_attendance(service, reg_no):
    sheet_id = '1GP_J9GdAR2GmVzd2dvGEBhQCm7gEoulPqL15LV27Zyk'
    range_name = 'Sheet1!A2:C'  # Modify range to get reg_no and name

    try:
        result = service.spreadsheets().values().get(spreadsheetId=sheet_id, range=range_name).execute()
        values = result.get('values', [])

        found = False
        current_week = calculate_current_week()
        current_session = get_session_for_today()

        print(f"Searching for reg_no: {reg_no}")

        # Loop through the values in the sheet
        for i, row in enumerate(values):
            if len(row) > 2:
                sheet_reg_no = row[2].strip()  # Strip any leading/trailing whitespace from reg_no in sheet
                print(f"Comparing QR reg_no: {reg_no} with Sheet reg_no: {sheet_reg_no}")

                if sheet_reg_no == reg_no:  # Column C is the reg_no
                    found = True
                    name = row[1]  # Assuming Name is in Column B
                    print(f"Found student {name} (Reg No: {reg_no}), updating attendance.")
                    
                    # Mark attendance in a specific column (e.g., Column D for attendance)
                    attendance_cell = f"Sheet1!D{i + 2}"  # Assuming attendance is in Column D
                    attendance_status = f"Week {current_week} - {current_session}"
                    update_data = {
                        "values": [[attendance_status]]
                    }

                    # Update the cell with attendance status
                    service.spreadsheets().values().update(
                        spreadsheetId=sheet_id,
                        range=attendance_cell,
                        valueInputOption="RAW",
                        body=update_data
                    ).execute()

                    print(f"Attendance updated for {name} (Reg No: {reg_no})")
                    break

        if not found:
            print(f"Student with reg_no {reg_no} not found in the sheet.")
            # Optionally, add a new entry here if the student is not found

    except Exception as e:
        print(f"Error updating attendance: {e}")


@app.route('/update-attendance', methods=['POST'])
def update_attendance_route():
    data = request.get_json()

    # Extract reg_no from QR code data
    reg_no = data.get('reg_no')
    
    # Assume reg_no is the data encoded in the QR code
    if reg_no:
        service = authenticate_google_sheets()
        if service:
            # Update attendance in the Google Sheet
            update_attendance(service, reg_no)
            return jsonify({"status": "success", "message": f"Attendance updated for {reg_no}."}), 200
        else:
            return jsonify({"status": "error", "message": "Failed to authenticate Google Sheets."}), 500
    else:
        return jsonify({"status": "error", "message": "Missing reg_no."}), 400


if __name__ == "__main__":
    # Disable Debugger PIN and set Flask to bind to all network interfaces
    os.environ["FLASK_DEBUG_PIN"] = "off"
    
    # Run the Flask app on all available interfaces (0.0.0.0) and port 5000
    app.run(debug=True, host='0.0.0.0', port=5000)
