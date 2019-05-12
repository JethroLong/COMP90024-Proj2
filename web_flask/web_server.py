from flask import Flask, render_template

from plot.draw_map import DrawMap
from plot.figure_plot import Plotter

web_app = Flask(__name__)


@web_app.route('/home')
def home():
    script = []
    div = []
    plotter = Plotter()

    # draw figures
    # Trending hashtags -- 0
    temp_script, temp_div = plotter.hashtag_plot(doc_id='trending_hashtags', db_name='results')
    script.append(temp_script)
    div.append(temp_div)

    # tweets time distribution --1
    temp_script, temp_div = plotter.time_distribution(doc_id='time_distribution', db_name='results')
    script.append(temp_script)
    div.append(temp_div)

    # education --2
    temp_script, temp_div = plotter.time_distribution(doc_id='time_distribution', db_name='results')
    script.append(temp_script)
    div.append(temp_div)

    return render_template('index.html', script=script, div=div)


@web_app.route('/sentiment')
def sentiment():
    script = []
    div = []
    plotter = Plotter()

    # Sentiment of the Day -- 0
    temp_script, temp_div = plotter.sentiment_of_the_day(doc_id='sentiment_time', db_name='results')
    script.append(temp_script)
    div.append(temp_div)

    return render_template('sentiment.html', script=script, div=div)


@web_app.route('/map')
def get_map():
    m = DrawMap().mapper(doc_id='sentiment_distribution', db_name='results')
    return m.get_root().render()


if __name__ == '__main__':
    web_app.run(host="0.0.0.0", port=5000, debug=True)