from flask import Blueprint, render_template, request, jsonify
from jinja2 import TemplateNotFound
from apps.API.utility import YahooAPI, IndicatorAPI

api_blueprint = Blueprint('api_blueprint', __name__, url_prefix='/api')

@api_blueprint.route('/data/<ticker>/<interval>', methods=['GET'])
def get_data(ticker, interval):
    try:
        yahoo_api = YahooAPI(ticker, interval)
        candlestick_data = yahoo_api.get_candlestick_data()
        line_data = yahoo_api.get_line_data()
        volume_data = yahoo_api.get_volume_data()
        return jsonify({'candlestick': candlestick_data, 'line': line_data, 'volume': volume_data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_blueprint.route('/sma/<string:ticker>/<string:period>/<int:sma_period>', methods=['GET'])
def get_sma(ticker, period, sma_period):
    try:
        yahoo_api = YahooAPI(ticker, period)
        sma_data = yahoo_api.get_sma_ind(sma_period)
        return jsonify(sma_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_blueprint.route('/<string:indicator>', methods=['POST'])
def get_indicator(indicator):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400

        indicator_api = IndicatorAPI(data)

        if hasattr(indicator_api, indicator):
            method = getattr(indicator_api, indicator)
            if callable(method):
                result = method()
                return jsonify(result), 200
            else:
                return jsonify({"error": "Indicator method is not callable"}), 400
        else:
            return jsonify({"error": "Unsupported indicator"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_blueprint.route('/view')
def view():
    try:
        return render_template('charts/test.html')
    except TemplateNotFound:
        return jsonify({"error": "Template not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


