from flask import Flask
from bulkSendToRegression import bucket
from flask import request

app = Flask(__name__)


@app.route('/')
def hello_world():
	return 'Hello World!'


@app.route('/sendToRegression', methods=['GET','POST'])
def send_to_regression():
	return bucket(request.args.get('pr',type=int))


if __name__ == '__main__':
	app.run(host = '0.0.0.0')
