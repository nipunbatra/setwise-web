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
        "Ultimate Demo": '''# 🚀 Ultimate Setwise Demo - All Features Showcase
# Templated questions, multi-part problems, matrices, chemistry, circuits, SI units, tables, plots
quiz_metadata = {
    "title": "Ultimate Setwise Demo Quiz",
    "subject": "Science & Engineering",
    "duration": "90 minutes",
    "total_marks": 50,
    "instructions": ["Show all working clearly", "Use appropriate units", "Include diagrams where helpful"]
}

mcq = [
    {
        "template": r"Calculate {{ a }} $\\times$ {{ b }} = ?",
        "options": [
            r"{{ a * b }}",
            r"{{ a + b }}",
            r"{{ a - b }}",
            r"{{ (a * b) + 1 }}"
        ],
        "answer": r"{{ a * b }}",
        "variables": [
            {"a": 12, "b": 8},
            {"a": 15, "b": 6},
            {"a": 9, "b": 11}
        ],
        "marks": 2
    },
    {
        "question": r"""
Consider the matrix:
\\begin{equation}
A = \\begin{pmatrix}
3 & 1 \\\\
2 & 4
\\end{pmatrix}
\\end{equation}
What is $\\det(A)$?""",
        "options": [r"10", r"12", r"14", r"8"],
        "answer": r"10",
        "marks": 3
    },
    {
        "question": r"""
The RC circuit shown has time constant:
\\begin{center}
\\begin{circuitikz}[scale=0.8]
\\draw (0,0) to[V, l=$V_0$] (0,2) to[R, l=\\SI{10}{\\kilo\\ohm}] (3,2) to[C, l=\\SI{100}{\\micro\\farad}] (3,0) -- (0,0);
\\end{circuitikz}
\\end{center}
What is $\\tau$?""",
        "options": [r"\\SI{1}{\\second}", r"\\SI{0.1}{\\second}", r"\\SI{10}{\\second}", r"\\SI{0.01}{\\second}"],
        "answer": r"\\SI{1}{\\second}",
        "marks": 4
    },
    {
        "template": r"If a circle has radius {{ r }} cm, what is its area using $\\pi = 3.14$?",
        "options": [
            r"${{ 3.14 * r * r }}$ cm$^2$",
            r"${{ 2 * 3.14 * r }}$ cm$^2$",
            r"${{ 3.14 * r }}$ cm$^2$",
            r"${{ r * r }}$ cm$^2$"
        ],
        "answer": r"${{ 3.14 * r * r }}$ cm$^2$",
        "variables": [
            {"r": 5},
            {"r": 7},
            {"r": 10}
        ],
        "marks": 3
    }
]

subjective = [
    {
        "template": r"Physics Problem - Projectile with velocity {{ v0 }} m/s at 30°:",
        "parts": [
            {
                "question": r"Calculate maximum height (use $g = \\SI{9.8}{\\meter\\per\\second\\squared}$).",
                "answer": r"$h = \\frac{(v_0 \\sin\\theta)^2}{2g} = \\frac{({{ v0 }} \\times 0.5)^2}{19.6} = {{ (v0 * 0.5)**2 / 19.6 | round(1) }}$ m",
                "marks": 4
            },
            {
                "question": r"Find the time of flight.",
                "answer": r"$t = \\frac{2v_0 \\sin\\theta}{g} = \\frac{2 \\times {{ v0 }} \\times 0.5}{9.8} = {{ v0 / 9.8 | round(2) }}$ s",
                "marks": 3
            }
        ],
        "variables": [
            {"v0": 20},
            {"v0": 25}
        ],
        "marks": 7
    },
    {
        "question": r"""
Chemical Analysis - Consider ethanol:
\\begin{center}
\\chemfig{H-C(-[2]H)(-[6]H)-C(-[2]H)(-[6]H)-OH}
\\end{center}""",
        "parts": [
            {
                "question": r"What is the molecular formula?",
                "answer": r"C$_2$H$_6$O (or C$_2$H$_5$OH)",
                "marks": 2
            },
            {
                "question": r"Calculate molar mass using C=12, H=1, O=16.",
                "answer": r"Molar mass = $2 \\times 12 + 6 \\times 1 + 1 \\times 16 = 46$ g/mol",
                "marks": 3
            }
        ],
        "marks": 5
    },
    {
        "question": r"""
Data Analysis - Material Properties:
\\begin{center}
\\begin{tabular}{|l|c|c|}
\\hline
\\textbf{Material} & \\textbf{Density} & \\textbf{Strength} \\\\
& \\textbf{(g/cm³)} & \\textbf{(MPa)} \\\\
\\hline
Steel & 7.85 & 250 \\\\
\\hline
Aluminum & 2.70 & 95 \\\\
\\hline
Carbon Fiber & 1.60 & 1200 \\\\
\\hline
\\end{tabular}
\\end{center}""",
        "parts": [
            {
                "question": r"Calculate specific strength (strength/density) for carbon fiber.",
                "answer": r"Specific strength = $\\frac{1200}{1.60} = 750$ MPa·cm³/g",
                "marks": 3
            },
            {
                "question": r"Why is carbon fiber preferred for aerospace?",
                "answer": r"Carbon fiber has the highest specific strength (750 vs 32 for steel), providing maximum strength with minimum weight.",
                "marks": 2
            }
        ],
        "marks": 5
    },
    {
        "question": r"""
Matrix Operations:
\\begin{equation}
A = \\begin{pmatrix} 2 & 1 \\\\ 1 & 3 \\end{pmatrix}, \\quad \\mathbf{b} = \\begin{pmatrix} 5 \\\\ 8 \\end{pmatrix}
\\end{equation}""",
        "parts": [
            {
                "question": r"Calculate $\\det(A)$.",
                "answer": r"$\\det(A) = 2 \\times 3 - 1 \\times 1 = 5$",
                "marks": 2
            },
            {
                "question": r"Solve $A\\mathbf{x} = \\mathbf{b}$ for $x_1$.",
                "answer": r"Using Cramer's rule: $x_1 = \\frac{\\det(A_1)}{\\det(A)} = \\frac{7}{5} = 1.4$",
                "marks": 4
            }
        ],
        "marks": 6
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
            # Parse existing questions to see if quiz_metadata exists
            questions_lines = questions_text.split('\n')
            has_quiz_metadata = any('quiz_metadata' in line for line in questions_lines)
            
            if header_config and any(header_config.values()):
                # User has provided header customization
                if has_quiz_metadata:
                    # Replace existing quiz_metadata with custom values
                    full_content = questions_text
                    # Find and replace the quiz_metadata section
                    import re
                    pattern = r'quiz_metadata\s*=\s*\{[^}]*\}'
                    
                    custom_metadata = "quiz_metadata = {\n"
                    if header_config.get('title'):
                        custom_metadata += f'    "title": "{header_config["title"]}",\n'
                    if header_config.get('subject'):
                        custom_metadata += f'    "subject": "{header_config["subject"]}",\n'
                    if header_config.get('exam_info'):
                        custom_metadata += f'    "duration": "{header_config["exam_info"]}",\n'
                    custom_metadata += '    "total_marks": 100\n}'
                    
                    full_content = re.sub(pattern, custom_metadata, full_content, flags=re.DOTALL)
                else:
                    # Add quiz_metadata at the beginning
                    metadata_header = "# Custom Quiz Metadata\n"
                    metadata_header += "quiz_metadata = {\n"
                    if header_config.get('title'):
                        metadata_header += f'    "title": "{header_config["title"]}",\n'
                    if header_config.get('subject'):
                        metadata_header += f'    "subject": "{header_config["subject"]}",\n'
                    if header_config.get('exam_info'):
                        metadata_header += f'    "duration": "{header_config["exam_info"]}",\n'
                    metadata_header += '    "total_marks": 100\n}\n\n'
                    
                    full_content = metadata_header + questions_text
            else:
                full_content = questions_text
            
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
    st.markdown("Generate professional LaTeX quizzes with dynamic templated questions")
    
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
        example = st.selectbox("Examples", ["", "Ultimate Demo"])
    
    with col_ctrl4:
        if st.button("Load Example", disabled=not example):
            st.session_state.questions = load_example_questions(example)
            st.rerun()
    
    # Header customization - simplified
    with st.expander("Quiz Header Customization"):
        col_header1, col_header2, col_header3 = st.columns([1, 1, 1])
        
        with col_header1:
            quiz_title = st.text_input("Quiz Title", value="Quiz")
        
        with col_header2:
            subject_name = st.text_input("Subject", value="")
        
        with col_header3:
            exam_info = st.text_input("Duration/Info", value="")
        
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
        
        if 'questions' not in st.session_state:
            st.session_state.questions = '''# Simple Demo Quiz - Load "Ultimate Demo" to see all features!
