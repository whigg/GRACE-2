from django.http import JsonResponse, HttpResponse, Http404
from django.shortcuts import render
from django.contrib.auth.decorators import login_required,user_passes_test
from django.views.decorators.csrf import csrf_exempt
from tethys_sdk.gizmos import *
from utilities import *
import json,time
from tethys_dataset_services.engines import GeoServerSpatialDatasetEngine
from sqlalchemy.orm.exc import ObjectDeletedError
from sqlalchemy.exc import IntegrityError
from model import *
import requests, urlparse
from gbyos import *
import shapely.geometry
import os
from config import GRACE_NETCDF_DIR,GLOBAL_NETCDF_DIR,TOTAL_NETCDF_DIR,TOTAL_GLOBAL_NETCDF_DIR,SW_NETCDF_DIR,SW_GLOBAL_NETCDF_DIR,SOIL_NETCDF_DIR,SOIL_GLOBAL_NETCDF_DIR,GW_NETCDF_DIR,GW_GLOBAL_NETCDF_DIR
from geoserver.catalog import Catalog
import geoserver


#GRACE_NETCDF_DIR = '/grace/'
#GLOBAL_NETCDF_DIR = '/grace/global/'

def plot_reg_tot(request):
    return_obj = {}
    return_obj = {}
    if request.is_ajax() and request.method == 'POST':
        info = request.POST

        region_id = info.get('region-info')
        Session = Grace.get_persistent_store_database('main_db', as_sessionmaker=True)
        session = Session()



        region = session.query(Region).get(region_id)
        display_name = region.display_name
        region_store = ''.join(display_name.split()).lower()

        FILE_DIR = os.path.join(TOTAL_NETCDF_DIR, '')

        region_dir = os.path.join(FILE_DIR + region_store, '')

        geotiff_dir = os.path.join(region_dir+"geotiff")


        geoserver = session.query(Geoserver).get(region.geoserver_id)
        geoserver_url = geoserver.url
        region_store = ''.join(display_name.split()).lower()

        bbox = [float(x) for x in region.latlon_bbox.strip("(").strip(")").split(',')]
        json.dumps(bbox)

        sorted_files = sorted(os.listdir(geotiff_dir), key=lambda x: datetime.strptime(x, '%Y_%m_%d.tif'))
        layers_length = len(sorted_files)
        grace_layer_options = []

        for file in sorted_files:
            year = int(file[:-4].split('_')[0])
            month = int(file[:-4].split('_')[1])
            day = int(file[:-4].split('_')[2])
            date_str = datetime(year,month,day)
            date_str = date_str.strftime("%Y %B %d")
            grace_layer_options.append([date_str,file[:-4]+"_"+region_store])



        csv_file = region_dir+region_store+".csv"
        with open(csv_file, 'rb') as f:
            reader = csv.reader(f)
            csvlist = list(reader)

        volume_time_series = []
        volume = []
        x_tracker = []
        formatter_string = "%m/%d/%Y"
        for item in csvlist:
            mydate = datetime.strptime(item[0], formatter_string)
            mydate = time.mktime(mydate.timetuple()) * 1000
            volume_time_series.append([mydate, float(item[1])])
            volume.append(float(item[1]))
            x_tracker.append(mydate)

        range = [round(min(volume), 2), round(max(volume), 2)]
        range = json.dumps(range)

    # Configure the time series Plot View
    #     grace_plot = TimeSeries(
    #         engine='highcharts',
    #         title=display_name+ ' GLDAS Data',
    #         y_axis_title='Total Surface Water Storage Anomaly',
    #         y_axis_units='cm',
    #         series=[
    #             {
    #                 'name': 'Height of Liquid Water',
    #                 'color': '#0066ff',
    #                 'data': volume_time_series,
    #             },
    #             {
    #                 'name': 'Tracker',
    #                 'color': '#ff0000',
    #                 'data': [[min(x_tracker), round(min(volume), 2)], [min(x_tracker), round(max(volume), 2)]]
    #             },
    #         ],
    #         width='100%',
    #         height='300px'
    #     )

        wms_url = geoserver_url[:-5]+"wms"
        color_bar = get_color_bar()
        color_bar = json.dumps(color_bar)

        if bbox[0] < 0 and bbox[2] < 0:
            map_center = [( (360+(int(bbox[0])))+(360+(int(bbox[2])))) / 2,(int(bbox[1])+int(bbox[3])) / 2]
        else:
            map_center = [(int(bbox[0]) + int(bbox[2])) / 2, (int(bbox[1]) + int(bbox[3])) / 2]
        json.dumps(map_center)
        json.dumps(x_tracker)

        return_obj['data']=volume_time_series
        return_obj['xmin']=min(x_tracker)
        return_obj['volmin']=round(min(volume), 2)
        return_obj['volmax']=round(max(volume), 2)
        return_obj['displayname']= display_name


        # return_obj["success"] = "success"

    return JsonResponse(return_obj)


