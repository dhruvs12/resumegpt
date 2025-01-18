# ResumeGPT

An AI-powered Chrome extension that automatically tailors your resume to job descriptions using Google's Gemini AI.

## Features

- Automatically extracts job descriptions from popular job sites
- Parses YAML/JSON formatted resumes
- Uses AI to tailor your resume to specific job requirements
- Real-time resume preview and editing
- Download tailored resumes in multiple formats

## Installation

### Backend Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/resumegpt.git
   cd resumegpt
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv env
   
   # On macOS/Linux
   source env/bin/activate
   
   # On Windows
   env\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -e .
   ```

4. Create a `.env` file with your API keys:
   ```env
   GOOGLE_API_KEY=your_api_key_here
   GEMINI_API_KEY=your_api_key_here
   GEMINI_MODEL_NAME=gemini-1.5-pro
   GEMINI_TEMPERATURE=0.7
   ```

### Chrome Extension Setup

1. Open Chrome and navigate to `chrome://extensions/`.
2. Enable "Developer mode."
3. Click "Load unpacked" and select the `chrome-extension` directory.

## Usage

1. Navigate to a job posting on a supported job site.
2. Click the ResumeGPT extension icon.
3. Upload your resume (YAML/JSON format).
4. Click "Tailor Resume."
5. Review, edit, and download the tailored resume.

## Development

### Backend Development
```bash
python -m resumegpt.app
```

### Extension Development
Load the unpacked extension in Chrome's developer mode.

## Contributing

1. Fork the repository.
2. Create your feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

MIT License

Copyright (c) 2024 Dhruv Singh

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

