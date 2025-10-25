# System Prompt Configuration

The Personal Assistant now supports configurable system prompts for the AI model. You can set and change the system prompt in multiple ways.

## 🔧 Configuration Methods

### 1. Environment Variable (Permanent)

Add to your `.env` file:

```env
ASSISTANT_SYSTEM_PROMPT=You are a helpful personal assistant. Be concise and helpful.
```

### 2. Runtime API Updates (Temporary)

#### Get Current System Prompt
```bash
GET http://localhost:8000/config/system-prompt
```

Response:
```json
{
  "system_prompt": "You are a helpful personal assistant. Be concise and helpful.",
  "model": "llama3.1-8b",
  "temperature": 0.2,
  "top_p": 0.9
}
```

#### Update System Prompt
```bash
POST http://localhost:8000/config/system-prompt
Content-Type: application/json

{
  "system_prompt": "You are an expert coding assistant. Provide detailed, accurate technical solutions."
}
```

#### Update Full AI Configuration
```bash
POST http://localhost:8000/config/ai
Content-Type: application/json

{
  "system_prompt": "You are a creative writing assistant. Help with storytelling and creative projects.",
  "model": "llama3.1-8b",
  "temperature": 0.7,
  "top_p": 0.9
}
```

## 🎯 Example System Prompts

### Coding Assistant
```
You are an expert coding assistant. Provide detailed, accurate technical solutions. Always include code examples and explain your reasoning.
```

### Creative Writing Assistant
```
You are a creative writing assistant. Help with storytelling, character development, and creative projects. Be imaginative and inspiring.
```

### Technical Documentation Assistant
```
You are a technical documentation specialist. Help create clear, comprehensive documentation. Focus on accuracy and user-friendliness.
```

### General Assistant
```
You are a helpful personal assistant. Be concise and helpful. Adapt your communication style to the user's needs.
```

### Screen-Aware Assistant
```
You are a screen-aware personal assistant. You can see and understand what's on the user's screen through OCR. Use this information to provide contextually relevant help.
```

## 🔄 Configuration Persistence

- **Environment Variable**: Changes persist across server restarts
- **API Updates**: Changes are temporary and reset when server restarts
- **Recommended**: Use environment variables for permanent changes

## 🚀 Usage Examples

### Python Script
```python
import requests

# Get current prompt
response = requests.get('http://localhost:8000/config/system-prompt')
current = response.json()['system_prompt']
print(f"Current: {current}")

# Update prompt
new_prompt = "You are a data analysis expert. Help with data interpretation and visualization."
response = requests.post('http://localhost:8000/config/system-prompt', 
                        json={'system_prompt': new_prompt})
print(f"Updated: {response.json()['success']}")
```

### cURL Commands
```bash
# Get current configuration
curl http://localhost:8000/config/system-prompt

# Update system prompt
curl -X POST http://localhost:8000/config/system-prompt \
  -H "Content-Type: application/json" \
  -d '{"system_prompt": "You are a helpful assistant."}'

# Update full AI config
curl -X POST http://localhost:8000/config/ai \
  -H "Content-Type: application/json" \
  -d '{"system_prompt": "You are a coding expert.", "temperature": 0.3}'
```

## 📝 Notes

- System prompt changes take effect immediately for new chat requests
- The system prompt influences how the AI responds to all queries
- Choose prompts that match your intended use case
- Test different prompts to find what works best for your needs
