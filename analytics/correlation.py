MIN_NUM_OF_REGION = 3
MIN_CORRELATION = 0.5
GROUP_NAME_SUB = r'(mild|medium|strongest|strong|_|-)'

TITLE_REPLACE_PATTERN = r'.%.'

# URL = 'http://10.9.131.221:5984/'
RAW_TWEETS = 'raw_tweets'
CORPUS_VIEW_NAME = 'word_choice_result'
ALL_DOC_VIEW_FUNC = "function (doc) {\n emit(doc._id, doc); \n}"
ALL_TEXT_VIEW_FUNC = "function (doc) {\n if (doc.text != null) {\n  emit(doc._id, doc.text);\n }\n}"
HAS_GEO_VIEW_FUNC = "function (doc) {\n  if (doc.coordinates != null){\n    var x = {};\n    x['coordinates'] =  doc.coordinates.coordinates;\n    x['text'] = doc.text;\n    emit(doc._id, x);\n  }\n}"



class CorrelationAnalyzer:

    def __init__(self, source_db, view_path, results_db):
        self.view_path = view_path
        self.source_db = source_db
        self.results_db = results_db

    def rearrange_info(self, result):
        aurin_item_name = set()
        corpus_name = set()

        for row in result.rows:
            for item in row.value['rows']:
                for name in item['edu_info']:
                    aurin_item_name.add(name)
                for name in item['word_choice']:
                    corpus_name.add(name)

        aurin_points = {}
        corpus_points = {}
        for row in result.rows:
            for item in row.value['rows']:
                for name in aurin_item_name:
                    try:
                        aurin_points[name]['value'].append(item['edu_info'][name])
                        aurin_points[name]['region'].append(item['region_name'])
                    except:
                        try:
                            aurin_points[name] = {'value': [item['edu_info'][name]], 'region': [item['region_name']]}
                        except:
                            try:
                                aurin_points[name]['value'].append(None)
                            except:
                                aurin_points[name] = {'value': [None], 'region': [None]}
                for name in corpus_name:
                    try:
                        corpus_points[name].append(item['word_choice'][name])
                    except:
                        try:
                            corpus_points[name] = [item['word_choice'][name]]
                        except:
                            try:
                                corpus_points[name].append(None)
                            except:
                                corpus_points[name] = [None]
        return aurin_points, corpus_points

    def obtain_scatter_info(self, aurin_points, corpus_points):
        correlation_result = {}
        script_map_list = []
        div_map_list = []

        # for edu_name, x_list in edu_points.items():
        for aurin_name, info in aurin_points.items():
            x_list = info['value']
            region_list = info['region']
            for corpus_name, y_list in corpus_points.items():
                valid_x = []
                valid_y = []
                valid_region = []
                valid_pos = []
                if x_list and y_list:
                    for i in range(len(x_list)):
                        if x_list[i] is not None and y_list[i] is not None:
                            valid_pos.append(i)

                    if len(valid_pos) >= MIN_NUM_OF_REGION:
                        for i in valid_pos:
                            valid_x.append(x_list[i])
                            valid_y.append(y_list[i])
                            valid_region.append(region_list[i])

                        fitted_y = curve_fit(valid_x, valid_y)
                        corpus_name = (corpus_name.replace('_', ' ') + " (%)").title()
                        script_map, div_map = scatter_fit_plot(valid_x, valid_y, fitted_y, valid_region, aurin_name,
                                                               corpus_name)
                        script_map_list.append(script_map)
                        div_map_list.append(div_map)
                        correlation_result[(aurin_name, corpus_name)] = pearsonr(valid_x, valid_y)
                        # print(correlation_result)
                        return script_map, div_map, correlation_result

        # for key, value in correlation_result.items():
        #     if value[0] >= MIN_CORRELATION:
        #         print(key, ": ", value)
        return None

    def group_info(self, result, whole_corpus_included=False):
        group_name_pattern = re.compile(GROUP_NAME_SUB)
        group_result = {}
        for name, value in result['corpus_count'].items():
            group_name = (re.sub(group_name_pattern, '', name.replace('_', ' '))).title()
            try:
                group_result[group_name] += value
            except:
                group_result[group_name] = value
        if whole_corpus_included:
            whole_corpus_name = max(group_result, key=lambda key: group_result[key])
            total = group_result[whole_corpus_name]
            del group_result[whole_corpus_name]
            repeated = sum(group_result.values())
            group_result['Unclassified'] = total - repeated
            # print(group_result)
        return group_result

    def degree_info(self, result, whole_corpus_included=False):
        degree_result = {}
        for name, value in result['corpus_count'].items():
            if 'mild' in name:
                degree_name = 'Mild'
            elif 'medium' in name:
                degree_name = 'Medium'
            elif 'strong' in name:
                degree_name = 'Strong'
            elif 'strongest' in name:
                degree_name = 'Strongest'
            else:
                degree_name = 'Unclassified'
            try:
                degree_result[degree_name] += value
            except:
                degree_result[degree_name] = value

        if whole_corpus_included:
            whole_corpus_name = max(degree_result, key=lambda key: degree_result[key])
            total = degree_result[whole_corpus_name]
            del degree_result[whole_corpus_name]
            repeated = sum(degree_result.values())
            degree_result['Unclassified'] = total - repeated
            # print(degree_result)
        ordered_result = {}

        if 'Unclassified' in degree_result.keys():
            ordered_result['Unclassified'] = degree_result['Unclassified']
        if 'Mild' in degree_result.keys():
            ordered_result['Mild'] = degree_result['Mild']
        if 'Medium' in degree_result.keys():
            ordered_result['Medium'] = degree_result['Medium']
        if 'Strong' in degree_result.keys():
            ordered_result['Strong'] = degree_result['Strong']
        if 'Strongest' in degree_result.keys():
            ordered_result['Strongest'] = degree_result['Strongest']
        # print(ordered_result)
        return ordered_result

    def run(self):
        couch_server = couchdb.Server(url=URL)
        corpus_db = couch_server[CORPUS_VIEW_NAME]
        corpus_view_path = create_view(url=URL, db_name=CORPUS_VIEW_NAME, view_name="corpus_view",
                                       mapFunc=ALL_DOC_VIEW_FUNC, overwrite=False)
        corpus_docs = corpus_db.view(corpus_view_path)
        # print(corpus_docs)

        edu_points, word_choice_points = rearrange_info(corpus_docs)
        script_map_scatter_list, div_map_scatter_list, correlation_result = obtain_scatter_info(edu_points,
                                                                                                word_choice_points)
        degree = degree_info(corpus_docs, True)
        group = group_info(corpus_docs, True)

        script_map_group_pie, div_map_group_pie = pie_chart(group, 'Offensive Word Group Pie Chart')
        script_map_degree_pie, div_map_degree_pie = pie_chart(degree, 'Offensive Word Degree', True)