def plot_reg_sw(request):
    return_obj = {}
    return_obj = {}
    if request.is_ajax() and request.method == 'POST':
        info = request.POST

        region_id = info.get('region-info')
        print(region_id)
        print("this is the reg id")
        Session = Grace.get_persistent_store_database('main_db', as_sessionmaker=True)
        session = Session()



        region = session.query(Region).get(region_id)
        display_name = region.display_name
        region_store = ''.join(display_name.split()).lower()

        FILE_DIR = os.path.join(SW_NETCDF_DIR, '')

        region_dir = os.path.join(FILE_DIR + region_store, '')

        geotiff_dir = os.path.join(region_dir+"geotiff")


        geoserver = session.query(Geoserver).get(region.geoserver_id)
        geoserver_url = geoserver.url
        region_store = ''.join(display_name.split()).lower()

        bbox = [float(x) for x in region.latlon_bbox.strip("(").strip(")").split(',')]
        json.dumps(bbox)

        sorted_files = sorted(os.listdir(geotiff_dir), key=lambda x: datetime.strptime(x, '%Y_%m_%d.tif'))
        layers_length = len(sorted_files)
        grace_layer_options = []

        for file in sorted_files:
            year = int(file[:-4].split('_')[0])
            month = int(file[:-4].split('_')[1])
            day = int(file[:-4].split('_')[2])
            date_str = datetime(year,month,day)
            date_str = date_str.strftime("%Y %B %d")
            grace_layer_options.append([date_str,file[:-4]+"_"+region_store])



        csv_file = region_dir+region_store+".csv"
        with open(csv_file, 'rb') as f:
            reader = csv.reader(f)
            csvlist = list(reader)

        volume_time_series = []
        volume = []
        x_tracker = []
        formatter_string = "%m/%d/%Y"
        for item in csvlist:
            mydate = datetime.strptime(item[0], formatter_string)
            mydate = time.mktime(mydate.timetuple()) * 1000
            volume_time_series.append([mydate, float(item[1])])
            volume.append(float(item[1]))
            x_tracker.append(mydate)

        range = [round(min(volume), 2), round(max(volume), 2)]
        range = json.dumps(range)

    # Configure the time series Plot View
    #     grace_plot = TimeSeries(
    #         engine='highcharts',
    #         title=display_name+ ' GLDAS Data',
    #         y_axis_title='Total Surface Water Storage Anomaly',
    #         y_axis_units='cm',
    #         series=[
    #             {
    #                 'name': 'Height of Liquid Water',
    #                 'color': '#0066ff',
    #                 'data': volume_time_series,
    #             },
    #             {
    #                 'name': 'Tracker',
    #                 'color': '#ff0000',
    #                 'data': [[min(x_tracker), round(min(volume), 2)], [min(x_tracker), round(max(volume), 2)]]
    #             },
    #         ],
    #         width='100%',
    #         height='300px'
    #     )

        wms_url = geoserver_url[:-5]+"wms"
        color_bar = get_color_bar()
        color_bar = json.dumps(color_bar)

        if bbox[0] < 0 and bbox[2] < 0:
            map_center = [( (360+(int(bbox[0])))+(360+(int(bbox[2])))) / 2,(int(bbox[1])+int(bbox[3])) / 2]
        else:
            map_center = [(int(bbox[0]) + int(bbox[2])) / 2, (int(bbox[1]) + int(bbox[3])) / 2]
        json.dumps(map_center)
        json.dumps(x_tracker)

        return_obj['data']=volume_time_series
        return_obj['xmin']=min(x_tracker)
        return_obj['volmin']=round(min(volume), 2)
        return_obj['volmax']=round(max(volume), 2)
        return_obj['displayname']= display_name


        # return_obj["success"] = "success"

    return JsonResponse(return_obj)

