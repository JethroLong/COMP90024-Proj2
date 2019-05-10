from flask import Flask, render_template

from flask.plot.figure_plot import Plotter

web_app = Flask(__name__)


@web_app.route('/home')
def home():
    script = []
    div = []
    plotter = Plotter()

    # draw figures
    temp_script, temp_div = plotter.hashtag_plot(doc_id='trending_hashtags', db_name='test_db')
    script.append(temp_script)
    div.append(temp_div)

    temp_script, temp_div = plotter.tweets_hour_breakdown(doc_id='time_distribution', db_name='test_db')
    script.append(temp_script)
    div.append(temp_div)

    return render_template('index.html', script=script, div=div)


@web_app.route('/home/sentiment')
def sentiment():
    script = []
    div = []
    plotter = Plotter()

    temp_script, temp_div = plotter.interactive_map(doc_id='sentiment_distribution', db_name='test_db')
    script.append(temp_script)
    div.append(temp_div)

    return render_template('index.html', script=script, div=div)



if __name__ == '__main__':
    web_app.run(host="0.0.0.0", port=5000, debug=True)