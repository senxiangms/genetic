from django.apps import AppConfig


class ClassifyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'classify'
    #xml_data = "orphadata.org_data_xml_en_product4.xml"
    print('in config')
