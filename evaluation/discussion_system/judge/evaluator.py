"""
LLM Judge evaluator using Ollama.
"""

import json
import re
from pathlib import Path

import ollama

from config import settings
from models import (
    ConversationScores,
    CriterionResult,
    DebateState,
    SubsessionMetrics,
)
from parser import find_state_file, get_session_name, get_subsession_name, parse_state_file
from prompts import CRITERIA


class JudgeEvaluator:
    """
    LLM-based evaluator for multi-agent debate conversations.
    """
    
    def __init__(
        self,
        model: str | None = None,
        temperature: float | None = None,
        base_url: str | None = None,
        num_ctx: int | None = None,
    ):
        """
        Initialize the evaluator.
        
        Args:
            model: Ollama model name (defaults to settings)
            temperature: Model temperature (defaults to settings)
            base_url: Ollama API base URL (defaults to settings)
            num_ctx: Context window size (defaults to settings)
        """
        self.model = model or settings.ollama_model
        self.temperature = temperature if temperature is not None else settings.ollama_temperature
        self.base_url = base_url or settings.ollama_base_url
        self.num_ctx = num_ctx or settings.ollama_num_ctx
        
        # Configure ollama client
        self.client = ollama.Client(host=self.base_url)
    
    def _parse_criterion_response(self, response_text: str) -> dict:
        """
        Parse the LLM response to extract score and reasoning for a single criterion.
        
        Args:
            response_text: Raw LLM response
            
        Returns:
            Dictionary with 'score' and 'reasoning'
        """
        # Try direct JSON parse
        try:
            return json.loads(response_text.strip())
        except json.JSONDecodeError:
            pass
        
        # Try to extract JSON from markdown code block
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Try to find any JSON object in the text
        json_match = re.search(r'\{[^{}]*\}', response_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
        
        # Return default if parsing fails
        print(f"Warning: Could not parse LLM response, using default score")
        return {
            "score": 3,
            "reasoning": f"Parse error. Raw response: {response_text[:200]}..."
        }
    
    def evaluate_criterion(
        self, 
        criterion_name: str,
        state: DebateState,
        verbose: bool = True
    ) -> CriterionResult:
        """
        Evaluate a single criterion for the conversation.
        
        Args:
            criterion_name: Name of the criterion to evaluate
            state: Full debate state
            verbose: Print progress messages
            
        Returns:
            CriterionResult with score and reasoning
        """
        criterion_config = CRITERIA[criterion_name]
        system_prompt = criterion_config["system_prompt"]
        user_prompt = criterion_config["user_prompt_fn"](state)
        
        try:
            response = self.client.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                options={
                    "temperature": self.temperature,
                    "num_ctx": self.num_ctx,
                }
            )
            
            response_text = response["message"]["content"]
            parsed = self._parse_criterion_response(response_text)
            
            score = parsed.get("score", 3)
            # Clamp score to 1-5 range
            score = max(1, min(5, int(score)))
            
            return CriterionResult(
                criterion=criterion_name,
                score=score,
                reasoning=parsed.get("reasoning", "")
            )
            
        except Exception as e:
            print(f"Error evaluating {criterion_name}: {e}")
            return CriterionResult(
                criterion=criterion_name,
                score=3,
                reasoning=f"Evaluation error: {str(e)}"
            )
    
    def evaluate_conversation(
        self, 
        state: DebateState,
        verbose: bool = True
    ) -> ConversationScores:
        """
        Evaluate the entire conversation with separate LLM calls per criterion.
        
        Args:
            state: Full debate state
            verbose: Print progress messages
            
        Returns:
            ConversationScores with all criteria scores
        """
        results = {}
        
        for criterion_name in CRITERIA.keys():
            if verbose:
                print(f"  Evaluating {criterion_name}...")
            
            result = self.evaluate_criterion(criterion_name, state, verbose)
            results[criterion_name] = result
            
            if verbose:
                print(f"    Score: {result.score}")
        
        return ConversationScores(
            argument_coherence=results["argument_coherence"].score,
            identity_consistency=results["identity_consistency"].score,
            responsiveness=results["responsiveness"].score,
            consensus_alignment=results["consensus_alignment"].score,
            conflict_avoidance=results["conflict_avoidance"].score,
            argument_coherence_reasoning=results["argument_coherence"].reasoning,
            identity_consistency_reasoning=results["identity_consistency"].reasoning,
            responsiveness_reasoning=results["responsiveness"].reasoning,
            consensus_alignment_reasoning=results["consensus_alignment"].reasoning,
            conflict_avoidance_reasoning=results["conflict_avoidance"].reasoning,
        )
    
    def evaluate_subsession(
        self, 
        subsession_path: Path,
        verbose: bool = True
    ) -> SubsessionMetrics | None:
        """
        Evaluate a subsession's conversation.
        
        Args:
            subsession_path: Path to subsession directory
            verbose: Print progress messages
            
        Returns:
            SubsessionMetrics with conversation evaluation, or None if state file not found
        """
        state_file = find_state_file(subsession_path)
        if not state_file:
            print(f"No state file found in {subsession_path}")
            return None
        
        if verbose:
            print(f"Evaluating subsession: {subsession_path.name}")
        
        state = parse_state_file(state_file)
        session_name = get_session_name(subsession_path)
        subsession_name = get_subsession_name(subsession_path)
        
        scores = self.evaluate_conversation(state, verbose)
        
        if verbose:
            print(f"  Overall average: {scores.average}")
        
        return SubsessionMetrics(
            session_name=session_name,
            subsession_name=subsession_name,
            debate_topic=state.debate_topic,
            num_agents=len(state.agents),
            num_messages=len(state.messages),
            scores=scores
        )