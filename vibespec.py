import re
import os
import time
import argparse
from openai import AzureOpenAI, APIConnectionError
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv
import pyttsx3

load_dotenv()

def print_banner():
    banner = r"""


 _    ___ __        _____
| |  / (_) /_  ___ / ___/____  ___  _____
| | / / / __ \/ _ \\__ \/ __ \/ _ \/ ___/
| |/ / / /_/ /  __/__/ / /_/ /  __/ /__
|___/_/_.___/\___/____/ .___/\___/\___/
                     /_/


VibeSpec: Hello! I'm VibeSpec, your helpful assistant for creating API definitions using TypeSpec. How can I help you?
    """
    print(banner)

print_banner()

# Initialize pyttsx3 engine
engine = pyttsx3.init()

# --- START: Code to list and set voice, uncomment to see what voices are available on your system ---
voices = engine.getProperty('voices')

# print("\n--- Available Voices ---")
# for idx, voice in enumerate(voices):
#     print(f"Voice {idx}:")
#     print(f"  ID: {voice.id}")
#     print(f"  Name: {voice.name}")
#     print(f"  Lang: {voice.languages}")
#     print(f"  Gender: {voice.gender}")
#     print(f"  Age: {voice.age}")
#     print("-" * 10)

# --- CHOOSE A VOICE ---
# Find the ID of the voice you want from the printed list above.
# For example, let's say you want to use the second voice in the list (index 1).
# Replace 'voices[1].id' with the actual ID string you want to use.
# If you only have one voice, you might use voices[0].id
try:
    # --- MODIFY THIS LINE ---
    # Example: Use the second voice found. You MUST check the output above
    # and select the appropriate index or copy the full ID string.
    desired_voice_id = voices[1].id # <--- CHANGE THIS INDEX OR ID
    # Alternatively, if you know the specific ID string, you can hardcode it:
    # desired_voice_id = "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0" # Example for Windows Zira

    # print(f"\nAttempting to set voice to ID: {desired_voice_id}")
    engine.setProperty('voice', desired_voice_id)
    # print("Voice set successfully.")

    # Optional: Adjust Rate and Volume
    engine.setProperty('rate', 220)  # Speed percent (can go over 100)
    # engine.setProperty('volume', 0.9) # Volume 0-1

except IndexError:
    print(f"\nError: Could not find voice at the specified index. Using default voice.")
except Exception as e:
    print(f"\nError setting voice: {e}. Using default voice.")

# --- Optional: Test the selected voice ---
# engine.say("Testing the selected voice.")
# engine.runAndWait()
# # --- END: Code to list and set voice ---

# Setup AzureOpenAI client
try:
    gpt_client = AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_API_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION")
    )
except Exception as e:
    print(f"Error setting up AzureOpenAI client: {e}")
    exit(1)

