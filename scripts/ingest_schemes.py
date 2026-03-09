import os
import sys

# Add the project root to the python path so we can import backend packages
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.services.rag_engine import rag_engine

def ingest_data():
    print("Starting data ingestion process...")
    try:
        rag_engine.load_documents()
        rag_engine.build_vector_index()
        print("Data ingestion completed successfully!")
    except Exception as e:
        print(f"Error during data ingestion: {e}")

if __name__ == "__main__":
    ingest_data()
