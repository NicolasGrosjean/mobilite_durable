import requests

# TODO Inherits from mxins


# curl 'http://localhost:8080/ors/v2/directions/foot-hiking?start=5.7643592,45.1558907&end=5.7636092,45.1491732'
def compute_distance(
    start_coords: tuple[float, float], end_coords: tuple[float, float]
) -> float:
    """
    Compute the walking distance between two coordinates using the openrouteservice API.

    Parameters:
    start_coords (tuple): A tuple containing the latitude and longitude of the start point (lat, lon).
    end_coords (tuple): A tuple containing the latitude and longitude of the end point (lat, lon).

    Returns:
    float: The walking distance in meters.
    """

    base_url = "http://localhost:8080/ors/v2/directions/foot-hiking"
    params = {
        "start": f"{start_coords[1]},{start_coords[0]}",
        "end": f"{end_coords[1]},{end_coords[0]}",
    }

    response = requests.get(base_url, params=params)
    response.raise_for_status()

    data = response.json()
    distance = data["features"][0]["properties"]["segments"][0]["distance"]

    return distance


print(compute_distance((45.1558907, 5.7643592), (45.1491732, 5.7636092)))
