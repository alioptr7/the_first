try:
    import api.main
    print("Import successful - API module loaded")
    print(f"FastAPI app: {api.main.app}")
except Exception as e:
    print(f"Import failed: {e}")
    import traceback
    traceback.print_exc()
