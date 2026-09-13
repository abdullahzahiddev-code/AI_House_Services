"""
ai_assistant/rag_service.py
───────────────────────────
Core RAG (Retrieval-Augmented Generation) pipeline.

How it works:
  1. User describes a problem (e.g., "My kitchen sink is leaking")
  2. We embed the problem using Sentence-Transformers
  3. We search ChromaDB for relevant knowledge-base chunks
  4. We retrieve matching providers from the Django database
  5. We combine everything into a prompt and call the LLM
  6. The LLM generates a personalized recommendation

The LLM never invents providers — it only explains the ones
we retrieve from our database.
"""
import os
import logging
from typing import Optional

from django.conf import settings

logger = logging.getLogger(__name__)


# ── Lazy-loaded AI components (avoid import errors at startup) ────────────────

def _get_embedding_function():
    """Load Sentence-Transformers embedding model."""
    try:
        from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
        return SentenceTransformerEmbeddingFunction(
            model_name=settings.EMBEDDING_MODEL
        )
    except Exception as e:
        logger.warning(f"Could not load embedding function: {e}")
        return None


def _get_chroma_collection():
    """Get or create the ChromaDB collection."""
    try:
        import chromadb
        client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
        ef = _get_embedding_function()
        collection = client.get_or_create_collection(
            name="home_services_knowledge",
            embedding_function=ef,
        )
        return collection
    except Exception as e:
        logger.warning(f"Could not connect to ChromaDB: {e}")
        return None


def _get_llm_client():
    """Create OpenAI-compatible LLM client."""
    try:
        from openai import OpenAI
        kwargs = {'api_key': settings.OPENAI_API_KEY}
        if settings.OPENAI_BASE_URL:
            kwargs['base_url'] = settings.OPENAI_BASE_URL
        return OpenAI(**kwargs)
    except Exception as e:
        logger.warning(f"Could not create LLM client: {e}")
        return None


# ── Category keyword mapping (fallback if RAG fails) ─────────────────────────

CATEGORY_KEYWORDS = {
    'plumber': [
        'leak', 'leaking', 'pipe', 'drain', 'tap', 'faucet', 'sink', 'toilet',
        'water', 'sewage', 'blockage', 'clogged', 'bathroom', 'kitchen', 'flush',
        'overflow', 'fitting', 'valve', 'pressure'
    ],
    'electrician': [
        'electric', 'electrical', 'wiring', 'switch', 'socket', 'outlet', 'plug',
        'breaker', 'fuse', 'light', 'bulb', 'power', 'voltage', 'spark', 'short circuit',
        'trip', 'mcb', 'fan', 'wire', 'cable', 'shock', 'current'
    ],
    'ac technician': [
        'ac', 'air conditioner', 'cooling', 'cool', 'heat', 'heating',
        'refrigerant', 'gas', 'compressor', 'filter', 'aircon', 'split unit',
        'window unit', 'inverter', 'temperature', 'condenser', 'remote'
    ],
    'carpenter': [
        'wood', 'wooden', 'furniture', 'door', 'window', 'cabinet', 'cupboard',
        'table', 'chair', 'shelf', 'wardrobe', 'carpenter', 'repair', 'hinge',
        'lock', 'handle', 'panel', 'flooring', 'ceiling'
    ],
    'painter': [
        'paint', 'painting', 'wall', 'ceiling', 'color', 'colour', 'brush',
        'roller', 'primer', 'whitewash', 'plaster', 'crack', 'peeling', 'damp',
        'moisture', 'seepage', 'waterproof'
    ],
    'appliance repair': [
        'washing machine', 'washer', 'dryer', 'refrigerator', 'fridge', 'oven',
        'microwave', 'dishwasher', 'geyser', 'water heater', 'iron', 'appliance',
        'motor', 'pump', 'inverter', 'ups'
    ],
    'cleaning': [
        'clean', 'cleaning', 'dirty', 'dust', 'sofa', 'carpet', 'mattress',
        'tank', 'water tank', 'deep clean', 'sanitize', 'disinfect', 'mold',
        'mould', 'pest', 'cockroach', 'termite'
    ],
}

