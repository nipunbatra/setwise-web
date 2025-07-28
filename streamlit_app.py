#!/usr/bin/env python3
"""
Setwise Web Interface
Professional LaTeX quiz generator with live preview
"""

import streamlit as st
import tempfile
import os
import base64
from pathlib import Path

# Try to import setwise package
try:
    from setwise.quiz_generator import QuizGenerator
    from setwise.template_manager import TemplateManager
    SETWISE_AVAILABLE = True
except ImportError as e:
    SETWISE_AVAILABLE = False
    IMPORT_ERROR = str(e)

st.set_page_config(
    page_title="Setwise Quiz Generator",
    page_icon="🎯",
    layout="wide"
)

def load_example_questions(subject):
    """Load example questions for different subjects"""
    examples = {
        "Physics": '''mcq = [
    {
        "question": r"What is the SI unit of force?",
        "options": [r"Joule", r"Newton", r"Watt", r"Pascal"],
        "answer": r"Newton",
        "marks": 1
    },
    {
        "question": r"The acceleration due to gravity is approximately:",
        "options": [r"$9.8\\,\\text{m/s}^2$", r"$10\\,\\text{m/s}^2$", r"$8.9\\,\\text{m/s}^2$", r"$11\\,\\text{m/s}^2$"],
        "answer": r"$9.8\\,\\text{m/s}^2$",
        "marks": 1
    },
    {
        "question": r"Which law states that force equals mass times acceleration?",
        "options": [r"Newton's First Law", r"Newton's Second Law", r"Newton's Third Law", r"Law of Conservation"],
        "answer": r"Newton's Second Law",
        "marks": 1
    },
    {
        "question": r"What is the formula for electric power?",
        "options": [r"$P = VI$", r"$P = IR$", r"$P = \\frac{V}{I}$", r"$P = V + I$"],
        "answer": r"$P = VI$",
        "marks": 1
    },
    {
        "question": r"The speed of light in vacuum is:",
        "options": [r"$3 \\times 10^8\\,\\text{m/s}$", r"$3 \\times 10^6\\,\\text{m/s}$", r"$9 \\times 10^8\\,\\text{m/s}$", r"$3 \\times 10^{10}\\,\\text{m/s}$"],
        "answer": r"$3 \\times 10^8\\,\\text{m/s}$",
        "marks": 1
    },
    {
        "question": r"What type of wave is sound?",
        "options": [r"Electromagnetic", r"Longitudinal", r"Transverse", r"Surface"],
        "answer": r"Longitudinal",
        "marks": 1
    },
    {
        "question": r"The unit of electric current is:",
        "options": [r"Volt", r"Ohm", r"Ampere", r"Watt"],
        "answer": r"Ampere",
        "marks": 1
    },
    {
        "question": r"Which particle has no electric charge?",
        "options": [r"Proton", r"Electron", r"Neutron", r"Ion"],
        "answer": r"Neutron",
        "marks": 1
    }
]

subjective = [
    {
        "question": r"Derive the kinetic energy formula. Show that $KE = \\frac{1}{2}mv^2$.",
        "answer": r"Starting with Newton's second law F=ma and work-energy theorem, we integrate force over distance to get kinetic energy.",
        "marks": 5
    },
    {
        "question": r"Explain Ohm's Law and derive the relationship between voltage, current, and resistance.",
        "answer": r"Ohm's Law states V=IR. For a conductor at constant temperature, voltage is directly proportional to current.",
        "marks": 4
    },
    {
        "question": r"Describe the photoelectric effect and explain why it supports the particle nature of light.",
        "answer": r"The photoelectric effect shows electrons are emitted when light hits a surface, demonstrating light's quantum nature.",
        "marks": 6
    },
    {
        "question": r"What is simple harmonic motion? Give examples and derive the equation of motion.",
        "answer": r"SHM is periodic motion where restoring force is proportional to displacement: F = -kx, leading to x(t) = A cos(ωt + φ).",
        "marks": 5
    }
]''',
        
        "Mathematics": '''mcq = [
    {
        "question": r"What is the derivative of $\\sin(x)$?",
        "options": [r"$\\cos(x)$", r"$-\\cos(x)$", r"$\\tan(x)$", r"$-\\sin(x)$"],
        "answer": r"$\\cos(x)$",
        "marks": 1
    },
    {
        "question": r"The integral $\\int x^2 dx$ equals:",
        "options": [r"$\\frac{x^3}{3} + C$", r"$2x + C$", r"$x^3 + C$", r"$\\frac{x^2}{2} + C$"],
        "answer": r"$\\frac{x^3}{3} + C$",
        "marks": 1
    },
    {
        "question": r"What is $\\lim_{x \\to 0} \\frac{\\sin x}{x}$?",
        "options": [r"0", r"1", r"$\\infty$", r"Does not exist"],
        "answer": r"1",
        "marks": 2
    },
    {
        "question": r"The slope of the line $y = 3x + 5$ is:",
        "options": [r"3", r"5", r"8", r"$\\frac{5}{3}$"],
        "answer": r"3",
        "marks": 1
    },
    {
        "question": r"Which of these is NOT a rational number?",
        "options": [r"$\\frac{22}{7}$", r"$0.\\overline{3}$", r"$\\sqrt{2}$", r"$-5$"],
        "answer": r"$\\sqrt{2}$",
        "marks": 1
    },
    {
        "question": r"The quadratic formula is:",
        "options": [r"$x = \\frac{-b \\pm \\sqrt{b^2-4ac}}{2a}$", r"$x = \\frac{b \\pm \\sqrt{b^2-4ac}}{2a}$", r"$x = \\frac{-b \\pm \\sqrt{b^2+4ac}}{2a}$", r"$x = \\frac{-b \\pm \\sqrt{4ac-b^2}}{2a}$"],
        "answer": r"$x = \\frac{-b \\pm \\sqrt{b^2-4ac}}{2a}$",
        "marks": 1
    },
    {
        "question": r"What is the value of $\\pi$ to 3 decimal places?",
        "options": [r"3.142", r"3.141", r"3.140", r"3.143"],
        "answer": r"3.142",
        "marks": 1
    },
    {
        "question": r"The factorial of 5 is:",
        "options": [r"25", r"120", r"20", r"100"],
        "answer": r"120",
        "marks": 1
    }
]

subjective = [
    {
        "question": r"Prove that $\\sum_{i=1}^{n} i = \\frac{n(n+1)}{2}$ using mathematical induction.",
        "answer": r"Base case: n=1, LHS=1, RHS=1(2)/2=1. Inductive step: assume true for k, prove for k+1.",
        "marks": 5
    },
    {
        "question": r"Find the area under the curve $y = x^2$ from $x = 0$ to $x = 2$.",
        "answer": r"Area = $\\int_0^2 x^2 dx = \\left[\\frac{x^3}{3}\\right]_0^2 = \\frac{8}{3}$",
        "marks": 4
    },
    {
        "question": r"Solve the system of equations: $2x + 3y = 7$ and $x - y = 1$.",
        "answer": r"From second equation: x = y + 1. Substituting: 2(y+1) + 3y = 7, so y = 1, x = 2.",
        "marks": 4
    },
    {
        "question": r"Prove that the square root of 2 is irrational.",
        "answer": r"Assume $\\sqrt{2} = \\frac{p}{q}$ in lowest terms. Then $2q^2 = p^2$, so p is even. This leads to contradiction.",
        "marks": 6
    }
]''',

        "Programming": '''mcq = [
    {
        "question": r"Which creates a list in Python?",
        "options": [r"[]", r"{}", r"()", r"<>"],
        "answer": r"[]",
        "marks": 1
    },
    {
        "question": r"Time complexity of binary search?",
        "options": [r"$O(n)$", r"$O(\\log n)$", r"$O(n^2)$", r"$O(1)$"],
        "answer": r"$O(\\log n)$",
        "marks": 1
    },
    {
        "question": r"What does SQL stand for?",
        "options": [r"Structured Query Language", r"Simple Query Language", r"Standard Query Language", r"Sequential Query Language"],
        "answer": r"Structured Query Language",
        "marks": 1
    },
    {
        "question": r"Which sorting algorithm has best average case complexity?",
        "options": [r"Bubble Sort", r"Quick Sort", r"Selection Sort", r"Insertion Sort"],
        "answer": r"Quick Sort",
        "marks": 2
    },
    {
        "question": r"In Python, what is the output of print(type([]))?",
        "options": [r"<class 'list'>", r"<class 'array'>", r"list", r"array"],
        "answer": r"<class 'list'>",
        "marks": 1
    },
    {
        "question": r"Which data structure uses LIFO principle?",
        "options": [r"Queue", r"Stack", r"Array", r"Tree"],
        "answer": r"Stack",
        "marks": 1
    },
    {
        "question": r"What is the purpose of a constructor in OOP?",
        "options": [r"Destroy objects", r"Initialize objects", r"Copy objects", r"Compare objects"],
        "answer": r"Initialize objects",
        "marks": 1
    },
    {
        "question": r"Which HTTP method is used to retrieve data?",
        "options": [r"POST", r"GET", r"PUT", r"DELETE"],
        "answer": r"GET",
        "marks": 1
    }
]

subjective = [
    {
        "question": r"Explain recursion with an example. Write a recursive factorial function.",
        "answer": r"Recursion is when a function calls itself. def factorial(n): return 1 if n <= 1 else n * factorial(n-1)",
        "marks": 5
    },
    {
        "question": r"Compare and contrast arrays and linked lists. When would you use each?",
        "answer": r"Arrays have O(1) access but fixed size. Linked lists have dynamic size but O(n) access. Use arrays for frequent access, linked lists for frequent insertions.",
        "marks": 6
    },
    {
        "question": r"Explain the concept of Big O notation and give examples.",
        "answer": r"Big O describes algorithm efficiency. O(1) constant, O(n) linear, O(n²) quadratic. Example: array access O(1), linear search O(n).",
        "marks": 4
    },
    {
        "question": r"What is the difference between SQL JOIN types? Provide examples.",
        "answer": r"INNER JOIN returns matching records. LEFT JOIN returns all left records. RIGHT JOIN returns all right records. FULL JOIN returns all records.",
        "marks": 5
    }
]'''
    }
    return examples.get(subject, "")

