"""Claude Code SDK integration for running prompts."""

import os
import subprocess
from datetime import datetime
from claude_code_sdk import query, ClaudeCodeOptions
ClaudeCodeClient = query


class ClaudeRunner:
    """Handles running prompts using Claude Code SDK."""
    
    def __init__(self, logger):
        """Initialize Claude runner."""
        self.logger = logger
        self.claude_client = None
        self._initialize_claude_client()
        
    def _initialize_claude_client(self):
        """Initialize the Claude Code SDK client."""
        if ClaudeCodeClient is None:
            self.logger.warning("Claude Code SDK not available. Install with: pip install claude-code-sdk")
            return
            
        try:
            # The query function is available, store it as the client
            self.claude_client = ClaudeCodeClient
            self.logger.info("Claude Code SDK client initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Claude Code SDK client: {e}")
            self.claude_client = None
        
    def run_prompt(self, inline_prompt=None, prompt_name=None, params=None, context=None, session_id=None):
        """Run a prompt using Claude Code SDK with template parameter replacement."""
        if inline_prompt:
          prompt_content = inline_prompt
        else:
          prompt_file = f"_Settings_/Prompts/{prompt_name}.md"
          
          if not os.path.exists(prompt_file):
            self.logger.error(f"Prompt file not found: {prompt_file}")
            return None
          
          # Read the prompt content
          with open(prompt_file, 'r') as f:
              prompt_content = f.read()
              
            
        try:
            # Replace template parameters if provided
            if params:
                for key, value in params.items():
                    placeholder = f"{{{key}}}"
                    prompt_content = prompt_content.replace(placeholder, str(value))
            
            # Add context if provided
            if context:
                prompt_content = f"{prompt_content}\n\nContext:\n{context}"
             
            self.logger.info(f"Running prompt: {prompt_name}")
            
            # Use claude-code-sdk to run the prompt
            result, session_id = self._execute_claude_prompt(prompt_content, prompt_name, session_id)
            if result:
                self.logger.info(f"Prompt {prompt_name} executed successfully")
                self.logger.info(result)
                return result, session_id
            else:
                self.logger.error(f"Prompt {prompt_name} execution failed")
                return None
                
        except Exception as e:
            self.logger.error(f"Error running prompt {prompt_name}: {e}")
            return None
            
    def _execute_claude_prompt(self, prompt_content, prompt_name, session_id=None):
        """Execute the prompt using Claude Code SDK."""
        try:
            self.logger.info(f"Executing Claude prompt: {prompt_name}")
            self.logger.info(f"Prompt content length: {len(prompt_content)} characters")
            
            # Check if Claude client is available
            if self.claude_client is None:
                self.logger.warning("Claude Code SDK client not available, using fallback")
                return self._fallback_execution(prompt_content, prompt_name)
            
            options = ClaudeCodeOptions(
                cwd=os.getcwd(),
                permission_mode='bypassPermissions',
                resume=session_id,
            )

            # 1. Claude Code SDK client is already initialized in __init__
            # 2. Send the prompt to Claude using async query function
            try:
                import asyncio
                
                async def run_query():
                    response_parts = []
                    session_id = None
                    async for message in self.claude_client(prompt=prompt_content, options=options):
                        # Extract only the text content from the message
                        if hasattr(message, 'content') and message.content:
                            if isinstance(message.content, list):
                                for block in message.content:
                                    if hasattr(block, 'text'):
                                        response_parts.append(block.text)
                            elif hasattr(message.content, 'text'):
                                response_parts.append(message.content.text)
                            elif isinstance(message.content, str):
                                response_parts.append(message.content)
                        elif hasattr(message, 'text'):
                            response_parts.append(message.text)
                        elif hasattr(message, 'result') and isinstance(message.result, str):
                            response_parts.append(message.result)
                        elif hasattr(message, 'data') and isinstance(message.data, dict):
                            session_id = message.data['session_id']
                    return ''.join(response_parts), session_id

                # Run the async query
                processed_content, session_id = asyncio.run(run_query())
                self.logger.info("Successfully received response from Claude")
                
                # 4. Log the successful execution (outputs are handled by caller)
                self.logger.info(f"Claude response length: {len(processed_content)} characters")
                
                return processed_content, session_id
                
            except AttributeError as e:
                self.logger.error(f"Claude SDK API mismatch: {e}")
                return self._fallback_execution(prompt_content, prompt_name)
            except Exception as e:
                self.logger.error(f"Claude API call failed: {e}")
                return self._fallback_execution(prompt_content, prompt_name)
            
        except Exception as e:
            self.logger.error(f"Claude execution error: {e}")
            return None
            
    def _fallback_execution(self, prompt_content, prompt_name):
        """Fallback execution when Claude SDK is not available."""
        self.logger.info("Using fallback execution - returning processed prompt template")
        
        # Simple fallback: return a basic response based on the prompt
        fallback_response = f"""# Generated Response for {prompt_name}

Based on the provided prompt and parameters, here is the generated content:

{prompt_content}

---
*Note: This is a fallback response. For AI-generated content, ensure Claude Code SDK is properly configured.*
"""
        return fallback_response

