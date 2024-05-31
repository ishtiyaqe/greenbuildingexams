import fitz  # PyMuPDF
import docx
from openai import OpenAI
client = OpenAI(api_key = 'sk-proj-d1C6VK0KpRTxBDNmAeguT3BlbkFJmci9p3jNlnr38c5STA6P')
# Initialize OpenAI API
# openai.api_key = 'sk-proj-d1C6VK0KpRTxBDNmAeguT3BlbkFJmci9p3jNlnr38c5STA6P'

def extract_text_from_pdf(file_path):
    text = ""
    doc = fitz.open(file_path)
    for page in doc:
        text += page.get_text()
    return text

def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

def split_text_into_chunks(text, max_chunk_size=2000):
    words = text.split()
    chunks = []
    current_chunk = []

    for word in words:
        if len(' '.join(current_chunk + [word])) <= max_chunk_size:
            current_chunk.append(word)
        else:
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks

def generate_questions_for_chunk(text_chunk, num_questions):
    print("generating data")
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": f"You will be provided with text from a document. Your task is to generate {num_questions} multiple-choice questions with correct answers based on the text, from question remove serial nuumber start with qquestion: correct answer start with answer, options will start with options ,all 4 option will in option list like options:['option 1','option 2','option 3','option 4] "
            },
            {
                "role": "user",
                "content": text_chunk
            }
        ],
        temperature=0.7,
        max_tokens=4096  # Adjust this value if needed
    )
    return response.choices[0].message.content.strip()

def generate_questions(text, num_questions=1):
    chunks = split_text_into_chunks(text)
    questions_per_chunk = num_questions // len(chunks)
    all_questions = ""

    for chunk in chunks:
        all_questions += generate_questions_for_chunk(chunk, questions_per_chunk) + "\n"

    return all_questions.strip()

def main(file_path, num_questions=10):
    print(file_path)
    if file_path.endswith('.pdf'):
        text = extract_text_from_pdf(file_path)
    elif file_path.endswith('.docx'):
        text = extract_text_from_docx(file_path)
    else:
        raise ValueError("Unsupported file format. Please upload a PDF or DOCX file.")
    
    questions = generate_questions(text, num_questions)
    return questions


