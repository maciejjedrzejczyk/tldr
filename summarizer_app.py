import os
from flask import Flask, Response
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import html

app = Flask(__name__)

def fetch_website_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        # Extract text from paragraphs
        paragraphs = soup.find_all('p')
        content = ' '.join([p.get_text() for p in paragraphs])
        return content
    except requests.RequestException as e:
        return f"Error fetching website content: {str(e)}"

def summarize_with_ollama(content):
    try:
        ollama_url = "http://host.docker.internal:11434/api/generate"
        prompt = "Summarize the following text. Start with an executive summary of 200 words or less. Then, provide: 1) A one-sentence overview. 2) 3-5 key points. 3) Critical data or statistics. 4) 2-3 actionable items. 5) Any time-sensitive information. 6) Potential impact. Use bullet points for clarity. Text to summarize:\n\n{content}\n\nSummary:"

        payload = {
            "model": "llama3.2:1b",
            "prompt": prompt.format(content=content),
            "stream": False
        }
        response = requests.post(ollama_url, json=payload)
        response.raise_for_status()
        result = response.json()
        return result['response']
    except requests.RequestException as e:
        return f"Error communicating with Ollama: {str(e)}"

@app.route('/<path:url>', methods=['GET'])
def summarize(url):
    # Ensure the URL has a scheme
    if not urlparse(url).scheme:
        url = 'https://' + url

    content = fetch_website_content(url)
    
    if content.startswith("Error"):
        return Response(f"# Error\n\n{content}", mimetype='text/markdown')

    summary = summarize_with_ollama(content)
    
    if summary.startswith("Error"):
        return Response(f"# Error\n\n{summary}", mimetype='text/markdown')

    # Create Markdown output
    markdown_output = f"""
# Summary of {html.escape(url)}

{summary}

---
Summarized by Ollama with support of Llama3.2:1b model.
    """

    return Response(markdown_output, mimetype='text/markdown')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
