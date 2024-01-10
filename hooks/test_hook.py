#Sure, here is a simple Python script using Flask to create a webhook. This webhook will listen for POST requests at the `/webhook` endpoint.
#
#```python
from flask import Flask, request

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def respond():
    print(request.json)
    return {'status': 'success'}, 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)
#```
#
#To test this webhook, you can use `curl` or any HTTP client to send a POST request. Here is an example using `curl`:
#
#```bash
#curl -X POST -H "Content-Type: application/json" -d '{"test": "data"}' http://localhost:5000/webhook
#```
#
#This will send a POST request with JSON data `{"test": "data"}` to the webhook. The webhook will print the received JSON data and respond with `{'status': 'success'}`.
#
#Please note that you need to have Flask installed in your Python environment. If you haven't installed Flask, you can install it using pip:
#
#```bash
#pip install flask
#```
