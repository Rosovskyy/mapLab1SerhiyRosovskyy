from itertools import islice
import pandas
import folium


def read_file(path):
    """
    (str) -> (list)q
    Return list of lines from file (path to file)
    """
    m = int(input("Enter a count of lines, which you need to read: "))
    lines_list = []
    f = open(path, encoding="utf-8", errors="ignore")
    print("Wait a moment")
    for i in islice(f.read().strip().split("\n"), 15, m):
        try:
            if '}' in i:
                i = i.split('}')
            else:
                i = i.split('\t')
            i = list(filter(lambda x: len(x) > 0, i))
            i[1] = i[1].replace('\t', '')
            lines_list.append(i)
        except:
            continue
    return lines_list


def country_dict(lines_list, year):
    """(set) -> (dict)
    Return dict from set of lines with a year as key and tuple(contry, film)
    as a value
    """
    film_dict = {}
    for i in lines_list:
        if '{' in i[0]:
            m = i[0].find('{') - 1
            i[0] = i[0][:m]
        if '(' in i[1]:
            m = i[1].find('(')
            i[1] = i[1][:m]
        i[0] = i[0].split(' (')
        try:
            if str(year) in i[0][1]:
                i[0][1] = int(i[0][1].replace(')', '').replace('/I', '').replace('I', ''))
            else:
                continue
        except:
            continue
        if i[0][1] in film_dict.keys():
            film_dict[i[0][1]].append((i[1], i[0][0]))
        else:
            film_dict[i[0][1]] = [(i[1], i[0][0])]
    return film_dict


def get_location(place):
    """(str) -> tuple(float, float)
    Take name of the place and return it's location
    """
    import requests
    url = "https://maps.googleapis.com/maps/api/geocode/json?address=1600"
    for i in place.split():
        url += '+' + i
    url += "&key=AIzaSyBZ9WWdYr5xHTci_LHkm6RaBicWYENSNRA"
    params = {'sensor': 'false', 'address': place}
    r = requests.get(url, params=params)
    result = r.json()["results"]
    location = result[0]['geometry']['location']
    return (location['lat'], location['lng'])


def layerWorld(mapp):
    mapp.add_child(folium.GeoJson(data=open('world.json', 'r',
            encoding='utf-8-sig').read(),
            style_function=lambda x: {'fillColor': 'green'
            if x['properties']['POP2005'] < 10000000
            else 'orange' if 10000000 <= x['properties']['POP2005'] < 20000000
            else 'red'}))
    return mapp


def station(mapp):
    data = pandas.read_csv("stations.csv")
    lat = data['lat']
    lng = data['lng']
    name = data['stat']

    mapp = folium.Map()
    fg = folium.FeatureGroup(name ="StationsInArctica")
    for lat, lng, name in zip(lat, lng, name):
        fg.add_child(folium.Marker(location=[lat, lng],
                                        icon=folium.Icon(color='black'),
                                        popup=name))
    return fg


def AfghanistanCities(mapp):
    data = pandas.read_csv("cities.csv")
    lat = data['lat']
    lon = data['lng']
    pop = data['pop']
    city = data['city']


    def  color_creator(population):
        if  population <  100000:
            return  "green"
        elif 100000  <= population <=  250000:
            return  "yellow"
        else:
            return  "red"

    fg = folium.FeatureGroup(name ="AfghanistanPop")
    for lt, ln, pop, city in zip(lat, lon, pop, city):
        fg.add_child(folium.CircleMarker(location=[lt, ln],
                                        radius=10,
                                        color=color_creator(pop),
                                        popup=str(pop) + " " + city,
                                        fill_opacity=0.5 ))
    return fg

def world_map(country_dict):
    """(dict) -> None
    Create a map, add markers and layers
    """
    mapp = folium.Map()
    f = 0
    k = 0
    fg_pp = folium.FeatureGroup(name="Population")
    afg = folium.FeatureGroup(name="AfghanistanCities")
    st = folium.FeatureGroup(name="AntarcticStations")
    st = station(st)
    afg = AfghanistanCities(afg)
    fg = layerWorld(fg_pp)
    for i in country_dict.values():
        for j in i:
            try:
                location = get_location(j[0])
                f += 1
                mapp.add_child(folium.Marker(
                    location=[location[0], location[1]],
                    popup=j[1].replace('"', '').replace("#", ''),
                    icon=folium.Icon()))
            except:
                k += 1
                continue
    folium.TileLayer('Mapbox Bright').add_to(mapp)
    mapp.add_child(fg)
    mapp.add_child(afg)
    mapp.add_child(st)
    mapp.add_child(folium.LayerControl())
    mapp.save('map.html')


def main():
    """(None) -> None
    Call every function and build map
    """
    year = int(input("Enter the year: "))
    world_map(country_dict(read_file('locations.list'), year))


main()