# Updated Initial system message
messages = [
    {
      "role": "system",
      "content": "You are an expert in defining APIs using TypeSpec from natural language descriptions of ideas a user shares with you for building a service, and we refer to you as 'VibeSpec'. Your mission is to take a user's input and flesh that out into a service that is defined in TypeSpec. You gently guide the user to a successful API definition, offering helpful suggestions when asked and pointing out ways to make the API more robust, maintainable, performant, and descriptive. You speak concisely in simple terms and avoid using technical jargon, making no assumptions about the user's experience with API development. Your conversational responses will be spoken aloud via text-to-speech, except for the TypeSpec code you write, which will be printed to the console. Therefore, for any communication other than providing the TypeSpec code, you *must* use conversational language and plain text, no markdown, bullet points or other elements that are good for reading but not for being spoken aloud. When you have enough information to begin generating a TypeSpec file, you will tell the user you are ready to create a TypeSpec draft for them and you will ask the user for permission to proceed. When you receive permission to proceed, you will output flawless TypeSpec code with proper comments for documentation that can be copied to the user's project to be compiled without errors. You will iterate over the spec design till the user is satisfied with the end result. You always refer to the following canonical examples as templates for generating syntactically correct TypeSpec spec creations. It's not necessary to adhere to the structure or format, only refer to them as a syntax guide.\n\nExample 1:\n```typescript\nimport \"@typespec/http\";\n\nusing Http;\n\n@service(#{ title: \"Meal Tracking App\" })\n@server(\"https://example.com\", \"Single server endpoint\")\nnamespace MealTracker;\n\n// Model for a meal\nmodel Meal {\n  id: int32;\n  date: utcDateTime; // Date of the meal\n  name: string; // Name of the meal\n  calories: int32; // Total calories in the meal\n  macros: Macros; // Macronutrient breakdown\n  ingredients: string[]; // Ingredients used in the meal\n}\n\n// Model for tracking macronutrients\nmodel Macros {\n  protein: int32; // Grams of protein\n  carbohydrates: int32; // Grams of fats\n}\n\n// Model for user preferences\nmodel UserProfile {\n  userId: int32; // Unique identifier for the user\n  calorieGoal: int32; // Daily calorie goal\n  macroGoals: Macros; // Daily macro goals\n  dietaryRestrictions: string[]; // Dietary restrictions/preferences\n}\n\n// Model for AI-generated recipe suggestions\nmodel RecipeSuggestion {\n  title: string; // Suggested recipe title\n  ingredients: string[]; // List of suggested ingredients\n  calories: int32; // Total calories for the recipe\n  macros: Macros; // Macronutrient breakdown for the recipe\n}\n\n// Common parameters for requests\nmodel CommonParameters {\n  @header\n  requestID: string;\n}\n\n// Highlight-start\nmodel MealListResponse {\n  ...OkResponse;\n  ...Body<Meal[]>;\n}\n\nmodel MealResponse {\n  ...OkResponse;\n  ...Body<Meal>;\n}\n\nmodel UserProfileResponse {\n  ...OkResponse;\n  ...Body<UserProfile>;\n}\n\nmodel RecipeSuggestionResponse {\n  ...OkResponse;\n  ...Body<RecipeSuggestion[]>;\n}\n// Highlight-end\n@route(\"/meals\")\nnamespace Meals {\n  @get\n  op listMeals(...CommonParameters): MealListResponse;\n\n  @post\n  op createMeal(@body meal: Meal): MealResponse;\n\n  @get\n  op getMeal(@path mealId: int32): MealResponse;\n\n  @route(\"/{mealId}\")\n  @put\n  op updateMeal(@path mealId: int32, @body meal: Meal): MealResponse;\n\n  @delete\n  op deleteMeal(@path mealId: int32): {\n    @statusCode statusCode: 204;\n  };\n}\n\n@route(\"/user\")\nnamespace User {\n  @get\n  op getUserProfile(...CommonParameters): UserProfileResponse;\n\n  @put\n  op updateUserProfile(@body profile: UserProfile): UserProfileResponse;\n}\n\n@route(\"/ai/suggestions\")\nnamespace AI {\n  @post\n  op getRecipeSuggestions(@body ingredients: string[], ...CommonParameters): RecipeSuggestionResponse;\n}\n\n@error\nmodel NotFoundError {\n  code: \"NOT_FOUND\";\n  message: string;\n}\n\n@error\nmodel ValidationError {\n  code: \"VALIDATION_ERROR\";\n  message: string;\n  details: string[];\n}\n\n@error\nmodel InternalServerError {\n  code: \"INTERNAL_SERVER_ERROR\";\n  message: string;\n}\n```\n\nExample 2:\n```typescript\nimport \"@typespec/http\";\n\nusing Http;\n\n// Define the service\n@service(#{ title: \"Task Tracking App\" })\n@server(\"https://example.com\", \"Single server endpoint for Task Tracking API\")\nnamespace TaskTracker;\n\n// Task Priority Enum\nenum Priority {\n  Low: \"Low importance\";\n  Medium: \"Medium importance\";\n  High: \"High importance\";\n  Critical: \"Critical importance\";\n}\n\n// Task Status Enum\nenum Status {\n  ToDo: \"Task has not yet been started.\";\n  InProgress: \"Task is currently being worked on.\";\n  Completed: \"Task has been completed.\";\n  Blocked: \"Task is blocked and cannot move forward.\";\n}\n\n// Model for a task\nmodel Task {\n  id: int32; // Unique task identifier\n  title: string; // Title of the task\n  description?: string; // Optional description of the task\n  dueDate: utcDateTime; // Due date for the task\n  priority: Priority; // Priority level of the task\n  status: Status; // Current status of the task\n  stakeholders: string[]; // List of people dependent on this task\n}\n\n// Model for listing tasks (filtered results)\nmodel TaskListResponse {\n  ...OkResponse;\n  ...Body<Task[]>;\n}\n\n// Model for a single task response\nmodel TaskResponse {\n  ...OkResponse;\n  ...Body<Task>;\n}\n\n// Endpoint parameters for common request metadata\nmodel CommonParameters {\n  @header\n  requestID: string;\n}\n\n@route(\"/tasks\")\nnamespace Tasks {\n  // Get all tasks\n  @get\n  op getAllTasks(...CommonParameters): TaskListResponse;\n\n  // Get tasks filtered by due date query parameter (e.g., today or this week)\n  @route(\"/filtered\")\n  @get\n  op listFilteredTasks(\n    @query filter: string, // e.g., \"today\", \"this-week\"\n    ...CommonParameters\n  ): TaskListResponse;\n\n  // Create a new task\n  @post\n  op createTask(@body task: Task): TaskResponse;\n\n  // Get a task by ID\n  @route(\"/{taskId}\")\n  @get\n  op getTask(@path taskId: int32): TaskResponse;\n\n  // Update a task by ID\n  @route(\"/{taskId}\")\n  @put\n  op updateTask(@path taskId: int32, @body task: Task): TaskResponse;\n\n  // Delete a task by ID\n  @route(\"/{taskId}\")\n  @delete\n  op deleteTask(@path taskId: int32): {\n    @statusCode statusCode: 204;\n  };\n}\n\n@route(\"/ai\")\nnamespace AI {\n  // Get task prioritization advice from the AI assistant\n  @post\n  @route(\"/prioritize\")\n  op prioritizeTasks(\n    @body context: string, // Example: \"Help me prioritize my tasks for today.\"\n    ...CommonParameters\n  ): AIAdviceResponse;\n\n  model AIAdviceResponse {\n    ...OkResponse;\n    ...Body<string>; // AI response as text-based advice\n  }\n\n  // Query tasks due today or this week with AI insights\n  @post\n  op getTaskSummary(@body summaryType: string, ...CommonParameters): TaskSummaryResponse;\n\n  model TaskSummaryResponse {\n    ...OkResponse;\n    ...Body<string>; // AI-generated summary of tasks for \"today\" or \"this week\"\n  }\n}\n\n@error\nmodel NotFoundError {\n  code: \"NOT_FOUND\";\n  message: string;\n}\n\n@error\nmodel ValidationError {\n  code: \"VALIDATION_ERROR\";\n  message: string;\n  details: string[];\n}\n\n@error\nmodel InternalServerError {\n  code: \"INTERNAL_SERVER_ERROR\";\n  message: string;\n}\n```"
    }
]

