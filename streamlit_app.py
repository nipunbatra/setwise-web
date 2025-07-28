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
    }
]

subjective = [
    {
        "question": r"Derive the kinetic energy formula. Show that $KE = \\frac{1}{2}mv^2$.",
        "answer": r"Starting with Newton's second law F=ma and work-energy theorem, we integrate force over distance to get kinetic energy.",
        "marks": 5
    }
]''',
        
        "Mathematics": '''mcq = [
    {
        "question": r"What is the derivative of $\\sin(x)$?",
        "options": [r"$\\cos(x)$", r"$-\\cos(x)$", r"$\\tan(x)$", r"$-\\sin(x)$"],
        "answer": r"$\\cos(x)$",
        "marks": 1
    }
]

subjective = [
    {
        "question": r"Prove that $\\sum_{i=1}^{n} i = \\frac{n(n+1)}{2}$ using mathematical induction.",
        "answer": r"Base case: n=1, LHS=1, RHS=1(2)/2=1. Inductive step: assume true for k, prove for k+1.",
        "marks": 5
    }
]''',

        "Programming": '''mcq = [
    {
        "question": r"Which creates a list in Python?",
        "options": [r"[]", r"{}", r"()", r"<>"],
        "answer": r"[]",
        "marks": 1
    }
]

subjective = [
    {
        "question": r"Explain recursion with an example. Write a recursive factorial function.",
        "answer": r"Recursion is when a function calls itself. def factorial(n): return 1 if n <= 1 else n * factorial(n-1)",
        "marks": 5
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
    }
]

subjective = [
    {
        "question": r"Explain photosynthesis.",
        "answer": r"Process by which plants convert sunlight to energy.",
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