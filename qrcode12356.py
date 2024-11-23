import qrcode

# Google Form URL
url = "https://docs.google.com/forms/d/e/1FAIpQLScgtLNSCwe0PE5mvqLBqnHtIQmCfcJ7xOESIu2fAC61aOFsAw/viewform?usp=sf_link"

# Create a QR code instance
qr = qrcode.QRCode(
    version=1,  # Controls the size of the QR code (1 is the smallest)
    error_correction=qrcode.constants.ERROR_CORRECT_L,  # Error correction level
    box_size=10,  # Size of each box in the QR code
    border=4,  # Size of the border around the QR code
)

# Add the URL data to the QR code
qr.add_data(url)
qr.make(fit=True)

# Create an image of the QR code
img = qr.make_image(fill='black', back_color='white')

# Save the image as a PNG file
img.save("google_form_qr_code.png")

# Show the image (optional)
img.show()

print("QR code generated and saved as 'google_form_qr_code.png'")
