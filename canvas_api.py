import requests
from typing import Dict, Any, List, Optional
import json

class CanvasAPI:
    def __init__(self, base_url: str, access_token: str):
        """
        Initialize the CanvasAPI client.

        :param base_url: Base URL for your Canvas instance (e.g., https://canvas.instructure.com/api/v1/)
        :param access_token: Personal access token for authenticating API requests.
        """
        self.base_url = base_url.rstrip("/") + "/api/v1"
        self.access_token = access_token

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a GET request to the Canvas API.

        :param endpoint: API endpoint to query (e.g., 'courses').
        :param params: Query parameters to include in the request.
        :return: Parsed JSON response from the API.
        """
        url = f"{self.base_url}/{endpoint}"
        if params is None:
            params = {}
        params['access_token'] = self.access_token
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def list_courses(self, enrollment_type: Optional[str] = None, enrollment_state: Optional[str] = None, 
                     exclude_blueprint_courses: Optional[bool] = None, include: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        List all courses for the authenticated user with optional filters, including all pages.

        :param enrollment_type: Filter courses by enrollment type (e.g., 'teacher', 'student').
        :param enrollment_state: Filter courses by enrollment state (e.g., 'active', 'completed').
        :param exclude_blueprint_courses: Exclude blueprint courses if set to True.
        :param include: Additional information to include with each course (e.g., ['syllabus_body', 'teachers']).
        :return: List of courses as dictionaries.
        """
        params = {}
        if enrollment_type:
            params['enrollment_type'] = enrollment_type
        if enrollment_state:
            params['enrollment_state'] = enrollment_state
        if exclude_blueprint_courses is not None:
            params['exclude_blueprint_courses'] = str(exclude_blueprint_courses).lower()
        if include:
            params['include[]'] = include

        all_courses = []
        url = f"{self.base_url}/courses"
        while url:
            response = requests.get(url, params={**params, "access_token": self.access_token})
            response.raise_for_status()
            data = response.json()
            all_courses.extend(data)

            # Get the next page URL from the 'Link' header
            links = response.headers.get("Link", "")
            next_link = None
            for link in links.split(","):
                if 'rel="next"' in link:
                    next_link = link[link.find("<") + 1:link.find(">")]
                    break
            url = next_link  # Continue to the next page or stop if None

        return all_courses

    def filter_courses_by_code(self, courses: List[Dict[str, Any]], course_codes: List[str]) -> List[Dict[str, Any]]:
        """
        Filter courses based on a manually provided list of course codes.

        :param courses: List of courses returned by the API.
        :param course_codes: List of course codes for the courses currently being taken.
        :return: Filtered list of courses with relevant information.
        """
        filtered_courses = []
        for course in courses:
            if 'course_code' in course and course['course_code'] in course_codes:
                relevant_info = {
                    'id': course['id'],
                    'name': course['name'],
                    'start_at': course['start_at'],
                    'end_at': course['end_at'],
                    'teachers': [{
                        'id': teacher['id'],
                        'display_name': teacher['display_name'],
                        'avatar_image_url': teacher['avatar_image_url']
                    } for teacher in course.get('teachers', [])],
                    'syllabus_body': course.get('syllabus_body', ''),
                    'course_code': course['course_code'],
                    'enrollment_term_id': course['enrollment_term_id'],
                    'time_zone': course['time_zone'],
                    'calendar': course.get('calendar', {}).get('ics', None)
                }
                filtered_courses.append(relevant_info)
        return filtered_courses

    def get_course_todo_items(self, course_id: int) -> List[Dict[str, Any]]:
        """
        Get the current user’s course-specific to-do items.

        :param course_id: The ID of the course.
        :return: List of to-do items as dictionaries.
        """
        endpoint = f"courses/{course_id}/todo"
        return self.get(endpoint)

    def list_course_assignments(self, course_id: int, include: Optional[List[str]] = None, search_term: Optional[str] = None, 
                                override_assignment_dates: Optional[bool] = True, bucket: Optional[str] = None, 
                                order_by: Optional[str] = "position") -> List[Dict[str, Any]]:
        """
        List all assignments for a given course, including handling pagination.

        :param course_id: The ID of the course.
        :param include: Additional information to include with each assignment (e.g., ['submission', 'overrides']).
        :param search_term: Filter assignments by a partial title match.
        :param override_assignment_dates: Apply assignment overrides (default is True).
        :param bucket: Filter assignments by due date or submission status (e.g., 'past', 'upcoming').
        :param order_by: Order the assignments (default is 'position').
        :return: List of assignments as dictionaries.
        """
        params = {}
        if include:
            params['include[]'] = include
        if search_term:
            params['search_term'] = search_term
        if override_assignment_dates is not None:
            params['override_assignment_dates'] = str(override_assignment_dates).lower()
        if bucket:
            params['bucket'] = bucket
        if order_by:
            params['order_by'] = order_by

        all_assignments = []
        url = f"{self.base_url}/courses/{course_id}/assignments"
        while url:
            response = requests.get(url, params={**params, "access_token": self.access_token})
            response.raise_for_status()
            data = response.json()
            all_assignments.extend(data)

            # Get the next page URL from the 'Link' header
            links = response.headers.get("Link", "")
            next_link = None
            for link in links.split(","):
                if 'rel="next"' in link:
                    next_link = link[link.find("<") + 1:link.find(">")]
                    break
            url = next_link  # Continue to the next page or stop if None

        return all_assignments

    def save_courses_to_json(self, courses: List[Dict[str, Any]], filename: str = "current_courses.json"):
        """
        Save filtered courses to a JSON file.

        :param courses: Filtered list of courses to save.
        :param filename: Name of the JSON file.
        """
        with open(filename, 'w') as f:
            json.dump(courses, f, indent=4)

# Example usage:
# canvas = CanvasAPI(base_url="https://canvas.instructure.com", access_token="your-access-token")
# all_courses = canvas.list_courses(include=["syllabus_body", "teachers"])
# current_course_codes = ["SPN1131", "MAT2023"]  # Replace with your actual course codes
# current_courses = canvas.filter_courses_by_code(all_courses, current_course_codes)
# canvas.save_courses_to_json(current_courses)
# assignments = canvas.list_course_assignments(course_id=523306, include=["submission", "all_dates"], bucket="upcoming")
# print(assignments)
