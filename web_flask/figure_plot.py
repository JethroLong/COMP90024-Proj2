import collections
from collections import Counter

import couchdb

# import matplotlib.pyplot as plt
from bokeh.core.property.dataspec import value
from bokeh.embed import components
from bokeh.models import GMapOptions, Circle, GMapPlot, PanTool, WheelZoomTool, ResetTool, SaveTool,\
    NumeralTickFormatter
from bokeh.plotting import figure
# from bokeh.resources import CDN


class Plotter:
    def __init__(self):
        couchdb_ip = self.read_ipAddr()
        couchdb_port = str(5984)
        self.url = "http://{}:{}".format(couchdb_ip, couchdb_port)

        self.couch_server = couchdb.Server(url=self.url)

    @staticmethod
    def read_ipAddr():
        with open("./hosts", mode='r') as f:
            found = False
            for line in f:
                if found:
                    if line.endswith("\n"):
                        return line[:-1]
                    else:
                        return line
                if line.find("[harvester]") >= 0:
                    found = True
        return None

    def retrieve_data(self, doc_id, db_name):
        while True:
            try:
                db = self.couch_server[db_name]
                data = db.get(doc_id)
                if data is not None:
                    break
            except Exception as e:
                print('No processed data for {}, please wait...'.format(doc_id))
        return data

    def hashtag_plot(self, doc_id, db_name):
        # retrieve data from db
        data = self.retrieve_data(doc_id=doc_id, db_name=db_name)

        count_terms_only = Counter()
        count_terms_only.update(data['data'])
        top10 = count_terms_only.most_common(10)
        x, y = zip(*top10)

        TOOLTIPS = [('', "@top")]

        f = figure(x_range=x, title="Hashtag Occurrences", tooltips=TOOLTIPS,
                   toolbar_location='right', plot_height=500, plot_width=639, background_fill_color='white',
                   background_fill_alpha=0.2,
                   border_fill_color='white',  # darkslategray
                   border_fill_alpha=0.5)

        f.title.text_font_size = '12pt'
        f.title.text_color = 'black'
        f.title.align = 'center'
        f.xaxis.major_label_text_color = "black"
        f.xaxis.major_label_text_font_size = '10pt'
        f.yaxis.major_label_text_color = "black"
        f.yaxis.major_label_text_font_size = '10pt'

        f.vbar(x=x, top=y, width=0.5, color='#c9d9d9')
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

        plot = GMapPlot(map_options=map_options, api_key=Gmap_API_key, plot_height=450, plot_width=666)  # h:573  w:925

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

    def sentiment_of_the_day(self, doc_id, db_name):
        # retrieve data from db
        data = self.retrieve_data(doc_id=doc_id, db_name=db_name)
        original_data = data['data']
        time_list = list(original_data.keys())
        sorted_original_data = {}
        for time, info in original_data.items():
            sorted_item = {}
            if info:
                sorted_item['neg'] = info['neg']
                sorted_item['neu'] = info['neu']
                sorted_item['pos'] = info['pos']
                sorted_original_data[time] = sorted_item
        dict_list = list(sorted_original_data.values())
        bar_data_dict = {}
        bar_data_dict['time'] = time_list
        bar_data_dict['neg'] = []
        bar_data_dict['neu'] = []
        bar_data_dict['pos'] = []
        for time, info in sorted_original_data.items():
            for k, v in info.items():
                bar_data_dict_item = {}
                bar_data_dict_item[k] = v
                if k == 'neg':
                    bar_data_dict['neg'].append(v)
                if k == 'neu':
                    bar_data_dict['neu'].append(v)
                if k == 'pos':
                    bar_data_dict['pos'].append(v)
        sentiment_list = list(dict_list[0].keys())
        colors = ["lightcoral", "burlywood", "mediumseagreen"]

        p = figure(x_range=time_list, plot_height=450, plot_width=666, title="Sentiments of the Day",
                   tools="hover, pan, save, reset", tooltips="$name @time: @$name")

        p.vbar_stack(sentiment_list, x='time', width=0.7, color=colors, source=bar_data_dict,
                     legend=[value(x) for x in sentiment_list])

        p.y_range.start = 0
        p.x_range.range_padding = 0.1
        p.xgrid.grid_line_color = None
        p.axis.minor_tick_line_color = None
        p.outline_line_color = None
        p.legend.location = "top_right"
        p.legend.orientation = "horizontal"

        script, div = components(p)

        return script, div

    def tweets_hour_breakdown(self, doc_id, db_name):
        # retrieve data from db
        data = self.retrieve_data(doc_id=doc_id, db_name=db_name)

        return 'str', 'str'

    def time_distribution(self, doc_id, db_name):
        # retrieve data from db
        data = self.retrieve_data(doc_id=doc_id, db_name=db_name)
        original_data = data['data']
        modified_data = original_data
        if '0' in modified_data.keys():
            modified_data['24'] = modified_data['0']
            modified_data.pop('0')

        s_data = {}
        for k, v in modified_data.items():
            nk_list = []
            nk = int(k)
            nk_list.append(nk)
            for n in nk_list:
                s_data[n] = v

        od = collections.OrderedDict(sorted(s_data.items()))
        sorted_data = {}
        for k, v in od.items():
            sorted_data[k] = v

        r_data = {}
        for k, v in sorted_data.items():
            nk_list = []
            nk = str(k)
            nk_list.append(nk)
            for n in nk_list:
                r_data[n] = v

        time = []
        num = []
        for k, v in r_data.items():
            time.append(k)
            num.append(v)

        rate_list = []
        suml = sum(num)
        for n in num:
            rate = n / suml
            rate_list.append(rate)

        TOOLTIPS = [("Rate", "@y{0.00%}")]

        p = figure(x_range=time, plot_height=400, plot_width=639, title="Time Distribution",
                   toolbar_location='right', tools="hover, pan, save, reset, wheel_zoom", tooltips=TOOLTIPS)

        # p.vbar(x=time, top=num, width=0.9)
        p.line(time, rate_list, line_width=0.9, color='#c9d9d9')
        p.yaxis.formatter = NumeralTickFormatter(format='0.00%')
        p.xaxis.axis_label = 'Time (hour)'

        p.xgrid.grid_line_color = None
        p.y_range.start = 0

        script_map, div_map = components(p)

        return script_map, div_map
