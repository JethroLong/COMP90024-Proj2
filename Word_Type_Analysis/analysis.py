import itertools
import json
import csv
import re
import time

import matplotlib.path as mplPath
from matplotlib import pyplot
import numpy as np
import spacy

AURIN_FILE_NAME = 'AURIN_Edu_2016.json'
GEO_CODE_FILE_NAME = 'LGA_2017_VIC.csv'
SPATIAL_FILE_NAME = 'geoinfo.json'
TWITTER_FILE_NAME = 'sample_tweets.json'


VALID_YEAR = '2019'
corpus_name_list = ['bad-words',
                    'body_parts_mild', 'body_parts_medium', 'body_parts_strong', 'body_parts_strongest',
                    'gender_identity_mild', 'gender_identity_medium',
                    'gender_identity_strong', 'gender_identity_strongest',
                    'mental_health_physical_disability_mild', 'mental_health_physical_disability_medium',
                    'mental_health_physical_disability_strong', 'mental_health_physical_disability_strongest',
                    'race_ethnicity_mild', 'race_ethnicity_medium',
                    'race_ethnicity_strong', 'race_ethnicity_strongest',
                    'sexual_reference_mild', 'sexual_reference_medium', 'sexual_reference_strong',
                    'older_people_mild', 'older_people_medium',
                    'religious_insults_strong'
                    ]
feature_name = ["chld_attnd_prescl_prog_less_than_15_hours_num",
                "hi_yr_scl_completed_p15_yrs_ov_completed_yr_8_below_pr100",
                "occup_empy_p_mach_ops_drv_pr100",
                "lbr_frc_statistics_lbr_frc_num",
                "hi_yr_scl_completed_p15_yrs_ov_completed_yr_11_equivalent_pr100",
                "yth_engagement_wrk_study_wrking_ft_studying_ft_pr100",
                "yth_engagement_wrk_study_engaged_pr100",
                "hi_yr_scl_completed_p15_yrs_ov_completed_yr_10_equivalent_pr100",
                "yth_engagement_wrk_study_wrking_ft_studying_pt_pr100",
                "chld_attnd_prescl_prog_15_hours_pls_num",
                "p_post_scl_qual_inadequately_described_ns_pr100",
                "chld_enrld_prescl_prog_chld_enrld_across_1_plus_prov_type_num",
                "occup_empy_p_mgmt_pr100","yth_engagement_wrk_study_wrking_ft_no_studying_pr100",
                "occup_empy_p_pros_pr100","hi_yr_scl_completed_p15_yrs_ov_ns_pr100",
                "higher_edu_loan_prog_help_repay_taxpayers_help_repay_num","p_post_scl_qual_advc_dipl_dipl_pr100",
                "chld_enrld_prescl_prog_5_yr_olds_num","p_post_scl_qual_postgrad_deg_pr100",
                "occup_empy_p_inadequately_described_ns_pr100","chld_enrld_prescl_prog_long_day_care_centre_num",
                "hi_yr_scl_completed_p15_yrs_ov_completed_yr_9_equivalent_pr100","p_post_scl_qual_p_post_scl_qual_pr100",
                "yth_engagement_wrk_study_wrking_pt_studying_pt_pr100","occup_empy_p_lbr_pr100",
                "p_post_scl_qual_bach_deg_pr100","occup_empy_p_cmty_p_wrk_pr100",
                "yth_engagement_wrk_study_tot_15_19_yrs_num","chld_enrld_prescl_prog_enrld_prescl_num",
                "lbr_frc_statistics_ptic_rt_pr100","yth_engagement_wrk_study_wrking_pt_studying_ft_pr100",
                "hi_yr_scl_completed_p15_yrs_ov_no_scl_pr100","p_post_scl_qual_grad_dipl_grad_cert_pr100",
                "occup_empy_p_sales_wrk_pr100","hi_yr_scl_completed_p15_yrs_ov_completed_yr_12_equivalent_pr100",
                "occup_empy_p_clerical_adm_wrk_pr100","occup_empy_p_techn_trd_wrk_pr100","p_post_scl_qual_cert_pr100",
                "lbr_frc_statistics_unemp_num","yth_engagement_wrk_study_studying_ft_no_wrking_pr100",
                "chld_enrld_prescl_prog_tot_enrld_prescl_prog_num",
                "lbr_frc_statistics_unemp_rt_pr100","chld_enrld_prescl_prog_4_yr_olds_num"
                ]
WHOLE_CORPUS = corpus_name_list[0]


def doc_tokenize(doc):
    pass
    # nlp = spacy.load("en_core_web_sm")
    # doc = nlp(doc)
    # tokens = set()
    # for token in doc:
    #     tokens.add(token.text)
    # return tokens


def check_belonging(point, contour):
    for element in contour:
        element = list(element)
        crd = np.array(element)  # poly
        bbPath = mplPath.Path(crd)
        r = 0.00001  # accuracy
        isIn = bbPath.contains_point(point, radius=r)
        return isIn