def plot_reg_soil(request):
    return_obj = {}
    return_obj = {}
    if request.is_ajax() and request.method == 'POST':
        info = request.POST

        region_id = info.get('region-info')
        print(region_id)
        print("this is the reg id")
        Session = Grace.get_persistent_store_database('main_db', as_sessionmaker=True)
        session = Session()



        region = session.query(Region).get(region_id)
        display_name = region.display_name
        region_store = ''.join(display_name.split()).lower()

        FILE_DIR = os.path.join(SOIL_NETCDF_DIR, '')

        region_dir = os.path.join(FILE_DIR + region_store, '')

        geotiff_dir = os.path.join(region_dir+"geotiff")


        geoserver = session.query(Geoserver).get(region.geoserver_id)
        geoserver_url = geoserver.url
        region_store = ''.join(display_name.split()).lower()

        bbox = [float(x) for x in region.latlon_bbox.strip("(").strip(")").split(',')]
        json.dumps(bbox)

        sorted_files = sorted(os.listdir(geotiff_dir), key=lambda x: datetime.strptime(x, '%Y_%m_%d.tif'))
        layers_length = len(sorted_files)
        grace_layer_options = []

        for file in sorted_files:
            year = int(file[:-4].split('_')[0])
            month = int(file[:-4].split('_')[1])
            day = int(file[:-4].split('_')[2])
            date_str = datetime(year,month,day)
            date_str = date_str.strftime("%Y %B %d")
            grace_layer_options.append([date_str,file[:-4]+"_"+region_store])



        csv_file = region_dir+region_store+".csv"
        with open(csv_file, 'rb') as f:
            reader = csv.reader(f)
            csvlist = list(reader)

        volume_time_series = []
        volume = []
        x_tracker = []
        formatter_string = "%m/%d/%Y"
        for item in csvlist:
            mydate = datetime.strptime(item[0], formatter_string)
            mydate = time.mktime(mydate.timetuple()) * 1000
            volume_time_series.append([mydate, float(item[1])])
            volume.append(float(item[1]))
            x_tracker.append(mydate)

        range = [round(min(volume), 2), round(max(volume), 2)]
        range = json.dumps(range)

    # Configure the time series Plot View
    #     grace_plot = TimeSeries(
    #         engine='highcharts',
    #         title=display_name+ ' GLDAS Data',
    #         y_axis_title='Total Surface Water Storage Anomaly',
    #         y_axis_units='cm',
    #         series=[
    #             {
    #                 'name': 'Height of Liquid Water',
    #                 'color': '#0066ff',
    #                 'data': volume_time_series,
    #             },
    #             {
    #                 'name': 'Tracker',
    #                 'color': '#ff0000',
    #                 'data': [[min(x_tracker), round(min(volume), 2)], [min(x_tracker), round(max(volume), 2)]]
    #             },
    #         ],
    #         width='100%',
    #         height='300px'
    #     )

        wms_url = geoserver_url[:-5]+"wms"
        color_bar = get_color_bar()
        color_bar = json.dumps(color_bar)

        if bbox[0] < 0 and bbox[2] < 0:
            map_center = [( (360+(int(bbox[0])))+(360+(int(bbox[2])))) / 2,(int(bbox[1])+int(bbox[3])) / 2]
        else:
            map_center = [(int(bbox[0]) + int(bbox[2])) / 2, (int(bbox[1]) + int(bbox[3])) / 2]
        json.dumps(map_center)
        json.dumps(x_tracker)

        return_obj['data']=volume_time_series
        return_obj['xmin']=min(x_tracker)
        return_obj['volmin']=round(min(volume), 2)
        return_obj['volmax']=round(max(volume), 2)
        return_obj['displayname']= display_name


        # return_obj["success"] = "success"

    return JsonResponse(return_obj)

