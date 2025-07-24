import runpod

def handler(event):
    print("⚡ Handler triggered:", event)

    # Juste un test pour voir si ça fonctionne
    return {
        "message": "Handler works!",
        "input": event.get("input", {})
    }

runpod.serverless.start({"handler": handler})

