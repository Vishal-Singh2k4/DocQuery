import os
from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, 'Engineering Organization - Roles & Specifications', border=False, ln=True, align='R')
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

def generate_pdf():
    os.makedirs('documents', exist_ok=True)
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # ---------------- PAGE 1 ----------------
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 18)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 10, 'Product Engineering Intern (7 positions)', ln=True)
    pdf.ln(5)

    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 7, 'Overview & Role Specifications', ln=True)
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(51, 65, 85)
    
    details = [
        ("Function:", "Product Engineering: AI, agentic AI and cybersecurity"),
        ("Degree:", "B.E. or B.Tech in CSE, IT, AI and ML, ECE or a related branch; MCA; M.Sc in Computer Science, Data Science or Cyber Security"),
        ("Converts to:", "Product Engineer"),
        ("Working Hours:", "Core hours are 11:00 to 17:00 IST"),
        ("Access:", "Development, test and lab environments with synthetic data.")
    ]
    
    for label, val in details:
        pdf.set_font('Helvetica', 'B', 10)
        pdf.cell(35, 6, label, ln=False)
        pdf.set_font('Helvetica', '', 10)
        pdf.multi_cell(0, 6, val)
        pdf.ln(2)

    pdf.ln(4)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 7, 'About the Role', ln=True)
    pdf.set_font('Helvetica', '', 10)
    pdf.multi_cell(0, 6, (
        "You will build AI features, AI agents and security capabilities in our products and "
        "take them from design to release. The software runs in the cloud and on customer premises."
    ))

    # ---------------- PAGE 2 ----------------
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 8, 'What You Will Do', ln=True)
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(51, 65, 85)
    pdf.ln(2)

    responsibilities = [
        "Build LLM features: retrieval over documents (RAG), structured extraction and evaluation.",
        "Build AI agents that plan, call tools through MCP and ask a person for approval.",
        "Red-team AI features and agents for prompt injection and data leakage. Build guardrails.",
        "Test web applications and APIs against the OWASP Top 10 security framework and fix what you find.",
        "Build security engineering features: asset discovery, vulnerability data pipelines and risk scoring.",
        "Write backend services in Python or TypeScript on PostgreSQL database, with screens in React.",
        "Package what you build in containers for the cloud and for on-premises installation.",
        "Write tests and evaluations for everything you ship. Give and receive code review."
    ]

    for resp in responsibilities:
        pdf.cell(5, 6, "-", ln=False)
        pdf.multi_cell(0, 6, f" {resp}")
        pdf.ln(1)

    # ---------------- PAGE 3 ----------------
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 8, 'Requirements & Selection Criteria', ln=True)
    pdf.ln(2)

    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(0, 6, 'What You Must Bring:', ln=True)
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(51, 65, 85)

    must_bring = [
        "Python or TypeScript, with at least one project we can read on GitHub or run.",
        "How LLMs work in practice: tokens, context windows, embeddings and tool calling.",
        "Web and API fundamentals: HTTP, REST, JSON, authentication and access control.",
        "Security fundamentals: the OWASP Top 10 security framework and basic networking.",
        "SQL, Git and the Linux command line."
    ]
    for mb in must_bring:
        pdf.cell(5, 6, "-", ln=False)
        pdf.multi_cell(0, 6, f" {mb}")
        pdf.ln(1)

    pdf.ln(3)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(0, 6, 'Good to Have:', ln=True)
    pdf.set_font('Helvetica', '', 10)
    good_to_have = [
        "A RAG or agent project built with a framework such as LangGraph or a model provider's SDK.",
        "Security practice through CTFs, PortSwigger Web Security Academy, TryHackMe or Hack The Box.",
        "Docker, a cloud platform or open-weight models run with Ollama or vLLM."
    ]
    for gh in good_to_have:
        pdf.cell(5, 6, "-", ln=False)
        pdf.multi_cell(0, 6, f" {gh}")
        pdf.ln(1)

    pdf.ln(3)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(0, 6, 'Role Exercise:', ln=True)
    pdf.set_font('Helvetica', '', 10)
    pdf.multi_cell(0, 6, (
        "Choose one task. Build a question-answering service over PDF documents we provide and "
        "score it on ten test questions. Or build an agent that checks DNS records and TLS "
        "certificate expiry for a list of domains. Or find and write up the vulnerabilities in "
        "a vulnerable web application we provide."
    ))

    output_path = os.path.join('documents', 'sample_document.pdf')
    pdf.output(output_path)
    print(f"Created {output_path} successfully!")

if __name__ == '__main__':
    generate_pdf()