def plot_reg_gw(request):
    return_obj = {}
    return_obj = {}
    if request.is_ajax() and request.method == 'POST':
        info = request.POST

        region_id = info.get('region-info')
        print(region_id)
        print("this is the reg id")
        Session = Grace.get_persistent_store_database('main_db', as_sessionmaker=True)
        session = Session()



        region = session.query(Region).get(region_id)
        display_name = region.display_name
        region_store = ''.join(display_name.split()).lower()

        FILE_DIR = os.path.join(GW_NETCDF_DIR, '')

        region_dir = os.path.join(FILE_DIR + region_store, '')

        geotiff_dir = os.path.join(region_dir+"geotiff")


        geoserver = session.query(Geoserver).get(region.geoserver_id)
        geoserver_url = geoserver.url
        region_store = ''.join(display_name.split()).lower()

        bbox = [float(x) for x in region.latlon_bbox.strip("(").strip(")").split(',')]
        json.dumps(bbox)

        sorted_files = sorted(os.listdir(geotiff_dir), key=lambda x: datetime.strptime(x, '%Y_%m_%d.tif'))
        layers_length = len(sorted_files)
        grace_layer_options = []

        for file in sorted_files:
            year = int(file[:-4].split('_')[0])
            month = int(file[:-4].split('_')[1])
            day = int(file[:-4].split('_')[2])
            date_str = datetime(year,month,day)
            date_str = date_str.strftime("%Y %B %d")
            grace_layer_options.append([date_str,file[:-4]+"_"+region_store])



        csv_file = region_dir+region_store+".csv"
        with open(csv_file, 'rb') as f:
            reader = csv.reader(f)
            csvlist = list(reader)

        volume_time_series = []
        volume = []
        x_tracker = []
        formatter_string = "%m/%d/%Y"
        for item in csvlist:
            mydate = datetime.strptime(item[0], formatter_string)
            mydate = time.mktime(mydate.timetuple()) * 1000
            volume_time_series.append([mydate, float(item[1])])
            volume.append(float(item[1]))
            x_tracker.append(mydate)

        range = [round(min(volume), 2), round(max(volume), 2)]
        range = json.dumps(range)

    # Configure the time series Plot View
    #     grace_plot = TimeSeries(
    #         engine='highcharts',
    #         title=display_name+ ' GLDAS Data',
    #         y_axis_title='Total Surface Water Storage Anomaly',
    #         y_axis_units='cm',
    #         series=[
    #             {
    #                 'name': 'Height of Liquid Water',
    #                 'color': '#0066ff',
    #                 'data': volume_time_series,
    #             },
    #             {
    #                 'name': 'Tracker',
    #                 'color': '#ff0000',
    #                 'data': [[min(x_tracker), round(min(volume), 2)], [min(x_tracker), round(max(volume), 2)]]
    #             },
    #         ],
    #         width='100%',
    #         height='300px'
    #     )

        wms_url = geoserver_url[:-5]+"wms"
        color_bar = get_color_bar()
        color_bar = json.dumps(color_bar)

        if bbox[0] < 0 and bbox[2] < 0:
            map_center = [( (360+(int(bbox[0])))+(360+(int(bbox[2])))) / 2,(int(bbox[1])+int(bbox[3])) / 2]
        else:
            map_center = [(int(bbox[0]) + int(bbox[2])) / 2, (int(bbox[1]) + int(bbox[3])) / 2]
        json.dumps(map_center)
        json.dumps(x_tracker)

        return_obj['data']=volume_time_series
        return_obj['xmin']=min(x_tracker)
        return_obj['volmin']=round(min(volume), 2)
        return_obj['volmax']=round(max(volume), 2)
        return_obj['displayname']= display_name


        # return_obj["success"] = "success"

    return JsonResponse(return_obj)


def plot_region_tot(request):
    return_obj = {}
    if request.is_ajax() and request.method == 'POST':
        info = request.POST

        region_id = info.get('region-info')
        pt_coords = request.POST['point-lat-lon']

        Session = Grace.get_persistent_store_database('main_db', as_sessionmaker=True)
        session = Session()

        region = session.query(Region).get(region_id)
        display_name = region.display_name
        region_store = ''.join(display_name.split()).lower()

        FILE_DIR = os.path.join(TOTAL_NETCDF_DIR, '')

        region_dir = os.path.join(FILE_DIR + region_store, '')

        nc_file = os.path.join(region_dir+region_store+".nc")

        if pt_coords:
            graph = get_pt_region(pt_coords,nc_file)
            graph = json.loads(graph)
            return_obj["values"] = graph["values"]
            return_obj["location"] = graph["point"]

        return_obj["success"] = "success"


    return JsonResponse(return_obj)

