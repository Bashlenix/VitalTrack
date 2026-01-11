# Electronic Health Record (EHR) Information System
## Project Documentation

---

## 1. Introduction

An Electronic Health Record (EHR) system is a digital version of a patient's paper medical chart. EHRs are real-time, patient-centered records that make information available instantly and securely to authorized users. These systems contain a patient's medical history, diagnoses, medications, treatment plans, immunization dates, allergies, radiology images, and laboratory test results.

EHR systems have become essential in modern healthcare because they improve the quality and safety of patient care, increase efficiency, and reduce healthcare costs. They allow healthcare providers to access patient information quickly, share data securely with other providers, and make more informed decisions about patient care. EHRs also help reduce medical errors by providing accurate, up-to-date information about patients at the point of care.

The history of EHRs dates back to the 1960s when hospitals began using computers to store patient data. However, it wasn't until the 2000s that EHR adoption became widespread, driven by government incentives and technological advances. Today, EHR systems are standard in most healthcare facilities worldwide.

I developed this EHR information system to practice building web-based healthcare information systems. Before starting development, I researched existing EHR systems by searching online to see what features they typically include and how they are structured. This research helped me understand the core functionality needed for managing patient records, appointments, lab results, and medical imaging.

The system I built is designed for doctors to manage their patients' health records digitally. It allows doctors to register, log in, create patient profiles, schedule appointments, record lab results, upload radiology images, and maintain medical history including allergies. This project helped me learn about web development, database design, and how to build secure systems that handle sensitive medical information.

---

## 2. Website Design and Technical Architecture

### 2.1 Design Process

Before implementing the system, I planned the overall structure and user interface. I thought about what pages would be needed and how users would navigate through the system. The design follows a simple, clean layout with a navigation bar at the top that provides access to all major sections of the system.

The user interface uses a modern design with a purple gradient navigation bar that includes the system logo "VT" (VitalTrack) and links to the main modules: Dashboard, Patients, Appointments, Lab Results, Radiology Imaging, and About Us. The navigation bar also displays the logged-in doctor's name and specialty, with a dropdown menu for profile settings and logout.

### 2.2 Frontend Structure

The frontend of the system is built using HTML, CSS, and Bootstrap framework. All pages extend from a base template (`base.html`) that provides the common navigation structure and styling. This approach ensures consistency across all pages and makes maintenance easier.

**Technologies Used:**
- **HTML5** - For page structure
- **CSS3** - For custom styling and layout
- **Bootstrap 4.6.2** - For responsive design components and grid system
- **Bootstrap Icons 1.11.0** - For icons throughout the interface
- **Font Awesome 5.15.4** - Additional icons
- **Google Fonts** - For custom typography (Kavoon, Mogra fonts)

The CSS includes custom styling for the navigation bar, cards, buttons, forms, and flash messages. The design uses a color scheme with purple gradients for primary elements, making the interface visually appealing while maintaining professionalism suitable for a healthcare application.

### 2.3 Backend Structure

The backend is built using Python and the Flask web framework. Flask is a lightweight and flexible framework that allows for rapid development of web applications. The application follows a modular structure with routes organized into separate blueprint files.

**Technologies Used:**
- **Python 3** - Programming language
- **Flask 2.3.3** - Web framework
- **Flask-SQLAlchemy 3.0.5** - Database ORM (Object-Relational Mapping)
- **Flask-Mail 0.9.1** - Email functionality
- **Werkzeug 2.3.7** - Password hashing and security utilities
- **itsdangerous 2.1.2** - Token generation for email confirmation and password reset
- **python-dotenv 1.0.0** - Environment variable management
- **mysql-connector-python 8.1.0** - MySQL database connector
- **Pillow 12.0.0** - Image processing for radiology uploads

The application uses Flask's application factory pattern, where the app is created in `app.py` using a `create_app()` function. This makes the application more flexible and easier to test. All routes are organized into separate blueprint modules:

- `auth.py` - Authentication routes (login, registration, password reset)
- `main.py` - Main navigation and dashboard
- `patients.py` - Patient management
- `appointments.py` - Appointment scheduling and management
- `lab_results.py` - Laboratory results management
- `radiology.py` - Radiology imaging management
- `medical_history.py` - Medical history and allergies
- `doctor.py` - Doctor profile management

