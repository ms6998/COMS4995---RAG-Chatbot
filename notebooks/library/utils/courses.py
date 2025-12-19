import os
import re
from dataclasses import dataclass
from pprint import pprint

from bs4 import BeautifulSoup, NavigableString, Comment


@dataclass(frozen=True, eq=True)
class Course:
    title: str
    description: str
    semester: str
    instructor: str
    subject: str
    url: str
    course_code: str
    file_name: str = ""


class ColumbiaCourseData:
    """
    Search HTML downloaded from the public directory of classes to
    get the professors teaching, and the subjects available
    """

    def __init__(
        self,
        courses_files: list[str],
        debug: bool=False,
    ) -> None:
        self.courses_files = courses_files
        self.debug = debug

        self.n_courses = 0
        self.courses = []
        self.subjects = []
        self.instructors = []

        for file in self.courses_files:
            self._check(file)

        for file in self.courses_files:
            soup = self._load(file)
            self._validate_structure(soup)
            self.courses += [
                self._parse_course_block(course)
                for course in self._extract_courses(soup)
            ]
            self.subjects += [course.subject for course in self.courses]
            self.instructors += [course.instructor for course in self.courses]

        self.courses = sorted(list(set(self.courses)), key=lambda c: c.title)
        self.subjects = sorted(list(set(self.subjects)))
        self.instructors = sorted(list(set(self.instructors)))

    def _check(self, file: str) -> None:
        if not os.path.isfile(file):
            raise FileNotFoundError(
                f"Course file not found: {file}"
            )

        if not file.lower().endswith(".html"):
            raise ValueError(
                f"Expected an HTML file, given: {file}"
            )

    def _load(self, file):
        with open(file, "r", encoding="utf-8") as f:
            return BeautifulSoup(f.read(), "html.parser")

    def _validate_structure(self, soup) -> None:
        """
        Check that the course HTML looks like we expect. It may change over time
        """

        # Exactly one div#search-results-container will contain courses
        results_containers = soup.find_all("div", id="search-results-container")
        if len(results_containers) != 1:
            raise ValueError(
                f"Expected exactly one div#search-results-container, found {len(results_containers)}"
            )
        results = results_containers[0]

        # The course HTML contains one unordered list
        results_children = [
            child
            for child in results.children
            if getattr(child, "name", None) is not None
            and not isinstance(child, (NavigableString, Comment))
        ]
        ul_children = [c for c in results_children if c.name == "ul"]
        if len(ul_children) != 1:
            raise ValueError(
                f"Expected exactly one '<ul>' of results, found {len(ul_children)}"
            )
        results = ul_children[0]

        # Get the first course (first '<li>')
        courses = results.find_all("li", recursive=False)
        self.n_courses = len(courses)
        if self.debug:
            print(f"Found {self.n_courses} courses")
        if len(courses) == 0:
            raise ValueError(
                "Did not find any courses (the courses '<ul>' is empty?)"
            )
        course = courses[0]

        # A course '<li>' consists of one container
        course_children = [
            child
            for child in course.children
            if getattr(child, "name", None) is not None
            and not isinstance(child, (NavigableString, Comment))
        ]
        course_containers = [c for c in course_children if c.name == "div"]
        if len(course_containers) != 1:
            raise ValueError(
                f"Expected one '<div>' containers, found {len(course_containers)}"
            )
        course = course_containers[0]

        # That container contains one '<h3>' and three containers
        course_children = [
            child
            for child in course.children
            if getattr(child, "name", None) is not None
            and not isinstance(child, (NavigableString, Comment))
        ]
        course_headers = [c for c in course_children if c.name == "h3"]
        course_containers = [c for c in course_children if c.name == "div"]
        if len(course_headers) != 1:
            raise ValueError(
                f"Expected one '<h3>' containers, found {len(course_headers)}"
            )
        if len(course_containers) != 3:
            raise ValueError(
                f"Expected three '<div>' containers, found {len(course_containers)}"
            )

    def _extract_courses(self, soup):
        """
        Return a list of BeautifulSoup elements, one per course.
        Each element is the inner <div> container validated in _validate_structure().
        """

        # Course search results
        results_container = soup.find("div", id="search-results-container")

        # The single <ul> of courses
        ul = next(
            c for c in results_container.children
            if getattr(c, "name", None) == "ul"
        )

        # Raw <li> course elements
        lis = [
            li for li in ul.children
            if getattr(li, "name", None) == "li"
        ]

        # Inner containers
        courses = []
        for li in lis:
            # each <li> must contain exactly one <div> (already validated)
            course_div = next(
                c for c in li.children
                if getattr(c, "name", None) == "div"
            )
            courses.append(course_div)

        # Ensure consistency
        if len(courses) != self.n_courses:
            raise ValueError(
                f"Expected {self.n_courses} courses, found {len(courses)}"
            )

        # Print a course
        if self.debug:
            pprint(courses[0])

        return courses

    def _parse_course_block(self, course) -> Course:
        """
        Parse a single course <div class="col-md-11"> into a Course
        """

        # title from <h3 class="class-title"> ... <a>Title</a>
        h3 = course.find("h3", class_="class-title")
        if h3 is None:
            raise ValueError("Course block missing <h3 class='class-title'>")

        title_link = h3.find("a")
        if title_link is not None:
            title = title_link.get_text(strip=True)
        else:
            # fallback: strip off leading "N. " if present
            text = h3.get_text(" ", strip=True)
            parts = text.split(". ", 1)
            title = parts[1] if len(parts) == 2 else text

        # description from <div class="description ...">
        desc_div = course.find("div", class_="description")
        description = desc_div.get_text(" ", strip=True) if desc_div else ""

        # table row with semester / instructor / subject
        table = course.find("table")
        if table is None or table.tbody is None:
            raise ValueError("Course block missing <table> with details")

        row = table.tbody.find("tr")
        if row is None:
            raise ValueError("Course table missing <tr> row")

        cells = row.find_all("td")
        if len(cells) < 5:
            raise ValueError(f"Expected at least 5 <td> cells, found {len(cells)}")

        # cells[2] = semester
        semester_cell = cells[2]
        semester_li = semester_cell.find("li")
        semester = semester_li.get_text(strip=True) if semester_li else semester_cell.get_text(" ", strip=True)

        # cells[3] = instructor(s)
        instructor_cell = cells[3]
        instructor_li = instructor_cell.find("li")
        instructor = instructor_li.get_text(strip=True) if instructor_li else instructor_cell.get_text(" ", strip=True)

        # cells[4] = subject
        subject_cell = cells[4]
        subject = subject_cell.get_text(" ", strip=True)

        # URL -> course code
        url = ""
        course_code = ""

        url_div = course.find("div", class_="url")
        if url_div:
            link = url_div.find("a", href=True)
            if link:
                url = link["href"].strip()

                m = re.search(r"subj/([^/]+)/([0-9A-Za-z\-]+)-", url)
                if m:
                    dept = m.group(1).replace("%20", " ").strip()
                    num = m.group(2).strip()
                    course_code = f"{dept} {num}"
        print(f"URL: {url}")
        print(f"Course code: {course_code}")

        return Course(
            title=title,
            description=description,
            semester=semester,
            instructor=instructor,
            subject=subject,
            url=url,
            course_code=course_code,
        )