def get_tweet_coordinates(item):
    point = None
    if item['doc']['geo']:  # get tweet coordinates
        point = item['doc']['geo']['coordinates']
    elif item['doc']['coordinates']:
        point = item['doc']['coordinates']['coordinates']
    elif item['doc']['place']['bounding_box']['coordinates']:
        points = item['doc']['place']['bounding_box']['coordinates'][0]
        x = []
        y = []
        [x.append(p[0]) for p in points]
        [y.append(p[1]) for p in points]
        point = [sum(x)/len(points), sum(y)/len(points)]
    return point


def get_valid_code(geoinfo, geo_code):
    valid_code = set()
    for item in geoinfo['features']:
        if item['properties']['lga_code17'] in geo_code.keys():
            valid_code.add(item['properties']['lga_code17'])
    return valid_code


def get_tweet_region(coordinate, geoinfo, valid_code):
    for polygons in geoinfo['features']:
        if polygons['properties']['lga_code17'] in valid_code:
            if check_belonging(coordinate, itertools.chain.from_iterable(polygons['geometry']['coordinates'])):
                return polygons['properties']['lga_name17']
    return None


def get_tweet_text(tweet):
    text = tweet['doc']['text'].lower()
    text = text.replace('-', ' ')
    return text


def hash_corpus():
    corpus_hash = {}
    for name in corpus_name_list:
        corpus_file = open(name+'.txt', 'r')
        for word in corpus_file:
            word = word.replace('\n', '')
            pattern = re.compile(r'\s+' + re.escape(word) + r'(\s+|\W+)')
            corpus_hash[pattern] = name
    return corpus_hash


def get_belonged_corpus(corpus_hash, text):
    for pattern, category in corpus_hash.items():
        if bool(pattern.search(text)):
            return category
    return None


def main():
    # load files
    twitter_file = open(TWITTER_FILE_NAME, 'rb')
    tweets = json.load(twitter_file)

    aurin_file = open(AURIN_FILE_NAME, 'r')
    aurin_info = json.load(aurin_file)

    code_file = open(GEO_CODE_FILE_NAME, 'r')
    reader = csv.reader(code_file)
    geo_code = {}
    for row in reader:
        geo_code[row[1]] = row[2]
    print(geo_code)
    print(len(geo_code))

    geo_file = open('geoinfo.json', 'r')
    geoinfo = json.load(geo_file)

    valid_code = get_valid_code(geoinfo, geo_code)

    # generate and store AURIN dataset info
    region_info = {}

    for item in aurin_info['features']:
        if item['properties']['lga_code17'] in valid_code:
            region_info[item['properties']['lga_name17']] = {'edu_info': {}, 'word_choice': {}}
            for feature in feature_name:
                region_info[item['properties']['lga_name17']]['edu_info'].update({feature: item['properties'][feature]})

    print(region_info)

    corpus_hash = hash_corpus()
    corpus_count = {}
    corpus_region = {}
    region_total_tweets = {}
    print(len(tweets['rows']))

    i = 0
    for item in tweets['rows']:
        if item['doc']['created_at']:  # filter valid year
            if bool(re.search(VALID_YEAR, item['doc']['created_at'])):
                point = get_tweet_coordinates(item)  # get Tweet coordinates
                if point:
                    region_name = get_tweet_region(point, geoinfo, valid_code)
                    if region_name:
                        try:
                            region_total_tweets[region_name] += 1
                        except:
                            region_total_tweets[region_name] = 1
                        text = get_tweet_text(item)
                        category = get_belonged_corpus(corpus_hash, text)
                        if category:
                            try:
                                corpus_count[category] += 1  # corpus sum
                            except:
                                corpus_count[category] = 1
                            try:
                                corpus_region[region_name][category] += 1
                                if category != WHOLE_CORPUS:
                                    corpus_region[region_name][WHOLE_CORPUS] += 1
                            except:
                                corpus_region[region_name] = {category: 1}
                                if category != WHOLE_CORPUS:
                                    try:
                                        corpus_region[region_name][WHOLE_CORPUS] += 1
                                    except:
                                        corpus_region[region_name][WHOLE_CORPUS] = 1
        # i+=1
        # if i==100:
        #     break

    print(region_total_tweets)
    print(corpus_region)

    result_json = {'rows': []}
    for name, value in corpus_region.items():
        for key, num in value.items():
            value[key] = round(num/region_total_tweets[name], 1)
        region_info[name]['word_choice'].update(value)
        row = {'region_name': name, 'region_total_tweets': region_total_tweets[name]}
        row.update(region_info[name])
        print(row)
        result_json['rows'].append(row)

    result_json = json.dumps(result_json)
    print(result_json)

    result_corpus_region = open('corpus_region.json', 'w+')
    for item in corpus_region:
        result_corpus_region.writelines(item)
    result_corpus_region.close()

    result = open('result.json', 'w+')
    for lines in result_json:
        result.writelines(lines)
    result.close()

    corpus_count[WHOLE_CORPUS] = sum(corpus_count.values())
    print(corpus_count)


if __name__ == '__main__':
    main()