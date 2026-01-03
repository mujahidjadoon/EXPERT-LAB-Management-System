# EXPERT-LAB-Management-System
Expert Lab Management System (v11.0)
Expert Lab Pro is a comprehensive solution for medical laboratories that specialize in routine and weekly patient monitoring. It eliminates manual paperwork by automating patient registration, medical data entry, and professional report generation.

🚀 Key Professional Features
Smart Patient Directory: Uses a centralized SQLite3 database. Register a patient once and search by Name or ID for all future visits.

Dynamic Medical Entry: Supports unlimited blood test types (e.g., Sugar, BP, HIV, Cholesterol, Uric Acid). Enter multiple results in one go.

Comparative Recovery Tracking: Automatically stores historical data. Every new report includes a table of previous results, making it easy to see if a patient’s health is improving.

One-Click Professional PDFs: Generates official medical reports in PDF format. Each patient has a dedicated folder where their entire yearly history is stored.

Field Dispatch & Maps: Includes a dedicated "Rider" button. By saving Google Maps links during registration, lab staff can instantly provide navigation to home-collection riders.

Subscription & Alert Management: Features a toggle to turn notifications ON/OFF, allowing labs to respect patient privacy while maintaining a weekly reminder list for active cases.

🛠️ Technical Stack
Language: Python 3.x

UI Framework: CustomTkinter (Modern High-Performance GUI)

PDF Engine: ReportLab

Database: SQLite3

Packaging Tool: PyInstaller / Auto-Py-To-Exe

💻 Local Installation & Setup
To run this project locally, follow these steps:

1. Prerequisites
Ensure you have Python installed. You will also need the following libraries:


pip install customtkinter reportlab pillow darkdetect
2. Running the Application
Clone this repository:


git clone https://github.com/YourUsername/Expert-Lab-System.git
Navigate to the project folder and run:


python main.py
3. Standalone EXE Version
For non-technical environments, we have converted the script into a standalone .exe using the following command: pyinstaller --noconfirm --onefile --windowed --collect-all customtkinter main.py

📂 Project Structure
main.py: The core application logic.

requirements.txt: List of dependencies.

Patient_Data_Vault/: Automatically generated folder to store patient PDF files.

lab_enterprise_v10.db: The local database file storing all encrypted patient data.





<img width="1416" height="880" alt="88888888" src="https://github.com/user-attachments/assets/00c92755-4504-471d-8126-dc3c97d55212" />

