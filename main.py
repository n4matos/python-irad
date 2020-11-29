import os
import pydicom
import json
import time
import requests
import connection
import unidecode
# import variables


rootdir = "C:/Projects/Python/IRAD/Images/1"
rootalternativo = "C:/Projects/Python/IRAD/imgs-2"
rootrm = "C:/Projects/Python/IRAD/6ec67862/c8c98b70"
rootcrd = "C:/arquivamento/data"

dont_print = ['PixelData', 'FileMetaInformationVersion',
              'ImageType', 'PixelAspectRatio', '']
just_name = ['Patient ID']
print_data = ['StudyDate', 'SeriesDate', 'AcquisitionDate', 'ContentDate', 'StudyTime', 'SeriesTime', 'AcquisitionTime',
              'ContentTime', 'AccessionNumber', 'Modality', 'Manufacturer', 'ManufacturerModelName', 'InstitutionName', 'StudyDescription',
              'SeriesDescription', 'PatientName', 'PatientID', 'PatientSex', 'PatientBirthDate', 'BodyPartExamined', 'ProtocolName', 'RelativeXRayExposure',
              'ExposureTime', 'XRayTubeCurrent', 'Exposure', 'GeneratorPower']


data = {}


def fileDelete(filepath):
    if filepath.endswith('.dcm'):
        os.remove(filepath)


def build_unique_json(dataset, current_value, previous_value):

    for data_element in dataset:
        if data_element.keyword in print_data:

            if data_element.keyword == 'PatientID':
                current_value = data_element.value

            if data_element.keyword == 'PatientName':
                data[data_element.keyword] = data_element.value.given_name
            else:
                data[data_element.keyword] = data_element.value

            json_data = json.dumps(data, sort_keys=True, indent=1)

    if current_value != previous_value:
        previous_value = current_value

        send_dicom_attributes(json_data)
        # return(json_data, current_value, previous_value)

    return(json_data, current_value, previous_value)
    # previous_value = current_value


def send_dicom_attributes(data):
    api_endpoint = 'http://crd.zapto.org:9090/api/rpc/irad_recebimento'

    headers = {
        'Content-Type': 'application/json',
        'Prefer': 'params=single-object'
    }

    json_object = json.loads(data)
    print(json_object)

    r = requests.post(url=api_endpoint, json=json_object, headers=headers)
    json_data = json.loads(r.text)
    print(json_data['resultado'])


def send_mongodb(db, data):

    json_object = json.loads(data)
    print(json_object)

    result = db.dcm_tags.insert_one(json_object)
    print(result.inserted_id)


def build_json_mongo(dataset):
    for data_element in dataset:
        if data_element.keyword not in dont_print:
            if data_element.VR == "IS":
                data[data_element.keyword] = data_element.value

            else:
                if data_element.keyword == 'PatientName' or data_element.keyword == 'ReferringPhysicianName':
                    if data_element.value:
                        data[data_element.keyword] = data_element.value.given_name + \
                            data_element.value.middle_name + data_element.value.family_name
                else:
                    if isinstance(data_element.value, str) and data_element.keyword:
                        data[data_element.keyword] = unidecode.unidecode(
                            data_element.value)

            json_data = json.dumps(data, sort_keys=True, indent=1)

    # send_dicom_attributes(json_data)
    send_mongodb(db, json_data)


def build_json(dataset):
    for data_element in dataset:
        if data_element.keyword in print_data:
            if data_element.VR == "IS":
                data[data_element.keyword] = data_element.value

            else:
                if data_element.keyword == 'PatientName':
                    data[data_element.keyword] = data_element.value.given_name + \
                        data_element.value.middle_name + data_element.value.family_name
                else:
                    data[data_element.keyword] = unidecode.unidecode(
                        data_element.value)

            json_data = json.dumps(data, sort_keys=True, indent=1)

    send_dicom_attributes(json_data)
    # send_mongodb(db, json_data)

    # print("{0:s} {1:s} = {2:s}".format(indent_string, data_element.name, repr_value))


def myprint_json(dataset, indent=0):
    """Go through all items in the dataset and print them with custom format

    Modelled after Dataset._pretty_str()
    """
    dont_print = ['Pixel Data', 'File Meta Information Version', 'Image Type']

    indent_string = "   " * indent
    next_indent_string = "   " * (indent + 1)

    for data_element in dataset:
        if data_element.VR == "SQ":   # a sequence
            print(indent_string, data_element.name)
            for sequence_item in data_element.value:
                myprint(sequence_item, indent + 1)
                print(next_indent_string + "---------")
        else:
            if data_element.name in dont_print:
                print("""<item not printed -- in the "don't print" list>""")
            else:
                repr_value = repr(data_element.value)
                if len(repr_value) > 50:
                    repr_value = repr_value[:50] + "..."

                data = {}
                data[data_element.name.replace(" ", "")] = repr_value
                json_data = json.dumps(data)

                print(json_data)
                # print("{0:s} {1:s} = {2:s}".format(indent_string, data_element.name, repr_value))


def myprint(dataset, indent=0):
    """Go through all items in the dataset and print them with custom format

    Modelled after Dataset._pretty_str()
    """
    dont_print = ['Pixel Data', 'File Meta Information Version']

    indent_string = "   " * indent
    next_indent_string = "   " * (indent + 1)

    for data_element in dataset:
        if data_element.VR == "SQ":   # a sequence
            print(indent_string, data_element.name)
            for sequence_item in data_element.value:
                myprint(sequence_item, indent + 1)
                print(next_indent_string + "---------")
        else:
            if data_element.name in dont_print:
                print("""<item not printed -- in the "don't print" list>""")
            else:
                repr_value = repr(data_element.value)
                if len(repr_value) > 50:
                    repr_value = repr_value[:50] + "..."
                print("{0:s} {1:s} = {2:s}".format(indent_string,
                                                   data_element.name,
                                                   repr_value))


start_time = time.time()


# Find total number of dicom files in series
j = 0
for subdir, dirs, files in os.walk(rootalternativo):
    for file in files:
        # if file.endswith(".dcm"):
        j = j + 1
totaldcm = j

print(totaldcm)


# connection.test_connection()
# db = connection.init_connection()

db = connection.init_docker_localhost()

# serverStatusResult = db.command("serverStatus")
# print(serverStatusResult)


current_value = ''
previous_value = ''
params = {}
params[1] = ''
params[2] = ''
for subdir, dirs, files in os.walk(rootalternativo):
    for file in files:
        # print os.path.join(subdir, file)
        filepath = subdir + os.sep + file

        dataset = pydicom.filereader.dcmread(filepath)
        # print datase
        # print(dataset)
        # print(myprint(dataset))

        # Função que monta o json e envia para o servidor obs: Unique patient id
        # params = build_unique_json(dataset, params[1], params[2])

        # Função que monta o json e envia para o servidor, envia todos os registros
        build_json_mongo(dataset)
        # myprint_json(dataset)

        # print(params[0])

        # fileDelete(filepath)

        '''
        for data_element in dataset:
            if data_element.name in print_data:

                if data_element.name == 'Patient ID':
                    current_value = data_element.value

                data[data_element.name.replace(" ", "")] = data_element.value
                json_data = json.dumps(data, sort_keys=True, indent=1)

        if current_value != previous_value:
            print(json_data)

        previous_value = current_value
        '''
        # build_json(dataset)


print("--- %s seconds ---" % (time.time() - start_time))

# print (filepath)

# if filepath.endswith(".dcm"):
#   print (filepath)
