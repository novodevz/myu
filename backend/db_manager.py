from app import Course, Grade, app, db

with app.app_context():
    # # Create a new course
    # new_course = Course(name="python")
    # # Add the course to the database
    # db.session.add(new_course)

    # # Create a new course
    # new_course = Course(name="sql")
    # # Add the course to the database
    # db.session.add(new_course)

    # # Create a new course
    # new_course = Course(name="js")
    # # Add the course to the database
    # db.session.add(new_course)
    # # Commit the changes
    # db.session.commit()

    # Let's assume the user and course have ids 1 and 1, respectively
    user_id = 3
    course_id_list = [1, 2, 3]
    grade_list = [63, 73, 93]

    for course_id, score in zip(course_id_list, grade_list):
        # Create a new grade
        new_grade = Grade(score=score, user_id=user_id, course_id=course_id)
        # Add the grade to the database
        db.session.add(new_grade)

    # Commit the changes after adding all grades
    db.session.commit()

    # # Get the course by ID
    # course_to_delete = Course.query.get(6)

    # if course_to_delete:
    #     # Delete the course
    #     db.session.delete(course_to_delete)
    #     # Commit the changes
    #     db.session.commit()
    #     print(f"Course with ID {6} deleted successfully.")
    # else:
    #     print(f"Course with ID {6} not found.")