def generate_quiz_pdfs(questions_text, template, num_sets):
    """Generate quiz PDFs using the setwise package"""
    try:
        if not SETWISE_AVAILABLE:
            return None, f"Setwise package not available. Import error: {IMPORT_ERROR}\n\nPlease ensure the setwise package is installed."
        
        # Validate questions format
        try:
            exec(questions_text)
        except SyntaxError as e:
            return None, f"Python syntax error: {str(e)}\n\nCheck your mcq = [...] and subjective = [...] format."
        except Exception as e:
            return None, f"Error in questions format: {str(e)}"
        
        # Create temporary file for questions
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(questions_text)
            questions_file = f.name
        
        # Create temporary output directory
        output_dir = tempfile.mkdtemp()
        
        try:
            # Use QuizGenerator API
            generator = QuizGenerator(
                output_dir=output_dir,
                questions_file=questions_file
            )
            
            success = generator.generate_quizzes(
                num_sets=num_sets,
                template_name=template,
                compile_pdf=True,
                seed=42
            )
            
            if not success:
                return None, "Quiz generation failed. Check your question format and LaTeX syntax."
            
        except Exception as e:
            return None, f"Generation error: {str(e)}"
        
        # Collect results
        quiz_sets = []
        for i in range(1, num_sets + 1):
            pdf_path = os.path.join(output_dir, f'quiz_set_{i}.pdf')
            answer_path = os.path.join(output_dir, f'answer_key_{i}.txt')
            
            if os.path.exists(pdf_path):
                with open(pdf_path, 'rb') as f:
                    pdf_data = f.read()
                
                answer_key = ""
                if os.path.exists(answer_path):
                    with open(answer_path, 'r') as f:
                        answer_key = f.read()
                
                quiz_sets.append({
                    'name': f'Quiz Set {i}',
                    'pdf_data': pdf_data,
                    'answer_key': answer_key
                })
        
        # Cleanup
        try:
            os.unlink(questions_file)
        except:
            pass
        
        return quiz_sets, None
        
    except Exception as e:
        return None, f"Unexpected error: {str(e)}"

