# from canvas_api import CanvasAPI
# import os
# import json
# import pprint

# print(os.environ.get("CANVAS_API_KEY"))

# canvas = CanvasAPI(base_url="https://ufl.instructure.com", access_token=os.environ.get("CANVAS_API_KEY"))

# # all_courses = canvas.list_courses(include=["syllabus_body", "teachers"])
# # current_course_codes = ["SPN1131", "GEO3315", "GEO3502", "GIS4123C/GIS6106C", "GEO4930"]  # Replace with your actual course codes
# # current_courses = canvas.filter_courses_by_code(all_courses, current_course_codes)
# # canvas.save_courses_to_json(current_courses)

# # todo_items = canvas.get_course_todo_items(course_id=523306)
# # pprint.pprint(todo_items)
# course_id = 523306
# assignments = canvas.list_course_assignments(course_id=course_id, include=["submission", "all_dates"], bucket="future")
# # Save assignments to JSON file
# processed_assignments = canvas.process_assignments(assignments)
# pprint.pprint(processed_assignments)

import psycopg2

DATABASE_URL = "postgres://ue913nvfed2if7:p96f9968d072827b400b776040d9b0f637f35de0d52522b5905712ba36966babc@cbec45869p4jbu.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/dbjbg1t9tknd1s"

try:
    conn = psycopg2.connect(DATABASE_URL)
    print("Connected to the database!")
    conn.close()
except Exception as e:
    print(f"Error: {e}")

