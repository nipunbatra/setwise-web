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
        "marks": 2
    },
    {
        "question": r"The acceleration due to gravity is approximately:",  
        "options": [r"$9.8\\,\\text{m/s}^2$", r"$10\\,\\text{m/s}^2$", r"$8.9\\,\\text{m/s}^2$", r"$11\\,\\text{m/s}^2$"],
        "answer": r"$9.8\\,\\text{m/s}^2$",
        "marks": 2
    },
    {
        "question": r"Which law states that force equals mass times acceleration?",
        "options": [r"Newton's First Law", r"Newton's Second Law", r"Newton's Third Law", r"Conservation of Energy"],
        "answer": r"Newton's Second Law", 
        "marks": 2
    }
]

subjective = [
    {
        "question": r"Derive the kinetic energy formula. Show that $KE = \\frac{1}{2}mv^2$.\\n\\n(a) Start with work-energy theorem\\n(b) Use Newton's second law\\n(c) Integrate to find the final expression",
        "answer": r"(a) Work-energy theorem: W = ΔKE\\n(b) F = ma, so W = ∫F·dx = ∫ma·dx\\n(c) Using v = dx/dt and a = dv/dt: W = ∫mv(dv/dt)dx = ∫mv dv = ½mv² - ½mv₀²\\nTherefore KE = ½mv²",
        "marks": 8
    },
    {
        "question": r"A projectile is launched at angle θ with initial velocity v₀.\\n\\n(a) Find the maximum height reached\\n(b) Calculate the range\\n(c) At what angle is range maximum?",
        "answer": r"(a) H = (v₀sinθ)²/(2g)\\n(b) R = v₀²sin(2θ)/g\\n(c) Maximum range at θ = 45° since sin(2θ) is maximum when 2θ = 90°",
        "marks": 10
    },
    {
        "question": r"Explain electromagnetic induction.\\n\\n(a) State Faraday's law\\n(b) Give two practical applications\\n(c) Explain Lenz's law with an example",
        "answer": r"(a) EMF = -dΦ/dt where Φ is magnetic flux\\n(b) Applications: generators, transformers, induction motors\\n(c) Lenz's law: induced current opposes the change causing it. Example: moving magnet toward coil induces current creating opposing magnetic field",
        "marks": 12
    }
]''',
        
        "Mathematics": '''mcq = [
    {
        "question": r"What is the derivative of $\\sin(x)$?",
        "options": [r"$\\cos(x)$", r"$-\\cos(x)$", r"$\\tan(x)$", r"$-\\sin(x)$"],
        "answer": r"$\\cos(x)$",
        "marks": 2
    },
    {
        "question": r"The integral $\\int_0^1 x^2 dx$ equals:",
        "options": [r"$\\frac{1}{3}$", r"$\\frac{1}{2}$", r"$1$", r"$\\frac{2}{3}$"],
        "answer": r"$\\frac{1}{3}$",
        "marks": 2
    },
    {
        "question": r"What is $\\lim_{x \\to 0} \\frac{\\sin x}{x}$?",
        "options": [r"0", r"1", r"$\\infty$", r"Does not exist"],
        "answer": r"1",
        "marks": 3
    }
]

