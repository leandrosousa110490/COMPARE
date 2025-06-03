# Modern Text Comparison Tool

A powerful, real-time text comparison application with two versions: a tkinter-based version and an advanced PyQt5 version with syntax highlighting. Both provide instant, character-by-character analysis of two text inputs with modern, dark-themed user interfaces.

## Versions Available

### 📁 tkinter Version (`text_compare_app.py`)
The original version using Python's built-in tkinter library.

### 🎨 PyQt5 Version (`text_compare_app_pyqt.py`) - **Recommended**
Advanced version with real-time syntax highlighting and enhanced visual feedback.

## Features

### 🚀 Real-time Comparison
- **Instant Analysis**: Compare texts as you type with zero delay
- **Live Updates**: Results update automatically when either text changes
- **Responsive Interface**: Smooth performance even with large text inputs
- **Real-time Highlighting**: (PyQt5 version) Live syntax highlighting as you type

### 📂 File Operations (PyQt5 version)
- **File Import**: Load text from files directly into either text area
- **File Export**: Save comparison results to a text file
- **Drag & Drop**: Drag text files directly into either text area
- **Recent Files**: Quick access to recently opened files


### 🎯 Accuracy & Detail
- **Character-by-Character Analysis**: Precise comparison down to individual characters
- **Similarity Percentage**: Accurate calculation of text similarity
- **Comprehensive Statistics**: Character counts, matching characters, and difference counts
- **Special Character Handling**: Proper display of spaces, newlines, tabs, and control characters

### 🎨 Modern UI Design
- **Dark Theme**: Easy on the eyes with a professional dark interface
- **Advanced Highlighting** (PyQt5 version):
  - 🟢 **Light Green Background**: Added text (insertions)
  - 🔴 **Light Red Background**: Deleted text (deletions) with strikethrough
  - 🟠 **Light Orange Background**: Modified text (replacements)
  - **Underlines and Strikethrough**: Additional visual cues for changes
- **Color-Coded Results**: 
  - 🟢 **Green**: Matching characters and identical content
  - 🔴 **Red**: Deleted characters (present in Text 1 but not Text 2)
  - 🔵 **Blue**: Added characters (present in Text 2 but not Text 1)
  - 🟡 **Yellow**: Headers and section dividers
- **Clean Layout**: Intuitive design with clear sections and proper spacing
- **Status Updates**: Real-time status bar showing comparison progress

### 📊 Detailed Analysis
- **Multiple View Modes**: 
  - Summary statistics
  - Character-by-character comparison table
- **Position Tracking**: Exact character positions for all differences
- **Match Status**: Clear indicators for each character comparison

## Installation

### Prerequisites
- Python 3.6 or higher
- tkinter (usually included with Python)
- PyQt5 (for the advanced version)

### Setup
1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   Or install PyQt5 manually:
   ```bash
   pip install PyQt5>=5.15.0
   ```

3. Run either version:
   ```bash
   # tkinter version (no additional dependencies)
   python text_compare_app.py
   
   # PyQt5 version (recommended - advanced highlighting)
   python text_compare_app_pyqt.py
   ```

## Usage

### PyQt5 Version
1. **Launch the application**:
   ```bash
   python text_compare_app_pyqt.py
   ```

2. **Use the enhanced features**:
   - **File Operations**: Use the toolbar buttons or keyboard shortcuts:
     - Open File 1 (Ctrl+1): Load text into the first panel
     - Open File 2 (Ctrl+2): Load text into the second panel
     - Save Results (Ctrl+S): Export comparison results to a file
   - **Drag & Drop**: Drag text files directly into either text area
   - **Recent Files**: Access recently opened files from the Recent Files menu in the toolbar
   - **Clear Buttons**: Each section (Text 1, Text 2, Results) has a clear button to quickly erase content

3. **Enter your texts**:
   - Type or paste text in the left panel (Text 1)
   - Type or paste text in the right panel (Text 2)

4. **View results instantly**:
   - The comparison results appear automatically below
   - Character-by-character differences are highlighted in real-time
   - Similarity percentage updates as you type

4. **Search for Differences**:
   

### tkinter Version
1. **Launch the application**:
   ```bash
   python text_compare_app.py
   ```

2. **Enter your texts**:
   - Type or paste text in the left panel (Text 1)
   - Type or paste text in the right panel (Text 2)

3. **View results instantly**:
   - The comparison results appear automatically below
   - Character-by-character differences are highlighted in real-time
   - Similarity percentage updates as you type

## Understanding the Results

#### Color Coding
- 🟢 **Green**: Matching text segments
- 🔴 **Red**: Different/deleted text from Text 1
- 🔵 **Blue**: Inserted/added text in Text 2
- 🟡 **Orange**: Deleted text segments

#### Result Sections
1. **Statistics Header**: Shows similarity percentage and character counts
2. **Detailed Comparison**: Lists all differences with operation types
3. **Character-by-Character View**: Position-by-position analysis table

#### Special Character Display
- `(sp)` - Space character
- `(nl)` - Newline character
- `(tab)` - Tab character
- `(cr)` - Carriage return
- `(#XX)` - Control characters (shown as ASCII code)
- `(end)` - End of text marker

## Examples

### Example 1: Simple Text Difference
**Text 1**: `Hello World`
**Text 2**: `Hello World!`

**Result**: Shows that an exclamation mark was added at the end

### Example 2: Character Substitution
**Text 1**: `The quick brown fox`
**Text 2**: `The quick brown cat`

**Result**: Shows "fox" was replaced with "cat"

### Example 3: Whitespace Differences
**Text 1**: `Hello World`
**Text 2**: `Hello  World` (extra space)

**Result**: Detects and highlights the extra space character

## Technical Details

### Algorithm
- Uses Python's `difflib.SequenceMatcher` for accurate text comparison
- Implements character-level diff analysis
- Real-time processing with minimal latency

### Performance
- Optimized for real-time use
- Handles texts up to several thousand characters efficiently
- Minimal memory footprint

### Compatibility
- Works on Windows, macOS, and Linux
- Compatible with Python 3.6+
- Uses standard library only (no external dependencies)

## Customization

### Modifying Colors
Edit the `setup_text_tags()` method in the code to change highlight colors:

```python
self.results_text.tag_configure('match', background='#2d5a2d', foreground='#90ee90')
self.results_text.tag_configure('diff', background='#5a2d2d', foreground='#ff6b6b')
```

### Changing Fonts
Modify the font settings in the `create_widgets()` method:

```python
font=('Consolas', 11)  # Change font family and size
```

### Window Size
Adjust the initial window size in `setup_window()`:

```python
self.root.geometry("1000x600")  # Width x Height
```

## Troubleshooting

### Common Issues

**App doesn't start**
- Ensure Python 3.6+ is installed
- Check that tkinter is available: `python -c "import tkinter"`

**Text not updating**
- Try clicking in the text box after typing
- Ensure both text boxes have focus capability

**Display issues**
- Try resizing the window
- Check your system's display scaling settings

### Performance Tips
- For very large texts (>10,000 characters), consider breaking them into smaller chunks
- Close other resource-intensive applications for optimal performance

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the application.

---

**Enjoy comparing texts with precision and style!** 🎯✨