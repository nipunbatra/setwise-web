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
        "Enhanced Demo": '''# 🚀 Enhanced Setwise Demo - Showcasing Advanced Features!
quiz_metadata = {
    "title": "Advanced Math & Science Quiz",
    "subject": "Mathematics & Physics",
    "duration": "60 minutes", 
    "total_marks": 35,
    "instructions": ["Show all working", "Use appropriate units", "Round to 2 decimal places where needed"]
}

mcq = [
    {
        "question": r"What is the value of $\\pi$ (pi) rounded to 2 decimal places?",
        "options": [r"3.14", r"3.15", r"3.16", r"3.13"],
        "answer": r"3.14",
        "marks": 2
    },
    {
        "template": r"If a circle has radius {{ r }} cm, what is its area? (Use $\\pi = 3.14$)",
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
    },
    {
        "template": r"What is {{ a }} $\\times$ {{ b }}?",
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
    }
]

subjective = [
    {
        "template": r"A ball is thrown upward with initial velocity {{ v0 }} m/s.",
        "parts": [
            {
                "question": r"Calculate the maximum height reached (use $g = 9.8$ m/s$^2$)",
                "answer": r"$h = \\frac{v_0^2}{2g} = \\frac{{{ v0 }}^2}{2 \\times 9.8} = \\frac{{{ v0 * v0 }}}{19.6} = {{ (v0 * v0 / 19.6) | round(2) }}$ m",
                "marks": 4
            },
            {
                "question": r"How long does it take to reach maximum height?",
                "answer": r"$t = \\frac{v_0}{g} = \\frac{{{ v0 }}}{9.8} = {{ (v0 / 9.8) | round(2) }}$ seconds",
                "marks": 3
            }
        ],
        "variables": [
            {"v0": 20},
            {"v0": 30}
        ],
        "marks": 7
    },
    {
        "parts": [
            {
                "question": r"Define kinetic energy and write its formula.",
                "answer": r"Kinetic energy is the energy possessed by an object due to its motion. Formula: $KE = \\frac{1}{2}mv^2$",
                "marks": 3
            },
            {
                "question": r"A car of mass 1000 kg moves at 20 m/s. Calculate its kinetic energy.",
                "answer": r"$KE = \\frac{1}{2}mv^2 = \\frac{1}{2} \\times 1000 \\times 20^2 = \\frac{1}{2} \\times 1000 \\times 400 = 200,000$ J",
                "marks": 4
            },
            {
                "question": r"What happens to kinetic energy if velocity doubles?",
                "answer": r"If velocity doubles, kinetic energy increases by a factor of 4 (since KE $\\propto$ v$^2$)",
                "marks": 2
            }
        ],
        "marks": 9
    },
    {
        "template": r"A rectangle has length {{ length }} cm and width {{ width }} cm.",
        "parts": [
            {
                "question": r"Calculate the area.",
                "answer": r"Area = length $\\times$ width = {{ length }} $\\times$ {{ width }} = {{ length * width }} cm$^2$",
                "marks": 2
            },
            {
                "question": r"Calculate the perimeter.",
                "answer": r"Perimeter = 2(length + width) = 2({{ length }} + {{ width }}) = {{ 2 * (length + width) }} cm",
                "marks": 2
            },
            {
                "question": r"If we increase both dimensions by 50%, what is the new area?",
                "answer": r"New length = {{ length * 1.5 }} cm, new width = {{ width * 1.5 }} cm. New area = {{ length * 1.5 }} $\\times$ {{ width * 1.5 }} = {{ (length * width * 2.25) }} cm$^2$",
                "marks": 3
            }
        ],
        "variables": [
            {"length": 12, "width": 8},
            {"length": 15, "width": 10}
        ],
        "marks": 7
    }
]''',
        "Physics": '''# Quiz metadata for professional headers
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
        "template": r"A ball is dropped from height {{ h }} m. What is its velocity just before hitting the ground? (g = 9.8 m/s$^2$)",
        "options": [
            r"$\\sqrt{2g \\times {{ h }}}$ $\\approx$ {{ velocity:.1f }} m/s",
            r"$g \\times {{ h }}$ = {{ h * 9.8 }} m/s", 
            r"$\\frac{g \\times {{ h }}}{2}$ = {{ h * 4.9 }} m/s",
            r"$2g \\times {{ h }}$ = {{ 2 * h * 9.8 }} m/s"
        ],
        "answer": r"$\\sqrt{2g \\times {{ h }}}$ $\\approx$ {{ velocity:.1f }} m/s",
        "variables": [
            {"h": 20, "velocity": 19.8},
            {"h": 45, "velocity": 29.7},
            {"h": 80, "velocity": 39.6}
        ],
        "marks": 3
    },
    {
        "template": r"Calculate kinetic energy: KE = $\\frac{1}{2}$mv$^2$ with m = {{ mass }} kg and v = {{ velocity }} m/s",
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
        "template": r"A projectile is launched with initial velocity {{ v0 }} m/s at angle {{ angle }}$^\\circ$. Calculate the maximum height and range.",
        "answer": r"Maximum height: $H = \\frac{({{ v0 }} \\sin {{ angle }}^\\circ)^2}{2g}$ m. Range: $R = \\frac{{{ v0 }}^2 \\sin(2 \\times {{ angle }}^\\circ)}{g}$ m.",
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
        "Machine Learning": '''# Machine Learning quiz with advanced features
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
        example = st.selectbox("Examples", ["", "Enhanced Demo", "Physics", "Machine Learning"])
    
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
            st.session_state.questions = '''# Simple Demo Quiz
quiz_metadata = {
    "title": "Math Quiz",
    "subject": "Mathematics",
    "duration": "30 minutes", 
    "total_marks": 10,
    "instructions": ["Show your work", "Use proper units"]
}

mcq = [
    {
        "question": r"What is 2 + 2?",
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
            {"a": 3, "b": 4},
            {"a": 5, "b": 2}
        ],
        "marks": 3
    }
]

subjective = [
    {
        "question": r"Multi-part Problem:",
        "parts": [
            {
                "question": r"What is 15 + 25?",
                "answer": r"15 + 25 = 40",
                "marks": 2
            },
            {
                "question": r"Explain why addition works this way.",
                "answer": r"Addition combines quantities together to get the total.",
                "marks": 3
            }
        ],
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