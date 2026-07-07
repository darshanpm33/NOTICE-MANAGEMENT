import webbrowser
url = "https://xkcd.com/353/"
print(f"Attempting to open {url}...")
result = webbrowser.open(url)
print(f"Result of webbrowser.open: {result}")
if result:
    print("Browser should have opened!")
else:
    print("FAILED to open browser via webbrowser module.")