def recognize_from_microphone():
    # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
    speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'), region=os.environ.get('SPEECH_REGION'))
    speech_config.speech_recognition_language = "en-US"

    speech_config.set_property(speechsdk.PropertyId.SpeechServiceConnection_EndSilenceTimeoutMs, "6000")  # 6 seconds

    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    print("Speak into your microphone.")
    speech_recognition_result = speech_recognizer.recognize_once_async().get()

    if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return speech_recognition_result.text
    elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized: {}".format(speech_recognition_result.no_match_details))
        return None
    elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_recognition_result.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))
            print("Did you set the speech resource key and region values?")
        return None

def speak_text(text):
    """Speaks the given text using pyttsx3."""
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Error during local speech synthesis: {e}")

def chat_with_vibespec(use_text_input=True):
    """Handles the chat loop with VibeSpec, using speech or text input."""
    while True:
        if use_text_input:
            user_input = input("\nYou (Text): ")
        else:
            user_input = recognize_from_microphone()
            if user_input:
                print(f"\nYou (Speech): {user_input}")
            else:
                print("\nNo speech recognized. Please try again or use text input.")
                continue  # Skip to the next loop iteration

        if user_input: # Check if user_input is not None or empty first
            normalized_input = user_input.lower().strip() # Normalize

            # --- MODIFIED REGEX EXIT CHECK ---
            # Define the regex pattern:
            # ^       - Start of the string
            # exit    - Literal "exit"
            # \s?     - Optional whitespace (zero or one space)
            # now     - Literal "now"
            # \.?     - Optional literal period (needs backslash escape)
            # $       - End of the string
            exit_pattern = r"^exit\s?now\.?$"

            # Use re.fullmatch to check if the entire normalized input matches the pattern
            if re.fullmatch(exit_pattern, normalized_input):
                print("Exiting chat...")
                break
            # --- END REGEX EXIT CHECK ---

        if not user_input:
            continue

        messages.append({"role": "user", "content": user_input})

        retries = 3
        for attempt in range(retries):
            try:
                completion = gpt_client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages,
                    stream=True
                )
                break
            except APIConnectionError as e:
                print(f"Connection error: {e}. Retrying ({attempt + 1}/{retries})...")
                time.sleep(2)
        else:
            print("Failed to connect after several attempts. Please check your network and try again later.")
            continue

        response_text = ""
        for chunk in completion:
            if len(chunk.choices) > 0:
                chunk_text = chunk.choices[0].delta.content
                if chunk_text:
                    response_text += chunk_text

        # Check if the response is TypeSpec code
        if "```" in response_text:  # Crude check
            print("\nVibeSpec (TypeSpec):\n" + response_text) # Print the full code block to the console
        else:
            print(f"\nVibeSpec: {response_text}")
            speak_text(response_text) # only speak the conversational output

        # Append the AI's response to the messages list!
        messages.append({"role": "assistant", "content": response_text})

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="VibeSpec - TypeSpec API Definition Assistant")
    parser.add_argument("--text", action="store_true", help="Use text input instead of speech recognition.")
    args = parser.parse_args()
    speak_text("Hello! I'm VibeSpec, your helpful assistant for creating API definitions using TypeSpec. How can I help you?")
    chat_with_vibespec(use_text_input=args.text)