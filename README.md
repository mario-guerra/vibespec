# VibeSpec

VibeSpec is an AI-powered assistant that helps you create API definitions using TypeSpec from natural language descriptions. It converts your service ideas into structured, well-documented TypeSpec definitions that are ready to implement.

```
 _    ___ __        _____
| |  / (_) /_  ___ / ___/____  ___  _____
| | / / / __ \/ _ \\__ \/ __ \/ _ \/ ___/
| |/ / / /_/ /  __/__/ / /_/ /  __/ /__
|___/_/_.___/\___/____/ .___/\___/\___/
                     /_/
```

## Features

- **Conversational Interface**: Describe your API needs in natural language.
- **Guided Design Process**: VibeSpec helps you refine your API definitions iteratively.
- **TypeSpec Code Generation**: Produces syntactically correct TypeSpec code with proper documentation.
- **Best Practice Recommendations**: Suggests improvements for robustness, maintainability, and performance.
- **Text-to-Speech Support**: Uses `pyttsx3` for local speech synthesis.
- **Speech Recognition**: Supports microphone input using Azure Cognitive Services Speech SDK.
- **Exit Command**: Allows users to exit the session by typing "exitnow" or saying it via speech input.

## Prerequisites

- Python 3.7+
- Azure OpenAI API access
- Azure Cognitive Services Speech SDK access
- `pyttsx3` for local text-to-speech

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/vibespec.git
   cd vibespec
   ```

2. Install dependencies:
   ```
   pip install openai azure-cognitiveservices-speech python-dotenv pyttsx3
   ```

3. Create a `.env` file in the project root with the following variables:
   ```
   AZURE_OPENAI_API_ENDPOINT=your_azure_openai_endpoint
   AZURE_OPENAI_API_KEY=your_azure_openai_key
   AZURE_OPENAI_API_VERSION=your_azure_openai_version
   AZURE_TTS_REGION=your_azure_tts_region
   AZURE_TTS_API_KEY=your_azure_tts_key
   SPEECH_KEY=your_azure_speech_key
   SPEECH_REGION=your_azure_speech_region
   ```

## Usage

1. Start VibeSpec:
   ```
   python vibespec.py --text  # For text input
   python vibespec.py         # For speech input
   ```

2. Describe your API or service requirements in natural language.

3. VibeSpec will guide you through refining your API design, asking clarifying questions when needed.

4. When you're ready for code generation, VibeSpec will ask for your permission to create a TypeSpec draft.

5. Review the generated TypeSpec code and iterate as needed.

6. Type `exitnow` or say "exit now" to end the session.

## Example Workflow

1. **User**: "I want to create an API for a pet adoption service."
2. **VibeSpec**: Asks about specific requirements, data models, and operations.
3. **User**: Provides details about pets, adoption process, etc.
4. **VibeSpec**: "I'm ready to create a TypeSpec draft for your pet adoption service. Would you like me to proceed?"
5. **User**: "Yes, please."
6. **VibeSpec**: Generates complete TypeSpec code for the pet adoption service API.

## How It Works

VibeSpec leverages Azure OpenAI's GPT-4 models to understand your requirements and generate TypeSpec definitions. The assistant is designed to:

1. Parse your natural language descriptions.
2. Guide you to a comprehensive API design.
3. Generate valid TypeSpec code with proper documentation.
4. Help you refine the design iteratively.

## TypeSpec Integration

The generated TypeSpec code follows best practices and can be directly used with the TypeSpec compiler. The output includes:

- Service definition with versioning.
- Data models with documentation.
- Operation specifications with parameters and responses.
- Error handling definitions.

## Troubleshooting

- If you encounter connection errors, the application will automatically retry up to 3 times.
- Check your `.env` file if you get authentication errors.
- Ensure you have proper network connectivity to Azure services.

## License

[MIT License](LICENSE)