Initially, I had all routes in a single file, but as the project grew, I split them into separate blueprints to keep the code organized and maintainable.

### 2.4 Database Structure

The system uses MySQL as the database management system. The database schema is defined using SQLAlchemy models in the `models.py` file. The database includes the following main tables:

**Core Tables:**
- **Doctor** - Stores doctor information (name, username, email, password, specialties)
- **Specialty** - Stores medical specialties
- **Patient** - Stores patient basic information (name, email, phone, age, gender, date of birth)
- **DemographicInfo** - Stores patient demographic details (address, emergency contact)
- **SocialHistory** - Stores patient social history (smoking, alcohol use, drug use, occupation)

**Medical Records Tables:**
- **MedicalHistory** - Links patients to allergies/conditions with descriptions and dates
- **Allergy** - Stores allergy/condition information
- **LaboratoryResult** - Stores lab test results (test name, result, unit, reference range, status)
- **RadiologyImaging** - Stores radiology imaging records with uploaded image files
- **Appointment** - Stores appointment information (patient, doctor, date, type, status, notes)
- **Prescription** - Stores prescription information (medication, dosage, frequency, dates)

The database uses relationships to connect these tables:
- One doctor can have many patients (one-to-many)
- One patient can have many appointments, lab results, radiology images, and medical history entries (one-to-many)
- Doctors and specialties have a many-to-many relationship in the database model (doctors can have multiple specialties), though the current implementation only supports one specialty per doctor
- Patients and allergies are linked through the MedicalHistory table

### 2.5 Data Flow

The data flow in the system follows a standard web application pattern:

1. **User Request**: The user interacts with the frontend (HTML pages) by clicking links or submitting forms.

2. **Route Handling**: Flask routes receive the HTTP requests and call the appropriate handler functions.

3. **Authentication Check**: Protected routes use the `@login_required` decorator to verify the user is logged in. This decorator checks the session for a `logged_in` flag.

4. **Database Operations**: The route handlers use SQLAlchemy to query or modify the database. For example, when viewing patients, the system queries the Patient table filtered by the logged-in doctor's ID.

5. **Data Processing**: The route handlers process the data, perform validations, and prepare it for display.

6. **Template Rendering**: Flask's Jinja2 templating engine renders HTML templates with the data, creating the final HTML page.

7. **Response**: The rendered HTML is sent back to the user's browser.

For example, when a doctor adds a new patient:
- The form data is submitted via POST request
- The route handler validates the input (checks required fields, validates email format, etc.)
- A new Patient object is created with SQLAlchemy
- The patient is linked to the logged-in doctor
- The data is saved to the database
- A success message is flashed, and the user is redirected to the patients list page

### 2.6 Security Features

The system includes several security features:

- **Password Hashing**: Passwords are hashed using Werkzeug's `generate_password_hash()` function before storing in the database. Initially, I stored passwords in plain text, but later I implemented proper password hashing for security.

- **Session Management**: User authentication is managed through Flask sessions. When a user logs in, their doctor ID and name are stored in the session.

- **Email Confirmation**: New doctor registrations require email confirmation before the account can be used. This prevents unauthorized account creation.

- **Password Reset**: The system includes a forgot password feature that sends a secure token via email to reset passwords.

- **Access Control**: Each doctor can only access their own patients' records. All queries filter by the logged-in doctor's ID to ensure data isolation.

- **File Upload Security**: Radiology image uploads are validated for file type and size. Files are stored in organized folders by patient ID.

- **Environment Variables**: Sensitive configuration data (database credentials, secret keys, email settings) are stored in a `.env` file rather than in the code. Initially, I had some configuration in the `config.py` file, but I later moved sensitive data to environment variables for better security.

> **NOTE:** For security reasons,the environment file (.env), is not committed to the repository. Instead, an example configuration file (.env.example) is provided."

---

## 3. EHR Information System

This section describes how to use the EHR system, including step-by-step instructions for each major function. The system is designed to be intuitive, but this guide will help users understand all available features.