def display_pdf_embed(pdf_data, height=400):
    """Display PDF using iframe"""
    base64_pdf = base64.b64encode(pdf_data).decode('utf-8')
    pdf_html = f'''
    <iframe src="data:application/pdf;base64,{base64_pdf}" 
            width="100%" height="{height}px" type="application/pdf"
            style="border: 1px solid #ddd; border-radius: 4px;">
    </iframe>
    '''
    st.markdown(pdf_html, unsafe_allow_html=True)

def main():
    # Custom CSS for better appearance
    st.markdown("""
    <style>
    .main > div { padding-top: 1rem; }
    .stTextArea textarea { 
        font-family: 'Monaco', 'Courier New', monospace;
        font-size: 14px;
    }
    .quiz-set-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        background: white;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("Setwise Quiz Generator")
    st.markdown("Professional LaTeX quiz generator with live preview")
    
    # Show status if package not available
    if not SETWISE_AVAILABLE:
        st.error(f"Setwise package not available: {IMPORT_ERROR}")
        st.info("The quiz generator requires the setwise package to be installed.")
        return
    
    # Controls row
    col_ctrl1, col_ctrl2, col_ctrl3, col_ctrl4 = st.columns([1, 1, 1, 2])
    
    with col_ctrl1:
        template = st.selectbox("Template", ["default", "compact", "minimal"])
    
    with col_ctrl2:
        num_sets = st.slider("Sets", 1, 5, 2)
    
    with col_ctrl3:
        example = st.selectbox("Examples", ["", "Physics", "Mathematics", "Programming"])
    
    with col_ctrl4:
        if st.button("Load Example", disabled=not example):
            st.session_state.questions = load_example_questions(example)
            st.rerun()
    
    # Main split pane layout
    col_left, col_right = st.columns([1, 1])
    
    # LEFT PANE: Questions Editor
    with col_left:
        st.subheader("Questions Editor")
        
        # Initialize default questions
        if 'questions' not in st.session_state:
            st.session_state.questions = '''mcq = [
    {
        "question": r"What is $2 + 2$?",
        "options": [r"3", r"4", r"5", r"6"],
        "answer": r"4",
        "marks": 1
    },
    {
        "question": r"Which planet is closest to the Sun?",
        "options": [r"Venus", r"Mercury", r"Earth", r"Mars"],
        "answer": r"Mercury",
        "marks": 1
    },
    {
        "question": r"What is the capital of Japan?",
        "options": [r"Seoul", r"Beijing", r"Tokyo", r"Bangkok"],
        "answer": r"Tokyo",
        "marks": 1
    }
]

subjective = [
    {
        "question": r"Explain the concept of photosynthesis.",
        "answer": r"Photosynthesis is the process by which plants convert sunlight into energy.",
        "marks": 5
    }
]'''
        
        # Text editor
        questions_text = st.text_area(
            "Questions (Python format)",
            value=st.session_state.questions,
            height=500,
            key="editor"
        )
        
        # Update session state
        st.session_state.questions = questions_text
        
        # Validation and generation buttons
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("Validate Questions", use_container_width=True):
                try:
                    exec(questions_text)
                    st.success("Questions format is valid!")
                except SyntaxError as e:
                    st.error(f"Syntax error: {str(e)}")
                except Exception as e:
                    st.error(f"Format error: {str(e)}")
        
        with col_btn2:
            if st.button("Generate Quiz Sets", type="primary", use_container_width=True):
                st.session_state.generate_now = True
                st.rerun()
    
    # RIGHT PANE: PDF Previews
    with col_right:
        st.subheader(f"PDF Preview ({num_sets} sets)")
        
        if st.session_state.get('generate_now', False) and questions_text.strip():
            with st.spinner(f"Generating {num_sets} quiz sets..."):
                quiz_sets, error = generate_quiz_pdfs(questions_text, template, num_sets)
            
            if error:
                st.error("Generation Failed")
                with st.expander("View Error Details"):
                    st.text(error)
            elif quiz_sets:
                # Display each PDF set in rows
                for i, quiz_set in enumerate(quiz_sets):
                    st.markdown(f"**{quiz_set['name']}**")
                    
                    # Three sub-columns: PDF preview, downloads, answer key
                    sub_col1, sub_col2, sub_col3 = st.columns([2, 1, 1])
                    
                    with sub_col1:
                        if quiz_set['pdf_data']:
                            display_pdf_embed(quiz_set['pdf_data'])
                        else:
                            st.warning("PDF generation failed for this set")
                    
                    with sub_col2:
                        if quiz_set['pdf_data']:
                            st.download_button(
                                label="Download PDF",
                                data=quiz_set['pdf_data'],
                                file_name=f"quiz_set_{i+1}.pdf",
                                mime="application/pdf",
                                key=f"download_pdf_{i}",
                                use_container_width=True
                            )
                    
                    with sub_col3:
                        if quiz_set['answer_key']:
                            st.download_button(
                                label="Download Answers",
                                data=quiz_set['answer_key'],
                                file_name=f"answer_key_{i+1}.txt",
                                mime="text/plain",
                                key=f"download_answers_{i}",
                                use_container_width=True
                            )
                            
                            # Show preview of answer key
                            with st.expander("View Answers"):
                                st.text(quiz_set['answer_key'])
                    
                    # Add spacing between sets
                    if i < len(quiz_sets) - 1:
                        st.markdown("---")
                
                # Reset generate flag
                st.session_state.generate_now = False
            else:
                st.warning("No PDFs generated")
        else:
            # Show instructions when no preview
            st.info("Enter questions and click 'Generate Quiz Sets'")
            st.markdown("""
            **How to use:**
            1. Edit questions in left pane
            2. Choose template and number of sets
            3. Click generate to see live PDF previews
            4. Download PDFs and answer keys
            
            **Question format:**
            - Use `mcq = [...]` and `subjective = [...]` arrays
            - LaTeX math: `r"What is $x^2$?"`
            - MCQ needs `answer` field matching an option
            """)

if __name__ == "__main__":
    main()