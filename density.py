def get_density(avg_vehicle):

    if avg_vehicle < 20:
        return "Sepi"

    elif avg_vehicle < 60:
        return "Sedang"

    else:
        return "Ramai"