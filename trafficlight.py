def get_traffic_light(density):

    if density == "Sepi":

        return {
            "green": 30,
            "red": 60
        }

    elif density == "Sedang":

        return {
            "green": 45,
            "red": 45
        }

    else:

        return {
            "green": 60,
            "red": 30
        }