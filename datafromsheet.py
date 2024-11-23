import os
import random
import segno
from PIL import Image, ImageDraw, ImageFont
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64

# Constants
CREDS_PATH = r'C:\Users\hanyo\OneDrive\Desktop\Project Beta\attendanceapp-442302-efaa947b3062.json'
SPREADSHEET_ID = '1GP_J9GdAR2GmVzd2dvGEBhQCm7gEoulPqL15LV27Zyk'
RANGE_NAME = 'Sheet1!A2:C'
QR_CODE_FOLDER = r'C:\Users\hanyo\OneDrive\Desktop\Project Beta\QR_Code Beta'
LOGO_PATH = r'C:\finalapp\assets\CPCLOGO.png'
ENCRYPTION_KEY = b'my_secure_key_16'  # Use a secure 16-byte key

# Authenticate and get data from Google Sheets
def authenticate_google_sheets():
    creds = Credentials.from_service_account_file(
        CREDS_PATH, scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
    )
    try:
        service = build('sheets', 'v4', credentials=creds)
        return service
    except HttpError as err:
        print(f"Error: {err}")
        return None

def get_student_data():
    service = authenticate_google_sheets()
    if not service:
        print("Unable to authenticate Google Sheets.")
        return []

    try:
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
        values = result.get('values', [])
        return values
    except HttpError as err:
        print(f"Error: {err}")
        return []

# Encrypt the registration number
def encrypt_data(data):
    cipher = AES.new(ENCRYPTION_KEY, AES.MODE_CBC)  # Use CBC mode
    iv = cipher.iv  # Initialization vector
    encrypted_data = cipher.encrypt(pad(data.encode(), AES.block_size))
    return base64.b64encode(iv + encrypted_data).decode()  # Combine IV and encrypted data

def generate_qr_code_with_shapes(student_details, filename):
    # Ensure data is valid
    if len(student_details) < 3:
        print(f"Insufficient data for student: {student_details}")
        return

    # Extract name and registration number
    name = student_details[0].strip()
    reg_no = student_details[2].strip()

    # Encrypt the registration number
    encrypted_reg_no = encrypt_data(reg_no)

    # Generate random muted colors
    def random_muted_color():
        return "#{:02x}{:02x}{:02x}".format(
            random.randint(50, 200),
            random.randint(50, 200),
            random.randint(50, 200)
        )

    foreground_color = random_muted_color()
    background_color = "#FFFFFF"

    # Generate QR code with segno
    qr = segno.make(encrypted_reg_no, error='H')

    # Save the QR code with custom colors
    qr.save(
        f"{QR_CODE_FOLDER}/{filename}.png",
        scale=10,
        dark=foreground_color,
        light=background_color
    )

    # Open the QR code image
    img = Image.open(f"{QR_CODE_FOLDER}/{filename}.png").convert("RGB")

    # Add logo to the QR code (optional)
    try:
        logo = Image.open(LOGO_PATH).convert("RGBA")
        qr_size = img.size[0]

        # Resize the logo proportionally
        logo_size = int(qr_size / 4)
        logo.thumbnail((logo_size, logo_size), Image.Resampling.LANCZOS)

        # Center the logo
        logo_position = ((qr_size - logo.size[0]) // 2, (qr_size - logo.size[1]) // 2)
        img.paste(logo, logo_position, mask=logo)
    except FileNotFoundError:
        print("Logo file not found. QR code will be generated without a logo.")

    # Add the student's name below the QR code
    draw = ImageDraw.Draw(img)
    text = name
    try:
        font = ImageFont.truetype("arial.ttf", 18)
    except IOError:
        font = ImageFont.load_default()

    # Position the text at the bottom
    bbox = draw.textbbox((0, 0), text, font=font)
    text_position_x = (img.width - (bbox[2] - bbox[0])) // 2
    text_position_y = img.height - (bbox[3] - bbox[1]) - 20
    draw.text((text_position_x, text_position_y), text, fill="black", font=font)

    # Save the final image
    img.save(f"{QR_CODE_FOLDER}/{filename}.png")
    print(f"QR Code saved for {name} with Foreground={foreground_color}, Background={background_color}.")

def main():
    # Ensure the output folder exists
    os.makedirs(QR_CODE_FOLDER, exist_ok=True)

    # Step 1: Fetch student data from Google Sheets
    students = get_student_data()
    if not students:
        print("No student data found.")
        return

    # Step 2: Generate QR codes for each student
    for i, student in enumerate(students):
        try:
            # Generate a unique filename for each student
            filename = f"student_{i+1}"
            generate_qr_code_with_shapes(student, filename)
        except Exception as e:
            print(f"Error generating QR code for {student}: {e}")

if __name__ == "__main__":
    main()
