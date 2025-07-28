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
        "question": r"A ball is dropped from height 20 m. What is its velocity just before hitting the ground?",
        "options": [r"$\\sqrt{2g \\times 20}$ m/s", r"$g \\times 20$ m/s", r"$\\frac{g \\times 20}{2}$ m/s", r"$2g \\times 20$ m/s"],
        "answer": r"$\\sqrt{2g \\times 20}$ m/s",
        "marks": 3
    },
    {
        "template": r"A car travels at {{ speed }} km/h for {{ time }} hours. What distance does it cover?",
        "options": [r"{{ speed * time }} km", r"{{ speed + time }} km", r"{{ speed / time }} km", r"{{ speed - time }} km"],
        "answer": r"{{ speed * time }} km",
        "variables": [
            {"speed": 60, "time": 2},
            {"speed": 80, "time": 3}
        ],
        "marks": 3
    }
]

subjective = [
    {
        "question": r"Derive the kinetic energy formula. Show that $KE = \\frac{1}{2}mv^2$.",
        "answer": r"Starting with Newton's second law F=ma and work-energy theorem, we integrate force over distance to get kinetic energy.",
        "marks": 8
    },
    {
        "template": r"A projectile is launched with initial velocity {{ v0 }} m/s at angle {{ angle }}°. Calculate the maximum height and range.",
        "answer": r"Maximum height: $H = \\frac{({{ v0 }} \\sin {{ angle }}°)^2}{2g}$ m. Range: $R = \\frac{{{ v0 }}^2 \\sin(2 \\times {{ angle }}°)}{g}$ m.",
        "variables": [
            {"v0": 20, "angle": 30},
            {"v0": 25, "angle": 45}
        ],
        "marks": 8
    },
    {
        "question": r"A ball is thrown upward with initial velocity $v_0 = 20$ m/s.",
        "parts": [
            {
                "question": r"Calculate the maximum height reached.",
                "answer": r"Using $v^2 = v_0^2 - 2gh$ at maximum height where $v = 0$: $h = \\frac{v_0^2}{2g} = \\frac{20^2}{2 \\times 9.8} = 20.4$ m",
                "marks": 3
            },
            {
                "question": r"Find the time taken to reach maximum height.",
                "answer": r"Using $v = v_0 - gt$ where $v = 0$: $t = \\frac{v_0}{g} = \\frac{20}{9.8} = 2.04$ s",
                "marks": 2
            }
        ],
        "marks": 5
    }
]''',
        "Machine Learning": '''mcq = [
    {
        "question": r"Which of the following best describes the bias-variance tradeoff in machine learning?",
        "options": [
            r"High bias models always perform better than high variance models",
            r"Bias and variance are independent and don't affect each other", 
            r"Reducing bias typically increases variance, and vice versa",
            r"Variance only matters in unsupervised learning"
        ],
        "answer": r"Reducing bias typically increases variance, and vice versa",
        "marks": 2
    },
    {
        "question": r"In a decision tree, which impurity measure is most commonly used for classification tasks?",
        "options": [
            r"Mean Squared Error (MSE)",
            r"Gini Impurity", 
            r"Mean Absolute Error (MAE)",
            r"R-squared"
        ],
        "answer": r"Gini Impurity",
        "marks": 2
    },
    {
        "template": r"In k-fold cross-validation with k={{ k_value }}, how many times is the model trained?",
        "options": [r"{{ k_value - 1 }}", r"{{ k_value }}", r"{{ k_value + 1 }}", r"{{ k_value * 2 }}"],
        "answer": r"{{ k_value }}",
        "variables": [
            {"k_value": 5},
            {"k_value": 10}
        ],
        "marks": 2
    }
]