quiz_metadata = {
    "title": "Simple Math Quiz",
    "subject": "Mathematics",
    "duration": "30 minutes", 
    "total_marks": 15
}

mcq = [
    {
        "question": r"What is $2 + 2$?",
        "options": [r"3", r"4", r"5", r"6"],
        "answer": r"4",
        "marks": 2
    },
    {
        "template": r"Calculate: {{ a }} $\\times$ {{ b }} = ?",
        "options": [
            r"{{ a * b }}",
            r"{{ a + b }}", 
            r"{{ a - b }}",
            r"{{ a }}"
        ],
        "answer": r"{{ a * b }}",
        "variables": [
            {"a": 6, "b": 7},
            {"a": 8, "b": 9}
        ],
        "marks": 3
    }
]

subjective = [
    {
        "question": r"Multi-part Problem:",
        "parts": [
            {
                "question": r"What is $15 + 25$?",
                "answer": r"$15 + 25 = 40$",
                "marks": 3
            },
            {
                "question": r"Explain how addition works.",
                "answer": r"Addition combines quantities together to find the total sum.",
                "marks": 4
            }
        ],
        "marks": 7
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
                st.error("Quiz Generation Failed")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Try Enhanced Demo", use_container_width=True):
                        st.session_state.questions = load_example_questions("Enhanced Demo")
                        st.rerun()
                
                with col2:
                    if st.button("Show Error Details", use_container_width=True):
                        st.session_state.show_raw_logs = True
            
                # Simplified error display
                with st.expander("View Error Details"):
                    if "LaTeX files created but PDF compilation failed" in error:
                        st.warning("LaTeX compilation failed - try simpler expressions or test locally")
                    elif "No LaTeX files created" in error:
                        st.warning("Question processing failed - check Python syntax")
                    else:
                        st.warning("Generation failed - try simpler questions or test locally")
                    
                    if st.session_state.get('show_raw_logs', False):
                        st.text(error)
                        if st.button("Hide Raw Logs"):
                            st.session_state.show_raw_logs = False
                    else:
                        if st.button("Show Technical Details"):
                            st.session_state.show_raw_logs = True
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
    
            with st.expander("📚 Quick Help"):
                st.markdown("""
                **Quick Start:**
                1. Edit questions or load an example
                2. Choose template and number of sets  
                3. Click "Generate Quiz Sets"
                4. Download PDFs and answer keys
        
                **Question Format:**
                ```python
                mcq = [...]          # Multiple choice questions
                subjective = [...]   # Written answer questions
                quiz_metadata = {    # Optional headers
                    "title": "My Quiz",
                    "duration": "60 minutes"
                }
                ```
        
                **Features:**
                - Templated questions with `{{ variables }}`
                - Multi-part subjective questions
                - Professional PDF output
                """) 
            
            with st.expander("💡 Troubleshooting"):
                st.markdown("""
                **If generation fails:**
                - Try the "Enhanced Demo" example first
                - Use simpler questions
                - Test locally: `pip install git+https://github.com/nipunbatra/setwise.git`
                
                **Common fixes:**
                - Check Python syntax
                - Ensure MCQ answers match options exactly
                - Use raw strings for LaTeX: `r"$x^2$"`
                """)

if __name__ == "__main__":
    main()