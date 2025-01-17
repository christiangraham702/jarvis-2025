from canvas_api import CanvasAPI
import os
import json
import pprint

print(os.environ.get("CANVAS_API_KEY"))

canvas = CanvasAPI(base_url="https://ufl.instructure.com", access_token=os.environ.get("CANVAS_API_KEY"))

# all_courses = canvas.list_courses(include=["syllabus_body", "teachers"])
# current_course_codes = ["SPN1131", "GEO3315", "GEO3502", "GIS4123C/GIS6106C", "GEO4930"]  # Replace with your actual course codes
# current_courses = canvas.filter_courses_by_code(all_courses, current_course_codes)
# canvas.save_courses_to_json(current_courses)

# todo_items = canvas.get_course_todo_items(course_id=523306)
# pprint.pprint(todo_items)
course_id = 523306
assignments = canvas.list_course_assignments(course_id=course_id, include=["submission", "all_dates"], bucket="future")
# Save assignments to JSON file
with open(f'assignments_{course_id}.json', 'w') as f:
    json.dump(assignments, f, indent=4)
print(f"Assignments data has been saved to 'assignments_{course_id}.json'")