### 3.1 Registration

To use the system, doctors must first create an account. Figure 1 shows the registration page where new doctors can sign up.

![Figure 1 - registration page.](/docs/images/01_registration_page.png "Figure 1 - registration page.")

The registration form requires the following information:
- First Name (optional)
- Last Name (required)
- Username (required, must be unique, 3-20 characters)
- Email (required, must be valid format and unique)
- Password (required, must meet strength requirements: at least 8 characters, including uppercase, lowercase, digit, and special character)
- Phone Number (optional)
- Specialty (optional, currently limited to one specialty per doctor, though the database model supports multiple)

When a doctor submits the registration form, the system validates all inputs. If the username or email already exists, an error message is displayed. The password is checked against strength requirements, and if it doesn't meet the criteria, specific error messages guide the user.

After successful registration, the system hashes the password using Werkzeug's password hashing function and stores the doctor's information in the database. An email confirmation link is sent to the provided email address. The doctor must click this link to confirm their email before they can log in.

Figure 2 shows the registration success page, which informs the user that a confirmation email has been sent.

![Figure 2 - registration success page.](/docs/images/02_registration_success_page.png "Figure 1 - registration success page.")

### 3.2 Login

Figure 3 shows the login page. Doctors can log in using either their username or email address along with their password.

![Figure 3 - login page.](/docs/images/03_login_page.png "Figure 3 - login page.")

The login process works as follows:
1. The user enters their username/email and password
2. The system looks up the doctor by username or email
3. The entered password is compared with the hashed password stored in the database
4. If the email is not confirmed, the user is informed and cannot log in
5. If credentials are correct and email is confirmed, the user is logged in and redirected to the dashboard

The system uses Flask sessions to maintain the logged-in state. Once logged in, the session stores the doctor's ID, name, specialty (currently the first specialty if multiple exist), and a `logged_in` flag.

### 3.3 Dashboard

Figure 4 shows the main dashboard, which is the central hub of the EHR system. After logging in, doctors are automatically redirected here.

![Figure 4 - main dashboard.](/docs/images/04_main_dashboard.png "Figure 4 - main dashboard.")

The dashboard displays:
- **Recent Lab Results**: The 10 most recent laboratory test results for the doctor's patients, showing patient name, test name, result, and date
- **Recent Appointments**: The 10 most recent appointments, showing patient name, appointment type, date, and status
- **Quick Navigation**: Cards with links to add new patients, schedule appointments, add lab results, and add radiology imaging

The dashboard provides a quick overview of recent activity and easy access to common tasks. This helps doctors quickly see what's happening with their patients and perform common operations without navigating through multiple pages.

### 3.4 Patient Management

#### 3.4.1 Viewing All Patients

Figure 5 shows the patients list page, which displays all patients belonging to the logged-in doctor in a table format.

![Figure 5 - patients list page.](/docs/images/05_patients_list_page.png "Figure 5 - patients list page.")

The page shows:
- Patient basic information (name, email, phone, age, gender)
- Statistics about the patient's records (number of appointments, lab results, radiology images, medical history entries)
- Recent medical history entries with allergy information
- Statistics panel showing total patients, gender distribution, age group distribution, and number of patients with medical history

Each patient row includes action buttons to view details, edit, or delete the patient. The page also has a button to add a new patient.

#### 3.4.2 Adding a New Patient

![Figure 6 - add patient form.](/docs/images/06_add_patient_form.png "Figure 6 - add patient form.")

Figure 6 shows the add patient form. To add a new patient, doctors must fill in:
- First Name (required)
- Last Name (required)
- Email (optional)
- Phone Number (optional)
- Age (optional)
- Gender (required: male, female, or other)
- Date of Birth (required)

The form validates that required fields are filled and that the date of birth is valid. When submitted, the system creates a new patient record linked to the logged-in doctor. The patient is immediately available in the system for appointments, lab results, and other records.

#### 3.4.3 Viewing Patient Details

![Figure 7 - detailed patient view page.](/docs/images/07_detailed_patient_view_page.png "Figure 7 - detailed patient view page.")

Figure 7 shows the detailed patient view page. This page displays comprehensive information about a single patient:

- **Basic Information**: Name, email, phone, age, gender, date of birth
- **Demographic Information**: Address, emergency contact (if available)
- **Social History**: Smoking status, alcohol use, drug use, occupation (if available)
- **Recent Appointments**: Last 5 appointments with type, date, and status
- **Recent Lab Results**: Last 5 laboratory test results with test name, result, and date
- **Recent Radiology Imaging**: Last 5 radiology images with name and date
- **Recent Medical History**: Last 5 medical history entries showing allergies/conditions and descriptions

The page includes buttons to edit the patient, add medical history, schedule an appointment, add lab result, or add radiology imaging. This centralized view helps doctors quickly understand a patient's complete health picture.

#### 3.4.4 Editing Patient Information

Figure 8 shows the edit patient form, which is similar to the add patient form but pre-filled with existing patient data. Doctors can update any patient information and save the changes. The system validates the input and updates the database accordingly.

![Figure 8 - edit patient form.](/docs/images/08_edit_patient_form.png "Figure 8 - edit patient form.")

#### 3.4.5 Deleting Patients

Doctors can delete patients from the system. When a patient is deleted, all related records (appointments, lab results, radiology images, medical history) are also deleted to maintain database integrity. The system asks for confirmation before deletion.

### 3.5 Appointment Management

#### 3.5.1 Viewing Appointments

![Figure 9 - appointments list page.](/docs/images/09_appointments_list_page.png "Figure 9 - appointments list page.")

Figure 9 shows the appointments list page, which displays all appointments for the logged-in doctor. The page shows:
- Patient name
- Appointment type (consultation, follow-up, emergency, check-up, surgery, procedure)
- Date and time
- Status (scheduled, completed, cancelled, no_show)
- Notes

The page includes statistics showing total appointments, upcoming appointments, completed appointments, and breakdown by status. Each appointment can be viewed, edited, or deleted.

#### 3.5.2 Scheduling an Appointment

![Figure 10 - schedule appointment form.](/docs/images/10_schedule_appointment_form.png "Figure 10 - schedule appointment form.")

Figure 10 shows the schedule appointment form. To schedule a new appointment:
1. Select a patient from the dropdown (only shows patients belonging to the logged-in doctor)
2. Choose appointment date and time
3. Select appointment type (optional)
4. Add notes (optional)

The system validates that:
- A patient is selected
- Date and time are provided
- The doctor doesn't already have another appointment at the same date and time

After scheduling, the appointment appears in the appointments list and on the dashboard.

#### 3.5.3 Viewing and Editing Appointments

![Figure 11 - appointment detail view.](/docs/images/11_appointment_detail_view.png "Figure 11 - appointment detailview.")

Figure 11 shows the appointment detail view, which displays all information about a specific appointment. Doctors can edit appointments to change the date, time, type, status, or notes. The system prevents scheduling conflicts by checking for existing appointments at the same time.

### 3.6 Laboratory Results Management

#### 3.6.1 Viewing Lab Results

![Figure 12 - lab results list page](/docs/images/12_lab_results_list_page.png "Figure 12 - lab results list page.")

Figure 12 shows the lab results list page, displaying all laboratory test results for the doctor's patients. Each result shows:
- Patient name
- Test name
- Result value
- Unit (if applicable)
- Reference range (if applicable)
- Status (normal, abnormal, high, low, critical, pending)
- Date
- Notes

The page includes statistics showing total results, recent results (within 7 days), and a list of unique test types in the system.

#### 3.6.2 Adding Lab Results

![Figure 13 - add lab result form](/docs/images/13_add_lab_result_form.png "Figure 13 - add lab result form.")

Figure 13 shows the add lab result form. To add a new lab result:
1. Select a patient
2. Enter test name (e.g., "Blood Glucose", "Cholesterol")
3. Enter test date
4. Enter result value
5. Optionally enter unit (e.g., "mg/dL", "mmol/L")
6. Optionally enter reference range (e.g., "70-100 mg/dL")
7. Select status (normal, abnormal, high, low, critical, pending)
8. Add notes (optional)

