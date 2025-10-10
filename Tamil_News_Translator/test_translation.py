from googletrans import Translator

translator = Translator()

try:
    # Test translation
    result = translator.translate("Hello World", src='en', dest='ta')
    print(f"Original: Hello World")
    print(f"Tamil: {result.text}")
    print("Translation working!")
except Exception as e:
    print(f"Translation error: {e}")





