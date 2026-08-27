def get_traffic_light(density):

    if density == "Sepi":

        return {
            "green": 20,
            "red": 57
        }

    elif density == "Sedang":

        return {
            "green": 40,
            "red": 37
        }

    else:

        return {
            "green": 60,
            "red": 17
        }