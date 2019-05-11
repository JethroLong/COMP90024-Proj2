from flask import Flask, render_template

from web_flask.plot.figure_plot import Plotter

web_app = Flask(__name__)


@web_app.route('/home')
def home():
    script = []
    div = []
    plotter = Plotter()

    # draw figures
    temp_script, temp_div = plotter.hashtag_plot(doc_id='trending_hashtags', db_name='results')
    script.append(temp_script)
    div.append(temp_div)

    # tweets time distribution
    temp_script, temp_div = plotter.time_distribution(doc_id='time_distribution', db_name='results')
    script.append(temp_script)
    div.append(temp_div)

    return render_template('index.html', script=script, div=div)


@web_app.route('/sentiment')
def sentiment():
    script = []
    div = []
    plotter = Plotter()

    # interactive map
    temp_script, temp_div = plotter.interactive_map(doc_id='sentiment_distribution', db_name='results')
    script.append(temp_script)
    div.append(temp_div)

    return render_template('sentiment.html', script=script, div=div)


if __name__ == '__main__':
    web_app.run(host="0.0.0.0", port=5000, debug=True)