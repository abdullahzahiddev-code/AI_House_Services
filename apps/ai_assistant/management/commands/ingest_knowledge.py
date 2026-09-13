"""
Management command: ingest_knowledge
Usage: python manage.py ingest_knowledge [--rebuild]

This command:
1. Scans the knowledge_base/ directory for documents (TXT, CSV, JSON, PDF)
2. Also generates provider profiles from the live database
3. Splits text into chunks
4. Creates embeddings using Sentence-Transformers
5. Stores everything in ChromaDB for fast similarity search

After running this command, the AI assistant can retrieve
relevant information when a customer describes a problem.
"""
import os
import json
import csv
import logging
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Ingest knowledge base documents and provider data into ChromaDB vector store.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--rebuild',
            action='store_true',
            help='Delete existing vector store and rebuild from scratch.',
        )
        parser.add_argument(
            '--providers-only',
            action='store_true',
            help='Only re-index provider profiles (skip knowledge base documents).',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('🔧 AI Knowledge Base Ingestion'))
        self.stdout.write('─' * 60)

        try:
            import chromadb
            from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
        except ImportError as e:
            raise CommandError(f"ChromaDB not installed: {e}")

        # Setup ChromaDB
        persist_dir = settings.CHROMA_PERSIST_DIR
        embedding_model = settings.EMBEDDING_MODEL

        self.stdout.write(f"📁 ChromaDB directory: {persist_dir}")
        self.stdout.write(f"🤖 Embedding model: {embedding_model}")

        client = chromadb.PersistentClient(path=persist_dir)

        if options['rebuild']:
            self.stdout.write(self.style.WARNING('⚠️  Rebuilding — deleting existing collection...'))
            try:
                client.delete_collection("home_services_knowledge")
            except Exception:
                pass

        # Load embedding function
        self.stdout.write('📥 Loading embedding model (first run may download ~80MB)...')
        ef = SentenceTransformerEmbeddingFunction(model_name=embedding_model)

        collection = client.get_or_create_collection(
            name="home_services_knowledge",
            embedding_function=ef,
        )

        self.stdout.write(f"📊 Current collection size: {collection.count()} documents")

        documents = []
        metadatas = []
        ids = []
        doc_counter = collection.count()

        if not options['providers_only']:
            # ── Load knowledge base documents ─────────────────────────────────
            kb_dir = Path(settings.KNOWLEDGE_BASE_DIR)
            if not kb_dir.exists():
                self.stdout.write(self.style.WARNING(f"knowledge_base/ directory not found at {kb_dir}"))
            else:
                self.stdout.write(f'\n📂 Scanning {kb_dir} for documents...')
                for filepath in kb_dir.rglob('*'):
                    if filepath.suffix.lower() in ('.txt', '.md'):
                        chunks = self._load_text_file(filepath)
                    elif filepath.suffix.lower() == '.json':
                        chunks = self._load_json_file(filepath)
                    elif filepath.suffix.lower() == '.csv':
                        chunks = self._load_csv_file(filepath)
                    elif filepath.suffix.lower() == '.pdf':
                        chunks = self._load_pdf_file(filepath)
                    else:
                        continue

                    for chunk in chunks:
                        if not chunk.strip():
                            continue
                        doc_counter += 1
                        documents.append(chunk)
                        metadatas.append({
                            'source': str(filepath.name),
                            'type': 'knowledge_base',
                        })
                        ids.append(f"kb_{doc_counter}")
                    self.stdout.write(f"  ✅ Loaded {filepath.name}: {len(chunks)} chunks")

        # ── Load provider profiles from database ─────────────────────────────
        self.stdout.write('\n🏪 Indexing provider profiles from database...')
        provider_count = 0
        from apps.providers.models import ProviderProfile

        for provider in ProviderProfile.objects.filter(is_verified=True).select_related(
            'user', 'category'
        ).prefetch_related('skills', 'service_areas'):
            profile_text = self._format_provider_for_embedding(provider)
            doc_counter += 1
            documents.append(profile_text)
            metadatas.append({
                'source': 'provider_profile',
                'type': 'provider',
                'provider_id': str(provider.pk),
                'provider_name': provider.business_name,
                'category': provider.category.name if provider.category else '',
            })
            ids.append(f"provider_{provider.pk}")
            provider_count += 1

        self.stdout.write(f"  ✅ {provider_count} provider profiles indexed")

        # ── Batch upsert into ChromaDB ────────────────────────────────────────
        if documents:
            self.stdout.write(f'\n⚡ Embedding and storing {len(documents)} documents...')
            # Upsert in batches of 50
            batch_size = 50
            for i in range(0, len(documents), batch_size):
                batch_docs = documents[i:i + batch_size]
                batch_meta = metadatas[i:i + batch_size]
                batch_ids = ids[i:i + batch_size]
                collection.upsert(
                    documents=batch_docs,
                    metadatas=batch_meta,
                    ids=batch_ids,
                )
                self.stdout.write(f"  Batch {i // batch_size + 1}: stored {len(batch_docs)} docs")

        final_count = collection.count()
        self.stdout.write('\n' + '─' * 60)
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Knowledge base ingestion complete!\n'
                f'   Total documents in vector store: {final_count}'
            )
        )

    def _format_provider_for_embedding(self, provider) -> str:
        """Convert a provider profile into a rich text document for embedding."""
        skills = ', '.join(provider.get_skills_list()) or 'General services'
        areas = ', '.join(provider.get_service_areas_list()) or provider.base_location
        return (
            f"Service Provider: {provider.business_name}\n"
            f"Category: {provider.category.name if provider.category else 'N/A'}\n"
            f"Description: {provider.bio}\n"
            f"Skills and Expertise: {skills}\n"
            f"Years of Experience: {provider.experience_years} years\n"
            f"Rating: {provider.average_rating}/5 based on {provider.total_reviews} customer reviews\n"
            f"Service Areas: {areas}\n"
            f"Base Location: {provider.base_location}\n"
            f"Charge Range: {provider.get_charge_range()}\n"
            f"Available: {'Yes' if provider.is_available else 'No'}\n"
        )

    def _load_text_file(self, filepath: Path, chunk_size: int = 500) -> list[str]:
        """Load a text file and split into chunks."""
        try:
            text = filepath.read_text(encoding='utf-8')
            # Simple chunking by paragraphs
            paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
            chunks = []
            current_chunk = []
            current_size = 0
            for para in paragraphs:
                if current_size + len(para) > chunk_size and current_chunk:
                    chunks.append('\n\n'.join(current_chunk))
                    current_chunk = []
                    current_size = 0
                current_chunk.append(para)
                current_size += len(para)
            if current_chunk:
                chunks.append('\n\n'.join(current_chunk))
            return chunks
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"    Warning: Could not read {filepath}: {e}"))
            return []

    def _load_json_file(self, filepath: Path) -> list[str]:
        """Load JSON file — each top-level item becomes a document."""
        try:
            data = json.loads(filepath.read_text(encoding='utf-8'))
            if isinstance(data, list):
                return [json.dumps(item, ensure_ascii=False, indent=2) for item in data]
            elif isinstance(data, dict):
                return [json.dumps(data, ensure_ascii=False, indent=2)]
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"    Warning: Could not parse {filepath}: {e}"))
        return []

    def _load_csv_file(self, filepath: Path) -> list[str]:
        """Load CSV — each row becomes a document."""
        chunks = []
        try:
            with open(filepath, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    text = '\n'.join(f"{k}: {v}" for k, v in row.items() if v)
                    chunks.append(text)
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"    Warning: Could not parse {filepath}: {e}"))
        return chunks

    def _load_pdf_file(self, filepath: Path) -> list[str]:
        """Load PDF using pypdf."""
        try:
            from pypdf import PdfReader
            reader = PdfReader(str(filepath))
            chunks = []
            for page in reader.pages:
                text = page.extract_text()
                if text and text.strip():
                    chunks.append(text.strip())
            return chunks
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"    Warning: Could not parse PDF {filepath}: {e}"))
            return []
