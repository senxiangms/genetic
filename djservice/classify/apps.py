from django.apps import AppConfig
import os
import logging
from django.conf import settings
from libs.multi_class import prepare_data


logging.getLogger().setLevel(logging.INFO)

class ClassifyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'classify'
    #xml_data = "orphadata.org_data_xml_en_product4.xml"
    DISEASES = None

    def ready(self):
        xml_file = os.path.join(settings.BASE_DIR, "..", "orphadata.org_data_xml_en_product4.xml")                
        logging.info(f'loading {xml_file}')        
        self.DISEASES, _, _, _ = prepare_data(xml_file)        