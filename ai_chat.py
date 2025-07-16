from flask import Blueprint, request, jsonify
import os
import openai
import google.generativeai as genai
from typing import Dict, Any
import time
import logging

ai_chat_bp = Blueprint('ai_chat', __name__)

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIModelRouter:
    def __init__(self):
        # API 키 설정 (환경변수에서 가져오기)
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        
        # OpenAI 클라이언트 초기화
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        
        # Gemini 클라이언트 초기화
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
    
    def route_message(self, message: str, model_preference: str = "auto") -> Dict[str, Any]:
        """
        메시지를 적절한 AI 모델로 라우팅
        """
        try:
            if model_preference == "gpt" or (model_preference == "auto" and self._should_use_gpt(message)):
                return self._call_gpt(message)
            elif model_preference == "gemini" or (model_preference == "auto" and self._should_use_gemini(message)):
                return self._call_gemini(message)
            else:
                # 기본값으로 GPT 사용
                return self._call_gpt(message)
        except Exception as e:
            logger.error(f"AI 모델 호출 중 오류 발생: {str(e)}")
            return {
                "response": "죄송합니다. 현재 AI 서비스에 문제가 있습니다. 잠시 후 다시 시도해주세요.",
                "model": "error",
                "error": str(e)
            }
    
    def _should_use_gpt(self, message: str) -> bool:
        """
        GPT를 사용해야 하는지 판단하는 로직
        """
        gpt_keywords = ["창작", "글쓰기", "코딩", "프로그래밍", "번역"]
        return any(keyword in message for keyword in gpt_keywords)
    
    def _should_use_gemini(self, message: str) -> bool:
        """
        Gemini를 사용해야 하는지 판단하는 로직
        """
        gemini_keywords = ["분석", "추론", "계산", "수학", "과학"]
        return any(keyword in message for keyword in gemini_keywords)
    
    def _call_gpt(self, message: str) -> Dict[str, Any]:
        """
        OpenAI GPT API 호출
        """
        if not self.openai_api_key:
            return {
                "response": "OpenAI API 키가 설정되지 않았습니다.",
                "model": "gpt",
                "error": "API key not configured"
            }
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "당신은 도움이 되는 AI 어시스턴트입니다. 한국어로 친근하고 정확하게 답변해주세요."},
                    {"role": "user", "content": message}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            return {
                "response": response.choices[0].message.content,
                "model": "gpt",
                "usage": response.usage._asdict() if hasattr(response, 'usage') else None
            }
        except Exception as e:
            logger.error(f"GPT API 호출 오류: {str(e)}")
            return {
                "response": f"GPT API 호출 중 오류가 발생했습니다: {str(e)}",
                "model": "gpt",
                "error": str(e)
            }
    
    def _call_gemini(self, message: str) -> Dict[str, Any]:
        """
        Google Gemini API 호출
        """
        if not self.gemini_api_key:
            return {
                "response": "Gemini API 키가 설정되지 않았습니다.",
                "model": "gemini",
                "error": "API key not configured"
            }
        
        try:
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(message)
            
            return {
                "response": response.text,
                "model": "gemini",
                "usage": None  # Gemini API usage 정보는 별도 처리 필요
            }
        except Exception as e:
            logger.error(f"Gemini API 호출 오류: {str(e)}")
            return {
                "response": f"Gemini API 호출 중 오류가 발생했습니다: {str(e)}",
                "model": "gemini",
                "error": str(e)
            }

# AI 모델 라우터 인스턴스 생성
ai_router = AIModelRouter()

@ai_chat_bp.route('/chat', methods=['POST'])
def chat():
    """
    AI 채팅 엔드포인트
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                "error": "메시지가 필요합니다.",
                "status": "error"
            }), 400
        
        message = data['message']
        model_preference = data.get('model', 'auto')  # auto, gpt, gemini
        
        # AI 모델로 메시지 라우팅
        result = ai_router.route_message(message, model_preference)
        
        return jsonify({
            "message": result["response"],
            "model": result["model"],
            "usage": result.get("usage"),
            "error": result.get("error"),
            "status": "success" if "error" not in result else "error"
        })
        
    except Exception as e:
        logger.error(f"채팅 엔드포인트 오류: {str(e)}")
        return jsonify({
            "error": f"서버 오류가 발생했습니다: {str(e)}",
            "status": "error"
        }), 500

@ai_chat_bp.route('/models', methods=['GET'])
def get_available_models():
    """
    사용 가능한 AI 모델 목록 반환
    """
    models = []
    
    if ai_router.openai_api_key:
        models.append({
            "id": "gpt",
            "name": "GPT-3.5 Turbo",
            "provider": "OpenAI",
            "status": "available"
        })
    
    if ai_router.gemini_api_key:
        models.append({
            "id": "gemini",
            "name": "Gemini Pro",
            "provider": "Google",
            "status": "available"
        })
    
    return jsonify({
        "models": models,
        "status": "success"
    })

@ai_chat_bp.route('/health', methods=['GET'])
def health_check():
    """
    AI 서비스 상태 확인
    """
    status = {
        "openai": "configured" if ai_router.openai_api_key else "not_configured",
        "gemini": "configured" if ai_router.gemini_api_key else "not_configured",
        "timestamp": time.time()
    }
    
    return jsonify({
        "status": status,
        "message": "AI 채팅 서비스가 실행 중입니다."
    })

