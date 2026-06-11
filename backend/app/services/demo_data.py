"""Demo datasets for agents without external integrations."""

CAMPUS_BUILDINGS = [
    {
        "id": "eng-hall",
        "name": "Engineering Hall",
        "code": "ENG",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "rooms": {"402": "CS Lab", "101": "Lecture Hall A"},
    },
    {
        "id": "library",
        "name": "Central Library",
        "code": "LIB",
        "latitude": 40.7135,
        "longitude": -74.0055,
        "rooms": {"201": "Study Zone", "301": "Archives"},
    },
    {
        "id": "business-school",
        "name": "Business School",
        "code": "BUS",
        "latitude": 40.7140,
        "longitude": -74.0070,
        "rooms": {"105": "MBA Classroom", "210": "Career Center"},
    },
    {
        "id": "student-center",
        "name": "Student Center",
        "code": "STC",
        "latitude": 40.7120,
        "longitude": -74.0050,
        "rooms": {"001": "Registrar", "050": "Advising Office"},
    },
]

WALKING_TIMES: dict[tuple[str, str], int] = {
    ("library", "eng-hall"): 5,
    ("library", "business-school"): 8,
    ("eng-hall", "business-school"): 7,
    ("eng-hall", "student-center"): 4,
    ("library", "student-center"): 6,
}

ADMISSIONS_PROGRAMS = [
    {
        "name": "BSc Computer Science",
        "level": "undergraduate",
        "department": "Engineering",
        "credits": 120,
        "tuition_annual": 18500,
        "requirements": ["High school diploma", "Math SAT 600+", "Personal statement"],
        "deadline": "2026-03-15",
    },
    {
        "name": "MSc Data Science",
        "level": "graduate",
        "department": "Engineering",
        "credits": 36,
        "tuition_annual": 24000,
        "requirements": ["Bachelor's degree", "GPA 3.0+", "GRE optional", "Two references"],
        "deadline": "2026-02-01",
    },
    {
        "name": "MBA",
        "level": "graduate",
        "department": "Business",
        "credits": 48,
        "tuition_annual": 32000,
        "requirements": ["Bachelor's degree", "2 years work experience", "GMAT/GRE"],
        "deadline": "2026-04-01",
    },
]

CAREER_OPPORTUNITIES = [
    {
        "id": "int-001",
        "title": "ML Engineering Intern",
        "company": "TechCorp AI",
        "type": "internship",
        "skills": ["Python", "Machine Learning", "TensorFlow"],
        "gpa_min": 3.0,
        "majors": ["Computer Science", "Data Science"],
    },
    {
        "id": "int-002",
        "title": "Software Developer Intern",
        "company": "CampusOS Labs",
        "type": "internship",
        "skills": ["Python", "React", "SQL"],
        "gpa_min": 2.8,
        "majors": ["Computer Science"],
    },
    {
        "id": "job-001",
        "title": "Junior Data Analyst",
        "company": "Analytics Inc",
        "type": "full_time",
        "skills": ["SQL", "Python", "Statistics"],
        "gpa_min": 3.2,
        "majors": ["Data Science", "Computer Science", "Statistics"],
    },
    {
        "id": "job-002",
        "title": "AI Research Associate",
        "company": "University Research Lab",
        "type": "part_time",
        "skills": ["PyTorch", "NLP", "Research"],
        "gpa_min": 3.5,
        "majors": ["Computer Science"],
    },
]

COURSE_SCHEDULES = [
    {"code": "CS401", "title": "Machine Learning", "days": ["Mon", "Wed"], "start": "09:00", "end": "10:30", "building": "eng-hall", "room": "402"},
    {"code": "CS350", "title": "Databases", "days": ["Tue", "Thu"], "start": "11:00", "end": "12:30", "building": "eng-hall", "room": "101"},
    {"code": "MATH301", "title": "Statistics", "days": ["Mon", "Wed", "Fri"], "start": "14:00", "end": "15:00", "building": "business-school", "room": "105"},
    {"code": "CS380", "title": "Software Engineering", "days": ["Tue"], "start": "09:00", "end": "12:00", "building": "eng-hall", "room": "402"},
]