subjective = [
    {
        "question": r"Compare and contrast overfitting and underfitting in machine learning models. Provide strategies to address each issue.",
        "answer": r"Overfitting: model memorizes training data, high training accuracy but low validation accuracy. Solutions: regularization, more data, simpler model. Underfitting: model too simple, poor performance on both training and validation. Solutions: more complex model, feature engineering.",
        "marks": 8
    },
    {
        "template": r"Consider a dataset with {{ n_pos }} positive samples and {{ n_neg }} negative samples. Calculate the precision if the model predicts {{ tp }} true positives and {{ fp }} false positives.",
        "answer": r"Precision = TP/(TP+FP) = {{ tp }}/({{ tp }}+{{ fp }}) = {{ tp/(tp+fp) }}",
        "variables": [
            {"n_pos": 100, "n_neg": 50, "tp": 85, "fp": 10},
            {"n_pos": 200, "n_neg": 80, "tp": 180, "fp": 15}
        ],
        "marks": 6
    },
    {
        "question": r"Analyze the performance of a neural network model:",
        "parts": [
            {
                "question": r"Explain the vanishing gradient problem and its impact on deep networks.",
                "answer": r"Gradients become exponentially small in early layers due to product of small derivatives, preventing learning in deep networks.",
                "marks": 4
            },
            {
                "question": r"Suggest two techniques to mitigate this problem.",
                "answer": r"1) Use ReLU activation functions instead of sigmoid/tanh, 2) Apply batch normalization or gradient clipping",
                "marks": 4
            }
        ],
        "marks": 8
    }
]'''
    }
    return examples.get(subject, "")

def generate_quiz_pdfs(questions_text, template, num_sets, header_config=None):
    """Generate quiz PDFs using the setwise package with comprehensive debugging"""
    debug_log = []
    if header_config is None:
        header_config = {}
    
    try:
        debug_log.append("=== STARTING QUIZ GENERATION ===")
        print(f"[DEBUG] Starting generation: template={template}, sets={num_sets}")
        
        if not SETWISE_AVAILABLE:
            print(f"[ERROR] Setwise not available: {IMPORT_ERROR}")
            return None, f"Setwise package not available. Import error: {IMPORT_ERROR}\\n\\nPlease ensure the setwise package is installed."
        
        debug_log.append("✓ Setwise package available")
        print("[DEBUG] ✓ Setwise package available")
        
        # Validate questions format and inspect content
        try:
            print("[DEBUG] Validating questions syntax...")
            exec_globals = {}
            exec(questions_text, exec_globals)
            debug_log.append("✓ Questions syntax valid")
            print("[DEBUG] ✓ Questions syntax valid")
            
            # Debug: inspect the parsed questions
            if 'mcq' in exec_globals:
                mcq_questions = exec_globals['mcq']
                print(f"[DEBUG] Found {len(mcq_questions)} MCQ questions")
                for i, q in enumerate(mcq_questions):
                    print(f"[DEBUG] MCQ {i+1}: keys = {list(q.keys())}")
                    if 'template' in q:
                        print(f"[DEBUG] MCQ {i+1} is templated with variables: {q.get('variables', 'NONE')}")
                    elif 'question' in q:
                        print(f"[DEBUG] MCQ {i+1} is standard question")
                    else:
                        print(f"[DEBUG] MCQ {i+1} ERROR: no 'question' or 'template' field!")
            
            if 'subjective' in exec_globals:
                subj_questions = exec_globals['subjective']
                print(f"[DEBUG] Found {len(subj_questions)} subjective questions")
                for i, q in enumerate(subj_questions):
                    print(f"[DEBUG] SUBJ {i+1}: keys = {list(q.keys())}")
                    if 'template' in q:
                        print(f"[DEBUG] SUBJ {i+1} is templated with variables: {q.get('variables', 'NONE')}")
                    elif 'question' in q:
                        print(f"[DEBUG] SUBJ {i+1} is standard question")
                        if 'parts' in q:
                            print(f"[DEBUG] SUBJ {i+1} has {len(q['parts'])} parts")
                    else:
                        print(f"[DEBUG] SUBJ {i+1} ERROR: no 'question' or 'template' field!")
                        
        except SyntaxError as e:
            print(f"[ERROR] Syntax error: {e}")
            return None, f"Python syntax error: {str(e)}\\n\\nCheck your mcq = [...] and subjective = [...] format."
        except Exception as e:
            print(f"[ERROR] Questions format error: {e}")
            return None, f"Error in questions format: {str(e)}"
        
        # Create temporary file for questions with header metadata
        print("[DEBUG] Creating temporary files...")
        
        # Add header metadata to questions file
        quiz_metadata = f"""
# Quiz Configuration
quiz_config = {{
    "title": "{header_config.get('title', 'Quiz')}",
    "subject": "{header_config.get('subject', '')}",
    "exam_info": "{header_config.get('exam_info', '')}",
    "institution": "",
    "date": "",
    "duration": "",
    "instructions": ""
}}

"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            full_content = quiz_metadata + questions_text
            f.write(full_content)
            questions_file = f.name
        
        debug_log.append(f"✓ Questions file created: {questions_file}")
        print(f"[DEBUG] ✓ Questions file created: {questions_file}")
        print(f"[DEBUG] Questions file content length: {len(full_content)} chars")
        print(f"[DEBUG] Questions file preview:")
        print("--- FILE START ---")
        print(full_content[:500] + "..." if len(full_content) > 500 else full_content)
        print("--- FILE END ---")
        
        # Create temporary output directory
        output_dir = tempfile.mkdtemp()
        debug_log.append(f"✓ Output directory created: {output_dir}")
        print(f"[DEBUG] ✓ Output directory created: {output_dir}")
        
        try:
            # Find the correct template directory
            print("[DEBUG] Setting up templates...")
            import setwise
            from pathlib import Path
            setwise_dir = Path(setwise.__file__).parent
            templates_dir = setwise_dir / 'templates'
            debug_log.append(f"✓ Using templates from: {templates_dir}")
            print(f"[DEBUG] ✓ Using templates from: {templates_dir}")
            
            print("[DEBUG] Initializing QuizGenerator...")
            generator = QuizGenerator(
                template_dir=str(templates_dir),
                output_dir=output_dir,
                questions_file=questions_file
            )
            
            debug_log.append("✓ QuizGenerator initialized")
            print("[DEBUG] ✓ QuizGenerator initialized")
            
            print(f"[DEBUG] Calling generate_quizzes(sets={num_sets}, template={template})...")
            import time
            import random
            random_seed = random.randint(1, 10000)
            print(f"[DEBUG] Using random seed: {random_seed}")
            start_time = time.time()
            
            # Header configuration is now included in the questions file as quiz_config
            print(f"[DEBUG] Header metadata included in questions file: title='{header_config.get('title', 'Quiz')}', subject='{header_config.get('subject', '')}', exam_info='{header_config.get('exam_info', '')}'")
            
            try:
                # Add timeout monitoring
                import signal
                
                def timeout_handler(signum, frame):
                    raise TimeoutError("Quiz generation timed out after 60 seconds")
                
                print("[DEBUG] Starting generation with 60 second timeout...")
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(60)  # 60 second timeout
                
                try:
                    success = generator.generate_quizzes(
                        num_sets=num_sets,
                        template_name=template,
                        compile_pdf=True,
                        seed=random_seed
                    )
                    
                    # Check intermediate results during generation
                    print(f"[DEBUG] Post-generation check - files in output dir:")
                    try:
                        files = os.listdir(output_dir)
                        for f in files:
                            fpath = os.path.join(output_dir, f)
                            size = os.path.getsize(fpath) if os.path.isfile(fpath) else 0
                            print(f"[DEBUG]   {f}: {size} bytes")
                    except Exception as e:
                        print(f"[DEBUG]   Error listing files: {e}")
                        
                finally:
                    signal.alarm(0)  # Cancel the alarm
                
                end_time = time.time()
                debug_log.append(f"→ generate_quizzes returned: {success} (took {end_time-start_time:.2f}s)")
                print(f"[DEBUG] → generate_quizzes returned: {success} (took {end_time-start_time:.2f}s)")
                
                if not success:
                    print("[ERROR] QuizGenerator returned False")
                    # Try to read any error logs from the generator if available
                    try:
                        # Check if there are any error files in the output directory
                        error_files = [f for f in os.listdir(output_dir) if 'error' in f.lower() or 'log' in f.lower()]
                        if error_files:
                            print(f"[DEBUG] Found error files: {error_files}")
                            for ef in error_files:
                                with open(os.path.join(output_dir, ef), 'r') as f:
                                    print(f"[DEBUG] Error file {ef}: {f.read()}")
                    except:
                        pass
                    
                    debug_info = "\\n".join(debug_log)
                    return None, f"QuizGenerator returned False.\\n\\nFull Debug Log:\\n{debug_info}"
                    
            except TimeoutError as timeout_error:
                end_time = time.time()
                print(f"[ERROR] Timeout during generation: {timeout_error}")
                debug_log.append(f"✗ Timeout after {end_time-start_time:.2f}s: {str(timeout_error)}")
                debug_info = "\\n".join(debug_log)
                return None, f"Generation timeout: {str(timeout_error)}\\n\\nFull Debug Log:\\n{debug_info}"
                    
            except Exception as gen_error:
                end_time = time.time()
                print(f"[ERROR] Exception during generate_quizzes: {gen_error}")
                debug_log.append(f"✗ Exception during generation: {str(gen_error)}")
                debug_info = "\\n".join(debug_log)
                return None, f"Generation exception: {str(gen_error)}\\n\\nFull Debug Log:\\n{debug_info}"
                
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            debug_log.append(f"✗ Error: {str(e)}")
            return None, f"Generation error: {str(e)}\\n\\nFull Debug Log:\\n" + "\\n".join(debug_log)
        
        # Collect results
        print("[DEBUG] Collecting results...")
        quiz_sets = []
        
        for i in range(1, num_sets + 1):
            pdf_path = os.path.join(output_dir, f'quiz_set_{i}.pdf')
            answer_path = os.path.join(output_dir, f'answer_key_{i}.txt')
            
            print(f"[DEBUG] Checking for files: PDF={os.path.exists(pdf_path)}, Answer={os.path.exists(answer_path)}")
            
            if os.path.exists(pdf_path):
                with open(pdf_path, 'rb') as f:
                    pdf_data = f.read()
                
                print(f"[DEBUG] Read PDF {i}: {len(pdf_data)} bytes")
                
                answer_key = ""
                if os.path.exists(answer_path):
                    with open(answer_path, 'r') as f:
                        answer_key = f.read()
                    print(f"[DEBUG] Read answer key {i}: {len(answer_key)} chars")
                
                quiz_sets.append({
                    'name': f'Quiz Set {i}',
                    'pdf_data': pdf_data,
                    'answer_key': answer_key
                })
                print(f"[DEBUG] Added quiz set {i} to results")
        
        print(f"[DEBUG] Final results: {len(quiz_sets)} quiz sets collected")
        
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
    
    # Controls row 1
    col_ctrl1, col_ctrl2, col_ctrl3, col_ctrl4 = st.columns([1, 1, 1, 2])
    
    with col_ctrl1:
        template = st.selectbox("Template", ["default", "compact", "minimal"])
    
    with col_ctrl2:
        num_sets = st.slider("Sets", 1, 5, 2)
    
    with col_ctrl3:
        example = st.selectbox("Examples", ["", "Physics", "Machine Learning"])
    
    with col_ctrl4:
        if st.button("Load Example", disabled=not example):
            st.session_state.questions = load_example_questions(example)
            st.rerun()
    
    # Controls row 2 - Header customization
    st.markdown("**Quiz Header Customization:**")
    col_header1, col_header2, col_header3 = st.columns([1, 1, 1])
    
    with col_header1:
        quiz_title = st.text_input("Quiz Title", value="Quiz", help="Main title that appears at the top")
    
    with col_header2:
        subject_name = st.text_input("Subject", value="", help="Subject name (e.g., 'Machine Learning', 'Physics')")
    
    with col_header3:
        exam_info = st.text_input("Exam Info", value="", help="Additional info (e.g., 'Midterm Exam', 'Final Test')")
    
    # Store header info in session state for quiz generation
    st.session_state.header_config = {
        "title": quiz_title,
        "subject": subject_name,
        "exam_info": exam_info
    }
    
    # Main split pane layout
    col_left, col_right = st.columns([1, 1])
    
    # LEFT PANE: Questions Editor
    with col_left:
        st.subheader("Questions Editor")
        
        # Initialize default questions - SIMPLE TEST (no templates)
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
    }
]

subjective = [
    {
        "question": r"Explain the concept of photosynthesis.",
        "answer": r"Photosynthesis is the process by which plants convert sunlight into energy.",
        "marks": 5
    },
    {
        "question": r"Derive Newton's second law of motion.",
        "answer": r"F = ma can be derived from Newton's first law and the definition of momentum.",
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
                # Clear previous results to ensure fresh generation
                if 'quiz_results' in st.session_state:
                    del st.session_state.quiz_results
                st.session_state.generate_now = True
                st.rerun()
    
    # RIGHT PANE: PDF Previews
    with col_right:
        st.subheader(f"PDF Preview ({num_sets} sets)")
        
        # Check if we need to generate new quizzes or show existing ones
        should_generate = st.session_state.get('generate_now', False) and questions_text.strip()
        has_existing = 'quiz_results' in st.session_state and st.session_state.quiz_results
        
        if should_generate:
            # Add debug info in the UI
            st.info("🔄 Starting quiz generation...")
            debug_container = st.empty()
            
            with st.spinner(f"Generating {num_sets} quiz sets..."):
                debug_container.text("Step 1: Validating questions...")
                header_config = st.session_state.get('header_config', {})
                print(f"[STREAMLIT] About to call generate_quiz_pdfs with {len(questions_text)} chars, template={template}, sets={num_sets}")
                quiz_sets, error = generate_quiz_pdfs(questions_text, template, num_sets, header_config)
                debug_container.text("Step 2: Generation complete, processing results...")
                print(f"[STREAMLIT] generate_quiz_pdfs returned: quiz_sets={len(quiz_sets) if quiz_sets else 0}, error={bool(error)}")
            
            # Store results in session state to prevent regeneration on download
            if quiz_sets and not error:
                st.session_state.quiz_results = {
                    'quiz_sets': quiz_sets,
                    'error': error,
                    'template': template,
                    'num_sets': num_sets
                }
            
            # Reset generate flag but preserve generated content
            if 'generate_now' in st.session_state:
                del st.session_state.generate_now
        
        # Display results (either newly generated or from session state)
        if has_existing or (should_generate and not st.session_state.get('generate_now')):
            if has_existing:
                quiz_data = st.session_state.quiz_results
                quiz_sets = quiz_data['quiz_sets']
                error = quiz_data['error']
            else:
                # Use the results we just generated
                pass
            
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
                
                # Results are now preserved in session state for downloads
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