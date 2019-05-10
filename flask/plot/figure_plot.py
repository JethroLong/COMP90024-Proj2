from collections import Counter

import couchdb
import matplotlib.pyplot as plt
from bokeh.embed import components
from bokeh.models import GMapOptions, Circle, GMapPlot, PanTool, WheelZoomTool, ResetTool, SaveTool
from bokeh.plotting import figure
from bokeh.resources import CDN


class Plotter:
    def __init__(self):
        self.url = 'http://localhost:5984'
        self.couch_server = couchdb.Server(url=self.url)

    def retrieve_data(self, doc_id, db_name):
        while True:
            try:
                db = self.couch_server[db_name]
                data = db.get(doc_id)
                if data is not None:
                    break
            except Exception as e:
                print(e)
        return data

    def hashtag_plot(self, doc_id, db_name):
        # retrieve data from db
        data = self.retrieve_data(doc_id=doc_id, db_name=db_name)

        count_terms_only = Counter()
        count_terms_only.update(data['data'])
        top10 = count_terms_only.most_common(10)
        x, y = zip(*top10)

        f = figure(x_range=x, title="Hashtag Occurrences", title_location='above',
                   toolbar_location='right', plot_height=399, plot_width=639, background_fill_color='gray',
                   background_fill_alpha=0.2,
                   border_fill_color='darkslategray',  # darkslategray
                   border_fill_alpha=0.5)
        f.title.text_font_size = '12pt'
        f.title.text_color = 'white'
        f.title.align = 'center'
        f.xaxis.major_label_text_color = "white"
        f.xaxis.major_label_text_font_size = '10pt'
        f.yaxis.major_label_text_color = "white"
        f.yaxis.major_label_text_font_size = '10pt'

        f.vbar(x=x, top=y, width=0.5, color='goldenrod')
        f.y_range.start = 0
        f.x_range.range_padding = 0.1
        f.xaxis.major_label_orientation = -1

        script_hashtag, div_hashtag = components(f)

        n = div_hashtag.split()
        str1 = 'style="position: relative; left: 50%; transform: translateX(-50%);"'
        n.insert(3, str1)
        div_hashtag = ' '.join(n)

        return script_hashtag, div_hashtag

    def interactive_map(self, doc_id, db_name):
        Gmap_API_key = 'AIzaSyBL5mv0DEHyXuopWAqQ532y_JuEACbqfko'
        # retrieve data from db
        data = self.retrieve_data(doc_id=doc_id, db_name=db_name)

        style_str = """[{"featureType":"all","elementType":"geometry.fill","stylers":[{"weight":"2.00"}]},{"featureType":"all","elementType":"geometry.stroke","stylers":[{"color":"#9c9c9c"}]},{"featureType":"all","elementType":"labels.text","stylers":[{"visibility":"on"}]},{"featureType":"landscape","elementType":"all","stylers":[{"color":"#f2f2f2"}]},{"featureType":"landscape","elementType":"geometry.fill","stylers":[{"color":"#ffffff"}]},{"featureType":"landscape.man_made","elementType":"geometry.fill","stylers":[{"color":"#ffffff"}]},{"featureType":"poi","elementType":"all","stylers":[{"visibility":"off"}]},{"featureType":"road","elementType":"all","stylers":[{"saturation":-100},{"lightness":45}]},{"featureType":"road","elementType":"geometry.fill","stylers":[{"color":"#eeeeee"}]},{"featureType":"road","elementType":"labels.text.fill","stylers":[{"color":"#7b7b7b"}]},{"featureType":"road","elementType":"labels.text.stroke","stylers":[{"color":"#ffffff"}]},{"featureType":"road.highway","elementType":"all","stylers":[{"visibility":"simplified"}]},{"featureType":"road.arterial","elementType":"labels.icon","stylers":[{"visibility":"off"}]},{"featureType":"transit","elementType":"all","stylers":[{"visibility":"off"}]},{"featureType":"water","elementType":"all","stylers":[{"color":"#46bcec"},{"visibility":"on"}]},{"featureType":"water","elementType":"geometry.fill","stylers":[{"color":"#c8d7d4"}]},{"featureType":"water","elementType":"labels.text.fill","stylers":[{"color":"#070707"}]},{"featureType":"water","elementType":"labels.text.stroke","stylers":[{"color":"#ffffff"}]}]"""
        AUS_BOUND_BOX = (113.338953078, -43.6345972634, 153.569469029, -10.6681857235)
        map_options = GMapOptions(lat=-28.7, lng=133.9, map_type="terrain", zoom=4, styles=style_str)

        plot = GMapPlot(map_options=map_options, api_key=Gmap_API_key, plot_height=573, plot_width=925)

        for each in data['data']:
            if AUS_BOUND_BOX[0] <= each['coordinates'][0] <= AUS_BOUND_BOX[2] and \
                    AUS_BOUND_BOX[1] <= each['coordinates'][1] <= AUS_BOUND_BOX[3]:
                if each['sentiment'] >= 0.05:
                    circle = Circle(x=each['coordinates'][0], y=each['coordinates'][1], size=5, fill_color='green')
                    plot.add_glyph(circle)
                elif -0.05 < each['sentiment'] < 0.05:
                    circle = Circle(x=each['coordinates'][0], y=each['coordinates'][1], size=5, fill_color='blue')
                    plot.add_glyph(circle)
                elif each['sentiment'] <= -0.05:
                    circle = Circle(x=each['coordinates'][0], y=each['coordinates'][1], size=5, fill_color='red')
                    plot.add_glyph(circle)

        # add interactive tools
        pan = PanTool()
        wheel_zoom = WheelZoomTool()
        reset = ResetTool()
        save = SaveTool()
        plot.add_tools(pan, wheel_zoom, reset, save)

        # interactive Hover -- to be added

        script_map, div_map = components(plot)
        return script_map, div_map

    def time_sentiment_plot(self, doc_id, db_name):
        # retrieve data from db
        data = self.retrieve_data(doc_id=doc_id, db_name=db_name)

        ####
        # draw

    def tweets_hour_breakdown(self, doc_id, db_name):
        # retrieve data from db
        data = self.retrieve_data(doc_id=doc_id, db_name=db_name)

        return 'str', 'str'
