# Personal Assistant - Modular Structure

This project has been refactored into a modular structure for better organization and maintainability.

## File Structure

### Core Modules

- **`models.py`** - Pydantic models and data structures
- **`config.py`** - Configuration management and environment variables
- **`screen_capture.py`** - Screen capture and OCR functionality
- **`window_utils.py`** - Window management and process information
- **`web_search.py`** - Web search functionality using DuckDuckGo
- **`ai_client.py`** - AI/LLM client management
- **`api_routes.py`** - FastAPI routes and endpoints

### Main Applications

- **`backend.py`** - Refactored FastAPI backend using modular structure
- **`assistant_daemon.py`** - Refactored GUI daemon using modular structure

## Key Benefits

1. **Separation of Concerns**: Each module has a single responsibility
2. **Better Testability**: Individual modules can be tested in isolation
3. **Improved Maintainability**: Changes to one feature don't affect others
4. **Reusability**: Modules can be imported and used independently
5. **Cleaner Code**: Reduced complexity in main application files

## Module Dependencies

```
backend.py
├── api_routes.py
│   ├── models.py
│   ├── screen_capture.py
│   ├── window_utils.py
│   ├── web_search.py
│   └── ai_client.py
└── config.py

assistant_daemon.py
├── models.py
├── config.py
├── screen_capture.py
├── window_utils.py
├── web_search.py
└── ai_client.py
```

## Usage

### Running the Backend
```bash
python backend.py
```

### Running the Daemon
```bash
python assistant_daemon.py
```

## Configuration

All configuration is managed through `config.py` and environment variables. The configuration system automatically detects available optional dependencies and provides appropriate defaults.

## Optional Dependencies

The system gracefully handles missing optional dependencies:
- `mss` - Screen capture
- `PIL` - Image processing
- `pytesseract` - OCR functionality
- `pynput` - Keyboard shortcuts
- `cerebras` - AI client
- `duckduckgo_search` - Web search

## API Endpoints

The modular structure provides additional API endpoints:
- `/health` - Health check
- `/config` - Configuration information
- `/capture/single` - Single screen capture
- `/window/active` - Active window information
- `/search` - Web search
- `/ai/test` - AI connection test
