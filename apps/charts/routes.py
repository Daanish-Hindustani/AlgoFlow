import uuid
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from jinja2 import TemplateNotFound
from apps.charts.db import data

charts_blueprint = Blueprint(
    'charts_blueprint',
    __name__,
    url_prefix='/chart'
)

# Route to render a specific chart based on chart_id
@charts_blueprint.route('/<string:chart_id>/', methods=['GET'])
def chart(chart_id):
    try:
        # Find the chart data by chart_id
        chart_data = next((chart for chart in data if chart['chart_id'] == chart_id), None)
        if chart_data is None:
            return jsonify({"error": "Chart not found"}), 404
        return render_template('charts/chart.html', chart_data=chart_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Route to handle initial chart creation or redirection
@charts_blueprint.route('/', methods=['GET', 'POST'])
def initial_chart():
    try:
        if request.method == 'GET':
            if data:
                # If there are charts in the database, redirect to the first one
                first_chart_id = data[0]['chart_id']
                return redirect(url_for('charts_blueprint.chart', chart_id=first_chart_id))
            else:
                # If no charts exist, create a new default chart and redirect to it
                new_chart = {
                    'chart_id': str(uuid.uuid4()),
                    'name': str(uuid.uuid4()),
                    'ticker': "AMZN",
                    'interval': "1d",
                    'chart_type': "bar",
                    'indicators': ["sma"]
                }
                data.append(new_chart)
                return redirect(url_for('charts_blueprint.chart', chart_id=new_chart["chart_id"]))
        elif request.method == 'POST':
            # Handling chart creation if requested via POST 
            new_chart = {
                'chart_id': str(uuid.uuid4()),
                'name': str(uuid.uuid4()),
                'ticker': request.json.get('ticker', "AMZN"),
                'interval': request.json.get('interval', "1d"),
                'chart_type': request.json.get('chart_type', "bar"),
                'indicators': request.json.get('indicators', ["sma"])
            }
            data.append(new_chart)
            return redirect(url_for('charts_blueprint.chart', chart_id=new_chart["chart_id"]))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Route to update a chart's specific field
@charts_blueprint.route('/update', methods=['POST'])
def update_chart():
    try:
        data_json = request.get_json()
        print(data_json)
        chart_id = data_json.get('chart_id')
        field = data_json.get('field')
        value = data_json.get('value')

        # Find the chart by chart_id and update the specified field
        chart_data = next((chart for chart in data if chart['chart_id'] == chart_id), None)
        if chart_data is None:
            return jsonify({"error": "Chart not found"}), 404

        chart_data[field] = value

        return jsonify({"success": True, "chart_data": chart_data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Route to delete a chart by chart_id
@charts_blueprint.route('/delete', methods=['POST'])
def delete_chart():
    try:
        data_json = request.get_json()
        chart_id = data_json.get('chart_id')

        # Remove the chart from data by chart_id
        global data
        data = [chart for chart in data if chart['chart_id'] != chart_id]

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