def plot_region_sw(request):
    return_obj = {}
    if request.is_ajax() and request.method == 'POST':
        info = request.POST

        region_id = info.get('region-info')
        pt_coords = request.POST['point-lat-lon']

        Session = Grace.get_persistent_store_database('main_db', as_sessionmaker=True)
        session = Session()

        region = session.query(Region).get(region_id)
        display_name = region.display_name
        region_store = ''.join(display_name.split()).lower()

        FILE_DIR = os.path.join(SW_NETCDF_DIR, '')

        region_dir = os.path.join(FILE_DIR + region_store, '')

        nc_file = os.path.join(region_dir+region_store+".nc")

        if pt_coords:
            graph = get_pt_region(pt_coords,nc_file)
            graph = json.loads(graph)
            return_obj["values"] = graph["values"]
            return_obj["location"] = graph["point"]

        return_obj["success"] = "success"


    return JsonResponse(return_obj)

def plot_region_soil(request):
    return_obj = {}
    if request.is_ajax() and request.method == 'POST':
        info = request.POST

        region_id = info.get('region-info')
        pt_coords = request.POST['point-lat-lon']

        Session = Grace.get_persistent_store_database('main_db', as_sessionmaker=True)
        session = Session()

        region = session.query(Region).get(region_id)
        display_name = region.display_name
        region_store = ''.join(display_name.split()).lower()

        FILE_DIR = os.path.join(SOIL_NETCDF_DIR, '')

        region_dir = os.path.join(FILE_DIR + region_store, '')

        nc_file = os.path.join(region_dir+region_store+".nc")

        if pt_coords:
            graph = get_pt_region(pt_coords,nc_file)
            graph = json.loads(graph)
            return_obj["values"] = graph["values"]
            return_obj["location"] = graph["point"]

        return_obj["success"] = "success"


    return JsonResponse(return_obj)

def plot_region_gw(request):
    return_obj = {}
    if request.is_ajax() and request.method == 'POST':
        info = request.POST

        region_id = info.get('region-info')
        pt_coords = request.POST['point-lat-lon']

        Session = Grace.get_persistent_store_database('main_db', as_sessionmaker=True)
        session = Session()

        region = session.query(Region).get(region_id)
        display_name = region.display_name
        region_store = ''.join(display_name.split()).lower()

        FILE_DIR = os.path.join(GW_NETCDF_DIR, '')

        region_dir = os.path.join(FILE_DIR + region_store, '')

        nc_file = os.path.join(region_dir+region_store+".nc")

        if pt_coords:
            graph = get_pt_region(pt_coords,nc_file)
            graph = json.loads(graph)
            return_obj["values"] = graph["values"]
            return_obj["location"] = graph["point"]

        return_obj["success"] = "success"


    return JsonResponse(return_obj)


def get_plot(request):

    return_obj = {}

    if request.is_ajax() and request.method == 'POST':
        # Get the point/polygon/shapefile coordinates along with the selected variable
        pt_coords = request.POST['point-lat-lon']
        # poly_coords = request.POST['poly-lat-lon']
        # shp_bounds = request.POST['shp-lat-lon']

        if pt_coords:
            graph = get_pt_plot(pt_coords)
            graph = json.loads(graph)
            return_obj["values"] = graph["values"]
            return_obj["location"] = graph["point"]

        return_obj['success'] = "success"

    return JsonResponse(return_obj)

def get_plot_global_tot(request):

    return_obj = {}

    if request.is_ajax() and request.method == 'POST':
        # Get the point/polygon/shapefile coordinates along with the selected variable
        pt_coords = request.POST['point-lat-lon']
        poly_coords = request.POST['poly-lat-lon']
        shp_bounds = request.POST['shp-lat-lon']

        GLOBAL_DIR = os.path.join(TOTAL_GLOBAL_NETCDF_DIR, '')


        for file in os.listdir(GLOBAL_DIR):
            if file.startswith('GRC') and file.endswith('.nc'):
                gbyos_grc_ncf = TOTAL_GLOBAL_NETCDF_DIR + file
            if file.startswith('CLM4') and file.endswith('.nc'):
                gbyos_fct_ncf = TOTAL_GLOBAL_NETCDF_DIR + file

        if pt_coords:
            graph = get_global_plot(pt_coords,TOTAL_GLOBAL_NETCDF_DIR)
            graph = json.loads(graph)
            return_obj["values"] = graph["values"]
            return_obj["location"] = graph["point"]


        return_obj['success'] = "success"

    return JsonResponse(return_obj)

