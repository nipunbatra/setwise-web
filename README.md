# Setwise Web Interface

Professional LaTeX quiz generator with live preview, built with Streamlit.

## Features

- **Split-pane editor**: Questions on left, PDF previews on right
- **Live PDF generation**: Real-time preview with LaTeX rendering
- **Multiple quiz sets**: Generate 1-5 randomized quiz variations
- **Answer keys**: Automatic generation with downloads
- **Example libraries**: Physics, Mathematics, Programming questions
- **Professional templates**: Default, compact, and minimal layouts

## Quick Start

The app is deployed on Streamlit Cloud: **[Launch Setwise Web App](https://setwise-web.streamlit.app)**

## Local Development

```bash
git clone https://github.com/nipunbatra/setwise-web.git
cd setwise-web
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Usage

1. **Edit questions** in the left pane using Python format
2. **Choose template** and number of sets
3. **Click "Generate Quiz Sets"** to see live previews
4. **Download PDFs** and answer keys for each set

### Question Format

```python
mcq = [
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
]
```

## Randomization

Generate multiple sets to see:
- **Question order shuffling** between sets
- **Option order randomization** within MCQs
- **Consistent answer tracking** across variations

## Core Package

This web interface uses the [Setwise](https://github.com/nipunbatra/setwise) core package for quiz generation.

## License

MIT License - see main [Setwise repository](https://github.com/nipunbatra/setwise) for details.