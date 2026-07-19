from app.ingestion.loaders.office import parse_office

# Should work instantly
docx_text = parse_office("D:\Projects\ai_engineer\agentic_rag\DATA\true_data\cronjobs.docx")
pptx_text = parse_office("D:\Projects\ai_engineer\agentic_rag\DATA\true_data\architecture.pptx")

print(f"DOCX: {len(docx_text)} chars")
print(f"PPTX: {len(pptx_text)} chars")