def get_plot_global_sw(request):

    return_obj = {}

    if request.is_ajax() and request.method == 'POST':
        # Get the point/polygon/shapefile coordinates along with the selected variable
        pt_coords = request.POST['point-lat-lon']
        poly_coords = request.POST['poly-lat-lon']
        shp_bounds = request.POST['shp-lat-lon']

        GLOBAL_DIR = os.path.join(SW_GLOBAL_NETCDF_DIR, '')


        for file in os.listdir(GLOBAL_DIR):
            if file.startswith('GRC') and file.endswith('.nc'):
                gbyos_grc_ncf = SW_GLOBAL_NETCDF_DIR + file
            if file.startswith('CLM4') and file.endswith('.nc'):
                gbyos_fct_ncf = SW_GLOBAL_NETCDF_DIR + file

        if pt_coords:
            graph = get_global_plot(pt_coords,SW_GLOBAL_NETCDF_DIR)
            graph = json.loads(graph)
            return_obj["values"] = graph["values"]
            return_obj["location"] = graph["point"]


        return_obj['success'] = "success"

    return JsonResponse(return_obj)

def get_plot_global_soil(request):

    return_obj = {}

    if request.is_ajax() and request.method == 'POST':
        # Get the point/polygon/shapefile coordinates along with the selected variable
        pt_coords = request.POST['point-lat-lon']
        poly_coords = request.POST['poly-lat-lon']
        shp_bounds = request.POST['shp-lat-lon']

        GLOBAL_DIR = os.path.join(SOIL_GLOBAL_NETCDF_DIR, '')


        for file in os.listdir(GLOBAL_DIR):
            if file.startswith('GRC') and file.endswith('.nc'):
                gbyos_grc_ncf = SOIL_GLOBAL_NETCDF_DIR + file
            if file.startswith('CLM4') and file.endswith('.nc'):
                gbyos_fct_ncf = SOIL_GLOBAL_NETCDF_DIR + file

        if pt_coords:
            graph = get_global_plot(pt_coords,SOIL_GLOBAL_NETCDF_DIR)
            graph = json.loads(graph)
            return_obj["values"] = graph["values"]
            return_obj["location"] = graph["point"]


        return_obj['success'] = "success"

    return JsonResponse(return_obj)

def get_plot_global_gw(request):

    return_obj = {}

    if request.is_ajax() and request.method == 'POST':
        # Get the point/polygon/shapefile coordinates along with the selected variable
        pt_coords = request.POST['point-lat-lon']
        poly_coords = request.POST['poly-lat-lon']
        shp_bounds = request.POST['shp-lat-lon']

        GLOBAL_DIR = os.path.join(GW_GLOBAL_NETCDF_DIR, '')


        for file in os.listdir(GLOBAL_DIR):
            if file.startswith('GRC') and file.endswith('.nc'):
                gbyos_grc_ncf = GW_GLOBAL_NETCDF_DIR + file
            if file.startswith('CLM4') and file.endswith('.nc'):
                gbyos_fct_ncf = GW_GLOBAL_NETCDF_DIR + file

        if pt_coords:
            graph = get_global_plot(pt_coords,GW_GLOBAL_NETCDF_DIR)
            graph = json.loads(graph)
            return_obj["values"] = graph["values"]
            return_obj["location"] = graph["point"]


        return_obj['success'] = "success"

    return JsonResponse(return_obj)

@user_passes_test(user_permission_test)
def region_add(request):

    response = {}

    if request.is_ajax() and request.method == 'POST':
        info = request.POST

        region_name = info.get('region_name')
        region_store = ''.join(region_name.split()).lower()
        geoserver_id = info.get('geoserver')

        shapefile = request.FILES.getlist('shapefile')

        Session = Grace.get_persistent_store_database('main_db', as_sessionmaker=True)
        session = Session()


        geoserver = session.query(Geoserver).get(geoserver_id)
        url,uname,pwd = geoserver.url,geoserver.username,geoserver.password

        print('Processing GRACE Total Storage')
        process_shapefile_highres(shapefile, url, uname, pwd, region_store, TOTAL_NETCDF_DIR, TOTAL_GLOBAL_NETCDF_DIR,region_name,geoserver_id,"tot_grace")
        print('Total Storage Processing Complete')

        shapefile = request.FILES.getlist('shapefile')

        print('Processing Soil Moisture Data')
        process_shapefile_highres_other_storage(shapefile, url, uname, pwd, region_store, SOIL_NETCDF_DIR, SOIL_GLOBAL_NETCDF_DIR,region_name,geoserver_id,"soil_grace")
        print('Soil Moisture Processing Complete')

        shapefile = request.FILES.getlist('shapefile')

        print('Processing Groundwater Data')
        process_shapefile_highres_other_storage(shapefile, url, uname, pwd, region_store, GW_NETCDF_DIR, GW_GLOBAL_NETCDF_DIR,region_name,geoserver_id,"gw_grace")
        print('Groundwater Processing Complete')

        shapefile = request.FILES.getlist('shapefile')

        print('Processing Surface Water Date')
        process_shapefile_highres_other_storage(shapefile, url, uname, pwd, region_store, SW_NETCDF_DIR, SW_GLOBAL_NETCDF_DIR,region_name,geoserver_id,"sw_grace")
        print('Surface Water Processing Complete')


        response = {"success":"success"}

        return JsonResponse(response)

