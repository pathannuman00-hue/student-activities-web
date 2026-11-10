# 🎓 Student Activities Management System

A web-based application built using **Python, Flask, and SQLite** to manage student activities, student records, participation, and activity reports in one centralized platform.

The project aims to simplify the management of college extracurricular activities through an organized and user-friendly web interface.

## 🚀 Project Overview

Managing student activities manually can be time-consuming and difficult to organize.

The **Student Activities Management System** provides a centralized platform where student information, activities, and participation records can be managed efficiently.

It offers dedicated sections for students, activities, participation tracking, and reports, making student activity management more organized.

## ✨ Key Features

- 📊 **Dashboard** – Provides an overview of the student activities system.
- 👨‍🎓 **Student Management** – Manage student records and information.
- 📅 **Activity Management** – Organize and manage different student activities.
- 📝 **Participation Tracking** – Maintain student participation records.
- 📈 **Reports** – Access organized reports related to student activities.
- 🗄️ **SQLite Database** – Store application data using a lightweight database.
- 🌐 **Web-Based Interface** – Access the system through a browser.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Flask | Web framework |
| SQLite | Database management |
| HTML5 | Web page structure |
| CSS3 | Styling and layout |
| Jinja2 | Dynamic HTML templates |
| CSV | Data handling |

## 📂 Project Structure

```text
Student-Activities-web/
│
├── app.py
├── student_activity.py
├── .gitignore
│
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── students.html
│   ├── activities.html
│   ├── participation.html
│   └── reports.html
│
└── README.md
```

## ⚙️ Installation & Setup

Follow these steps to run the project locally.

**1. Clone the repository**

```bash
git clone https://github.com/pathannuman00-hue/student-activities-web.git
```

**2. Navigate to the project directory**

```bash
cd student-activities-web
```

**3. Create a virtual environment**

```bash
python -m venv venv
```

**4. Activate the virtual environment**

For Windows:

```bash
venv\Scripts\activate
```

**5. Install Flask**

```bash
pip install Flask
```

**6. Run the application**

```bash
python app.py
```

**7. Open in your browser**

Visit:

```text
http://127.0.0.1:5000/
```

## 🔒 Database & Security

- SQLite is used for local data storage.
- Database files (`.db`, `.sqlite`, `.sqlite3`) are excluded from Git tracking through `.gitignore`.
- Environment variables and local Python environment files are excluded from version control.

## 🎯 Learning Outcomes

Through this project, I gained practical experience in:

- Python backend development.
- Building web applications using Flask.
- Working with SQLite databases.
- Creating dynamic web pages using HTML and Jinja2.
- Organizing application functionality into different modules.
- Managing project versions using Git and GitHub.

## 🔮 Future Improvements

- User authentication and role-based access.
- Advanced analytics and activity statistics.
- Improved reporting and data visualization.
- Enhanced user interface and responsiveness.
- Exportable student activity reports.

## 👨‍💻 Author

**Numan Pathan**

Computer Engineering Student | Python Developer | Software Development & Data Analytics

🔗 **GitHub:** [pathannuman00-hue](https://github.com/pathannuman00-hue)

---

⭐ If you find this project interesting, feel free to explore the repository and share your feedback!

**Built with Python, Flask, and a passion for learning.**
