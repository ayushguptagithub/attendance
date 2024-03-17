import cv2
from pyzbar.pyzbar import decode

def scan_qr_code():
    # Open camera
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Unable to access the camera.")
        return

    qr_code_detected = False

    while not qr_code_detected:
        # Read frame from camera
        ret, frame = cap.read()

        if not ret:
            print("Error: Unable to capture frame.")
            break

        # Decode QR codes
        decoded_objects = decode(frame)

        # Display the frame
        cv2.imshow('QR Code Scanner', frame)

        # Check for QR codes in the frame
        if decoded_objects:
            for obj in decoded_objects:
                qr_data = obj.data.decode('utf-8')
                print('Scanned QR Code:', qr_data)
                qr_code_detected = True  # Set flag to True
                break  # Exit the loop after detecting a QR code

        # Break loop if 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the camera and close OpenCV windows
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    scan_qr_code()
