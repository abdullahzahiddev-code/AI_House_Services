"""
ai_assistant/views.py — Chat interface views.
"""
import json
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from .models import AIConversation, AIMessage
from .rag_service import generate_recommendation


@login_required
def chat_home(request):
    """AI Assistant chat page."""
    # Get or create an active conversation for this session
    conversation = AIConversation.objects.filter(
        user=request.user, is_active=True
    ).first()

    # Get user's location from profile if available
    user_location = ''
    try:
        user_location = request.user.customer_profile.location
    except Exception:
        pass

    context = {
        'conversation': conversation,
        'user_location': user_location,
    }
    return render(request, 'ai_assistant/chat.html', context)


@login_required
@require_POST
def ask_ai(request):
    """
    AJAX endpoint that processes a user's problem description.
    Returns JSON with the AI's recommendation.
    """
    try:
        data = json.loads(request.body)
        problem = data.get('problem', '').strip()
        location = data.get('location', '').strip()
        conversation_id = data.get('conversation_id')
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({'error': 'Invalid request format.'}, status=400)

    if not problem:
        return JsonResponse({'error': 'Please describe your problem.'}, status=400)

    if len(problem) < 10:
        return JsonResponse(
            {'error': 'Please provide more detail about your problem (at least 10 characters).'},
            status=400
        )

    # Get or create conversation
    if conversation_id:
        try:
            conversation = AIConversation.objects.get(
                pk=conversation_id, user=request.user
            )
        except AIConversation.DoesNotExist:
            conversation = None
    else:
        conversation = None

    if not conversation:
        conversation = AIConversation.objects.create(
            user=request.user,
            session_title=problem[:100],
            problem_context=problem,
            location_context=location,
        )

    # Save user message
    AIMessage.objects.create(
        conversation=conversation,
        role=AIMessage.Role.USER,
        content=problem,
    )

    # Run RAG pipeline
    result = generate_recommendation(problem=problem, location=location)

    # Save AI response
    AIMessage.objects.create(
        conversation=conversation,
        role=AIMessage.Role.ASSISTANT,
        content=result['ai_response'],
        raw_context=str(result.get('rag_context_used', '')),
    )

    # Save recommendations to DB
    if result.get('providers'):
        from apps.recommendations.models import Recommendation
        for i, p in enumerate(result['providers']):
            try:
                from apps.providers.models import ProviderProfile
                provider = ProviderProfile.objects.get(pk=p['id'])
                Recommendation.objects.create(
                    conversation=conversation,
                    provider=provider,
                    rank=i + 1,
                    score=p['score'],
                    reason=f"Score: {p['score']:.0%} — Category match with {p['category']}",
                )
            except Exception:
                pass

    return JsonResponse({
        'conversation_id': conversation.pk,
        'detected_category': result.get('detected_category'),
        'is_dangerous': result.get('is_dangerous', False),
        'safety_warning': result.get('safety_warning'),
        'ai_response': result.get('ai_response', ''),
        'providers': result.get('providers', []),
    })


@login_required
def conversation_history(request):
    """View past AI conversations."""
    conversations = AIConversation.objects.filter(
        user=request.user
    ).prefetch_related('messages').order_by('-created_at')[:20]
    return render(request, 'ai_assistant/history.html', {'conversations': conversations})
