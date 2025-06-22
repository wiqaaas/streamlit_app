# config.py

import os

# Tab labels for the chat interface
TAB_LABELS = ["Upcoming Match", "Lesson", "Course", "Article"]

# Map each tab to its corresponding Excel filename
FILENAME_MAP = {
    "Upcoming Match": "df_schedule.xlsx",
    "Lesson":         "df_lessons.xlsx",
    "Course":         "df_courses.xlsx",
    "Article":        "df_article_schedule.xlsx",
}
