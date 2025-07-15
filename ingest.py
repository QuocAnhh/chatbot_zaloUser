import typer
from pathlib import Path
from app.services.rag_service import ingest_documents

app = typer.Typer()

@app.command()
def ingest(path: str):
    ingest_documents(path)
    typer.echo("✅ Đã nạp tài liệu vào vector store!")

if __name__ == "__main__":
    app()