
# InsightHub

**InsightHub** is a Django-based platform that allows users to upload CSV files and create interactive, shareable dashboards using drag-and-drop charts powered by Chart.js and GridStack.js. 

Users can optionally generate QR codes for the public sharing of their dashboards.

Check the project structure decleration form for superuser details.

## 🌐 If accessing via UQ Zones

1. Run the development server
`python3.12 manage.py runserver 0.0.0.0:8000`

2. Access via the following URLs
   - Frontend: `https://infs3202-c6866c5d.uqcloud.net/insighthub/`
   - Admin: `https://infs3202-c6866c5d.uqcloud.net/insighthub/admin`

## ⚙️ If installing from the submitted ZIP

1. Navigate to the directory which contains `manage.py`: `cd insighthub`
2. Create and activate a virtual environment:
   - `python -m venv venv`
   - `source venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Apply migrations:
   - `python manage.py makemigrations`
   - `python manage.py migrate`
5. Run the server: `python3.12 manage.py runserver 0.0.0.0:8000`
6. Access the app:
   - Frontend: `https://infs3202-c6866c5d.uqcloud.net/insighthub/`
   - Admin: `https://infs3202-c6866c5d.uqcloud.net/insighthub/admin`

---

## ✅ Usage Summary

1. **Create an account**
2. **Upload a CSV file**
3. **Create a dashboard**
4. **Drag and drop charts**
5. **Save layout**
6. **Optionally share via QR code**

---

## 🧪 Features

### 🧾 CSV Upload and Management

- Upload `.csv` files under "My Files"
- Rename and delete uploaded files
- Automatically parses headers and values
- Supports numeric and text data for visualizations

### 📊 Dashboard Builder

- Drag-and-drop widgets using GridStack.js
- Choose from Bar, Line, and Pie charts
- Configure charts with custom X and Y axes
- Save dashboard layout to the backend
- Generate QR codes to publicly share dashboards

### 🤖 Chat UI Assistant

- Access via “AI Assistant” in navbar
- Get tips on dashboard design
- Powered by OpenAI GPT model

---

## 🔐 Authentication

- Supports account creation via email/password or Google
- Social auth is handled by `django-allauth`

---

## 🔑 Admin Panel Access

1. Visit: `http://127.0.0.1:8000/admin/` (or `/insighthub/admin/` on UQCloud)
2. Login with the credentials of a Django superuser
3. Manage:
   - Users and UserProfiles
   - Uploaded CSVs and associated values
   - Dashboards and QR codes

---

## 🧱 Tech Stack

- Django 5.2.1
- MySQL (via `mysqlclient`)
- Chart.js + GridStack.js (frontend)
- Bootstrap 5.3.3
- `django-allauth` for login/signup
- OpenAI integration for the chatbot

---

## 📁 Folder Structure

- `dashboardapp/` – All models, views, and forms
- `templates/` – HTML templates (Bootstrap-based)
- `static/` – Images and static files
- `insighthub/` - Urls and settings for the project

---

## 🤖 How generative AI has been utilised in my project
- I utilised generative AI for much of the work I completed in this asssignment, not always to write the code directly, sometimes to act as google would if you needed to refresh on syntax or a concept
- Turning my db design into Django models
- Registering my models in admin.py
- Updating forms.py from the tutorial version
- Creating a superuser to access Django admin panel
- Completing views.py based on tutorial work
- Debugging urls.py after it didn't work
- Creating base html files to get the project off the ground
- Setting up dashboard_detail so that it has save states and charts can be created with data from csv files
- Handling csv uploading and parsing
- Transferring work I did in mockups to a functioning UI in the project
- Updating the allauth login/logout/signup pages to be styled according to the rest of the project
- Implementation of the ChatUI feature
- Writing up some function comments
- Assistance with finishing the readme.txt file