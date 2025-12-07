import logging
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_pdf_documents(data_dir: str) -> list:
    """Загрузка всех PDF документов из директории"""
    pages = []
    data_path = Path(data_dir)
    
    if not data_path.exists():
        logger.warning(f"Directory {data_dir} does not exist")
        return pages

    pdf_files = list(data_path.glob("*.pdf"))
    logger.info(f"Found {len(pdf_files)} PDF files in {data_dir}")
    
    for pdf_file in pdf_files:
        loader = PyPDFLoader(str(pdf_file))
        pages.extend(loader.load())
        logger.info(f"Loaded {pdf_file.name}")
    
    return pages

def count_chunks(pages: list, chunk_size: int, chunk_overlap: int) -> int:
    """Разбиение документов на чанки и возврат количества"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    chunks = text_splitter.split_documents(pages)
    logger.info(f"chunk_size={chunk_size}, chunk_overlap={chunk_overlap} -> {len(chunks)} chunks")
    return len(chunks)

if __name__ == "__main__":
    data_dir = "data"
    pages = load_pdf_documents(data_dir)
    if not pages:
        print("No pages loaded")
        exit(1)
    
    total_chars = sum(len(page.page_content) for page in pages)
    print(f"Total pages: {len(pages)}")
    print(f"Total characters: {total_chars}")
    
    # Параметр 1
    count1 = count_chunks(pages, chunk_size=500, chunk_overlap=50)
    # Параметр 2
    count2 = count_chunks(pages, chunk_size=1500, chunk_overlap=150)
    
    print("\nResults:")
    print(f"chunk_size=500, chunk_overlap=50 -> {count1} chunks")
    print(f"chunk_size=1500, chunk_overlap=150 -> {count2} chunks")