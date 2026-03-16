"""
Test Script - Verify LangChain Setup
Run this BEFORE the main app to ensure everything works
"""

def test_imports():
    """Test if all required libraries are installed"""
    print("="*60)
    print("TESTING IMPORTS")
    print("="*60)
    
    tests = [
        ("langchain", "LangChain"),
        ("openai", "OpenAI"),
        ("chromadb", "ChromaDB"),
        ("streamlit", "Streamlit"),
        ("tiktoken", "Tiktoken")
    ]
    
    all_passed = True
    
    for module, name in tests:
        try:
            __import__(module)
            print(f"✅ {name:15} - Installed")
        except ImportError:
            print(f"❌ {name:15} - NOT installed")
            all_passed = False
    
    print("="*60)
    
    if all_passed:
        print("\n✅ ALL LIBRARIES INSTALLED!")
        print("You can now run the main application:")
        print("  streamlit run langchain_corrective_rag.py")
    else:
        print("\n❌ SOME LIBRARIES MISSING!")
        print("Please install missing libraries:")
        print("  pip install -r requirements_langchain.txt")
    
    return all_passed


def test_langchain_basic():
    """Test basic LangChain functionality"""
    print("\n" + "="*60)
    print("TESTING LANGCHAIN BASIC FUNCTIONALITY")
    print("="*60)
    
    try:
        from langchain.prompts import PromptTemplate
        
        # Create a simple prompt
        template = "Tell me about {topic}"
        prompt = PromptTemplate(template=template, input_variables=["topic"])
        
        result = prompt.format(topic="AI")
        
        if "AI" in result:
            print("✅ LangChain PromptTemplate works!")
            print(f"   Test output: {result}")
            return True
        else:
            print("❌ LangChain test failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing LangChain: {e}")
        return False


def test_openai_connection():
    """Test OpenAI API connection"""
    print("\n" + "="*60)
    print("TESTING OPENAI API CONNECTION")
    print("="*60)
    
    import openai
    
    print("\nPlease enter your OpenAI API key:")
    print("(starts with 'sk-')")
    api_key = input("API Key: ").strip()
    
    if not api_key:
        print("❌ No API key provided. Skipping OpenAI test.")
        return False
    
    if not api_key.startswith('sk-'):
        print("⚠️  Warning: API key should start with 'sk-'")
    
    print("\n🔧 Testing API connection...")
    
    try:
        client = openai.OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Say 'Test successful!'"}
            ],
            max_tokens=20
        )
        
        result = response.choices[0].message.content
        
        print("✅ OpenAI API connection successful!")
        print(f"   Response: {result}")
        return True
        
    except openai.AuthenticationError:
        print("❌ Authentication failed - Invalid API key")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    print("\n" + "="*60)
    print("LANGCHAIN CORRECTIVE RAG - SETUP TEST")
    print("="*60)
    print("\nThis script will verify your setup is correct.\n")
    
    # Test 1: Imports
    imports_ok = test_imports()
    
    if not imports_ok:
        print("\n⚠️  Please install missing libraries before continuing.")
        input("\nPress Enter to exit...")
        return
    
    # Test 2: LangChain basic functionality
    langchain_ok = test_langchain_basic()
    
    # Test 3: OpenAI API (optional)
    print("\n" + "="*60)
    print("Would you like to test your OpenAI API key? (y/n)")
    test_api = input("Choice: ").strip().lower()
    
    if test_api == 'y':
        openai_ok = test_openai_connection()
    else:
        print("Skipping OpenAI API test.")
        openai_ok = True
    
    # Final summary
    print("\n" + "="*60)
    print("FINAL SUMMARY")
    print("="*60)
    
    if imports_ok and langchain_ok and openai_ok:
        print("\n🎉 ALL TESTS PASSED!")
        print("\nYou're ready to run the main application:")
        print("\n  streamlit run langchain_corrective_rag.py\n")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
    
    print("="*60)
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
