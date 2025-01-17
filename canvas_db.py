import psycopg2
from psycopg2 import sql
from typing import List, Dict
from canvas_api import CanvasAPI
import os

# Replace with your actual Heroku DATABASE_URL
DATABASE_URL = "postgres://ue913nvfed2if7:p96f9968d072827b400b776040d9b0f637f35de0d52522b5905712ba36966babc@cbec45869p4jbu.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/dbjbg1t9tknd1s"

# Canvas API setup
API_URL = "https://ufl.instructure.com"
API_KEY = os.environ.get("CANVAS_API_KEY")
canvas = CanvasAPI(base_url=API_URL, access_token=API_KEY)
current_course_codes = ["SPN1131", "GEO3315", "GEO3502", "GIS4123C/GIS6106C", "GEO4930"]

def initialize_database():
    connection = psycopg2.connect(DATABASE_URL)
    cursor = connection.cursor()

    # Create courses table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS courses (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        course_code TEXT UNIQUE NOT NULL,
        start_at TIMESTAMP,
        end_at TIMESTAMP,
        syllabus_body TEXT,
        time_zone TEXT
    );
    """)

    # Create assignments table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assignments (
        id SERIAL PRIMARY KEY,
        course_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        due_at TIMESTAMP,
        points_possible REAL,
        grading_type TEXT,
        html_url TEXT,
        submission_score REAL,
        submission_state TEXT,
        submitted_at TIMESTAMP,
        FOREIGN KEY (course_id) REFERENCES courses (id)
    );
    """)

    connection.commit()
    cursor.close()
    connection.close()
    print("Database initialized!")

def insert_courses(courses: List[Dict]):
    connection = psycopg2.connect(DATABASE_URL)
    cursor = connection.cursor()

    for course in courses:
        cursor.execute("""
        INSERT INTO courses (id, name, course_code, start_at, end_at, syllabus_body, time_zone)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (course_code) DO NOTHING
        """, (
            course['id'],
            course['name'],
            course['course_code'],
            course.get('start_at'),
            course.get('end_at'),
            course.get('syllabus_body', ''),
            course.get('time_zone', ''),
        ))

    connection.commit()
    cursor.close()
    connection.close()
    print("Courses inserted!")

def insert_assignments(assignments: List[Dict], course_id: int):
    connection = psycopg2.connect(DATABASE_URL)
    cursor = connection.cursor()

    for assignment in assignments:
        cursor.execute("""
        INSERT INTO assignments (id, course_id, name, description, due_at, points_possible, grading_type, html_url, submission_score, submission_state, submitted_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
        """, (
            assignment['id'],
            course_id,
            assignment['name'],
            assignment.get('description'),
            assignment.get('due_at'),
            assignment.get('points_possible'),
            assignment.get('grading_type'),
            assignment.get('html_url'),
            assignment.get('submission', {}).get('score'),
            assignment.get('submission', {}).get('workflow_state'),
            assignment.get('submission', {}).get('submitted_at')
        ))

    connection.commit()
    cursor.close()
    connection.close()
    print("Assignments inserted!")

def fetch_courses():
    connection = psycopg2.connect(DATABASE_URL)
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM courses;")
    courses = cursor.fetchall()

    connection.close()
    return courses

def fetch_assignments(course_id: int):
    connection = psycopg2.connect(DATABASE_URL)
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM assignments WHERE course_id = %s;", (course_id,))
    assignments = cursor.fetchall()

    connection.close()
    return assignments

def populate_database_from_canvas():
    # Fetch courses from Canvas API
    courses = canvas.list_courses()
    current_courses = canvas.filter_courses_by_code(courses, current_course_codes)
    insert_courses(current_courses)

    # Fetch assignments for each course
    for course in current_courses:
        course_id = course['id']
        assignments = canvas.list_course_assignments(course_id=course_id, include=["submission", "all_dates"], bucket="future")
        insert_assignments(assignments, course_id=course_id)

if __name__ == "__main__":
    initialize_database()
    populate_database_from_canvas()

    # Example usage
    print(fetch_courses())
    for course in fetch_courses():
        print(f"Assignments for course {course[1]}:")
        print(fetch_assignments(course_id=course[0]))
