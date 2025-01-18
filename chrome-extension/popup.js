class ResumeGPTExtension {
    constructor() {
        this.API_URL = 'http://localhost:5000/api';
        this.resumeData = null;
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
    }
    
    setupDragAndDrop() {
        const dropZone = document.getElementById('dropZone');
        
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('drag-over');
        });
        
        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('drag-over');
        });
        
        dropZone.addEventListener('drop', async (e) => {
            e.preventDefault();
            dropZone.classList.remove('drag-over');
            
            const file = e.dataTransfer.files[0];
            await this.processFile(file);
        });
    }
    
    async processFile(file) {
        console.log("Processing file:", file.name);
        const reader = new FileReader();
        return new Promise((resolve, reject) => {
            reader.onload = async (e) => {
                try {
                    const content = e.target.result;
                    // Parse YAML content into JSON object
                    const parsedResume = this.parseResumeContent(content);
                    this.resumeData = {
                        name: parsedResume.name || "",
                        skills: parsedResume.skills || [],
                        experience: parsedResume.experience || [],
                        education: parsedResume.education || []
                    };
                    console.log("Parsed resume data:", this.resumeData);
                    await this.checkJobPage();
                    resolve();
                } catch (error) {
                    console.error("Error processing file:", error);
                    reject(error);
                }
            };
            reader.onerror = (error) => reject(error);
            reader.readAsText(file);
        });
    }

    parseResumeContent(content) {
        // Simple YAML-like parser
        const lines = content.split('\n');
        const resume = {
            name: '',
            skills: [],
            experience: [],
            education: []
        };

        let currentSection = '';
        let currentItem = null;

        for (let line of lines) {
            line = line.trim();
            if (!line) continue;

            // Remove YAML markers
            if (line.startsWith('- ')) {
                line = line.substring(2);
            }

            // Extract name (usually first line)
            if (!resume.name && !line.toLowerCase().includes('education') && !line.toLowerCase().includes('experience')) {
                resume.name = line;
                continue;
            }

            // Detect sections
            if (line.toLowerCase().includes('education')) {
                currentSection = 'education';
                continue;
            } else if (line.toLowerCase().includes('experience')) {
                currentSection = 'experience';
                continue;
            } else if (line.toLowerCase().includes('skills')) {
                currentSection = 'skills';
                continue;
            }

            // Process content based on section
            if (currentSection === 'skills') {
                if (line.includes(':')) {
                    const [, skillList] = line.split(':');
                    resume.skills = skillList.split(',').map(s => s.trim());
                }
            } else if (currentSection === 'experience') {
                if (line.includes('•')) {
                    if (currentItem) {
                        currentItem.description = (currentItem.description || '') + ' ' + line.substring(1).trim();
                    }
                } else if (line.includes('–') || line.includes('-')) {
                    if (currentItem) {
                        resume.experience.push(currentItem);
                    }
                    const [title, company] = line.split('–')[0].split('@').map(s => s.trim());
                    currentItem = {
                        title: title,
                        company: company || '',
                        description: ''
                    };
                }
            } else if (currentSection === 'education') {
                if (!line.includes('•')) {
                    resume.education.push({
                        degree: line,
                        school: '',
                        description: ''
                    });
                }
            }
        }

        // Add last experience item if exists
        if (currentItem) {
            resume.experience.push(currentItem);
        }

        return resume;
    }

    async tailorResume() {
        if (!this.resumeData) {
            alert('Please upload a resume first.');
            return;
        }

        try {
            const jobHtml = await this.getJobHtml();
            if (!jobHtml || !jobHtml.description) {
                throw new Error('Failed to extract job details.');
            }

            // Log the exact data we're sending
            const requestData = {
                jobHtml: jobHtml.description,
                resumeData: this.resumeData
            };
            console.log('Request Data:', JSON.stringify(requestData, null, 2));

            document.getElementById('tailorResume').disabled = true;
            document.getElementById('status').textContent = 'Tailoring resume...';
            
            const response = await fetch(`${this.API_URL}/tailor-resume`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(requestData)
            });

            console.log('Response status:', response.status);
            const responseText = await response.text();
            console.log('Response text:', responseText);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}, message: ${responseText}`);
            }
            
            const result = JSON.parse(responseText);
            console.log('Parsed result:', result);

            if (result.success) {
                this.displayTailoredResume(result.data.tailored_resume);
                document.getElementById('status').textContent = 'Resume tailored successfully!';
                document.getElementById('status').className = 'success';
            } else {
                throw new Error(result.error || 'Failed to tailor resume');
            }
        } catch (error) {
            console.error('Detailed error:', error);
            document.getElementById('status').textContent = `Error: ${error.message}`;
            document.getElementById('status').className = 'error';
        } finally {
            this.checkJobPage();
        }
    }

    async getJobHtml() {
        console.log("Getting job HTML...");
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        
        try {
            // Execute script to get job description
            const result = await chrome.scripting.executeScript({
                target: { tabId: tab.id },
                function: () => {
                    // Get job details from the page
                    const selectors = {
                        linkedin: '.jobs-description__content',
                        indeed: '#jobDescriptionText',
                        glassdoor: '.jobDescriptionContent',
                        monster: '.job-description',
                        default: '[data-test="job-description"]'
                    };
                    
                    // Try all selectors
                    for (const selector of Object.values(selectors)) {
                        const element = document.querySelector(selector);
                        if (element) {
                            return {
                                description: element.innerHTML,
                                title: document.title,
                                url: window.location.href
                            };
                        }
                    }
                    
                    return null;
                }
            });
            
            console.log("Job HTML retrieved:", result[0]?.result);
            return result[0]?.result;
        } catch (error) {
            console.error("Error getting job HTML:", error);
            return null;
        }
    }

    displayTailoredResume(data) {
        const tailoredResumeDiv = document.getElementById('tailoredResume');
        tailoredResumeDiv.innerHTML = `
            <h2>${data.name}</h2>
            <p><strong>Skills:</strong> ${data.skills.join(', ')}</p>
            <div id="resumeContent">
                <h3>Experience</h3>
                ${data.experience.map(exp => `<p><strong>${exp.title}</strong> at <strong>${exp.company}</strong><br>${exp.description}</p>`).join('')}
                <h3>Education</h3>
                ${data.education.map(edu => `<p><strong>${edu.degree}</strong> at <strong>${edu.school}</strong><br>${edu.description}</p>`).join('')}
            </div>
            <button id="downloadResume">Download Tailored Resume</button>
        `;
        tailoredResumeDiv.style.display = 'block';
        
        // Add download handler
        document.getElementById('downloadResume').addEventListener('click', () => {
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'tailored_resume.json';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        });
        
        // Enable Preview and Edit buttons
        document.getElementById('togglePreview').disabled = false;
        document.getElementById('editResume').disabled = false;
        document.getElementById('saveEdits').disabled = false;
    }

    togglePreview() {
        const tailoredResumeDiv = document.getElementById('tailoredResume');
        styledResumeDiv.classList.toggle('preview');
        // Implement actual preview toggling logic as needed
    }

    enableEditing() {
        const tailoredResumeDiv = document.getElementById('tailoredResume');
        tailoredResumeDiv.classList.add('editing');
        
        // Make content editable
        const resumeContent = document.getElementById('resumeContent');
        resumeContent.contentEditable = true;
        resumeContent.classList.add('editable');
    }

    saveEdits() {
        const tailoredResumeDiv = document.getElementById('tailoredResume');
        tailoredResumeDiv.classList.remove('editing');
        
        // Make content non-editable
        const resumeContent = document.getElementById('resumeContent');
        resumeContent.contentEditable = false;
        resumeContent.classList.remove('editable');
        
        // Optionally, send the edited resume back to the backend for saving
        alert('Edits saved successfully!');
    }

    async checkJobPage() {
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            const tab = tabs[0];
            const url = tab.url;
            console.log("Checking job page for URL:", url);
            
            // Enhanced regex to cover more job posting URL patterns
            const jobPagePatterns = [
                /linkedin\.com\/jobs\//,
                /indeed\.com\/viewjob/,
                /glassdoor\.com\/job-listing/,
                /monster\.com\/job/,
                /careerbuilder\.com\/job/
            ];
            
            const isJobPage = jobPagePatterns.some(pattern => pattern.test(url));
            
            console.log("Is job page:", isJobPage);
            
            const tailorButton = document.getElementById('tailorResume');
            if (isJobPage && this.resumeData) {
                tailorButton.disabled = false;
                console.log("Tailor button enabled");
            } else {
                tailorButton.disabled = true;
                console.log("Tailor button disabled. Resume data:", !!this.resumeData);
            }
        });
    }

    async handleFileUpload(event) {
        console.log("File upload triggered");
        const file = event.target.files[0];
        if (file) {
            document.getElementById('status').textContent = 'Processing resume...';
            document.getElementById('status').className = '';
            try {
                await this.processFile(file);
                document.getElementById('status').textContent = 'Resume uploaded successfully.';
                document.getElementById('status').className = 'success';
                this.checkJobPage();
            } catch (error) {
                document.getElementById('status').textContent = `Error processing file: ${error.message}`;
                document.getElementById('status').className = 'error';
                console.error("File Upload Error:", error);
            }
        }
    }
}

// Initialize the extension
document.addEventListener('DOMContentLoaded', () => {
    console.log("Extension loaded");
    new ResumeGPTExtension();
}); 