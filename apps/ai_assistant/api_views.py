"""ai_assistant/api_views.py — REST API endpoints for AI."""
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .rag_service import generate_recommendation
from .models import AIConversation, AIMessage


class RecommendAPIView(APIView):
    """
    POST /api/ai/recommend/
    
    The main AI recommendation API endpoint.
    
    Request:
        {
            "problem": "My kitchen sink is leaking",
            "location": "Bahria Town Rawalpindi"
        }
    
    Response:
        {
            "service_category": "plumber",
            "problem_summary": "...",
            "is_dangerous": false,
            "safety_warning": null,
            "recommendations": [...],
            "ai_explanation": "..."
        }
    """
    permission_classes = [permissions.AllowAny]  # Public API for discovery

    def post(self, request):
        problem = request.data.get('problem', '').strip()
        location = request.data.get('location', '').strip()

        if not problem:
            return Response({'error': 'Problem description is required.'}, status=400)

        result = generate_recommendation(problem=problem, location=location)

        # Save conversation if user is authenticated
        if request.user.is_authenticated:
            conv = AIConversation.objects.create(
                user=request.user,
                session_title=problem[:100],
                problem_context=problem,
                location_context=location,
            )
            AIMessage.objects.create(
                conversation=conv,
                role=AIMessage.Role.USER,
                content=problem,
            )
            AIMessage.objects.create(
                conversation=conv,
                role=AIMessage.Role.ASSISTANT,
                content=result['ai_response'],
            )

        return Response({
            'service_category': result.get('detected_category'),
            'problem_summary': problem,
            'is_dangerous': result.get('is_dangerous', False),
            'safety_warning': result.get('safety_warning'),
            'recommendations': result.get('providers', []),
            'ai_explanation': result.get('ai_response', ''),
        })


class ChatAPIView(APIView):
    """
    POST /api/ai/chat/ — Stateful chat within a conversation.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        problem = request.data.get('message', '').strip()
        location = request.data.get('location', '').strip()
        conversation_id = request.data.get('conversation_id')

        if not problem:
            return Response({'error': 'Message is required.'}, status=400)

        result = generate_recommendation(problem=problem, location=location)
        return Response({
            'response': result.get('ai_response', ''),
            'providers': result.get('providers', []),
            'detected_category': result.get('detected_category'),
        })
