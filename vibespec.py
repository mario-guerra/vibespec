import os
import time
from openai import AzureOpenAI, APIConnectionError
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

load_dotenv()

def print_banner():
    banner = r"""
   
____   ____._____.            _________                     
\   \ /   /|__\_ |__   ____  /   _____/_____   ____   ____  
 \   Y   / |  || __ \_/ __ \ \_____  \\____ \_/ __ \_/ ___\ 
  \     /  |  || \_\ \  ___/ /        \  |_> >  ___/\  \___ 
   \___/   |__||___  /\___  >_______  /   __/ \___  >\___  >
                   \/     \/        \/|__|        \/     \/ 


VibeSpec: Hello! I'm VibeSpec, your helpful assistant for creating API definitions using TypeSpec. My goal is to take your ideas and turn them into clear, structured service definitions that are easy to understand and implement. If you have a concept in mind for a service or API, I can guide you through the process of defining it, making sure we cover all the important aspects like data models, error handling, and operations.                                          
    """
    print(banner)

print_banner()

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

# Setup speech synthesizer
try:
    speech_config = speechsdk.SpeechConfig(
        endpoint=f"wss://{os.getenv('AZURE_TTS_REGION')}.tts.speech.microsoft.com/cognitiveservices/websocket/v2",
        subscription=os.getenv("AZURE_TTS_API_KEY")
    )
    speech_config.speech_synthesis_voice_name = "en-US-BrianMultilingualNeural"
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
    speech_synthesizer.synthesizing.connect(lambda evt: print("[audio]", end=""))

    # Set timeout values to avoid SDK canceling the request when GPT latency is too high
    speech_config.set_property(speechsdk.PropertyId.SpeechSynthesis_FrameTimeoutInterval, "100000000")
    speech_config.set_property(speechsdk.PropertyId.SpeechSynthesis_RtfTimeoutThreshold, "10")
except Exception as e:
    print(f"Error setting up speech synthesizer: {e}")
    exit(1)

# Updated Initial system message
messages = [
    {
        "role": "system",
        "content": "You are an expert in defining APIs using TypeSpec from natural language descriptions of ideas a user shares with you for building a service, and we refer to you as 'VibeSpec'. Your mission is to take a user's input and flesh that out into a service that is defined in TypeSpec. You gently guide the user to a successful API definition, offering helpful suggestions when asked and pointing out ways to make the API more robust, maintainable, performant, and descriptive. You speak in simple terms and avoid using technical jargon, making no assumptions about the user's experience with API developement. When you have enough information to begin generating a TypeSpec file, you will tell the user you are ready to create a TypeSpec draft for them and you will ask the user for permission to proceed. When you receive permission to proceed, you will output flawless TypeSpec code *with proper comments for documentation* that can be copied to the user's project to be compiled without errors. You will iterate over the spec design till the user is satisfied with the end result. You *always* refer to the following canonical example as a template for generating syntatically correct TypeSpec spec creations, although it's not necessary to adhere to the structure or format, only refer to it as a syntax guide:\n\n```\nimport \"@typespec/http\";\nimport \"@typespec/versioning\";\n\nusing Http;\nusing Versioning;\n\n@service(#{ title: \"Meal Tracking App\" })\n@server(\"https://example.com\", \"Single server endpoint\")\n@versioned(Versions)\nnamespace MealTracker;\n\nenum Versions {\n  v1: \"1.0\",\n}\n\n// Model for a meal\nmodel Meal {\n  id: int32;\n  date: utcDateTime; // Date of the meal\n  name: string; // Name of the meal\n  calories: int32; // Total calories in the meal\n  macros: Macros; // Macronutrient breakdown\n  ingredients: string[]; // Ingredients used in the meal\n}\n\n// Model for tracking macronutrients\nmodel Macros {\n  protein: int32; // Grams of protein\n  carbohydrates: int32; // Grams of carbohydrates\n  fats: int32; // Grams of fats\n}\n\n// Model for user preferences\nmodel UserProfile {\n  userId: int32; // Unique identifier for the user\n  calorieGoal: int32; // Daily calorie goal\n  macroGoals: Macros; // Daily macro goals\n  dietaryRestrictions: string[]; // Dietary restrictions/preferences\n}\n\n// Model for AI-generated recipe suggestions\nmodel RecipeSuggestion {\n  title: string; // Suggested recipe title\n  ingredients: string[]; // List of suggested ingredients\n  calories: int32; // Total calories for the recipe\n  macros: Macros; // Macronutrient breakdown for the recipe\n}\n\n// Common parameters for requests\nmodel CommonParameters {\n  @header\n  requestID: string;\n}\n\n// Highlight-start\nmodel MealListResponse {\n  ...OkResponse;\n  ...Body<Meal[]>;\n}\n\nmodel MealResponse {\n  ...OkResponse;\n  ...Body<Meal>;\n}\n\nmodel UserProfileResponse {\n  ...OkResponse;\n  ...Body<UserProfile>;\n}\n\nmodel RecipeSuggestionResponse {\n  ...OkResponse;\n  ...Body<RecipeSuggestion[]>;\n}\n// Highlight-end\n\n@route(\"/meals\")\nnamespace Meals {\n  @get\n  op listMeals(...CommonParameters): MealListResponse;\n\n  @post\nop createMeal(@body meal: Meal): MealResponse;\n\n  @get\n  op getMeal(@path mealId: int32): MealResponse;\n\n  @route(\"/{mealId}\")\n  @put\n  op updateMeal(@path mealId: int32, @body meal: Meal): MealResponse;\n\n  @delete\n  op deleteMeal(@path mealId: int32): {\n    @statusCode statusCode: 204;\n  };\n}\n\n@route(\"/user\")\nnamespace User {\n  @get\n  op getUserProfile(...CommonParameters): UserProfileResponse;\n\n  @put\n  op updateUserProfile(@body profile: UserProfile): UserProfileResponse;\n}\n\n@route(\"/ai/suggestions\")\nnamespace AI {\n  @post\n  op getRecipeSuggestions(@body ingredients: string[], ...CommonParameters): RecipeSuggestionResponse;\n}\n\n@error\nmodel NotFoundError {\n  code: \"NOT_FOUND\";\n  message: string;\n}\n\n@error\nmodel ValidationError {\n  code: \"VALIDATION_ERROR\";\n  message: string;\n  details: string[];\n}\n\n@error\nmodel InternalServerError {\n  code: \"INTERNAL_SERVER_ERROR\";\n  message: string;\n}\n```"
    }
]

def chat_with_vibespec():
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == "exitnow":
            print("Exiting chat...")
            break

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

        print(f"\nVibeSpec: {response_text}")

        # Append the AI's response to the messages list!
        messages.append({"role": "assistant", "content": response_text})

if __name__ == "__main__":
    chat_with_vibespec()