from flask import Flask, jsonify, request, make_response
from dbfunctions import get_details
import psycopg2
from dbfunctions import get_jobs
from decouple import config

application = Flask(__name__)


@application.route('/search')
def search():
	""" when someone types /search in the url this function will work to
	present what we want for this page """

	job_id = request.args.get('job_id', None)
	city = request.args.get('city', None)
	state_province = request.args.get('state_province', None)
	country = request.args.get('country', 'US')
	title = request.args.get('title', None)
	count = request.args.get('count', 50)
	before = request.args.get('before', None)
	after = request.args.get('after', None)
	seniority = request.args.get('seniority', None)
	salary_min = request.args.get('salary_min', None)
	salary_max = request.args.get('salary_max', None)
	with psycopg2.connect(
			dbname=config("DB_DB"),
			user=config("DB_USER"),
			password=config("DB_PASSWORD"),
			host=config("DB_HOST"),
			port=config("DB_PORT")
	) as psql_conn:
		output = get_jobs(
			psql_conn,
			count=count,
			city=city,
			state_province=state_province,
			country=country,
			title=title,
			salary_max=salary_max,
			salary_min=salary_min,
			before=before,
			after=after,
			seniority=seniority,
		)
	ret = {
		'count': len(output),
		'responses': output
	}
	return jsonify(ret)


@application.route('/details')
def details():
	""" when someone types /details in the url this function will work to
	present what we want for this page """
	# args = request.get_json()
	args = request.args  # Use query args for simplicity for now
	job_id = args.get('job_id', None)
	if job_id is None:
		output = {
			'error': 'job_id parameter is required'
		}
		return jsonify(output)
	with psycopg2.connect(
			dbname=config("DB_DB"),
			user=config("DB_USER"),
			password=config("DB_PASSWORD"),
			host=config("DB_HOST"),
			port=config("DB_PORT")
	) as psql_conn:
		output = get_details(job_id, psql_conn)
	return jsonify(output)


@application.before_request
def before_request():  # CORS preflight
	def _build_cors_prelight_response():
		response = make_response()
		response.headers.add("Access-Control-Allow-Origin", "*")
		response.headers.add("Access-Control-Allow-Headers", "*")
		response.headers.add("Access-Control-Allow-Methods", "*")
		return response
	if request.method == "OPTIONS":
		return _build_cors_prelight_response()


@application.after_request
def after_request(response):  # CORS headers
	header = response.headers
	header['Access-Control-Allow-Origin'] = '*'
	return response


if __name__ == "__main__":
	application.run()
