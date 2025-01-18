class ResumeGPTExtension {
    constructor() {
        this.API_URL = 'http://localhost:5000/api';
        this.resumeData = null;
        this.tailoredResume = null;
        this.setupEventListeners();
        this.setupDragAndDrop();
        this.checkJobPage();
    }

    setupEventListeners() {
        document.getElementById('resumeUpload').addEventListener('change', this.handleFileUpload.bind(this));
        document.getElementById('tailorResume').addEventListener('click', this.tailorResume.bind(this));
        
        // Add preview toggle
        document.getElementById('togglePreview').addEventListener('click', this.togglePreview.bind(this));
        
        // Add manual adjustments
        document.getElementById('editResume').addEventListener('click', this.enableEditing.bind(this));
        document.getElementById('saveEdits').addEventListener('click', this.saveEdits.bind(this));
        
        // Add download button listeners
        document.getElementById('downloadJSON').addEventListener('click', () => this.downloadResume('json'));
        document.getElementById('downloadPDF').addEventListener('click', () => this.downloadResume('pdf'));
    }

    // ... other methods ...

    downloadResume(format) {
        try {
            console.log('Initiating download:', format);
            if (!this.tailoredResume) {
                throw new Error('No tailored resume available to download.');
            }
            console.log('Tailored resume data:', this.tailoredResume);

            if (format === 'json') {
                const jsonData = {
                    tailored_resume: this.tailoredResume.tailored_resume || {},
                    match_score: this.tailoredResume.match_score || 0,
                    improvements: this.tailoredResume.improvements || []
                };
                const blob = new Blob([JSON.stringify(jsonData, null, 2)], { type: 'application/json' });
                this.downloadBlob(blob, 'tailored_resume.json');
            } else if (format === 'pdf') {
                this.generatePDF();
            }
        } catch (error) {
            console.error('Download error:', error);
            document.getElementById('status').textContent = `Error: ${error.message}`;
            document.getElementById('status').className = 'error';
        }
    }

    downloadBlob(blob, filename) {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        
        a.click(); // <-- Trigger the download
        
        document.body.removeChild(a); // <-- Clean up
        URL.revokeObjectURL(url);
    }

    generatePDF() {
        try {
            const { jsPDF } = window.jspdf;
            const doc = new jsPDF();
            const resumeContent = document.getElementById('resumeContent').innerText;

            doc.text(resumeContent, 10, 10);
            doc.save('tailored_resume.pdf');
        } catch (error) {
            console.error('PDF generation error:', error);
            document.getElementById('status').textContent = `Error: ${error.message}`;
            document.getElementById('status').className = 'error';
        }
    }

    // ... other methods ...
} 