The system validates required fields and ensures the patient belongs to the logged-in doctor. Lab results are immediately available in the patient's record and on the dashboard.

#### 3.6.3 Editing and Deleting Lab Results

Doctors can edit existing lab results to correct errors or update information. The edit form is similar to the add form but pre-filled with existing data. Lab results can also be deleted if entered incorrectly.

### 3.7 Radiology Imaging Management

#### 3.7.1 Viewing Radiology Images

![Figure 14 - radiology imaging list page](/docs/images/14_radiology_imaging_list_page.png "Figure 14 - radiology imaging list page.")

Figure 14 shows the radiology imaging list page, displaying all radiology imaging records for the doctor's patients. The page shows:
- Patient name
- Imaging name/type (e.g., "Chest X-Ray", "MRI Brain")
- Date
- Thumbnail preview of uploaded images (if available)

The page includes search functionality to filter by patient name or imaging name. This helps doctors quickly find specific imaging records when they have many patients.

#### 3.7.2 Adding Radiology Imaging

![Figure 15 - radiology imaging form](/docs/images/15_radiology_imaging_form.png "Figure 15 - radiology imaging form.")

Figure 15 shows the add radiology imaging form. To add a new imaging record:
1. Select a patient
2. Enter imaging name/type
3. Enter imaging date
4. Upload an image file (optional, supports PNG, JPG, JPEG, GIF, BMP, TIFF, DCM, DICOM formats)

The system validates the file type and size (maximum 10MB). Uploaded images are stored in organized folders by patient ID for easy management. The image filename is stored in the database, and the actual file is saved in the `static/uploads/radiology/patient_X/` directory.

#### 3.7.3 Editing and Deleting Radiology Records

Doctors can edit imaging records to update the name or date. When deleting a radiology record, the associated image file is also deleted from the server to save storage space.

### 3.8 Medical History Management

#### 3.8.1 Adding Medical History

![Figure 16 - add medical history form](/docs/images/16_add_medical_history_form.png "Figure 16 - add medical history form.")

Figure 16 shows the add medical history form. Medical history entries link patients to allergies or medical conditions. To add a medical history entry:
1. Select a patient
2. Enter or select an allergy/condition name (the system includes common allergies like Penicillin, Peanuts, Shellfish, etc., or doctors can enter new ones)
3. Enter a description of the condition, reaction, or relevant details
4. Enter the date when this condition was identified or recorded

The system automatically creates new allergy entries if the entered name doesn't exist. This allows flexibility while maintaining consistency in allergy naming.

#### 3.8.2 Viewing Medical History

Medical history entries appear in several places:
- On the patient detail page (last 5 entries)
- On the patients list page (recent entries for each patient)
- When viewing individual patient records

Each entry shows the allergy/condition name, description, and date, helping doctors quickly identify patient allergies and medical conditions.

#### 3.8.3 Editing and Deleting Medical History

Doctors can edit medical history entries to update descriptions or dates, or correct errors. Entries can also be deleted if they were added incorrectly.

### 3.9 Doctor Profile Management

![Figure 17 - doctor profile page](/docs/images/17_doctor_profile_page.png "Figure 17 - doctor profile page.")

Figure 17 shows the doctor profile page, where doctors can view and edit their own information. Doctors can update:
- First name
- Last name
- Email address
- Phone number

This allows doctors to keep their information updated. The system validates changes and ensures emails remains unique.

### 3.10 Password Management

#### 3.10.1 Forgot Password

![Figure 18 - forgot password form](/docs/images/18_forgot_password_form.png "Figure 18 - forgot password form.")

If a doctor forgets their password, they can use the "Forgot Password" feature. Figure 18 shows the forgot password form where doctors enter their email address. The system sends a password reset link to the registered email. This link contains a secure token that expires after 24 hours.

#### 3.10.2 Reset Password

![Figure 19 - password reset form](/docs/images/19_password_reset_form.png "Figure 19 - password reset form.")

Figure 19 shows the password reset form, accessible via the link sent in the email. Doctors enter a new password that must meet the same strength requirements as during registration. After resetting, doctors can log in with their new password.

### 3.11 About Us Page

