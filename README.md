<h1 align="center">Student Registration System</h1>

<p align="center"><b>University enrolment made simple: programmes, courses, semesters and student registration with role-based access.</b></p>

<p align="center">![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white) ![Django](https://img.shields.io/badge/Django-092E20?logo=django&logoColor=white) ![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite&logoColor=white)</p>

## Overview

Django university registration system: programmes, courses and semesters, student enrolment, role-based access with a custom user model, and admin/student dashboards.

## Features

- Custom user model with role-based access decorators (admin vs student)
- Academics: programmes, courses and semesters
- Enrollment: students register for courses and view "My courses"
- Separate admin and student dashboards
- Reporting app for enrolment summaries

## Tech stack

Python · Django · SQLite

## Getting started

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install django
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver      # http://127.0.0.1:8000
```

## Project structure

`config/` settings · `apps/accounts`, `apps/academics`, `apps/enrollment`, `apps/reporting` · `templates/`

---

<p align="center">Built by <a href="https://github.com/allan818181"><b>Allan Muganyizi Deus</b></a> · Full-Stack &amp; DevOps Engineer · Dar es Salaam, Tanzania<br/>
<a href="https://www.linkedin.com/in/allan-deus-4b888631a">LinkedIn</a> · <a href="mailto:allandeus014@gmail.com">Email</a></p>
