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
        print(r)
        return loads(r.text)

    def query(self, item):
        text = item['corpus']
        try:
            response = Main.recognize(text)
            print(response)
        except Exception as exception:
            logger.error(f"Query failed: {exception}")
            response = None
        return response

    def map_entities(self, response, item):
        entities = []

        if not response:
            return None

        if response and 'annotations' in response:
            for annotation in response['annotations']:
                item['key'] = annotation['key']
                item['entity_type'] = annotation['entity_type']
                item['document_start'] = annotation['start']
                item['document_end'] = annotation['end']
                entities.append(item)
        return entities


if __name__ == '__main__':
    print("MAIN")
    document = Main.create_recognize_document(
        'Python Programmierer sind überall gesucht.')
    print(Main.recognize(document))