![Figure 20 - About Us page](/docs/images/20_About_Us_page.png "Figure 20 - password reset form.")

![Figure 21 - About Us page](/docs/images/21_About_Us_page.png "Figure 21 - password reset form.")

Figure 20 and Figure 21 show the About Us page, which displays system-wide statistics:
- Total number of patients in the system
- Total number of appointments
- Total number of lab results
- Total number of radiology imaging records
- Total number of registered doctors

This page provides an overview of the system's usage and scale.

### 3.12 System Features Summary

The EHR system provides comprehensive functionality for managing patient health records:

1. **Patient Management**: Create, view, edit, and delete patient records with demographic and social history information.

2. **Appointment Scheduling**: Schedule, view, edit, and manage appointments with different types and statuses.

3. **Laboratory Results**: Record, view, and manage lab test results with status indicators and reference ranges.

4. **Radiology Imaging**: Upload, view, and manage radiology images with organized file storage.

5. **Medical History**: Track patient allergies and medical conditions with detailed descriptions and dates.

6. **Security**: Secure authentication, password hashing, email confirmation, and access control to ensure only authorized doctors can access patient data.

7. **User-Friendly Interface**: Clean, modern design with intuitive navigation and helpful statistics and summaries.

Each feature is designed to be useful in real healthcare scenarios. For example, the appointment system helps doctors manage their schedule and avoid double-booking. The lab results system helps track patient test results over time. The radiology imaging feature allows doctors to store and review medical images. The medical history feature helps prevent medical errors by tracking allergies and conditions.

---

## 4. Evaluation of the EHR Information System

To assess the usability of the EHR system, I conducted a usability evaluation using the System Usability Scale (SUS) methodology. SUS is a widely used, reliable tool for measuring the perceived usability of systems.

### 4.1 SUS Methodology

The System Usability Scale is a questionnaire consisting of 10 statements that users rate on a 5-point Likert scale from "Strongly Disagree" (1) to "Strongly Agree" (5). The statements alternate between positive and negative wording to reduce response bias.

The 10 SUS statements are:
1. I think that I would like to use this system frequently.
2. I found the system unnecessarily complex.
3. I thought the system was easy to use.
4. I think that I would need the support of a technical person to be able to use this system.
5. I found the various functions in this system were well integrated.
6. I thought there was too much inconsistency in this system.
7. I would imagine that most people would learn to use this system very quickly.
8. I found the system very cumbersome to use.
9. I felt very confident using the system.
10. I needed to learn a lot of things before I could get going with this system.

### 4.2 Evaluation Process

For this project evaluation, I asked one person (a fellow student) to use the system and complete the SUS questionnaire. While SUS is often used with multiple evaluators, I used a single evaluator to get a depper understanding of the evaluation methodology.

The evaluator was given access to the system and asked to:
1. Register a new doctor account
2. Log in to the system
3. Add a new patient
4. Schedule an appointment
5. Add a lab result
6. Add a radiology imaging record
7. Add medical history for a patient
8. View patient details
9. Complete the SUS questionnaire

The evaluator used the system for approximately 15-20 minutes to complete these tasks and then filled out the SUS questionnaire.

### 4.3 SUS Score Calculation

SUS scores are calculated using the specific formula below:

1. For odd-numbered items (1, 3, 5, 7, 9): Subtract 1 from the user score
2. For even-numbered items (2, 4, 6, 8, 10): Subtract the user score from 5
3. Sum all the adjusted scores
4. Multiply the sum by 2.5 to get the final SUS score (ranging from 0 to 100)

**Evaluator Responses:**

The evaluator provided the following responses:
- Statement 1: 4 (Strongly Agree)
- Statement 2: 2 (Disagree)
- Statement 3: 5 (Strongly Agree)
- Statement 4: 2 (Disagree)
- Statement 5: 4 (Agree)
- Statement 6: 2 (Disagree)
- Statement 7: 4 (Agree)
- Statement 8: 2 (Disagree)
- Statement 9: 4 (Agree)
- Statement 10: 2 (Disagree)