DANGEROUS_KEYWORDS = [
    'gas leak', 'gas smell', 'fire', 'burning smell', 'electric shock',
    'structural crack', 'wall collapse', 'roof collapse', 'explosion',
    'smoke', 'sparking', 'flooding',
]


def detect_category_from_keywords(problem_text: str) -> Optional[str]:
    """
    Simple keyword matching to detect the most likely service category.
    Used as a fast fallback when RAG retrieval is unavailable.
    """
    problem_lower = problem_text.lower()
    scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in problem_lower)
        if score > 0:
            scores[category] = score
    if scores:
        return max(scores, key=scores.get)
    return None


def has_dangerous_content(problem_text: str) -> bool:
    """Check if the problem description contains dangerous keywords."""
    problem_lower = problem_text.lower()
    return any(kw in problem_lower for kw in DANGEROUS_KEYWORDS)


def retrieve_rag_context(problem: str, n_results: int = 5) -> str:
    """
    Search ChromaDB for relevant knowledge-base documents.
    Returns a formatted string of retrieved context.
    """
    collection = _get_chroma_collection()
    if not collection:
        return "Knowledge base unavailable — using keyword matching fallback."

    try:
        results = collection.query(
            query_texts=[problem],
            n_results=min(n_results, collection.count() or 1),
            include=['documents', 'metadatas', 'distances'],
        )
        if not results['documents'] or not results['documents'][0]:
            return "No relevant knowledge found for this problem."

        context_parts = []
        for doc, meta, dist in zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0],
        ):
            relevance = max(0, 1 - dist)  # Convert distance to relevance score
            source = meta.get('source', 'Knowledge Base')
            context_parts.append(
                f"[Relevance: {relevance:.0%} | Source: {source}]\n{doc}"
            )

        return "\n\n---\n\n".join(context_parts)
    except Exception as e:
        logger.error(f"RAG retrieval error: {e}")
        return f"RAG retrieval encountered an error: {str(e)}"


def get_providers_context(category_name: str, location: str, limit: int = 5) -> tuple[list, str]:
    """
    Retrieve and score providers from the database.
    Returns (list of scored providers, formatted context string).
    """
    from apps.providers.models import ProviderProfile
    from apps.recommendations.scoring import score_provider
    from django.db.models import Q

    # Filter providers by category and location
    qs = ProviderProfile.objects.filter(
        is_verified=True,
        is_available=True,
    ).select_related('user', 'category').prefetch_related('skills', 'service_areas')

    if category_name:
        qs = qs.filter(
            Q(category__name__icontains=category_name) |
            Q(category__slug__icontains=category_name.lower().replace(' ', '-'))
        )

    # Score and rank each provider
    scored_providers = []
    for provider in qs[:20]:  # pre-filter top 20 for scoring
        score = score_provider(provider, category_name, location)
        scored_providers.append((score, provider))

    # Sort by score, take top N
    scored_providers.sort(key=lambda x: x[0], reverse=True)
    top_providers = scored_providers[:limit]

    if not top_providers:
        return [], "No verified providers found for this service category in your area."

    # Format provider context for LLM
    context_parts = []
    provider_list = []
    for i, (score, provider) in enumerate(top_providers, 1):
        skills = ', '.join(provider.get_skills_list()) or 'General services'
        areas = ', '.join(provider.get_service_areas_list()) or provider.base_location
        charge_range = provider.get_charge_range()

        context_parts.append(
            f"Provider #{i}: {provider.business_name}\n"
            f"  Category: {provider.category.name if provider.category else 'N/A'}\n"
            f"  Skills: {skills}\n"
            f"  Experience: {provider.experience_years} years\n"
            f"  Rating: {provider.average_rating:.1f}/5 ({provider.total_reviews} reviews)\n"
            f"  Service Areas: {areas}\n"
            f"  Base Location: {provider.base_location}\n"
            f"  Charges: {charge_range}\n"
            f"  Match Score: {score:.0%}\n"
        )

        provider_list.append({
            'id': provider.id,
            'business_name': provider.business_name,
            'category': provider.category.name if provider.category else '',
            'rating': float(provider.average_rating),
            'experience_years': provider.experience_years,
            'skills': provider.get_skills_list(),
            'service_areas': provider.get_service_areas_list(),
            'base_location': provider.base_location,
            'charge_range': charge_range,
            'score': score,
        })

    return provider_list, "\n\n".join(context_parts)


