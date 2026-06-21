import json

from app.asi_client import asi_one_chat_completion
from app.agents.extraction_agent import ExtractionAgent
from app.agents.fusion_agent import FusionAgent
from app.agents.memory_agent import MemoryAgent
from app.agents.prioritization_agent import PrioritizationAgent
from app.storage import clusters
from app.utils.agent_logger import log_agent


class ASIToolOrchestrator:
    def __init__(self):
        self.extraction_agent = ExtractionAgent()
        self.fusion_agent = FusionAgent()
        self.memory_agent = MemoryAgent()
        self.prioritization_agent = PrioritizationAgent()

    def normalize_source(self, source):
        allowed = {"voice", "web", "social", "weather", "field"}

        if source in allowed:
            return source

        return "field"

    def tools(self):
        return [
            {
                "type": "function",
                "function": {
                    "name": "submit_to_fusion",
                    "description": "Extract a structured emergency event from raw text and submit it to the incident fusion engine.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "raw_text": {"type": "string"},
                            "source": {
                                "type": "string",
                                "enum": ["voice", "web", "social", "weather", "field"]
                            }
                        },
                        "required": ["raw_text"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "retrieve_memory",
                    "description": "Retrieve historical disaster memory for a given cluster.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "cluster_id": {"type": "string"}
                        },
                        "required": ["cluster_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "rank_clusters",
                    "description": "Rank all active incident clusters by priority.",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            }
        ]

    def safe_dump(self, obj):
        if isinstance(obj, dict):
            cleaned = {}

            for key, value in obj.items():
                if hasattr(value, "model_dump"):
                    cleaned[key] = value.model_dump()
                else:
                    cleaned[key] = value

            return cleaned

        if hasattr(obj, "model_dump"):
            return obj.model_dump()

        return obj

    def execute_tool(self, name, arguments, fallback_source="field"):
        if name == "submit_to_fusion":
            source = self.normalize_source(
                arguments.get("source", fallback_source)
            )

            log_agent(
                "Extraction Agent",
                "Analyzing incoming incident report"
            )
            event = self.extraction_agent.extract_event(
                raw_text=arguments["raw_text"],
                source=source
            )

            result = self.fusion_agent.submit_event(event)
            log_agent(
                "Fusion Agent",
                f"Created/updated {result['cluster_id']}"
            )
            return self.safe_dump(result)

        if name == "retrieve_memory":
            cluster_id = arguments.get("cluster_id")
            cluster = clusters.get(cluster_id)

            if not cluster:
                return {
                    "error": "Cluster not found",
                    "cluster_id": cluster_id
                }
            log_agent(
                "Memory Agent",
                f"Retrieved memory for {cluster_id}"
            )
            return self.memory_agent.retrieve_memory(cluster)

        if name == "rank_clusters":
            return self.prioritization_agent.rank_clusters()

            log_agent(
                "Prioritization Agent",
                "Ranked active incidents"
            )
            return self.safe_dump(ranked)

    def parse_final_response(self, text):
        if not text:
            return {
                "recommendation": "No recommendation returned by ASI:One.",
                "reason": "Empty response.",
                "next_steps": []
            }

        cleaned = text.strip()

        if cleaned.startswith("```"):
            cleaned = cleaned.replace("```json", "").replace("```", "").strip()

        try:
            return json.loads(cleaned)
        except Exception:
            return {
                "recommendation": cleaned,
                "reason": "ASI:One returned plain text instead of JSON.",
                "next_steps": [
                    "Review incident details",
                    "Dispatch appropriate response resources",
                    "Continue monitoring new reports"
                ]
            }

    def process_report(self, raw_text: str, source: str = "web"):
        source = self.normalize_source(source)

        initial_message = {
            "role": "user",
            "content": f"""
You are ASI:One coordinating Lifeline AI emergency response tools.

Process this raw crisis report:
"{raw_text}"

Use the available tools.

Required workflow:
1. Call submit_to_fusion with the raw report.
2. After submit_to_fusion returns a cluster_id, call retrieve_memory using that cluster_id.
3. Call rank_clusters.
4. Produce a final responder recommendation.

Return the final answer as ONLY valid JSON:
{{
  "recommendation": "clear responder action",
  "reason": "why this incident matters",
  "next_steps": ["step 1", "step 2", "step 3"]
}}
"""
        }

        messages_history = [initial_message]

        first_response = asi_one_chat_completion(
            messages=messages_history,
            tools=self.tools(),
            conversation_id="lifeline_ai_tool_orchestration"
        )

        assistant_message = first_response["choices"][0]["message"]
        tool_calls = assistant_message.get("tool_calls", [])

        messages_history.append(assistant_message)

        executed_tools = []

        for tool_call in tool_calls:
            name = tool_call["function"]["name"]

            try:
                arguments = json.loads(
                    tool_call["function"].get("arguments", "{}")
                )
            except Exception:
                arguments = {}

            if name == "submit_to_fusion":
                arguments["raw_text"] = arguments.get("raw_text", raw_text)
                arguments["source"] = self.normalize_source(
                    arguments.get("source", source)
                )

            result = self.execute_tool(
                name=name,
                arguments=arguments,
                fallback_source=source
            )

            executed_tools.append({
                "tool": name,
                "arguments": arguments,
                "result": result
            })

            messages_history.append({
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "content": json.dumps(result, default=str)
            })

                # Keep looping if ASI:One asks for more tool calls
        max_rounds = 4

        for _ in range(max_rounds):
            response = asi_one_chat_completion(
                messages=messages_history,
                tools=self.tools(),
                conversation_id="lifeline_ai_tool_orchestration"
            )

            assistant_message = response["choices"][0]["message"]
            tool_calls = assistant_message.get("tool_calls", [])

            # If ASI:One gives normal tool_calls
            if tool_calls:
                messages_history.append(assistant_message)

                for tool_call in tool_calls:
                    name = tool_call["function"]["name"]

                    try:
                        arguments = json.loads(
                            tool_call["function"].get("arguments", "{}")
                        )
                    except Exception:
                        arguments = {}

                    result = self.execute_tool(
                        name=name,
                        arguments=arguments,
                        fallback_source=source
                    )

                    executed_tools.append({
                        "tool": name,
                        "arguments": arguments,
                        "result": result
                    })

                    messages_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": json.dumps(result, default=str)
                    })

                continue

            content = assistant_message.get("content", "")

            # If ASI returns pseudo tool text like:
            # <tool_call>retrieve_memory<arg_key>cluster_id</arg_key><arg_value>...</arg_value></tool_call>
            if "<tool_call>retrieve_memory" in content:
                cluster_id = content.split("<arg_value>")[1].split("</arg_value>")[0]

                result = self.execute_tool(
                    name="retrieve_memory",
                    arguments={"cluster_id": cluster_id},
                    fallback_source=source
                )

                executed_tools.append({
                    "tool": "retrieve_memory",
                    "arguments": {"cluster_id": cluster_id},
                    "result": result
                })

                messages_history.append({
                    "role": "user",
                    "content": (
                        "Tool result for retrieve_memory:\n"
                        f"{json.dumps(result, default=str)}\n\n"
                        "Now call rank_clusters or produce final JSON recommendation."
                    )
                })

                continue

            if "<tool_call>rank_clusters" in content:
                result = self.execute_tool(
                    name="rank_clusters",
                    arguments={},
                    fallback_source=source
                )

                executed_tools.append({
                    "tool": "rank_clusters",
                    "arguments": {},
                    "result": result
                })

                messages_history.append({
                    "role": "user",
                    "content": (
                        "Tool result for rank_clusters:\n"
                        f"{json.dumps(result, default=str)}\n\n"
                        "Now produce final JSON recommendation."
                    )
                })

                continue

            return {
                "orchestrator": "ASI:One Tool Calling",
                "raw_text": raw_text,
                "tool_calls_executed": executed_tools,
                "final_response": self.parse_final_response(content)
            }

        return {
            "orchestrator": "ASI:One Tool Calling",
            "raw_text": raw_text,
            "tool_calls_executed": executed_tools,
            "final_response": {
                "recommendation": "ASI:One orchestration reached maximum rounds.",
                "reason": "The model kept requesting tools instead of producing a final recommendation.",
                "next_steps": [
                    "Review executed tool results",
                    "Dispatch highest-priority incident manually",
                    "Continue monitoring reports"
                ]
            }
        }

        log_agent(
            "ASI:One",
            "Generated emergency response recommendation"
        )

        return {
            "orchestrator": "ASI:One Tool Calling",
            "raw_text": raw_text,
            "tool_calls_executed": executed_tools,
            "final_response": self.parse_final_response(final_text)
        }