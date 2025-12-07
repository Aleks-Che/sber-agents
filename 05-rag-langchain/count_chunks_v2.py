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

def count_chunks_custom(pages: list) -> int:
    """Разбиение документов на чанки с кастомными сепараторами"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        separators=[
            "\n\n\n",    # Тройной перенос - обычно разделы
            "\n\n",      # Двойной перенос - параграфы
            "\n",        # Одинарный перенос
            ". ",        # Конец предложения
            " ",         # Пробелы
            ""           # Символы
        ],
        keep_separator=True  # Сохраняем разделители для контекста
    )
    chunks = text_splitter.split_documents(pages)
    logger.info(f"chunk_size=800, chunk_overlap=100, custom separators -> {len(chunks)} chunks")
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
    
    count = count_chunks_custom(pages)
    print(f"\nResult: {count} chunks")