subjective = [
    {
        "question": r"Prove that $\\sum_{i=1}^{n} i = \\frac{n(n+1)}{2}$ using mathematical induction.\\n\\n(a) State and verify the base case\\n(b) Write the inductive hypothesis\\n(c) Prove the inductive step",
        "answer": r"(a) Base case n=1: LHS = 1, RHS = 1(2)/2 = 1 ✓\\n(b) Assume true for k: ∑ᵢ₌₁ᵏ i = k(k+1)/2\\n(c) For n=k+1: ∑ᵢ₌₁ᵏ⁺¹ i = ∑ᵢ₌₁ᵏ i + (k+1) = k(k+1)/2 + (k+1) = (k+1)(k+2)/2",
        "marks": 8
    },
    {
        "question": r"Find the area between curves $y = x^2$ and $y = 2x$.\\n\\n(a) Find intersection points\\n(b) Set up the integral\\n(c) Evaluate the integral",
        "answer": r"(a) x² = 2x → x² - 2x = 0 → x(x-2) = 0 → x = 0, 2\\n(b) Area = ∫₀² (2x - x²) dx\\n(c) = [x² - x³/3]₀² = 4 - 8/3 = 4/3",
        "marks": 10
    },
    {
        "question": r"Solve the differential equation $\\frac{dy}{dx} = \\frac{x}{y}$.\\n\\n(a) Separate variables\\n(b) Integrate both sides\\n(c) Find the general solution",
        "answer": r"(a) y dy = x dx\\n(b) ∫y dy = ∫x dx → y²/2 = x²/2 + C\\n(c) y² = x² + 2C → y² - x² = K (hyperbola family)",
        "marks": 8
    }
]''',

        "Programming": '''mcq = [
    {
        "question": r"Which creates a list in Python?",
        "options": [r"[]", r"{}", r"()", r"<>"],
        "answer": r"[]",
        "marks": 2
    },
    {
        "question": r"Time complexity of binary search is:",
        "options": [r"$O(n)$", r"$O(\\log n)$", r"$O(n^2)$", r"$O(1)$"],
        "answer": r"$O(\\log n)$",
        "marks": 2
    },
    {
        "question": r"Which data structure uses LIFO principle?",
        "options": [r"Queue", r"Stack", r"Array", r"Tree"],
        "answer": r"Stack",
        "marks": 2
    }
]

subjective = [
    {
        "question": r"Explain recursion and implement factorial function.\\n\\n(a) Define recursion\\n(b) Write recursive factorial code\\n(c) Trace execution for factorial(4)",
        "answer": r"(a) Recursion: function calls itself with simpler input until base case\\n(b) def factorial(n):\\n    if n <= 1: return 1\\n    return n * factorial(n-1)\\n(c) f(4)→4*f(3)→4*3*f(2)→4*3*2*f(1)→4*3*2*1=24",
        "marks": 8
    },
    {
        "question": r"Compare sorting algorithms.\\n\\n(a) Time complexity of bubble sort vs quicksort\\n(b) When to use each algorithm\\n(c) Write bubble sort pseudocode",
        "answer": r"(a) Bubble: O(n²) always; Quicksort: O(n log n) average, O(n²) worst\\n(b) Bubble: educational/small data; Quick: large datasets\\n(c) for i=0 to n-1:\\n    for j=0 to n-i-2:\\n        if arr[j] > arr[j+1]: swap(arr[j], arr[j+1])",
        "marks": 10
    },
    {
        "question": r"Design a simple REST API.\\n\\n(a) List 4 HTTP methods and their purposes\\n(b) Design endpoints for a book library system\\n(c) Write a sample JSON response for GET /books",
        "answer": r"(a) GET(retrieve), POST(create), PUT(update), DELETE(remove)\\n(b) GET /books, POST /books, PUT /books/:id, DELETE /books/:id\\n(c) {\\\"books\\\": [{\\\"id\\\": 1, \\\"title\\\": \\\"Python Guide\\\", \\\"author\\\": \\\"Smith\\\"}]}",
        "marks": 12
    }
]''',

        "Template": '''mcq = [
    {
        "question": r"Sample MCQ with LaTeX: What is $\\int e^x dx$?",
        "options": [r"$e^x + C$", r"$xe^x + C$", r"$\\frac{e^x}{x} + C$", r"$\\ln(e^x) + C$"],
        "answer": r"$e^x + C$",
        "marks": 3
    }
]