**Calculation:**
- Item 1 (odd): 4 - 1 = 3
- Item 2 (even): 5 - 2 = 3
- Item 3 (odd): 5 - 1 = 4
- Item 4 (even): 5 - 2 = 3
- Item 5 (odd): 4 - 1 = 3
- Item 6 (even): 5 - 2 = 3
- Item 7 (odd): 4 - 1 = 3
- Item 8 (even): 5 - 2 = 3
- Item 9 (odd): 4 - 1 = 3
- Item 10 (even): 5 - 2 = 3

Sum = 3 + 3 + 4 + 3 + 3 + 3 + 3 + 3 + 3 + 3 = 31
SUS Score = 31 × 2.5 = 77.5

### 4.4 SUS Score Interpretation

SUS scores range from 0 to 100, with higher scores indicating better usability. The average SUS score across all systems is approximately 68. Scores can be interpreted as follows:
- Above 80: Excellent usability
- 68-80: Good usability (above average)
- 50-68: OK usability (below average)
- Below 50: Poor usability

In the example calculation above, a score of 77.5 indicates good usability, above the 68 benchmark. This suggests the system is relatively easy to use and learn.

### 4.5 Evaluation Results Discussion

The SUS evaluation helps identify areas where the system performs well and areas that could be improved. Positive responses to statements like "I thought the system was easy to use" and "I would imagine that most people would learn to use this system very quickly" indicate good usability. Negative responses to statements like "I found the system unnecessarily complex" and "I found the system very cumbersome to use" would indicate areas needing improvement.

The evaluation process demonstrates understanding of usability testing methodology. While a single evaluator provides limited statistical significance, it still offers valuable insights into the system's usability and helps identify potential improvements.

---

## 5. Conclusion

This project involved developing a complete web-based Electronic Health Record (EHR) information system using HTML, CSS, and Python with the Flask framework. The system provides comprehensive functionality for doctors to manage patient records, including patient information, appointments, laboratory results, radiology imaging, and medical history.

Throughout the development process, I learned about web application architecture, database design, user authentication, file handling, and security best practices. The system evolved from initial simple implementations to a more robust solution with proper password hashing, email confirmation, organized code structure, and secure file handling.

The system successfully implements core EHR functionality:
- Secure doctor registration and authentication
- Comprehensive patient record management
- Appointment scheduling and tracking
- Laboratory results recording and viewing
- Radiology image upload and management
- Medical history tracking including allergies
- User-friendly interface with intuitive navigation

**Limitations and Future Improvements:**

While the system provides essential EHR functionality, there are several limitations and areas for potential improvement:

1. **Scalability**: The current system is designed for single-doctor use or small practices. For larger healthcare facilities, additional features like multi-doctor collaboration, patient transfer between doctors, and advanced search capabilities would be needed.

2. **Data Export**: The system doesn't currently support exporting patient data to standard formats (like HL7 or FHIR) that are commonly used in healthcare for data exchange.

3. **Reporting**: Advanced reporting features like generating patient summaries, appointment reports, or lab result trends over time would be valuable additions.

4. **Mobile Responsiveness**: While the system uses Bootstrap for responsive design, further optimization for mobile devices would improve usability for doctors accessing the system on tablets or smartphones.

5. **Backup and Recovery**: The system would benefit from automated backup functionality to protect patient data.

6. **Audit Trail**: For healthcare compliance, an audit trail logging all data access and modifications would be important.

7. **Advanced Security**: Additional security features like two-factor authentication, role-based access control, and encryption at rest would enhance security for sensitive medical data.

8. **Multiple Specialties Support**: The database model was initially designed to support a many-to-many relationship between doctors and specialties, allowing doctors to have multiple specialties. However, due to time constraints, the implementation was simplified to handle only one specialty per doctor. The registration form, profile editing, and display logic all treat doctors as having a single specialty, even though the database structure supports multiple. Implementing full multiple specialties support would require updating the registration form to allow selecting multiple specialties, modifying the profile edit page to manage specialty lists, and updating the display logic to show all specialties instead of just the first one.

This project provided me a valuable hands-on experience in full-stack web development and healthcare information systems. While it may not have all the features of commercial EHR systems, I made sure to have the core elements and functionality needed implemented for managing patient health records in a digital format.
