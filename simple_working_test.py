#!/usr/bin/env python3
"""
Ultra simple test that should definitely work
"""

# Simple quiz metadata
quiz_metadata = {
    "title": "Simple Test Quiz",
    "subject": "Mathematics",
    "duration": "30 minutes", 
    "total_marks": 10
}

# Very simple MCQ questions - no templates
mcq = [
    {
        "question": r"What is 2 + 2?",
        "options": [r"3", r"4", r"5", r"6"],
        "answer": r"4",
        "marks": 2
    },
    {
        "question": r"What is 3 x 3?",
        "options": [r"6", r"8", r"9", r"12"],
        "answer": r"9",
        "marks": 2
    }
]

# Very simple subjective questions - no templates
subjective = [
    {
        "question": r"What is addition?",
        "answer": r"Addition is combining numbers to get a sum.",
        "marks": 3
    },
    {
        "question": r"What is multiplication?",
        "answer": r"Multiplication is repeated addition.",
        "marks": 3
    }
]