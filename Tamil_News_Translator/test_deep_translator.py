from deep_translator import GoogleTranslator

try:
    translator = GoogleTranslator(source='en', target='ta')
    result = translator.translate("Hello World")
    print(f"Original: Hello World")
    print(f"Tamil: {result}")
    print("✅ Translation working!")
    
    # Test with a longer text
    long_text = "The best laptop deals you can get for Amazon's October Prime Day"
    result2 = translator.translate(long_text)
    print(f"\nOriginal: {long_text}")
    print(f"Tamil: {result2}")
    print("✅ Long text translation working!")
    
except Exception as e:
    print(f"❌ Translation error: {e}")