subjective = [
    {
        "question": r"Template subjective question with parts:\\n\\nGiven the function $f(x) = x^3 - 3x^2 + 2x$.\\n\\n(a) Find $f'(x)$\\n(b) Solve $f'(x) = 0$\\n(c) Classify the critical points",
        "answer": r"(a) $f'(x) = 3x^2 - 6x + 2$\\n(b) Using quadratic formula: $x = \\frac{6 \\pm \\sqrt{36-24}}{6} = \\frac{6 \\pm 2\\sqrt{3}}{6} = 1 \\pm \\frac{\\sqrt{3}}{3}$\\n(c) Use second derivative test: $f''(x) = 6x - 6$. Both points are inflection regions.",
        "marks": 10
    }
]'''
    }
    return examples.get(subject, "")

def generate_quiz_pdfs(questions_text, template, num_sets):
    """Generate quiz PDFs using the setwise package with comprehensive debugging"""
    debug_log = []
    
    try:
        debug_log.append("=== STARTING QUIZ GENERATION ===")
        
        if not SETWISE_AVAILABLE:
            return None, f"Setwise package not available. Import error: {IMPORT_ERROR}\\n\\nPlease ensure the setwise package is installed."
        
        debug_log.append("✓ Setwise package available")
        
        # Validate questions format
        try:
            exec(questions_text)
            debug_log.append("✓ Questions syntax valid")
        except SyntaxError as e:
            return None, f"Python syntax error: {str(e)}\\n\\nCheck your mcq = [...] and subjective = [...] format."
        except Exception as e:
            return None, f"Error in questions format: {str(e)}"
        
        # Create temporary file for questions
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(questions_text)
            questions_file = f.name
        
        debug_log.append(f"✓ Questions file created: {questions_file}")
        
        # Create temporary output directory
        output_dir = tempfile.mkdtemp()
        debug_log.append(f"✓ Output directory created: {output_dir}")
        
        try:
            # Find the correct template directory
            import setwise
            from pathlib import Path
            setwise_dir = Path(setwise.__file__).parent
            templates_dir = setwise_dir / 'templates'
            debug_log.append(f"✓ Using templates from: {templates_dir}")
            
            generator = QuizGenerator(
                template_dir=str(templates_dir),
                output_dir=output_dir,
                questions_file=questions_file
            )
            
            debug_log.append("✓ QuizGenerator initialized")
            
            success = generator.generate_quizzes(
                num_sets=num_sets,
                template_name=template,
                compile_pdf=True,
                seed=42
            )
            
            debug_log.append(f"→ generate_quizzes returned: {success}")
            
            if not success:
                debug_info = "\\n".join(debug_log)
                return None, f"QuizGenerator returned False.\\n\\nFull Debug Log:\\n{debug_info}"
                
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            debug_log.append(f"✗ Error: {str(e)}")
            return None, f"Generation error: {str(e)}\\n\\nFull Debug Log:\\n" + "\\n".join(debug_log)
        
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
    """Display PDF with browser compatibility"""
    # Simple approach: show basic info and let user use download buttons
    st.success(f"✅ PDF generated successfully ({len(pdf_data):,} bytes)")
    st.markdown("*Use the Download PDF button to view the quiz (some browsers block inline PDF preview)*")

def main():
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
        example = st.selectbox("Examples", ["", "Physics", "Mathematics", "Programming", "Template"])
    
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
        "marks": 2
    },
    {
        "question": r"Which planet is closest to the Sun?",
        "options": [r"Venus", r"Mercury", r"Earth", r"Mars"],
        "answer": r"Mercury",
        "marks": 2
    },
    {
        "question": r"What is the capital of Japan?",
        "options": [r"Seoul", r"Beijing", r"Tokyo", r"Bangkok"],
        "answer": r"Tokyo",
        "marks": 2
    }
]

subjective = [
    {
        "question": r"Explain photosynthesis.\\n\\n(a) Define the process\\n(b) Write the chemical equation\\n(c) Name two factors that affect the rate",
        "answer": r"(a) Process by which plants convert light energy into chemical energy\\n(b) 6CO₂ + 6H₂O + light → C₆H₁₂O₆ + 6O₂\\n(c) Light intensity, temperature, CO₂ concentration",
        "marks": 8
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
                                key=f"download_pdf_{i}_{len(quiz_sets)}",
                                use_container_width=True,
                                help="Download PDF to your device"
                            )
                    
                    with sub_col3:
                        if quiz_set['answer_key']:
                            st.download_button(
                                label="Download Answers",
                                data=quiz_set['answer_key'],
                                file_name=f"answer_key_{i+1}.txt",
                                mime="text/plain",
                                key=f"download_answers_{i}_{len(quiz_sets)}",
                                use_container_width=True,
                                help="Download answer key as text file"
                            )
                            
                            # Show preview of answer key
                            with st.expander("View Answers"):
                                st.text(quiz_set['answer_key'])
                    
                    # Add spacing between sets
                    if i < len(quiz_sets) - 1:
                        st.markdown("---")
                
                # Reset generate flag but preserve generated content
                if 'generate_now' in st.session_state:
                    del st.session_state.generate_now
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