@user_passes_test(user_permission_test)
def geoserver_add(request):

    response = {}

    if request.is_ajax() and request.method == 'POST':
        info = request.POST

        geoserver_name = info.get('geoserver_name')
        geoserver_url = info.get('geoserver_url')
        geoserver_username = info.get('geoserver_username')
        geoserver_password = info.get('geoserver_password')

        try:
            cat = Catalog(geoserver_url, username=geoserver_username, password=geoserver_password,disable_ssl_certificate_validation=True)
            layer_list = cat.get_layers()
            if layer_list:
                Session = Grace.get_persistent_store_database('main_db', as_sessionmaker=True)
                session = Session()
                geoserver = Geoserver(name=geoserver_name, url=geoserver_url, username=geoserver_username, password=geoserver_password)
                session.add(geoserver)
                session.commit()
                session.close()
                response = {"data": geoserver_name, "success": "Success"}
        except Exception as e:
            print e
            response={"error":"Error processing the Geoserver URL. Please check the url,username and password."}


        return JsonResponse(response)


@user_passes_test(user_permission_test)
def geoserver_update(request):
    """
    Controller for updating a geoserver.
    """
    if request.is_ajax() and request.method == 'POST':
        # get/check information from AJAX request
        post_info = request.POST
        geoserver_id = post_info.get('geoserver_id')
        geoserver_name = post_info.get('geoserver_name')
        geoserver_url = post_info.get('geoserver_url')
        geoserver_username = post_info.get('geoserver_username')
        geoserver_password = post_info.get('geoserver_password')
        # check data
        if not geoserver_id or not geoserver_name or not geoserver_url or not \
                geoserver_username or not geoserver_password:
            return JsonResponse({'error': "Missing input data."})
        # make sure id is id
        try:
            int(geoserver_id)
        except ValueError:
            return JsonResponse({'error': 'Geoserver id is faulty.'})

        Session = Grace.get_persistent_store_database('main_db', as_sessionmaker=True)
        session = Session()

        geoserver = session.query(Geoserver).get(geoserver_id)
        try:
            spatial_dataset_engine = GeoServerSpatialDatasetEngine(endpoint=geoserver_url, username=geoserver_username,
                                                                   password=geoserver_password)
            layer_list = spatial_dataset_engine.list_layers(debug=True)
            if layer_list:


                geoserver.geoserver_name = geoserver_name
                geoserver.geoserver_url = geoserver_url
                geoserver.geoserver_username = geoserver_username
                geoserver.geoserver_password = geoserver_password

                session.commit()
                session.close()
                return JsonResponse({'success': "Geoserver sucessfully updated!"})
        except:
            return JsonResponse({'error': "A problem with your request exists."})


@user_passes_test(user_permission_test)
def geoserver_delete(request):
    """
    Controller for deleting a geoserver.
    """
    if request.is_ajax() and request.method == 'POST':
        # get/check information from AJAX request
        post_info = request.POST
        geoserver_id = post_info.get('geoserver_id')

        # initialize session
        Session = Grace.get_persistent_store_database('main_db', as_sessionmaker=True)
        session = Session()
        try:
            # delete geoserver
            try:
                geoserver = session.query(Geoserver).get(geoserver_id)
            except ObjectDeletedError:
                session.close()
                return JsonResponse({'error': "The geoserver to delete does not exist."})
            session.delete(geoserver)
            session.commit()
            session.close()
        except IntegrityError:
            session.close()
            return JsonResponse(
                {'error': "This geoserver is connected with a watershed! Must remove connection to delete."})
        return JsonResponse({'success': "Geoserver sucessfully deleted!"})
    return JsonResponse({'error': "A problem with your request exists."})

