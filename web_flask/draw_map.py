import json

import couchdb
import folium
import pandas as pd
from folium.plugins import MarkerCluster


class DrawMap:
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

    # @staticmethod
    # def set_color(sentiment):
        # if sentiment >= 0.05:
        #     return 'green'
        # elif -0.05 < sentiment < 0.05:
        #     return 'orange'
        # elif sentiment <= -0.05:
        #     return 'red'

    @staticmethod
    def create_marker(cor, sentiment, text, pos_fg, neu_fg, neg_fg):
        if sentiment >= 0.05:
            marker = folium.Marker(location=cor[::-1], popup=(folium.Popup(text)),
                                   icon=(folium.Icon(color='green')))
            pos_fg.add_child(marker)
        elif -0.05 < sentiment < 0.05:
            marker = folium.Marker(location=cor[::-1], popup=(folium.Popup(text)),
                                   icon=(folium.Icon(color='yellow')))
            neu_fg.add_child(marker)
        elif sentiment <= -0.05:
            marker = folium.Marker(location=cor[::-1], popup=(folium.Popup(text)),
                                   icon=(folium.Icon(color='red')))
            neg_fg.add_child(marker)
        return marker, pos_fg, neu_fg, neg_fg

    def mapper(self, doc_id, db_name):
        AUS_BOUND_BOX = (113.338953078, -43.6345972634, 153.569469029, -10.6681857235)
        centeroid = [(AUS_BOUND_BOX[1] + AUS_BOUND_BOX[3]) / 2, (AUS_BOUND_BOX[0] + AUS_BOUND_BOX[2]) / 2]
        data = self.retrieve_data(doc_id, db_name)
        df = pd.DataFrame(data['data'])

        map = folium.Map(location=centeroid, zoom_start=4, tiles='OpenStreetMap')
        folium.TileLayer('Mapbox Control Room').add_to(map)
        folium.TileLayer('Stamen Terrain').add_to(map)
        folium.TileLayer('Stamen Toner').add_to(map)
        folium.TileLayer('stamenwatercolor').add_to(map)
        folium.TileLayer('cartodbpositron').add_to(map)

        cluster = MarkerCluster(name='Cluster')
        fg = folium.FeatureGroup(name='Sentiment Distribution')
        pos_fg = folium.FeatureGroup(name='Positive')
        neu_fg = folium.FeatureGroup(name='Neutral')
        neg_fg = folium.FeatureGroup(name='Negative')

        for index, row in df.iterrows():
            cor = row['coordinates']
            if AUS_BOUND_BOX[0] <= cor[0] <= AUS_BOUND_BOX[2] and AUS_BOUND_BOX[1] <= cor[1] <= AUS_BOUND_BOX[3]:
                marker, pos_fg, neu_fg, neg_fg = self.create_marker(cor, row['sentiment'], row['text'],
                                                                    pos_fg, neu_fg, neg_fg)
                cluster.add_child(marker)

        fg.add_child(cluster)
        fg.add_child(pos_fg)
        fg.add_child(neu_fg)
        fg.add_child(neg_fg)
        map.add_child(fg)

        # map.add_child(pos_fg)
        # map.add_child(neu_fg)
        # map.add_child(neg_fg)

        # folium.LayerControl().add_to(fg)
        folium.LayerControl().add_to(map)

        return map
