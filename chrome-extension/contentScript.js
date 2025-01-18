// Portal-specific selectors
const PORTAL_SELECTORS = {
    'linkedin.com': {
        title: '.topcard__title, .jobs-unified-top-card__job-title',
        description: '.show-more-less-html__markup, .jobs-description__content',
        skills: '.jobs-description-section__word-tag'
    },
    'indeed.com': {
        title: '.jobsearch-JobInfoHeader-title, h1.jobsearch-JobInfoHeader-title',
        description: '#jobDescriptionText, .jobsearch-jobDescriptionText',
        skills: '.jobsearch-KeywordsBar-keywords, .jobsearch-JobComponent-icon'
    },
    'glassdoor.com': {
        title: '.css-17x2pwl, .jobHeader__title',
        description: '.jobDescription__container, .desc',
        skills: '.jobDescription__skill, .css-1aw0on9'
    }
};

function getPortalSelectors() {
    const hostname = window.location.hostname;
    return Object.entries(PORTAL_SELECTORS)
        .find(([domain]) => hostname.includes(domain))?.[1];
}

function extractJobDetails() {
    const selectors = getPortalSelectors();
    if (!selectors) return null;

    const title = document.querySelector(selectors.title)?.innerText?.trim() || "N/A";
    const description = document.querySelector(selectors.description)?.innerHTML || "N/A";
    const skillsElements = document.querySelectorAll(selectors.skills);
    const skills = Array.from(skillsElements).map(el => el.innerText.trim());

    return {
        title,
        description,
        skills,
        url: window.location.href,
        source: window.location.hostname,
        timestamp: new Date().toISOString()
    };
}

// Listen for messages from the popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'EXTRACT_JOB_DETAILS') {
        const jobDetails = extractJobDetails();
        sendResponse(jobDetails);
    }
}); 