def generate_recommendation(problem: str, location: str = '') -> dict:
    """
    Main RAG pipeline entry point.

    Steps:
    1. Check for dangerous content → safety warning
    2. Detect service category from problem
    3. Retrieve RAG knowledge context
    4. Retrieve and score providers from database
    5. Build prompt and call LLM
    6. Return structured response
    """
    from .prompts import RECOMMENDATION_PROMPT_TEMPLATE, SYSTEM_PROMPT

    # Step 1: Safety check
    is_dangerous = has_dangerous_content(problem)
    safety_warning = None
    if is_dangerous:
        safety_warning = (
            "⚠️ SAFETY WARNING: Your problem description contains potentially dangerous keywords. "
            "If you smell gas, see sparks, or observe structural damage — please evacuate the area "
            "immediately and call emergency services (Rescue 1122 or SNGPL 1199) before anything else. "
            "Do NOT use any electrical switches or open flames."
        )

    # Step 2: Detect category
    detected_category = detect_category_from_keywords(problem)

    # Step 3: Retrieve RAG context
    rag_context = retrieve_rag_context(problem)

    # Step 4: Get providers
    provider_list, providers_context = get_providers_context(
        detected_category or '', location
    )

    # Step 5: Build LLM prompt
    prompt = RECOMMENDATION_PROMPT_TEMPLATE.format(
        problem=problem,
        location=location or "Not specified",
        rag_context=rag_context,
        providers_context=providers_context if providers_context else "No providers found.",
    )

    # Step 6: Call LLM
    ai_response = _call_llm(SYSTEM_PROMPT, prompt)

    return {
        'detected_category': detected_category,
        'is_dangerous': is_dangerous,
        'safety_warning': safety_warning,
        'ai_response': ai_response,
        'providers': provider_list,
        'rag_context_used': bool(rag_context and 'unavailable' not in rag_context),
    }


def _call_llm(system_prompt: str, user_message: str) -> str:
    """
    Call the LLM with the given system prompt and user message.
    Falls back to a keyword-based response if the API is unavailable.
    """
    client = _get_llm_client()
    api_key = settings.OPENAI_API_KEY

    if not client or not api_key or api_key == 'your-openai-api-key-here':
        return _fallback_response(user_message)

    try:
        response = client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_message},
            ],
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=settings.LLM_MAX_TOKENS,
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"LLM API call failed: {e}")
        return _fallback_response(user_message)


def _fallback_response(prompt: str) -> str:
    """
    Simple fallback response when the LLM API is not configured.
    This ensures the app still works without an API key.
    """
    detected = detect_category_from_keywords(prompt)
    if detected:
        return (
            f"📋 **Analysis:** Based on your description, this appears to be a "
            f"**{detected.title()}** issue.\n\n"
            f"🔧 I recommend hiring a qualified {detected} to assess and fix this problem.\n\n"
            f"📌 **Note:** Full AI recommendations require an OpenAI API key configured in your .env file. "
            f"Please check the provider listings below for available professionals in your area.\n\n"
            f"⚠️ Please note that this is an initial assessment only and not a professional diagnosis."
        )
    return (
        "I wasn't able to clearly classify your problem. "
        "Please browse the provider categories below or describe the problem in more detail. "
        "Note: Full AI responses require an OpenAI API key."
    )
