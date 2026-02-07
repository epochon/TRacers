EMAIL_TEMPLATES = {
    "medical": {
        "subject": "Request for Medical Leave: {{REASON}}",
        "body": "I am writing to formally request medical leave due to {{CONTEXT}}. As per college guidelines, I have attached the necessary medical certificates. I ensure to cover any missed academic responsibilities upon my return."
    },
    "internship": {
        "subject": "Application for Internship NOC: {{COMPANY_NAME}}",
        "body": "I am writing to request a No Objection Certificate (NOC) for an internship opportunity at {{CONTEXT}}. This internship aligns with my academic curriculum and will provide valuable industry exposure. I assure you that my academic performance will not be hindered."
    },
    "attendance": {
        "subject": "Request for Attendance Condonation",
        "body": "I am writing to request condonation for my attendance shortage due to {{CONTEXT}}. I understand the importance of regular attendance and have been consistent otherwise. I kindly request you to consider my situation."
    },
    "general": {
        "subject": "Formal Request Regarding {{REASON}}",
        "body": "I am writing to bring to your attention {{CONTEXT}}. I kindly request your guidance and support in this matter."
    }
}