@user_passes_test(user_permission_test)
def region_delete(request):
    """
    Controller for deleting a region.
    """
    if request.is_ajax() and request.method == 'POST':
        # get/check information from AJAX request
        post_info = request.POST
        region_id = post_info.get('region_id')

        # initialize session
        Session = Grace.get_persistent_store_database('main_db', as_sessionmaker=True)
        session = Session()
        try:
            # delete region
            try:
                region = session.query(Region).get(region_id)
            except ObjectDeletedError:
                session.close()
                return JsonResponse({'error': "The geoserver to delete does not exist."})
            display_name = region.display_name
            region_store = ''.join(display_name.split()).lower()
            geoserver_id = region.geoserver_id
            geoserver = session.query(Geoserver).get(geoserver_id)
            geoserver_url = geoserver.url
            uname = geoserver.username
            pwd = geoserver.password

            spatial_dataset_engine = GeoServerSpatialDatasetEngine(endpoint=geoserver_url, username=uname,
                                                                   password=pwd)

            stores = spatial_dataset_engine.list_stores()

            for store in stores['result']:
                if store.endswith(region_store):
                    spatial_dataset_engine.delete_store(store,purge=True,recurse=True)

            FILE_DIR = os.path.join(TOTAL_NETCDF_DIR, '')

            tot_region_dir = os.path.join(FILE_DIR + region_store, '')


            FILE_DIR = os.path.join(SW_NETCDF_DIR, '')

            sw_region_dir = os.path.join(FILE_DIR + region_store, '')

            FILE_DIR = os.path.join(SOIL_NETCDF_DIR, '')

            soil_region_dir = os.path.join(FILE_DIR + region_store, '')

            FILE_DIR = os.path.join(GW_NETCDF_DIR, '')

            gw_region_dir = os.path.join(FILE_DIR + region_store, '')

            session.delete(region)
            session.commit()

            session.close()
        except IntegrityError:
            session.close()
            return JsonResponse(
                {'error': "This geoserver is connected with a watershed! Must remove connection to delete."})
        finally:
        # Delete the temporary directory once the geojson string is created
            if tot_region_dir is not None:
                if os.path.exists(tot_region_dir):
                    shutil.rmtree(tot_region_dir)
            if sw_region_dir is not None:
                if os.path.exists(sw_region_dir):
                    shutil.rmtree(sw_region_dir)
            if soil_region_dir is not None:
                if os.path.exists(soil_region_dir):
                    shutil.rmtree(soil_region_dir)
            if gw_region_dir is not None:
                if os.path.exists(gw_region_dir):
                    shutil.rmtree(gw_region_dir)
        return JsonResponse({'success': "Region sucessfully deleted!"})
    return JsonResponse({'error': "A problem with your request exists."})

def upload_shp(request):

    return_obj = {
        'success':False
    }
    GLOBAL_DIR = os.path.join(GLOBAL_NETCDF_DIR, '')

    for file in os.listdir(GLOBAL_DIR):
        if file.startswith('GRC') and file.endswith('.nc'):
            gbyos_grc_ncf = GLOBAL_NETCDF_DIR + file
        if file.startswith('CLM4') and file.endswith('.nc'):
            gbyos_fct_ncf = GLOBAL_NETCDF_DIR + file


    #Check if its an ajax post request
    if request.is_ajax() and request.method == 'POST':
        #Gettings the file list and converting the files to a geojson object. See utilities.py for the convert_shp function.
        # shapefile = request.FILES.getlist('files')
        # vals_from_shp(shapefile,GLOBAL_DIR)
        file_list = request.FILES.getlist('files')

        shp_json = convert_shp(file_list)
        gjson_obj = json.loads(shp_json)




        geometry = gjson_obj["features"][0]["geometry"]
        shape_obj = shapely.geometry.asShape(geometry)
        poly_bounds = shape_obj.bounds

        # reproj_poly_bounds = convert_shp_bounds(poly_bounds)

        #Returning the bounds and the geo_json object as a json object
        return_obj["bounds"] = poly_bounds
        return_obj["geo_json"] = gjson_obj
        return_obj["success"] = True

    return JsonResponse(return_obj)
