# -*- coding: utf-8 -*-

from orbis_eval.core.base import AggregationBaseClass

import logging
import requests
from os import getenv
from json import loads
logger = logging.getLogger(__name__)


class Main(AggregationBaseClass):

    @staticmethod
    def create_recognize_document(text):
        """
        Transform the given text into the format required by Recognize.
        """
        return {'id': 1,
                'content': text,
                'partitions': {'BODY': [
                    {'@type': 'CharSpan', 'start': 0, 'end': len(text)}
                ]}}

    @staticmethod
    def recognize(recognize_document):
        url = getenv('RECOGNIZE_URL')
        user = getenv('RECOGNIZE_USER')
        pwd = getenv('RECOGNIZE_PASS')
        profile = getenv('RECOGNIZE_PROFILE')
        auth = (user, pwd) if user and pwd else None
        r = requests.post(f'{url}/search_document?profileName={profile}',
                      auth=auth, json=recognize_document)
        return loads(r.text)

    def query(self, item):
        doc = Main.create_recognize_document(item['corpus'])
        try:
            response = Main.recognize(doc)
            print(response)
        except Exception as exception:
            logger.error(f"Query failed: {exception}")
            response = None
        return response

    def map_entities(self, response, item):
        ignore_types = list(filter(None,
                                   getenv('RECOGNIZE_IGNORE', '').split(',')))
        entities = []

        if response and 'annotations' in response:
            for annotation in response['annotations']:
                entity_type = annotation['key'].split('#')[1].split('/')[0]
                if entity_type in ignore_types:
                    continue

                entities.append({
                    'key': annotation['key'],
                    'document_start': annotation['start'],
                    'document_end': annotation['end'],
                    'entity_type':entity_type,
                    'type_url': annotation['entity_type'],
                    'surfaceForm': annotation['surfaceForm'],
                })

        # return a nil entity if nothing has been found
        return entities if entities else [{'key': 'https://nil.org',
                                           'document_start': 0,
                                           'document_end': 3,
                                           'entity_type': 'nil',
                                           'surfaceForm': 'nil'}]


if __name__ == '__main__':
    print("MAIN")
    document = Main.create_recognize_document(
        'Python Programmierer sind überall gesucht.')
    print(Main.recognize(document))