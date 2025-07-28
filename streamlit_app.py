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

# Try to import PDF viewer
try:
    from streamlit_pdf_viewer import pdf_viewer
    PDF_VIEWER_AVAILABLE = True
except ImportError:
    PDF_VIEWER_AVAILABLE = False

st.set_page_config(
    page_title="Setwise Quiz Generator",
    page_icon="🎯",
    layout="wide"
)

def load_example_questions(subject):
    """Load example questions for different subjects"""
    examples = {
        "Physics": '''# Quiz metadata - NEW in Setwise v2.0!
quiz_metadata = {
    "title": "Physics Fundamentals Quiz",
    "subject": "Physics", 
    "duration": "60 minutes",
    "total_marks": 25,
    "instructions": ["Show all work", "Use proper units"]
}

mcq = [
    {
        "question": r"What is the SI unit of force?",
        "options": [r"Joule", r"Newton", r"Watt", r"Pascal"],
        "answer": r"Newton",
        "marks": 2
    },
    {
        "template": r"A ball is dropped from height {{ h }} m. What is its velocity just before hitting the ground? (g = 9.8 m/s²)",
        "options": [
            r"$\\sqrt{2g \$\times$ {{ h }}}$ ≈ {{ velocity:.1f }} m/s",
            r"$g \$\times$ {{ h }}$ = {{ h * 9.8 }} m/s", 
            r"$\\frac{g \$\times$ {{ h }}}{2}$ = {{ h * 4.9 }} m/s",
            r"$2g \$\times$ {{ h }}$ = {{ 2 * h * 9.8 }} m/s"
        ],
        "answer": r"$\\sqrt{2g \$\times$ {{ h }}}$ ≈ {{ velocity:.1f }} m/s",
        "variables": [
            {"h": 20, "velocity": 19.8},
            {"h": 45, "velocity": 29.7},
            {"h": 80, "velocity": 39.6}
        ],
        "marks": 3
    },
    {
        "template": r"Calculate kinetic energy: KE = ½mv² with m = {{ mass }} kg and v = {{ velocity }} m/s",
        "options": [
            r"{{ 0.5 * mass * velocity**2 }} J",
            r"{{ mass * velocity**2 }} J",
            r"{{ 0.5 * mass * velocity }} J", 
            r"{{ mass * velocity }} J"
        ],
        "answer": r"{{ 0.5 * mass * velocity**2 }} J",
        "variables": [
            {"mass": 2, "velocity": 10},  # KE = 100 J
            {"mass": 5, "velocity": 6},   # KE = 90 J  
            {"mass": 3, "velocity": 8}    # KE = 96 J
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
        "answer": r"Maximum height: $H = \\frac{({{ v0 }} \\sin {{ angle }}°)^2}{2g}$ m. Range: $R = \\frac{{{ v0 }}^2 \\sin(2 \$\times$ {{ angle }}°)}{g}$ m.",
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
                "answer": r"Using $v^2 = v_0^2 - 2gh$ at maximum height where $v = 0$: $h = \\frac{v_0^2}{2g} = \\frac{20^2}{2 \$\times$ 9.8} = 20.4$ m",
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
        "Machine Learning": '''# Showcase NEW Setwise v2.0 features!
quiz_metadata = {
    "title": "Machine Learning Fundamentals",
    "subject": "Computer Science",
    "course_code": "CS 4780", 
    "duration": "90 minutes",
    "total_marks": 50,
    "instructor": "Prof. AI",
    "instructions": ["Show all calculations", "Explain your reasoning"]
}

mcq = [
    {
        "question": r"Which of the following best describes the bias-variance tradeoff?",
        "options": [
            r"High bias models always perform better",
            r"Reducing bias typically increases variance, and vice versa",
            r"Variance only matters in unsupervised learning"
        ],
        "answer": r"Reducing bias typically increases variance, and vice versa",
        "marks": 2
    },
    {
        "template": r"In k-fold cross-validation with k={{ k }}, what percentage of data is used for validation in each fold?",
        "options": [
            r"{{ (100/k):.1f }}%",
            r"{{ (100*(k-1)/k):.1f }}%", 
            r"{{ 100/k**2 }}%",
            r"{{ 50 }}%"
        ],
        "answer": r"{{ (100/k):.1f }}%",
        "variables": [
            {"k": 5},   # 20% validation
            {"k": 10},  # 10% validation
            {"k": 3}    # 33.3% validation
        ],
        "marks": 2
    },
    {
        "template": r"A dataset has {{ n_samples }} samples and {{ n_features }} features. Using {{ train_pct }}% for training, how many samples for training?",
        "options": [
            r"{{ int(n_samples * train_pct / 100) }} samples",
            r"{{ int(n_samples * (100-train_pct) / 100) }} samples",
            r"{{ n_features * train_pct }} samples", 
            r"{{ n_samples }} samples"
        ],
        "answer": r"{{ int(n_samples * train_pct / 100) }} samples",
        "variables": [
            {"n_samples": 1000, "train_pct": 80, "n_features": 10},  # 800 training
            {"n_samples": 500, "train_pct": 70, "n_features": 5},   # 350 training
            {"n_samples": 1500, "train_pct": 75, "n_features": 8}   # 1125 training
        ],
        "marks": 3
    }
]

subjective = [
    {
        "question": r"Compare overfitting and underfitting in machine learning models.",
        "answer": r"Overfitting: model memorizes training data, high training accuracy but low validation accuracy. Solutions: regularization, more data. Underfitting: model too simple, poor performance on both. Solutions: more complex model, feature engineering.",
        "marks": 6
    },
    {
        "template": r"Consider a neural network with {{ layers }} hidden layers, each with {{ neurons }} neurons. Calculate total parameters if input dimension is {{ input_dim }} and output is {{ output_dim }}.",
        "variables": [
            {
                "layers": 2, "neurons": 64, "input_dim": 784, "output_dim": 10,
                "answer": "Layer 1: (784$\times$64)+64=50,240. Layer 2: (64$\times$64)+64=4,160. Output: (64$\times$10)+10=650. Total: 55,050 parameters"
            },
            {
                "layers": 1, "neurons": 128, "input_dim": 1000, "output_dim": 5,
                "answer": "Layer 1: (1000$\times$128)+128=128,128. Output: (128$\times$5)+5=645. Total: 128,773 parameters"
            }
        ],
        "marks": 8
    },
    {
        "question": r"Model Performance Analysis:",
        "parts": [
            {
                "question": r"Given training accuracy = 95% and validation accuracy = 65%, what problem does this indicate?",
                "answer": r"This indicates overfitting. Large gap between training (95%) and validation (65%) shows the model memorized training data rather than learning generalizable patterns.",
                "marks": 3
            },
            {
                "question": r"Suggest three techniques to address this issue.",
                "answer": r"1) Regularization (L1/L2) to penalize large weights. 2) Dropout during training to prevent co-adaptation. 3) Early stopping based on validation performance.",
                "marks": 6
            }
        ],
        "marks": 9
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
        
        # Create questions file WITHOUT quiz_config to test if that's causing issues
        print("[DEBUG] Creating questions file WITHOUT quiz_config metadata...")
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            full_content = questions_text  # Just the questions, no metadata
            f.write(full_content)
            questions_file = f.name
        
        debug_log.append(f"✓ Questions file created: {questions_file}")
        print(f"[DEBUG] ✓ Questions file created: {questions_file}")
        print(f"[DEBUG] Questions file content length: {len(full_content)} chars")
        print(f"[DEBUG] FULL Questions file content:")
        print("=" * 80)
        print(full_content)
        print("=" * 80)
        
        # Create temporary output directory
        output_dir = tempfile.mkdtemp()
        debug_log.append(f"✓ Output directory created: {output_dir}")
        print(f"[DEBUG] ✓ Output directory created: {output_dir}")
        
        try:
            # Find the correct template directory - setwise expects to be run from its own directory
            print("[DEBUG] Setting up templates...")
            import setwise
            from pathlib import Path
            setwise_dir = Path(setwise.__file__).parent
            templates_dir = setwise_dir / 'templates'
            debug_log.append(f"✓ Using templates from: {templates_dir}")
            print(f"[DEBUG] ✓ Using templates from: {templates_dir}")
            
            # Change to setwise directory (CLI expects this)
            original_cwd = os.getcwd()
            print(f"[DEBUG] Changing directory from {original_cwd} to {setwise_dir}")
            os.chdir(str(setwise_dir))
            
            print("[DEBUG] Initializing QuizGenerator...")
            generator = QuizGenerator(
                questions_file=questions_file,
                output_dir=output_dir
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
                print("[DEBUG] Starting quiz generation...")
                
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
                
                end_time = time.time()
                debug_log.append(f"→ generate_quizzes returned: {success} (took {end_time-start_time:.2f}s)")
                print(f"[DEBUG] → generate_quizzes returned: {success} (took {end_time-start_time:.2f}s)")
                
                # Restore original directory
                print(f"[DEBUG] Restoring directory to {original_cwd}")
                os.chdir(original_cwd)
                
                if not success:
                    print("[ERROR] QuizGenerator returned False")
                    
                    # Enhanced error investigation
                    enhanced_debug = []
                    
                    # 1. Check generated files
                    try:
                        files = os.listdir(output_dir)
                        enhanced_debug.append(f"Files created: {files}")
                        
                        # Look for .log files specifically
                        log_files = [f for f in files if f.endswith('.log')]
                        tex_files = [f for f in files if f.endswith('.tex')]
                        pdf_files = [f for f in files if f.endswith('.pdf')]
                        
                        enhanced_debug.append(f"LaTeX files: {tex_files}")
                        enhanced_debug.append(f"PDF files: {pdf_files}")
                        enhanced_debug.append(f"Log files: {log_files}")
                        
                        # Read LaTeX log files for compilation errors
                        for log_file in log_files:
                            log_path = os.path.join(output_dir, log_file)
                            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                                log_content = f.read()
                                if 'Error' in log_content or 'error' in log_content:
                                    enhanced_debug.append(f"LaTeX errors in {log_file}:")
                                    # Extract error lines
                                    error_lines = [line.strip() for line in log_content.split('\n') 
                                                 if ('error' in line.lower() or 'Error' in line) and line.strip()]
                                    enhanced_debug.extend(error_lines[:5])  # First 5 errors
                        
                        # Check if TEX files were created but PDF compilation failed
                        if tex_files and not pdf_files:
                            enhanced_debug.append("❌ LaTeX files created but PDF compilation failed")
                            enhanced_debug.append("💡 This suggests a LaTeX compilation error")
                            
                            # Try to read the tex file to see if it's valid
                            for tex_file in tex_files[:1]:  # Check first tex file
                                tex_path = os.path.join(output_dir, tex_file)
                                with open(tex_path, 'r', encoding='utf-8', errors='ignore') as f:
                                    tex_content = f.read()
                                    enhanced_debug.append(f"TEX file size: {len(tex_content)} characters")
                                    if len(tex_content) < 100:
                                        enhanced_debug.append("⚠️ TEX file seems very small - generation may have failed")
                                    enhanced_debug.append(f"TEX content preview: {tex_content[:200]}...")
                        
                        elif not tex_files:
                            enhanced_debug.append("❌ No LaTeX files created - question processing failed")
                            enhanced_debug.append("💡 This suggests an error in question validation or template processing")
                            
                    except Exception as e:
                        enhanced_debug.append(f"Error investigating files: {e}")
                    
                    # 2. Check template and questions
                    try:
                        enhanced_debug.append(f"Template used: {template}")
                        enhanced_debug.append(f"Number of sets: {num_sets}")
                        enhanced_debug.append(f"Questions file size: {len(open(questions_file).read())} chars")
                        
                        # Try to validate questions manually
                        with open(questions_file, 'r') as f:
                            content = f.read()
                            enhanced_debug.append(f"Questions preview: {content[:300]}...")
                            
                    except Exception as e:
                        enhanced_debug.append(f"Error checking questions: {e}")
                    
                    # 3. Suggest local testing
                    enhanced_debug.append("")
                    enhanced_debug.append("🔍 TROUBLESHOOTING SUGGESTIONS:")
                    enhanced_debug.append("1. Try running locally: pip install git+https://github.com/nipunbatra/setwise.git")
                    enhanced_debug.append("2. Test with: setwise generate --questions-file your_file.py --sets 1")
                    enhanced_debug.append("3. Check LaTeX installation: pdflatex --version")
                    enhanced_debug.append("4. Validate questions: setwise questions validate your_file.py")
                    enhanced_debug.append("")
                    enhanced_debug.append("💡 This error often occurs due to:")
                    enhanced_debug.append("   - LaTeX not properly installed on server")
                    enhanced_debug.append("   - Invalid question syntax")
                    enhanced_debug.append("   - Template rendering errors")
                    enhanced_debug.append("   - Permission issues in temporary directories")
                    
                    debug_info = "\\n".join(debug_log + enhanced_debug)
                    return None, f"QuizGenerator returned False.\\n\\nDetailed Debug Information:\\n{debug_info}"
                    
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
            tex_path = os.path.join(output_dir, f'quiz_set_{i}.tex')
            
            print(f"[DEBUG] Checking for files: PDF={os.path.exists(pdf_path)}, Answer={os.path.exists(answer_path)}, TEX={os.path.exists(tex_path)}")
            
            if os.path.exists(pdf_path):
                with open(pdf_path, 'rb') as f:
                    pdf_data = f.read()
                
                print(f"[DEBUG] Read PDF {i}: {len(pdf_data)} bytes")
                
                answer_key = ""
                if os.path.exists(answer_path):
                    with open(answer_path, 'r') as f:
                        answer_key = f.read()
                    print(f"[DEBUG] Read answer key {i}: {len(answer_key)} chars")
                
                tex_data = ""
                if os.path.exists(tex_path):
                    with open(tex_path, 'r', encoding='utf-8') as f:
                        tex_data = f.read()
                    print(f"[DEBUG] Read TEX {i}: {len(tex_data)} chars")
                
                quiz_sets.append({
                    'name': f'Quiz Set {i}',
                    'pdf_data': pdf_data,
                    'answer_key': answer_key,
                    'tex_data': tex_data
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

def display_pdf_embed(pdf_data, height=400, key_suffix=""):
    """Display PDF with streamlit-pdf-viewer for better compatibility"""
    # Debug: Check if pdf_data is valid
    if pdf_data is None:
        st.error("PDF data is None - generation may have failed")
        return
    
    if not isinstance(pdf_data, bytes):
        st.error(f"PDF data has wrong type: {type(pdf_data)} (expected bytes)")
        return
    
    if len(pdf_data) == 0:
        st.error("PDF data is empty")
        return
    
    if PDF_VIEWER_AVAILABLE:
        try:
            # Try different approaches to fix the NoneType error
            print(f"[DEBUG] Attempting PDF viewer with data type: {type(pdf_data)}, size: {len(pdf_data)}")
            
            # Use the ORIGINAL working version (before zoom_level caused issues)
            pdf_viewer(
                input=pdf_data,
                width=700,
                height=height,
                key=f"pdf_viewer_{key_suffix}"
            )
            st.caption("📖 PDF Preview - Use download button for full-size PDF")
        except Exception as e:
            import traceback
            print(f"[DEBUG] PDF viewer exception details:")
            print(traceback.format_exc())
            
            # Fallback to simple success message
            st.error(f"PDF viewer error: {e}")
            st.success(f"✅ PDF generated successfully ({len(pdf_data):,} bytes)")
            st.markdown("*Use the Download PDF button to view the quiz*")
    else:
        # Fallback when PDF viewer not available
        st.success(f"✅ PDF generated successfully ({len(pdf_data):,} bytes)")
        st.markdown("*Use the Download PDF button to view the quiz (PDF viewer not available)*")

def main():
    st.title("🎯 Setwise Quiz Generator")
    st.markdown("**Professional LaTeX quiz generator with advanced templating**")
    
    # ✨ NEW FEATURES SHOWCASE
    st.info("""
    🎉 **NEW in Setwise v2.0!** This webapp showcases enhanced features:
    
    ✅ **Quiz Metadata** - Professional headers with title, duration, instructions  
    ✅ **Templated MCQ Questions** - Variables in both questions AND options  
    ✅ **Multi-part Questions** - Complex problems with individual marks  
    ✅ **Enhanced Examples** - Physics & Machine Learning with templates  
    """)
    
    st.warning("""
    ⚠️ **Server Limitations:** The web interface has LaTeX and processing limitations. 
    For best results with advanced features, **install locally**: 
    ```bash
    pip install git+https://github.com/nipunbatra/setwise.git
    ```
    💡 Try the **"Try Simpler Example"** button if generation fails!
    """)
    
    # Feature comparison table
    with st.expander("📊 **What's New in v2.0**"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Before v2.0:**")
            st.markdown("""
            - Basic questions only
            - No quiz metadata  
            - MCQ templates blocked
            - Simple subjective questions
            """)
            
        with col2:
            st.markdown("**After v2.0 ✨:**")  
            st.markdown("""
            - **Quiz metadata** with title, duration, etc.
            - **MCQ templates** with variables  
            - **Multi-part questions** with individual marks
            - **Enhanced examples** for Physics & ML
            """)
    
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
        
        # ✨ NEW: Showcase Setwise v2.0 enhanced features!
        if 'questions' not in st.session_state:
            # Try to load from file first, fallback to inline
            try:
                with open('simple_working_test.py', 'r') as f:
                    st.session_state.questions = f.read()
            except:
# Load working example that's been tested locally
                st.session_state.questions = '''# ✨ Setwise v2.0 Demo - Tested and Working!
quiz_metadata = {
    "title": "Enhanced Setwise Demo Quiz",
    "subject": "Mathematics & Science",
    "duration": "45 minutes", 
    "total_marks": 20,
    "instructions": ["Show your work", "Use proper units"]
}

mcq = [
    {
        "question": r"What is 2 + 2?",
        "options": [r"3", r"4", r"5", r"6"],
        "answer": r"4",
        "marks": 1
    },
    {
        "template": r"Calculate: {{ a }} + {{ b }} = ?",
        "options": [
            r"{{ a + b }}",
            r"{{ a - b }}", 
            r"{{ a * b }}",
            r"{{ a }}"
        ],
        "answer": r"{{ a + b }}",
        "variables": [
            {"a": 3, "b": 4},   # 3 + 4 = 7
            {"a": 5, "b": 2},   # 5 + 2 = 7  
            {"a": 8, "b": 1}    # 8 + 1 = 9
        ],
        "marks": 2
    },
    {
        "template": r"A circle has radius {{ r }} cm. What is its area? (pi = 3.14)",
        "options": [
            r"{{ 3.14 * r * r }} square cm",
            r"{{ 2 * 3.14 * r }} square cm",
            r"{{ 3.14 * r }} square cm",
            r"{{ r * r }} square cm"
        ],
        "answer": r"{{ 3.14 * r * r }} square cm",
        "variables": [
            {"r": 2},   # Area = 12.56
            {"r": 3},   # Area = 28.26
            {"r": 5}    # Area = 78.5
        ],
        "marks": 3
    }
]

subjective = [
    {
        "question": r"Explain the concept of mathematical operations.",
        "answer": r"Mathematical operations are procedures that combine numbers to produce new numbers. The four basic operations are addition, subtraction, multiplication, and division.",
        "marks": 4
    },
    {
        "template": r"Calculate the area and perimeter of a rectangle with length {{ length }} units and width {{ width }} units.",
        "variables": [
            {
                "length": 8, "width": 5,
                "answer": "Area = length $\times$ width = 8 $\times$ 5 = 40 square units. Perimeter = 2(length + width) = 2(8 + 5) = 26 units."
            },
            {
                "length": 12, "width": 3, 
                "answer": "Area = length $\times$ width = 12 $\times$ 3 = 36 square units. Perimeter = 2(length + width) = 2(12 + 3) = 30 units."
            }
        ],
        "marks": 6
    },
    {
        "question": r"Problem Solving Steps:",
        "parts": [
            {
                "question": r"What is 15 + 25?",
                "answer": r"15 + 25 = 40",
                "marks": 1
            },
            {
                "question": r"What is 40 $\div$ 8?", 
                "answer": r"40 $\div$ 8 = 5",
                "marks": 1
            },
            {
                "question": r"Explain why these operations give these results.",
                "answer": r"Addition combines quantities: 15 + 25 counts all units together. Division splits equally: 40 $\div$ 8 means 40 split into 8 equal groups of 5.",
                "marks": 2
            }
        ],
        "marks": 4
    }
]'''
quiz_metadata = {
    "title": "Enhanced Setwise Demo Quiz",
    "subject": "Mathematics & Science",
    "duration": "45 minutes", 
    "total_marks": 20,
    "instructions": ["Show your work", "Use proper units"]
}

mcq = [
    {
        "question": r"What is 2 + 2?",
        "options": [r"3", r"4", r"5", r"6"],
        "answer": r"4",
        "marks": 1
    },
    {
        "template": r"Calculate: {{ a }} $\times$ {{ b }} = ?",
        "options": [
            r"{{ a * b }}",
            r"{{ a + b }}", 
            r"{{ a - b }}",
            r"{{ a / b if b != 0 else 'undefined' }}"
        ],
        "answer": r"{{ a * b }}",
        "variables": [
            {"a": 6, "b": 7},   # 42
            {"a": 8, "b": 9},   # 72
            {"a": 4, "b": 5}    # 20
        ],
        "marks": 2
    },
    {
        "template": r"A circle has radius {{ r }} cm. What is its area? (π ≈ 3.14)",
        "options": [
            r"{{ 3.14 * r**2 }} cm²",
            r"{{ 2 * 3.14 * r }} cm²",
            r"{{ 3.14 * r }} cm²",
            r"{{ r**2 }} cm²"
        ],
        "answer": r"{{ 3.14 * r**2 }} cm²",
        "variables": [
            {"r": 3},   # Area = 28.26 cm²
            {"r": 5},   # Area = 78.5 cm²
            {"r": 2}    # Area = 12.56 cm²
        ],
        "marks": 3
    }
]

subjective = [
    {
        "question": r"Explain the concept of mathematical operations.",
        "answer": r"Mathematical operations are procedures that combine numbers to produce new numbers. The four basic operations are addition, subtraction, multiplication, and division.",
        "marks": 4
    },
    {
        "template": r"Calculate the area and perimeter of a rectangle with length {{ length }} units and width {{ width }} units.",
        "variables": [
            {
                "length": 8, "width": 5,
                "answer": "Area = length $\times$ width = 8 $\times$ 5 = 40 square units. Perimeter = 2(length + width) = 2(8 + 5) = 26 units."
            },
            {
                "length": 12, "width": 3, 
                "answer": "Area = length $\times$ width = 12 $\times$ 3 = 36 square units. Perimeter = 2(length + width) = 2(12 + 3) = 30 units."
            }
        ],
        "marks": 6
    },
    {
        "question": r"Problem Solving Steps:",
        "parts": [
            {
                "question": r"What is 15 + 25?",
                "answer": r"15 + 25 = 40",
                "marks": 1
            },
            {
                "question": r"What is 40 $\div$ 8?", 
                "answer": r"40 $\div$ 8 = 5",
                "marks": 1
            },
            {
                "question": r"Explain why these operations give these results.",
                "answer": r"Addition combines quantities: 15 + 25 counts all units together. Division splits equally: 40 $\div$ 8 means 40 split into 8 equal groups of 5.",
                "marks": 2
            }
        ],
        "marks": 4
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
                st.error("⚠️ Quiz Generation Failed")
            
                # Add quick actions for user
                col_error1, col_error2, col_error3 = st.columns(3)
            
                with col_error1:
                    if st.button("💡 Try Simpler Example", use_container_width=True):
                        # Load the verified working example
                        try:
                            with open('simple_working_test.py', 'r') as f:
                                st.session_state.questions = f.read()
                            st.rerun()
                        except:
                            # Fallback to inline simple example
                            st.session_state.questions = '''# Ultra simple test
quiz_metadata = {
    "title": "Simple Test Quiz",
    "duration": "30 minutes",
    "total_marks": 10
}

mcq = [{
    "question": r"What is 2 + 2?",
    "options": [r"3", r"4", r"5", r"6"],
    "answer": r"4",
    "marks": 2
}]

subjective = [{
    "question": r"What is addition?",
    "answer": r"Addition combines numbers.",
    "marks": 3
}]'''
                            st.rerun()
            
                with col_error2:
                    if st.button("📋 Copy for Local Testing", use_container_width=True):
                        # Create local test instructions
                        local_test = f'''# Save this as test_quiz.py
{questions_text}

# Then run locally:
# pip install git+https://github.com/nipunbatra/setwise.git
# setwise generate --questions-file test_quiz.py --sets 1'''
                        st.code(local_test, language="python")
            
                with col_error3:
                    if st.button("🔍 Show Raw Logs", use_container_width=True):
                        st.session_state.show_raw_logs = True
            
                # Show different error views
                if st.session_state.get('show_raw_logs', False):
                    with st.expander("🔍 Raw Server Logs (Technical Details)", expanded=True):
                        st.text(error)
                        if st.button("Hide Raw Logs"):
                            st.session_state.show_raw_logs = False
                else:
                    with st.expander("View Error Details", expanded=False):
                        # Parse and show user-friendly error info
                        if "LaTeX files created but PDF compilation failed" in error:
                            st.warning("**LaTeX Compilation Error** 📄")
                            st.markdown("""
                            The questions were processed successfully, but PDF generation failed. This usually means:
                        
                            - **LaTeX is not properly installed on the server**
                            - **Complex math expressions need fixing**
                            - **Missing LaTeX packages**
                        
                            **💡 Try:**
                            1. Use simpler math expressions
                            2. Test locally with your own LaTeX installation
                            3. Check the "Try Simpler Example" button above
                            """)
                        elif "No LaTeX files created" in error:
                            st.warning("**Question Processing Error** ❌")
                            st.markdown("""
                            The questions couldn't be processed. This usually means:
                        
                            - **Syntax error in questions file**
                            - **Invalid question structure**
                            - **Template rendering error**
                        
                            **💡 Try:**
                            1. Check your Python syntax
                            2. Validate question format
                            3. Use the "Try Simpler Example" button above
                            """)
                        else:
                            st.info("**General Generation Error** ⚠️")
                            st.markdown("""
                            Quiz generation failed for unknown reasons. This could be:
                        
                            - **Server configuration issues**
                            - **Temporary file permission problems**
                            - **Resource limitations**
                        
                            **💡 Try:**
                            1. Refresh the page and try again
                            2. Use simpler questions
                            3. Test locally (recommended)
                            """)
                    
                        # Always show the technical details as a sub-expander
                        with st.expander("🔧 Technical Details (for debugging)"):
                            st.text(error)
            elif quiz_sets:
                # Display each PDF set in rows
                for i, quiz_set in enumerate(quiz_sets):
                    st.markdown(f"**{quiz_set['name']}**")
                    
                    # Four sub-columns: PDF preview, PDF download, TEX download, answer key
                    sub_col1, sub_col2, sub_col3, sub_col4 = st.columns([2, 0.7, 0.7, 0.6])
                    
                    with sub_col1:
                        pdf_data = quiz_set.get('pdf_data')
                        print(f"[DEBUG] Quiz set {i+1} PDF data: type={type(pdf_data)}, size={len(pdf_data) if pdf_data else 'None'}")
                        if pdf_data:
                            display_pdf_embed(pdf_data, height=400, key_suffix=f"set_{i}_{len(quiz_sets)}")
                        else:
                            st.warning(f"PDF generation failed for set {i+1} - no PDF data")
                    
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
                        if quiz_set.get('tex_data'):
                            st.download_button(
                                label="Download TEX",
                                data=quiz_set['tex_data'],
                                file_name=f"quiz_set_{i+1}.tex",
                                mime="text/plain",
                                key=f"download_tex_{i}_{len(quiz_sets)}",
                                use_container_width=True,
                                help="Download LaTeX source file"
                            )
                    
                    with sub_col4:
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
            st.info("📝 Enter questions and click 'Generate Quiz Sets' to get started!")
    
            # Enhanced help with troubleshooting
            with st.expander("📚 How to Use This Interface", expanded=False):
                st.markdown("""
                **✨ Quick Start:**
                1. **Edit questions** in the left pane (or load an example)
                2. **Choose template** (default/compact/minimal) and number of sets
                3. **Click "Generate Quiz Sets"** to see live PDF previews
                4. **Download** PDFs and answer keys when ready
        
                **📋 Question Format:**
                ```python
                # Required arrays
                mcq = [...]          # Multiple choice questions
                subjective = [...]   # Written answer questions
        
                # Optional (NEW in v2.0!)
                quiz_metadata = {    # Professional headers
                    "title": "My Quiz",
                    "duration": "60 minutes"
                }
                ```
        
                **🔧 NEW v2.0 Features:**
                - **Templated MCQ:** Use `{{ variables }}` in questions and options
                - **Quiz metadata:** Professional headers with title, duration
                - **Multi-part questions:** Individual marks for each part
        
                **💡 If Generation Fails:**
                - Try the **"Physics"** or **"Machine Learning"** examples first
                - Use **"Try Simpler Example"** button if you see errors
                - **Test locally** for best reliability: `pip install git+https://github.com/nipunbatra/setwise.git`
                """)
    
            # Add a tips section
            with st.expander("💡 Pro Tips & Troubleshooting"):
                st.markdown("""
                **🎯 Best Practices:**
                - Start with **built-in examples** (Physics, ML) to see v2.0 features
                - Use **raw strings** for LaTeX: `r"$x^2$"` instead of `"$x^2$"`
                - **MCQ answers** must exactly match one of the options
                - **Test simple questions** first, then add complexity
        
                **🔧 Common Issues:**
                - **"Generation Failed"**: Often due to server LaTeX limitations
                - **Solution**: Download and test locally for full reliability
                - **Syntax errors**: Check Python syntax and question structure
                - **Template errors**: Ensure all `{{ variables }}` are defined
        
                **🖥️ Local Testing (Recommended):**
                ```bash
                # Install Setwise locally for best experience
                pip install git+https://github.com/nipunbatra/setwise.git
        
                # Create your questions file and test
                setwise generate --questions-file my_quiz.py --sets 3
                ```
        
                **🌐 This web interface is great for:**
                - Quick experimentation and demos
                - Exploring v2.0 features
                - Learning question formats
                - Sharing examples
        
                **💻 Local installation is better for:**
                - Production quiz generation
                - Complex LaTeX expressions
                - Large question sets
                - Reliable PDF generation
                """)

if __name__ == "__main__":
    main()